from flask import Blueprint, jsonify

from extensions import limiter
from models import Device, WakeEvent
from version import __version__

bp = Blueprint('health', __name__)


@bp.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'service': 'ProxyWake', 'version': __version__})


@bp.route('/api/metrics')
def metrics():
    device_count = Device.query.count()
    wake_total = WakeEvent.query.count()
    wake_success = WakeEvent.query.filter_by(success=True, skipped=False).count()
    lines = [
        '# HELP proxywake_devices_total Total configured devices',
        '# TYPE proxywake_devices_total gauge',
        f'proxywake_devices_total {device_count}',
        '# HELP proxywake_wake_events_total Total wake events',
        '# TYPE proxywake_wake_events_total counter',
        f'proxywake_wake_events_total {wake_total}',
        '# HELP proxywake_wake_success_total Successful wake events',
        '# TYPE proxywake_wake_success_total counter',
        f'proxywake_wake_success_total {wake_success}',
    ]
    return '\n'.join(lines) + '\n', 200, {'Content-Type': 'text/plain; version=0.0.4'}
