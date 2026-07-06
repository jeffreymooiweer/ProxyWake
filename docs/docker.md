# Docker

Run ProxyWake in Docker with production-ready defaults.

## Purpose

Deploy ProxyWake as a container with correct capabilities, volumes, and health checks.

## Requirements

- Docker 20+ or Docker Compose v2
- Port `8462` (host) → `5001` (container) unless customized
- `NET_RAW` capability for Wake-on-LAN

## Step-by-step

### Docker Hub (recommended)

```bash
docker run -d \
  --name proxywake \
  --restart unless-stopped \
  --cap-add NET_RAW \
  -p 8462:5001 \
  -e PROXYWAKE_PASSWORD=YourSecurePassword \
  -v proxywake_data:/app/backend/data \
  jeffersonmouze/proxywake:4.2.1
```

Pin `:4.2` for the minor line or `:latest` for the newest build.

### Docker Compose (root)

```bash
curl -O https://raw.githubusercontent.com/jeffreymooiweer/ProxyWake/main/docker-compose.yml
cp .env.example .env   # optional: edit variables
docker compose up -d
```

### Local build

```bash
git clone https://github.com/jeffreymooiweer/ProxyWake.git
cd ProxyWake/docker
cp .env.example .env
docker compose up -d --build
```

## Image details

| Property | Value |
|----------|-------|
| Image | `jeffersonmouze/proxywake` |
| Tags | `latest`, `4.2`, `4.2.1` (see [CHANGELOG](../CHANGELOG.md)) |
| Architectures | `linux/amd64`, `linux/arm64` |
| Base | `python:3.11-slim` + Node 20 build stage |
| User | Non-root `proxywake` (UID 1000) |
| Health check | `GET /api/health` every 30s |

The multi-stage [Dockerfile](../Dockerfile) builds the React frontend, installs Python dependencies, and bundles `ipmitool`, `openssh-client`, and `sshpass` for SSH and IPMI wake methods.

## Volumes

| Container path | Purpose |
|----------------|---------|
| `/app/backend/data` | SQLite DB, logs, API keys, settings |

Back up this directory before upgrades. See [Migration](migration.md).

## Environment

See [Configuration](configuration.md). Minimum production setup:

```bash
PROXYWAKE_PASSWORD=strong-password
```

## Signal handling

The container runs `gunicorn` via [entrypoint.sh](../backend/entrypoint.sh). Docker `SIGTERM` stops workers gracefully.

## Examples

**Custom image tag:**

```bash
PROXYWAKE_IMAGE=jeffersonmouze/proxywake:4.2.1 docker compose up -d
```

**View logs:**

```bash
docker logs -f proxywake
```

## Common mistakes

- Missing `NET_RAW` — WOL fails.
- Binding only to `127.0.0.1` on the host while NPM runs in another container.
- Expecting SSH/IPMI wake without network route from container to target BMC/SSH host.

## Related pages

- [Unraid](unraid.md)
- [Quick Start](quick-start.md)
- [Configuration](configuration.md)
- [Troubleshooting](troubleshooting.md)
