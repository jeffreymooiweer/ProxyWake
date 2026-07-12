import csv
import io
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request

from auth import api_key_or_session_required, login_required
from extensions import limiter
from models import Device, DeviceDependency, ScheduledWake, WakeEvent, db
from services.credential_service import save_credentials
from services.dependency_service import (
    DependencyCycleError,
    dependencies_to_dict,
    set_device_dependencies,
)
from services.settings_service import export_devices, import_devices, log_audit
from services.status_service import bulk_online_status
from services.wake_executor import WakeMethodError
from services.wake_job_service import create_wake_job, get_wake_job, start_verified_wake
from services.wake_service import smart_wake_device
from utils.http import actor_ip, json_error, json_message
from utils.validators import validate_device_payload

bp = Blueprint('devices', __name__)


@bp.route('/api/devices')
@api_key_or_session_required('read')
def list_devices():
    include_status = request.args.get('status', 'false').lower() == 'true'
    devices = Device.query.order_by(Device.domain.asc()).all()
    if not include_status:
        return jsonify([device.to_dict() for device in devices])
    online_map = bulk_online_status(devices)
    return jsonify([
        device.to_dict(include_status=True, online=online_map.get(device.id, False))
        for device in devices
    ])


@bp.route('/api/devices', methods=['POST'])
@api_key_or_session_required('write')
def create_device():
    data = request.get_json(silent=True) or {}
    payload, error_code = validate_device_payload(data)
    if error_code:
        return json_error(error_code)
    device = Device(**payload)
    db.session.add(device)
    db.session.commit()
    log_audit('device_created', device.domain, actor_ip())
    return jsonify(device.to_dict()), 201


@bp.route('/api/devices/<int:device_id>', methods=['PUT', 'DELETE'])
@api_key_or_session_required('write')
def modify_device(device_id):
    device = Device.query.get_or_404(device_id)
    if request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        payload, error_code = validate_device_payload(data, device=device)
        if error_code:
            return json_error(error_code)
        for key, value in payload.items():
            setattr(device, key, value)
        db.session.commit()
        log_audit('device_updated', device.domain, actor_ip())
        return jsonify(device.to_dict()), 200

    domain = device.domain
    # Remove dependent rows first: wake_event.device_id and schedule rows are
    # NOT NULL, so deleting the device alone fails with an IntegrityError.
    WakeEvent.query.filter_by(device_id=device.id).delete()
    ScheduledWake.query.filter_by(device_id=device.id).delete()
    DeviceDependency.query.filter(
        (DeviceDependency.device_id == device.id)
        | (DeviceDependency.depends_on_device_id == device.id)
    ).delete()
    db.session.delete(device)
    db.session.commit()
    log_audit('device_deleted', domain, actor_ip())
    return json_message('DEVICE_DELETED')


@bp.route('/api/devices/<int:device_id>/wake', methods=['POST'])
@limiter.limit('30 per minute')
@api_key_or_session_required('wake')
def wake_device(device_id):
    device = Device.query.get_or_404(device_id)
    force = request.args.get('force', 'false').lower() == 'true'
    verify = request.args.get('verify', 'false').lower() == 'true'

    if verify:
        job_id = create_wake_job(device.id)
        start_verified_wake(current_app._get_current_object(), device, job_id, force=force)
        return jsonify({'job_id': job_id, 'status': 'starting', 'device_id': device.id}), 202

    try:
        result = smart_wake_device(device, source='manual', force=force)
        return jsonify(result), 200
    except WakeMethodError as exc:
        return json_error(exc.code, 500)
    except Exception:
        return json_error('WAKE_FAILED', 500)


@bp.route('/api/devices/<int:device_id>/dependencies')
@api_key_or_session_required('read')
def get_device_dependencies(device_id):
    Device.query.get_or_404(device_id)
    return jsonify({'dependencies': dependencies_to_dict(device_id)})


@bp.route('/api/devices/<int:device_id>/dependencies', methods=['PUT'])
@api_key_or_session_required('write')
def update_device_dependencies(device_id):
    Device.query.get_or_404(device_id)
    data = request.get_json(silent=True) or {}
    try:
        depends_on = set_device_dependencies(device_id, data.get('depends_on', []))
    except DependencyCycleError:
        return json_error('DEPENDENCY_CYCLE', 400)
    log_audit('device_dependencies_updated', str(depends_on), actor_ip())
    return jsonify({'depends_on': depends_on, 'dependencies': dependencies_to_dict(device_id)})


@bp.route('/api/devices/<int:device_id>/credentials', methods=['PUT'])
@login_required
def update_device_credentials(device_id):
    Device.query.get_or_404(device_id)
    data = request.get_json(silent=True) or {}
    save_credentials(device_id, data.get('credentials', {}))
    log_audit('device_credentials_updated', str(device_id), actor_ip())
    return jsonify({'saved': True}), 200


@bp.route('/api/wake/jobs/<job_id>')
@api_key_or_session_required('read')
def wake_job_status(job_id):
    job = get_wake_job(job_id)
    if not job:
        return json_error('NOT_FOUND', 404)
    return jsonify(job)


@bp.route('/api/devices/<int:device_id>/status')
@api_key_or_session_required('read')
def device_status(device_id):
    device = Device.query.get_or_404(device_id)
    return jsonify(device.to_dict(include_status=True))


@bp.route('/api/devices/export')
@login_required
def export_devices_route():
    fmt = request.args.get('format', 'json')
    devices = export_devices()
    if fmt == 'csv':
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['name', 'domain', 'ip', 'mac', 'use_broadcast', 'wake_cooldown_seconds'])
        writer.writeheader()
        for device in devices:
            writer.writerow({key: device.get(key) for key in writer.fieldnames})
        return output.getvalue(), 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=proxywake-devices.csv'}
    return jsonify({'devices': devices, 'exported_at': datetime.now(timezone.utc).isoformat()})


@bp.route('/api/devices/import', methods=['POST'])
@login_required
def import_devices_route():
    data = request.get_json(silent=True) or {}
    devices = data.get('devices', [])
    merge = data.get('merge', True)
    count = import_devices(devices, merge=merge)
    log_audit('devices_imported', f'{count} apparaten', actor_ip())
    return jsonify({'imported': count}), 200
