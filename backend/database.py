import logging

from config import DATA_DIR, LOG_FILE
from models import db
from services.migration_service import migrate_db
from services.scheduler_service import start_scheduler


def init_database(app):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(LOG_FILE),
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s',
    )
    with app.app_context():
        db.create_all()
        migrate_db(db.engine)
        start_scheduler(app)
