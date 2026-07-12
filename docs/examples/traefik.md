# Traefik

Wake devices on access using Traefik's **built-in `forwardAuth` middleware** — no plugins required.

Every request to the router is first sent to ProxyWake's `/api/wake/by-host` endpoint. Traefik includes the original domain as `X-Forwarded-Host`, ProxyWake looks up the device for that domain and wakes it if it is offline, then answers `200` so the request continues to your service. When the device is already online the call adds only a few milliseconds.

The API key is passed as a query parameter because `forwardAuth` cannot attach custom headers to the auth request.

## Docker labels

```yaml
labels:
  # Define the middleware once
  - "traefik.http.middlewares.proxywake.forwardauth.address=http://proxywake:5001/api/wake/by-host?api_key=YOUR_API_KEY"
  # Attach it to the router of every service that should be woken
  - "traefik.http.routers.my-service.middlewares=proxywake"
```

## File provider (dynamic configuration)

```yaml
http:
  middlewares:
    proxywake:
      forwardAuth:
        address: "http://proxywake:5001/api/wake/by-host?api_key=YOUR_API_KEY"

  routers:
    my-service:
      rule: "Host(`app.example.com`)"
      service: my-service
      middlewares:
        - proxywake
```

Copy the exact snippet (with your URL and API key filled in) from **Integration → Traefik** in the ProxyWake UI.

## Steps

1. Set the ProxyWake URL in **Settings** (reachable from Traefik — LAN IP or Docker network name).
2. Open **Integration → Traefik** and copy the generated labels.
3. Attach the `proxywake` middleware to each router that fronts a wakeable device.
4. Test with the device powered off: the first request triggers the wake; refresh once the device is up.

## Behaviour and caveats

- ProxyWake responds immediately after sending the wake — it does not hold the request until the device is online. Users may need to refresh while the device boots.
- If ProxyWake itself is unreachable, `forwardAuth` blocks requests to the router. Keep ProxyWake on the same Docker network or a reliable host.
- Requests with a **valid** API key are exempt from the endpoint's rate limit; invalid keys are throttled at 60/minute.
- Use an internal (LAN/Docker) ProxyWake address so the API key in the URL never crosses a public network.

## See also

- [Reverse Proxy](../reverse-proxy.md)
- [Configuration](../configuration.md)
