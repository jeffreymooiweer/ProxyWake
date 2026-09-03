def build_npm_global_config(base_url, api_key):
    return f"""# ProxyWake - Global Nginx Proxy Manager configuration (add once)
# Location: /data/nginx/custom/server_proxy.conf
#
# This internal location forwards a mirrored copy of every request to
# ProxyWake, which wakes the device behind the requested domain if needed.

location = /_proxywake_trigger {{
    internal;
    proxy_pass {base_url}/api/wake/by-host;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-API-Key "{api_key}";
    proxy_connect_timeout 2s;
    proxy_read_timeout 2s;
}}

# Optional: show the ProxyWake waiting page while the device boots (502/504)
error_page 502 504 =302 {base_url}/waiting?domain=$host;
"""


def build_npm_host_config():
    return """# ProxyWake - Advanced configuration per proxy host
# Paste into the "Advanced" tab of each proxy host that should wake a device.
mirror /_proxywake_trigger;
mirror_request_body off;
"""


def build_traefik_config(base_url, api_key):
    return f"""# ProxyWake - Traefik (built-in forwardAuth middleware, no plugins required)
#
# Every request first passes through ProxyWake: Traefik sends the original
# domain as X-Forwarded-Host, ProxyWake looks up the device for that domain
# and wakes it if it is offline. A 200 response lets the request continue
# to your service.
#
# Docker labels - define the middleware once, then attach it per service:

labels:
  - "traefik.http.middlewares.proxywake.forwardauth.address={base_url}/api/wake/by-host?api_key={api_key}"
  - "traefik.http.routers.MY-SERVICE.middlewares=proxywake"

# File provider (dynamic configuration) equivalent:
#
# http:
#   middlewares:
#     proxywake:
#       forwardAuth:
#         address: "{base_url}/api/wake/by-host?api_key={api_key}"
#   routers:
#     my-service:
#       middlewares:
#         - proxywake
#
# Notes:
# - The API key is in the URL because forwardAuth cannot add custom headers.
#   Use an internal (LAN / Docker network) ProxyWake URL.
# - If ProxyWake itself is offline, forwardAuth blocks the request.
"""


def build_caddy_config(base_url, api_key):
    return f"""# ProxyWake - Caddy (built-in directives, no plugins required)
#
# forward_auth sends every request past ProxyWake first (wakes the device
# if it is offline); handle_errors shows the waiting page while the backend
# is still booting. Replace APP.EXAMPLE.COM and the upstream address.

APP.EXAMPLE.COM {{
    forward_auth {base_url} {{
        uri /api/wake/by-host?api_key={api_key}
    }}

    reverse_proxy 192.168.1.50:8080

    # Backend not reachable yet (502/504)? Show the ProxyWake waiting page,
    # which wakes the device and redirects back once it is online.
    # (handle_errors with status codes requires Caddy 2.8+)
    handle_errors 502 504 {{
        redir * {base_url}/waiting?domain={{host}}
    }}
}}

# Notes:
# - {base_url} must be reachable by Caddy (forward_auth) and by the
#   visitor's browser (redirect to the waiting page).
# - The API key is in the URL because forward_auth cannot add custom headers.
"""


def build_home_assistant_config(device, base_url, api_key):
    return f"""# Home Assistant REST switch for {device.get('name', device.get('domain'))}
switch:
  - platform: rest
    name: "Wake {device.get('name', device.get('domain'))}"
    resource: "{base_url}/api/devices/{device.get('id')}/wake"
    method: POST
    headers:
      X-API-Key: "{api_key}"
    body_on: "{{}}"
    body_off: "{{}}"
"""


def integration_instructions():
    return {
        'npm': [
            'Add the global configuration once (Settings -> Default Site -> Advanced, or server_proxy.conf).',
            'Paste the per-host snippet into the Advanced tab of each proxy host.',
            'Optional: the error_page rule shows the waiting page while a device boots.',
        ],
        'traefik': [
            'Define the forwardAuth middleware once (labels or file provider).',
            'Attach the middleware to the router of every service that should be woken.',
            'Make sure Traefik can reach ProxyWake; if ProxyWake is offline the middleware blocks requests.',
        ],
        'caddy': [
            'Add forward_auth and handle_errors to the site block of your service (Caddy 2.8+).',
            'Use a ProxyWake URL that both Caddy and the browser can reach.',
            'Reload Caddy with `caddy reload` and test with the device powered off.',
        ],
        'home_assistant': [
            'Add the REST switch to configuration.yaml.',
            'Restart Home Assistant after the change.',
        ],
    }
