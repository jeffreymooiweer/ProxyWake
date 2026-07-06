from flask import Blueprint, jsonify, request

from auth import is_auth_configured, login_required, set_password
from config import VALID_API_SCOPES, get_api_key_scopes, get_or_create_api_key, get_previous_api_key, is_supported_language, rotate_api_key, set_api_key_scopes
from services.settings_service import get_notification_settings, get_setting, is_onboarding_complete, log_audit, set_notification_settings, set_setting
from utils.http import actor_ip, get_proxywake_base_url, json_error, json_message
from utils.logging_config import VALID_LOG_LEVELS, setup_logging
from config import LOG_FILE

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
        'api_scopes': get_api_key_scopes(),
        'available_api_scopes': list(VALID_API_SCOPES),
        'log_level': get_setting('log_level', 'INFO'),
        'notifications': get_notification_settings(),
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
    body['api_scopes'] = get_api_key_scopes()
    return jsonify(body), status


@bp.route('/api/settings/api-scopes', methods=['PUT'])
@login_required
def update_api_scopes():
    data = request.get_json(silent=True) or {}
    scopes = set_api_key_scopes(data.get('scopes', []))
    log_audit('api_scopes_updated', ','.join(scopes), actor_ip())
    return jsonify({'api_scopes': scopes}), 200


@bp.route('/api/settings/log-level', methods=['PUT'])
@login_required
def update_log_level():
    data = request.get_json(silent=True) or {}
    level = (data.get('level') or 'INFO').upper()
    if level not in VALID_LOG_LEVELS:
        return json_error('INVALID_LOG_LEVEL', 400)
    set_setting('log_level', level)
    setup_logging(LOG_FILE, level=level)
    log_audit('log_level_updated', level, actor_ip())
    return jsonify({'log_level': level}), 200


@bp.route('/api/settings/notifications', methods=['PUT'])
@login_required
def update_notifications():
    data = request.get_json(silent=True) or {}
    settings = set_notification_settings(data)
    log_audit('notification_settings_updated', None, actor_ip())
    return jsonify(settings), 200
