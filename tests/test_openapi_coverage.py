"""Tests that OpenAPI spec covers all Flask /api routes."""


def test_openapi_covers_all_api_routes(client):
    from app import app
    from openapi.spec import build_openapi_spec, collect_flask_api_paths

    flask_paths = collect_flask_api_paths(app)
    spec_paths = build_openapi_spec()['paths']

    missing = []
    for path, methods in sorted(flask_paths.items()):
        if path not in spec_paths:
            missing.append(f'{path} (all methods)')
            continue
        for method in methods:
            if method not in spec_paths[path]:
                missing.append(f'{method.upper()} {path}')

    assert not missing, 'OpenAPI spec missing routes:\n' + '\n'.join(missing)


def test_openapi_has_substantial_coverage(client):
    spec = __import__('openapi.spec', fromlist=['build_openapi_spec']).build_openapi_spec()
    assert len(spec['paths']) >= 40
