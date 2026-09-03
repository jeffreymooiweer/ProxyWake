# ProxyWake documentation

ProxyWake wakes sleeping computers on your network the moment someone tries to use them through your reverse proxy. These guides take you from installation to a working setup, and help when something goes wrong.

**New here?** Start with the [Quick Start](quick-start.md) — it walks you through everything in order.

## Install

| Guide | What it covers |
|-------|----------------|
| [Quick Start](quick-start.md) | Install ProxyWake, add your first device, connect your proxy |
| [Docker](docker.md) | Docker run / Compose, networking (important for Wake-on-LAN), volumes, upgrades |
| [Unraid](unraid.md) | Installing through Community Applications or the Docker tab |
| [Configuration](configuration.md) | Every environment variable and setting explained |

## Connect your reverse proxy

| Guide | What it covers |
|-------|----------------|
| [How wake-on-access works](reverse-proxy.md) | The idea behind it, in plain terms |
| [Nginx Proxy Manager](examples/nginx-proxy-manager.md) | Copy-paste setup for NPM |
| [Traefik](examples/traefik.md) | Setup with Traefik's built-in middleware |
| [Caddy](examples/caddy.md) | Setup with Caddy's built-in directives |
| [Home Assistant](examples/home-assistant.md) | Wake from Home Assistant, or let ProxyWake trigger Home Assistant |

## Help

| Guide | What it covers |
|-------|----------------|
| [Troubleshooting](troubleshooting.md) | "It does not wake" and other common problems, with fixes |
| [Security](security.md) | Passwords, API keys, what is public and what is not |
| [Migration](migration.md) | Upgrading safely between versions |
| [API](api.md) | Using the REST API yourself |

## Project

- [Changelog](../CHANGELOG.md)
- [Contributing](../CONTRIBUTING.md) — development setup and pull requests
- [Security policy](../SECURITY.md) — reporting vulnerabilities
