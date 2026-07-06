# API Reference

ProxyWake exposes a REST API under `/api/*`.

## Interactive docs

When ProxyWake is running:

| Resource | URL |
|----------|-----|
| Swagger UI | `/api/docs` |
| OpenAPI JSON | `/api/openapi.json` |

## Authentication

| Method | Mechanism |
|--------|-----------|
| Session | Cookie after `POST /api/auth/login` |
| API key | `X-API-Key: <key>` |

API keys support scopes: `read`, `write`, `wake`, `admin`. Configure in **Settings**.

## Public endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check and version |
| `/api/metrics` | GET | Aggregate counters |
| `/api/public/status/<domain>` | GET | Device online status |
| `/api/public/wake/<domain>` | POST | Trigger wake (rate limited) |

See [Security](security.md) for exposure guidance.

## Common API tasks

**Health check:**

```bash
curl -s http://host:8462/api/health
```

**Wake with API key:**

```bash
curl -X POST -H "X-API-Key: $KEY" http://host:8462/api/wake/<device-id>
```

**Backup:**

```bash
curl -H "X-API-Key: $KEY" http://host:8462/api/backup -o proxywake-backup.json
```

For the full route list, use `/api/docs`.

## See also

- [Configuration](configuration.md)
- [Security](security.md)
- [Migration](migration.md)
