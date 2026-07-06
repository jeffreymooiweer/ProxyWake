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
