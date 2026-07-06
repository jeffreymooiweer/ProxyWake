"""Tests for authentication and API key access."""

import pytest

from auth import hash_password, verify_api_key
from config import get_or_create_api_key, save_admin_password_hash


def test_health_endpoint_is_public(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['version'] == '3.2.0'


def test_devices_require_auth_when_password_set(client, monkeypatch):
    save_admin_password_hash(hash_password('testpassword123'))
    response = client.get('/api/devices')
    assert response.status_code == 401
    assert response.get_json()['error_code'] == 'AUTH_REQUIRED'


def test_login_and_session_access(client):
    save_admin_password_hash(hash_password('testpassword123'))

    login = client.post('/api/auth/login', json={'password': 'testpassword123'})
    assert login.status_code == 200
    assert login.get_json()['message_code'] == 'LOGIN_SUCCESS'

    devices = client.get('/api/devices')
    assert devices.status_code == 200


def test_invalid_login(client):
    save_admin_password_hash(hash_password('testpassword123'))

    login = client.post('/api/auth/login', json={'password': 'wrongpassword'})
    assert login.status_code == 401
    assert login.get_json()['error_code'] == 'INVALID_PASSWORD'


def test_api_key_access(client, api_key):
    save_admin_password_hash(hash_password('testpassword123'))

    response = client.get('/api/devices', headers={'X-API-Key': api_key})
    assert response.status_code == 200


def test_invalid_api_key_rejected(client):
    save_admin_password_hash(hash_password('testpassword123'))
    with client.session_transaction() as sess:
        sess.clear()

    response = client.get('/api/devices', headers={'X-API-Key': 'invalid-key'})
    assert response.status_code == 401


def test_verify_api_key_matches_current():
    key = get_or_create_api_key()
    assert verify_api_key(key) is True
    assert verify_api_key('wrong') is False
