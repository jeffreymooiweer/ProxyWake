# API Reference

ProxyWake has a REST API under `/api/`. Everything the web UI does, you can do with the API — useful for scripts, Home Assistant, or your own tooling.

## Interactive documentation

While ProxyWake is running:

| Resource | URL |
|----------|-----|
| Swagger UI (try requests in the browser) | `http://<proxywake>/api/docs` |
| OpenAPI specification (JSON) | `http://<proxywake>/api/openapi.json` |

## Authentication

| Method | How |
|--------|-----|
| Session cookie | Log in with `POST /api/auth/login` and reuse the cookie (what the web UI does) |
| API key in a header | `X-API-Key: <key>` or `Authorization: Bearer <key>` |
| API key in the URL | `?api_key=<key>` — for tools that cannot set headers, such as Traefik's forwardAuth |

Find or rotate the key under **Settings**. Keys can be limited with scopes (`read`, `write`, `wake`, `admin`); see [Configuration](configuration.md#api-key-scopes).

## Endpoints you will use most

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check and version (no auth) |
| `/api/devices` | GET | List devices; add `?status=true` for online/offline |
| `/api/devices/<id>/wake` | POST | Wake a device. `?verify=true` returns a job you can poll for progress; `?force=true` ignores online check and cooldown |
| `/api/wake/jobs/<job_id>` | GET | Progress of a verified wake |
| `/api/wake/by-host` | GET/POST | Wake the device behind a hostname (`X-Forwarded-Host`, `Host` or `?host=`) — what reverse proxies call |
| `/api/groups/<id>/wake` | POST | Wake every device in a group |
| `/api/public/status/<domain>` | GET | Online/offline for a domain (no auth, rate limited) |
| `/api/public/wake/<domain>` | POST | Wake by domain and wait until online; `?wait=false` returns immediately (no auth, rate limited) |
| `/api/backup` | GET | Full backup as JSON (`admin` scope) |
| `/api/backup/restore` | POST | Restore a backup (`admin` scope) |
| `/api/metrics` | GET | Prometheus-style counters (no auth) |

The complete list, with request and response formats, is in `/api/docs`.

## Examples

Health check:

```bash
curl -s http://192.168.1.10:5001/api/health
```

Wake device 1 with an API key:

```bash
curl -X POST -H "X-API-Key: $KEY" http://192.168.1.10:5001/api/devices/1/wake
```

Wake and follow the progress:

```bash
JOB=$(curl -s -X POST -H "X-API-Key: $KEY" "http://192.168.1.10:5001/api/devices/1/wake?verify=true" | jq -r .job_id)
curl -s -H "X-API-Key: $KEY" http://192.168.1.10:5001/api/wake/jobs/$JOB
```

Download a backup:

```bash
curl -H "X-API-Key: $KEY" http://192.168.1.10:5001/api/backup -o proxywake-backup.json
```

## Rate limits

To stop abuse, some endpoints are limited per client IP: login (10/min), manual wake (30/min), public wake (30/min), public status (120/min), network scan (5/min). `/api/wake/by-host` limits only calls with an **invalid** key (60/min); calls with a valid key are unlimited because reverse proxies route every request through it.

## See also

- [Configuration](configuration.md) · [Security](security.md) · [Migration](migration.md)
