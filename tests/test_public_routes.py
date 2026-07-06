"""Tests for unauthenticated public API routes."""

from unittest.mock import patch


def test_public_status_unknown_domain(client):
    response = client.get('/api/public/status/unknown.example')
    assert response.status_code == 404
    assert response.get_json()['error_code'] == 'DEVICE_NOT_FOUND'


@patch('services.status_service.check_device_online', return_value=True)
def test_public_status_known_domain(mock_online, client, sample_device):
    response = client.get(f'/api/public/status/{sample_device["domain"]}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['domain'] == sample_device['domain']
    assert data['online'] is True
    mock_online.assert_called_once()


def test_public_status_is_case_insensitive(client, sample_device):
    domain = sample_device['domain'].upper()
    with patch('services.status_service.check_device_online', return_value=False):
        response = client.get(f'/api/public/status/{domain}')
    assert response.status_code == 200
    assert response.get_json()['online'] is False


@patch('routes.public_routes.wake_and_wait', return_value={'status': 'online', 'waited_seconds': 0})
def test_public_wake_known_domain(mock_wake, client, sample_device):
    response = client.post(f'/api/public/wake/{sample_device["domain"]}')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'online'
    mock_wake.assert_called_once()


def test_public_wake_unknown_domain(client):
    response = client.post('/api/public/wake/missing.example')
    assert response.status_code == 404
    assert response.get_json()['error_code'] == 'DEVICE_NOT_FOUND'
