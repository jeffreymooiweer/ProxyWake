import logging
from datetime import datetime, timezone

from wakeonlan import send_magic_packet

from models import db
from services.notification_service import record_wake_event, send_webhooks
from utils.network import check_host_online, wait_for_host

# Re-exported at package level for tests that patch services.check_host_online
__all__ = [
    '_broadcast_for_ip',
    '_send_packets',
    'smart_wake_device',
    'wake_and_wait',
    'wake_group',
]


def _broadcast_for_ip(ip):
    parts = ip.split('.')
    if len(parts) == 4:
        return f'{parts[0]}.{parts[1]}.{parts[2]}.255'
    return '255.255.255.255'


def _send_packets(device):
    send_magic_packet(device.mac, ip_address=device.ip)
    if device.use_broadcast:
        broadcast = device.broadcast_ip or _broadcast_for_ip(device.ip)
        if broadcast:
            send_magic_packet(device.mac, ip_address=broadcast)


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
    from models import Device

    devices = Device.query.filter_by(group_id=group_id).all()
    results = []
    for device in devices:
        try:
            results.append({'device_id': device.id, **smart_wake_device(device, source=source)})
        except Exception as exc:
            results.append({'device_id': device.id, 'error': str(exc)})
    return results
