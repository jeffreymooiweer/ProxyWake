# Upgrading

How to move to a newer ProxyWake version without losing anything.

## Before you upgrade

1. **Make a backup.** Either copy the data folder (`/app/backend/data` in the container, `/mnt/user/appdata/proxywake` on Unraid), or download a full backup:
   - in the UI: **Settings → Full backup**, or
   - with the API: `curl -H "X-API-Key: $KEY" http://192.168.1.10:5001/api/backup -o proxywake-backup.json`
2. Note the environment variables you set (`PROXYWAKE_PASSWORD`, `TZ`, and `PROXYWAKE_SECRET_KEY` if you set one).

## Upgrade

Docker Compose:

```bash
docker compose pull
docker compose up -d
```

Plain Docker: stop and remove the old container, then run the same `docker run` command again with the **same volume** and environment variables. Unraid: click the container's **Update** button.

The database is upgraded automatically on first start; you do not need to do anything. Check **Logs** if the container does not come up.

## Verify

```bash
curl -s http://192.168.1.10:5001/api/health
```

The `version` field should show the new version.

## Pinning a version

If you prefer not to follow `latest`, use a version tag:

```yaml
image: jeffersonmouze/proxywake:4.3.0
```

`4.3` follows all 4.3.x patch releases; `4.3.0` never changes.

## Downgrading

Not supported. Restore a backup taken on the older version if you need to go back.

## Notes for specific versions

- **4.4.0** — no configuration changes. Wake-on-LAN now also works from a macvlan/ipvlan network (Unraid *Custom: br0*); see [Docker → Networking](docker.md#networking-and-wake-on-lan). Contributors: the frontend build moved to Vite and needs Node 22.
- **4.3.0** — new devices wake with broadcast on by default; existing devices keep their setting. Scheduled wakes now use the `TZ` environment variable; set it if your schedules should run in local time.
- **4.2.4** — the secret key is now generated once and stored in the data folder. If you saved SSH/IPMI passwords on 4.2.3 or older *without* setting `PROXYWAKE_SECRET_KEY`, enter them again once.
- **3.x → 4.x** — take a full backup first. 3.x images are no longer supported.

## Common mistakes

- Upgrading without a backup.
- Changing `PROXYWAKE_SECRET_KEY` during the upgrade — stored SSH/IPMI passwords become unreadable.
- Forgetting the volume: starting a new container without `-v proxywake_data:/app/backend/data` gives you an empty ProxyWake.

## See also

- [Docker](docker.md) · [Configuration](configuration.md) · [Changelog](../CHANGELOG.md)
