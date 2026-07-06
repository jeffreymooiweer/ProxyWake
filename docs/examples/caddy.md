# Caddy

Integrate ProxyWake with Caddy.

## Purpose

Add Caddyfile snippets that wake devices when a site is accessed.

## Requirements

- Caddy v2+
- ProxyWake reachable from the Caddy host

## Step-by-step

1. Configure ProxyWake URL in **Settings**.
2. Open **Integration → Caddy**.
3. Copy the Caddyfile snippet for your device or global pattern.
4. Reload Caddy (`caddy reload`).
5. Test access with device offline.

## Examples

Snippets are generated in the UI and may use `reverse_proxy` with a `handle` block that calls ProxyWake via `reverse_proxy` or `request` directives depending on your setup.

## Common mistakes

- Editing snippet hostnames manually — regenerate from UI after domain changes.
- Caddy on another machine without network path to WOL broadcast domain.

## Related pages

- [Reverse Proxy](../reverse-proxy.md)
- [Nginx Proxy Manager](nginx-proxy-manager.md)
