"""Tests for device status checks."""

from unittest.mock import MagicMock, patch

from services.status_service import check_device_online, check_http_url, check_tcp_port


def test_check_tcp_port_success():
    with patch('services.status_service.socket.create_connection'):
        assert check_tcp_port('192.168.1.1', 22) is True


def test_check_tcp_port_failure():
    with patch('services.status_service.socket.create_connection', side_effect=OSError):
        assert check_tcp_port('192.168.1.1', 22) is False


def test_check_http_url_success():
    response = MagicMock(status_code=200)
    with patch('services.status_service.requests.get', return_value=response):
        assert check_http_url('http://192.168.1.1/') is True


def test_check_http_url_server_error():
    response = MagicMock(status_code=503)
    with patch('services.status_service.requests.get', return_value=response):
        assert check_http_url('http://192.168.1.1/') is False


def test_check_device_online_ping():
    device = MagicMock(ip='192.168.1.50', status_check_type='ping', status_check_host=None)
    with patch('services.status_service.check_host_online', return_value=True) as mock_ping:
        assert check_device_online(device) is True
        mock_ping.assert_called_once_with('192.168.1.50')


def test_check_device_online_tcp():
    device = MagicMock(
        ip='192.168.1.50',
        status_check_type='tcp',
        status_check_host=None,
        status_check_port=32400,
    )
    with patch('services.status_service.check_tcp_port', return_value=True) as mock_tcp:
        assert check_device_online(device) is True
        mock_tcp.assert_called_once_with('192.168.1.50', 32400)
