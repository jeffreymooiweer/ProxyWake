from sqlalchemy import inspect, text

SCHEMA_VERSION = '4.1'

DEVICE_MIGRATIONS = {
    'group_id': 'INTEGER',
    'npm_host_id': 'INTEGER',
    'use_broadcast': 'BOOLEAN DEFAULT 0',
    'broadcast_ip': 'VARCHAR(15)',
    'wake_cooldown_seconds': 'INTEGER DEFAULT 30',
    'last_wake_at': 'DATETIME',
    'status_check_type': "VARCHAR(16) DEFAULT 'ping'",
    'status_check_host': 'VARCHAR(255)',
    'status_check_port': 'INTEGER',
    'status_check_url': 'VARCHAR(500)',
    'wake_timeout_seconds': 'INTEGER DEFAULT 120',
    'wake_poll_interval_seconds': 'INTEGER DEFAULT 3',
    'last_wake_success': 'BOOLEAN',
    'last_wake_duration_seconds': 'INTEGER',
    'wake_count': 'INTEGER DEFAULT 0',
    'wake_success_count': 'INTEGER DEFAULT 0',
    'wake_failure_count': 'INTEGER DEFAULT 0',
    'wake_method': "VARCHAR(16) DEFAULT 'wol'",
    'wol_port': 'INTEGER DEFAULT 9',
    'ssh_host': 'VARCHAR(255)',
    'ssh_port': 'INTEGER DEFAULT 22',
    'ssh_username': 'VARCHAR(120)',
    'ssh_command': "VARCHAR(500) DEFAULT 'exit'",
    'webhook_url': 'VARCHAR(500)',
    'webhook_method': "VARCHAR(16) DEFAULT 'POST'",
    'webhook_headers': 'TEXT',
    'webhook_body': 'TEXT',
    'homeassistant_webhook_url': 'VARCHAR(500)',
    'ipmi_host': 'VARCHAR(255)',
    'ipmi_port': 'INTEGER DEFAULT 623',
    'ipmi_username': 'VARCHAR(120)',
}

WAKE_EVENT_MIGRATIONS = {
    'duration_ms': 'INTEGER',
    'status': 'VARCHAR(32)',
    'wake_method': 'VARCHAR(16)',
}


def migrate_db(engine):
    inspector = inspect(engine)
    if inspector.has_table('device'):
        _apply_alterations(engine, inspector, 'device', DEVICE_MIGRATIONS)
    if inspector.has_table('wake_event'):
        _apply_alterations(engine, inspector, 'wake_event', WAKE_EVENT_MIGRATIONS)
    if inspector.has_table('app_setting'):
        _store_schema_version()


def _apply_alterations(engine, inspector, table_name, alterations):
    columns = {column['name'] for column in inspector.get_columns(table_name)}
    with engine.connect() as conn:
        for column, col_type in alterations.items():
            if column not in columns:
                conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {column} {col_type}'))
        conn.commit()


def _store_schema_version():
    from models import AppSetting, db

    row = AppSetting.query.filter_by(key='schema_version').first()
    if row:
        row.value = SCHEMA_VERSION
    else:
        db.session.add(AppSetting(key='schema_version', value=SCHEMA_VERSION))
    db.session.commit()
