# Configuration

Everything you can configure, and what it means. Most installs only need a password and a timezone.

## Environment variables

Set these when starting the container (`-e NAME=value` with `docker run`, in `.env` with Docker Compose, or as variables in the Unraid template).

| Variable | Needed? | Default | What it does |
|----------|---------|---------|--------------|
| `PROXYWAKE_PASSWORD` | Recommended | — | Password for the web UI. If empty, the setup wizard asks for one on first visit. |
| `TZ` | Recommended | `UTC` | Timezone for scheduled wakes, e.g. `Europe/Amsterdam`. Without it, "07:00" means 07:00 UTC. |
| `PROXYWAKE_API_KEY` | No | Generated | The key your reverse proxy uses to trigger wakes. ProxyWake generates one and shows it under **Settings**; set this only if you want a fixed value. |
| `PROXYWAKE_SECRET_KEY` | No | Generated and stored | Signs login sessions and encrypts stored SSH/IPMI passwords. ProxyWake creates one on first start and keeps it in the data folder, so you do not need to set it. Set it yourself only if you want to control it, for example to restore a backup on a different machine. |
| `PROXYWAKE_ALLOWED_ORIGINS` | No | any | Comma-separated list of browser origins allowed to call the API. Only needed when the UI is served from a different hostname than the API. |
| `PROXYWAKE_SESSION_COOKIE_SECURE` | No | `false` | Set to `true` when the UI is **only** opened over HTTPS. With `true` on plain HTTP you cannot log in. |
| `PROXYWAKE_DATA_DIR` | No | `/app/backend/data` | Where the database, logs, keys and settings are stored. |
| `PROXYWAKE_WOL_INTERFACE` | No | auto | Local IP of the network interface to send Wake-on-LAN broadcasts from. ProxyWake normally picks the interface on the device's LAN by itself; set this only if it guesses wrong on a host or container with several LAN interfaces. |

### Example `.env` for Docker Compose

```bash
PROXYWAKE_PASSWORD=ChooseAStrongPassword
TZ=Europe/Amsterdam
```

A commented template is in [`.env.example`](../.env.example).

## Settings in the web UI

Under **Settings** you will find:

| Section | What you can do |
|---------|-----------------|
| Appearance | Dark/light theme, UI language (15 languages) |
| API key | View or rotate the key used by your proxy. After rotating, the old key keeps working until you rotate again, so you can update your proxy config without downtime. |
| Password | Change the login password |
| Export / import | Export or import the device list (JSON/CSV), or make a **full backup** of everything |
| API key scopes | Limit what the API key may do (see below) |
| Notifications | Slack and Telegram alerts on wake success/failure |
| Logging | Log level shown on the Logs page |

## Per-device settings

Click the pencil icon next to a device to open its settings.

| Setting | Meaning |
|---------|---------|
| Status check | How ProxyWake decides whether the device is online: **ping** (default), **TCP** (a port answers, e.g. 445 for a NAS) or **HTTP** (a URL responds). Use TCP/HTTP for devices that block ping. |
| Wake timeout | How long to wait for the device to come online before reporting a failure. ProxyWake extends this automatically for devices that have proven to boot slowly. |
| Wake method | Wake-on-LAN, SSH, webhook, Home Assistant or IPMI. Each shows its own fields. |
| Broadcast WOL | Sends the magic packet as a broadcast as well as directly. Leave on. Optionally set a custom broadcast address (e.g. `192.168.1.255`) for unusual subnets. |
| Dependencies | Devices that must be online first. ProxyWake wakes them in order — for example the NAS before the media server that stores its files on it. |
| Cooldown | Minimum time between two wake attempts for the same device, so a page full of images does not send fifty magic packets. |

## API key scopes

The API key can be restricted to what your integration really needs:

| Scope | Allows |
|-------|--------|
| `read` | Listing devices, status, statistics, logs |
| `write` | Creating and changing devices and groups |
| `wake` | Triggering wakes — this is all a reverse proxy needs |
| `admin` | Backup and restore |

The key starts with all scopes. Restrict it under **Settings → API key scopes** if the key is stored somewhere you consider less safe (for example in a proxy configuration file).

## Common mistakes

- Exposing the UI to the internet without a password or HTTPS.
- Setting `PROXYWAKE_SESSION_COOKIE_SECURE=true` while still opening the UI over plain HTTP (logins will not stick).
- Changing `PROXYWAKE_SECRET_KEY` after saving SSH or IPMI passwords — they become unreadable and must be entered again.
- Forgetting `TZ`, then wondering why the 07:00 schedule fires at 09:00.

## See also

- [Docker](docker.md) · [Security](security.md) · [API](api.md)
