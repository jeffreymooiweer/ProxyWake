# Quick Start

Get ProxyWake running and wake your first device.

## Purpose

Install ProxyWake, register a device, and trigger Wake-on-LAN when a reverse proxy receives traffic for that domain.

## Requirements

- Docker (recommended) or Python 3.11+ and Node.js 20+
- A device with Wake-on-LAN enabled (BIOS + NIC)
- Network access from the ProxyWake container to the target subnet
- `NET_RAW` capability when using Docker (for magic packets)

## Step-by-step

### 1. Run ProxyWake

```bash
docker run -d \
  --name proxywake \
  --restart unless-stopped \
  --cap-add NET_RAW \
  -p 8462:5001 \
  -e PROXYWAKE_PASSWORD=YourSecurePassword \
  -v proxywake_data:/app/backend/data \
  jeffersonmouze/proxywake:4.2.2
```

Use `:latest` for the newest build on Docker Hub, or pin `:4.2` for the current minor line.

Open `http://<server-ip>:8462` and complete the setup wizard.

### 2. Add a device

1. Go to **Devices** → **Add device**.
2. Enter a friendly name, domain (as used in your reverse proxy), IP address, and MAC address.
3. Save the device.

### 3. Configure your reverse proxy

1. Open the **Integration** tab.
2. Copy the **global NPM config** and **per-host snippet** (or Traefik/Caddy equivalent).
3. Ensure ProxyWake is reachable from your proxy container using the **host LAN IP**, not `localhost`.

See [Reverse Proxy](reverse-proxy.md) and [Nginx Proxy Manager](examples/nginx-proxy-manager.md).

### 4. Test

1. Shut down or suspend the target device.
2. Visit the proxied domain in a browser.
3. Confirm the waiting page appears and the device wakes.

Use **Integration → Test NPM wake** in the UI for a quick sanity check.

## Examples

**Minimal device:**

| Field | Example |
|-------|---------|
| Name | NAS |
| Domain | `nas.home.lab` |
| IP | `192.168.1.50` |
| MAC | `AA:BB:CC:DD:EE:01` |

**Docker Compose:**

```bash
curl -O https://raw.githubusercontent.com/jeffreymooiweer/ProxyWake/main/docker-compose.yml
PROXYWAKE_PASSWORD=YourSecurePassword docker compose up -d
```

## Common mistakes

- Using `localhost` in NPM instead of the Docker host IP — the NPM container cannot reach the host via `localhost`.
- Forgetting `--cap-add NET_RAW` — WOL magic packets may fail silently.
- Wrong MAC address (Wi-Fi vs Ethernet) — wake packets must target the interface that supports WOL.
- Domain mismatch — the domain in ProxyWake must match the proxy host name exactly.

## Related pages

- [Docker](docker.md)
- [Configuration](configuration.md)
- [Reverse Proxy](reverse-proxy.md)
- [Troubleshooting](troubleshooting.md)
