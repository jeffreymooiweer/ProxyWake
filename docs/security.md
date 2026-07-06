# Security

Security practices for self-hosted ProxyWake.

## Basics

- Set **`PROXYWAKE_PASSWORD`** before exposing the UI.
- Rotate the API key via **Settings** when needed.
- Use **scoped API keys** — NPM typically needs only `wake`.
- Do not expose the management UI to the internet without HTTPS.

## Public endpoints

These are intentionally unauthenticated (rate limited where noted):

| Endpoint | Notes |
|----------|-------|
| `GET /api/health` | No sensitive data |
| `GET /api/metrics` | Aggregate counters only |
| `GET /api/public/status/<domain>` | Domain must exist |
| `POST /api/public/wake/<domain>` | 30 requests/minute per IP |

Review these on untrusted networks.

## Secrets

- API keys and password hashes live in `PROXYWAKE_DATA_DIR`.
- Device credentials (SSH, IPMI, webhooks) are encrypted with `PROXYWAKE_SECRET_KEY`.
- Passwords and secrets are never returned by the API.

Set a fixed `PROXYWAKE_SECRET_KEY` in production so sessions and encrypted credentials survive restarts.

## HTTPS

When ProxyWake is behind HTTPS, ensure your reverse proxy forwards `X-Forwarded-Proto: https` and set `PROXYWAKE_SESSION_COOKIE_SECURE=true` if the UI is HTTPS-only.

## Reporting vulnerabilities

See [SECURITY.md](../SECURITY.md) for private vulnerability reporting.

## See also

- [Configuration](configuration.md)
- [Troubleshooting](troubleshooting.md)
