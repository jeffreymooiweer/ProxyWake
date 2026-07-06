from flask import Blueprint, jsonify, request

from auth import api_key_or_session_required, login_required
from models import DeviceGroup, db
from services.wake_service import wake_group
from utils.http import json_error, json_message

bp = Blueprint('groups', __name__)


@bp.route('/api/groups')
@api_key_or_session_required
def list_groups():
    return jsonify([group.to_dict() for group in DeviceGroup.query.all()])


@bp.route('/api/groups', methods=['POST'])
@login_required
def create_group():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return json_error('GROUP_NAME_REQUIRED', 400)
    group = DeviceGroup(name=name, color=data.get('color', '#6366f1'))
    db.session.add(group)
    db.session.commit()
    return jsonify(group.to_dict()), 201


@bp.route('/api/groups/<int:group_id>/wake', methods=['POST'])
@api_key_or_session_required
def wake_group_route(group_id):
    DeviceGroup.query.get_or_404(group_id)
    return jsonify({'results': wake_group(group_id)}), 200


@bp.route('/api/groups/<int:group_id>', methods=['PUT', 'DELETE'])
@login_required
def modify_group(group_id):
    group = DeviceGroup.query.get_or_404(group_id)
    if request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        group.name = data.get('name', group.name)
        group.color = data.get('color', group.color)
        db.session.commit()
        return jsonify(group.to_dict()), 200
    db.session.delete(group)
    db.session.commit()
    return json_message('GROUP_DELETED')
