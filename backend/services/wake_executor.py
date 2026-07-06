import json
import logging
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
        'ipmi': _wake_ipmi_placeholder,
    }
    return handlers[method](device)


def _wake_wol(device):
    port = device.wol_port or 9
    send_magic_packet(device.mac, ip_address=device.ip, port=port)
    if device.use_broadcast:
        broadcast = device.broadcast_ip or _broadcast_for_ip(device.ip)
        if broadcast:
            send_magic_packet(device.mac, ip_address=broadcast, port=port)


def _broadcast_for_ip(ip):
    parts = ip.split('.')
    if len(parts) == 4:
        return f'{parts[0]}.{parts[1]}.{parts[2]}.255'
    return '255.255.255.255'


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
        result = subprocess.run(
            ssh_cmd,
            input=private_key.encode() if private_key else None,
            capture_output=True,
            timeout=15,
            check=False,
        )
        if result.returncode != 0 and not password:
            raise WakeMethodError('SSH_WAKE_FAILED', 'SSH wake command failed.')
        if password:
            # Fallback: sshpass if available, otherwise skip password auth in MVP
            sshpass = subprocess.run(
                ['which', 'sshpass'],
                capture_output=True,
                timeout=2,
            )
            if sshpass.returncode != 0:
                logging.warning('sshpass not available; SSH password auth skipped for %s', device.domain)
            else:
                subprocess.run(
                    ['sshpass', '-p', password, *ssh_cmd],
                    capture_output=True,
                    timeout=15,
                    check=False,
                )
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


def _wake_ipmi_placeholder(device):
    raise WakeMethodError('IPMI_NOT_SUPPORTED', 'IPMI wake is reserved for a future release.')
