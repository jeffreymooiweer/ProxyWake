import ipaddress
import re
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed


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


def check_host_online(ip, timeout=1):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
    try:
        result = subprocess.run(
            ['ping', param, '1', timeout_param, str(timeout), ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 1,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, OSError):
        return False


def wait_for_host(ip, max_wait=120, interval=3):
    import time
    elapsed = 0
    while elapsed < max_wait:
        if check_host_online(ip):
            return elapsed * 1000
        time.sleep(interval)
        elapsed += interval
    return None


def subnet_from_ip(ip):
    try:
        network = ipaddress.ip_network(f'{ip}/24', strict=False)
        return str(network)
    except ValueError:
        return None


def scan_subnet(subnet, max_hosts=64):
    try:
        network = ipaddress.ip_network(subnet, strict=False)
    except ValueError:
        return []

    hosts = list(network.hosts())[:max_hosts]
    results = []

    def probe(host):
        ip = str(host)
        if check_host_online(ip, timeout=1):
            return {'ip': ip, 'online': True}
        return None

    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = {executor.submit(probe, host): host for host in hosts}
        for future in as_completed(futures):
            item = future.result()
            if item:
                results.append(item)

    return sorted(results, key=lambda item: ipaddress.ip_address(item['ip']))
