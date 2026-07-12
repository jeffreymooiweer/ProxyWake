from flask import Blueprint, jsonify, request

from auth import api_key_or_session_required, api_key_required, login_required
from config import get_or_create_api_key
from extensions import limiter
from integrations import (
    build_caddy_config,
    build_home_assistant_config,
    build_npm_global_config,
    build_npm_host_config,
    build_traefik_config,
    integration_instructions,
)
from models import Device, NpmHost, db
from services.wake_service import smart_wake_device
from utils.http import get_proxywake_base_url, json_error, json_message

bp = Blueprint('integration', __name__)


@bp.route('/api/npm-hosts')
@login_required
def list_npm_hosts():
    return jsonify([host.to_dict() for host in NpmHost.query.all()])


@bp.route('/api/npm-hosts', methods=['POST'])
@login_required
def create_npm_host():
    data = request.get_json(silent=True) or {}
    host = NpmHost(name=data.get('name'), base_url=data.get('base_url'))
    db.session.add(host)
    db.session.commit()
    return jsonify(host.to_dict()), 201


@bp.route('/api/npm-hosts/<int:host_id>', methods=['DELETE'])
@login_required
def delete_npm_host(host_id):
    host = NpmHost.query.get_or_404(host_id)
    Device.query.filter_by(npm_host_id=host.id).update({'npm_host_id': None})
    db.session.delete(host)
    db.session.commit()
    return json_message('NPM_HOST_DELETED')


@bp.route('/api/wake/by-host', methods=['GET', 'POST'])
@api_key_required
@limiter.limit('60 per minute')
def wake_by_host():
    # The explicit ?host= parameter must beat the implicit Host header, which
    # is always present in HTTP and would otherwise make the parameter dead.
    host = (
        request.headers.get('X-Forwarded-Host')
        or request.args.get('host')
        or request.headers.get('Host')
        or ''
    ).split(':')[0].strip().lower()
    if not host:
        return json_error('HOST_HEADER_MISSING', 400)
    device = Device.query.filter_by(domain=host).first()
    if not device:
        return json_error('DEVICE_NOT_FOUND_FOR_DOMAIN', 404)
    try:
        result = smart_wake_device(device, source='npm')
        return jsonify({'message_code': 'WAKE_PROCESSED', 'domain': device.domain, 'device_id': device.id, **result}), 200
    except Exception:
        return json_error('WAKE_FAILED', 500)


@bp.route('/api/npm/config')
@api_key_or_session_required
def npm_config():
    base_url = request.args.get('base_url') or get_proxywake_base_url()
    api_key = get_or_create_api_key()
    instructions = integration_instructions()
    return jsonify({
        'npm': {'global_config': build_npm_global_config(base_url, api_key), 'host_config': build_npm_host_config(), 'instructions': instructions['npm']},
        'traefik': {'config': build_traefik_config(base_url, api_key), 'instructions': instructions['traefik']},
        'caddy': {'config': build_caddy_config(base_url, api_key), 'instructions': instructions['caddy']},
        'home_assistant': {'instructions': instructions['home_assistant']},
    })


@bp.route('/api/npm/config/<int:device_id>')
@api_key_or_session_required
def npm_config_for_device(device_id):
    device = Device.query.get_or_404(device_id)
    base_url = request.args.get('base_url') or get_proxywake_base_url()
    api_key = get_or_create_api_key()
    return jsonify({
        'device': device.to_dict(),
        'npm': {'global_config': build_npm_global_config(base_url, api_key), 'host_config': build_npm_host_config()},
        'home_assistant': build_home_assistant_config(device.to_dict(), base_url, api_key),
        'test_url': f'{base_url}/api/wake/by-host',
        'test_headers': {'Host': device.domain, 'X-API-Key': api_key},
    })


@bp.route('/api/npm/test/<int:device_id>', methods=['POST'])
@login_required
def npm_test(device_id):
    from flask import current_app

    device = Device.query.get_or_404(device_id)
    api_key = get_or_create_api_key()
    try:
        with current_app.test_client() as client:
            response = client.get(
                '/api/wake/by-host',
                headers={'Host': device.domain, 'X-API-Key': api_key},
            )
        return jsonify({'success': response.status_code == 200, 'status_code': response.status_code, 'body': response.get_json()}), 200
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc)}), 500
