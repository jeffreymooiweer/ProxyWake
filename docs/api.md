# API Reference

ProxyWake exposes a REST API under `/api/*` with OpenAPI documentation.

## Purpose

Describe authentication, scopes, and how to explore the full API surface.

## Requirements

- Running ProxyWake instance
- API key and/or session cookie for protected routes

## Interactive documentation

When ProxyWake is running:

| Resource | URL |
|----------|-----|
| Swagger UI | `/api/docs` |
| OpenAPI JSON | `/api/openapi.json` |

The OpenAPI spec version matches `backend/version.py` (currently **4.2.1**).

## Authentication

| Method | Header / mechanism |
|--------|-------------------|
| Session | Cookie after `POST /api/auth/login` |
| API key | `X-API-Key: <key>` |

API keys support scopes: `read`, `write`, `wake`, `admin`. Configure in **Settings**.

## Public endpoints

These do not require authentication (see [Security](security.md)):

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check and version |
| `/api/metrics` | GET | Prometheus-style metrics |
| `/api/public/status/<domain>` | GET | Waiting page status |
| `/api/public/wake/<domain>` | POST | Waiting page wake trigger |

Public wake/status routes are rate limited.

## Common API workflows

**List devices (API key):**

```bash
curl -s -H "X-API-Key: $KEY" http://localhost:8462/api/devices | jq
```

**Wake a device:**

```bash
curl -s -X POST -H "X-API-Key: $KEY" \
  http://localhost:8462/api/devices/1/wake
```

**Backup (admin scope):**

```bash
curl -s -H "X-API-Key: $KEY" http://localhost:8462/api/backup -o backup.json
```

## Examples

NPM background wake (simplified — use UI-generated snippet):

```nginx
location = /proxywake-wake {
    internal;
    proxy_pass http://192.168.1.10:8462/api/public/wake/$host;
    proxy_set_header X-API-Key "your-api-key";
}
```

## Common mistakes

- Using session-only endpoints from NPM without an API key.
- Missing `admin` scope for backup/restore.
- Assuming passwords or credential secrets appear in API responses — they do not.

## Related pages

- [Configuration](configuration.md) — API key env vars
- [Security](security.md)
- [Development](development.md) — running tests including OpenAPI parity
