import logging

import requests

from models import WakeEvent, Webhook, db
from services.settings_service import get_notification_settings
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


def send_notification_channels(event_name, payload):
    settings = get_notification_settings()
    message = _format_notification(event_name, payload)

    if settings.get('slack_enabled') and settings.get('slack_webhook_url'):
        try:
            requests.post(
                settings['slack_webhook_url'],
                json={'text': message},
                timeout=5,
            )
        except requests.RequestException as exc:
            logging.error('Slack notification mislukt: %s', exc)

    if settings.get('telegram_enabled') and settings.get('telegram_bot_token') and settings.get('telegram_chat_id'):
        try:
            requests.post(
                f"https://api.telegram.org/bot{settings['telegram_bot_token']}/sendMessage",
                json={'chat_id': settings['telegram_chat_id'], 'text': message},
                timeout=5,
            )
        except requests.RequestException as exc:
            logging.error('Telegram notification mislukt: %s', exc)


def _format_notification(event_name, payload):
    name = payload.get('name') or payload.get('domain') or 'device'
    if event_name == 'wake_success':
        return f'ProxyWake: {name} is online.'
    if event_name == 'wake_failed':
        error = payload.get('error') or 'unknown error'
        return f'ProxyWake: wake failed for {name} ({error}).'
    return f'ProxyWake event {event_name} for {name}'


def record_wake_event(device, source, success=True, skipped=False, online_after_ms=None, error=None, status=None, duration_ms=None, wake_method=None):
    event = WakeEvent(
        device_id=device.id,
        source=source,
        success=success,
        skipped=skipped,
        online_after_ms=online_after_ms,
        error=error,
        status=status,
        duration_ms=duration_ms if duration_ms is not None else online_after_ms,
        wake_method=wake_method or getattr(device, 'wake_method', 'wol'),
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
        send_notification_channels('wake_success', payload)
    elif not success:
        send_webhooks('wake_failed', payload)
        send_notification_channels('wake_failed', payload)
