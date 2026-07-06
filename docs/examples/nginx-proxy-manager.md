# Nginx Proxy Manager

Integrate ProxyWake with Nginx Proxy Manager (NPM).

## Purpose

Configure NPM to trigger ProxyWake when a proxied host receives traffic.

## Requirements

- NPM and ProxyWake on the same LAN
- Device registered with domain matching the NPM proxy host
- API key with `wake` scope

## Step-by-step

1. In ProxyWake, set **Settings → ProxyWake URL** to an address NPM can reach (e.g. `http://192.168.1.10:8462`).
2. Open **Integration → NPM**.
3. Copy **Global config** into NPM → **Settings** → **Default Site** → **Advanced** → custom Nginx configuration (`server_proxy.conf` or equivalent).
4. For each proxy host, paste the **per-host snippet** under **Advanced**.
5. Run **Test NPM wake** in the Integration tab.

Exact snippets are generated in the UI with your API key embedded.

## Global config (concept)

The global section defines an internal location that NPM calls without blocking the user request. The UI provides the full, up-to-date snippet.

## Per-host snippet (concept)

Each sleeping service needs a snippet that:

- Triggers background wake for its hostname
- Optionally redirects to the waiting page while offline

## Examples

**ProxyWake URL (Unraid / Docker host):**

```
http://192.168.1.10:8462
```

**Test from NPM container:**

```bash
curl -s http://192.168.1.10:8462/api/health
```

## Common mistakes

- `localhost` or `127.0.0.1` as ProxyWake URL from inside NPM.
- Missing API key header in the internal wake location.
- Domain in ProxyWake does not match NPM **Domain Names** field.

## Related pages

- [Reverse Proxy](../reverse-proxy.md)
- [Quick Start](../quick-start.md)
- [Troubleshooting](../troubleshooting.md)
