# Quick Start

Get ProxyWake running and wake your first device.

## 1. Run ProxyWake

```bash
docker run -d \
  --name proxywake \
  --restart unless-stopped \
  --cap-add NET_RAW \
  -p 8462:5001 \
  -e PROXYWAKE_PASSWORD=YourSecurePassword \
  -v proxywake_data:/app/backend/data \
  jeffersonmouze/proxywake:latest
```

Open `http://<server-ip>:8462` and complete the setup wizard.

**Docker Compose:** see [Docker](docker.md).

**Requirements:** Docker, Wake-on-LAN enabled on the target device, and `NET_RAW` for magic packets.

## 2. Add a device

1. Go to **Devices** → **Add device**.
2. Enter name, domain (as used in your reverse proxy), IP address, and MAC address.
3. Save.

| Field | Example |
|-------|---------|
| Name | NAS |
| Domain | `nas.home.lab` |
| IP | `192.168.1.50` |
| MAC | `AA:BB:CC:DD:EE:01` |

## 3. Configure your reverse proxy

1. Open the **Integration** tab.
2. Copy the **global** and **per-host** snippets for your proxy.
3. Set the ProxyWake URL to an address your proxy can reach — usually `http://<host-lan-ip>:8462`.

Guides: [Reverse Proxy](reverse-proxy.md) · [Nginx Proxy Manager](examples/nginx-proxy-manager.md)

## 4. Test

1. Power off or suspend the target device.
2. Visit the proxied domain in a browser.
3. Confirm the waiting page appears and the device wakes.

Use **Integration → Test NPM wake** for a quick sanity check.

## Common mistakes

- Using `localhost` in NPM — the NPM container cannot reach the host via `localhost`.
- Forgetting `--cap-add NET_RAW` — WOL may fail silently.
- Wrong MAC address (Wi-Fi vs Ethernet).
- Domain mismatch — the domain in ProxyWake must match the proxy hostname exactly.

## See also

- [Docker](docker.md)
- [Configuration](configuration.md)
- [Troubleshooting](troubleshooting.md)
