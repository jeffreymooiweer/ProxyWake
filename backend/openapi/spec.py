import re

from version import __version__

API_SCOPES = {
    'read': 'Read devices, status, and wake jobs',
    'write': 'Create, update, and delete devices',
    'wake': 'Trigger wake actions',
    'admin': 'Full API access including backup and settings',
}

PUBLIC_PATHS = {
    '/api/health',
    '/api/metrics',
    '/api/auth/login',
    '/api/auth/status',
    '/api/setup',
    '/api/openapi.json',
    '/api/docs',
    '/api/public/status/{domain}',
    '/api/public/wake/{domain}',
}

SESSION_ONLY_PATHS = {
    '/api/settings',
    '/api/settings/language',
    '/api/settings/theme',
    '/api/settings/password',
    '/api/settings/rotate-api-key',
    '/api/settings/api-scopes',
    '/api/settings/log-level',
    '/api/settings/notifications',
    '/api/devices/export',
    '/api/devices/import',
    '/api/devices/{device_id}/credentials',
    '/api/groups',
    '/api/groups/{group_id}',
    '/api/webhooks',
    '/api/webhooks/{hook_id}',
    '/api/schedules',
    '/api/schedules/{schedule_id}',
    '/api/stats',
    '/api/wake-events',
    '/api/audit',
    '/api/scan',
    '/api/logs',
    '/api/npm-hosts',
    '/api/npm-hosts/{host_id}',
    '/api/npm/config',
    '/api/npm/config/{device_id}',
    '/api/npm/test/{device_id}',
    '/api/auth/logout',
}


def build_openapi_spec(base_url=''):
    return {
        'openapi': '3.0.3',
        'info': {
            'title': 'ProxyWake API',
            'version': __version__,
            'description': (
                'Self-hosted Wake-on-LAN platform API. '
                'Authenticate via session cookie or API key (Bearer / X-API-Key). '
                'Endpoints marked session-only require a logged-in browser session.'
            ),
        },
        'servers': [{'url': base_url or '/'}],
        'components': {
            'securitySchemes': {
                'ApiKeyAuth': {'type': 'apiKey', 'in': 'header', 'name': 'X-API-Key'},
                'BearerAuth': {'type': 'http', 'scheme': 'bearer'},
                'SessionAuth': {'type': 'apiKey', 'in': 'cookie', 'name': 'session'},
            },
            'schemas': {
                'Device': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'domain': {'type': 'string'},
                        'ip': {'type': 'string'},
                        'mac': {'type': 'string'},
                        'wake_method': {
                            'type': 'string',
                            'enum': ['wol', 'ssh', 'webhook', 'home_assistant', 'ipmi'],
                        },
                        'online': {'type': 'boolean'},
                    },
                },
                'WakeJob': {
                    'type': 'object',
                    'properties': {
                        'job_id': {'type': 'string'},
                        'status': {'type': 'string'},
                        'message_code': {'type': 'string'},
                        'online': {'type': 'boolean'},
                    },
                },
                'Error': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'},
                        'error_code': {'type': 'string'},
                    },
                },
            },
        },
        'security': [{'ApiKeyAuth': []}, {'BearerAuth': []}, {'SessionAuth': []}],
        'tags': [
            {'name': 'auth', 'description': 'Authentication and setup'},
            {'name': 'settings', 'description': 'Application settings'},
            {'name': 'devices', 'description': 'Device management and wake actions'},
            {'name': 'groups', 'description': 'Device groups'},
            {'name': 'backup', 'description': 'Full configuration backup and restore'},
            {'name': 'automation', 'description': 'Webhooks and scheduled wake'},
            {'name': 'integration', 'description': 'NPM and proxy integration'},
            {'name': 'stats', 'description': 'Statistics, logs, and network scan'},
            {'name': 'health', 'description': 'Health and metrics'},
            {'name': 'public', 'description': 'Unauthenticated public endpoints'},
            {'name': 'docs', 'description': 'API documentation'},
        ],
        'paths': _paths(),
        'x-api-scopes': API_SCOPES,
    }


def flask_rule_to_openapi(rule):
    return re.sub(r'<(?:\w+:)?(\w+)>', r'{\1}', rule)


def collect_flask_api_paths(app):
    paths = {}
    for rule in app.url_map.iter_rules():
        if not rule.rule.startswith('/api/'):
            continue
        openapi_path = flask_rule_to_openapi(rule.rule)
        methods = sorted(m for m in rule.methods if m not in {'HEAD', 'OPTIONS'})
        paths.setdefault(openapi_path, set()).update(method.lower() for method in methods)
    return paths


def _op(summary, tag, scopes=None, session_only=False, public=False, parameters=None, responses=None):
    operation = {'summary': summary, 'tags': [tag]}
    if public:
        operation['security'] = []
    elif session_only:
        operation['security'] = [{'SessionAuth': []}]
        operation['x-session-only'] = True
    elif scopes:
        operation['x-scopes'] = scopes
    if parameters:
        operation['parameters'] = parameters
    operation['responses'] = responses or {'200': {'description': 'OK'}}
    return operation


def _path_id(name='id', type_='integer'):
    return {'name': name, 'in': 'path', 'required': True, 'schema': {'type': type_}}


def _paths():
    paths = {}

    def add(path, **methods):
        paths[path] = methods

    add('/api/health', get=_op('Health check', 'health', public=True))
    add('/api/metrics', get=_op('Prometheus metrics', 'health', public=True))

    add('/api/auth/status', get=_op('Authentication status', 'auth', public=True))
    add('/api/auth/login', post=_op('Log in', 'auth', public=True))
    add('/api/auth/logout', post=_op('Log out', 'auth', session_only=True))
    add('/api/setup', post=_op('Complete initial setup', 'auth', public=True))

    add('/api/settings', get=_op('Get settings', 'settings', session_only=True))
    add('/api/settings/language', put=_op('Update language', 'settings', session_only=True))
    add('/api/settings/theme', put=_op('Update theme', 'settings', session_only=True))
    add('/api/settings/password', put=_op('Update password', 'settings', session_only=True))
    add('/api/settings/rotate-api-key', post=_op('Rotate API key', 'settings', session_only=True))
    add('/api/settings/api-scopes', put=_op('Update API key scopes', 'settings', session_only=True))
    add('/api/settings/log-level', put=_op('Update log level', 'settings', session_only=True))
    add('/api/settings/notifications', put=_op('Update notification channels', 'settings', session_only=True))

    add('/api/devices',
        get=_op('List devices', 'devices', scopes=['read', 'admin'],
                parameters=[{'name': 'status', 'in': 'query', 'schema': {'type': 'boolean'}}]),
        post=_op('Create device', 'devices', scopes=['write', 'admin'], responses={'201': {'description': 'Created'}}))
    add('/api/devices/{device_id}',
        put=_op('Update device', 'devices', scopes=['write', 'admin'], parameters=[_path_id('device_id')]),
        delete=_op('Delete device', 'devices', scopes=['write', 'admin'], parameters=[_path_id('device_id')]))
    add('/api/devices/{device_id}/wake',
        post=_op('Wake device', 'devices', scopes=['wake', 'admin'],
                 parameters=[_path_id('device_id'),
                             {'name': 'verify', 'in': 'query', 'schema': {'type': 'boolean'}},
                             {'name': 'force', 'in': 'query', 'schema': {'type': 'boolean'}}],
                 responses={'200': {'description': 'Wake sent'}, '202': {'description': 'Job started'}}))
    add('/api/devices/{device_id}/status',
        get=_op('Device status', 'devices', scopes=['read', 'admin'], parameters=[_path_id('device_id')]))
    add('/api/devices/{device_id}/dependencies',
        get=_op('Get dependencies', 'devices', scopes=['read', 'admin'], parameters=[_path_id('device_id')]),
        put=_op('Set dependencies', 'devices', scopes=['write', 'admin'], parameters=[_path_id('device_id')]))
    add('/api/devices/{device_id}/credentials',
        put=_op('Save device credentials', 'devices', session_only=True, parameters=[_path_id('device_id')]))
    add('/api/devices/export',
        get=_op('Export devices', 'devices', session_only=True,
                parameters=[{'name': 'format', 'in': 'query', 'schema': {'type': 'string', 'enum': ['json', 'csv']}}]))
    add('/api/devices/import', post=_op('Import devices', 'devices', session_only=True))

    add('/api/wake/jobs/{job_id}',
        get=_op('Poll wake job', 'devices', scopes=['read', 'admin'],
                parameters=[_path_id('job_id', 'string')],
                responses={'200': {'content': {'application/json': {'schema': {'$ref': '#/components/schemas/WakeJob'}}}}}))

    add('/api/groups',
        get=_op('List groups', 'groups', scopes=['read', 'admin']),
        post=_op('Create group', 'groups', session_only=True))
    add('/api/groups/{group_id}',
        put=_op('Update group', 'groups', session_only=True, parameters=[_path_id('group_id')]),
        delete=_op('Delete group', 'groups', session_only=True, parameters=[_path_id('group_id')]))
    add('/api/groups/{group_id}/wake',
        post=_op('Wake group', 'groups', scopes=['wake', 'admin'], parameters=[_path_id('group_id')]))

    add('/api/backup', get=_op('Download backup', 'backup', scopes=['admin']))
    add('/api/backup/restore', post=_op('Restore backup', 'backup', scopes=['admin']))

    add('/api/webhooks',
        get=_op('List webhooks', 'automation', session_only=True),
        post=_op('Create webhook', 'automation', session_only=True, responses={'201': {'description': 'Created'}}))
    add('/api/webhooks/{hook_id}',
        put=_op('Update webhook', 'automation', session_only=True, parameters=[_path_id('hook_id')]),
        delete=_op('Delete webhook', 'automation', session_only=True, parameters=[_path_id('hook_id')]))
    add('/api/schedules',
        get=_op('List schedules', 'automation', session_only=True),
        post=_op('Create schedule', 'automation', session_only=True, responses={'201': {'description': 'Created'}}))
    add('/api/schedules/{schedule_id}',
        delete=_op('Delete schedule', 'automation', session_only=True, parameters=[_path_id('schedule_id')]))

    add('/api/npm-hosts',
        get=_op('List NPM hosts', 'integration', session_only=True),
        post=_op('Create NPM host', 'integration', session_only=True, responses={'201': {'description': 'Created'}}))
    add('/api/npm-hosts/{host_id}',
        delete=_op('Delete NPM host', 'integration', session_only=True, parameters=[_path_id('host_id')]))
    add('/api/wake/by-host',
        get=_op('Wake by Host header (GET)', 'integration', scopes=['wake', 'admin']),
        post=_op('Wake by Host header (POST)', 'integration', scopes=['wake', 'admin']))
    add('/api/npm/config',
        get=_op('Global NPM config snippet', 'integration', session_only=True,
                parameters=[{'name': 'base_url', 'in': 'query', 'schema': {'type': 'string'}}]))
    add('/api/npm/config/{device_id}',
        get=_op('Per-device NPM config', 'integration', session_only=True, parameters=[_path_id('device_id')]))
    add('/api/npm/test/{device_id}',
        post=_op('Test NPM wake flow', 'integration', session_only=True, parameters=[_path_id('device_id')]))

    add('/api/stats', get=_op('Wake statistics', 'stats', session_only=True))
    add('/api/wake-events',
        get=_op('Recent wake events', 'stats', session_only=True,
                parameters=[{'name': 'limit', 'in': 'query', 'schema': {'type': 'integer'}}]))
    add('/api/audit',
        get=_op('Audit log', 'stats', session_only=True,
                parameters=[{'name': 'limit', 'in': 'query', 'schema': {'type': 'integer'}}]))
    add('/api/scan', post=_op('Scan network subnet', 'stats', session_only=True))
    add('/api/logs',
        get=_op('Tail application logs', 'stats', session_only=True,
                parameters=[
                    {'name': 'lines', 'in': 'query', 'schema': {'type': 'integer'}},
                    {'name': 'level', 'in': 'query', 'schema': {'type': 'string'}},
                    {'name': 'search', 'in': 'query', 'schema': {'type': 'string'}},
                ]))

    add('/api/public/status/{domain}',
        get=_op('Public device status', 'public', public=True, parameters=[_path_id('domain', 'string')]))
    add('/api/public/wake/{domain}',
        post=_op('Public wake by domain', 'public', public=True, parameters=[_path_id('domain', 'string')]))

    add('/api/openapi.json', get=_op('OpenAPI specification', 'docs', public=True))
    add('/api/docs', get=_op('Swagger UI', 'docs', public=True))

    return paths
