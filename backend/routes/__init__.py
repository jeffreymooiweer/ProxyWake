from routes.auth_routes import bp as auth_bp
from routes.automation_routes import bp as automation_bp
from routes.backup_routes import bp as backup_bp
from routes.device_routes import bp as device_bp
from routes.docs_routes import bp as docs_bp
from routes.group_routes import bp as group_bp
from routes.health_routes import bp as health_bp
from routes.integration_routes import bp as integration_bp
from routes.public_routes import bp as public_bp
from routes.settings_routes import bp as settings_bp
from routes.spa_routes import bp as spa_bp, register_error_handlers
from routes.stats_routes import bp as stats_bp


def register_blueprints(app):
    for blueprint in (
        health_bp,
        docs_bp,
        auth_bp,
        settings_bp,
        backup_bp,
        device_bp,
        group_bp,
        integration_bp,
        public_bp,
        automation_bp,
        stats_bp,
        spa_bp,
    ):
        app.register_blueprint(blueprint)
    register_error_handlers(app)
