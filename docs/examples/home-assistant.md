# Home Assistant

Wake devices via Home Assistant automations and ProxyWake webhooks.

## Purpose

Combine ProxyWake wake methods (including Home Assistant integration) with automations.

## Requirements

- Home Assistant with network access to target devices
- ProxyWake device configured with **Home Assistant** wake method (if using HA as executor)

## Step-by-step

### Option A: ProxyWake → Home Assistant wake

1. Edit device → Wake method: **Home Assistant**.
2. Enter HA URL and long-lived access token (stored encrypted).
3. Configure HA entity or service to power on the device.

### Option B: Home Assistant → ProxyWake API

1. Create a REST command or webhook automation calling:

```yaml
rest_command:
  proxywake_wake_nas:
    url: "http://192.168.1.10:8462/api/devices/1/wake"
    method: POST
    headers:
      X-API-Key: "your-api-key"
```

2. Trigger on button press, schedule, or external event.

### Integration tab

Copy the **Home Assistant** snippet from **Integration** for UI-generated examples.

## Examples

**Automation on calendar or presence:**

```yaml
automation:
  - alias: Wake NAS before backup
    trigger:
      - platform: time
        at: "02:55:00"
    action:
      - service: rest_command.proxywake_wake_nas
```

## Common mistakes

- HA URL uses `localhost` from inside a container — use host IP or `homeassistant.local`.
- API key missing `wake` scope.

## Related pages

- [API](../api.md)
- [Configuration](../configuration.md)
- [Reverse Proxy](../reverse-proxy.md)
