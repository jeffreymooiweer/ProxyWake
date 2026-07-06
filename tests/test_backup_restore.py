"""Tests for full backup and restore."""

from models import Device, DeviceGroup, Webhook, db
from services.backup_service import create_backup, restore_backup


def test_create_backup_contains_devices(client, sample_device):
    backup = create_backup()
    assert backup['backup_version'] == '3.5'
    assert len(backup['devices']) == 1
    assert backup['devices'][0]['domain'] == sample_device['domain']


def test_restore_backup_imports_devices(client):
    payload = {
        'devices': [{
            'domain': 'restored.test.local',
            'ip': '192.168.1.99',
            'mac': 'AA:BB:CC:DD:EE:99',
            'name': 'Restored',
            'wake_method': 'wol',
        }],
        'groups': [{'name': 'Lab', 'color': '#123456'}],
        'webhooks': [{
            'name': 'Alerts',
            'url': 'https://example.com/hook',
            'events': ['wake_failed'],
            'enabled': True,
        }],
    }
    summary = restore_backup(payload, merge=True)
    assert summary['devices'] == 1
    assert Device.query.filter_by(domain='restored.test.local').count() == 1
    assert DeviceGroup.query.filter_by(name='Lab').count() == 1
    assert Webhook.query.filter_by(url='https://example.com/hook').count() == 1
