# Contributing to ProxyWake

Thank you for your interest in contributing to ProxyWake!

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (optional, for container testing)

### Local Development

```bash
# Clone the repository
git clone https://github.com/jeffreymooiweer/ProxyWake.git
cd ProxyWake

# Backend
cd backend
pip install -r requirements.txt -r requirements-dev.txt
export PROXYWAKE_DATA_DIR=/tmp/proxywake-dev
python app.py

# Frontend (separate terminal)
cd frontend
npm ci
npm start
```

The backend serves the production frontend build on port `5001`. For frontend development with hot reload, run `npm start` (port 3000) and configure a proxy, or build the frontend:

```bash
cd frontend && npm run build
```

### Docker Development

```bash
cd docker
cp .env.example .env   # edit PROXYWAKE_PASSWORD
docker compose up -d --build
```

## Running Tests

```bash
# Backend tests
pip install -r backend/requirements-dev.txt
pytest

# With coverage
pytest --cov=backend --cov-report=term-missing

# Frontend build check
cd frontend && npm ci && npm run build
```

## Versioning

The application version is defined in `backend/version.py`. After changing it, run:

```bash
python3 scripts/sync_version.py
```

This updates `frontend/package.json`, `Dockerfile` OCI labels, and Docker publish workflow tags.

## Code Style

- **Python:** Follow existing patterns in `backend/`. Routes live in `routes/`, business logic in `services/`, shared helpers in `utils/`. Keep routes thin.
- **JavaScript:** React functional components, MUI for UI, `react-i18next` for all user-facing strings.
- **Commits:** Small, logical changesets with clear messages.
- **API:** Maintain backwards compatibility. Do not break existing endpoints without deprecation.

## Pull Request Process

1. Fork the repository and create a feature branch from `main`.
2. Make your changes with tests where applicable.
3. Ensure `pytest` and `npm run build` pass.
4. Update `CHANGELOG.md` under `[Unreleased]`.
5. Open a pull request with a clear description of what changed and why.

## Adding Translations

1. Add keys to `frontend/src/i18n/locales/en.json`.
2. Run `python3 scripts/sync_i18n.py` to merge keys into other locales.
3. Add backend error/message codes to `backend/errors.py` if needed.

## Documentation

User-facing guides live in `docs/`. Update the relevant page when changing installation, configuration, or integration behavior. Cross-link related pages instead of duplicating content.

## Reporting Issues

- **Bugs:** Use the bug report template.
- **Features:** Use the feature request template.
- **Security:** See [SECURITY.md](SECURITY.md).

## Roadmap

See [CHANGELOG.md](CHANGELOG.md) for release history and the [Unreleased] section for upcoming work. Contributions aligned with the roadmap are especially welcome.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
