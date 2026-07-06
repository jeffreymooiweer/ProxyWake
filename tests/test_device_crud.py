"""Tests for device CRUD API."""

import pytest


def test_create_device(client):
    response = client.post(
        '/api/devices',
        json={
            'name': 'Plex',
            'domain': 'plex.home.lab',
            'ip': '192.168.1.60',
            'mac': 'AA:BB:CC:DD:EE:02',
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['domain'] == 'plex.home.lab'
    assert data['mac'] == 'AA:BB:CC:DD:EE:02'


def test_create_device_validation_errors(client):
    response = client.post('/api/devices', json={'domain': 'bad', 'ip': 'x', 'mac': 'invalid'})
    assert response.status_code == 400
    assert response.get_json()['error_code'] in ('INVALID_DOMAIN', 'INVALID_IP', 'INVALID_MAC')


def test_create_device_duplicate_domain(client, sample_device):
    response = client.post(
        '/api/devices',
        json={
            'domain': sample_device['domain'],
            'ip': '192.168.1.99',
            'mac': 'AA:BB:CC:DD:EE:99',
        },
    )
    assert response.status_code == 400
    assert response.get_json()['error_code'] == 'DOMAIN_ALREADY_EXISTS'


def test_list_devices(client, sample_device):
    response = client.get('/api/devices')
    assert response.status_code == 200
    devices = response.get_json()
    assert len(devices) == 1
    assert devices[0]['domain'] == sample_device['domain']


def test_update_device(client, sample_device):
    response = client.put(
        f'/api/devices/{sample_device["id"]}',
        json={
            'name': 'Updated NAS',
            'domain': sample_device['domain'],
            'ip': '192.168.1.51',
            'mac': sample_device['mac'],
        },
    )
    assert response.status_code == 200
    assert response.get_json()['ip'] == '192.168.1.51'
    assert response.get_json()['name'] == 'Updated NAS'


def test_delete_device(client, sample_device):
    response = client.delete(f'/api/devices/{sample_device["id"]}')
    assert response.status_code == 200

    listing = client.get('/api/devices')
    assert listing.get_json() == []
