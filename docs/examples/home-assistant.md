# Home Assistant

ProxyWake and Home Assistant can work in both directions.

## Option A: Home Assistant wakes devices through ProxyWake

Add a switch to Home Assistant that calls the ProxyWake API. ProxyWake generates the exact snippet under **Integration → Home Assistant** (pick the device); it looks like this:

```yaml
switch:
  - platform: rest
    name: "Wake NAS"
    resource: "http://192.168.1.10:5001/api/devices/1/wake"
    method: POST
    headers:
      X-API-Key: "your-api-key"
    body_on: "{}"
    body_off: "{}"
```

Add it to `configuration.yaml`, restart Home Assistant, and use the switch in dashboards or automations ("wake the media server every weekday at 18:00").

Prefer a service call instead of a switch? A `rest_command` works the same way:

```yaml
rest_command:
  wake_nas:
    url: "http://192.168.1.10:5001/api/devices/1/wake"
    method: POST
    headers:
      X-API-Key: "your-api-key"
```

## Option B: ProxyWake wakes a device through Home Assistant

Useful when Home Assistant already knows how to switch the device on — a smart plug, a Zigbee relay, an ESPHome button.

1. In Home Assistant, create an automation with a **Webhook** trigger. Home Assistant shows the webhook URL, e.g. `http://homeassistant.local:8123/api/webhook/wake-nas-abc123`. As the action, turn on the plug/relay.
2. In ProxyWake, edit the device, set **Wake method** to **Home Assistant** and paste that webhook URL.

When the device needs waking, ProxyWake sends a POST to the webhook and Home Assistant does the rest. No access token is needed — the webhook URL itself is the secret, so keep it private.

## Common mistakes

- Using `localhost` in the URL from inside a container — use the LAN IP or `homeassistant.local`.
- The API key was restricted and lacks the `wake` scope.
- Webhook automations in Home Assistant are disabled by default for external access; keep both on the same LAN.

## See also

- [API](../api.md) · [How wake-on-access works](../reverse-proxy.md)
