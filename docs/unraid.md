# Unraid

Deploy ProxyWake on Unraid using the official Community Applications template or manual Docker setup.

## Community Applications template

ProxyWake ships an Unraid template in the repository:

- Template: [../unraid/proxywake.xml](../unraid/proxywake.xml)
- Installation guide: [../unraid/README.md](../unraid/README.md)

| Item | Value |
|------|-------|
| **Docker image** | `jeffersonmouze/proxywake:latest` |
| **WebUI port** | Container `5001` (template default host port `5001`) |
| **Appdata** | `/mnt/user/appdata/proxywake` → `/app/backend/data` |
| **Secret key** | `PROXYWAKE_SECRET_KEY` (required in template) |
| **WOL capability** | `--cap-add=NET_RAW` (set in template `ExtraParams`) |

### Private template testing

Before CA publication, install as a private app:

```bash
mkdir -p /boot/config/plugins/community.applications/private/proxywake
cp unraid/proxywake.xml /boot/config/plugins/community.applications/private/proxywake/proxywake.xml
```

Then open **Apps → Private Apps** and install ProxyWake.

### Community Applications submission

To list ProxyWake in the public CA catalog:

1. Verify the template with `python3 scripts/validate_unraid_template.py`.
2. Test via **Private Apps** on a real Unraid server.
3. Confirm the icon loads from `raw.githubusercontent.com`.
4. Confirm the **WebUI** button opens `http://<host>:<port>`.
5. Follow the [Unraid CA submission process](https://forums.unraid.net/topic/38582-plug-in-community-applications/) and point maintainers to the raw template URL:

   `https://raw.githubusercontent.com/jeffreymooiweer/ProxyWake/main/unraid/proxywake.xml`

## Manual Docker setup

If you prefer adding the container without the template:

1. Open **Docker** in the Unraid web UI.
2. Search for `jeffersonmouze/proxywake` or add a custom template.
3. Configure the container:

| Setting | Value |
|---------|-------|
| **Repository** | `jeffersonmouze/proxywake:latest` (or a pinned tag such as `4.2.2`) |
| **Network Type** | Bridge (default) |
| **Port** | `8462:5001` (or `5001:5001`) |
| **Extra Parameters** | `--cap-add=NET_RAW` |
| **Variable** | `PROXYWAKE_SECRET_KEY` = long random string |
| **Variable** | `PROXYWAKE_PASSWORD` = your secure password (optional; setup wizard if empty) |
| **Path** | `/mnt/user/appdata/proxywake` → `/app/backend/data` |

4. Apply and start the container.
5. Open `http://<unraid-ip>:<host-port>` and complete setup.
6. Configure NPM or another reverse proxy using the **Integration** tab.

## Reverse proxy notes

- Set `PROXYWAKE_ALLOWED_ORIGINS` when using a public hostname.
- Set `PROXYWAKE_SESSION_COOKIE_SECURE=true` when the UI is only served over HTTPS.
- In NPM Integration, use `http://<unraid-ip>:<host-port>` — the address NPM can reach, not NPM's own address.
- If NPM and ProxyWake share a Docker network, container DNS may work when configured.

See [examples/nginx-proxy-manager.md](examples/nginx-proxy-manager.md) for NPM-specific steps.

## Common mistakes

- Omitting `--cap-add=NET_RAW` in Extra Parameters.
- Mapping appdata to `/app/data` instead of `/app/backend/data`.
- Storing data on the cache pool without backup — include `appdata/proxywake` in backups.
- Using `localhost` from NPM container — use the host IP or shared Docker network DNS.

## Related pages

- [Unraid template README](../unraid/README.md)
- [Docker](docker.md)
- [Nginx Proxy Manager](examples/nginx-proxy-manager.md)
- [Configuration](configuration.md)
