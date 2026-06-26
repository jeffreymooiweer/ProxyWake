# ProxyWake v3.0

**ProxyWake** is een compleet Wake-on-LAN platform voor self-hosted omgevingen, met diepe integratie voor **Nginx Proxy Manager**, plus ondersteuning voor Traefik, Caddy en Home Assistant.

---

## Features

### Kern
- Slimme Wake-on-LAN (alleen als offline, cooldown, broadcast)
- Wachtpagina met auto-redirect (`/waiting?domain=...`)
- Online/offline status via ping
- Apparaatgroepen — batch wake

### Integraties
- **NPM** — mirror-module + optionele error_page wachtpagina
- **Traefik** — Docker labels voorbeeld
- **Caddy** — Caddyfile snippet
- **Home Assistant** — REST switch configuratie
- Inline NPM-test vanuit de UI

### Automatisering
- Webhooks (Discord, ntfy, etc.)
- Geplande wake (cron-achtig per uur/minuut)
- Export/import JSON

### Beveiliging
- Bcrypt wachtwoorden
- API-sleutel met rotatie (vorige sleutel blijft geldig)
- Rate limiting
- Auditlog
- Security headers

### Observability
- Wake-geschiedenis & statistieken
- Prometheus metrics op `/api/metrics`
- Systeemlog + audittrail in UI

### UX
- Setup-wizard bij eerste start
- Donker/licht thema
- PWA (installeerbaar)
- Netwerkscanner

---

## Snel starten

```bash
cd docker
PROXYWAKE_PASSWORD=SterkWachtwoord123 docker compose up -d
```

Open: `http://<server-ip>:8462`

De setup-wizard begeleidt je door beveiliging en netwerkconfiguratie.

---

## Omgevingsvariabelen

| Variabele | Beschrijving |
|-----------|--------------|
| `PROXYWAKE_PASSWORD` | Wachtwoord webinterface |
| `PROXYWAKE_PASSWORD_HASH` | Bcrypt hash (alternatief) |
| `PROXYWAKE_API_KEY` | Vaste API-sleutel |
| `PROXYWAKE_SECRET_KEY` | Flask sessiesleutel |
| `PROXYWAKE_ALLOWED_ORIGINS` | CORS origins |
| `PROXYWAKE_DATA_DIR` | Data directory |

---

## NPM configureren

1. Tab **Integratie** → kopieer globale config naar `server_proxy.conf`
2. Per proxy host: plak Advanced snippet
3. Optioneel: `error_page` toont wachtpagina bij offline backend
4. Test via **NPM Test** tab

---

## Wachtpagina

Wanneer een backend offline is, redirect NPM naar:

```
http://<proxywake-ip>:8462/waiting?domain=jouw.domein.nl
```

De pagina triggert wake, toont voortgang en redirect naar HTTPS zodra online.

---

## Home Assistant

```yaml
switch:
  - platform: rest
    name: "Wake NAS"
    resource: "http://proxywake:8462/api/devices/1/wake"
    method: POST
    headers:
      X-API-Key: "jouw-api-sleutel"
```

Of genereer automatisch via **Integratie → Home Assistant**.

---

## API overzicht

| Endpoint | Auth | Beschrijving |
|----------|------|--------------|
| `GET /api/health` | — | Health check |
| `GET /api/metrics` | — | Prometheus metrics |
| `POST /api/setup` | — | Eerste setup |
| `GET /api/stats` | Sessie | Statistieken |
| `GET /api/wake-events` | Sessie | Wake-geschiedenis |
| `GET /api/audit` | Sessie | Auditlog |
| `POST /api/scan` | Sessie | Netwerkscan |
| `POST /api/groups/:id/wake` | Sessie/API | Groep wake |
| `GET /api/public/status/:domain` | — | Publieke status |
| `POST /api/public/wake/:domain` | — | Publieke wake+wait |

Zie ook eerdere device/npm endpoints.

---

## HTTPS & Wake-on-WAN

- **HTTPS**: plaats ProxyWake achter NPM met Let's Encrypt
- **Wake-on-WAN**: gebruik Tailscale/WireGuard; open geen WOL-poorten naar internet

---

## Licentie

MIT
