# Traefik

Integrate ProxyWake with Traefik.

## Purpose

Use Traefik middleware or dynamic configuration to wake devices on access.

## Requirements

- Traefik v2+ with access to ProxyWake API
- Device domain matching Traefik router rule

## Step-by-step

1. Set ProxyWake URL in **Settings** (LAN-reachable).
2. Open **Integration → Traefik** in the ProxyWake UI.
3. Copy the generated labels or middleware configuration.
4. Apply to the Docker service or file provider for the target router.
5. Test with the device powered off.

## Examples

Traefik snippets are **generated per environment** in the Integration tab. Typical pattern:

- HTTP middleware calls ProxyWake wake endpoint with `X-API-Key`
- Router uses middleware before forwarding to upstream

Refer to the UI for exact label names and URLs — they include your API key and hostnames.

## Common mistakes

- Middleware on the wrong router (Host rule mismatch).
- ProxyWake only on internal Docker network without route from Traefik.

## Related pages

- [Reverse Proxy](../reverse-proxy.md)
- [Configuration](../configuration.md)
