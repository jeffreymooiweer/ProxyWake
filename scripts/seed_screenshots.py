#!/usr/bin/env python3
"""Seed demo data for README screenshots."""
import os
import sys
from pathlib import Path

DATA_DIR = Path(os.environ.get('PROXYWAKE_DATA_DIR', '/workspace/tmp/proxywake-screenshots'))
os.environ['PROXYWAKE_DATA_DIR'] = str(DATA_DIR)

if DATA_DIR.exists():
    import shutil
    shutil.rmtree(DATA_DIR)
DATA_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'backend'))

from app import app, db
from models import Device, DeviceGroup
from services import set_setting

with app.app_context():
    db.create_all()
    set_setting('onboarding_completed', 'true')
    set_setting('language', 'en')
    set_setting('theme', 'dark')
    set_setting('proxywake_url', 'http://192.168.1.6:5001')

    media = DeviceGroup(name='Media', color='#39ff14')
    infra = DeviceGroup(name='Infrastructure', color='#22d3ee')
    db.session.add_all([media, infra])
    db.session.flush()

    devices = [
        Device(name='NAS Server', domain='nas.home.lab', ip='192.168.1.50', mac='AA:BB:CC:DD:EE:01', group_id=infra.id, wake_cooldown_seconds=30),
        Device(name='Plex Media', domain='plex.home.lab', ip='192.168.1.60', mac='AA:BB:CC:DD:EE:02', group_id=media.id, use_broadcast=True, wake_cooldown_seconds=45),
        Device(name='Gaming PC', domain='gaming.home.lab', ip='192.168.1.70', mac='AA:BB:CC:DD:EE:03', group_id=media.id, wake_cooldown_seconds=30),
        Device(name='Home Assistant', domain='ha.home.lab', ip='192.168.1.80', mac='AA:BB:CC:DD:EE:04', group_id=infra.id, wake_cooldown_seconds=60),
    ]
    db.session.add_all(devices)
    db.session.commit()
    print(f'Demo data seeded in {DATA_DIR}')
