import json
import logging
import os
import socket
import subprocess

import requests
from wakeonlan import send_magic_packet

from services.credential_service import get_credential

VALID_WAKE_METHODS = ('wol', 'ssh', 'webhook', 'home_assistant', 'ipmi')


class WakeMethodError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def execute_wake_action(device):
    method = (device.wake_method or 'wol').lower()
    if method not in VALID_WAKE_METHODS:
        raise WakeMethodError('INVALID_WAKE_METHOD', f'Unsupported wake method: {method}')

    handlers = {
        'wol': _wake_wol,
        'ssh': _wake_ssh,
        'webhook': _wake_webhook,
        'home_assistant': _wake_home_assistant,
        'ipmi': _wake_ipmi,
    }
    return handlers[method](device)


LIMITED_BROADCAST = '255.255.255.255'


def wol_targets(device):
    """Addresses a magic packet is sent to, most specific first.

    A sleeping machine no longer answers ARP, so a unicast packet to its IP
    is often undeliverable. Broadcasts reach the NIC regardless: the
    subnet-directed broadcast follows the routing table (correct interface
    on multi-homed hosts) and the limited broadcast is what most WoL tools
    use. Sending to all of them costs nothing and maximises the chance that
    one of them reaches the device.
    """
    targets = [device.ip]
    if device.use_broadcast is None or device.use_broadcast:
        directed = device.broadcast_ip or _broadcast_for_ip(device.ip)
        for candidate in (directed, LIMITED_BROADCAST):
            if candidate and candidate not in targets:
                targets.append(candidate)
    return targets


def _source_ip_for(target_ip):
    """Local IP of the interface that routes to target_ip.

    Binding the socket to it makes the limited broadcast (255.255.255.255)
    leave through the interface that is actually on the device's LAN. That
    matters when the container has several interfaces: host networking on
    a multi-NIC server, or a macvlan/ipvlan network combined with a bridge
    network for the reverse proxy. PROXYWAKE_WOL_INTERFACE overrides the
    automatic choice with a fixed local IP.
    """
    forced = os.environ.get('PROXYWAKE_WOL_INTERFACE', '').strip()
    if forced:
        return forced
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect((target_ip, 9))
            return probe.getsockname()[0]
    except OSError:
        return None


def _send_via(mac, target, port, source_ip):
    if source_ip:
        try:
            send_magic_packet(mac, ip_address=target, port=port, interface=source_ip)
            return
        except OSError as exc:
            logging.debug('Bound send to %s via %s failed (%s); retrying unbound', target, source_ip, exc)
    send_magic_packet(mac, ip_address=target, port=port)


def _wake_wol(device):
    port = device.wol_port or 9
    source_ip = _source_ip_for(device.ip)
    sent = 0
    last_error = None
    for target in wol_targets(device):
        try:
            _send_via(device.mac, target, port, source_ip)
            sent += 1
        except OSError as exc:
            # One unreachable target must not stop the others (e.g. unicast
            # "network unreachable" while the broadcast would have worked).
            last_error = exc
            logging.warning('Magic packet to %s for %s failed: %s', target, device.mac, exc)
    if sent == 0:
        raise WakeMethodError('WOL_SEND_FAILED', f'Could not send a magic packet: {last_error}')
    logging.debug('Magic packet for %s sent to %d target(s) from %s', device.mac, sent, source_ip or 'default interface')


def _broadcast_for_ip(ip):
    parts = ip.split('.')
    if len(parts) == 4:
        return f'{parts[0]}.{parts[1]}.{parts[2]}.255'
    return LIMITED_BROADCAST


def _wake_ssh(device):
    host = device.ssh_host or device.ip
    port = device.ssh_port or 22
    username = device.ssh_username or 'root'
    command = device.ssh_command or 'exit'
    password = get_credential(device.id, 'ssh_password')
    private_key = get_credential(device.id, 'ssh_private_key')

    if not password and not private_key:
        raise WakeMethodError('SSH_CREDENTIALS_MISSING', 'SSH credentials are not configured for this device.')

    ssh_cmd = ['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=no', '-p', str(port)]
    if private_key:
        ssh_cmd.extend(['-i', '/dev/stdin'])
    ssh_cmd.append(f'{username}@{host}')
    ssh_cmd.append(command)

    try:
        if private_key:
            result = subprocess.run(
                ssh_cmd,
                input=private_key.encode(),
                capture_output=True,
                timeout=15,
                check=False,
            )
            if result.returncode != 0:
                raise WakeMethodError('SSH_WAKE_FAILED', 'SSH wake command failed.')
            return

        if not password:
            raise WakeMethodError('SSH_CREDENTIALS_MISSING', 'SSH credentials are not configured for this device.')

        sshpass = subprocess.run(['which', 'sshpass'], capture_output=True, timeout=2)
        if sshpass.returncode != 0:
            raise WakeMethodError('SSH_PASS_UNAVAILABLE', 'sshpass is required for SSH password authentication.')

        result = subprocess.run(
            ['sshpass', '-p', password, *ssh_cmd],
            capture_output=True,
            timeout=15,
            check=False,
        )
        if result.returncode != 0:
            raise WakeMethodError('SSH_WAKE_FAILED', 'SSH wake command failed.')
    except subprocess.TimeoutExpired as exc:
        raise WakeMethodError('SSH_WAKE_FAILED', 'SSH wake command timed out.') from exc
    except OSError as exc:
        raise WakeMethodError('SSH_WAKE_FAILED', 'SSH wake command could not be executed.') from exc


def _wake_webhook(device):
    url = device.webhook_url
    if not url:
        raise WakeMethodError('WEBHOOK_URL_MISSING', 'Webhook URL is not configured.')
    method = (device.webhook_method or 'POST').upper()
    headers = {}
    if device.webhook_headers:
        try:
            headers = json.loads(device.webhook_headers)
        except json.JSONDecodeError as exc:
            raise WakeMethodError('INVALID_WEBHOOK_HEADERS', 'Webhook headers must be valid JSON.') from exc
    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            data=device.webhook_body or None,
            timeout=10,
        )
        if response.status_code >= 400:
            raise WakeMethodError('WEBHOOK_WAKE_FAILED', f'Webhook returned status {response.status_code}.')
    except requests.RequestException as exc:
        raise WakeMethodError('WEBHOOK_WAKE_FAILED', 'Webhook request failed.') from exc


def _wake_home_assistant(device):
    url = device.homeassistant_webhook_url or device.webhook_url
    if not url:
        raise WakeMethodError('HA_WEBHOOK_MISSING', 'Home Assistant webhook URL is not configured.')
    try:
        response = requests.post(url, json={}, timeout=10)
        if response.status_code >= 400:
            raise WakeMethodError('HA_WAKE_FAILED', f'Home Assistant webhook returned status {response.status_code}.')
    except requests.RequestException as exc:
        raise WakeMethodError('HA_WAKE_FAILED', 'Home Assistant webhook request failed.') from exc


def _wake_ipmi(device):
    host = device.ipmi_host or device.ip
    port = device.ipmi_port or 623
    username = device.ipmi_username or 'ADMIN'
    password = get_credential(device.id, 'ipmi_password')

    if not password:
        raise WakeMethodError('IPMI_CREDENTIALS_MISSING', 'IPMI password is not configured for this device.')

    cmd = [
        'ipmitool',
        '-I', 'lanplus',
        '-H', host,
        '-p', str(port),
        '-U', username,
        '-P', password,
        'chassis', 'power', 'on',
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=15, check=False, text=True)
        output = f'{result.stdout or ""}{result.stderr or ""}'.lower()
        if result.returncode != 0 and 'already' not in output:
            logging.error('IPMI wake failed for %s: %s', device.domain, output.strip())
            raise WakeMethodError('IPMI_WAKE_FAILED', 'IPMI chassis power on command failed.')
    except subprocess.TimeoutExpired as exc:
        raise WakeMethodError('IPMI_WAKE_FAILED', 'IPMI command timed out.') from exc
    except OSError as exc:
        raise WakeMethodError('IPMI_WAKE_FAILED', 'ipmitool could not be executed.') from exc
