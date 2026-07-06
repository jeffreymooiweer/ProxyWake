import re

from models import Device

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
    }, None
