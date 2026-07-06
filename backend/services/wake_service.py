import logging
from datetime import datetime, timezone

from models import db
from services.dependency_service import get_wake_order
from services.notification_service import record_wake_event, send_webhooks
from services.status_service import check_device_online, wait_for_device
from services.wake_executor import WakeMethodError, execute_wake_action
from services.wake_job_service import update_wake_job

__all__ = [
    'execute_wake_action',
    'run_verified_wake',
    'smart_wake_device',
    'wake_and_wait',
    'wake_group',
]


def _update_wake_stats(device, success, duration_seconds=None):
    device.wake_count = (device.wake_count or 0) + 1
    if success:
        device.wake_success_count = (device.wake_success_count or 0) + 1
        device.last_wake_success = True
    else:
        device.wake_failure_count = (device.wake_failure_count or 0) + 1
        device.last_wake_success = False
    if duration_seconds is not None:
        device.last_wake_duration_seconds = duration_seconds
    db.session.commit()


def _perform_wake_action(device, source):
    try:
        execute_wake_action(device)
        return None
    except WakeMethodError as exc:
        logging.error('Wake mislukt voor %s (%s): %s', device.domain, exc.code, exc)
        record_wake_event(device, source, success=False, error=str(exc), status='failed')
        return exc.code


def _wake_chain_if_needed(target_device, source, job_id=None, force=False):
    order = get_wake_order(target_device.id)
    for device in order[:-1]:
        if check_device_online(device) and not force:
            continue
        if job_id:
            update_wake_job(
                job_id,
                status='waiting',
                message_code='WAKE_DEPENDENCY',
                name=device.name or device.domain,
                dependency_name=device.name or device.domain,
            )
        error_code = _perform_wake_action(device, f'{source}:dependency')
        if error_code:
            return error_code
        waited_ms = wait_for_device(device)
        if waited_ms is None:
            return 'DEPENDENCY_WAKE_FAILED'
    return None


def smart_wake_device(device, source='manual', force=False):
    now = datetime.now(timezone.utc)
    online = check_device_online(device)

    if online and not force:
        record_wake_event(device, source, success=True, skipped=True, status='skipped')
        name = device.name or device.domain
        return {
            'message_code': 'DEVICE_ALREADY_ONLINE',
            'name': name,
            'skipped': True,
            'online': True,
            'status': 'skipped',
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
                'status': 'cooldown',
            }

    dependency_error = _wake_chain_if_needed(device, source, force=force)
    if dependency_error:
        return {
            'message_code': dependency_error,
            'name': device.name or device.domain,
            'skipped': False,
            'online': online,
            'status': 'failed',
        }

    error_code = _perform_wake_action(device, source)
    if error_code:
        return {
            'message_code': error_code,
            'name': device.name or device.domain,
            'skipped': False,
            'online': online,
            'status': 'failed',
        }

    device.last_wake_at = now
    db.session.commit()
    logging.info('Wake action sent to %s (%s) via %s using %s', device.domain, device.ip, source, device.wake_method or 'wol')
    record_wake_event(device, source, success=True, skipped=False, status='sent', wake_method=device.wake_method)
    name = device.name or device.domain
    return {
        'message_code': 'WAKE_SENT',
        'name': name,
        'skipped': False,
        'online': online,
        'status': 'sent',
        'wake_method': device.wake_method or 'wol',
    }


def run_verified_wake(device, job_id, source='manual', force=False):
    update_wake_job(job_id, status='checking', message_code=None)

    if check_device_online(device) and not force:
        record_wake_event(device, source, success=True, skipped=True, status='skipped')
        update_wake_job(job_id, status='skipped', message_code='DEVICE_ALREADY_ONLINE', online=True, waited_ms=0)
        return

    now = datetime.now(timezone.utc)
    if device.last_wake_at and not force:
        elapsed = (now - device.last_wake_at.replace(tzinfo=timezone.utc)).total_seconds()
        if elapsed < device.wake_cooldown_seconds:
            seconds = int(device.wake_cooldown_seconds - elapsed)
            update_wake_job(
                job_id,
                status='cooldown',
                message_code='DEVICE_COOLDOWN',
                online=check_device_online(device),
                error=str(seconds),
            )
            return

    dependency_error = _wake_chain_if_needed(device, source, job_id=job_id, force=force)
    if dependency_error:
        _update_wake_stats(device, success=False)
        update_wake_job(job_id, status='failed', message_code=dependency_error)
        return

    update_wake_job(job_id, status='sending_packet', message_code='WAKE_SENDING', name=device.name or device.domain)
    error_code = _perform_wake_action(device, source)
    if error_code:
        _update_wake_stats(device, success=False)
        update_wake_job(job_id, status='failed', message_code=error_code)
        return

    device.last_wake_at = datetime.now(timezone.utc)
    db.session.commit()

    if check_device_online(device):
        record_wake_event(device, source, success=True, skipped=False, status='online', duration_ms=0, wake_method=device.wake_method)
        _update_wake_stats(device, success=True, duration_seconds=0)
        update_wake_job(job_id, status='online', message_code='WAKE_ONLINE', online=True, waited_ms=0, name=device.name or device.domain, seconds=0)
        return

    update_wake_job(job_id, status='waiting', message_code='WAKE_WAITING', name=device.name or device.domain)
    waited_ms = wait_for_device(device)
    if waited_ms is not None:
        duration_seconds = int(waited_ms / 1000)
        record_wake_event(device, source, success=True, online_after_ms=waited_ms, status='online', duration_ms=waited_ms, wake_method=device.wake_method)
        _update_wake_stats(device, success=True, duration_seconds=duration_seconds)
        update_wake_job(job_id, status='online', message_code='WAKE_ONLINE', online=True, waited_ms=waited_ms, name=device.name or device.domain, seconds=duration_seconds)
        return

    timeout = device.wake_timeout_seconds or 120
    send_webhooks('wake_failed', {'device_id': device.id, 'domain': device.domain, 'error': 'timeout'})
    record_wake_event(device, source, success=False, error='timeout', status='failed', duration_ms=timeout * 1000, wake_method=device.wake_method)
    _update_wake_stats(device, success=False, duration_seconds=timeout)
    update_wake_job(job_id, status='failed', message_code='WAKE_TIMEOUT', online=False, waited_ms=timeout * 1000)


def wake_and_wait(device, source='public', max_wait=None):
    if check_device_online(device):
        record_wake_event(device, source, success=True, skipped=True, status='skipped')
        return {'online': True, 'waited_ms': 0, 'message_code': 'ALREADY_ONLINE', 'skipped': True, 'status': 'skipped'}

    dependency_error = _wake_chain_if_needed(device, source)
    if dependency_error:
        return {'online': False, 'message_code': dependency_error, 'status': 'failed'}

    result = smart_wake_device(device, source=source)
    if result.get('message_code') in ('DEPENDENCY_WAKE_FAILED', 'SSH_CREDENTIALS_MISSING', 'WEBHOOK_URL_MISSING'):
        return {'online': False, 'status': 'failed', **result}

    if check_device_online(device):
        return {'online': True, 'waited_ms': 0, 'status': 'online', **result}

    waited_ms = wait_for_device(device, max_wait=max_wait)
    if waited_ms is not None:
        record_wake_event(device, source, success=True, online_after_ms=waited_ms, status='online', duration_ms=waited_ms, wake_method=device.wake_method)
        _update_wake_stats(device, success=True, duration_seconds=int(waited_ms / 1000))
        return {'online': True, 'waited_ms': waited_ms, 'status': 'online', **result}

    timeout = max_wait if max_wait is not None else (device.wake_timeout_seconds or 120)
    send_webhooks('wake_failed', {'device_id': device.id, 'domain': device.domain, 'error': 'timeout'})
    record_wake_event(device, source, success=False, error='timeout', status='failed', duration_ms=timeout * 1000, wake_method=device.wake_method)
    _update_wake_stats(device, success=False, duration_seconds=timeout)
    return {'online': False, 'waited_ms': timeout * 1000, 'message_code': 'WAKE_TIMEOUT', 'status': 'failed', **result}


def wake_group(group_id, source='group'):
    from models import Device

    devices = Device.query.filter_by(group_id=group_id).all()
    results = []
    for device in devices:
        try:
            results.append({'device_id': device.id, **smart_wake_device(device, source=source)})
        except WakeMethodError as exc:
            results.append({'device_id': device.id, 'error': str(exc), 'message_code': exc.code})
        except Exception as exc:
            results.append({'device_id': device.id, 'error': str(exc)})
    return results
