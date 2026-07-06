# Unraid

Deploy ProxyWake on Unraid using Docker.

## Purpose

Run ProxyWake as an Unraid Docker container with persistent appdata and Wake-on-LAN support.

## Requirements

- Unraid 6.x with Docker enabled
- Available host port (default `8462`)
- Device on the same LAN as Unraid with WOL enabled

## Step-by-step

1. Open **Docker** in the Unraid web UI.
2. Search for `jeffersonmouze/proxywake` or add a custom template.
3. Configure the container:

| Setting | Value |
|---------|-------|
| **Repository** | `jeffersonmouze/proxywake:latest` |
| **Network Type** | Bridge (default) |
| **Port** | `8462:5001` |
| **Extra Parameters** | `--cap-add=NET_RAW` |
| **Variable** | `PROXYWAKE_PASSWORD` = your secure password |
| **Path** | `/mnt/user/appdata/proxywake` → `/app/backend/data` |

4. Apply and start the container.
5. Open `http://<unraid-ip>:8462` and complete setup.
6. Configure NPM or another reverse proxy using the **Integration** tab.

## Examples

**Optional fixed API key:**

| Variable | Value |
|----------|-------|
| `PROXYWAKE_API_KEY` | Long random string (match in NPM config) |

**Reachability from NPM on Unraid:**

Use the Unraid host IP (e.g. `192.168.1.10:8462`) in Integration → ProxyWake URL, not `localhost`.

## Common mistakes

- Omitting `--cap-add=NET_RAW` in Extra Parameters.
- Storing data on the cache pool without backup — include `appdata/proxywake` in backups.
- Using `localhost` from NPM container — use the host IP.

## Related pages

- [Docker](docker.md)
- [Nginx Proxy Manager](examples/nginx-proxy-manager.md)
- [Configuration](configuration.md)
