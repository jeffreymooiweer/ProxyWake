import logging

import requests

from models import WakeEvent, Webhook, db
from version import __version__


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
                headers={'Content-Type': 'application/json', 'User-Agent': f'ProxyWake/{__version__}'},
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
