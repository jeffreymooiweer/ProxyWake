import re

from models import Device
from services.wake_executor import VALID_WAKE_METHODS

VALID_CHECK_TYPES = ('ping', 'tcp', 'http')

IP_PATTERN = re.compile(
    r"""
    ^
    (?:
      (?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)
    \.){3}
    (?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)
    $
    """,
    re.VERBOSE,
)

MAC_PATTERN = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
DOMAIN_PATTERN = re.compile(
    r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
)


def is_valid_ip(ip):
    return bool(IP_PATTERN.match(ip))


def is_valid_mac(mac):
    return bool(MAC_PATTERN.match(mac))


def normalize_mac(mac):
    cleaned = mac.replace('-', ':').upper()
    parts = cleaned.split(':')
    return ':'.join(part.zfill(2) for part in parts)


def is_valid_domain(domain):
    return bool(DOMAIN_PATTERN.match(domain.strip()))


def validate_device_payload(data, device=None):
    domain = (data.get('domain') or '').strip().lower()
    ip = (data.get('ip') or '').strip()
    mac = normalize_mac((data.get('mac') or '').strip())
    name = (data.get('name') or '').strip() or None

    if not domain or not ip or not mac:
        return None, 'REQUIRED_FIELDS'
    if not is_valid_domain(domain):
        return None, 'INVALID_DOMAIN'
    if not is_valid_ip(ip):
        return None, 'INVALID_IP'
    if not is_valid_mac(mac):
        return None, 'INVALID_MAC'

    existing = Device.query.filter_by(domain=domain).first()
    if existing and (device is None or existing.id != device.id):
        return None, 'DOMAIN_ALREADY_EXISTS'

    group_id = data.get('group_id')
    npm_host_id = data.get('npm_host_id')
    if group_id == '' or group_id is None:
        group_id = None
    else:
        group_id = int(group_id)
    if npm_host_id == '' or npm_host_id is None:
        npm_host_id = None
    else:
        npm_host_id = int(npm_host_id)

    status_check_type = (data.get('status_check_type') or 'ping').strip().lower()
    if status_check_type not in VALID_CHECK_TYPES:
        return None, 'INVALID_STATUS_CHECK_TYPE'

    status_check_host = (data.get('status_check_host') or '').strip() or None
    if status_check_host and not is_valid_ip(status_check_host) and not is_valid_domain(status_check_host):
        return None, 'INVALID_IP'

    status_check_port = data.get('status_check_port')
    if status_check_port in ('', None):
        status_check_port = None
    else:
        status_check_port = int(status_check_port)

    def _unmasked_url(field):
        # to_dict() masks credentials/tokens in webhook URLs; when a client
        # echoes the masked value back on update, keep the stored original.
        value = (data.get(field) or '').strip() or None
        if value and '***' in value and device is not None:
            return getattr(device, field)
        return value

    status_check_url = (data.get('status_check_url') or '').strip() or None
    wake_timeout_seconds = int(data.get('wake_timeout_seconds', 120))
    wake_poll_interval_seconds = int(data.get('wake_poll_interval_seconds', 3))
    wake_method = (data.get('wake_method') or 'wol').strip().lower()
    if wake_method not in VALID_WAKE_METHODS:
        return None, 'INVALID_WAKE_METHOD'

    return {
        'domain': domain,
        'ip': ip,
        'mac': mac,
        'name': name,
        'group_id': group_id,
        'npm_host_id': npm_host_id,
        'use_broadcast': bool(data.get('use_broadcast', False)),
        'broadcast_ip': data.get('broadcast_ip'),
        'wake_cooldown_seconds': int(data.get('wake_cooldown_seconds', 30)),
        'status_check_type': status_check_type,
        'status_check_host': status_check_host,
        'status_check_port': status_check_port,
        'status_check_url': status_check_url,
        'wake_timeout_seconds': wake_timeout_seconds,
        'wake_poll_interval_seconds': wake_poll_interval_seconds,
        'wake_method': wake_method,
        'wol_port': int(data.get('wol_port', 9)),
        'ssh_host': (data.get('ssh_host') or '').strip() or None,
        'ssh_port': int(data.get('ssh_port', 22)),
        'ssh_username': (data.get('ssh_username') or '').strip() or None,
        'ssh_command': (data.get('ssh_command') or 'exit').strip() or 'exit',
        'webhook_url': _unmasked_url('webhook_url'),
        'webhook_method': (data.get('webhook_method') or 'POST').upper(),
        'webhook_headers': data.get('webhook_headers'),
        'webhook_body': data.get('webhook_body'),
        'homeassistant_webhook_url': _unmasked_url('homeassistant_webhook_url'),
        'ipmi_host': (data.get('ipmi_host') or '').strip() or None,
        'ipmi_port': int(data.get('ipmi_port', 623)),
        'ipmi_username': (data.get('ipmi_username') or '').strip() or None,
    }, None
