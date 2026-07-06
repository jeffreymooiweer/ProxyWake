# GitHub repository metadata

Checklist for maintainers — apply these in GitHub Settings, not from the repository.

## Repository description

> Self-hosted Wake-on-LAN platform for Nginx Proxy Manager, Traefik, and Caddy — wake sleeping devices when accessed through a reverse proxy.

## Topics

`wake-on-lan`, `wol`, `docker`, `self-hosted`, `homelab`, `nginx-proxy-manager`, `traefik`, `caddy`, `home-assistant`, `flask`, `react`, `unraid`

## Website

`https://github.com/jeffreymooiweer/ProxyWake/tree/main/docs`

## Social preview

Upload `docs/assets/banner.png` or a dashboard screenshot under **Settings → General → Social preview**.

## Releases

| Setting | Recommendation |
|---------|----------------|
| Tag format | `v4.2.2` (semver with `v` prefix) |
| Title | `ProxyWake v4.2.2` |
| Body | Copy from [CHANGELOG.md](../CHANGELOG.md) |

## Branch protection (`main`)

- Require pull request before merging
- Require status checks: `Backend Tests`, `Frontend Build`
- Do not allow force push

## Actions secrets (Docker publish)

- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
