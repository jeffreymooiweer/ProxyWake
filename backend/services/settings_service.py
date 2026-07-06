import logging

from models import AppSetting, AuditLog, Device, db


def get_setting(key, default=None):
    row = AppSetting.query.filter_by(key=key).first()
    return row.value if row else default


def set_setting(key, value):
    row = AppSetting.query.filter_by(key=key).first()
    if row:
        row.value = str(value)
    else:
        db.session.add(AppSetting(key=key, value=str(value)))
    db.session.commit()


def is_onboarding_complete():
    return get_setting('onboarding_completed', 'false') == 'true'


def log_audit(action, details=None, actor_ip=None):
    db.session.add(AuditLog(action=action, details=details, actor_ip=actor_ip))
    db.session.commit()
    logging.info('Audit: %s - %s', action, details)


def export_devices():
    devices = Device.query.order_by(Device.domain.asc()).all()
    return [device.to_dict() for device in devices]


def import_devices(data_list, merge=True):
    imported = 0
    for item in data_list:
        domain = (item.get('domain') or '').strip().lower()
        if not domain:
            continue
        existing = Device.query.filter_by(domain=domain).first()
        if existing and not merge:
            continue
        payload = {
            'domain': domain,
            'ip': item.get('ip'),
            'mac': item.get('mac'),
            'name': item.get('name'),
            'group_id': item.get('group_id'),
            'npm_host_id': item.get('npm_host_id'),
            'use_broadcast': item.get('use_broadcast', False),
            'broadcast_ip': item.get('broadcast_ip'),
            'wake_cooldown_seconds': item.get('wake_cooldown_seconds', 30),
            'status_check_type': item.get('status_check_type', 'ping'),
            'status_check_host': item.get('status_check_host'),
            'status_check_port': item.get('status_check_port'),
            'status_check_url': item.get('status_check_url'),
            'wake_timeout_seconds': item.get('wake_timeout_seconds', 120),
            'wake_poll_interval_seconds': item.get('wake_poll_interval_seconds', 3),
        }
        if existing:
            for key, value in payload.items():
                if value is not None:
                    setattr(existing, key, value)
        else:
            db.session.add(Device(**payload))
        imported += 1
    db.session.commit()
    return imported
