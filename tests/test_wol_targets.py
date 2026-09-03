"""Wake-on-LAN sends to every useful address and tolerates partial failures."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from services.wake_executor import LIMITED_BROADCAST, WakeMethodError, _wake_wol, wol_targets


def _device(**overrides):
    base = dict(ip='192.168.1.186', mac='AA:BB:CC:DD:EE:FF', wol_port=9, use_broadcast=True, broadcast_ip=None)
    base.update(overrides)
    return SimpleNamespace(**base)


def test_targets_include_unicast_directed_and_limited_broadcast():
    assert wol_targets(_device()) == ['192.168.1.186', '192.168.1.255', LIMITED_BROADCAST]


def test_custom_broadcast_ip_replaces_directed_broadcast():
    assert wol_targets(_device(broadcast_ip='10.0.0.255')) == ['192.168.1.186', '10.0.0.255', LIMITED_BROADCAST]


def test_broadcast_disabled_sends_unicast_only():
    assert wol_targets(_device(use_broadcast=False)) == ['192.168.1.186']


def test_legacy_rows_without_flag_still_broadcast():
    # Devices created before the column existed have use_broadcast=None.
    assert LIMITED_BROADCAST in wol_targets(_device(use_broadcast=None))


def test_one_failing_target_does_not_block_the_others():
    sent = []

    def fake_send(mac, ip_address, port):
        if ip_address == '192.168.1.186':
            raise OSError('Network is unreachable')
        sent.append(ip_address)

    with patch('services.wake_executor.send_magic_packet', side_effect=fake_send):
        _wake_wol(_device())

    assert sent == ['192.168.1.255', LIMITED_BROADCAST]


def test_all_targets_failing_raises_wol_error():
    with patch('services.wake_executor.send_magic_packet', side_effect=OSError('boom')):
        with pytest.raises(WakeMethodError) as excinfo:
            _wake_wol(_device())
    assert excinfo.value.code == 'WOL_SEND_FAILED'


def test_new_devices_broadcast_by_default(client):
    response = client.post('/api/devices', json={
        'domain': 'bc.test.local', 'ip': '192.168.1.70', 'mac': 'AA:BB:CC:DD:EE:70',
    })
    assert response.status_code == 201
    assert response.get_json()['use_broadcast'] is True


def test_actor_ip_uses_first_forwarded_address(client):
    from utils.http import actor_ip

    with client.application.test_request_context(headers={'X-Forwarded-For': '203.0.113.9, 10.0.0.1'}):
        assert actor_ip() == '203.0.113.9'
    with client.application.test_request_context():
        assert actor_ip() is None or isinstance(actor_ip(), str)
