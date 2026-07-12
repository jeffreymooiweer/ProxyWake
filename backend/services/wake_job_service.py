import json
import threading
import uuid
from datetime import datetime, timedelta, timezone

from models import WakeJob, db

# Jobs are transient; anything older than this is stale and gets pruned.
JOB_RETENTION = timedelta(hours=1)

_COLUMN_FIELDS = ('status', 'message_code', 'online', 'waited_ms', 'error')


def create_wake_job(device_id):
    job_id = str(uuid.uuid4())
    _prune_stale_jobs()
    db.session.add(WakeJob(id=job_id, device_id=device_id, status='starting'))
    db.session.commit()
    return job_id


def get_wake_job(job_id):
    job = db.session.get(WakeJob, job_id)
    if not job:
        return None
    return job.to_dict()


def update_wake_job(job_id, **kwargs):
    job = db.session.get(WakeJob, job_id)
    if not job:
        return
    extra = {}
    if job.extra:
        try:
            extra = json.loads(job.extra)
        except ValueError:
            extra = {}
    for key, value in kwargs.items():
        if key in _COLUMN_FIELDS:
            setattr(job, key, value)
        else:
            extra[key] = value
    if extra:
        job.extra = json.dumps(extra)
    job.updated_at = datetime.now(timezone.utc)
    db.session.commit()


def _prune_stale_jobs():
    cutoff = datetime.now(timezone.utc) - JOB_RETENTION
    WakeJob.query.filter(WakeJob.updated_at < cutoff).delete()


def start_verified_wake(app, device, job_id, force=False):
    def run():
        with app.app_context():
            from models import Device
            from services.wake_service import run_verified_wake

            fresh_device = db.session.get(Device, device.id)
            if fresh_device:
                run_verified_wake(fresh_device, job_id, source='manual', force=force)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
