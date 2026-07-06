# ProxyWake Unraid Template

Official Community Applications template files for installing ProxyWake on Unraid.

## What this is

This directory contains the Unraid **Community Applications** template for ProxyWake:

- `proxywake.xml` — container template used by the CA plugin
- `icons/proxywake.png` — template icon shown in the Apps UI

ProxyWake wakes sleeping devices on your LAN when traffic hits your reverse proxy (Nginx Proxy Manager, Traefik, Caddy, and similar).

## Installation through Community Applications

Once the template is published in Community Applications:

1. Open **Apps** in the Unraid web UI.
2. Search for **ProxyWake**.
3. Click **Install**.
4. Set **Secret Key** (`PROXYWAKE_SECRET_KEY`) to a long random value (at least 32 characters).
5. Optionally set **Password** (`PROXYWAKE_PASSWORD`) or leave it empty and use the first-run setup wizard.
6. Confirm **Appdata** maps `/mnt/user/appdata/proxywake` → `/app/backend/data`.
7. Apply and start the container.
8. Open the WebUI from the container link or `http://<unraid-ip>:5001` (or your chosen host port).

The template adds `--cap-add=NET_RAW` automatically — required for Wake-on-LAN ping.

## Manual / private template testing

Test the template before CA submission:

```bash
mkdir -p /boot/config/plugins/community.applications/private/proxywake
```

Copy this file from the repository:

`unraid/proxywake.xml`

to:

`/boot/config/plugins/community.applications/private/proxywake/proxywake.xml`

Then in Unraid:

1. Open **Apps**.
2. Go to **Private Apps**.
3. Install **ProxyWake**.

Private templates read from the USB boot path; update the XML there when you change the template locally.

## Required settings

| Setting | Value |
|---------|-------|
| **Repository** | `jeffersonmouze/proxywake:latest` |
| **WebUI port** | Container `5001` (map a host port, default `5001`) |
| **Appdata** | `/mnt/user/appdata/proxywake` → `/app/backend/data` |
| **Secret Key** | `PROXYWAKE_SECRET_KEY` — long random string |
| **Extra Parameters** | `--cap-add=NET_RAW` (included in template) |

## Recommended settings

| Setting | Notes |
|---------|-------|
| `PROXYWAKE_PASSWORD` | Set a strong password, or leave empty for the setup wizard on first visit |
| `PROXYWAKE_ALLOWED_ORIGINS` | Set when using a reverse proxy with a public hostname, e.g. `https://proxywake.example.com` |
| `PROXYWAKE_SESSION_COOKIE_SECURE` | `true` only when the UI is served over HTTPS |
| Backups | Include `/mnt/user/appdata/proxywake` in your Unraid backup routine |

Log level is configured in the ProxyWake UI under **Settings**, not via an environment variable.

## Reverse proxy notes

When ProxyWake sits behind Nginx Proxy Manager or another reverse proxy:

- Set `PROXYWAKE_ALLOWED_ORIGINS` to your public URL.
- Set `PROXYWAKE_SESSION_COOKIE_SECURE=true` when using HTTPS.
- Ensure the proxy can reach ProxyWake on the Unraid host (not `localhost` from inside another container unless they share a Docker network).

## Nginx Proxy Manager notes

In ProxyWake **Integration**, set the ProxyWake URL to an address NPM can reach:

```
http://UNRAID-IP:5001
```

Use your actual Unraid LAN IP and the **host** port you mapped (often `5001` with this template, or `8462` if you prefer that convention).

Important:

- Do **not** use NPM's own IP/port in the ProxyWake setup wizard.
- Use the address NPM uses to reach ProxyWake — usually `http://UNRAID-IP:5001`.
- If ProxyWake and NPM share a Docker custom network, you may use the container name/DNS instead when name resolution works.

## Troubleshooting

| Problem | Check |
|---------|-------|
| WOL / ping fails | Extra Parameters must include `--cap-add=NET_RAW` |
| NPM cannot reach ProxyWake | Use Unraid host IP, not `localhost` from NPM |
| Sessions reset after restart | Set a fixed `PROXYWAKE_SECRET_KEY` |
| Permission errors on appdata | Container runs as UID 1000; ensure appdata folder is writable |
| WebUI not loading | Confirm host port maps to container `5001` and the container is healthy |

## Links

| Resource | URL |
|----------|-----|
| Project | https://github.com/jeffreymooiweer/ProxyWake |
| Docker Hub | https://hub.docker.com/r/jeffersonmouze/proxywake |
| Issues | https://github.com/jeffreymooiweer/ProxyWake/issues |
| Template XML | https://raw.githubusercontent.com/jeffreymooiweer/ProxyWake/main/unraid/proxywake.xml |
| Full Unraid docs | [docs/unraid.md](../docs/unraid.md) |
