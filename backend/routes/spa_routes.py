import os

from flask import Blueprint, current_app, request, send_from_directory

from utils.http import json_error

bp = Blueprint('spa', __name__)


@bp.route('/', defaults={'path': ''})
@bp.route('/<path:path>')
def serve(path):
    static_folder = current_app.static_folder
    if path.startswith('api/'):
        return json_error('NOT_FOUND', 404)
    if path and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    return send_from_directory(static_folder, 'index.html')


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith('/api/'):
            return json_error('NOT_FOUND', 404)
        return send_from_directory(app.static_folder, 'index.html')

    @app.errorhandler(429)
    def rate_limited(_error):
        return json_error('RATE_LIMITED', 429)
