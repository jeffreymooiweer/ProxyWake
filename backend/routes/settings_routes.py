from flask import Blueprint, jsonify

from auth import is_auth_configured, login_required, set_password
from config import get_or_create_api_key, get_previous_api_key, is_supported_language, rotate_api_key
from services.settings_service import get_setting, is_onboarding_complete, log_audit, set_setting
from utils.http import actor_ip, get_proxywake_base_url, json_error, json_message

bp = Blueprint('settings', __name__)


@bp.route('/api/settings')
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


@bp.route('/api/settings/language', methods=['PUT'])
@login_required
def update_language():
    from flask import request

    data = request.get_json(silent=True) or {}
    language = data.get('language', 'en')
    if not is_supported_language(language):
        return json_error('INVALID_LANGUAGE', 400)
    set_setting('language', language)
    return jsonify({'language': language}), 200


@bp.route('/api/settings/theme', methods=['PUT'])
@login_required
def update_theme():
    from flask import request

    data = request.get_json(silent=True) or {}
    theme = data.get('theme', 'dark')
    if theme not in ('dark', 'light'):
        return json_error('INVALID_THEME', 400)
    set_setting('theme', theme)
    return jsonify({'theme': theme}), 200


@bp.route('/api/settings/password', methods=['PUT'])
@login_required
def update_password():
    from flask import request

    data = request.get_json(silent=True) or {}
    password = data.get('password', '').strip()
    if len(password) < 8:
        return json_error('PASSWORD_TOO_SHORT', 400)
    set_password(password)
    log_audit('password_changed', None, actor_ip())
    return json_message('PASSWORD_UPDATED')


@bp.route('/api/settings/rotate-api-key', methods=['POST'])
@login_required
def rotate_key():
    from errors import message_response

    new_key = rotate_api_key()
    log_audit('api_key_rotated', 'API key rotated', actor_ip())
    body, status = message_response('API_KEY_ROTATED')
    body['api_key'] = new_key
    body['previous_api_key'] = get_previous_api_key()
    return jsonify(body), status
