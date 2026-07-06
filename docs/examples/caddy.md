# Caddy

Add Caddyfile snippets that wake devices when a site is accessed.

## Steps

1. Configure the ProxyWake URL in **Settings**.
2. Open **Integration → Caddy**.
3. Copy the Caddyfile snippet for your device or global pattern.
4. Reload Caddy (`caddy reload`).
5. Test with the device offline.

Snippets are generated in the UI — regenerate after domain changes instead of editing hostnames manually.

## Common mistakes

- Caddy on another machine without network path to the WOL broadcast domain.
- Stale snippets after renaming domains.

## See also

- [Reverse Proxy](../reverse-proxy.md)
- [Nginx Proxy Manager](nginx-proxy-manager.md)
