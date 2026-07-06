import socket
import time

import requests

from services.adaptive_wake_service import effective_wake_timeout
from utils.network import check_host_online
from utils.validators import VALID_CHECK_TYPES

__all__ = ['VALID_CHECK_TYPES', 'check_device_online', 'check_http_url', 'check_tcp_port', 'wait_for_device']


def check_tcp_port(host, port, timeout=2):
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except OSError:
        return False


def check_http_url(url, timeout=3):
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        return response.status_code < 500
    except requests.RequestException:
        return False


def check_device_online(device):
    check_type = getattr(device, 'status_check_type', None) or 'ping'
    host = device.status_check_host or device.ip

    if check_type == 'tcp':
        port = device.status_check_port or 80
        return check_tcp_port(host, port)
    if check_type == 'http':
        url = device.status_check_url
        if not url:
            port = device.status_check_port or 80
            url = f'http://{host}:{port}/'
        return check_http_url(url)
    return check_host_online(host)


def wait_for_device(device, max_wait=None, interval=None):
    timeout = effective_wake_timeout(device, max_wait=max_wait)
    poll_interval = interval if interval is not None else (device.wake_poll_interval_seconds or 3)
    elapsed = 0
    while elapsed < timeout:
        if check_device_online(device):
            return elapsed * 1000
        time.sleep(poll_interval)
        elapsed += poll_interval
    return None
