# Nginx Proxy Manager

Make Nginx Proxy Manager (NPM) wake a device whenever someone visits its domain.

## How it works

NPM's nginx has a `mirror` feature: for every request it also sends a copy, in the background, to another location. ProxyWake's snippet points that copy at `/api/wake/by-host`, which wakes the device behind the requested domain if it is offline. The visitor never notices — the mirror does not slow the request down and its result is ignored.

A second, optional line redirects visitors to the ProxyWake **waiting page** when the backend is down (nginx error 502/504), so they see a progress page instead of an error while the device boots.

## Steps

1. In ProxyWake, open **Integration → NPM**. Set the **ProxyWake URL** at the top to the address NPM can reach — the LAN IP of the ProxyWake host, e.g. `http://192.168.1.10:5001` (never `localhost`). Click **Refresh**.
2. **Global configuration (once):** copy the *Global NPM configuration* snippet. In NPM go to **Settings → Default Site → Advanced**, or create the file `/data/nginx/custom/server_proxy.conf` inside the NPM container's data folder, and paste it there. NPM includes this file in every proxy host.
3. **Per proxy host:** open each proxy host that should wake a device, go to the **Advanced** tab, paste the *Per host* snippet (`mirror /_proxywake_trigger; mirror_request_body off;`) and save.
4. Make sure the **Domain Names** of that proxy host match the domain of the device in ProxyWake exactly.
5. Test: go to **Integration → NPM test**, pick the device and click **Test**. A green result means NPM can reach ProxyWake and the domain is known.

## Checking connectivity from NPM

From the NPM container:

```bash
curl -s http://192.168.1.10:5001/api/health
```

should return `{"status":"ok", …}`. If it does not, NPM cannot reach ProxyWake — check the IP, the port (5001 with host networking) and firewalls.

## Notes

- The generated snippet contains your API key. NPM's configuration files are not public, but treat them as confidential.
- The mirror fires on **every** request. ProxyWake ignores calls for devices that are already online and applies the per-device cooldown, so this creates no noticeable load.
- The waiting page redirect sends visitors to `http://<proxywake>/waiting?domain=<host>`; that address must be reachable from their browsers too.

## Common mistakes

- `localhost` or `127.0.0.1` as ProxyWake URL — from inside the NPM container that is NPM itself.
- Domain in ProxyWake does not exactly match the NPM **Domain Names** field.
- Global snippet pasted into a proxy host, or per-host snippet pasted into the default site — they belong in different places.

## See also

- [How wake-on-access works](../reverse-proxy.md) · [Quick Start](../quick-start.md) · [Troubleshooting](../troubleshooting.md)
