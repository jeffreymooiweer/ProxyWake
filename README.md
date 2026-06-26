# ProxyWake

**ProxyWake** integreert Wake-on-LAN (WOL) met [Nginx Proxy Manager (NPM)](https://nginxproxymanager.com/). Apparaten worden automatisch geactiveerd via een Magic Packet wanneer iemand een proxy/domein benadert.

Ontworpen voor self-hosted omgevingen zoals Unraid, met een moderne webinterface en veilige API.

---

## Features

- **Wake-on-LAN** — Verstuur Magic Packets naar apparaten op je netwerk
- **NPM-integratie** — Genereer kant-en-klare Nginx-configuratie met mirror-module
- **Apparaatbeheer** — Toevoegen, bewerken, verwijderen en testen
- **Live status** — Online/offline detectie via ping
- **Logboek** — Bekijk wake-acties en fouten in de UI
- **Beveiliging** — Wachtwoordbeveiliging, API-sleutel, rate limiting, security headers
- **Docker-ready** — Productie-server met Gunicorn en health checks

---

## Snel starten

### Docker Compose

```bash
cd docker
PROXYWAKE_PASSWORD=jouwwachtwoord docker compose up -d
```

Open daarna: `http://<server-ip>:8462`

### Omgevingsvariabelen

| Variabele | Beschrijving |
|-----------|--------------|
| `PROXYWAKE_PASSWORD` | Wachtwoord voor de webinterface (aanbevolen) |
| `PROXYWAKE_API_KEY` | Vaste API-sleutel voor NPM (optioneel, anders auto-gegenereerd) |
| `PROXYWAKE_SECRET_KEY` | Flask sessiesleutel (optioneel) |
| `PROXYWAKE_ALLOWED_ORIGINS` | CORS origins, komma-gescheiden (optioneel) |
| `PROXYWAKE_DATA_DIR` | Pad voor database, logs en API-sleutel |

---

## NPM configureren

1. Open **Integratie** in ProxyWake
2. Kopieer de **globale configuratie** naar NPM (`server_proxy.conf` of Custom Nginx)
3. Voeg per proxy host de **host-configuratie** toe onder **Advanced**
4. Zorg dat NPM ProxyWake kan bereiken op je interne netwerk

Bij elk bezoek stuurt NPM op de achtergrond een wake-verzoek naar ProxyWake zonder de gebruiker te vertragen.

---

## API

Basis-URL: `http://<server-ip>:8462/api`

| Methode | Endpoint | Auth | Beschrijving |
|---------|----------|------|--------------|
| GET | `/health` | — | Health check |
| GET | `/devices` | Sessie/API-key | Apparaten ophalen |
| POST | `/devices` | Sessie/API-key | Apparaat toevoegen |
| PUT | `/devices/:id` | Sessie/API-key | Apparaat bijwerken |
| DELETE | `/devices/:id` | Sessie/API-key | Apparaat verwijderen |
| POST | `/devices/:id/wake` | Sessie/API-key | Magic Packet testen |
| GET/POST | `/wake/by-host` | API-key | Wake op basis van Host-header (voor NPM) |
| GET | `/npm/config` | Sessie/API-key | NPM-configuratie genereren |
| GET | `/logs` | Sessie | Logboek ophalen |

Authenticatie via sessiecookie (webinterface) of header `X-API-Key` / `Authorization: Bearer <key>`.

---

## Ontwikkeling

```bash
# Backend
cd backend
pip install -r requirements.txt
PROXYWAKE_DATA_DIR=./data python app.py

# Frontend (aparte terminal)
cd frontend
npm install
npm start
```

---

## Licentie

MIT — zie [LICENSE](LICENSE).
