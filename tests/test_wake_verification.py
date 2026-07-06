"""Tests for verified wake job flow."""

from unittest.mock import patch

from models import Device, db
from services.wake_job_service import create_wake_job, get_wake_job
from services.wake_service import run_verified_wake


def test_verified_wake_job_completes_online(client):
    device = Device(
        name='Test',
        domain='verify.test.local',
        ip='192.168.1.55',
        mac='AA:BB:CC:DD:EE:55',
        wake_timeout_seconds=30,
        wake_poll_interval_seconds=1,
    )
    db.session.add(device)
    db.session.commit()

    job_id = create_wake_job(device.id)

    with patch('services.wake_service.check_device_online', return_value=False):
        with patch('services.wake_service.wait_for_device', return_value=5000):
            with patch('services.wake_service.execute_wake_action'):
                run_verified_wake(device, job_id, source='manual')

    job = get_wake_job(job_id)
    assert job['status'] == 'online'
    assert job['online'] is True
    assert job['message_code'] == 'WAKE_ONLINE'

    refreshed = Device.query.get(device.id)
    assert refreshed.wake_success_count == 1
    assert refreshed.last_wake_success is True


def test_wake_verify_endpoint_returns_job(client, sample_device):
    with patch('services.wake_service.run_verified_wake'):
        response = client.post(f'/api/devices/{sample_device["id"]}/wake?verify=true')
    assert response.status_code == 202
    data = response.get_json()
    assert 'job_id' in data
    assert data['status'] == 'starting'
