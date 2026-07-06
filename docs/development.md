# Development

Local development setup for ProxyWake contributors.

## Purpose

Run the backend and frontend locally, execute tests, and follow project conventions.

## Requirements

- Python 3.11+
- Node.js 20+
- Optional: Docker for container testing

## Step-by-step

### Backend

```bash
git clone https://github.com/jeffreymooiweer/ProxyWake.git
cd ProxyWake/backend
pip install -r requirements.txt -r requirements-dev.txt
export PROXYWAKE_DATA_DIR=/tmp/proxywake-dev
python app.py
```

Backend listens on `http://127.0.0.1:5001`.

### Frontend

```bash
cd frontend
npm ci
npm start          # dev server on :3000
# or
npm run build      # production build served by Flask
```

For production-like testing, build the frontend and restart the backend.

### Docker

```bash
cd docker
cp .env.example .env
docker compose up -d --build
```

## Tests

```bash
pip install -r backend/requirements-dev.txt
pytest --tb=short -q

# With coverage
pytest --cov=backend --cov-report=term-missing
```

OpenAPI parity is enforced by `tests/test_openapi_coverage.py`.

## Version synchronization

Single source of truth: `backend/version.py`.

After changing the version:

```bash
python3 scripts/sync_version.py
python3 scripts/check_version_consistency.py
```

This updates `frontend/package.json`, `Dockerfile` OCI labels, and Docker workflow tags.

## i18n

```bash
python3 scripts/sync_i18n.py
```

Merges missing keys from `en.json` into other locales.

## Code layout

```
backend/
  routes/       # Flask blueprints (thin)
  services/     # Business logic
  utils/        # Shared helpers
  openapi/      # OpenAPI spec
frontend/src/   # React + MUI + i18n
tests/          # pytest suite
```

## Common mistakes

- Forgetting `PROXYWAKE_DATA_DIR` — tests and dev may share production data paths.
- Skipping `npm run build` before testing the integrated UI on port 5001.
- Hardcoding version strings — import from `version.py` or run `sync_version.py`.

## Related pages

- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [API](api.md)
- [Troubleshooting](troubleshooting.md)
