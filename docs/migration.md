# Migration

Upgrading ProxyWake between versions.

## Purpose

Safe upgrade paths, schema versions, and backup strategy.

## Requirements

- Backup of `PROXYWAKE_DATA_DIR` before any upgrade
- Compatible Docker image tag or git branch

## Step-by-step

### 1. Backup

**Via UI:** Settings → Backup → Download.

**Via API:**

```bash
curl -H "X-API-Key: $KEY" http://host:8462/api/backup -o proxywake-backup.json
```

**Via volume:** Copy the entire data directory.

### 2. Upgrade image

```bash
docker pull jeffersonmouze/proxywake:4.2
docker stop proxywake && docker rm proxywake
# Re-run with same volume and env vars
```

Or with Compose:

```bash
docker compose pull && docker compose up -d
```

### 3. Verify

```bash
curl -s http://localhost:8462/api/health | jq .version
```

Check **Logs** for migration messages on first start.

## Schema versions

Internal schema version is managed by `migration_service.py` (independent of app semver):

| App version | Schema |
|-------------|--------|
| 4.1.x+ | `4.1` |
| 4.0.x | `4.0` |

Backup format version (`BACKUP_VERSION`) is `4.0` — restores remain compatible across 4.x.

## Version 3.x → 4.x

- Modular backend and new settings keys — backup/restore recommended.
- Review [CHANGELOG](../CHANGELOG.md) for Golf A–E features.
- Docker tags `3.x` are no longer supported ([SECURITY.md](../SECURITY.md)).

## Downgrades

Not officially supported. Restore from a backup taken on the target version if needed.

## Examples

**Pin version:**

```yaml
image: jeffersonmouze/proxywake:4.2.2
```

## Common mistakes

- Upgrading without volume backup.
- Changing `PROXYWAKE_SECRET_KEY` during upgrade — breaks encrypted credentials.
- Expecting `latest` to roll back — tag is mutable; pin semver for production.

## Related pages

- [Docker](docker.md)
- [Configuration](configuration.md)
- [CHANGELOG](../CHANGELOG.md)
