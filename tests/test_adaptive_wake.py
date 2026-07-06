"""Tests for adaptive wake timeout calculation."""

from models import Device, db
from services.adaptive_wake_service import effective_wake_timeout


def test_effective_timeout_uses_configured_when_no_history(client):
    device = Device(
        name='New',
        domain='new.test.local',
        ip='192.168.1.80',
        mac='AA:BB:CC:DD:EE:80',
        wake_timeout_seconds=120,
    )
    assert effective_wake_timeout(device) == 120


def test_effective_timeout_extends_from_last_wake(client):
    device = Device(
        name='Slow',
        domain='slow.test.local',
        ip='192.168.1.81',
        mac='AA:BB:CC:DD:EE:81',
        wake_timeout_seconds=120,
        last_wake_duration_seconds=180,
    )
    db.session.add(device)
    db.session.commit()
    assert effective_wake_timeout(device) == 285
