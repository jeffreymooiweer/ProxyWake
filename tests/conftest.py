"""Pytest configuration and shared fixtures for ProxyWake backend tests."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent / 'backend'
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

SESSION_DATA_DIR = tempfile.mkdtemp(prefix='proxywake-pytest-')
os.environ['PROXYWAKE_DATA_DIR'] = SESSION_DATA_DIR
os.environ['PROXYWAKE_SECRET_KEY'] = 'pytest-secret-key-do-not-use-in-production'

from app import app  # noqa: E402
from extensions import limiter  # noqa: E402
from config import PASSWORD_HASH_FILE  # noqa: E402
from models import (  # noqa: E402
    AppSetting,
    AuditLog,
    Device,
    DeviceCredential,
    DeviceDependency,
    DeviceGroup,
    NpmHost,
    ScheduledWake,
    WakeEvent,
    Webhook,
    db,
)


@pytest.fixture(autouse=True)
def disable_rate_limiter():
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client
            _clear_database()


def _clear_database():
    for model in (
        WakeEvent,
        ScheduledWake,
        Webhook,
        AuditLog,
        DeviceDependency,
        DeviceCredential,
        Device,
        DeviceGroup,
        NpmHost,
        AppSetting,
    ):
        model.query.delete()
    db.session.commit()
    if PASSWORD_HASH_FILE.exists():
        PASSWORD_HASH_FILE.unlink()


@pytest.fixture
def sample_device(client):
    response = client.post(
        '/api/devices',
        json={
            'name': 'Test NAS',
            'domain': 'nas.test.local',
            'ip': '192.168.1.50',
            'mac': 'AA:BB:CC:DD:EE:FF',
            'wake_cooldown_seconds': 30,
        },
    )
    assert response.status_code == 201
    return response.get_json()


@pytest.fixture
def api_key(client):
    response = client.get('/api/settings')
    assert response.status_code == 200
    return response.get_json()['api_key']
