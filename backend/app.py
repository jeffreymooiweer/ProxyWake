import logging

import logging

from flask import Flask
from flask_cors import CORS

from config import DATA_DIR, get_allowed_origins, get_secret_key
from database import init_database
from extensions import limiter
from models import db
from routes import register_blueprints


def create_app():
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

    limiter.init_app(app)

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    register_blueprints(app)
    init_database(app)

    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
