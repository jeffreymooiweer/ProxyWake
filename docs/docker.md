# Docker

How to run ProxyWake as a container, and — most importantly — how to network it so Wake-on-LAN actually works.

Installing for the first time? The [Quick Start](quick-start.md) has the short version.

## Networking and Wake-on-LAN

**Read this first — it is the number one reason wake attempts silently do nothing.**

Wake-on-LAN works by sending a "magic packet" as a **broadcast** on your local network: every device on the LAN hears it, including one that is asleep. A sleeping machine does not answer normal network traffic anymore, so the broadcast is the only thing that reaches it.

By default Docker puts every container on its own private network (the *bridge*, usually `172.17.x.x`). A broadcast sent from there stays on that private network and **never arrives on your LAN**. ProxyWake will happily report "magic packet sent", and nothing wakes up.

The fix is to run the container with **host networking**, which puts ProxyWake directly on the LAN of the machine it runs on:

- `docker run`: add `--network host` (and drop any `-p` port mapping — it is ignored in host mode).
- Docker Compose: `network_mode: host` (already set in the bundled `docker-compose.yml`).
- Unraid: set **Network Type** to **Host** (the Community Applications template does this).

With host networking the web UI is on **port 5001** of the host's IP.

Cannot use host networking?

- Use a **macvlan** network so the container gets its own IP on your LAN, or
- Wake devices through **SSH**, a **webhook**, **Home Assistant** or **IPMI** instead of Wake-on-LAN — those are normal network connections that work from any Docker network.

> Docker Desktop on macOS and Windows runs containers inside a virtual machine; host networking there does not reach your physical LAN either. Run ProxyWake on a Linux host for Wake-on-LAN.

## Docker run

```bash
docker run -d \
  --name proxywake \
  --restart unless-stopped \
  --network host \
  --cap-add NET_RAW \
  -e PROXYWAKE_PASSWORD=ChooseAStrongPassword \
  -e TZ=Europe/Amsterdam \
  -v proxywake_data:/app/backend/data \
  jeffersonmouze/proxywake:latest
```

Pin a release with `:4.3.0`, or follow a minor line with `:4.3`.

## Docker Compose

```bash
curl -O https://raw.githubusercontent.com/jeffreymooiweer/ProxyWake/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/jeffreymooiweer/ProxyWake/main/.env.example
cp .env.example .env      # set PROXYWAKE_PASSWORD and TZ
docker compose up -d
```

The bundled Compose file uses host networking. If you really need bridge networking, comment out `network_mode: host`, uncomment the `ports:` section, and read the networking section above.

## Image details

| Property | Value |
|----------|-------|
| Image | [`jeffersonmouze/proxywake`](https://hub.docker.com/r/jeffersonmouze/proxywake) |
| Tags | `latest`, `4.3`, `4.3.0` |
| Architectures | `linux/amd64`, `linux/arm64` |
| Web UI port | `5001` (host networking) — or map it with `-p 8462:5001` in bridge mode |
| Runs as | Non-root user `proxywake` (UID 1000); the entrypoint fixes data-folder ownership on start |
| Health check | `GET /api/health` every 30 s |
| Includes | `ping`, `ssh`, `sshpass`, `ipmitool`, timezone data |

**`--cap-add NET_RAW`** lets the container send ICMP pings, which the default "ping" status check uses to see whether a device is online. Without it, use the TCP or HTTP status check per device.

## Data folder

| Container path | Contents |
|----------------|----------|
| `/app/backend/data` | SQLite database (devices, history), application log, API key, generated secret key, settings |

Everything ProxyWake knows lives here. Back it up before upgrading — or use **Settings → Full backup** for a downloadable file. See [Migration](migration.md).

## Environment variables

Only `PROXYWAKE_PASSWORD` and `TZ` are needed for a typical install. All variables are explained in [Configuration](configuration.md).

## Timezone

Scheduled wakes ("wake the NAS at 07:00 on weekdays") run in the container's timezone, which is UTC unless you set `TZ`. Use a name from the [tz database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones), e.g. `Europe/Amsterdam`.

## Building locally (contributors)

```bash
git clone https://github.com/jeffreymooiweer/ProxyWake.git
cd ProxyWake/docker
cp .env.example .env
docker compose up -d --build
```

## Useful commands

```bash
docker logs -f proxywake                 # follow the log
docker compose pull && docker compose up -d   # upgrade to the latest image
```

## Common mistakes

- **Bridge networking** (`-p 8462:5001` without `--network host`) — Wake-on-LAN never reaches the LAN.
- **Missing `NET_RAW`** — the ping status check always reports devices as offline.
- **Expecting SSH/IPMI wake to work** while the container cannot reach the device over the network.
- **No `TZ`** — schedules fire at UTC times.

## See also

- [Unraid](unraid.md) · [Configuration](configuration.md) · [Troubleshooting](troubleshooting.md)
