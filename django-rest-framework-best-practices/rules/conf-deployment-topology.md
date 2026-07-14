---
title: Deployment Topology & Containerization
impact: HIGH
description: Defines the end-to-end production deployment method — layered Docker Compose overlays, a Caddy reverse proxy, a hardened non-root image with a release entrypoint, gunicorn, and host-level scheduled operations via systemd timers.
tags: configuration, docker, deployment, ops
---

## Deployment Topology & Containerization

**Impact (HIGH):** A single, opinionated deployment method removes ambiguity between environments and shrinks the production attack surface. Layered _Compose_ files keep one source of truth per environment, a non-root image with a release entrypoint guarantees migrations and static collection run before traffic is served, and host-level timers make backups and reconciliation observable instead of ad hoc.

The stack is _Docker Compose_ with per-environment overlays, fronted by a _Caddy_ reverse proxy (automatic HTTPS), running the application under _gunicorn_ as a non-root user, with release tasks in an entrypoint and recurring host jobs in _systemd_ timers.

**Guidelines:**

1.  **Layered _Compose_ (base + overlays):**
    - `compose.yml`: the **environment-agnostic base** (services, named volumes, reverse-domain container/image names, secrets injected via `${VAR}`). Never hardcode a command or `DJANGO_SETTINGS_MODULE` here
    - `compose.override.yml`: the **development** overlay, loaded automatically by `docker compose`. Bind-mounts source, exposes ports, sets `settings.development`, runs `runserver`, and mounts seed SQL
    - `compose.prod.yml`: the **production** overlay, passed **explicitly** with `-f`. Adds `restart: always`, log rotation (a shared `x-logging` anchor), `settings.production`, and the `caddy` service
2.  **Base Image & Hardened Dockerfile:**
    - Use _Python_ `slim` (e.g. `python:3.13-slim`); set `PYTHONUNBUFFERED=1` and `PYTHONDONTWRITEBYTECODE=1`
    - Copy `requirements/production.txt` and install **before** copying source to preserve layer caching. Install OS build/runtime deps (e.g. `gettext`) in a single `apt-get` layer and clean `/var/lib/apt/lists`
    - Create and switch to a **non-root** system user; `chown` the app tree and its home to that user
    - `ENTRYPOINT` runs the release script; `CMD` runs _gunicorn_
3.  **Reverse-Domain Naming:** Containers and images `com.example.project.service` (e.g. `com.example.project.api`); named volumes use the kebab-case variant `com-example-project-service`
4.  **Release Entrypoint (`deploy/scripts/entrypoint.sh`):** Wait for the database, then run `migrate --noinput`, `createcachetable`, and `collectstatic --noinput`, and finally `exec "$@"` to hand off to _gunicorn_. Static files are served by _WhiteNoise_ inside _gunicorn_, not by the proxy
5.  **Reverse Proxy (_Caddy_):** A `Caddyfile` terminates TLS (automatic HTTPS), enables `zstd`/`gzip`, caps the request body, and `reverse_proxy`es to the app service. The proxy exists **only** in the production overlay and owns ports `80`/`443`
6.  **Scheduled Host Operations (_systemd_, not cron):** Recurring jobs live in `deploy/systemd/` as `oneshot` `*.service` + `*.timer` pairs (`After`/`Requires=docker.service`), each pinging a **dead-man's-switch** monitor via `ExecStartPost`. Units carry `<path>`/`<user>`/`<monitor>` placeholders to be filled on the host. The portable job every deployment should have is the **offsite database backup** (`pg_dump` → `gzip` → `scp`, with local retention). Any project-specific recurring task (e.g. a data-reconciliation management command) reuses the same `service` + `timer` + monitor pattern — but ships only when that project actually needs it
7.  **Database Seeding:** Seed/init SQL is mounted into `/docker-entrypoint-initdb.d/`; rely on _Postgres_'s **alphabetical execution order** (e.g. `00-init-role.sql` before `10-database.sql`) for ordering
8.  **Production Django Hardening (behind the proxy):** In `settings/production.py`, trust the proxy and enforce TLS — `SECURE_PROXY_SSL_HEADER`, `USE_X_FORWARDED_HOST`, `SECURE_SSL_REDIRECT`, secure cookies, HSTS, and explicit `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`/`CORS_ALLOWED_ORIGINS`. See `conf-settings-structure` for the modular split itself
9.  **Ignore Files:** A strict `.dockerignore` excludes `.venv.*`, `.env`, `__pycache__`, and system/editor files

**Incorrect (single file, root user, no release step, generic names):**

```dockerfile
# ./Dockerfile

# Bad: fat image, code before requirements (breaks cache), runs as root
FROM python:3.13
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "project.wsgi"]
```

```yaml
# ./compose.yml

services:
  db: # Bad: generic name, collision prone
    image: postgres
  api:
    build: .
    command: python manage.py runserver 0.0.0.0:8000 # Bad: dev command baked into base
```

**Correct (hardened image, layered overlays, proxy, entrypoint):**

```dockerfile
# ./Dockerfile

# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && \
    apt-get install --no-install-recommends --yes gettext && \
    rm -rf /var/lib/apt/lists/*

# Layer caching: requirements before source
COPY requirements/production.txt requirements/production.txt

RUN pip install --no-cache-dir -r requirements/production.txt

COPY . .

RUN addgroup --system nonroot && \
    adduser --system --ingroup nonroot --home /home/nonroot nonroot && \
    mkdir -p /usr/src/app/staticfiles && \
    chmod +x deploy/scripts/entrypoint.sh && \
    chown -R nonroot:nonroot /usr/src/app /home/nonroot

USER nonroot

ENTRYPOINT ["./deploy/scripts/entrypoint.sh"]

CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "4"]
```

```yaml
# ./compose.yml (environment-agnostic base)

services:
  database:
    image: postgres:17.0-alpine
    restart: always
    volumes:
      - database:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${DATABASE_NAME}
      - POSTGRES_USER=${DATABASE_USER}
      - POSTGRES_PASSWORD=${DATABASE_PASSWORD}
    container_name: com.example.project.database

  api:
    build: .
    image: com.example.project.api
    container_name: com.example.project.api
    environment:
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - DATABASE_HOST=database
      - DATABASE_PORT=5432
      - DATABASE_NAME=${DATABASE_NAME}
      - DATABASE_USER=${DATABASE_USER}
      - DATABASE_PASSWORD=${DATABASE_PASSWORD}
    depends_on:
      - database

volumes:
  database:
    name: com-example-project-database
```

```yaml
# ./compose.override.yml (development, auto-loaded)

services:
  database:
    ports:
      - ${DATABASE_PORT}:5432
    volumes:
      - ./deploy/postgres/init-role.sql:/docker-entrypoint-initdb.d/00-init-role.sql:ro
      - ./database.txt:/docker-entrypoint-initdb.d/10-database.sql:ro

  api:
    volumes:
      - .:/usr/src/app
    ports:
      - ${PORT}:8000
    environment:
      - DJANGO_SETTINGS_MODULE=project.settings.development
    command: python manage.py runserver 0.0.0.0:8000
```

```yaml
# ./compose.prod.yml (production, explicit via -f)

x-logging: &logging
  driver: json-file
  options:
    max-size: '10m'
    max-file: '3'

services:
  api:
    restart: always
    logging: *logging
    environment:
      - DJANGO_SETTINGS_MODULE=project.settings.production

  database:
    logging: *logging

  caddy:
    image: caddy:2-alpine
    restart: always
    logging: *logging
    ports:
      - 80:80
      - 443:443
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - api
    container_name: com.example.project.caddy

volumes:
  caddy_data:
    name: com-example-project-caddy-data
  caddy_config:
    name: com-example-project-caddy-config
```

```plaintext
# ./Caddyfile

api.example.com {
    encode zstd gzip

    request_body {
        max_size 4MB
    }

    reverse_proxy api:8000
}
```

```bash
# ./deploy/scripts/entrypoint.sh

#!/usr/bin/env bash

set -euo pipefail

echo "[entrypoint] Waiting for the database to become available"

until python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()" >/dev/null 2>&1; do
  echo "[entrypoint] Database unavailable, retrying in 5s"
  sleep 5
done

python manage.py migrate --noinput
python manage.py createcachetable
python manage.py collectstatic --noinput

echo "[entrypoint] Startup tasks completed, handing off to: \`$*\`"

exec "$@"
```

```ini
# ./deploy/systemd/backup.service
# Replace <path> (project root on host), <user>/<group>, and <monitor> (push address).

[Unit]
Description=@com.example.project/backup
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
User=<user>
Group=<group>
WorkingDirectory=<path>
ExecStart=<path>/deploy/scripts/backup.sh
ExecStartPost=/usr/bin/curl -fsS -m 10 --retry 3 <monitor>
```

```ini
# ./deploy/systemd/backup.timer

[Unit]
Description=@com.example.project/backup

[Timer]
OnCalendar=*-*-* 00:00:00 America/Bogota
Persistent=true

[Install]
WantedBy=timers.target
```

```python
# ./project/settings/production.py (proxy-aware hardening; see conf-settings-structure)

from .settings import *

DEBUG = False
ALLOWED_HOSTS = ["api.example.com"]

# Trust the reverse proxy and force HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

CSRF_TRUSTED_ORIGINS = ["https://api.example.com"]
CORS_ALLOWED_ORIGINS = ["https://api.example.com"]
```

```plaintext
# ./.dockerignore

# environment
.venv.*/
.env

# os
.DS_Store

# database
*.sqlite3

# python
__pycache__/

# editor
.marks.json
```

### Execution Reference

**Development (override applied automatically):**

```bash
$ docker compose up -d --build
```

**Production (base + explicit production overlay):**

```bash
$ docker compose -f compose.yml -f compose.prod.yml up -d --build
```

**Enable a scheduled host job (on the server):**

```bash
$ sudo systemctl enable --now backup.timer
```

Reference: [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices) · [Caddy Reverse Proxy](https://caddyserver.com/docs/quick-starts/reverse-proxy) · [systemd Timers](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html) · [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
