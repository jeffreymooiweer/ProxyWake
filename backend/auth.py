import bcrypt
from functools import wraps

from flask import jsonify, request, session

from config import (
    VALID_API_SCOPES,
    get_admin_password_hash,
    get_api_key_scopes,
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


def api_key_has_scopes(required_scopes):
    if not required_scopes:
        return True
    granted = get_api_key_scopes()
    if 'admin' in granted:
        return True
    return any(scope in granted for scope in required_scopes)


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


def api_key_or_session_required(*required_scopes):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            api_key = get_request_api_key()
            if api_key:
                if not verify_api_key(api_key):
                    return jsonify({'error': ERROR_MESSAGES['INVALID_API_KEY'], 'error_code': 'INVALID_API_KEY'}), 401
                if required_scopes and not api_key_has_scopes(required_scopes):
                    return jsonify({
                        'error': ERROR_MESSAGES['INSUFFICIENT_API_SCOPE'],
                        'error_code': 'INSUFFICIENT_API_SCOPE',
                        'required_scopes': list(required_scopes),
                    }), 403
                return f(*args, **kwargs)
            if is_authenticated():
                return f(*args, **kwargs)
            return jsonify({'error': ERROR_MESSAGES['AUTH_REQUIRED'], 'error_code': 'AUTH_REQUIRED'}), 401

        return decorated

    if len(required_scopes) == 1 and callable(required_scopes[0]):
        return decorator(required_scopes[0])
    return decorator
