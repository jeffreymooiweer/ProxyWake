def build_npm_global_config(base_url, api_key):
    return f"""# ProxyWake - Globale NPM configuratie (eenmalig)
# Locatie: /data/nginx/custom/server_proxy.conf

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

# Optioneel: wachtpagina bij offline backend (502/504)
error_page 502 504 =302 {base_url}/waiting?domain=$host;
"""


def build_npm_host_config():
    return """# ProxyWake - Advanced configuratie per proxy host
mirror /_proxywake_trigger;
mirror_request_body off;
"""


def build_traefik_config(base_url, api_key):
    return f"""# ProxyWake - Traefik middleware (Docker labels voorbeeld)
# Voeg toe aan je service labels:

labels:
  - "traefik.http.middlewares.proxywake-wake.plugin.webhook.url={base_url}/api/wake/by-host"
  - "traefik.http.middlewares.proxywake-wake.plugin.webhook.headers.X-API-Key={api_key}"
  - "traefik.http.middlewares.proxywake-wake.plugin.webhook.headers.Host={{Host}}"
  - "traefik.http.routers.myservice.middlewares=proxywake-wake"
"""


def build_caddy_config(base_url, api_key):
    host = base_url.replace('https://', '').replace('http://', '').rstrip('/')
    return f"""# ProxyWake - Caddy snippet (Caddyfile)
@wake_needed {{
    not host localhost
}}
handle @wake_needed {{
    route /_proxywake_internal/* {{
        reverse_proxy {host} {{
            header_up X-API-Key "{api_key}"
            header_up Host {{http.request.host}}
        }}
    }}
}}
"""


def build_home_assistant_config(device, base_url, api_key):
    return f"""# Home Assistant REST switch voor {device.get('name', device.get('domain'))}
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
            'Voeg de globale NPM-configuratie eenmalig toe.',
            'Voeg per proxy host de host-configuratie toe onder Advanced.',
            'Optioneel: error_page regel toont wachtpagina bij offline backend.',
        ],
        'traefik': [
            'Gebruik een webhook/forward-auth plugin of externe middleware.',
            'Pas labels aan op basis van je Traefik-versie.',
        ],
        'caddy': [
            'Voeg het snippet toe aan je Caddyfile site-blok.',
            'Zorg dat Caddy ProxyWake intern kan bereiken.',
        ],
        'home_assistant': [
            'Voeg REST switch toe aan configuration.yaml.',
            'Herstart Home Assistant na wijzigingen.',
        ],
    }
