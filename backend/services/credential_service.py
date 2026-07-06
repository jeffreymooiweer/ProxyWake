from models import DeviceCredential, db
from utils.crypto import decrypt_value, encrypt_value

SUPPORTED_CREDENTIAL_KEYS = ('ssh_password', 'ssh_private_key')


def save_credentials(device_id, credentials):
    if not credentials:
        return
    for key, value in credentials.items():
        if key not in SUPPORTED_CREDENTIAL_KEYS:
            continue
        if value in (None, ''):
            delete_credential(device_id, key)
            continue
        row = DeviceCredential.query.filter_by(device_id=device_id, key=key).first()
        encrypted = encrypt_value(value)
        if row:
            row.encrypted_value = encrypted
        else:
            db.session.add(DeviceCredential(device_id=device_id, key=key, encrypted_value=encrypted))
    db.session.commit()


def get_credential(device_id, key):
    row = DeviceCredential.query.filter_by(device_id=device_id, key=key).first()
    if not row:
        return ''
    return decrypt_value(row.encrypted_value)


def delete_credential(device_id, key):
    row = DeviceCredential.query.filter_by(device_id=device_id, key=key).first()
    if row:
        db.session.delete(row)
        db.session.commit()


def credentials_configured(device_id):
    return DeviceCredential.query.filter_by(device_id=device_id).count() > 0
