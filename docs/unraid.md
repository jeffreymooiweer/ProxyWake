# Unraid

Install ProxyWake on Unraid — through Community Applications (easiest) or by adding the container yourself.

## Community Applications (recommended)

1. Open **Apps** in the Unraid web UI and search for **ProxyWake**. (Not published yet? See *Private template* below.)
2. Click **Install**. The template already uses **host networking**, which Wake-on-LAN needs (see [why](docker.md#networking-and-wake-on-lan)).
3. Fill in:

| Field | What to enter |
|-------|---------------|
| **Appdata** | Leave the default `/mnt/user/appdata/proxywake` |
| **Timezone** | Your timezone, e.g. `Europe/Amsterdam` — used for scheduled wakes |
| **Password** | A password for the web UI, or leave empty to set it in the setup wizard |

   The advanced fields (secret key, allowed origins, secure cookie) can stay empty for a normal install.

4. Click **Apply**. Open the web UI from the container's icon, or go to `http://<unraid-ip>:5001`.

The template adds `--cap-add=NET_RAW` automatically so ProxyWake can ping devices to see whether they are online.

### Private template (before publication in Community Applications)

```bash
mkdir -p /boot/config/plugins/community.applications/private/proxywake
cp unraid/proxywake.xml /boot/config/plugins/community.applications/private/proxywake/
```

Then install it from **Apps → Private Apps**.

## Adding the container manually

1. Open **Docker** in the Unraid web UI and click **Add Container**.
2. Repository: `jeffersonmouze/proxywake:latest`
3. Use these settings:

| Setting | Value |
|---------|-------|
| **Network Type** | **Host**, or **Custom: br0** with a fixed IP if you want ProxyWake on its own LAN address. Both put ProxyWake on your LAN, which Wake-on-LAN needs. Plain *Bridge* does **not** work for Wake-on-LAN. |
| **Extra Parameters** | `--cap-add=NET_RAW` |
| **Path** | `/mnt/user/appdata/proxywake` → `/app/backend/data` |
| **Variable** `TZ` | e.g. `Europe/Amsterdam` |
| **Variable** `PROXYWAKE_PASSWORD` | your password (optional — the setup wizard asks otherwise) |

   No port mapping is needed with Host or Custom: br0; the UI is on port 5001 of the Unraid IP (Host) or of the container's own IP (Custom: br0). With Custom: br0, enable **Settings → Docker → Host access to custom networks** if you want to reach the UI from the Unraid server itself.

4. Apply, then open `http://<unraid-ip>:5001`.

## Nginx Proxy Manager on Unraid

Under **Integration** in ProxyWake, set the ProxyWake URL to the address NPM can reach — the Unraid IP:

```
http://<unraid-ip>:5001
```

Do **not** use `localhost` — from inside the NPM container that points at NPM itself. Then follow [Nginx Proxy Manager](examples/nginx-proxy-manager.md).

## Common mistakes

- **Bridge network** — the UI works but nothing ever wakes. Switch to Host or Custom: br0.
- Mapping appdata to `/app/data` instead of `/app/backend/data`.
- `localhost` in the NPM snippet.
- Forgetting to include `/mnt/user/appdata/proxywake` in your backup routine.

## See also

- [Template README](../unraid/README.md) · [Nginx Proxy Manager](examples/nginx-proxy-manager.md) · [Configuration](configuration.md) · [Docker](docker.md)
