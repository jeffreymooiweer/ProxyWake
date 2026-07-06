# Home Assistant

Wake devices via Home Assistant automations and the ProxyWake API.

## Option A: ProxyWake calls Home Assistant

1. Edit device → Wake method: **Home Assistant**.
2. Enter HA URL and long-lived access token.
3. Configure the HA entity or service to power on the device.

## Option B: Home Assistant calls ProxyWake

```yaml
rest_command:
  proxywake_wake_nas:
    url: "http://192.168.1.10:8462/api/devices/1/wake"
    method: POST
    headers:
      X-API-Key: "your-api-key"
```

Trigger from a button, schedule, or automation. Copy additional examples from **Integration → Home Assistant** in the UI.

## Common mistakes

- HA URL uses `localhost` from inside a container — use host IP or `homeassistant.local`.
- API key missing `wake` scope.

## See also

- [API](../api.md)
- [Reverse Proxy](../reverse-proxy.md)
