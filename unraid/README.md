# ProxyWake Unraid template

The Community Applications template for installing ProxyWake on Unraid.

## What is in this folder

- `proxywake.xml` — the container template used by the Community Applications plugin
- `icons/proxywake.png` — the icon shown in the Apps tab

ProxyWake wakes sleeping devices on your LAN when they are accessed through a reverse proxy (Nginx Proxy Manager, Traefik, Caddy and similar).

## Installing through Community Applications

1. Open **Apps** in the Unraid web UI.
2. Search for **ProxyWake** and click **Install**.
3. Set **Timezone** (e.g. `Europe/Amsterdam`) and, optionally, a **Password**. Leave the password empty to set it in the first-run setup wizard.
4. Keep **Appdata** at `/mnt/user/appdata/proxywake`.
5. Click **Apply** and open the web UI at `http://<unraid-ip>:5001`.

The template uses **host networking**. This is required: Wake-on-LAN magic packets are LAN broadcasts and never leave Docker's private bridge network. It also adds `--cap-add=NET_RAW` so ProxyWake can ping devices to check whether they are online.

## Testing the template before it is published

```bash
mkdir -p /boot/config/plugins/community.applications/private/proxywake
cp unraid/proxywake.xml /boot/config/plugins/community.applications/private/proxywake/proxywake.xml
```

Then open **Apps → Private Apps** and install **ProxyWake** from there. Private templates are read from the USB boot drive; update the XML there when you change it.

## Template settings

| Setting | Value |
|---------|-------|
| **Repository** | `jeffersonmouze/proxywake:latest` |
| **Network Type** | Host (web UI on port `5001`) |
| **Appdata** | `/mnt/user/appdata/proxywake` → `/app/backend/data` |
| **Timezone** (`TZ`) | Your timezone, for scheduled wakes |
| **Password** (`PROXYWAKE_PASSWORD`) | Optional; the setup wizard asks otherwise |
| **Extra Parameters** | `--cap-add=NET_RAW` (included) |

Advanced (normally left empty):

| Setting | When to use |
|---------|-------------|
| `PROXYWAKE_SECRET_KEY` | ProxyWake generates and stores one itself. Set your own only if you want to control it, e.g. to restore a backup on another machine. |
| `PROXYWAKE_ALLOWED_ORIGINS` | When the UI is served from a public hostname through a reverse proxy, e.g. `https://proxywake.example.com` |
| `PROXYWAKE_SESSION_COOKIE_SECURE` | `true` only when the UI is opened over HTTPS |

The log level is set in the ProxyWake UI under **Settings**, not through a variable.

## Nginx Proxy Manager on Unraid

Under **Integration** in ProxyWake, set the ProxyWake URL to the address NPM can reach:

```
http://<unraid-ip>:5001
```

Use the Unraid LAN IP, not `localhost` (from inside the NPM container that is NPM itself). Then follow [docs/examples/nginx-proxy-manager.md](../docs/examples/nginx-proxy-manager.md).

## Troubleshooting

| Problem | Check |
|---------|-------|
| Nothing wakes | Network Type must be **Host**; then verify the MAC address. See [docs/troubleshooting.md](../docs/troubleshooting.md#wake-does-not-work) |
| Devices always shown offline | Extra Parameters must include `--cap-add=NET_RAW`, or switch the device's status check to TCP/HTTP |
| NPM cannot reach ProxyWake | Use the Unraid IP and port 5001, not `localhost` |
| `unable to open database file` | Fixed automatically since 4.2.3; on older images run `chown -R 1000:1000 /mnt/user/appdata/proxywake` |
| Schedules fire at the wrong time | Set the **Timezone** variable |

## Links

| Resource | URL |
|----------|-----|
| Project | https://github.com/jeffreymooiweer/ProxyWake |
| Docker Hub | https://hub.docker.com/r/jeffersonmouze/proxywake |
| Issues | https://github.com/jeffreymooiweer/ProxyWake/issues |
| Template XML | https://raw.githubusercontent.com/jeffreymooiweer/ProxyWake/main/unraid/proxywake.xml |
| Full Unraid guide | [docs/unraid.md](../docs/unraid.md) |
