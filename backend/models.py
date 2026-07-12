from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class AppSetting(db.Model):
    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text, nullable=False)


class DeviceGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    color = db.Column(db.String(16), default='#6366f1')
    devices = db.relationship('Device', backref='group', lazy=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'color': self.color}


class NpmHost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    base_url = db.Column(db.String(255), nullable=False)
    devices = db.relationship('Device', backref='npm_host', lazy=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'base_url': self.base_url}


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False, unique=True)
    ip = db.Column(db.String(15), nullable=False)
    mac = db.Column(db.String(17), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('device_group.id'), nullable=True)
    npm_host_id = db.Column(db.Integer, db.ForeignKey('npm_host.id'), nullable=True)
    use_broadcast = db.Column(db.Boolean, default=False)
    broadcast_ip = db.Column(db.String(15), nullable=True)
    wake_cooldown_seconds = db.Column(db.Integer, default=30)
    last_wake_at = db.Column(db.DateTime, nullable=True)
    status_check_type = db.Column(db.String(16), default='ping')
    status_check_host = db.Column(db.String(255), nullable=True)
    status_check_port = db.Column(db.Integer, nullable=True)
    status_check_url = db.Column(db.String(500), nullable=True)
    wake_timeout_seconds = db.Column(db.Integer, default=120)
    wake_poll_interval_seconds = db.Column(db.Integer, default=3)
    last_wake_success = db.Column(db.Boolean, nullable=True)
    last_wake_duration_seconds = db.Column(db.Integer, nullable=True)
    wake_count = db.Column(db.Integer, default=0)
    wake_success_count = db.Column(db.Integer, default=0)
    wake_failure_count = db.Column(db.Integer, default=0)
    wake_method = db.Column(db.String(16), default='wol')
    wol_port = db.Column(db.Integer, default=9)
    ssh_host = db.Column(db.String(255), nullable=True)
    ssh_port = db.Column(db.Integer, default=22)
    ssh_username = db.Column(db.String(120), nullable=True)
    ssh_command = db.Column(db.String(500), default='exit')
    webhook_url = db.Column(db.String(500), nullable=True)
    webhook_method = db.Column(db.String(16), default='POST')
    webhook_headers = db.Column(db.Text, nullable=True)
    webhook_body = db.Column(db.Text, nullable=True)
    homeassistant_webhook_url = db.Column(db.String(500), nullable=True)
    ipmi_host = db.Column(db.String(255), nullable=True)
    ipmi_port = db.Column(db.Integer, default=623)
    ipmi_username = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self, include_status=False, online=None):
        from services.dependency_service import dependencies_to_dict
        from services.status_service import check_device_online

        payload = {
            'id': self.id,
            'domain': self.domain,
            'ip': self.ip,
            'mac': self.mac,
            'name': self.name or self.domain,
            'group_id': self.group_id,
            'npm_host_id': self.npm_host_id,
            'use_broadcast': self.use_broadcast,
            'broadcast_ip': self.broadcast_ip,
            'wake_cooldown_seconds': self.wake_cooldown_seconds,
            'last_wake_at': self.last_wake_at.isoformat() if self.last_wake_at else None,
            'status_check_type': self.status_check_type or 'ping',
            'status_check_host': self.status_check_host,
            'status_check_port': self.status_check_port,
            'status_check_url': self.status_check_url,
            'wake_timeout_seconds': self.wake_timeout_seconds or 120,
            'wake_poll_interval_seconds': self.wake_poll_interval_seconds or 3,
            'last_wake_success': self.last_wake_success,
            'last_wake_duration_seconds': self.last_wake_duration_seconds,
            'wake_count': self.wake_count or 0,
            'wake_success_count': self.wake_success_count or 0,
            'wake_failure_count': self.wake_failure_count or 0,
            'wake_method': self.wake_method or 'wol',
            'wol_port': self.wol_port or 9,
            'ssh_host': self.ssh_host,
            'ssh_port': self.ssh_port or 22,
            'ssh_username': self.ssh_username,
            'ssh_command': self.ssh_command or 'exit',
            'webhook_url': self._public_webhook_url(),
            'webhook_method': self.webhook_method or 'POST',
            'webhook_headers': self.webhook_headers,
            'webhook_body': self.webhook_body,
            'homeassistant_webhook_url': self._public_webhook_url(self.homeassistant_webhook_url),
            'ipmi_host': self.ipmi_host,
            'ipmi_port': self.ipmi_port or 623,
            'ipmi_username': self.ipmi_username,
            'ssh_credentials_configured': self._ssh_credentials_configured(),
            'ipmi_credentials_configured': self._ipmi_credentials_configured(),
            'dependencies': dependencies_to_dict(self.id) if self.id else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_status:
            payload['online'] = online if online is not None else check_device_online(self)
        return payload

    def _public_webhook_url(self, url=None):
        from utils.masking import mask_url

        return mask_url(url or self.webhook_url or '')

    def _ssh_credentials_configured(self):
        from services.credential_service import credentials_configured

        return credentials_configured(self.id, keys=('ssh_password', 'ssh_private_key'))

    def _ipmi_credentials_configured(self):
        from services.credential_service import credentials_configured

        return credentials_configured(self.id, keys=('ipmi_password',))


class WakeEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    source = db.Column(db.String(32), nullable=False)
    success = db.Column(db.Boolean, default=True)
    skipped = db.Column(db.Boolean, default=False)
    online_after_ms = db.Column(db.Integer, nullable=True)
    duration_ms = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(32), nullable=True)
    wake_method = db.Column(db.String(16), nullable=True)
    error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    device = db.relationship('Device', backref='wake_events')

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device.name if self.device else None,
            'domain': self.device.domain if self.device else None,
            'source': self.source,
            'success': self.success,
            'skipped': self.skipped,
            'online_after_ms': self.online_after_ms,
            'duration_ms': self.duration_ms,
            'status': self.status,
            'wake_method': self.wake_method,
            'error': self.error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(64), nullable=False)
    details = db.Column(db.Text, nullable=True)
    actor_ip = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'details': self.details,
            'actor_ip': self.actor_ip,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Webhook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    events = db.Column(db.String(255), default='wake_failed,wake_success')
    enabled = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'events': self.events.split(',') if self.events else [],
            'enabled': self.enabled,
        }


class ScheduledWake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    minute = db.Column(db.Integer, default=0)
    days = db.Column(db.String(32), default='0,1,2,3,4,5,6')
    enabled = db.Column(db.Boolean, default=True)
    device = db.relationship('Device', backref='schedules')

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device.name if self.device else None,
            'hour': self.hour,
            'minute': self.minute,
            'days': [int(day) for day in self.days.split(',') if day != ''] if self.days else [],
            'enabled': self.enabled,
        }


class WakeJob(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    device_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(32), default='starting')
    message_code = db.Column(db.String(64), nullable=True)
    online = db.Column(db.Boolean, default=False)
    waited_ms = db.Column(db.Integer, nullable=True)
    error = db.Column(db.Text, nullable=True)
    extra = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        import json

        payload = {
            'job_id': self.id,
            'device_id': self.device_id,
            'status': self.status,
            'message_code': self.message_code,
            'online': self.online,
            'waited_ms': self.waited_ms,
            'error': self.error,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if self.extra:
            try:
                payload.update(json.loads(self.extra))
            except ValueError:
                pass
        return payload


class DeviceCredential(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    key = db.Column(db.String(64), nullable=False)
    encrypted_value = db.Column(db.Text, nullable=False)
    device = db.relationship('Device', backref=db.backref('credential_rows', lazy=True, cascade='all, delete-orphan'))

    __table_args__ = (db.UniqueConstraint('device_id', 'key', name='uq_device_credential'),)


class DeviceDependency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    depends_on_device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    device = db.relationship('Device', foreign_keys=[device_id], backref=db.backref('dependency_rows', lazy=True, cascade='all, delete-orphan'))
    depends_on = db.relationship('Device', foreign_keys=[depends_on_device_id])

    __table_args__ = (db.UniqueConstraint('device_id', 'depends_on_device_id', name='uq_device_dependency'),)
