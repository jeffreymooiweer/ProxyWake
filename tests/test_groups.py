"""Tests for device group API."""

from unittest.mock import patch

import pytest

from auth import hash_password, save_admin_password_hash
from config import set_api_key_scopes


@pytest.fixture
def logged_in_client(client):
    save_admin_password_hash(hash_password('testpassword123'))
    login = client.post('/api/auth/login', json={'password': 'testpassword123'})
    assert login.status_code == 200
    return client


def test_list_groups_empty(client, api_key):
    set_api_key_scopes(['read'])
    response = client.get('/api/groups', headers={'X-API-Key': api_key})
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_group_requires_session(client, api_key):
    save_admin_password_hash(hash_password('testpassword123'))
    set_api_key_scopes(['write', 'admin'])
    response = client.post(
        '/api/groups',
        json={'name': 'Media'},
        headers={'X-API-Key': api_key},
    )
    assert response.status_code == 401


def test_create_and_list_group(logged_in_client):
    create = logged_in_client.post('/api/groups', json={'name': 'Media', 'color': '#39ff14'})
    assert create.status_code == 201
    group = create.get_json()
    assert group['name'] == 'Media'

    listing = logged_in_client.get('/api/groups')
    assert listing.status_code == 200
    assert len(listing.get_json()) == 1


def test_group_wake_requires_wake_scope(logged_in_client, api_key):
    group = logged_in_client.post('/api/groups', json={'name': 'Lab'}).get_json()
    set_api_key_scopes(['read'])
    response = logged_in_client.post(
        f'/api/groups/{group["id"]}/wake',
        headers={'X-API-Key': api_key},
    )
    assert response.status_code == 403
    assert response.get_json()['error_code'] == 'INSUFFICIENT_API_SCOPE'


@patch('services.wake_service.check_device_online', return_value=False)
@patch('services.wake_service.execute_wake_action')
def test_group_wake_with_wake_scope(mock_wake, mock_online, logged_in_client, api_key):
    group = logged_in_client.post('/api/groups', json={'name': 'Wakeables'}).get_json()
    device = logged_in_client.post(
        '/api/devices',
        json={
            'name': 'NAS',
            'domain': 'nas.group.test',
            'ip': '192.168.1.50',
            'mac': 'AA:BB:CC:DD:EE:01',
            'group_id': group['id'],
        },
    ).get_json()

    set_api_key_scopes(['wake'])
    response = logged_in_client.post(
        f'/api/groups/{group["id"]}/wake',
        headers={'X-API-Key': api_key},
    )
    assert response.status_code == 200
    results = response.get_json()['results']
    assert len(results) == 1
    assert results[0]['device_id'] == device['id']
    assert results[0]['message_code'] == 'WAKE_SENT'
    mock_wake.assert_called_once()
