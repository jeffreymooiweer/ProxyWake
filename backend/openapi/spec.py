from version import __version__

API_SCOPES = {
    'read': 'Read devices, status, and wake jobs',
    'write': 'Create, update, and delete devices',
    'wake': 'Trigger wake actions',
    'admin': 'Full API access including backup and settings',
}


def build_openapi_spec(base_url=''):
    server_url = base_url or '/'
    return {
        'openapi': '3.0.3',
        'info': {
            'title': 'ProxyWake API',
            'version': __version__,
            'description': 'Self-hosted Wake-on-LAN platform API. Authenticate via session cookie or API key (Bearer / X-API-Key).',
        },
        'servers': [{'url': server_url}],
        'components': {
            'securitySchemes': {
                'ApiKeyAuth': {
                    'type': 'apiKey',
                    'in': 'header',
                    'name': 'X-API-Key',
                },
                'BearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                },
            },
            'schemas': {
                'Device': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'domain': {'type': 'string'},
                        'ip': {'type': 'string'},
                        'mac': {'type': 'string'},
                        'wake_method': {'type': 'string', 'enum': ['wol', 'ssh', 'webhook', 'home_assistant', 'ipmi']},
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
        'security': [{'ApiKeyAuth': []}, {'BearerAuth': []}],
        'tags': [
            {'name': 'devices', 'description': 'Device management and wake actions'},
            {'name': 'backup', 'description': 'Full configuration backup and restore'},
            {'name': 'groups', 'description': 'Device groups'},
            {'name': 'health', 'description': 'Health and metrics'},
            {'name': 'public', 'description': 'Unauthenticated public wake endpoints'},
        ],
        'paths': _paths(),
        'x-api-scopes': API_SCOPES,
    }


def _paths():
    return {
        '/api/health': {
            'get': {
                'tags': ['health'],
                'summary': 'Health check',
                'security': [],
                'responses': {'200': {'description': 'Service healthy'}},
            },
        },
        '/api/devices': {
            'get': {
                'tags': ['devices'],
                'summary': 'List devices',
                'x-scopes': ['read', 'admin'],
                'parameters': [
                    {'name': 'status', 'in': 'query', 'schema': {'type': 'boolean'}},
                ],
                'responses': {
                    '200': {
                        'description': 'Device list',
                        'content': {'application/json': {'schema': {'type': 'array', 'items': {'$ref': '#/components/schemas/Device'}}}},
                    },
                },
            },
            'post': {
                'tags': ['devices'],
                'summary': 'Create device',
                'x-scopes': ['write', 'admin'],
                'responses': {'201': {'description': 'Device created'}},
            },
        },
        '/api/devices/{device_id}/wake': {
            'post': {
                'tags': ['devices'],
                'summary': 'Wake device',
                'x-scopes': ['wake', 'admin'],
                'parameters': [
                    {'name': 'device_id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}},
                    {'name': 'verify', 'in': 'query', 'schema': {'type': 'boolean'}},
                    {'name': 'force', 'in': 'query', 'schema': {'type': 'boolean'}},
                ],
                'responses': {
                    '200': {'description': 'Wake sent'},
                    '202': {'description': 'Verified wake job started', 'content': {'application/json': {'schema': {'$ref': '#/components/schemas/WakeJob'}}}},
                },
            },
        },
        '/api/wake/jobs/{job_id}': {
            'get': {
                'tags': ['devices'],
                'summary': 'Poll wake job status',
                'x-scopes': ['read', 'admin'],
                'parameters': [{'name': 'job_id', 'in': 'path', 'required': True, 'schema': {'type': 'string'}}],
                'responses': {'200': {'description': 'Job status', 'content': {'application/json': {'schema': {'$ref': '#/components/schemas/WakeJob'}}}}},
            },
        },
        '/api/devices/{device_id}/dependencies': {
            'get': {
                'tags': ['devices'],
                'summary': 'Get device dependencies',
                'x-scopes': ['read', 'admin'],
                'responses': {'200': {'description': 'Dependency list'}},
            },
            'put': {
                'tags': ['devices'],
                'summary': 'Set device dependencies',
                'x-scopes': ['write', 'admin'],
                'responses': {'200': {'description': 'Dependencies updated'}},
            },
        },
        '/api/backup': {
            'get': {
                'tags': ['backup'],
                'summary': 'Download full configuration backup',
                'x-scopes': ['admin'],
                'responses': {'200': {'description': 'Backup JSON'}},
            },
        },
        '/api/backup/restore': {
            'post': {
                'tags': ['backup'],
                'summary': 'Restore configuration from backup',
                'x-scopes': ['admin'],
                'responses': {'200': {'description': 'Backup restored'}},
            },
        },
        '/api/public/wake/{domain}': {
            'post': {
                'tags': ['public'],
                'summary': 'Public wake by domain',
                'security': [],
                'responses': {'200': {'description': 'Wake processed'}},
            },
        },
        '/api/groups': {
            'get': {
                'tags': ['groups'],
                'summary': 'List device groups',
                'x-scopes': ['read', 'admin'],
                'responses': {'200': {'description': 'Group list'}},
            },
        },
        '/api/groups/{group_id}/wake': {
            'post': {
                'tags': ['groups'],
                'summary': 'Wake all devices in a group',
                'x-scopes': ['wake', 'admin'],
                'responses': {'200': {'description': 'Group wake results'}},
            },
        },
        '/api/metrics': {
            'get': {
                'tags': ['health'],
                'summary': 'Prometheus metrics',
                'security': [],
                'responses': {'200': {'description': 'Prometheus text format'}},
            },
        },
    }
