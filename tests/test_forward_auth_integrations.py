"""Tests for the Traefik forwardAuth / Caddy forward_auth integration flow.

The requests below mirror exactly what those middlewares send:
- Traefik forwardAuth: GET to the configured address (query params included),
  original domain in X-Forwarded-Host, plus X-Forwarded-Method/Uri/Proto.
- Caddy forward_auth: GET with the rewritten uri, original Host preserved,
  X-Forwarded-Host set by the underlying reverse_proxy.
Neither can attach custom headers, hence the api_key query parameter.
"""

from unittest.mock import patch

from models import WakeEvent


def _online(monkeypatch):
    monkeypatch.setattr('services.wake_service.check_device_online', lambda device: True)


def test_traefik_forwardauth_request_shape(client, sample_device, api_key, monkeypatch):
    _online(monkeypatch)
    response = client.get(
        f'/api/wake/by-host?api_key={api_key}',
        headers={
            'X-Forwarded-Host': sample_device['domain'],
            'X-Forwarded-Method': 'GET',
            'X-Forwarded-Proto': 'https',
            'X-Forwarded-Uri': '/some/deep/path?x=1',
            'X-Forwarded-For': '192.168.1.99',
        },
    )
    assert response.status_code == 200
    assert response.get_json()['domain'] == sample_device['domain']


def test_caddy_forward_auth_request_shape(client, sample_device, api_key, monkeypatch):
    _online(monkeypatch)
    response = client.get(
        f'/api/wake/by-host?api_key={api_key}',
        headers={
            'Host': sample_device['domain'],
            'X-Forwarded-Host': sample_device['domain'],
            'X-Forwarded-Method': 'GET',
            'X-Forwarded-Uri': '/',
        },
    )
    assert response.status_code == 200
    assert response.get_json()['domain'] == sample_device['domain']


def test_api_key_query_param_rejected_when_invalid(client, sample_device):
    response = client.get(
        '/api/wake/by-host?api_key=wrong-key',
        headers={'X-Forwarded-Host': sample_device['domain']},
    )
    assert response.status_code == 401


def test_header_key_takes_precedence_over_query(client, sample_device, api_key, monkeypatch):
    _online(monkeypatch)
    response = client.get(
        f'/api/wake/by-host?api_key={api_key}',
        headers={'X-API-Key': 'wrong-key', 'X-Forwarded-Host': sample_device['domain']},
    )
    assert response.status_code == 401


def test_wake_by_host_offline_sends_wake(client, sample_device, api_key, monkeypatch):
    monkeypatch.setattr('services.wake_service.check_device_online', lambda device: False)
    with patch('services.wake_service.execute_wake_action') as execute:
        response = client.get(
            f'/api/wake/by-host?api_key={api_key}',
            headers={'X-Forwarded-Host': sample_device['domain']},
        )
    assert response.status_code == 200
    assert response.get_json()['status'] == 'sent'
    execute.assert_called_once()


def test_by_host_skips_are_not_recorded(client, sample_device, api_key, monkeypatch):
    _online(monkeypatch)
    for _ in range(5):
        response = client.get(
            f'/api/wake/by-host?api_key={api_key}',
            headers={'X-Forwarded-Host': sample_device['domain']},
        )
        assert response.status_code == 200
    # Forward-auth routes every proxied request through here; skipped events
    # must not flood the wake_event table.
    assert WakeEvent.query.count() == 0


def test_invalid_key_brute_force_is_rate_limited(client, sample_device):
    """The limiter must wrap the auth decorator: with auth on the outside a
    401 was returned before the limit was ever counted, so API-key
    brute-force ran unthrottled."""
    from extensions import limiter

    limiter.reset()
    limiter.enabled = True
    try:
        codes = [
            client.get(
                '/api/wake/by-host?api_key=wrong-key',
                headers={'X-Forwarded-Host': sample_device['domain']},
            ).status_code
            for _ in range(65)
        ]
    finally:
        limiter.enabled = False
        limiter.reset()
    assert 429 in codes
    assert codes[0] == 401


def test_valid_key_is_exempt_from_rate_limit(client, sample_device, api_key, monkeypatch):
    from extensions import limiter

    _online(monkeypatch)
    limiter.reset()
    limiter.enabled = True
    try:
        codes = [
            client.get(
                f'/api/wake/by-host?api_key={api_key}',
                headers={'X-Forwarded-Host': sample_device['domain']},
            ).status_code
            for _ in range(65)
        ]
    finally:
        limiter.enabled = False
        limiter.reset()
    assert all(code == 200 for code in codes)


def test_generated_traefik_snippet_is_forwardauth(client, api_key):
    response = client.get('/api/npm/config')
    config = response.get_json()['traefik']['config']
    assert 'forwardauth.address=' in config
    assert f'/api/wake/by-host?api_key={api_key}' in config
    assert 'plugin.webhook' not in config


def test_generated_caddy_snippet_is_forward_auth(client, api_key):
    response = client.get('/api/npm/config')
    config = response.get_json()['caddy']['config']
    assert 'forward_auth' in config
    assert f'/api/wake/by-host?api_key={api_key}' in config
    assert 'handle_errors 502 504' in config
    assert '/waiting?domain={host}' in config
