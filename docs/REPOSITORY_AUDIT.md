# Repository Audit — v4.2.1 Polish Sprint

Audit date: 2026-07-06. This document summarizes the pre-polish state and actions taken in the v4.2.1 sprint.

## Version consistency

| Location | Before | After |
|----------|--------|-------|
| `backend/version.py` | 4.2.0 | **4.2.1** (source of truth) |
| `frontend/package.json` | 4.2.0 | 4.2.1 (via `sync_version.py`) |
| `Dockerfile` OCI label | 4.2.0 | 4.2.1 |
| Docker CI default tags | 4.2.0 + 4.2 | 4.2 + 4.2.1 |
| `tests/test_auth.py` | hardcoded `4.2.0` | imports `__version__` |
| OpenAPI spec | dynamic | unchanged (reads `version.py`) |

**Intentionally separate:** `SCHEMA_VERSION` (`4.1`) and `BACKUP_VERSION` (`4.0`) — data format versions, not app semver.

## Documentation

| Item | Before | After |
|------|--------|-------|
| `docs/` | Missing | Full site (12 guides + examples) |
| README Docker tags | 4.1 / 4.0 only | 4.2.x + doc links |
| README screenshots | Broken paths | Regenerated PNGs |
| Banner | Missing | `docs/assets/banner.svg` |
| Root `.env.example` | Missing | Added |

## Release / GitHub

| Item | Before | After |
|------|--------|-------|
| CHANGELOG 4.2.1 | — | Added |
| SECURITY supported | 4.1.x, 4.0.x | + 4.2.x |
| PR template | Missing | Added |
| Issue `config.yml` | Missing | Added |
| GitHub metadata guide | — | `docs/github-metadata-checklist.md` |

## Docker

| Check | Status |
|-------|--------|
| Multi-stage build | OK |
| Non-root user | OK (`proxywake:1000`) |
| Healthcheck | OK |
| NET_RAW documented | OK |
| SSH/IPMI tools | OK (4.1.0+) |
| Signal handling (gunicorn) | OK |

No breaking Docker changes in this sprint.

## CI workflows

| Workflow | Notes |
|----------|-------|
| `backend-tests.yml` | + coverage, version sync check |
| `frontend-build.yml` | OK |
| `docker.yml` | Tags/description fixed |
| `codeql.yml` | **Added** |
| Dependabot | OK (pip, npm, actions) |

## Tests

- **77 tests**, all passing
- Coverage: ~65% backend (pytest-cov in CI)
- OpenAPI parity test present
- Added: groups, public routes, write-scope, config helpers

## Dependencies

- Python: pinned ranges in `requirements.txt` — no unused packages found
- Node: CRA 5 + React 18 + MUI 5 — stable, no risky major bumps
- Docker base: `node:20-alpine`, `python:3.11-slim` — current

## Code quality

- No `TODO` / `FIXME` / `HACK` in application code
- Modular backend structure maintained
- No dead routes removed (all registered routes covered by OpenAPI test)

## Security review summary

| Area | Finding |
|------|---------|
| Secrets in repo | None found |
| API password leakage | Not returned by API |
| Credential encryption | Fernet via `PROXYWAKE_SECRET_KEY` |
| Public endpoints | Documented + rate limited |
| CORS | Configurable via env |
| Log sanitization | Masking utils present |

## Outdated / removed

- Stale Docker workflow tag `4.2.0` on default branch (replaced by `4.2.1`)
- Hardcoded version in auth test

## Remaining technical debt

See CHANGELOG and sprint deliverables in PR #27.
