import hashlib
import hmac
from functools import wraps

from flask import jsonify, request, session

from config import get_admin_password, get_or_create_api_key


def _password_matches(candidate):
    stored = get_admin_password()
    if not stored:
        return True
    return hmac.compare_digest(
        hashlib.sha256(candidate.encode()).hexdigest(),
        hashlib.sha256(stored.encode()).hexdigest(),
    )


def is_auth_configured():
    return bool(get_admin_password())


def is_authenticated():
    if not is_auth_configured():
        return True
    return session.get('authenticated') is True


def verify_api_key(provided_key):
    if not provided_key:
        return False
    expected = get_or_create_api_key()
    return hmac.compare_digest(provided_key.strip(), expected)


def get_request_api_key():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.lower().startswith('bearer '):
        return auth_header[7:].strip()
    return request.headers.get('X-API-Key', '').strip()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if is_authenticated():
            return f(*args, **kwargs)
        return jsonify({'error': 'Authenticatie vereist.'}), 401

    return decorated


def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if verify_api_key(get_request_api_key()):
            return f(*args, **kwargs)
        return jsonify({'error': 'Ongeldige of ontbrekende API-sleutel.'}), 401

    return decorated


def api_key_or_session_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if is_authenticated() or verify_api_key(get_request_api_key()):
            return f(*args, **kwargs)
        return jsonify({'error': 'Authenticatie vereist.'}), 401

    return decorated
