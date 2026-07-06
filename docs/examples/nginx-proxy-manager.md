# Nginx Proxy Manager

Configure NPM to trigger ProxyWake when a proxied host receives traffic.

## Steps

1. In ProxyWake **Settings**, set the ProxyWake URL to an address NPM can reach (e.g. `http://192.168.1.10:8462`).
2. Open **Integration → NPM**.
3. Copy **Global config** into NPM → **Settings** → **Default Site** → **Advanced** (custom Nginx configuration).
4. For each proxy host, paste the **per-host snippet** under **Advanced**.
5. Run **Test NPM wake** in the Integration tab.

Snippets are generated in the UI with your API key embedded.

## ProxyWake URL example

```
http://192.168.1.10:8462
```

Test from the NPM container:

```bash
curl -s http://192.168.1.10:8462/api/health
```

## Common mistakes

- `localhost` or `127.0.0.1` as ProxyWake URL from inside NPM.
- Domain in ProxyWake does not match NPM **Domain Names** field.
- API key missing `wake` scope.

## See also

- [Reverse Proxy](../reverse-proxy.md)
- [Quick Start](../quick-start.md)
- [Troubleshooting](../troubleshooting.md)
