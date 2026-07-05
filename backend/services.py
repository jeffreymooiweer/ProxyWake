import json
import logging
import threading
from datetime import datetime, timezone

import requests
from wakeonlan import send_magic_packet

from models import AppSetting, AuditLog, Device, WakeEvent, Webhook, db
from utils import check_host_online, wait_for_host


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


def send_webhooks(event_name, payload):
    hooks = Webhook.query.filter_by(enabled=True).all()
    for hook in hooks:
        events = hook.events.split(',') if hook.events else []
        if event_name not in events:
            continue
        try:
            requests.post(
                hook.url,
                json={'event': event_name, **payload},
                timeout=5,
                headers={'Content-Type': 'application/json', 'User-Agent': 'ProxyWake/3.0'},
            )
        except requests.RequestException as exc:
            logging.error('Webhook %s mislukt: %s', hook.name, exc)


def record_wake_event(device, source, success=True, skipped=False, online_after_ms=None, error=None):
    event = WakeEvent(
        device_id=device.id,
        source=source,
        success=success,
        skipped=skipped,
        online_after_ms=online_after_ms,
        error=error,
    )
    db.session.add(event)
    db.session.commit()

    payload = {
        'device_id': device.id,
        'domain': device.domain,
        'name': device.name or device.domain,
        'source': source,
        'skipped': skipped,
        'online_after_ms': online_after_ms,
        'error': error,
    }
    if success and not skipped:
        send_webhooks('wake_success', payload)
    elif not success:
        send_webhooks('wake_failed', payload)


def _send_packets(device):
    send_magic_packet(device.mac, ip_address=device.ip)
    if device.use_broadcast:
        broadcast = device.broadcast_ip or _broadcast_for_ip(device.ip)
        if broadcast:
            send_magic_packet(device.mac, ip_address=broadcast)


def _broadcast_for_ip(ip):
    parts = ip.split('.')
    if len(parts) == 4:
        return f'{parts[0]}.{parts[1]}.{parts[2]}.255'
    return '255.255.255.255'


def smart_wake_device(device, source='manual', force=False):
    now = datetime.now(timezone.utc)
    online = check_host_online(device.ip)

    if online and not force:
        record_wake_event(device, source, success=True, skipped=True)
        name = device.name or device.domain
        return {
            'message_code': 'DEVICE_ALREADY_ONLINE',
            'name': name,
            'skipped': True,
            'online': True,
        }

    if device.last_wake_at and not force:
        elapsed = (now - device.last_wake_at.replace(tzinfo=timezone.utc)).total_seconds()
        if elapsed < device.wake_cooldown_seconds:
            seconds = int(device.wake_cooldown_seconds - elapsed)
            return {
                'message_code': 'DEVICE_COOLDOWN',
                'seconds': seconds,
                'skipped': True,
                'online': online,
            }

    try:
        _send_packets(device)
        device.last_wake_at = now
        db.session.commit()
        logging.info('Magic packet sent to %s (%s) via %s', device.domain, device.ip, source)
        record_wake_event(device, source, success=True, skipped=False)
        name = device.name or device.domain
        return {
            'message_code': 'WAKE_SENT',
            'name': name,
            'skipped': False,
            'online': online,
        }
    except Exception as exc:
        logging.error('Wake mislukt voor %s: %s', device.domain, exc)
        record_wake_event(device, source, success=False, error=str(exc))
        raise


def wake_and_wait(device, source='public', max_wait=120):
    if check_host_online(device.ip):
        record_wake_event(device, source, success=True, skipped=True)
        return {'online': True, 'waited_ms': 0, 'message_code': 'ALREADY_ONLINE', 'skipped': True}

    result = smart_wake_device(device, source=source)
    if check_host_online(device.ip):
        return {'online': True, 'waited_ms': 0, **result}

    waited_ms = wait_for_host(device.ip, max_wait=max_wait)
    if waited_ms is not None:
        record_wake_event(device, source, success=True, online_after_ms=waited_ms)
        return {'online': True, 'waited_ms': waited_ms, **result}

    send_webhooks('wake_failed', {'device_id': device.id, 'domain': device.domain, 'error': 'timeout'})
    return {'online': False, 'waited_ms': max_wait * 1000, 'message_code': 'WAKE_TIMEOUT', **result}


def wake_group(group_id, source='group'):
    devices = Device.query.filter_by(group_id=group_id).all()
    results = []
    for device in devices:
        try:
            results.append({'device_id': device.id, **smart_wake_device(device, source=source)})
        except Exception as exc:
            results.append({'device_id': device.id, 'error': str(exc)})
    return results


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


_scheduler_started = False


def start_scheduler(app):
    global _scheduler_started
    if _scheduler_started:
        return
    _scheduler_started = True

    def loop():
        import time
        from models import ScheduledWake

        while True:
            try:
                with app.app_context():
                    now = datetime.now()
                    weekday = str(now.weekday())
                    schedules = ScheduledWake.query.filter_by(enabled=True).all()
                    for schedule in schedules:
                        days = schedule.days.split(',')
                        if weekday not in days:
                            continue
                        if schedule.hour == now.hour and schedule.minute == now.minute:
                            device = Device.query.get(schedule.device_id)
                            if device:
                                try:
                                    smart_wake_device(device, source='scheduled')
                                except Exception as exc:
                                    logging.error('Geplande wake mislukt: %s', exc)
            except Exception as exc:
                logging.error('Scheduler fout: %s', exc)
            time.sleep(60)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()


def migrate_db(engine):
    from sqlalchemy import inspect, text

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
