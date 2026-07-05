import csv
import io
import logging
import os
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import func

from auth import (
    _password_matches,
    api_key_or_session_required,
    api_key_required,
    is_auth_configured,
    is_authenticated,
    login_required,
    set_password,
)
from config import DATA_DIR, LOG_FILE, get_allowed_origins, get_or_create_api_key, get_previous_api_key, get_secret_key, rotate_api_key
from integrations import (
    build_caddy_config,
    build_home_assistant_config,
    build_npm_global_config,
    build_npm_host_config,
    build_traefik_config,
    integration_instructions,
)
from models import AuditLog, Device, DeviceGroup, NpmHost, ScheduledWake, WakeEvent, Webhook, db
from services import (
    export_devices,
    get_setting,
    import_devices,
    is_onboarding_complete,
    log_audit,
    migrate_db,
    record_wake_event,
    set_setting,
    smart_wake_device,
    start_scheduler,
    wake_and_wait,
    wake_group,
)
from errors import ERROR_MESSAGES, error_response, message_response

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
app.config['SECRET_KEY'] = get_secret_key()
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATA_DIR / "devices.db"}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

db.init_app(app)

allowed_origins = get_allowed_origins()
if allowed_origins:
    CORS(app, origins=allowed_origins, supports_credentials=True)
else:
    CORS(app, supports_credentials=True)

limiter = Limiter(get_remote_address, app=app, default_limits=['300 per minute'], storage_uri='memory://')
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(filename=str(LOG_FILE), level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')


def validate_device_payload(data, device=None):
    domain = (data.get('domain') or '').strip().lower()
    ip = (data.get('ip') or '').strip()
    mac = normalize_mac((data.get('mac') or '').strip())
    name = (data.get('name') or '').strip() or None

    if not domain or not ip or not mac:
        return None, 'REQUIRED_FIELDS'
    if not is_valid_domain(domain):
        return None, 'INVALID_DOMAIN'
    if not is_valid_ip(ip):
        return None, 'INVALID_IP'
    if not is_valid_mac(mac):
        return None, 'INVALID_MAC'

    existing = Device.query.filter_by(domain=domain).first()
    if existing and (device is None or existing.id != device.id):
        return None, 'DOMAIN_ALREADY_EXISTS'

    group_id = data.get('group_id')
    npm_host_id = data.get('npm_host_id')
    if group_id == '' or group_id is None:
        group_id = None
    else:
        group_id = int(group_id)
    if npm_host_id == '' or npm_host_id is None:
        npm_host_id = None
    else:
        npm_host_id = int(npm_host_id)

    return {
        'domain': domain,
        'ip': ip,
        'mac': mac,
        'name': name,
        'group_id': group_id,
        'npm_host_id': npm_host_id,
        'use_broadcast': bool(data.get('use_broadcast', False)),
        'broadcast_ip': data.get('broadcast_ip'),
        'wake_cooldown_seconds': int(data.get('wake_cooldown_seconds', 30)),
    }, None


def get_proxywake_base_url():
    stored = get_setting('proxywake_url')
    if stored:
        return stored.rstrip('/')
    return (request.headers.get('X-ProxyWake-Base-Url') or request.host_url.rstrip('/')).rstrip('/')


def json_error(code, status=400, **extra):
    body, _ = error_response(code, status, **extra)
    return jsonify(body), status


def json_message(code, status=200, **params):
    body, _ = message_response(code, status, **params)
    return jsonify(body), status


def actor_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr)


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'service': 'ProxyWake', 'version': '3.0'})


@app.route('/api/metrics')
def metrics():
    device_count = Device.query.count()
    wake_total = WakeEvent.query.count()
    wake_success = WakeEvent.query.filter_by(success=True, skipped=False).count()
    lines = [
        '# HELP proxywake_devices_total Total configured devices',
        '# TYPE proxywake_devices_total gauge',
        f'proxywake_devices_total {device_count}',
        '# HELP proxywake_wake_events_total Total wake events',
        '# TYPE proxywake_wake_events_total counter',
        f'proxywake_wake_events_total {wake_total}',
        '# HELP proxywake_wake_success_total Successful wake events',
        '# TYPE proxywake_wake_success_total counter',
        f'proxywake_wake_success_total {wake_success}',
    ]
    return '\n'.join(lines) + '\n', 200, {'Content-Type': 'text/plain; version=0.0.4'}


@app.route('/api/auth/status')
def auth_status():
    return jsonify({
        'authenticated': is_authenticated(),
        'password_required': is_auth_configured(),
        'api_key_configured': bool(get_or_create_api_key()),
        'onboarding_completed': is_onboarding_complete(),
        'theme': get_setting('theme', 'dark'),
        'language': get_setting('language', 'en'),
    })


@app.route('/api/auth/login', methods=['POST'])
@limiter.limit('10 per minute')
def login():
    if not is_auth_configured():
        session['authenticated'] = True
        session.permanent = True
        return json_message('NO_PASSWORD_CONFIGURED')

    data = request.get_json(silent=True) or {}
    password = data.get('password', '')
    if not password or not _password_matches(password):
        return json_error('INVALID_PASSWORD', 401)

    session['authenticated'] = True
    session.permanent = True
    log_audit('login', 'Successful login', actor_ip())
    return json_message('LOGIN_SUCCESS')


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return json_message('LOGOUT_SUCCESS')


@app.route('/api/setup', methods=['POST'])
def setup():
    if is_onboarding_complete() and is_auth_configured():
        return json_error('SETUP_ALREADY_COMPLETE', 400)

    data = request.get_json(silent=True) or {}
    password = data.get('password', '').strip()
    proxywake_url = (data.get('proxywake_url') or '').strip().rstrip('/')

    if password:
        set_password(password)
    if proxywake_url:
        set_setting('proxywake_url', proxywake_url)
    if data.get('theme') in ('dark', 'light'):
        set_setting('theme', data['theme'])
    if data.get('language') in ('en', 'nl', 'de', 'fr'):
        set_setting('language', data['language'])

    set_setting('onboarding_completed', 'true')
    session['authenticated'] = True
    session.permanent = True
    log_audit('setup_complete', 'Initial setup completed', actor_ip())
    body, status = message_response('SETUP_COMPLETE')
    body['api_key'] = get_or_create_api_key()
    return jsonify(body), status


@app.route('/api/settings')
@login_required
def get_settings():
    return jsonify({
        'api_key': get_or_create_api_key(),
        'previous_api_key': get_previous_api_key(),
        'proxywake_url': get_proxywake_base_url(),
        'password_required': is_auth_configured(),
        'theme': get_setting('theme', 'dark'),
        'onboarding_completed': is_onboarding_complete(),
        'language': get_setting('language', 'en'),
    })


@app.route('/api/settings/language', methods=['PUT'])
@login_required
def update_language():
    data = request.get_json(silent=True) or {}
    language = data.get('language', 'en')
    if language not in ('en', 'nl', 'de', 'fr'):
        return json_error('INVALID_LANGUAGE', 400)
    set_setting('language', language)
    return jsonify({'language': language}), 200


@app.route('/api/settings/theme', methods=['PUT'])
@login_required
def update_theme():
    data = request.get_json(silent=True) or {}
    theme = data.get('theme', 'dark')
    if theme not in ('dark', 'light'):
        return json_error('INVALID_THEME', 400)
    set_setting('theme', theme)
    return jsonify({'theme': theme}), 200


@app.route('/api/settings/password', methods=['PUT'])
@login_required
def update_password():
    data = request.get_json(silent=True) or {}
    password = data.get('password', '').strip()
    if len(password) < 8:
        return json_error('PASSWORD_TOO_SHORT', 400)
    set_password(password)
    log_audit('password_changed', None, actor_ip())
    return json_message('PASSWORD_UPDATED')


@app.route('/api/settings/rotate-api-key', methods=['POST'])
@login_required
def rotate_key():
    new_key = rotate_api_key()
    log_audit('api_key_rotated', 'API key rotated', actor_ip())
    body, status = message_response('API_KEY_ROTATED')
    body['api_key'] = new_key
    body['previous_api_key'] = get_previous_api_key()
    return jsonify(body), status


@app.route('/api/devices')
@api_key_or_session_required
def list_devices():
    include_status = request.args.get('status', 'false').lower() == 'true'
    devices = Device.query.order_by(Device.domain.asc()).all()
    return jsonify([device.to_dict(include_status=include_status) for device in devices])


@app.route('/api/devices', methods=['POST'])
@api_key_or_session_required
def create_device():
    data = request.get_json(silent=True) or {}
    payload, error_code = validate_device_payload(data)
    if error_code:
        return json_error(error_code)
    device = Device(**payload)
    db.session.add(device)
    db.session.commit()
    log_audit('device_created', device.domain, actor_ip())
    return jsonify(device.to_dict()), 201


@app.route('/api/devices/<int:device_id>', methods=['PUT', 'DELETE'])
@api_key_or_session_required
def modify_device(device_id):
    device = Device.query.get_or_404(device_id)
    if request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        payload, error_code = validate_device_payload(data, device=device)
        if error_code:
            return json_error(error_code)
        for key, value in payload.items():
            setattr(device, key, value)
        db.session.commit()
        log_audit('device_updated', device.domain, actor_ip())
        return jsonify(device.to_dict()), 200

    domain = device.domain
    db.session.delete(device)
    db.session.commit()
    log_audit('device_deleted', domain, actor_ip())
    return json_message('DEVICE_DELETED')


@app.route('/api/devices/<int:device_id>/wake', methods=['POST'])
@api_key_or_session_required
@limiter.limit('30 per minute')
def wake_device(device_id):
    device = Device.query.get_or_404(device_id)
    force = request.args.get('force', 'false').lower() == 'true'
    try:
        result = smart_wake_device(device, source='manual', force=force)
        return jsonify(result), 200
    except Exception as exc:
        return json_error('WAKE_FAILED', 500)


@app.route('/api/devices/<int:device_id>/status')
@api_key_or_session_required
def device_status(device_id):
    device = Device.query.get_or_404(device_id)
    return jsonify(device.to_dict(include_status=True))


@app.route('/api/devices/export')
@login_required
def export_devices_route():
    fmt = request.args.get('format', 'json')
    devices = export_devices()
    if fmt == 'csv':
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['name', 'domain', 'ip', 'mac', 'use_broadcast', 'wake_cooldown_seconds'])
        writer.writeheader()
        for device in devices:
            writer.writerow({key: device.get(key) for key in writer.fieldnames})
        return output.getvalue(), 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=proxywake-devices.csv'}
    return jsonify({'devices': devices, 'exported_at': datetime.now(timezone.utc).isoformat()})


@app.route('/api/devices/import', methods=['POST'])
@login_required
def import_devices_route():
    data = request.get_json(silent=True) or {}
    devices = data.get('devices', [])
    merge = data.get('merge', True)
    count = import_devices(devices, merge=merge)
    log_audit('devices_imported', f'{count} apparaten', actor_ip())
    return jsonify({'imported': count}), 200


@app.route('/api/groups')
@api_key_or_session_required
def list_groups():
    return jsonify([group.to_dict() for group in DeviceGroup.query.all()])


@app.route('/api/groups', methods=['POST'])
@login_required
def create_group():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return json_error('GROUP_NAME_REQUIRED', 400)
    group = DeviceGroup(name=name, color=data.get('color', '#6366f1'))
    db.session.add(group)
    db.session.commit()
    return jsonify(group.to_dict()), 201


@app.route('/api/groups/<int:group_id>/wake', methods=['POST'])
@api_key_or_session_required
def wake_group_route(group_id):
    DeviceGroup.query.get_or_404(group_id)
    return jsonify({'results': wake_group(group_id)}), 200


@app.route('/api/groups/<int:group_id>', methods=['PUT', 'DELETE'])
@login_required
def modify_group(group_id):
    group = DeviceGroup.query.get_or_404(group_id)
    if request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        group.name = data.get('name', group.name)
        group.color = data.get('color', group.color)
        db.session.commit()
        return jsonify(group.to_dict()), 200
    db.session.delete(group)
    db.session.commit()
    return json_message('GROUP_DELETED')


@app.route('/api/npm-hosts')
@login_required
def list_npm_hosts():
    return jsonify([host.to_dict() for host in NpmHost.query.all()])


@app.route('/api/npm-hosts', methods=['POST'])
@login_required
def create_npm_host():
    data = request.get_json(silent=True) or {}
    host = NpmHost(name=data.get('name'), base_url=data.get('base_url'))
    db.session.add(host)
    db.session.commit()
    return jsonify(host.to_dict()), 201


@app.route('/api/npm-hosts/<int:host_id>', methods=['DELETE'])
@login_required
def delete_npm_host(host_id):
    host = NpmHost.query.get_or_404(host_id)
    db.session.delete(host)
    db.session.commit()
    return json_message('NPM_HOST_DELETED')


@app.route('/api/wake/by-host', methods=['GET', 'POST'])
@api_key_required
@limiter.limit('60 per minute')
def wake_by_host():
    host = (
        request.headers.get('X-Forwarded-Host')
        or request.headers.get('Host')
        or request.args.get('host')
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
    except Exception as exc:
        return json_error('WAKE_FAILED', 500)


@app.route('/api/public/status/<domain>')
@limiter.limit('120 per minute')
def public_status(domain):
    device = Device.query.filter_by(domain=domain.lower()).first()
    if not device:
        return json_error('DEVICE_NOT_FOUND', 404)
    return jsonify({
        'domain': device.domain,
        'name': device.name or device.domain,
        'online': device.to_dict(include_status=True)['online'],
    })


@app.route('/api/public/wake/<domain>', methods=['POST'])
@limiter.limit('30 per minute')
def public_wake(domain):
    device = Device.query.filter_by(domain=domain.lower()).first()
    if not device:
        return json_error('DEVICE_NOT_FOUND', 404)
    result = wake_and_wait(device, source='public')
    return jsonify(result), 200


@app.route('/api/npm/config')
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


@app.route('/api/npm/config/<int:device_id>')
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


@app.route('/api/npm/test/<int:device_id>', methods=['POST'])
@login_required
def npm_test(device_id):
    device = Device.query.get_or_404(device_id)
    api_key = get_or_create_api_key()
    try:
        with app.test_client() as client:
            response = client.get(
                '/api/wake/by-host',
                headers={'Host': device.domain, 'X-API-Key': api_key},
            )
        return jsonify({'success': response.status_code == 200, 'status_code': response.status_code, 'body': response.get_json()}), 200
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc)}), 500


@app.route('/api/webhooks')
@login_required
def list_webhooks():
    return jsonify([hook.to_dict() for hook in Webhook.query.all()])


@app.route('/api/webhooks', methods=['POST'])
@login_required
def create_webhook():
    data = request.get_json(silent=True) or {}
    hook = Webhook(
        name=data.get('name'),
        url=data.get('url'),
        events=','.join(data.get('events', ['wake_failed', 'wake_success'])),
        enabled=data.get('enabled', True),
    )
    db.session.add(hook)
    db.session.commit()
    return jsonify(hook.to_dict()), 201


@app.route('/api/webhooks/<int:hook_id>', methods=['PUT', 'DELETE'])
@login_required
def modify_webhook(hook_id):
    hook = Webhook.query.get_or_404(hook_id)
    if request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        hook.name = data.get('name', hook.name)
        hook.url = data.get('url', hook.url)
        hook.events = ','.join(data.get('events', hook.events.split(',')))
        hook.enabled = data.get('enabled', hook.enabled)
        db.session.commit()
        return jsonify(hook.to_dict()), 200
    db.session.delete(hook)
    db.session.commit()
    return json_message('WEBHOOK_DELETED')


@app.route('/api/schedules')
@login_required
def list_schedules():
    return jsonify([item.to_dict() for item in ScheduledWake.query.all()])


@app.route('/api/schedules', methods=['POST'])
@login_required
def create_schedule():
    data = request.get_json(silent=True) or {}
    schedule = ScheduledWake(
        device_id=data.get('device_id'),
        hour=int(data.get('hour', 7)),
        minute=int(data.get('minute', 0)),
        days=','.join(str(day) for day in data.get('days', [0, 1, 2, 3, 4, 5, 6])),
        enabled=data.get('enabled', True),
    )
    db.session.add(schedule)
    db.session.commit()
    return jsonify(schedule.to_dict()), 201


@app.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
@login_required
def delete_schedule(schedule_id):
    schedule = ScheduledWake.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    return json_message('SCHEDULE_DELETED')


@app.route('/api/stats')
@login_required
def stats():
    since = datetime.now(timezone.utc) - timedelta(days=7)
    total = WakeEvent.query.count()
    week = WakeEvent.query.filter(WakeEvent.created_at >= since).count()
    successes = WakeEvent.query.filter_by(success=True, skipped=False).count()
    per_day = db.session.query(
        func.date(WakeEvent.created_at),
        func.count(WakeEvent.id),
    ).filter(WakeEvent.created_at >= since).group_by(func.date(WakeEvent.created_at)).all()

    device_stats = []
    for device in Device.query.all():
        events = WakeEvent.query.filter_by(device_id=device.id).order_by(WakeEvent.created_at.desc()).limit(5).all()
        avg_wake = db.session.query(func.avg(WakeEvent.online_after_ms)).filter(
            WakeEvent.device_id == device.id,
            WakeEvent.online_after_ms.isnot(None),
        ).scalar()
        device_stats.append({
            'device': device.to_dict(include_status=True),
            'wake_count': WakeEvent.query.filter_by(device_id=device.id).count(),
            'avg_wake_ms': int(avg_wake) if avg_wake else None,
            'recent_events': [event.to_dict() for event in events],
        })

    return jsonify({
        'total_wake_events': total,
        'wake_events_7d': week,
        'successful_wakes': successes,
        'per_day': [{'date': str(day), 'count': count} for day, count in per_day],
        'devices': device_stats,
    })


@app.route('/api/wake-events')
@login_required
def wake_events():
    limit = min(int(request.args.get('limit', 50)), 200)
    events = WakeEvent.query.order_by(WakeEvent.created_at.desc()).limit(limit).all()
    return jsonify([event.to_dict() for event in events])


@app.route('/api/audit')
@login_required
def audit_logs():
    limit = min(int(request.args.get('limit', 100)), 300)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return jsonify([log.to_dict() for log in logs])


@app.route('/api/scan', methods=['POST'])
@login_required
@limiter.limit('5 per minute')
def scan_network():
    data = request.get_json(silent=True) or {}
    subnet = data.get('subnet')
    if not subnet and data.get('ip'):
        subnet = subnet_from_ip(data['ip'])
    if not subnet:
        return json_error('SUBNET_REQUIRED', 400)
    hosts = scan_subnet(subnet, max_hosts=int(data.get('max_hosts', 64)))
    return jsonify({'subnet': subnet, 'hosts': hosts})


@app.route('/api/logs')
@login_required
def get_logs():
    lines = min(int(request.args.get('lines', 100)), 500)
    if not LOG_FILE.exists():
        return jsonify({'logs': []}), 200
    content = LOG_FILE.read_text(encoding='utf-8', errors='replace').splitlines()
    return jsonify({'logs': content[-lines:]})


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path.startswith('api/'):
        return json_error('NOT_FOUND', 404)
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


@app.errorhandler(404)
def not_found(_error):
    if request.path.startswith('/api/'):
        return json_error('NOT_FOUND', 404)
    return send_from_directory(app.static_folder, 'index.html')


@app.errorhandler(429)
def rate_limited(_error):
    return json_error('RATE_LIMITED', 429)


with app.app_context():
    migrate_db(db.engine)
    db.create_all()
    start_scheduler(app)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
