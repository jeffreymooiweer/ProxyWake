import base64
from hashlib import sha256

from cryptography.fernet import Fernet, InvalidToken

from config import get_secret_key


def _fernet():
    digest = sha256(get_secret_key().encode()).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_value(value):
    if not value:
        return ''
    return _fernet().encrypt(value.encode()).decode()


def decrypt_value(value):
    if not value:
        return ''
    try:
        return _fernet().decrypt(value.encode()).decode()
    except InvalidToken:
        return ''
