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
    return f"""# ProxyWake - Traefik (ingebouwde forwardAuth-middleware, geen plugins nodig)
#
# Elk request gaat eerst langs ProxyWake: Traefik stuurt X-Forwarded-Host mee,
# ProxyWake zoekt het apparaat op dat domein en wekt het indien offline.
# Antwoord 200 = request gaat door naar je service.
#
# Docker labels — eenmalig de middleware definieren, daarna per service koppelen:

labels:
  - "traefik.http.middlewares.proxywake.forwardauth.address={base_url}/api/wake/by-host?api_key={api_key}"
  - "traefik.http.routers.MIJN-SERVICE.middlewares=proxywake"

# File provider (dynamic config) equivalent:
#
# http:
#   middlewares:
#     proxywake:
#       forwardAuth:
#         address: "{base_url}/api/wake/by-host?api_key={api_key}"
#   routers:
#     mijn-service:
#       middlewares:
#         - proxywake
#
# Let op:
# - De API-key staat in de URL omdat forwardAuth geen eigen headers kan
#   meesturen. Gebruik een interne (LAN/Docker-netwerk) ProxyWake-URL.
# - Is ProxyWake zelf offline, dan blokkeert forwardAuth het request.
"""


def build_caddy_config(base_url, api_key):
    return f"""# ProxyWake - Caddy (ingebouwde directives, geen plugins nodig)
#
# forward_auth stuurt elk request eerst langs ProxyWake (wekt het apparaat
# indien offline); handle_errors toont de wachtpagina zolang de backend
# nog opstart. Vervang APP.EXAMPLE.COM en het upstream-adres.

APP.EXAMPLE.COM {{
    forward_auth {base_url} {{
        uri /api/wake/by-host?api_key={api_key}
    }}

    reverse_proxy 192.168.1.50:8080

    # Backend nog niet bereikbaar (502/504)? Toon de ProxyWake-wachtpagina,
    # die het apparaat wekt en automatisch terugstuurt zodra het online is.
    # (handle_errors met statuscodes vereist Caddy 2.8+)
    handle_errors 502 504 {{
        redir * {base_url}/waiting?domain={{host}}
    }}
}}

# Let op:
# - {base_url} moet zowel voor Caddy (forward_auth) als voor de browser
#   (redirect naar de wachtpagina) bereikbaar zijn.
# - De API-key staat in de URL omdat forward_auth geen eigen headers kan
#   meesturen.
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
            'Definieer de forwardAuth-middleware eenmalig (labels of file provider).',
            'Koppel de middleware aan de router van elke service die gewekt moet worden.',
            'Zorg dat Traefik ProxyWake kan bereiken; als ProxyWake offline is blokkeert de middleware requests.',
        ],
        'caddy': [
            'Voeg forward_auth en handle_errors toe aan het site-blok van je service (Caddy 2.8+).',
            'Gebruik een ProxyWake-URL die zowel Caddy als de browser kan bereiken.',
            'Herlaad Caddy met `caddy reload` en test met het apparaat uit.',
        ],
        'home_assistant': [
            'Voeg REST switch toe aan configuration.yaml.',
            'Herstart Home Assistant na wijzigingen.',
        ],
    }
