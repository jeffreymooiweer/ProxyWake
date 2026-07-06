import logging

from config import DATA_DIR, LOG_FILE
from models import db
from services.migration_service import migrate_db
from services.scheduler_service import start_scheduler
from services.settings_service import get_setting
from utils.logging_config import setup_logging


def init_database(app):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        db.create_all()
        migrate_db(db.engine)
        log_level = get_setting('log_level', 'INFO')
        setup_logging(LOG_FILE, level=log_level)
        logging.info('ProxyWake logging initialized at %s level', log_level)
        start_scheduler(app)
