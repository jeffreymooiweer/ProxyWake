# Quick Start

This guide gets ProxyWake running and wakes your first device. No prior Docker experience is needed beyond being able to paste a command into a terminal.

## Before you begin

You need:

- **A machine that is always on** to run ProxyWake: a NAS, an Unraid or TrueNAS server, a Raspberry Pi, a mini PC — anything that runs Docker on Linux. It must be on the **same local network** as the devices you want to wake.
- **Wake-on-LAN enabled** on each device you want to wake. This is a setting in the device's BIOS/UEFI and sometimes in the network adapter driver ("Wake on Magic Packet"). Wake-on-LAN normally only works over a **wired** (Ethernet) connection.
- The device's **IP address** and **MAC address** (the hardware address of its wired network adapter, looking like `AA:BB:CC:DD:EE:FF`).

## 1. Run ProxyWake

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

What the important parts mean:

| Part | Why it is there |
|------|-----------------|
| `--network host` | **Puts ProxyWake on your LAN, which Wake-on-LAN needs.** The magic packet is a broadcast; from Docker's default private network it would never reach your devices. Prefer a dedicated IP for the container? Use a macvlan network instead — see [Docker → Networking](docker.md#networking-and-wake-on-lan). |
| `--cap-add NET_RAW` | Allows ProxyWake to *ping* devices to see whether they are online. |
| `-e TZ=…` | Your timezone, so scheduled wakes happen at the right local time. |
| `-v proxywake_data:…` | Keeps your devices, settings and logs when the container is updated. |

Prefer Docker Compose or Unraid? See [Docker](docker.md) or [Unraid](unraid.md).

Now open **`http://<ip-of-the-machine>:5001`** in your browser and complete the setup wizard. It asks for a password (if you did not set one above) and the address other machines use to reach ProxyWake — usually exactly the URL you just opened.

## 2. Add a device

1. Go to **Devices**.
2. Fill in the **New device** form:

| Field | Example | Notes |
|-------|---------|-------|
| Name | `NAS` | Anything you like |
| Domain | `nas.home.lab` | The hostname people type in the browser — must match your proxy **exactly** |
| IP | `192.168.1.50` | The device's LAN address |
| MAC | `AA:BB:CC:DD:EE:01` | Of the wired adapter that has Wake-on-LAN enabled |
| Broadcast WOL | on | Leave on; it makes waking far more reliable |

3. Click **Add**.

## 3. Test that it wakes

Put the device to sleep or shut it down, then press the ⏻ (power) button in the device's row. ProxyWake sends the wake signal and shows the progress until the device answers. If it does not come up, go to [Troubleshooting → Wake does not work](troubleshooting.md#wake-does-not-work) — the most common causes take a minute to check.

## 4. Connect your reverse proxy

1. Open the **Integration** tab.
2. Pick your proxy (Nginx Proxy Manager, Traefik or Caddy) and copy the generated configuration. It already contains your API key and ProxyWake address.
3. Paste it where the guide for your proxy says:
   - [Nginx Proxy Manager](examples/nginx-proxy-manager.md)
   - [Traefik](examples/traefik.md)
   - [Caddy](examples/caddy.md)

The **ProxyWake URL** in the generated snippets must be reachable *from the proxy*. If the proxy runs in another container, use the LAN IP of the machine running ProxyWake (e.g. `http://192.168.1.10:5001`), never `localhost`.

## 5. Try it for real

With the device off, open its domain in a browser. Your proxy notifies ProxyWake, ProxyWake wakes the device, and — depending on your proxy setup — you either see the ProxyWake waiting page that forwards you automatically, or you refresh once the device is up.

## Common mistakes

- **Running without `--network host`** — everything looks fine in the UI but nothing ever wakes. See [Docker → Networking](docker.md#networking-and-wake-on-lan).
- **Wrong MAC address** — a PC often has several adapters (Ethernet, Wi-Fi, a second Ethernet port). Use the one that is plugged in and has Wake-on-LAN enabled.
- **`localhost` in the proxy snippet** — another container cannot reach ProxyWake through `localhost`.
- **Domain mismatch** — `nas.home.lab` in ProxyWake and `nas.home.lab:443` or `www.nas.home.lab` in the proxy are not the same.

## See also

- [Docker](docker.md) · [Configuration](configuration.md) · [Troubleshooting](troubleshooting.md)
