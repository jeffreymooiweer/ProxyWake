# Troubleshooting

Common problems and how to fix them.

## Permission errors on Unraid (unable to open database file)

**Symptoms:** Container crashes on start with `sqlite3.OperationalError: unable to open database file`.

**Cause:** The appdata folder is not writable by the container user (UID 1000).

**Fix (immediate, without updating the image):**

```bash
chown -R 1000:1000 /mnt/user/appdata/proxywake
```

Then restart the container.

**Fix (image 4.2.3+):** The entrypoint automatically fixes appdata ownership on startup when running as root.

## Wake does not work

**Checks:**

1. WOL enabled in BIOS and on the correct NIC (usually Ethernet).
2. MAC address matches the WOL-capable interface.
3. Docker has `--cap-add NET_RAW`.
4. ProxyWake and target device share a broadcast domain (same VLAN/subnet).
5. Review **Logs** for errors.

**Try:** Manual wake from **Devices** → Wake.

## NPM cannot reach ProxyWake

**Checks:**

1. ProxyWake URL uses the **host LAN IP**, not `localhost`.
2. Host port (default `8462`) is open on the firewall.
3. NPM container can reach the host IP.

See [Reverse Proxy](reverse-proxy.md) and [Nginx Proxy Manager](examples/nginx-proxy-manager.md).

## Waiting page stuck

**Checks:**

1. Device IP and verification method (ping/TCP/HTTP) are correct.
2. Increase timeout in device settings for slow boots.
3. Check `GET /api/public/status/<domain>` in browser dev tools.

## Authentication errors

**Checks:**

1. `X-API-Key` matches **Settings → API key**.
2. API key has `wake` scope for background wake.
3. Re-login if the session expired.

## Credentials invalid after restart

**Cause:** `PROXYWAKE_SECRET_KEY` changed.

**Fix:** Set a fixed `PROXYWAKE_SECRET_KEY` or re-save device credentials.

## Errors after upgrade

Back up `PROXYWAKE_DATA_DIR` and see [Migration](migration.md).

## Quick checks

```bash
curl -s http://192.168.1.10:8462/api/health | jq
docker logs --tail 100 proxywake
```

## See also

- [Quick Start](quick-start.md)
- [Configuration](configuration.md)
- [Docker](docker.md)
