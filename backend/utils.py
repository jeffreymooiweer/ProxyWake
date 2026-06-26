import re
import subprocess
import platform


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


def check_host_online(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
    try:
        result = subprocess.run(
            ['ping', param, '1', timeout_param, '1', ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, OSError):
        return False
