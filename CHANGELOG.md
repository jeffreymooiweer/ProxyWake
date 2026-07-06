# Changelog

All notable changes to ProxyWake are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v4.0.0

- Wake verification with TCP/HTTP health checks
- Multiple wake methods (WOL, SSH, webhook, Home Assistant)
- Device dependencies and adaptive wake intelligence
- OpenAPI documentation and API scopes
- Enhanced logging, statistics, backups, and notifications

## [3.2.0] - 2026-07-06

### Added

- Backend modular structure: `routes/` blueprints, `services/` package, `utils/` package
- `create_app()` factory pattern in `app.py`
- `database.py` for initialization and schema migration
- `extensions.py` for shared Flask extensions (rate limiter)
- Schema version tracking in database migrations (`schema_version` setting)

### Changed

- Split monolithic `app.py` (710 lines) into focused route modules
- Split `services.py` into `wake_service`, `settings_service`, `notification_service`, etc.
- Split `utils.py` into `validators`, `network`, and `http` helpers
- No breaking API changes — all existing endpoints preserved

- Multiple wake methods (WOL, SSH, webhook, Home Assistant)
- Device dependencies and adaptive wake intelligence
- OpenAPI documentation and API scopes
- Enhanced logging, statistics, backups, and notifications

## [3.1.0] - 2026-07-06

### Added

- `backend/version.py` as single source of truth for application version
- Baseline pytest test suite (validators, auth, device CRUD, wake flow)
- `CHANGELOG.md`, `SECURITY.md`, and `CONTRIBUTING.md`
- GitHub issue templates and Dependabot configuration
- CI workflows for backend tests and frontend build

### Fixed

- Missing `utils` imports in `app.py` (device validation and network scan)

### Changed

- Aligned version numbers across backend, frontend, and Docker labels (`3.1.0`)

## [3.0.0] - 2026-07-05

### Added

- Full ProxyWake v3 rewrite with modern React UI (8 tabs)
- Nginx Proxy Manager, Traefik, Caddy, and Home Assistant integration snippets
- Waiting page with auto-redirect (`/waiting?domain=...`)
- Webhooks, scheduled wake, export/import
- Password protection, API key auth, rate limiting, audit log
- Multi-language support (15 languages)
- Multi-arch Docker image (`linux/amd64`, `linux/arm64`)
- README screenshot gallery

[Unreleased]: https://github.com/jeffreymooiweer/ProxyWake/compare/v3.1.0...main
[3.1.0]: https://github.com/jeffreymooiweer/ProxyWake/compare/v3.0.0...v3.1.0
[3.0.0]: https://github.com/jeffreymooiweer/ProxyWake/releases/tag/v3.0.0
