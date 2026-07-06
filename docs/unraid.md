# Unraid

Run ProxyWake on Unraid with persistent appdata and Wake-on-LAN support.

## Container settings

1. Open **Docker** in the Unraid web UI.
2. Add container from `jeffersonmouze/proxywake` (`:latest` or a pinned tag such as `:4.2.2`).
3. Use these settings:

| Setting | Value |
|---------|-------|
| **Network** | Bridge |
| **Port** | `8462:5001` |
| **Extra Parameters** | `--cap-add=NET_RAW` |
| **Variable** | `PROXYWAKE_PASSWORD` = your password (optional — setup wizard if empty) |
| **Variable** | `PROXYWAKE_SECRET_KEY` = long random string (recommended) |
| **Path** | `/mnt/user/appdata/proxywake` → `/app/backend/data` |

4. Start the container and open `http://<unraid-ip>:8462`.
5. Configure your reverse proxy via the **Integration** tab.

## NPM on Unraid

In Integration, set the ProxyWake URL to something NPM can reach — usually:

```
http://<unraid-lan-ip>:8462
```

Do not use `localhost` from inside the NPM container.

## Common mistakes

- Omitting `--cap-add=NET_RAW`.
- Mapping appdata to `/app/data` instead of `/app/backend/data`.
- Forgetting to back up `/mnt/user/appdata/proxywake`.

## See also

- [Nginx Proxy Manager](examples/nginx-proxy-manager.md)
- [Configuration](configuration.md)
- [Docker](docker.md)
