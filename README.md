# ProxyWake

<p align="center">
  <img src="docs/assets/banner.png" alt="ProxyWake — Access it. Wake it." width="900" />
</p>

<p align="center">
  <a href="https://hub.docker.com/r/jeffersonmouze/proxywake"><img src="https://img.shields.io/docker/pulls/jeffersonmouze/proxywake?style=flat-square&logo=docker" alt="Docker Pulls"></a>
  <a href="https://hub.docker.com/r/jeffersonmouze/proxywake"><img src="https://img.shields.io/docker/v/jeffersonmouze/proxywake/latest?style=flat-square&logo=docker&label=version" alt="Docker Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/jeffreymooiweer/ProxyWake?style=flat-square" alt="License"></a>
  <img src="https://img.shields.io/badge/platform-amd64%20%7C%20arm64-blue?style=flat-square" alt="Platform">
</p>

<p align="center">
  <strong>Access it. Wake it.</strong><br/>
  Wake sleeping devices when they are accessed through a reverse proxy.
</p>

<p align="center">
  <a href="https://hub.docker.com/r/jeffersonmouze/proxywake"><strong>Docker Hub → jeffersonmouze/proxywake</strong></a>
</p>

---

## What it does

1. Register a device (domain, IP, MAC address).
2. Your reverse proxy sends a background wake request when someone visits that domain.
3. ProxyWake wakes the device and optionally shows a waiting page until it is online.

No need to keep servers running 24/7 just because they might be accessed.

---

## Quick start

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

Open `http://<server-ip>:8462` and follow the setup wizard.

**Next steps:** add a device, then copy the integration snippets from the **Integration** tab into Nginx Proxy Manager (or Traefik/Caddy). Full walkthrough: [docs/quick-start.md](docs/quick-start.md).

| Install option | Guide |
|----------------|-------|
| Docker Compose | [docs/docker.md](docs/docker.md) |
| Unraid | [docs/unraid.md](docs/unraid.md) — CA template in [unraid/](unraid/) |
| Environment variables | [docs/configuration.md](docs/configuration.md) |

Image: [`jeffersonmouze/proxywake`](https://hub.docker.com/r/jeffersonmouze/proxywake) — tags `latest`, `4.2`, `4.2.5` · amd64 & arm64

---

## Reverse proxy integration

Works with **Nginx Proxy Manager**, **Traefik**, **Caddy**, and **Home Assistant**.

1. Open **Integration** in the ProxyWake UI.
2. Copy the config snippets for your proxy.
3. Use your server's **LAN IP** in the ProxyWake URL (not `localhost` from inside another container).

| Guide | Link |
|-------|------|
| Overview | [docs/reverse-proxy.md](docs/reverse-proxy.md) |
| NPM | [docs/examples/nginx-proxy-manager.md](docs/examples/nginx-proxy-manager.md) |
| Traefik | [docs/examples/traefik.md](docs/examples/traefik.md) |
| Caddy | [docs/examples/caddy.md](docs/examples/caddy.md) |
| Home Assistant | [docs/examples/home-assistant.md](docs/examples/home-assistant.md) |

---

## Screenshots

<p align="center">
  <img src="docs/assets/screenshots/dashboard.png" alt="ProxyWake Dashboard" width="900" />
</p>

<p align="center">
  <img src="docs/assets/screenshots/integration.png" alt="NPM integration" width="700" />
</p>

---

## Documentation

| Topic | Link |
|-------|------|
| **Start here** | [docs/quick-start.md](docs/quick-start.md) |
| All guides | [docs/README.md](docs/README.md) |
| Troubleshooting | [docs/troubleshooting.md](docs/troubleshooting.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |

API reference (when running): `/api/docs`

---

## License

MIT — see [LICENSE](LICENSE).
