import logging
import threading
from datetime import datetime

from models import Device
from services.wake_service import smart_wake_device

_scheduler_started = False


def start_scheduler(app):
    global _scheduler_started
    if _scheduler_started:
        return
    _scheduler_started = True

    def loop():
        import time
        from models import ScheduledWake

        while True:
            try:
                with app.app_context():
                    now = datetime.now()
                    weekday = str(now.weekday())
                    schedules = ScheduledWake.query.filter_by(enabled=True).all()
                    for schedule in schedules:
                        days = schedule.days.split(',')
                        if weekday not in days:
                            continue
                        if schedule.hour == now.hour and schedule.minute == now.minute:
                            device = Device.query.get(schedule.device_id)
                            if device:
                                try:
                                    smart_wake_device(device, source='scheduled')
                                except Exception as exc:
                                    logging.error('Geplande wake mislukt: %s', exc)
            except Exception as exc:
                logging.error('Scheduler fout: %s', exc)
            time.sleep(60)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
