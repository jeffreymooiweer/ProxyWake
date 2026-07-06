# Migration

Upgrading ProxyWake between versions.

## Before you upgrade

1. **Back up** your data directory or use **Settings → Backup**.
2. Note your environment variables (`PROXYWAKE_PASSWORD`, `PROXYWAKE_SECRET_KEY`, etc.).

```bash
curl -H "X-API-Key: $KEY" http://host:8462/api/backup -o proxywake-backup.json
```

## Upgrade

```bash
docker pull jeffersonmouze/proxywake:latest
docker compose pull && docker compose up -d
```

Or stop, remove, and re-run `docker run` with the **same volume** and env vars.

## Verify

```bash
curl -s http://localhost:8462/api/health | jq .version
```

Check **Logs** for migration messages on first start.

## Pinning versions

For production, pin a semver tag instead of `latest`:

```yaml
image: jeffersonmouze/proxywake:4.2.2
```

## Downgrades

Not officially supported. Restore from a backup taken on the target version if needed.

## Major upgrades (3.x → 4.x)

Backup/restore is strongly recommended. Docker tags `3.x` are no longer supported — see [SECURITY.md](../SECURITY.md) and [CHANGELOG](../CHANGELOG.md).

## Common mistakes

- Upgrading without a backup.
- Changing `PROXYWAKE_SECRET_KEY` during upgrade — breaks encrypted credentials.

## See also

- [Docker](docker.md)
- [Configuration](configuration.md)
- [CHANGELOG](../CHANGELOG.md)
