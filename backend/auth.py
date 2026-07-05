import bcrypt
from functools import wraps

from flask import jsonify, request, session

from config import (
    get_admin_password_hash,
    get_or_create_api_key,
    get_previous_api_key,
    save_admin_password_hash,
)
from errors import ERROR_MESSAGES


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _password_matches(candidate):
    stored = get_admin_password_hash()
    if not stored:
        return True
    try:
        return bcrypt.checkpw(candidate.encode(), stored.encode())
    except ValueError:
        return False


def is_auth_configured():
    return bool(get_admin_password_hash())


def is_authenticated():
    if not is_auth_configured():
        return True
    return session.get('authenticated') is True


def verify_api_key(provided_key):
    if not provided_key:
        return False
    provided_key = provided_key.strip()
    current = get_or_create_api_key()
    previous = get_previous_api_key()
    if provided_key == current:
        return True
    if previous and provided_key == previous:
        return True
    return False


def get_request_api_key():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.lower().startswith('bearer '):
        return auth_header[7:].strip()
    return request.headers.get('X-API-Key', '').strip()


def set_password(password):
    save_admin_password_hash(hash_password(password))


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if is_authenticated():
            return f(*args, **kwargs)
        return jsonify({'error': ERROR_MESSAGES['AUTH_REQUIRED'], 'error_code': 'AUTH_REQUIRED'}), 401

    return decorated


def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if verify_api_key(get_request_api_key()):
            return f(*args, **kwargs)
        return jsonify({'error': ERROR_MESSAGES['INVALID_API_KEY'], 'error_code': 'INVALID_API_KEY'}), 401

    return decorated


def api_key_or_session_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if is_authenticated() or verify_api_key(get_request_api_key()):
            return f(*args, **kwargs)
        return jsonify({'error': ERROR_MESSAGES['AUTH_REQUIRED'], 'error_code': 'AUTH_REQUIRED'}), 401

    return decorated
