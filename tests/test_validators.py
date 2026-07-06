"""Tests for network and device field validators."""

import pytest

from utils import is_valid_domain, is_valid_ip, is_valid_mac, normalize_mac, subnet_from_ip


@pytest.mark.parametrize(
    'ip,expected',
    [
        ('192.168.1.1', True),
        ('10.0.0.255', True),
        ('256.1.1.1', False),
        ('not-an-ip', False),
        ('', False),
    ],
)
def test_is_valid_ip(ip, expected):
    assert is_valid_ip(ip) is expected


@pytest.mark.parametrize(
    'mac,expected',
    [
        ('AA:BB:CC:DD:EE:FF', True),
        ('aa-bb-cc-dd-ee-ff', True),
        ('AA:BB:CC:DD:EE', False),
        ('invalid', False),
    ],
)
def test_is_valid_mac(mac, expected):
    assert is_valid_mac(mac) is expected


def test_normalize_mac():
    assert normalize_mac('aa-bb-cc-dd-ee-ff') == 'AA:BB:CC:DD:EE:FF'
    assert normalize_mac('a:b:c:d:e:f') == '0A:0B:0C:0D:0E:0F'


@pytest.mark.parametrize(
    'domain,expected',
    [
        ('nas.example.com', True),
        ('sub.host.lab', True),
        ('invalid', False),
        ('-bad.com', False),
    ],
)
def test_is_valid_domain(domain, expected):
    assert is_valid_domain(domain) is expected


def test_subnet_from_ip():
    assert subnet_from_ip('192.168.1.50') == '192.168.1.0/24'
    assert subnet_from_ip('invalid') is None
