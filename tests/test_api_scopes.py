"""Tests for scoped API key access."""

import pytest

from config import VALID_API_SCOPES, set_api_key_scopes


@pytest.fixture(autouse=True)
def reset_scopes():
    yield
    set_api_key_scopes(list(VALID_API_SCOPES))


def test_read_scope_allows_list_devices(client, api_key):
    set_api_key_scopes(['read'])
    response = client.get('/api/devices', headers={'X-API-Key': api_key})
    assert response.status_code == 200


def test_wake_scope_required_for_wake(client, sample_device, api_key):
    set_api_key_scopes(['read'])
    response = client.post(
        f'/api/devices/{sample_device["id"]}/wake',
        headers={'X-API-Key': api_key},
    )
    assert response.status_code == 403
    assert response.get_json()['error_code'] == 'INSUFFICIENT_API_SCOPE'


def test_wake_scope_allows_wake(client, sample_device, api_key):
    set_api_key_scopes(['wake'])
    response = client.post(
        f'/api/devices/{sample_device["id"]}/wake',
        headers={'X-API-Key': api_key},
    )
    assert response.status_code == 200


def test_backup_requires_admin_scope(client, api_key):
    set_api_key_scopes(['read'])
    response = client.get('/api/backup', headers={'X-API-Key': api_key})
    assert response.status_code == 403


def test_backup_allows_admin_scope(client, api_key):
    set_api_key_scopes(['admin'])
    response = client.get('/api/backup', headers={'X-API-Key': api_key})
    assert response.status_code == 200


def test_write_scope_required_for_create(client, api_key):
    set_api_key_scopes(['read'])
    response = client.post(
        '/api/devices',
        json={
            'name': 'Blocked',
            'domain': 'blocked.test',
            'ip': '192.168.1.99',
            'mac': 'AA:BB:CC:DD:EE:99',
        },
        headers={'X-API-Key': api_key},
    )
    assert response.status_code == 403
    assert response.get_json()['error_code'] == 'INSUFFICIENT_API_SCOPE'


def test_write_scope_allows_create(client, api_key):
    set_api_key_scopes(['write'])
    response = client.post(
        '/api/devices',
        json={
            'name': 'Allowed',
            'domain': 'allowed.test',
            'ip': '192.168.1.88',
            'mac': 'AA:BB:CC:DD:EE:88',
        },
        headers={'X-API-Key': api_key},
    )
    assert response.status_code == 201


def test_write_scope_required_for_update(client, sample_device, api_key):
    set_api_key_scopes(['read'])
    response = client.put(
        f'/api/devices/{sample_device["id"]}',
        json={
            'name': 'Nope',
            'domain': sample_device['domain'],
            'ip': sample_device['ip'],
            'mac': sample_device['mac'],
        },
        headers={'X-API-Key': api_key},
    )
    assert response.status_code == 403


def test_write_scope_allows_dependency_update(client, sample_device, api_key):
    set_api_key_scopes(['write'])
    response = client.put(
        f'/api/devices/{sample_device["id"]}/dependencies',
        json={'depends_on': []},
        headers={'X-API-Key': api_key},
    )
    assert response.status_code == 200
