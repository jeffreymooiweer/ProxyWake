# Traefik

Use Traefik middleware or labels to wake devices on access.

## Steps

1. Set the ProxyWake URL in **Settings** (LAN-reachable).
2. Open **Integration → Traefik**.
3. Copy the generated labels or middleware configuration.
4. Apply to the Docker service or file provider for the target router.
5. Test with the device powered off.

Snippets are generated per environment in the Integration tab. They typically call the ProxyWake wake endpoint with `X-API-Key` before forwarding to the upstream.

## Common mistakes

- Middleware on the wrong router (Host rule mismatch).
- ProxyWake only on an internal Docker network without route from Traefik.

## See also

- [Reverse Proxy](../reverse-proxy.md)
- [Configuration](../configuration.md)
