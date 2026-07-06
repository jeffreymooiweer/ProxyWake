# Troubleshooting

Common ProxyWake problems and how to fix them.

## Purpose

Diagnose wake failures, connectivity issues, and configuration errors.

## Requirements

- Access to ProxyWake logs (Settings → Logs or `docker logs proxywake`)
- Basic network knowledge (IP, MAC, subnets)

## Wake does not work

**Symptoms:** Device stays offline after proxy access.

**Checks:**

1. WOL enabled in BIOS and on the correct NIC (usually Ethernet).
2. MAC address matches the interface that supports WOL.
3. Docker has `--cap-add NET_RAW`.
4. ProxyWake and target device share a broadcast domain (same VLAN/subnet).
5. Review **Logs** for wake errors (SSH, IPMI, webhook).

**Try:** Manual wake from **Devices** → Wake button.

## NPM cannot reach ProxyWake

**Symptoms:** Integration test fails; no wake on access.

**Checks:**

1. ProxyWake URL uses **host LAN IP**, not `localhost`.
2. Port `8462` (or custom) is open on the host firewall.
3. NPM container can ping the host IP.

See [Reverse Proxy](reverse-proxy.md).

## Waiting page stuck

**Symptoms:** Visitor sees waiting page indefinitely.

**Checks:**

1. Device IP and verification method (ping/TCP/HTTP) are correct.
2. Adaptive timeout — slow boots may need higher timeout in device settings.
3. `GET /api/public/status/<domain>` returns expected state (browser dev tools).

## Authentication errors

**Symptoms:** `401 AUTH_REQUIRED` from API or NPM.

**Checks:**

1. `X-API-Key` matches Settings → API key.
2. API key has `wake` scope for background wake.
3. Session expired — re-login to the UI.

## Encrypted credentials invalid after restart

**Symptoms:** SSH/IPMI wake fails after container recreate.

**Cause:** `PROXYWAKE_SECRET_KEY` changed.

**Fix:** Set a fixed `PROXYWAKE_SECRET_KEY` or re-save device credentials.

## Database / migration issues

**Symptoms:** Errors on startup after upgrade.

**Fix:** See [Migration](migration.md). Back up `PROXYWAKE_DATA_DIR` first.

## Examples

**Health check:**

```bash
curl -s http://192.168.1.10:8462/api/health | jq
```

**Docker logs:**

```bash
docker logs --tail 100 proxywake
```

## Common mistakes

- Debugging WOL across routers without directed broadcast or relay.
- Testing with Wi-Fi MAC while WOL is on Ethernet only.

## Related pages

- [Quick Start](quick-start.md)
- [Configuration](configuration.md)
- [Docker](docker.md)
