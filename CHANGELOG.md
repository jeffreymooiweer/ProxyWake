# Changelog

All notable changes to ProxyWake are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [4.2.5] - 2026-07-12

### Fixed

- **API-key brute force was never throttled**: rate-limit decorators sat inside the auth decorators, so rejected (401) requests were returned before the limiter ever counted them. The limiter now wraps auth on `/api/wake/by-host`, device wake and network scan, so invalid keys are throttled while valid traffic is unaffected
- `/api/wake/by-host` no longer writes a skipped wake event for every proxied request when the device is already online, which flooded the wake-event table on busy proxies

### Changed

- **Traefik integration snippet rewritten** to a tested, plugin-free configuration using the built-in `forwardAuth` middleware (the old snippet referenced a generic "webhook plugin" that does not exist out of the box)
- **Caddy integration snippet rewritten** to a tested, plugin-free configuration using built-in `forward_auth` plus `handle_errors` with a redirect to the waiting page (the old snippet did not trigger wakes)
- The API key may be passed as an `?api_key=` query parameter (required for forward-auth middlewares, which cannot attach custom headers); headers still take precedence
- Requests with a valid API key are exempt from the `/api/wake/by-host` rate limit, since forward-auth setups route every proxied request through it
- `docs/examples/traefik.md` and `docs/examples/caddy.md` rewritten around the new configurations, including caveats

## [4.2.4] - 2026-07-12

### Fixed

- Deleting a device that has wake history no longer fails with HTTP 500 (`NOT NULL constraint failed: wake_event.device_id`); wake events, schedules and dependency links are removed together with the device
- First boot with a fresh database no longer crashes intermittently: both gunicorn workers raced in `db.create_all()` and one failed on `table app_setting already exists`, taking the server down. Schema creation now runs under a file lock
- `?host=` query parameter of `/api/wake/by-host` was unreachable because the always-present `Host` header took precedence; the explicit parameter now wins over the implicit header

- Secret key is now persisted in the data directory when `PROXYWAKE_SECRET_KEY` is not set. Previously every worker (and every call) generated a fresh random key, which invalidated sessions between the two gunicorn workers and made stored SSH/IPMI credentials permanently undecryptable
- Verified-wake job status is stored in the database instead of per-process memory, so job polling works regardless of which gunicorn worker answers the request
- Scheduled wakes run in exactly one worker (data-dir file lock); previously every worker ran its own scheduler loop. The loop now aligns to minute boundaries so schedules can no longer be skipped or double-fired
- Log level filtering on the Logs page: the log timestamp contains colons, so the parser never recognised the level of a line
- Editing a device no longer overwrites webhook URLs with their masked (`***`) display value; full backups now export the real webhook URLs so restores round-trip
- Deleting a group or NPM host clears the reference on linked devices instead of leaving a dangling id
- Schedules validate that the device exists and that hour/minute are in range; the API now also returns the configured `days`
- The waiting page fires the wake request once (non-blocking via `?wait=false`) instead of starting a new blocking wake every 3 seconds, which could exhaust all server threads
- Wake progress polling on the Devices page recovers from transient errors instead of leaving the spinner stuck

### Changed

- `POST /api/public/wake/{domain}` accepts `?wait=false` to send a wake without blocking until the device is online
- Device status checks (`/api/devices?status=true`, `/api/stats`) run concurrently instead of serially, so lists stay fast with several offline devices

## [4.2.3] - 2026-07-06

### Fixed

- Docker entrypoint fixes appdata volume permissions on Unraid and similar hosts (`unable to open database file` on first start)

## [4.2.2] - 2026-07-06

### Added

- `docs/releases/v4.2.2.md` — release notes for the correction release

### Changed

- Repository version references aligned to **4.2.2** (`backend/version.py`, frontend, Dockerfile, docs)
- `scripts/check_version_consistency.py` — generic changelog compare-link validation for any release
- CHANGELOG compare links: `[Unreleased]` → `v4.2.2...main`, `[4.2.2]` → `v4.2.1...v4.2.2`

### Fixed

- Final release consistency fixes after v4.2.1 finalization sprint
- Corrected changelog compare links that still referenced v4.2.1 as the open baseline
- Version-check script no longer hardcodes v4.2.1-specific compare expectations
- Docker workflow tag description updated to 4.2.2 (tags still derived from `backend/version.py`)
- Release/tag alignment: v4.2.2 published from current `main` without rewriting v4.2.1 history

## [4.2.1] - 2026-07-06

### Added

- Full `docs/` documentation site (quick start, Docker, reverse proxy, API, security, examples)
- `scripts/sync_version.py` — propagate version from `backend/version.py` to package.json and Dockerfile
- `scripts/check_version_consistency.py` — fail CI when critical version files disagree
- `.github/workflows/version-check.yml` — dedicated version consistency workflow
- `docs/releases/v4.2.1.md` — release notes draft
- Root `.env.example` for Docker Compose
- GitHub PR template and issue template config
- `docs/github-metadata-checklist.md` for repository settings
- SVG banner (`docs/assets/banner.svg`)
- Tests: groups, public routes, write-scope matrix, config helpers

### Changed

- README and docs updated for **v4.2.1** (Docker tags, documentation links, reverse proxy section)
- `SECURITY.md` — explicit 4.2.x / 4.1.x / 4.0.x support policy
- `backend/version.py` — `__version__` and `VERSION` constants as single source of truth
- Backend tests import version from `version.py` instead of hardcoding
- CI: pytest coverage report; version consistency check in backend tests and `version-check.yml`
- Docker workflow derives default-branch tags (`latest`, minor, patch) from `backend/version.py`
- `PROXYWAKE_SESSION_COOKIE_SECURE` for HTTPS-only session cookies

### Fixed

- CHANGELOG compare links aligned to v4.2.1 (`[Unreleased]`, `[4.2.1]`)
- Stale v4.2.0 references as current release in documentation
- Prevented future version drift through automated consistency checks

## [4.2.0] - 2026-07-06

### Added

- Complete OpenAPI 3.0 coverage for all `/api/*` routes (40+ paths)
- Automated OpenAPI parity test against Flask route registry
- `scripts/sync_i18n.py` to merge missing translation keys from English

### Changed

- i18n: Golf C–E strings synced to all 13 non-English locales (missing keys fall back to English)
- OpenAPI spec documents session-only vs scoped vs public endpoints
- `package-lock.json` version aligned with frontend `4.2.0`

## [4.1.0] - 2026-07-06

### Added

- **IPMI wake** via `ipmitool chassis power on` (BMC host, port, username, encrypted password)
- IPMI configuration fields in device edit dialog
- Credential encryption tests
- API scope tests for backup (`admin` required)

### Fixed

- Docker image now includes `openssh-client`, `sshpass`, and `ipmitool` for SSH and IPMI wake
- SSH password auth fails clearly when `sshpass` is unavailable (no silent skip)
- Backup/restore routes enforce `admin` API scope (aligned with OpenAPI)
- Group wake and dependency updates enforce `wake` / `write` scopes
- `BACKUP_VERSION` aligned to `4.0`
- Duplicate and misplaced entries in CHANGELOG 3.2.0 section removed

### Changed

- Schema version bumped to `4.1`
- IPMI removed from “coming soon” in UI

## [4.0.0] - 2026-07-06

Major release — consolidates Golf A through E into a production-ready v4 baseline.

### Added (since 3.0.0)

- **Golf A (3.1.0):** pytest suite, CI, CHANGELOG, SECURITY.md, version centralization
- **Golf B (3.2.0):** modular backend (`routes/`, `services/`, `utils/`), `create_app()` factory
- **Golf C (3.3.0):** wake verification (ping/TCP/HTTP), job polling API, wake statistics
- **Golf D (3.4.0):** multiple wake methods (WOL, SSH, webhook, Home Assistant), encrypted credentials, device dependencies
- **Golf E (3.5.0):** OpenAPI docs, API scopes, full backup/restore, rotating logs, Slack/Telegram notifications
- **Adaptive wake timeout:** extends wait time based on historical boot duration per device

### Changed

- Schema version bumped to `4.0`
- Docker image tags: `latest`, `4.0`, `4.0.0`

### Known limitations

- None for planned v4 baseline features

## [3.5.0] - 2026-07-06

### Added

- OpenAPI 3.0 specification at `/api/openapi.json` with Swagger UI at `/api/docs`
- API key scopes: `read`, `write`, `wake`, `admin` with scope enforcement on device endpoints
- Full configuration backup and restore (`GET /api/backup`, `POST /api/backup/restore`)
- Rotating log files (5 × 5 MB) with configurable log level
- Log viewer filters (level + search) in frontend
- Notification channels: Slack webhook and Telegram bot
- Settings UI for API scopes, notifications, log level, and full backup/restore

### Changed

- Schema version bumped to `3.5`
- Wake notifications now dispatch to configured Slack/Telegram channels

## [3.4.0] - 2026-07-06

### Added

- Multiple wake methods per device: WOL, SSH, webhook, Home Assistant (IPMI reserved)
- Encrypted device credentials (Fernet) for SSH password/private key
- Device dependencies with circular-dependency detection
- Dependency chain wake: dependencies are woken and verified before the target device
- API endpoints: `PUT/GET /api/devices/:id/dependencies`, `PUT /api/devices/:id/credentials`
- Frontend wake method selector, dependency multi-select, and SSH credential fields

### Changed

- Wake execution refactored into `wake_executor` service
- `WakeEvent` records `wake_method`
- Schema version bumped to `3.4`

## [3.3.0] - 2026-07-06

### Added

- Wake verification with ICMP ping, TCP port, and HTTP health checks per device
- Verified wake jobs with polling API (`POST /api/devices/:id/wake?verify=true`, `GET /api/wake/jobs/:id`)
- Device wake statistics (`wake_count`, success/failure counts, last wake duration)
- Frontend wake progress indicator on Devices page
- Status check configuration in device edit dialog

### Changed

- Online detection uses per-device `status_check_type` instead of ping-only
- Public waiting page uses device-specific timeout and check settings
- `WakeEvent` records `status` and `duration_ms`

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

[Unreleased]: https://github.com/jeffreymooiweer/ProxyWake/compare/v4.2.5...main
[4.2.5]: https://github.com/jeffreymooiweer/ProxyWake/compare/v4.2.4...v4.2.5
[4.2.4]: https://github.com/jeffreymooiweer/ProxyWake/compare/v4.2.3...v4.2.4
[4.2.3]: https://github.com/jeffreymooiweer/ProxyWake/compare/v4.2.2...v4.2.3
[4.2.2]: https://github.com/jeffreymooiweer/ProxyWake/compare/v4.2.1...v4.2.2
[4.2.1]: https://github.com/jeffreymooiweer/ProxyWake/compare/v4.2.0...v4.2.1
[4.2.0]: https://github.com/jeffreymooiweer/ProxyWake/compare/v4.1.0...v4.2.0
[4.1.0]: https://github.com/jeffreymooiweer/ProxyWake/compare/v4.0.0...v4.1.0
[4.0.0]: https://github.com/jeffreymooiweer/ProxyWake/compare/v3.5.0...v4.0.0
[3.5.0]: https://github.com/jeffreymooiweer/ProxyWake/compare/v3.4.0...v3.5.0
[3.4.0]: https://github.com/jeffreymooiweer/ProxyWake/compare/v3.3.0...v3.4.0
[3.3.0]: https://github.com/jeffreymooiweer/ProxyWake/compare/v3.2.0...v3.3.0
[3.2.0]: https://github.com/jeffreymooiweer/ProxyWake/compare/v3.1.0...v3.2.0
[3.1.0]: https://github.com/jeffreymooiweer/ProxyWake/compare/v3.0.0...v3.1.0
[3.0.0]: https://github.com/jeffreymooiweer/ProxyWake/releases/tag/v3.0.0
