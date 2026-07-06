# Unraid

Install ProxyWake on Unraid via the Community Applications template or manual Docker setup.

## Community Applications (recommended)

ProxyWake ships an official template in [unraid/proxywake.xml](../unraid/proxywake.xml). Step-by-step guide: [unraid/README.md](../unraid/README.md).

1. Open **Apps** and install **ProxyWake** (or **Private Apps** while testing — see below).
2. Set `PROXYWAKE_SECRET_KEY` to a long random string.
3. Confirm appdata maps `/mnt/user/appdata/proxywake` → `/app/backend/data`.
4. Start the container and open the WebUI.

| Item | Value |
|------|-------|
| Image | `jeffersonmouze/proxywake:latest` |
| WebUI port | Container `5001` (template default host port `5001`) |
| Appdata | `/mnt/user/appdata/proxywake` → `/app/backend/data` |
| WOL | `--cap-add=NET_RAW` (included in template) |

**Test as a private app** (before CA publication):

```bash
mkdir -p /boot/config/plugins/community.applications/private/proxywake
cp unraid/proxywake.xml /boot/config/plugins/community.applications/private/proxywake/proxywake.xml
```

Then open **Apps → Private Apps**.

## Manual Docker setup

1. Open **Docker** in the Unraid web UI.
2. Add container from `jeffersonmouze/proxywake` (`:latest` or a pinned tag).
3. Use these settings:

| Setting | Value |
|---------|-------|
| **Network** | Bridge |
| **Port** | `8462:5001` (or `5001:5001`) |
| **Extra Parameters** | `--cap-add=NET_RAW` |
| **Variable** | `PROXYWAKE_SECRET_KEY` = long random string |
| **Variable** | `PROXYWAKE_PASSWORD` = password (optional — setup wizard if empty) |
| **Path** | `/mnt/user/appdata/proxywake` → `/app/backend/data` |

4. Start and open `http://<unraid-ip>:<host-port>`.
5. Configure your reverse proxy via the **Integration** tab.

## NPM on Unraid

Set the ProxyWake URL in Integration to an address NPM can reach:

```
http://<unraid-lan-ip>:<host-port>
```

Usually `http://<unraid-ip>:5001` with the CA template, or `:8462` with manual setup. Do not use `localhost` from inside the NPM container.

## Common mistakes

- Omitting `--cap-add=NET_RAW`.
- Mapping appdata to `/app/data` instead of `/app/backend/data`.
- Using `localhost` from the NPM container.
- Forgetting to back up `/mnt/user/appdata/proxywake`.

## See also

- [Unraid template README](../unraid/README.md)
- [Nginx Proxy Manager](examples/nginx-proxy-manager.md)
- [Configuration](configuration.md)
- [Docker](docker.md)
