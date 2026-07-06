# GitHub Repository Metadata Checklist

Manual settings to configure on GitHub for a professional open-source presence. **Do not automate these from the repository** — apply them in GitHub Settings.

## Repository description

**Suggested:**

> Self-hosted Wake-on-LAN platform for Nginx Proxy Manager, Traefik, and Caddy — wake sleeping devices when accessed through a reverse proxy.

## Topics

Suggested topics (add all that apply):

`wake-on-lan`, `wol`, `docker`, `self-hosted`, `homelab`, `nginx-proxy-manager`, `traefik`, `caddy`, `home-assistant`, `flask`, `react`, `unraid`

## Website

Set to documentation entry point:

`https://github.com/jeffreymooiweer/ProxyWake/tree/main/docs`

Or project homepage if you publish docs elsewhere later.

## Social preview image

Upload `docs/assets/banner.svg` (export as 1280×640 PNG) or a dashboard screenshot for the Open Graph image under **Settings → General → Social preview**.

## Releases

| Setting | Recommendation |
|---------|----------------|
| Tag format | `v4.2.2` (semver with `v` prefix) |
| Title | `ProxyWake v4.2.2` |
| Body | Copy from [CHANGELOG.md](../CHANGELOG.md) section |
| Assets | Attach `docker pull jeffersonmouze/proxywake:4.2.2` instructions |

## Labels

Suggested default labels:

| Label | Color | Use |
|-------|-------|-----|
| `bug` | red | Defects |
| `enhancement` | blue | Features |
| `documentation` | green | Docs only |
| `good first issue` | purple | Starter tasks |
| `help wanted` | yellow | Community help |
| `security` | dark red | Security (link to private advisory) |

## Discussions

Enable **Discussions** for:

- Q&A (installation, NPM setup)
- Ideas (feature brainstorming separate from issues)

Categories: General, Ideas, Q&A, Show and tell.

## Projects

Optional GitHub Project board:

- Columns: Backlog → In progress → Review → Done
- Track roadmap items for v4.3 / v4.4 / v5.0

## Security settings

- Enable **Private vulnerability reporting** (already linked in SECURITY.md)
- Enable **Dependabot alerts** and **security updates**
- Consider **Code scanning** (CodeQL workflow)

## Branch protection (`main`)

Recommended rules:

- Require pull request before merging
- Require status checks: `Backend Tests`, `Frontend Build`
- Require branches to be up to date
- Do not allow force push
- Restrict who can push (maintainers only)

## Actions secrets

Required for Docker publish workflow:

- `DOCKER_USERNAME`
- `DOCKER_PASSWORD` (access token)

## About box

- ☑ Releases
- ☑ Packages (if publishing to GHCR later)
- License: MIT
