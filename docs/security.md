# Security

What ProxyWake protects, what it exposes, and how to keep it safe.

## The basics

- **Set a password.** Without one, anyone on your network who finds the UI can wake, add and delete devices. Set `PROXYWAKE_PASSWORD` or use the setup wizard.
- **Keep the UI on your LAN.** ProxyWake is a management tool; there is rarely a reason to expose it to the internet. If you must, put it behind HTTPS with authentication on your proxy and set `PROXYWAKE_SESSION_COOKIE_SECURE=true`.
- **Treat the API key like a password.** It ends up in your proxy configuration; keep that file private. Rotate the key under **Settings** if it may have leaked.
- **Limit the key's scopes.** A reverse proxy only needs `wake`. See [Configuration](configuration.md#api-key-scopes).

## What is reachable without logging in

These endpoints are intentionally public so that proxies and waiting pages work without credentials. They are rate limited and expose no secrets.

| Endpoint | What it reveals |
|----------|-----------------|
| `GET /api/health` | Version number |
| `GET /api/metrics` | Counters (number of devices, number of wakes) |
| `GET /api/public/status/<domain>` | Whether a *registered* domain is online |
| `POST /api/public/wake/<domain>` | Wakes a registered domain (max 30 requests per minute per IP) |

If your ProxyWake is reachable from an untrusted network, be aware that anyone who knows a registered domain can wake that device.

## How secrets are stored

| Secret | Where | Protection |
|--------|-------|------------|
| Login password | data folder, `password.hash` | bcrypt hash — the password itself is never stored |
| API key | data folder, `api_keys.json` | file readable only by the container user |
| Secret key | data folder, `secret.key` | generated on first start, readable only by the container user |
| SSH / IPMI passwords, SSH keys | database | encrypted with the secret key; never returned by the API |
| Webhook URLs | database | stored as entered; shown masked in the UI if they contain a token |

Everything is inside `PROXYWAKE_DATA_DIR`. Protect that folder (and your backups — a full backup contains the encrypted credentials and all settings).

If you set your own `PROXYWAKE_SECRET_KEY`, keep it the same forever: changing it makes stored SSH/IPMI passwords unreadable.

## Brute-force protection

Login attempts are limited to 10 per minute per IP, and API calls with an invalid key to 60 per minute. Requests with a valid key are not limited.

## HTTPS

Put ProxyWake behind your reverse proxy with a certificate if you want HTTPS. Make sure the proxy forwards `X-Forwarded-Proto: https`, and set `PROXYWAKE_SESSION_COOKIE_SECURE=true` once the UI is only opened over HTTPS.

## Reporting a vulnerability

Please report security issues privately as described in [SECURITY.md](../SECURITY.md).

## See also

- [Configuration](configuration.md) · [Troubleshooting](troubleshooting.md)
