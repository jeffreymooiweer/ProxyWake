# Docker

Deploy ProxyWake as a container with persistent data and Wake-on-LAN support.

For a first install, start with [Quick Start](quick-start.md).

## Docker run

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

Pin a release with `:4.2.2` or the minor line with `:4.2`.

## Docker Compose

```bash
curl -O https://raw.githubusercontent.com/jeffreymooiweer/ProxyWake/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/jeffreymooiweer/ProxyWake/main/.env.example
cp .env.example .env   # edit PROXYWAKE_PASSWORD
docker compose up -d
```

## Image

| Property | Value |
|----------|-------|
| Image | `jeffersonmouze/proxywake` on [Docker Hub](https://hub.docker.com/r/jeffersonmouze/proxywake) |
| Tags | `latest`, `4.2`, `4.2.2` |
| Architectures | `linux/amd64`, `linux/arm64` |
| Container port | `5001` (default host mapping `8462`) |
| User | Non-root `proxywake` (UID 1000) |
| Health check | `GET /api/health` every 30s |

`NET_RAW` is required for Wake-on-LAN.

## Data volume

| Container path | Contents |
|----------------|----------|
| `/app/backend/data` | SQLite database, logs, API keys, settings |

Back up this directory before upgrades. See [Migration](migration.md).

## Environment variables

See [Configuration](configuration.md). Minimum for production:

```bash
PROXYWAKE_PASSWORD=strong-password
```

## Local build (contributors)

```bash
git clone https://github.com/jeffreymooiweer/ProxyWake.git
cd ProxyWake/docker
cp .env.example .env
docker compose up -d --build
```

## Useful commands

```bash
docker logs -f proxywake
PROXYWAKE_IMAGE=jeffersonmouze/proxywake:4.2.2 docker compose up -d
```

## Common mistakes

- Missing `NET_RAW` — WOL fails.
- Binding only to `127.0.0.1` while the reverse proxy runs in another container.
- Expecting SSH/IPMI wake without network access from the container to the target.

## See also

- [Unraid](unraid.md)
- [Configuration](configuration.md)
- [Troubleshooting](troubleshooting.md)
