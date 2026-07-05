ERROR_MESSAGES = {
    'AUTH_REQUIRED': 'Authentication required.',
    'INVALID_API_KEY': 'Invalid or missing API key.',
    'INVALID_PASSWORD': 'Incorrect password.',
    'SETUP_ALREADY_COMPLETE': 'Setup has already been completed.',
    'INVALID_LANGUAGE': 'Invalid language.',
    'PASSWORD_TOO_SHORT': 'Password must be at least 8 characters.',
    'REQUIRED_FIELDS': 'All required fields must be filled in.',
    'INVALID_DOMAIN': 'Invalid domain name.',
    'INVALID_IP': 'Invalid IP address.',
    'INVALID_MAC': 'Invalid MAC address.',
    'DOMAIN_ALREADY_EXISTS': 'This domain is already linked to another device.',
    'GROUP_NAME_REQUIRED': 'Group name is required.',
    'HOST_HEADER_MISSING': 'Host header is missing.',
    'DEVICE_NOT_FOUND': 'Device not found.',
    'DEVICE_NOT_FOUND_FOR_DOMAIN': 'No device found for this domain.',
    'SUBNET_REQUIRED': 'Subnet or IP is required.',
    'NOT_FOUND': 'Resource not found.',
    'RATE_LIMITED': 'Too many requests. Please try again later.',
    'WAKE_FAILED': 'Failed to send magic packet.',
    'INTERNAL_ERROR': 'Internal server error.',
    'GENERIC': 'Something went wrong.',
}

MESSAGE_CODES = {
    'NO_PASSWORD_CONFIGURED': 'No password configured, session started.',
    'LOGIN_SUCCESS': 'Successfully logged in.',
    'LOGOUT_SUCCESS': 'Logged out.',
    'SETUP_COMPLETE': 'Setup completed.',
    'PASSWORD_UPDATED': 'Password updated.',
    'API_KEY_ROTATED': 'API key rotated. Previous key remains valid temporarily.',
    'DEVICE_DELETED': 'Device deleted.',
    'GROUP_DELETED': 'Group deleted.',
    'NPM_HOST_DELETED': 'NPM host deleted.',
    'WEBHOOK_DELETED': 'Webhook deleted.',
    'SCHEDULE_DELETED': 'Schedule deleted.',
    'DEVICE_ALREADY_ONLINE': '{{name}} is already online.',
    'DEVICE_COOLDOWN': 'Cooldown active. Wait {{seconds}} more seconds.',
    'WAKE_SENT': 'Magic packet sent to {{name}}.',
    'WAKE_SKIPPED_ONLINE': '{{name}} is already online.',
    'WAKE_PROCESSED': 'Wake processed for {{domain}}.',
    'WAKE_TIMEOUT': 'Timed out waiting for device to start.',
    'ALREADY_ONLINE': 'Device is already online.',
}


def error_response(code, status=400, **extra):
    payload = {'error': ERROR_MESSAGES.get(code, ERROR_MESSAGES['GENERIC']), 'error_code': code}
    payload.update(extra)
    return payload, status


def message_response(code, status=200, **params):
    text = MESSAGE_CODES.get(code, code)
    for key, value in params.items():
        text = text.replace(f'{{{{{key}}}}}', str(value))
    return {'message': text, 'message_code': code, **params}, status
