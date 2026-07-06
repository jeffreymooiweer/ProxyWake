# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.1.x   | :white_check_mark: |
| 3.0.x   | :white_check_mark: |
| < 3.0   | :x:                |

## Reporting a Vulnerability

**Please do not open public GitHub issues for security vulnerabilities.**

If you discover a security issue in ProxyWake, report it responsibly:

1. Email the maintainer via GitHub (private security advisory) or open a **private** security advisory on:
   https://github.com/jeffreymooiweer/ProxyWake/security/advisories/new

2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Impact assessment
   - Suggested fix (if any)

3. Allow reasonable time for a fix before public disclosure.

## Security Considerations

### Authentication

- Set `PROXYWAKE_PASSWORD` in production.
- Rotate the API key periodically via Settings.
- Do not expose ProxyWake directly to the internet without HTTPS (use NPM with Let's Encrypt).

### Public Endpoints

The following endpoints are intentionally unauthenticated:

| Endpoint | Purpose | Risk mitigation |
|----------|---------|-----------------|
| `GET /api/health` | Health checks | No sensitive data |
| `GET /api/metrics` | Prometheus metrics | Aggregate counts only |
| `GET /api/public/status/<domain>` | Waiting page status | Domain must exist in DB |
| `POST /api/public/wake/<domain>` | Waiting page wake | Rate limited (30/min) |

Review these endpoints when deploying in untrusted networks.

### Network

- Wake-on-LAN requires `NET_RAW` capability in Docker.
- For Wake-on-WAN, use Tailscale/WireGuard instead of opening ports.
- Network scan (`POST /api/scan`) requires authentication and is rate limited.

### Data Storage

- API keys and password hashes are stored in `PROXYWAKE_DATA_DIR`.
- Back up this volume regularly.
- Do not commit `.env` files or `password.hash` to version control.

## Hardening Checklist

- [ ] Set a strong `PROXYWAKE_PASSWORD`
- [ ] Configure `PROXYWAKE_ALLOWED_ORIGINS` for CORS
- [ ] Set a fixed `PROXYWAKE_SECRET_KEY` for session stability
- [ ] Place ProxyWake behind a reverse proxy with HTTPS
- [ ] Restrict network access to the management UI
- [ ] Keep Docker images updated
