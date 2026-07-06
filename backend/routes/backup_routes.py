from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from auth import api_key_or_session_required, login_required
from services.backup_service import create_backup, restore_backup
from services.settings_service import log_audit
from utils.http import actor_ip, json_error

bp = Blueprint('backup', __name__)


@bp.route('/api/backup')
@api_key_or_session_required('admin')
def download_backup():
    data = create_backup()
    log_audit('backup_exported', data.get('exported_at'), actor_ip())
    return jsonify(data), 200, {
        'Content-Disposition': f'attachment; filename=proxywake-backup-{datetime.now(timezone.utc).strftime("%Y%m%d")}.json',
    }


@bp.route('/api/backup/restore', methods=['POST'])
@api_key_or_session_required('admin')
def restore_backup_route():
    data = request.get_json(silent=True) or {}
    merge = data.get('merge', True)
    payload = data.get('backup') or data
    try:
        summary = restore_backup(payload, merge=merge)
    except ValueError:
        return json_error('INVALID_BACKUP', 400)
    log_audit('backup_restored', str(summary), actor_ip())
    return jsonify({'restored': summary}), 200
