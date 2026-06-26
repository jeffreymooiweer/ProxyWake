import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get('PROXYWAKE_DATA_DIR', BASE_DIR))

API_KEY_FILE = DATA_DIR / '.api_key'
LOG_FILE = DATA_DIR / 'app.log'
DB_PATH = DATA_DIR / 'devices.db'


def get_secret_key():
    key = os.environ.get('PROXYWAKE_SECRET_KEY')
    if key:
        return key
    return secrets.token_hex(32)


def get_or_create_api_key():
    env_key = os.environ.get('PROXYWAKE_API_KEY')
    if env_key:
        return env_key.strip()

    if API_KEY_FILE.exists():
        return API_KEY_FILE.read_text().strip()

    new_key = secrets.token_urlsafe(32)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    API_KEY_FILE.write_text(new_key)
    API_KEY_FILE.chmod(0o600)
    return new_key


def get_admin_password():
    return os.environ.get('PROXYWAKE_PASSWORD', '').strip()


def get_allowed_origins():
    origins = os.environ.get('PROXYWAKE_ALLOWED_ORIGINS', '')
    if origins:
        return [origin.strip() for origin in origins.split(',') if origin.strip()]
    return None
