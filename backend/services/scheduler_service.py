import logging
import threading
import time
from datetime import datetime

from models import Device
from services.wake_service import smart_wake_device

_scheduler_started = False
_lock_handle = None


def _acquire_scheduler_lock():
    """Take a data-dir file lock so only one gunicorn worker runs the scheduler."""
    global _lock_handle
    try:
        import fcntl

        from config import DATA_DIR

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        handle = open(DATA_DIR / 'scheduler.lock', 'w')
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            handle.close()
            return False
        _lock_handle = handle
        return True
    except ImportError:
        # Non-POSIX platform (dev only): run without the lock.
        return True


def start_scheduler(app):
    global _scheduler_started
    if _scheduler_started:
        return
    if not _acquire_scheduler_lock():
        logging.info('Scheduler already running in another worker; skipping in this process')
        return
    _scheduler_started = True

    def loop():
        from models import ScheduledWake

        last_fired = set()
        while True:
            try:
                with app.app_context():
                    now = datetime.now()
                    weekday = str(now.weekday())
                    minute_key = now.strftime('%Y-%m-%d %H:%M')
                    schedules = ScheduledWake.query.filter_by(enabled=True).all()
                    for schedule in schedules:
                        days = schedule.days.split(',') if schedule.days else []
                        if weekday not in days:
                            continue
                        if schedule.hour != now.hour or schedule.minute != now.minute:
                            continue
                        fire_key = (schedule.id, minute_key)
                        if fire_key in last_fired:
                            continue
                        last_fired.add(fire_key)
                        device = Device.query.get(schedule.device_id)
                        if device:
                            try:
                                smart_wake_device(device, source='scheduled')
                            except Exception as exc:
                                logging.error('Geplande wake mislukt: %s', exc)
                    if len(last_fired) > 1000:
                        last_fired = {key for key in last_fired if key[1] == minute_key}
            except Exception as exc:
                logging.error('Scheduler fout: %s', exc)
            # Wake up just past the next minute boundary so no minute is skipped.
            time.sleep(max(1, 61 - datetime.now().second))

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
