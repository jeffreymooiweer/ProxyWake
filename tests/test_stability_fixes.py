"""Regression tests for multi-worker stability and data-integrity fixes."""

import config
from models import Device, ScheduledWake, WakeEvent, WakeJob, db
from services.wake_job_service import create_wake_job, get_wake_job, update_wake_job
from utils.logging_config import filter_log_lines, parse_log_line


def test_secret_key_is_stable_without_env(monkeypatch, tmp_path):
    monkeypatch.delenv('PROXYWAKE_SECRET_KEY', raising=False)
    monkeypatch.setattr(config, 'DATA_DIR', tmp_path)
    monkeypatch.setattr(config, 'SECRET_KEY_FILE', tmp_path / 'secret.key')

    first = config.get_secret_key()
    second = config.get_secret_key()

    assert first == second
    assert (tmp_path / 'secret.key').read_text().strip() == first


def test_secret_key_recovers_from_empty_file(monkeypatch, tmp_path):
    """A worker that read the file mid-write (or a crashed writer) must not
    leave the app with an empty secret key."""
    monkeypatch.delenv('PROXYWAKE_SECRET_KEY', raising=False)
    monkeypatch.setattr(config, 'DATA_DIR', tmp_path)
    monkeypatch.setattr(config, 'SECRET_KEY_FILE', tmp_path / 'secret.key')
    (tmp_path / 'secret.key').write_text('')

    key = config.get_secret_key()
    assert key
    assert config.get_secret_key() == key


def test_secret_key_env_still_wins(monkeypatch, tmp_path):
    monkeypatch.setenv('PROXYWAKE_SECRET_KEY', 'env-key')
    monkeypatch.setattr(config, 'SECRET_KEY_FILE', tmp_path / 'secret.key')
    assert config.get_secret_key() == 'env-key'


def test_parse_log_line_handles_colons_in_timestamp():
    line = '2026-07-12 10:15:30,123:ERROR:Something failed: badly'
    parsed = parse_log_line(line)
    assert parsed['level'] == 'ERROR'
    assert parsed['message'] == 'Something failed: badly'
    assert parsed['timestamp'] == '2026-07-12 10:15:30,123'


def test_filter_log_lines_by_level():
    lines = [
        '2026-07-12 10:15:30,123:ERROR:boom',
        '2026-07-12 10:15:31,456:INFO:fine',
    ]
    filtered = filter_log_lines(lines, level='error')
    assert len(filtered) == 1
    assert filtered[0]['message'] == 'boom'


def test_wake_job_survives_in_database(client, sample_device):
    job_id = create_wake_job(sample_device['id'])
    update_wake_job(job_id, status='waiting', message_code='WAKE_WAITING', name='NAS')

    # Simulate another worker: expire this session's cache and read from the DB.
    db.session.expire_all()
    assert db.session.get(WakeJob, job_id) is not None

    job = get_wake_job(job_id)
    assert job['status'] == 'waiting'
    assert job['message_code'] == 'WAKE_WAITING'
    assert job['name'] == 'NAS'

    response = client.get(f'/api/wake/jobs/{job_id}')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'waiting'


def test_masked_webhook_url_is_not_saved_on_update(client):
    created = client.post('/api/devices', json={
        'domain': 'hook.test.local',
        'ip': '192.168.1.60',
        'mac': 'AA:BB:CC:DD:EE:60',
        'wake_method': 'webhook',
        'webhook_url': 'https://hooks.example.com/fire?token=supersecret',
    })
    assert created.status_code == 201
    payload = created.get_json()
    assert '***' in payload['webhook_url']

    # The UI echoes the masked URL back on save; the original must survive.
    update = client.put(f"/api/devices/{payload['id']}", json={**payload})
    assert update.status_code == 200

    device = db.session.get(Device, payload['id'])
    assert device.webhook_url == 'https://hooks.example.com/fire?token=supersecret'


def test_group_delete_clears_device_group_id(client, sample_device):
    group = client.post('/api/groups', json={'name': 'Servers'}).get_json()
    updated = client.put(f"/api/devices/{sample_device['id']}", json={**sample_device, 'group_id': group['id']})
    assert updated.status_code == 200

    response = client.delete(f"/api/groups/{group['id']}")
    assert response.status_code == 200

    device = db.session.get(Device, sample_device['id'])
    assert device.group_id is None


def test_schedule_requires_existing_device(client):
    response = client.post('/api/schedules', json={'device_id': 9999, 'hour': 7})
    assert response.status_code == 404


def test_schedule_to_dict_includes_days(client, sample_device):
    response = client.post('/api/schedules', json={'device_id': sample_device['id'], 'hour': 6, 'minute': 30, 'days': [0, 1]})
    assert response.status_code == 201
    data = response.get_json()
    assert data['days'] == [0, 1]


def test_delete_device_with_wake_history(client, sample_device):
    from services.notification_service import record_wake_event

    device = db.session.get(Device, sample_device['id'])
    record_wake_event(device, 'manual', success=True, status='sent')
    schedule = ScheduledWake(device_id=device.id, hour=7, minute=0)
    db.session.add(schedule)
    db.session.commit()

    response = client.delete(f"/api/devices/{device.id}")
    assert response.status_code == 200
    assert db.session.get(Device, sample_device['id']) is None


def test_wake_by_host_query_param(client, sample_device, monkeypatch, api_key):
    monkeypatch.setattr('services.wake_service.check_device_online', lambda device: True)
    response = client.post(
        f"/api/wake/by-host?host={sample_device['domain']}",
        headers={'X-API-Key': api_key},
    )
    assert response.status_code == 200
    assert response.get_json()['domain'] == sample_device['domain']


def test_public_wake_nonblocking_param(client, sample_device, monkeypatch):
    monkeypatch.setattr('services.wake_service.check_device_online', lambda device: True)
    response = client.post(f"/api/public/wake/{sample_device['domain']}?wait=false")
    assert response.status_code == 200
    assert response.get_json()['status'] == 'skipped'
