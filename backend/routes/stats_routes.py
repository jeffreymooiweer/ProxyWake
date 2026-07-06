from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from auth import login_required
from config import LOG_FILE
from extensions import limiter
from models import AuditLog, Device, WakeEvent, db
from utils.http import json_error
from utils.network import scan_subnet, subnet_from_ip

bp = Blueprint('stats', __name__)


@bp.route('/api/stats')
@login_required
def stats():
    since = datetime.now(timezone.utc) - timedelta(days=7)
    total = WakeEvent.query.count()
    week = WakeEvent.query.filter(WakeEvent.created_at >= since).count()
    successes = WakeEvent.query.filter_by(success=True, skipped=False).count()
    per_day = db.session.query(
        func.date(WakeEvent.created_at),
        func.count(WakeEvent.id),
    ).filter(WakeEvent.created_at >= since).group_by(func.date(WakeEvent.created_at)).all()

    device_stats = []
    for device in Device.query.all():
        events = WakeEvent.query.filter_by(device_id=device.id).order_by(WakeEvent.created_at.desc()).limit(5).all()
        avg_wake = db.session.query(func.avg(WakeEvent.online_after_ms)).filter(
            WakeEvent.device_id == device.id,
            WakeEvent.online_after_ms.isnot(None),
        ).scalar()
        device_stats.append({
            'device': device.to_dict(include_status=True),
            'wake_count': WakeEvent.query.filter_by(device_id=device.id).count(),
            'avg_wake_ms': int(avg_wake) if avg_wake else None,
            'recent_events': [event.to_dict() for event in events],
        })

    return jsonify({
        'total_wake_events': total,
        'wake_events_7d': week,
        'successful_wakes': successes,
        'per_day': [{'date': str(day), 'count': count} for day, count in per_day],
        'devices': device_stats,
    })


@bp.route('/api/wake-events')
@login_required
def wake_events():
    limit = min(int(request.args.get('limit', 50)), 200)
    events = WakeEvent.query.order_by(WakeEvent.created_at.desc()).limit(limit).all()
    return jsonify([event.to_dict() for event in events])


@bp.route('/api/audit')
@login_required
def audit_logs():
    limit = min(int(request.args.get('limit', 100)), 300)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return jsonify([log.to_dict() for log in logs])


@bp.route('/api/scan', methods=['POST'])
@login_required
@limiter.limit('5 per minute')
def scan_network():
    data = request.get_json(silent=True) or {}
    subnet = data.get('subnet')
    if not subnet and data.get('ip'):
        subnet = subnet_from_ip(data['ip'])
    if not subnet:
        return json_error('SUBNET_REQUIRED', 400)
    hosts = scan_subnet(subnet, max_hosts=int(data.get('max_hosts', 64)))
    return jsonify({'subnet': subnet, 'hosts': hosts})


@bp.route('/api/logs')
@login_required
def get_logs():
    lines = min(int(request.args.get('lines', 100)), 500)
    if not LOG_FILE.exists():
        return jsonify({'logs': []}), 200
    content = LOG_FILE.read_text(encoding='utf-8', errors='replace').splitlines()
    return jsonify({'logs': content[-lines:]})
