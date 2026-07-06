"""Tests for wake method execution."""

from unittest.mock import patch

import pytest

from models import Device, db
from services.wake_executor import WakeMethodError, execute_wake_action


def test_wol_wake_sends_magic_packet(client):
    device = Device(
        name='WOL',
        domain='wol.test.local',
        ip='192.168.1.60',
        mac='AA:BB:CC:DD:EE:60',
        wake_method='wol',
    )
    db.session.add(device)
    db.session.commit()

    with patch('services.wake_executor.send_magic_packet') as mock_send:
        execute_wake_action(device)
    mock_send.assert_called()


def test_webhook_requires_url(client):
    device = Device(
        name='Hook',
        domain='hook.test.local',
        ip='192.168.1.61',
        mac='AA:BB:CC:DD:EE:61',
        wake_method='webhook',
    )
    db.session.add(device)
    db.session.commit()

    with pytest.raises(WakeMethodError) as exc:
        execute_wake_action(device)
    assert exc.value.code == 'WEBHOOK_URL_MISSING'


def test_ipmi_requires_password(client):
    device = Device(
        name='IPMI',
        domain='ipmi.test.local',
        ip='192.168.1.62',
        mac='AA:BB:CC:DD:EE:62',
        wake_method='ipmi',
        ipmi_host='192.168.1.62',
        ipmi_username='ADMIN',
    )
    db.session.add(device)
    db.session.commit()

    with pytest.raises(WakeMethodError) as exc:
        execute_wake_action(device)
    assert exc.value.code == 'IPMI_CREDENTIALS_MISSING'


def test_ipmi_wake_runs_ipmitool(client):
    device = Device(
        name='IPMI',
        domain='ipmi2.test.local',
        ip='192.168.1.63',
        mac='AA:BB:CC:DD:EE:63',
        wake_method='ipmi',
        ipmi_host='192.168.1.63',
        ipmi_port=623,
        ipmi_username='ADMIN',
    )
    db.session.add(device)
    db.session.commit()

    with patch('services.wake_executor.get_credential', return_value='secret'):
        with patch('services.wake_executor.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            execute_wake_action(device)

    args = mock_run.call_args[0][0]
    assert args[0] == 'ipmitool'
    assert 'chassis' in args
    assert 'power' in args
