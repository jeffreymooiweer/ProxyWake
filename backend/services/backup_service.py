import json
from datetime import datetime, timezone

from models import (
    AppSetting,
    Device,
    DeviceCredential,
    DeviceDependency,
    DeviceGroup,
    NpmHost,
    ScheduledWake,
    Webhook,
    db,
)
from version import __version__

BACKUP_VERSION = '4.0'


def create_backup():
    devices = Device.query.order_by(Device.domain.asc()).all()
    return {
        'backup_version': BACKUP_VERSION,
        'app_version': __version__,
        'exported_at': datetime.now(timezone.utc).isoformat(),
        'devices': [_device_export(device) for device in devices],
        'groups': [group.to_dict() for group in DeviceGroup.query.all()],
        'npm_hosts': [host.to_dict() for host in NpmHost.query.all()],
        'webhooks': [hook.to_dict() for hook in Webhook.query.all()],
        'schedules': [_schedule_export(item) for item in ScheduledWake.query.all()],
        'dependencies': [
            {
                'device_id': row.device_id,
                'depends_on_device_id': row.depends_on_device_id,
            }
            for row in DeviceDependency.query.all()
        ],
        'credentials': [
            {
                'device_id': row.device_id,
                'key': row.key,
                'encrypted_value': row.encrypted_value,
            }
            for row in DeviceCredential.query.all()
        ],
        'settings': {row.key: row.value for row in AppSetting.query.all()},
    }


def _device_export(device):
    payload = device.to_dict(include_status=False)
    payload.pop('dependencies', None)
    payload.pop('ssh_credentials_configured', None)
    payload.pop('ipmi_credentials_configured', None)
    # to_dict() masks webhook URLs for display; a backup must round-trip the
    # real values (the endpoint is admin-scoped).
    payload['webhook_url'] = device.webhook_url
    payload['homeassistant_webhook_url'] = device.homeassistant_webhook_url
    return payload


def _schedule_export(schedule):
    return {
        'device_id': schedule.device_id,
        'hour': schedule.hour,
        'minute': schedule.minute,
        'days': schedule.days,
        'enabled': schedule.enabled,
    }


def restore_backup(data, merge=True):
    if not isinstance(data, dict):
        raise ValueError('INVALID_BACKUP')

    _restore_groups(data.get('groups', []), merge=merge)
    _restore_npm_hosts(data.get('npm_hosts', []), merge=merge)
    _restore_devices(data.get('devices', []), merge=merge)
    _restore_webhooks(data.get('webhooks', []), merge=merge)
    _restore_schedules(data.get('schedules', []), merge=merge)
    _restore_dependencies(data.get('dependencies', []), merge=merge)
    _restore_credentials(data.get('credentials', []), merge=merge)
    _restore_settings(data.get('settings', {}), merge=merge)
    db.session.commit()
    return {
        'devices': len(data.get('devices', [])),
        'groups': len(data.get('groups', [])),
        'webhooks': len(data.get('webhooks', [])),
    }


def _restore_groups(groups, merge=True):
    if not merge:
        DeviceGroup.query.delete()
    for item in groups:
        name = (item.get('name') or '').strip()
        if not name:
            continue
        existing = DeviceGroup.query.filter_by(name=name).first()
        if existing:
            existing.color = item.get('color', existing.color)
        else:
            db.session.add(DeviceGroup(name=name, color=item.get('color', '#6366f1')))


def _restore_npm_hosts(hosts, merge=True):
    if not merge:
        NpmHost.query.delete()
    for item in hosts:
        base_url = (item.get('base_url') or '').strip()
        if not base_url:
            continue
        existing = NpmHost.query.filter_by(base_url=base_url).first()
        if existing:
            existing.name = item.get('name', existing.name)
        else:
            db.session.add(NpmHost(name=item.get('name', base_url), base_url=base_url))


def _restore_devices(devices, merge=True):
    from services.settings_service import import_devices

    if not merge:
        DeviceDependency.query.delete()
        DeviceCredential.query.delete()
        Device.query.delete()
        db.session.commit()
    import_devices(devices, merge=merge)


def _restore_webhooks(webhooks, merge=True):
    if not merge:
        Webhook.query.delete()
    for item in webhooks:
        url = (item.get('url') or '').strip()
        if not url:
            continue
        existing = Webhook.query.filter_by(url=url).first()
        events = item.get('events', ['wake_failed', 'wake_success'])
        if isinstance(events, str):
            events = events.split(',')
        if existing:
            existing.name = item.get('name', existing.name)
            existing.events = ','.join(events)
            existing.enabled = item.get('enabled', existing.enabled)
        else:
            db.session.add(Webhook(
                name=item.get('name', 'Imported'),
                url=url,
                events=','.join(events),
                enabled=item.get('enabled', True),
            ))


def _restore_schedules(schedules, merge=True):
    if not merge:
        ScheduledWake.query.delete()
    for item in schedules:
        device_id = item.get('device_id')
        if not device_id or not Device.query.get(device_id):
            continue
        db.session.add(ScheduledWake(
            device_id=device_id,
            hour=int(item.get('hour', 7)),
            minute=int(item.get('minute', 0)),
            days=item.get('days', '0,1,2,3,4,5,6'),
            enabled=item.get('enabled', True),
        ))


def _restore_dependencies(dependencies, merge=True):
    if not merge:
        DeviceDependency.query.delete()
    for item in dependencies:
        device_id = item.get('device_id')
        depends_on = item.get('depends_on_device_id')
        if not device_id or not depends_on:
            continue
        if not Device.query.get(device_id) or not Device.query.get(depends_on):
            continue
        exists = DeviceDependency.query.filter_by(
            device_id=device_id,
            depends_on_device_id=depends_on,
        ).first()
        if not exists:
            db.session.add(DeviceDependency(device_id=device_id, depends_on_device_id=depends_on))


def _restore_credentials(credentials, merge=True):
    if not merge:
        DeviceCredential.query.delete()
    for item in credentials:
        device_id = item.get('device_id')
        key = item.get('key')
        value = item.get('encrypted_value')
        if not device_id or not key or not value:
            continue
        if not Device.query.get(device_id):
            continue
        row = DeviceCredential.query.filter_by(device_id=device_id, key=key).first()
        if row:
            row.encrypted_value = value
        else:
            db.session.add(DeviceCredential(device_id=device_id, key=key, encrypted_value=value))


def _restore_settings(settings, merge=True):
    if not isinstance(settings, dict):
        return
    if not merge:
        AppSetting.query.delete()
    for key, value in settings.items():
        if key == 'schema_version':
            continue
        row = AppSetting.query.filter_by(key=key).first()
        if row:
            row.value = str(value)
        else:
            db.session.add(AppSetting(key=key, value=str(value)))


def backup_as_json(data):
    return json.dumps(data, indent=2)
