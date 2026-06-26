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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self, include_status=False, online=None):
        from utils import check_host_online

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
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_status:
            payload['online'] = online if online is not None else check_host_online(self.ip)
        return payload


class WakeEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    source = db.Column(db.String(32), nullable=False)
    success = db.Column(db.Boolean, default=True)
    skipped = db.Column(db.Boolean, default=False)
    online_after_ms = db.Column(db.Integer, nullable=True)
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
            'days': [int(day) for day in self.days.split(',') if day != ''],
            'enabled': self.enabled,
        }
