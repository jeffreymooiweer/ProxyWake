# Caddy

Wake devices on access using Caddy's **built-in `forward_auth` and `handle_errors` directives** — no plugins required (Caddy 2.8+ for the `handle_errors 502 504` form).

Two building blocks:

1. **`forward_auth`** sends every request past ProxyWake's `/api/wake/by-host` first. Caddy forwards the original `Host`/`X-Forwarded-Host`, ProxyWake wakes the device if it is offline and answers `200`, and the request continues to your upstream.
2. **`handle_errors`** catches `502`/`504` while the device is still booting and redirects the visitor to the ProxyWake waiting page, which polls the device and sends the visitor back automatically once it is online.

The API key is passed as a query parameter because `forward_auth` cannot attach custom headers to the auth request.

## Caddyfile

```caddyfile
app.example.com {
    # Wake the device on every visit (fast no-op when it is already online)
    forward_auth http://proxywake:5001 {
        uri /api/wake/by-host?api_key=YOUR_API_KEY
    }

    reverse_proxy 192.168.1.50:8080

    # Device still booting? Show the ProxyWake waiting page.
    handle_errors 502 504 {
        redir * http://proxywake:5001/waiting?domain={host}
    }
}
```

Copy the exact snippet (with your URL and API key filled in) from **Integration → Caddy** in the ProxyWake UI.

On Caddy older than 2.8, replace the `handle_errors` block with the expression form:

```caddyfile
handle_errors {
    @offline expression `{err.status_code} in [502, 504]`
    redir @offline http://proxywake:5001/waiting?domain={host}
}
```

## Steps

1. Configure the ProxyWake URL in **Settings** — it must be reachable by **both** Caddy (for `forward_auth`) and the visitor's browser (for the waiting-page redirect).
2. Open **Integration → Caddy** and copy the generated snippet into the site block.
3. Reload Caddy (`caddy reload`).
4. Test with the device powered off: the first request wakes it and shows the waiting page, which redirects back when the device is online.

## Behaviour and caveats

- If ProxyWake itself is unreachable, `forward_auth` blocks requests to the site.
- Requests with a **valid** API key are exempt from the endpoint's rate limit; invalid keys are throttled at 60/minute.
- Caddy must have a network path to the device's broadcast domain for Wake-on-LAN (or use an SSH/webhook/IPMI wake method).

## See also

- [Reverse Proxy](../reverse-proxy.md)
- [Nginx Proxy Manager](nginx-proxy-manager.md)
