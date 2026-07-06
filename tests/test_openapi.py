"""Tests for OpenAPI documentation endpoints."""


def test_openapi_json_available(client):
    response = client.get('/api/openapi.json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['openapi'].startswith('3.0')
    assert data['info']['title'] == 'ProxyWake API'
    assert '/api/devices' in data['paths']


def test_swagger_ui_available(client):
    response = client.get('/api/docs')
    assert response.status_code == 200
    assert b'swagger-ui' in response.data.lower()
