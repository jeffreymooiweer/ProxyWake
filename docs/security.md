# Security

Security practices for self-hosted ProxyWake deployments.

## Purpose

Help operators deploy ProxyWake safely on home and small-office networks.

## Requirements

- Understanding of your network trust boundary
- HTTPS termination at your reverse proxy (recommended)

## Authentication

- Set **`PROXYWAKE_PASSWORD`** before exposing the UI.
- Rotate the API key periodically via **Settings**.
- Use **scoped API keys** — NPM typically needs only `wake`.
- Do not expose the management UI directly to the internet without HTTPS.

## Public endpoints

Intentionally unauthenticated (rate limited where noted):

| Endpoint | Risk mitigation |
|----------|-----------------|
| `GET /api/health` | No sensitive data |
| `GET /api/metrics` | Aggregate counters only |
| `GET /api/public/status/<domain>` | Domain must exist |
| `POST /api/public/wake/<domain>` | 30 requests/minute per IP |

Review these when deploying on untrusted networks. See [SECURITY.md](../SECURITY.md) for vulnerability reporting.

## Secrets and credentials

- API keys and password hashes live in `PROXYWAKE_DATA_DIR`.
- Device credentials (SSH, IPMI, webhooks) are **encrypted at rest** using `PROXYWAKE_SECRET_KEY`.
- Passwords and secrets are **never returned** by the API.
- Logs sanitize sensitive values — do not enable debug logging on shared systems without review.

## Network

- Docker requires `NET_RAW` for WOL — minimize container capabilities otherwise.
- Prefer Tailscale/WireGuard over Wake-on-WAN port forwarding.
- `POST /api/scan` requires authentication and is rate limited.

## CORS and headers

- Set `PROXYWAKE_ALLOWED_ORIGINS` when the UI is served from a specific origin.
- Place ProxyWake behind a reverse proxy that sets `X-Forwarded-Proto` for HTTPS.

## Backup and restore

- Backup files contain encrypted credentials — treat as sensitive.
- Restore requires compatible `PROXYWAKE_SECRET_KEY` for encrypted fields.

## Hardening checklist

- [ ] Strong `PROXYWAKE_PASSWORD`
- [ ] Fixed `PROXYWAKE_SECRET_KEY` in production
- [ ] Restricted API key scopes
- [ ] HTTPS via reverse proxy
- [ ] Management UI not publicly reachable
- [ ] Regular image updates (`latest` or pinned semver tag)
- [ ] Volume backups encrypted at rest (disk/OS level)

## Common mistakes

- Publishing port `8462` to the internet without authentication.
- Sharing API keys in screenshots or git repos.
- Changing `PROXYWAKE_SECRET_KEY` without re-entering device credentials.

## Related pages

- [Configuration](configuration.md)
- [API](api.md)
- [SECURITY.md](../SECURITY.md)
