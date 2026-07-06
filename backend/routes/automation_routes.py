from flask import Blueprint, jsonify, request

from auth import login_required
from models import ScheduledWake, Webhook, db
from utils.http import json_message

bp = Blueprint('automation', __name__)


@bp.route('/api/webhooks')
@login_required
def list_webhooks():
    return jsonify([hook.to_dict() for hook in Webhook.query.all()])


@bp.route('/api/webhooks', methods=['POST'])
@login_required
def create_webhook():
    data = request.get_json(silent=True) or {}
    hook = Webhook(
        name=data.get('name'),
        url=data.get('url'),
        events=','.join(data.get('events', ['wake_failed', 'wake_success'])),
        enabled=data.get('enabled', True),
    )
    db.session.add(hook)
    db.session.commit()
    return jsonify(hook.to_dict()), 201


@bp.route('/api/webhooks/<int:hook_id>', methods=['PUT', 'DELETE'])
@login_required
def modify_webhook(hook_id):
    hook = Webhook.query.get_or_404(hook_id)
    if request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        hook.name = data.get('name', hook.name)
        hook.url = data.get('url', hook.url)
        hook.events = ','.join(data.get('events', hook.events.split(',')))
        hook.enabled = data.get('enabled', hook.enabled)
        db.session.commit()
        return jsonify(hook.to_dict()), 200
    db.session.delete(hook)
    db.session.commit()
    return json_message('WEBHOOK_DELETED')


@bp.route('/api/schedules')
@login_required
def list_schedules():
    return jsonify([item.to_dict() for item in ScheduledWake.query.all()])


@bp.route('/api/schedules', methods=['POST'])
@login_required
def create_schedule():
    data = request.get_json(silent=True) or {}
    schedule = ScheduledWake(
        device_id=data.get('device_id'),
        hour=int(data.get('hour', 7)),
        minute=int(data.get('minute', 0)),
        days=','.join(str(day) for day in data.get('days', [0, 1, 2, 3, 4, 5, 6])),
        enabled=data.get('enabled', True),
    )
    db.session.add(schedule)
    db.session.commit()
    return jsonify(schedule.to_dict()), 201


@bp.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
@login_required
def delete_schedule(schedule_id):
    schedule = ScheduledWake.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    return json_message('SCHEDULE_DELETED')
