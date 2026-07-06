from flask import Blueprint, jsonify, request, session

from auth import _password_matches, is_auth_configured, is_authenticated, set_password
from config import get_or_create_api_key, is_supported_language
from extensions import limiter
from services.settings_service import get_setting, is_onboarding_complete, log_audit, set_setting
from utils.http import actor_ip, json_error, json_message

bp = Blueprint('auth', __name__)


@bp.route('/api/auth/status')
def auth_status():
    return jsonify({
        'authenticated': is_authenticated(),
        'password_required': is_auth_configured(),
        'api_key_configured': bool(get_or_create_api_key()),
        'onboarding_completed': is_onboarding_complete(),
        'theme': get_setting('theme', 'dark'),
        'language': get_setting('language', 'en'),
    })


@bp.route('/api/auth/login', methods=['POST'])
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


@bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return json_message('LOGOUT_SUCCESS')


@bp.route('/api/setup', methods=['POST'])
def setup():
    from errors import message_response

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
    if data.get('language') and is_supported_language(data['language']):
        set_setting('language', data['language'])

    set_setting('onboarding_completed', 'true')
    session['authenticated'] = True
    session.permanent = True
    log_audit('setup_complete', 'Initial setup completed', actor_ip())
    body, status = message_response('SETUP_COMPLETE')
    body['api_key'] = get_or_create_api_key()
    return jsonify(body), status
