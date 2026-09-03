# Troubleshooting

Common problems, what causes them, and how to fix them. Start with the section that matches what you see.

## Wake does not work

The device stays off after pressing ⏻ in ProxyWake (or after visiting its domain). Work through these in order — the first two cause the vast majority of cases.

### 1. ProxyWake is not on your LAN (Docker networking)

**Symptom:** ProxyWake reports "magic packet sent", the Logs page shows `Wake action sent to …`, but nothing wakes. Another tool on a real computer or phone *can* wake the device.

**Cause:** The container runs on Docker's default bridge network. Wake-on-LAN packets are broadcasts, and broadcasts from that private network never reach your LAN.

**Fix:** Put ProxyWake on your LAN — either with **host networking** or with a **macvlan/ipvlan network** that gives it its own LAN IP:

- `docker run … --network host …` (remove any `-p` mapping), or
- Docker Compose: `network_mode: host`, or the bundled `docker-compose.macvlan.yml`, or
- Unraid: **Network Type: Host** or **Custom: br0** with a fixed IP

The UI then lives on port `5001` (of the host IP, or of the container's own IP). Details and the differences: [Docker → Networking](docker.md#networking-and-wake-on-lan).

If you use a macvlan/custom network **and** the container also has a second network (for example the proxy's network), ProxyWake picks the interface on the device's LAN automatically. Check the Logs page at debug level for `Magic packet … sent to 3 target(s) from <ip>`; if the IP is not on the device's LAN, set `PROXYWAKE_WOL_INTERFACE` to the container's LAN IP.

### 2. Wrong MAC address

**Symptom:** Same as above, but host networking is already in use.

**Cause:** PCs often have more than one network adapter (Ethernet, Wi-Fi, a second port, a virtual adapter). Wake-on-LAN only works with the MAC address of the adapter that is **plugged in** and has Wake-on-LAN **enabled**. Other tools that wake the device successfully may have learned the correct MAC automatically.

**Fix:** On the device, look up the MAC of the wired adapter (`ipconfig /all` on Windows, `ip link` on Linux) and compare it letter by letter with ProxyWake.

### 3. Wake-on-LAN is not enabled on the device

Check the BIOS/UEFI ("Wake on LAN", "Power on by PCI-E", "ErP" must be *disabled*) and the adapter driver settings in the OS ("Wake on Magic Packet"). On Windows also disable Fast Startup, which keeps the adapter in a state that ignores magic packets after a shutdown.

### 4. Broadcast switched off or wrong subnet

Open the device settings in ProxyWake and make sure **Broadcast WOL** is on. If your network uses an unusual subnet mask, set the broadcast address explicitly (e.g. `192.168.0.255`).

### 5. Check what ProxyWake actually did

The **Logs** page shows one of:

- `Wake action sent to …` — the packet left ProxyWake; the problem is on the network or the device (points 1–4).
- `… is already online` / skipped — ProxyWake thinks the device is up. Its status check may be hitting something else (another device took over the IP, or a TCP/HTTP check is pointed at the wrong port). Fix the status check in the device settings.
- An error such as `SSH_CREDENTIALS_MISSING` or `WEBHOOK_WAKE_FAILED` — the wake method is misconfigured; open the device settings.

### Test outside ProxyWake

To rule out ProxyWake, send a magic packet straight from the container (host networking required):

```bash
docker exec proxywake python3 -c "from wakeonlan import send_magic_packet; send_magic_packet('AA:BB:CC:DD:EE:FF', ip_address='255.255.255.255')"
```

If this does not wake the device either, the problem is the MAC address, the device's Wake-on-LAN settings, or the network path.

## The device is shown as offline although it is on

**Cause:** The status check does not get an answer. Many devices (Windows in particular) do not answer ping, and ping also needs `--cap-add NET_RAW`.

**Fix:** In the device settings switch the status check to **TCP** with a port the device listens on (445 for SMB, 22 for SSH, 32400 for Plex, 8123 for Home Assistant…) or **HTTP** with a URL that returns a page.

## Container crashes on start: `unable to open database file`

**Cause:** The data folder is not writable by the container user (UID 1000). Common on Unraid when the folder was created by root.

**Fix:** Images 4.2.3 and newer fix the ownership automatically on start. On older images run:

```bash
chown -R 1000:1000 /mnt/user/appdata/proxywake
```

## The proxy cannot reach ProxyWake

**Symptom:** NPM's "Test wake" fails, or the proxy logs connection errors to ProxyWake.

**Checks:**

1. The ProxyWake URL in the snippet uses the **LAN IP** of the ProxyWake host, not `localhost` or `127.0.0.1`.
2. With host networking the port is `5001`; in bridge mode it is whatever you mapped (`8462` by default).
3. From inside the proxy container: `curl http://<proxywake-ip>:5001/api/health` should return JSON.

## Waiting page never finishes

**Checks:**

1. The status check for the device works (see "shown as offline" above).
2. The device really boots within the **wake timeout** (device settings). Increase it for slow machines.
3. Open the browser's developer tools and look at the requests to `/api/public/status/…` — they show what ProxyWake sees.

## Logged out all the time / login does not stick

- `PROXYWAKE_SESSION_COOKIE_SECURE=true` while opening the UI over plain HTTP → set it to `false` or use HTTPS.
- Versions before 4.2.4 lost sessions between restarts; upgrade.

## SSH or IPMI passwords stopped working

**Cause:** `PROXYWAKE_SECRET_KEY` changed (or you moved the data folder without it).

**Fix:** Re-enter the credentials in the device settings. Keep the secret key stable from now on.

## Schedules fire at the wrong time

**Cause:** The container's clock is in UTC.

**Fix:** Set `TZ` (e.g. `Europe/Amsterdam`) and restart the container. The Logs page shows the active timezone at startup.

## Quick checks

```bash
curl -s http://192.168.1.10:5001/api/health      # is ProxyWake up?
docker logs --tail 100 proxywake                 # what happened recently?
```

## See also

- [Quick Start](quick-start.md) · [Docker](docker.md) · [Configuration](configuration.md)
