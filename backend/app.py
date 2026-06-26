import logging
import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from wakeonlan import send_magic_packet

from auth import (
    api_key_or_session_required,
    api_key_required,
    get_request_api_key,
    is_auth_configured,
    is_authenticated,
    login_required,
    verify_api_key,
)
from config import DATA_DIR, DB_PATH, LOG_FILE, get_allowed_origins, get_or_create_api_key, get_secret_key
from utils import check_host_online, is_valid_domain, is_valid_ip, is_valid_mac, normalize_mac

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
app.config['SECRET_KEY'] = get_secret_key()
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

allowed_origins = get_allowed_origins()
if allowed_origins:
    CORS(app, origins=allowed_origins, supports_credentials=True)
else:
    CORS(app, supports_credentials=True)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=['200 per minute'],
    storage_uri='memory://',
)

DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s',
)

db = SQLAlchemy(app)


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False, unique=True)
    ip = db.Column(db.String(15), nullable=False)
    mac = db.Column(db.String(17), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self, include_status=False):
        payload = {
            'id': self.id,
            'domain': self.domain,
            'ip': self.ip,
            'mac': self.mac,
            'name': self.name or self.domain,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_status:
            payload['online'] = check_host_online(self.ip)
        return payload


def validate_device_payload(data, device=None):
    domain = (data.get('domain') or '').strip().lower()
    ip = (data.get('ip') or '').strip()
    mac = normalize_mac((data.get('mac') or '').strip())
    name = (data.get('name') or '').strip() or None

    if not domain or not ip or not mac:
        return None, 'Alle verplichte velden moeten ingevuld zijn.'

    if not is_valid_domain(domain):
        return None, 'Ongeldige domeinnaam.'

    if not is_valid_ip(ip):
        return None, 'Ongeldig IP-adres.'

    if not is_valid_mac(mac):
        return None, 'Ongeldig MAC-adres (formaat: AA:BB:CC:DD:EE:FF).'

    existing = Device.query.filter_by(domain=domain).first()
    if existing and (device is None or existing.id != device.id):
        return None, 'Dit domein is al gekoppeld aan een ander apparaat.'

    return {'domain': domain, 'ip': ip, 'mac': mac, 'name': name}, None


def send_wake_packet(device):
    send_magic_packet(device.mac, ip_address=device.ip)
    logging.info('Magic Packet verzonden naar %s (%s)', device.domain, device.ip)


def get_proxywake_base_url():
    return (request.headers.get('X-ProxyWake-Base-Url') or request.host_url.rstrip('/')).rstrip('/')


def build_npm_global_config(base_url, api_key):
    return f"""# ProxyWake - Globale configuratie (eenmalig)
# Plak dit in NPM: Settings > Custom Locations > of /data/nginx/custom/server_proxy.conf
#
# Vervang PROXYWAKE_HOST indien nodig door het IP van je ProxyWake-server.

location = /_proxywake_trigger {{
    internal;
    proxy_pass {base_url}/api/wake/by-host;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-API-Key "{api_key}";
    proxy_connect_timeout 2s;
    proxy_read_timeout 2s;
}}
"""


def build_npm_host_config():
    return """# ProxyWake - Voeg dit toe aan Advanced van deze proxy host
mirror /_proxywake_trigger;
mirror_request_body off;
"""


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'ProxyWake'}), 200


@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    return jsonify({
        'authenticated': is_authenticated(),
        'password_required': is_auth_configured(),
        'api_key_configured': bool(get_or_create_api_key()),
    }), 200


@app.route('/api/auth/login', methods=['POST'])
@limiter.limit('10 per minute')
def login():
    if not is_auth_configured():
        session['authenticated'] = True
        session.permanent = True
        return jsonify({'message': 'Geen wachtwoord geconfigureerd, sessie gestart.'}), 200

    data = request.get_json(silent=True) or {}
    password = data.get('password', '')
    if not password:
        return jsonify({'error': 'Wachtwoord is vereist.'}), 400

    from auth import _password_matches
    if not _password_matches(password):
        logging.warning('Mislukte loginpoging vanaf %s', request.remote_addr)
        return jsonify({'error': 'Onjuist wachtwoord.'}), 401

    session['authenticated'] = True
    session.permanent = True
    logging.info('Succesvolle login vanaf %s', request.remote_addr)
    return jsonify({'message': 'Succesvol ingelogd.'}), 200


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Uitgelogd.'}), 200


@app.route('/api/settings', methods=['GET'])
@login_required
def get_settings():
    return jsonify({
        'api_key': get_or_create_api_key(),
        'proxywake_url': get_proxywake_base_url(),
        'password_required': is_auth_configured(),
    }), 200


@app.route('/api/devices', methods=['GET'])
@api_key_or_session_required
def list_devices():
    include_status = request.args.get('status', 'false').lower() == 'true'
    devices = Device.query.order_by(Device.domain.asc()).all()
    return jsonify([device.to_dict(include_status=include_status) for device in devices]), 200


@app.route('/api/devices', methods=['POST'])
@api_key_or_session_required
def create_device():
    data = request.get_json(silent=True) or {}
    payload, error = validate_device_payload(data)
    if error:
        return jsonify({'error': error}), 400

    device = Device(**payload)
    try:
        db.session.add(device)
        db.session.commit()
        logging.info('Apparaat toegevoegd: %s', device.domain)
        return jsonify(device.to_dict()), 201
    except Exception as exc:
        db.session.rollback()
        logging.error('Fout bij toevoegen apparaat: %s', exc)
        return jsonify({'error': 'Fout bij toevoegen apparaat.'}), 500


@app.route('/api/devices/<int:device_id>', methods=['PUT', 'DELETE'])
@api_key_or_session_required
def modify_device(device_id):
    device = Device.query.get_or_404(device_id)

    if request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        payload, error = validate_device_payload(data, device=device)
        if error:
            return jsonify({'error': error}), 400

        device.domain = payload['domain']
        device.ip = payload['ip']
        device.mac = payload['mac']
        device.name = payload['name']

        try:
            db.session.commit()
            logging.info('Apparaat bijgewerkt: %s', device.domain)
            return jsonify(device.to_dict()), 200
        except Exception as exc:
            db.session.rollback()
            logging.error('Fout bij bijwerken apparaat: %s', exc)
            return jsonify({'error': 'Fout bij bijwerken apparaat.'}), 500

    try:
        db.session.delete(device)
        db.session.commit()
        logging.info('Apparaat verwijderd: %s', device.domain)
        return jsonify({'message': 'Apparaat verwijderd.'}), 200
    except Exception as exc:
        db.session.rollback()
        logging.error('Fout bij verwijderen apparaat: %s', exc)
        return jsonify({'error': 'Fout bij verwijderen apparaat.'}), 500


@app.route('/api/devices/<int:device_id>/wake', methods=['POST'])
@api_key_or_session_required
@limiter.limit('30 per minute')
def wake_device(device_id):
    device = Device.query.get_or_404(device_id)
    try:
        send_wake_packet(device)
        return jsonify({'message': f'Magic Packet verzonden naar {device.name or device.domain}'}), 200
    except Exception as exc:
        logging.error('Fout bij verzenden Magic Packet naar %s: %s', device.domain, exc)
        return jsonify({'error': 'Fout bij verzenden Magic Packet.'}), 500


@app.route('/api/devices/<int:device_id>/status', methods=['GET'])
@api_key_or_session_required
def device_status(device_id):
    device = Device.query.get_or_404(device_id)
    online = check_host_online(device.ip)
    return jsonify({'id': device.id, 'online': online, 'ip': device.ip}), 200


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
        return jsonify({'error': 'Host-header ontbreekt.'}), 400

    device = Device.query.filter_by(domain=host).first()
    if not device:
        logging.warning('Wake-aanvraag voor onbekend domein: %s', host)
        return jsonify({'error': 'Geen apparaat gevonden voor dit domein.'}), 404

    try:
        send_wake_packet(device)
        return jsonify({'message': f'Wake verzonden voor {device.domain}', 'device_id': device.id}), 200
    except Exception as exc:
        logging.error('Fout bij wake-by-host voor %s: %s', host, exc)
        return jsonify({'error': 'Fout bij verzenden Magic Packet.'}), 500


@app.route('/api/npm/config', methods=['GET'])
@api_key_or_session_required
def npm_config():
    base_url = request.args.get('base_url') or get_proxywake_base_url()
    api_key = get_or_create_api_key()
    return jsonify({
        'global_config': build_npm_global_config(base_url, api_key),
        'host_config': build_npm_host_config(),
        'instructions': [
            'Voeg de globale configuratie eenmalig toe in NPM (Custom Nginx Configuration).',
            'Voeg per proxy host de host-configuratie toe onder Advanced.',
            'Zorg dat ProxyWake bereikbaar is vanaf je NPM-container op het netwerk.',
            'Bij het eerste bezoek aan een domein wordt automatisch een Magic Packet verstuurd.',
        ],
    }), 200


@app.route('/api/npm/config/<int:device_id>', methods=['GET'])
@api_key_or_session_required
def npm_config_for_device(device_id):
    device = Device.query.get_or_404(device_id)
    base_url = request.args.get('base_url') or get_proxywake_base_url()
    api_key = get_or_create_api_key()
    return jsonify({
        'device': device.to_dict(),
        'global_config': build_npm_global_config(base_url, api_key),
        'host_config': build_npm_host_config(),
        'test_url': f'{base_url}/api/wake/by-host',
        'test_headers': {'Host': device.domain, 'X-API-Key': api_key},
    }), 200


@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    lines = min(int(request.args.get('lines', 100)), 500)
    if not LOG_FILE.exists():
        return jsonify({'logs': []}), 200

    try:
        content = LOG_FILE.read_text(encoding='utf-8', errors='replace').splitlines()
        return jsonify({'logs': content[-lines:]}), 200
    except OSError as exc:
        logging.error('Fout bij lezen logbestand: %s', exc)
        return jsonify({'error': 'Kon logboek niet lezen.'}), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path.startswith('api/'):
        return jsonify({'error': 'Resource niet gevonden.'}), 404
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


@app.errorhandler(404)
def not_found(_error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Resource niet gevonden.'}), 404
    return send_from_directory(app.static_folder, 'index.html')


@app.errorhandler(429)
def rate_limited(_error):
    return jsonify({'error': 'Te veel verzoeken. Probeer het later opnieuw.'}), 429


@app.errorhandler(500)
def internal_error(_error):
    return jsonify({'error': 'Interne serverfout.'}), 500


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
