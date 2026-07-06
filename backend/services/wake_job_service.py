import threading
import uuid
from datetime import datetime, timezone

_jobs = {}
_lock = threading.Lock()


def create_wake_job(device_id):
    job_id = str(uuid.uuid4())
    with _lock:
        _jobs[job_id] = {
            'job_id': job_id,
            'device_id': device_id,
            'status': 'starting',
            'message_code': None,
            'online': False,
            'waited_ms': None,
            'error': None,
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }
    return job_id


def get_wake_job(job_id):
    with _lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None


def update_wake_job(job_id, **kwargs):
    with _lock:
        if job_id not in _jobs:
            return
        _jobs[job_id].update(kwargs)
        _jobs[job_id]['updated_at'] = datetime.now(timezone.utc).isoformat()


def start_verified_wake(app, device, job_id, force=False):
    def run():
        with app.app_context():
            from models import Device
            from services.wake_service import run_verified_wake

            fresh_device = Device.query.get(device.id)
            if fresh_device:
                run_verified_wake(fresh_device, job_id, source='manual', force=force)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
