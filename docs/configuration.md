# Configuration

Environment variables and application settings.

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROXYWAKE_PASSWORD` | Recommended | — | Web UI login password |
| `PROXYWAKE_API_KEY` | No | Auto-generated | API key for reverse-proxy wake requests |
| `PROXYWAKE_SECRET_KEY` | No | Random per start | Session secret and credential encryption — set a fixed value for stable sessions |
| `PROXYWAKE_ALLOWED_ORIGINS` | No | `*` | Comma-separated CORS origins |
| `PROXYWAKE_SESSION_COOKIE_SECURE` | No | `false` | Set `true` when the UI is HTTPS-only |
| `PROXYWAKE_DATA_DIR` | No | `/app/backend/data` | Database, logs, and settings |

### Example `.env`

```bash
PROXYWAKE_PASSWORD=ChangeMeNow
PROXYWAKE_PORT=8462
# PROXYWAKE_API_KEY=
# PROXYWAKE_SECRET_KEY=
# PROXYWAKE_ALLOWED_ORIGINS=https://proxywake.example.com
```

Copy from [`.env.example`](../.env.example) at the repository root.

## Settings (Web UI)

Under **Settings** you can configure theme, language, API key scopes, wake cooldown, notifications, log level, and backup/restore.

## API key scopes

| Scope | Use |
|-------|-----|
| `read` | List devices, logs, statistics |
| `write` | Create/update devices and groups |
| `wake` | Trigger wake (NPM background requests) |
| `admin` | Backup/restore and destructive operations |

NPM integration typically needs `wake` only.

## Common mistakes

- Exposing the UI without `PROXYWAKE_PASSWORD`.
- Changing `PROXYWAKE_SECRET_KEY` after saving encrypted SSH/IPMI credentials.
- Setting CORS too narrowly and breaking the UI.

## See also

- [Docker](docker.md)
- [Security](security.md)
- [API](api.md)
