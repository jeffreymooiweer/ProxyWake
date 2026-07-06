from sqlalchemy import inspect, text

SCHEMA_VERSION = '3.1'


def migrate_db(engine):
    inspector = inspect(engine)
    if not inspector.has_table('device'):
        return

    columns = {column['name'] for column in inspector.get_columns('device')}
    alterations = {
        'group_id': 'INTEGER',
        'npm_host_id': 'INTEGER',
        'use_broadcast': 'BOOLEAN DEFAULT 0',
        'broadcast_ip': 'VARCHAR(15)',
        'wake_cooldown_seconds': 'INTEGER DEFAULT 30',
        'last_wake_at': 'DATETIME',
    }
    with engine.connect() as conn:
        for column, col_type in alterations.items():
            if column not in columns:
                conn.execute(text(f'ALTER TABLE device ADD COLUMN {column} {col_type}'))
        conn.commit()

    _store_schema_version()


def _store_schema_version():
    from models import AppSetting, db

    row = AppSetting.query.filter_by(key='schema_version').first()
    if row:
        row.value = SCHEMA_VERSION
    else:
        db.session.add(AppSetting(key='schema_version', value=SCHEMA_VERSION))
    db.session.commit()
