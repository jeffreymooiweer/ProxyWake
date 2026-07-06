from flask import Blueprint, jsonify

from extensions import limiter
from models import Device
from services.wake_service import wake_and_wait
from utils.http import json_error

bp = Blueprint('public', __name__)


@bp.route('/api/public/status/<domain>')
@limiter.limit('120 per minute')
def public_status(domain):
    device = Device.query.filter_by(domain=domain.lower()).first()
    if not device:
        return json_error('DEVICE_NOT_FOUND', 404)
    return jsonify({
        'domain': device.domain,
        'name': device.name or device.domain,
        'online': device.to_dict(include_status=True)['online'],
    })


@bp.route('/api/public/wake/<domain>', methods=['POST'])
@limiter.limit('30 per minute')
def public_wake(domain):
    device = Device.query.filter_by(domain=domain.lower()).first()
    if not device:
        return json_error('DEVICE_NOT_FOUND', 404)
    result = wake_and_wait(device, source='public')
    return jsonify(result), 200
