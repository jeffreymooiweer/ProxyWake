from flask import jsonify, request

from errors import error_response, message_response
from services.settings_service import get_setting


def actor_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr)


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
