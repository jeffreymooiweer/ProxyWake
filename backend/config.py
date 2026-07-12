import json
import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get('PROXYWAKE_DATA_DIR', BASE_DIR))

API_KEY_FILE = DATA_DIR / 'api_keys.json'
PASSWORD_HASH_FILE = DATA_DIR / 'password.hash'
SECRET_KEY_FILE = DATA_DIR / 'secret.key'
LOG_FILE = DATA_DIR / 'app.log'
DB_PATH = DATA_DIR / 'devices.db'


def _read_secret_key_file():
    try:
        return SECRET_KEY_FILE.read_text().strip()
    except OSError:
        return ''


def _write_secret_key_file():
    new_key = secrets.token_hex(32)
    fd = os.open(SECRET_KEY_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as handle:
        handle.write(new_key)
    return new_key


def get_secret_key():
    """Return a stable secret key.

    The key must be identical across gunicorn workers and restarts: it signs
    session cookies and derives the Fernet key for stored device credentials.
    Without the env var, a generated key is persisted in the data directory.
    Creation is serialized with a file lock: with O_EXCL alone the second
    worker could read the file in the window before the winner finished
    writing and end up with an empty key.
    """
    key = os.environ.get('PROXYWAKE_SECRET_KEY')
    if key:
        return key

    stored = _read_secret_key_file()
    if stored:
        return stored

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        import fcntl
    except ImportError:
        return _read_secret_key_file() or _write_secret_key_file()

    with open(DATA_DIR / 'secret.key.lock', 'w') as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        stored = _read_secret_key_file()
        if stored:
            return stored
        return _write_secret_key_file()


VALID_API_SCOPES = ('read', 'write', 'wake', 'admin')


def _load_api_keys():
    env_key = os.environ.get('PROXYWAKE_API_KEY', '').strip()
    if env_key:
        return {'current': env_key, 'previous': None, 'scopes': list(VALID_API_SCOPES)}

    if API_KEY_FILE.exists():
        try:
            data = json.loads(API_KEY_FILE.read_text())
            return {
                'current': data.get('current', ''),
                'previous': data.get('previous'),
                'scopes': data.get('scopes'),
            }
        except (json.JSONDecodeError, OSError):
            pass

    new_key = secrets.token_urlsafe(32)
    _save_api_keys(new_key, None)
    return {'current': new_key, 'previous': None, 'scopes': None}


def _save_api_keys(current, previous, scopes=None):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {'current': current, 'previous': previous}
    if scopes is not None:
        payload['scopes'] = list(scopes)
    API_KEY_FILE.write_text(json.dumps(payload))
    API_KEY_FILE.chmod(0o600)


def get_or_create_api_key():
    return _load_api_keys()['current']


def get_previous_api_key():
    return _load_api_keys().get('previous')


def rotate_api_key():
    keys = _load_api_keys()
    new_key = secrets.token_urlsafe(32)
    _save_api_keys(new_key, keys['current'], scopes=keys.get('scopes'))
    return new_key


def get_api_key_scopes():
    scopes = _load_api_keys().get('scopes')
    if not scopes:
        return list(VALID_API_SCOPES)
    return [scope for scope in scopes if scope in VALID_API_SCOPES] or list(VALID_API_SCOPES)


def set_api_key_scopes(scopes):
    keys = _load_api_keys()
    cleaned = [scope for scope in (scopes or []) if scope in VALID_API_SCOPES]
    if not cleaned:
        cleaned = list(VALID_API_SCOPES)
    _save_api_keys(keys['current'], keys['previous'], scopes=cleaned)
    return cleaned


def get_admin_password_hash():
    env_hash = os.environ.get('PROXYWAKE_PASSWORD_HASH', '').strip()
    if env_hash:
        return env_hash

    env_password = os.environ.get('PROXYWAKE_PASSWORD', '').strip()
    if env_password:
        from auth import hash_password
        return hash_password(env_password)

    if PASSWORD_HASH_FILE.exists():
        return PASSWORD_HASH_FILE.read_text().strip()

    return ''


def save_admin_password_hash(password_hash):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PASSWORD_HASH_FILE.write_text(password_hash)
    PASSWORD_HASH_FILE.chmod(0o600)


def get_allowed_origins():
    origins = os.environ.get('PROXYWAKE_ALLOWED_ORIGINS', '')
    if origins:
        return [origin.strip() for origin in origins.split(',') if origin.strip()]
    return None


def session_cookie_secure():
    """Whether Flask session cookies require HTTPS (set PROXYWAKE_SESSION_COOKIE_SECURE=true behind TLS)."""
    value = os.environ.get('PROXYWAKE_SESSION_COOKIE_SECURE', '').strip().lower()
    if value in ('1', 'true', 'yes', 'on'):
        return True
    if value in ('0', 'false', 'no', 'off'):
        return False
    return False


SUPPORTED_LANGUAGES = (
    'en', 'nl', 'de', 'fr', 'es', 'it', 'pt', 'pl', 'sv',
    'ja', 'zh', 'ko', 'ru', 'tr', 'uk',
)


def is_supported_language(language):
    return language in SUPPORTED_LANGUAGES
