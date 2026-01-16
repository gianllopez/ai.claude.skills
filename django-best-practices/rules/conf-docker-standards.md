---
title: Docker & Container Standards
impact: MEDIUM
description: Enforces usage of slim base images, reverse-domain naming conventions for containers/volumes, and distinct commands for Dev/Prod environments.
tags: docker, devops, configuration, naming-convention
---

## Docker & Container Standards

**Impact (MEDIUM):** Optimized images (slim) reduce build time and attack surface. Reverse-domain naming (`com.org.project.service`) prevents collisions on shared hosts. Distinct entry commands ensure the correct application server runs in each environment.

**Guidelines:**

1.  **Base Image:** Always use Python `slim` variants (e.g., `python:3.13-slim`) to minimize image size.
2.  **Dockerfile Optimization:**
    * Set `PYTHONUNBUFFERED=1` and `PYTHONDONTWRITEBYTECODE=1`.
    * Copy and install `requirements` before copying the source code to leverage *Docker* layer caching.
    * Use strict paths (e.g., `requirements/production.txt`).
3.  **Naming Convention (Reverse Domain):**
    * **Container Names:** `com.example.project.service` (e.g., `com.example.project.api`).
    * **Volume Names:** `com-example-project-service-data` (kebab-case variant of reverse domain).
    * **Image Names:** `com.example.project.service`.
4.  **Environment Segregation:**
    * **Development:** Use `python manage.py runserver 0.0.0.0:8000` and `settings.development`.
    * **Production:** Use `gunicorn project.wsgi --bind=0.0.0.0:8000` and `settings.production`.
5.  **Ignore Files:** Strict `.dockerignore` including `.venv`, `.env`, `__pycache__`, and system files.

**Incorrect (Generic names, fat images, cache breaking):**

```dockerfile
# Bad: Full image is heavy
FROM python:3.13

# Bad: Copies code before requirements (breaks cache on code change)
COPY . .
RUN pip install -r requirements.txt
```

```yaml
# compose.yml
services:
  database:
    image: postgres
    container_name: db # Too generic, collision prone
    volumes:
      - data:/var/lib/postgresql/data
```

**Correct (Slim, Cached, Reverse Domain, Env-Aware):**

```dockerfile
# Dockerfile

# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Layer caching: Requirements first
COPY requirements/production.txt requirements/production.txt

RUN pip install -r requirements/production.txt

COPY . .
```

```yaml
# compose.yml

services:
  database:
    image: postgres:17.0-alpine
    restart: always
    ports:
      - ${DATABASE_PORT}:5432
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
    ports:
      - ${PORT}:8000
    volumes:
      - .:/usr/src/app
    environment:
      # django
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - DJANGO_SETTINGS_MODULE=project.settings.development
      # database
      - DATABASE_HOST=database
      - DATABASE_PORT=${DATABASE_PORT}
      - DATABASE_NAME=${DATABASE_NAME}
      - DATABASE_USER=${DATABASE_USER}
      - DATABASE_PASSWORD=${DATABASE_PASSWORD}
    depends_on:
      - database
    command: python manage.py runserver 0.0.0.0:8000

volumes:
  database:
    name: com-example-project-database
```

```yaml
# compose.production.yml

services:
  app:
    environment:
      - DJANGO_SETTINGS_MODULE=project.settings.production
    command: gunicorn project.wsgi --bind=0.0.0.0:8000
```

```plaintext
# .dockerignore

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

**Development (Default):**    
```bash
$ docker compose up -d --build
```
    
**Production (Override):**
Combines the base config with production overrides.
    
```bash
$ docker compose -f compose.yml -f compose.prod.yml up -d --build    
```

Reference: [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices)
