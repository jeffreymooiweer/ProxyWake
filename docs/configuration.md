# Configuration

Environment variables and application settings for ProxyWake.

## Purpose

Reference for all supported configuration options when deploying ProxyWake.

## Requirements

- Access to container or process environment (Docker, Compose, or shell)
- Persistent volume for `PROXYWAKE_DATA_DIR` in production

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROXYWAKE_PASSWORD` | Recommended | — | Web UI login password. Set before first use in production. |
| `PROXYWAKE_API_KEY` | No | Auto-generated | Fixed API key for reverse-proxy wake requests. Scopes configurable in Settings. |
| `PROXYWAKE_SECRET_KEY` | No | Random per start | Flask session secret and credential encryption key. Set a fixed value for stable sessions across restarts. |
| `PROXYWAKE_ALLOWED_ORIGINS` | No | `*` | Comma-separated CORS origins for browser API access. |
| `PROXYWAKE_SESSION_COOKIE_SECURE` | No | `false` | Set to `true` when ProxyWake is served only over HTTPS (session cookies require TLS). |
| `PROXYWAKE_DATA_DIR` | No | `/app/backend/data` | SQLite database, logs, API keys, and backups. |

### Example `.env`

```bash
PROXYWAKE_PASSWORD=ChangeMeNow
PROXYWAKE_PORT=8462
# PROXYWAKE_API_KEY=
# PROXYWAKE_SECRET_KEY=
# PROXYWAKE_ALLOWED_ORIGINS=https://proxywake.example.com
```

Copy from [`.env.example`](../.env.example) at the repository root or [`docker/.env.example`](../docker/.env.example).

## Settings (Web UI)

Configurable under **Settings**:

- Theme and language (15 locales)
- API key rotation and scopes (`read`, `write`, `wake`, `admin`)
- Wake cooldown, verification, and adaptive timeout
- Slack / Telegram notifications
- Log level and log viewer
- Full backup and restore

## API key scopes

| Scope | Typical use |
|-------|-------------|
| `read` | List devices, logs, statistics |
| `write` | Create/update devices and groups |
| `wake` | Trigger wake (including NPM background requests) |
| `admin` | Backup/restore, destructive operations |

NPM integration typically needs at least `wake`. Restrict scopes in Settings for least privilege.

## HTTPS and sessions

When ProxyWake is served behind HTTPS (recommended), ensure your reverse proxy forwards `X-Forwarded-Proto: https`. Session cookies use secure defaults appropriate to the deployment; place the management UI behind HTTPS in untrusted networks.

## Examples

**Docker Compose with custom data path:**

```yaml
volumes:
  - /mnt/user/appdata/proxywake:/app/backend/data
```

**Fixed API key for NPM:**

```bash
-e PROXYWAKE_API_KEY=your-long-random-key
```

## Common mistakes

- Omitting `PROXYWAKE_PASSWORD` on an internet-exposed instance.
- Rotating `PROXYWAKE_SECRET_KEY` without understanding that encrypted device credentials become unreadable.
- Setting CORS too narrowly and breaking the UI when accessed from a different origin.

## Related pages

- [Docker](docker.md)
- [Security](security.md)
- [API](api.md)
- [Quick Start](quick-start.md)
