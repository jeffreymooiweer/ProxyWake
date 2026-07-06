"""Tests for wake flow logic (mocked network)."""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from models import Device, WakeEvent, db
from services import smart_wake_device


@pytest.fixture
def offline_device(client):
    device = Device(
        name='Sleeping PC',
        domain='sleep.test.local',
        ip='192.168.1.70',
        mac='AA:BB:CC:DD:EE:03',
        wake_cooldown_seconds=60,
    )
    db.session.add(device)
    db.session.commit()
    return device


@patch('services.check_host_online', return_value=False)
@patch('services._send_packets')
def test_wake_sends_packet_when_offline(mock_send, mock_online, offline_device):
    result = smart_wake_device(offline_device, source='manual')

    mock_send.assert_called_once_with(offline_device)
    assert result['message_code'] == 'WAKE_SENT'
    assert result['skipped'] is False

    events = WakeEvent.query.filter_by(device_id=offline_device.id).all()
    assert len(events) == 1
    assert events[0].success is True
    assert events[0].skipped is False


@patch('services.check_host_online', return_value=True)
@patch('services._send_packets')
def test_wake_skips_when_already_online(mock_send, mock_online, offline_device):
    result = smart_wake_device(offline_device, source='manual')

    mock_send.assert_not_called()
    assert result['message_code'] == 'DEVICE_ALREADY_ONLINE'
    assert result['skipped'] is True


@patch('services.check_host_online', return_value=False)
@patch('services._send_packets')
def test_wake_respects_cooldown(mock_send, mock_online, offline_device):
    offline_device.last_wake_at = datetime.now(timezone.utc)
    db.session.commit()

    result = smart_wake_device(offline_device, source='manual')

    mock_send.assert_not_called()
    assert result['message_code'] == 'DEVICE_COOLDOWN'
    assert 'seconds' in result


@patch('services.check_host_online', return_value=False)
@patch('services._send_packets')
def test_wake_force_bypasses_cooldown(mock_send, mock_online, offline_device):
    offline_device.last_wake_at = datetime.now(timezone.utc)
    db.session.commit()

    result = smart_wake_device(offline_device, source='manual', force=True)

    mock_send.assert_called_once()
    assert result['message_code'] == 'WAKE_SENT'


@patch('services.check_host_online', return_value=False)
@patch('services._send_packets')
def test_wake_device_api_endpoint(mock_send, mock_online, client, sample_device):
    response = client.post(f'/api/devices/{sample_device["id"]}/wake')
    assert response.status_code == 200
    assert response.get_json()['message_code'] == 'WAKE_SENT'
    mock_send.assert_called_once()
