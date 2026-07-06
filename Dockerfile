# syntax=docker/dockerfile:1

# ── Frontend build ──────────────────────────────────────────────────────────
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --prefer-offline --no-audit

COPY frontend/ ./
RUN npm run build

# ── Runtime ─────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="ProxyWake" \
      org.opencontainers.image.description="Wake-on-LAN platform for Nginx Proxy Manager" \
      org.opencontainers.image.source="https://github.com/jeffreymooiweer/ProxyWake" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="4.1.0"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        iputils-ping \
        curl \
        openssh-client \
        sshpass \
        ipmitool \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 proxywake \
    && useradd --uid 1000 --gid proxywake --shell /bin/sh --create-home proxywake

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend
COPY --from=frontend-build /app/frontend/build ./frontend/build

RUN chmod +x /app/backend/entrypoint.sh \
    && mkdir -p /app/backend/data \
    && chown -R proxywake:proxywake /app

ENV PROXYWAKE_DATA_DIR=/app/backend/data \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 5001

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -fsS http://127.0.0.1:5001/api/health || exit 1

USER proxywake

CMD ["/app/backend/entrypoint.sh"]
