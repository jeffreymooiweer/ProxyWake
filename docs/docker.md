# Docker

How to run ProxyWake as a container, and — most importantly — how to network it so Wake-on-LAN actually works.

Installing for the first time? The [Quick Start](quick-start.md) has the short version.

## Networking and Wake-on-LAN

**Read this first — it is the number one reason wake attempts silently do nothing.**

Wake-on-LAN works by sending a "magic packet" as a **broadcast** on your local network: every device on the LAN hears it, including one that is asleep. A sleeping machine does not answer normal network traffic anymore, so the broadcast is the only thing that reaches it.

By default Docker puts every container on its own private network (the *bridge*, usually `172.17.x.x`). A broadcast sent from there stays on that private network and **never arrives on your LAN**. ProxyWake will happily report "magic packet sent", and nothing wakes up.

ProxyWake needs to sit **on your LAN**. There are two ways to get there — pick one:

| Option | What it is | Web UI address | Good for |
|--------|------------|----------------|----------|
| **Host networking** | The container shares the host's network stack | `http://<host-ip>:5001` | Simplest; works everywhere on Linux |
| **macvlan / ipvlan** ("custom" network with its own IP) | The container gets its **own IP address** on your LAN, like a separate device | `http://<container-ip>:5001` | You want a dedicated IP, or other containers already use host ports |

A plain **bridge** network — Docker's default, and also the "custom bridge" networks you create with `docker network create` — is **not** enough: it is a private network behind the host, and broadcasts do not cross it. On a bridge network you can still use the **SSH**, **webhook**, **Home Assistant** and **IPMI** wake methods, which are normal network connections; only Wake-on-LAN needs one of the two options above.

### Option 1: host networking

- `docker run`: add `--network host` (and drop any `-p` port mapping — it is ignored in host mode).
- Docker Compose: `network_mode: host` (already set in the bundled `docker-compose.yml`).
- Unraid: **Network Type: Host**.

### Option 2: macvlan / ipvlan (own IP on the LAN)

The container becomes a separate device on your network with its own IP. Use the bundled [`docker-compose.macvlan.yml`](../docker-compose.macvlan.yml): set the parent interface (your LAN NIC, e.g. `eth0` or `br0`), your subnet and gateway, and a free IP outside your DHCP range, then:

```bash
docker compose -f docker-compose.macvlan.yml up -d
```

On Unraid this is the **Custom: br0** network type with a fixed IP — no Compose file needed.

Two things to know about macvlan:

- **The Docker host itself cannot talk to a macvlan container** (a Linux kernel rule). Open the UI from another device on the LAN, or add a "shim" interface on the host — search for *macvlan shim* for your distribution. Unraid handles this for you when *Host access to custom networks* is enabled in Docker settings.
- **Your reverse proxy must be able to reach ProxyWake.** If the proxy is on a bridge network on the same host, it reaches ProxyWake via the container's LAN IP like any other device. You can also attach ProxyWake to the proxy's network as well (see the commented `proxy:` network in the Compose file) and use the container name.

ProxyWake detects automatically which of its network interfaces is on the device's LAN and sends the wake broadcast from there, so combining a macvlan network with a bridge network works out of the box. If it ever picks wrong on an unusual setup, pin it with `PROXYWAKE_WOL_INTERFACE=<the container's LAN IP>`.

> Docker Desktop on macOS and Windows runs containers inside a virtual machine; neither option reaches your physical LAN from there. Run ProxyWake on a Linux host for Wake-on-LAN.

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

Pin a release with `:4.4.0`, or follow a minor line with `:4.4`. Prefer GitHub's registry? Use `ghcr.io/jeffreymooiweer/proxywake` instead of `jeffersonmouze/proxywake` — the images are built from the same commit in the same workflow run.

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
| Image (Docker Hub) | [`jeffersonmouze/proxywake`](https://hub.docker.com/r/jeffersonmouze/proxywake) |
| Image (GitHub Container Registry) | [`ghcr.io/jeffreymooiweer/proxywake`](https://github.com/jeffreymooiweer/ProxyWake/pkgs/container/proxywake) — identical builds, same tags |
| Tags | `latest`, `4.4`, `4.4.0` |
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
