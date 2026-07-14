# Django REST Framework Best Practices

**Version 1.0.0**  
_Gian López_  
_January 2026_

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring _Django_ and _Django REST Framework_ codebases. Humans  
> may also find it useful, but guidance here is optimized for automation  
> and consistency by AI-assisted workflows.

---

## Abstract

A comprehensive configuration for _Django_ and _Django REST Framework_ development, optimized for AI-driven workflows. This setup defines strict architectural patterns for service-layer separation, _ORM_ query optimization (N+1 prevention), and robust data validation protocols. It provides a structured framework for automated code generation, refactoring, and unit testing, ensuring high-performance back-end systems through precise technical constraints.

---

## Table of Contents

1. [Architecture & Structure](#1-architecture--structure) — `HIGH`
   - 1.1 [Modular App Structure & Configuration](#11-modular-app-structure--configuration)
2. [Configuration & DevOps](#2-configuration--devops) — `HIGH`
   - 2.1 [Modular Settings Configuration](#21-modular-settings-configuration)
   - 2.2 [Deployment Topology & Containerization](#22-deployment-topology--containerization)
   - 2.3 [Environment & Dependency Segregation](#23-environment--dependency-segregation)
3. [ORM & Database](#3-orm--database) — `HIGH`
   - 3.1 [Standard Model Definition](#31-standard-model-definition)
4. [API & Serialization](#4-api--serialization) — `HIGH`
   - 4.1 [Serializer Definition, Naming & Delegation](#41-serializer-definition-naming--delegation)
   - 4.2 [View Selection, Typing & Registration](#42-view-selection-typing--registration)

---

## 1. Architecture & Structure

### 1.1 Modular App Structure & Configuration

**Impact (HIGH):** Ensures scalability and organization by grouping applications under an `apps/` directory and converting monolithic `models.py` and `views.py` into _Python_ packages. This facilitates better separation of concerns and cleaner imports via the _Facade_ pattern.

**Guidelines:**

1.  **Directory Location:** All _Django_ apps must reside inside the project's `apps/` folder, not the project root
2.  **Package Conversion:** `models`, `serializers`, and `views` must be directories (packages) containing an `__init__.py`
3.  **Public API:** Use `__init__.py` to explicitly export only the public classes/functions
4.  **File Cleanup:** `admin.py` and `tests.py` should be cleared or reset upon creation; `urls.py` must be created if missing
5.  **App Configuration:** The `apps.py` file must use the full path in `name` (e.g., `apps.users`) and include a translatable `verbose_name`

**Incorrect (Flat structure & Default Config):**

```plaintext
./users/
├── apps.py (missing)
├── models.py
└── views.py
```

```python
# ./apps/users/apps.py

from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"  # Missing namespace
```

**Correct (Modular Structure & Custom Config):**

```plaintext
./apps/
└── users/
    ├── apps.py
    ├── models/
    │   ├── __init__.py
    │   └── user.py
    ├── serializers/
    │   └── __init__.py
    ├── urls.py
    └── views/
        └── __init__.py
```

```python
# ./apps/users/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"  # Correct namespace
    verbose_name = _("Users")  # Translatable name
```

```python
# ./apps/app/models/__init__.py

# Facade pattern: Import internal implementations
from .users import User

# Export only what is public
__all__ = ["User"]
```

Reference: [Django AppConfig Documentation](https://docs.djangoproject.com/en/6.0/ref/applications)

---

## 2. Configuration & DevOps

### 2.1 Modular Settings Configuration

**Impact (MEDIUM):** Splitting settings prevents accidental deployment of insecure configurations (like `DEBUG=True`) to production. It cleanly separates shared logic (database connections, apps) from environment-specific overrides.

**Guidelines:**

1.  **Directory Structure:** Do not use a single `settings.py`. Create a `settings/` package inside the project configuration directory
2.  **File Organization:**
    - `settings.py`: Contains shared configurations (Apps, Middleware, Database connection logic, I18N, Auth)
    - `development.py`: Imports base (`from .settings import *`) and sets `DEBUG = True` and permissive access
    - `production.py`: Imports base (`from .settings import *`) and sets `DEBUG = False` and restricted access
3.  **Path Adjustment:** In `settings.py`, `BASE_DIR` must calculate the parent three times (`.parent.parent.parent`) to compensate for the new subdirectory depth
4.  **Environment Variables:** Sensitive data (`SECRET_KEY`, `DB_PASSWORD`) must be loaded via `os.environ` in the base settings

**Incorrect (Monolithic & Insecure):**

```plaintext
./project/
└── settings.py
```

```python
# ./project/settings.py

# Risk: Forgetting to change this before deployment
DEBUG = True
BASE_DIR = Path(__file__).resolve().parent.parent
```

**Correct (Modular & Environment-Aware):**

```plaintext
./project/
└── settings/
    ├── __init__.py
    ├── development.py
    ├── production.py
    └── settings.py
```

```python
# ./project/settings/settings.py (Base)

import os
from pathlib import Path

# Note: 3 parents to reach root from project/settings/settings.py
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

INSTALLED_APPS = [
    # ... django apps ...
    "apps.users",  # Local apps
]

TIME_ZONE = "America/Bogota"
```

```python
# ./project/settings/development.py

from .settings import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True
```

```python
# ./project/settings/production.py

from .settings import *

DEBUG = False
ALLOWED_HOSTS = [] # Must be set explicitly
```

Reference: [Django Settings](https://docs.djangoproject.com/en/6.0/ref/settings)

### 2.2 Deployment Topology & Containerization

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

#### Execution Reference

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

### 2.3 Environment & Dependency Segregation

**Impact (MEDIUM):** Strict separation ensures production artifacts remain lightweight and secure by excluding development tools. Using distinct virtual environments prevents accidental "pollution" of the production dependency tree during local testing.

**Guidelines:**

1.  **Dual Virtual Environments:** Do not use a generic `.venv`. Create two explicit environments in the project root:
    - `.venv.development`: For local coding, linting, and testing
    - `.venv.production`: To simulate the build process and verify clean installs
2.  **Requirement Files:** Store dependencies in a `requirements/` directory, never in a root `./requirements.txt`
    - `./requirements/production.txt`: Only libraries required for the application to run
    - `./requirements/development.txt`: Libraries for type checking (stubs), formatting, and debugging
3.  **Contextual Installation:** Before installing a package, explicitly decide: "Is this needed for the app logic or for the developer?" Install into the corresponding environment/file
4.  **Standard Development Stack:** Development requirements must include type stubs for strict typing (e.g., `django-stubs`, `djangorestframework-stubs`)

**Incorrect (Mixed environment & Monolithic file):**

```bash
# Bad: Generic environment
$ python3 -m venv .venv

# Bad: Root file mixing concerns
$ cat ./project/requirements.txt
```

**Correct (Segregated Environments & Files):**

```bash
# 1. Create Production Environment
$ python3 -m venv .venv.production

# 2. Create Development Environment
$ python3 -m venv .venv.development
```

**File Structure:**

```plaintext
./project/
├── .venv.development/
├── .venv.production/
└── requirements/
    ├── development.txt
    └── production.txt
```

**Content Examples:**

```plaintext
# ./requirements/production.txt (example)

Django==5.2.6
djangorestframework==3.16.1
gunicorn==23.0.0
psycopg2-binary==2.9.10
```

```plaintext
# ./requirements/development.txt (example)

certifi==2025.8.3
charset-normalizer==3.4.3
django-stubs==5.2.5
django-stubs-ext==5.2.5
djangorestframework-stubs==3.16.3
idna==3.10
requests==2.32.5
types-PyYAML==6.0.12.20250915
types-requests==2.32.4.20250913
typing_extensions==4.15.0
urllib3==2.5.0
```

Reference: [Python venv Documentation](https://docs.python.org/3/library/venv.html)

---

## 3. ORM & Database

### 3.1 Standard Model Definition

**Impact (HIGH):** Consistency in model definition drastically reduces cognitive load when navigating the data layer. Enforcing "one model per file" prevents massive `models.py` files, while strict ordering and typing ensure predictable and self-documenting code.

**Guidelines:**

1.  **File Isolation:** Each model must reside in its own file within the `models/` package (e.g., `./apps/users/models/user.py`)
2.  **Field Definition:** The first argument of every non-relational field must be the translated `verbose_name` (using `gettext_lazy`)
3.  **Class Structure:** Adhere to the following order inside the class:
    1.  `Choices` (Enums/TextChoices)
    2.  Database Fields
    3.  Custom Managers (`objects = ...`)
    4.  `class Meta`
    5.  Properties / Custom Methods
    6.  `def __str__(self):`
4.  **Metadata:**
    - Explicitly define `verbose_name` and `verbose_name_plural`
    - Explicitly define `db_table` (conditional) for models with multi-word names (e.g., `UserAsset`), you must explicitly define `db_table` to enforce _snake_case_ separation (e.g., `users_user_asset`). For single-word models, the default behavior is acceptable
5.  **Typing:** Add type hints only when they add real value to the reader. Omit return annotations on dunder methods (`__str__`, `__repr__`) since their contract is defined by the protocol, and on properties/methods where the return expression is self-documenting

**Incorrect (Mixed structure, missing translations/types):**

```python
# ./apps/users/models/asset.py

class UserAsset(models.Model):
    # Implicit table: "users_userasset" (Hard to read)
    class Meta:
        verbose_name = _("user asset")
        verbose_name_plural = _("user assets")
        # Missing `db_table` -> Data inconsistency in naming convention
```

**Correct (Conditional logic applied)**

```python
# ./apps/users/models/user.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.managers import UserManager

class User(AbstractUser):
    # 1. Choices
    class Role(models.TextChoices):
        ADMIN = "admin", _("Admin")
        CUSTOMER = "customer", _("Customer")

    # 2. Fields
    phone = models.CharField(_("phone"), max_length=20, blank=True)
    role = models.CharField(_("role"), max_length=10, choices=Role.choices, default=Role.CUSTOMER)

    # 3. Managers
    objects = UserManager()

    # 4. Meta
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    # 5. Methods/Properties
    @property
    def is_premium(self):
        return self.role == self.Role.CUSTOMER

    # 6. String representation
    def __str__(self):
        return self.email or self.username
```

Reference: [Django Model Meta Options](https://docs.djangoproject.com/en/6.0/ref/models/options)

---

## 4. API & Serialization

### 4.1 Serializer Definition, Naming & Delegation

**Impact (HIGH):** Separating serializers by action (Read vs. Write) prevents leaky abstractions. Using a delegation mixin for write operations ensures that responses contain rich data without code duplication or manual `to_representation` overrides.

**Guidelines:**

1.  **Conditional Imports:**
    - **Simple:** If inheriting _only_ from `ModelSerializer` with no custom fields, import `ModelSerializer` directly
    - **Complex:** If using custom fields (e.g., `CharField`), import the `serializers` module and use `serializers.ModelSerializer`
2.  **Naming Convention:** Use specific suffixes:
    - `*ListSerializer`: Optimized for collections
    - `*RetrieveSerializer`: Detailed single-object read
    - `*CreateSerializer` / `*UpdateSerializer`: For write operations
3.  **Response Delegation (Write Operations):**
    - When a write serializer (`Create`/`Update`) needs to return a different representation than its input (e.g., return the full `UserRetrieveSerializer` structure after creating a user), must inherit from `DelegateRepresentationMixin`
    - Define the target serializer in `Meta.representation`
4.  **Field Declaration:**
    - `Meta.fields` must always be an explicit list `[...]`. Never use `"__all__"` or any other shorthand
    - The order of fields in the list must match the order in which they are defined in the model

**Incorrect (Implicit fields or arbitrary order):**

```python
class UserRetrieveSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"  # Bad: Exposes unintended fields; order is non-deterministic
```

```python
class UserRetrieveSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "id", "phone"]  # Bad: Order does not match model definition
```

**Correct (Explicit list ordered by model definition):**

```python
# Model definition order: id, phone, name, role
class UserRetrieveSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone", "name", "role"]  # Matches model field order
```

**Incorrect (Manual override or returning incomplete data):**

```python
# Bad: Manually overriding to_representation (Repeated logic)
class UserCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["name", "code"]

    # This logic is fragile and repetitive across the project
    def to_representation(self, instance):
        from .user_retrieve_serializer import UserRetrieveSerializer
        return UserRetrieveSerializer(instance, context=self.context).data
```

**Correct (Mixin Delegation):**

```python
from rest_framework import serializers

from apps.common.mixins import DelegateRepresentationMixin
from apps.users.models import User
from apps.users.serializers.user_retrieve_serializer import UserRetrieveSerializer

# Inherits from Mixin + Serializer
class UserCreateSerializer(DelegateRepresentationMixin, serializers.ModelSerializer):
    code = serializers.CharField(max_length=6)

    class Meta:
        model = User
        fields = ["identification", "name", "phone", "sid", "code"]
        # Magic: Automatically transforms the response using the Retrieve serializer
        representation = UserRetrieveSerializer
```

Reference: [DRF Customizing Serialization](https://www.google.com/search?q=https://www.django-rest-framework.org/api-guide/serializers/%23customizing-serialization)

### 4.2 View Selection, Typing & Registration

**Impact (MEDIUM):** Standardization prevents boilerplate code. Using generic views reduces maintenance. Purposeful typing in _APIViews_ improves IDE support and communicates intent. Explicit declaration of `authentication_classes` and `permission_classes` prevents relying on implicit global defaults, making the security contract of every view self-documenting. Module-level imports in `urls.py` prevent naming conflicts and circular dependencies.

**Guidelines:**

1.  **Selection Criteria:**
    - **_Generic Views_:** Must be the default choice for standard _CRUD_ operations (e.g., `ListCreateAPIView`)
    - **_APIView_:** Use only when standard Generics are insufficient (e.g., complex business logic, Auth, RPC)
2.  **Typing (_APIView_):**
    - Always type-hint `request` as `Request` — it adds real value by enabling IDE autocompletion and making the parameter contract explicit
    - Omit return type annotations when the `return` statement is self-documenting (e.g., `return Response(...)`); add them only when branching logic makes the return type non-obvious
    - Use explicit imports (e.g., `from rest_framework.request import Request`)
3.  **URL Registration:**
    - In `urls.py`, import the views module relatively: `from . import views`
    - Register paths referencing the module: `views.MyClassName.as_view()`
4.  **Security Declaration:**
    - Every view (_APIView_, _Generic View_, or _ViewSet_) must explicitly declare both `authentication_classes` and `permission_classes`
    - When a view requires no authentication or permissions, declare empty lists explicitly — never rely on implicit global defaults
    - The two attributes must be declared together, separated from `queryset` and `serializer_class` by a blank line

**Incorrect (Implicit security — relies on global defaults):**

```python
# ./apps/users/views/login.py

class UserLoginAPIView(APIView):
    # Bad: No authentication_classes or permission_classes declared.
    # Security behavior depends entirely on DEFAULT_AUTHENTICATION_CLASSES
    # and DEFAULT_PERMISSION_CLASSES in settings — invisible to the reader.
    def post(self, request: Request):
        return Response({})
```

```python
# ./apps/users/views/profile.py

class UserProfileListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserRetrieveSerializer
    # Bad: Missing explicit security declaration on a Generic View
```

**Correct (Explicit security on all view types):**

```python
# ./apps/users/views/login.py — APIView with no auth required

from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

class UserLoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request: Request):
        return Response({})
```

```python
# ./apps/users/views/profile.py — Generic View with auth required

from rest_framework.generics import ListAPIView

from apps.users.models import User
from apps.users.serializers import UserRetrieveSerializer

class UserProfileListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserRetrieveSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
```

**Incorrect (Direct imports & Missing Types):**

```python
# ./apps/users/urls.py

from .views import UserLoginAPIView # Potential name conflict

urlpatterns = [
    path("login/", UserLoginAPIView.as_view()),
]
```

```python
# ./apps/users/views/login.py

class UserLoginAPIView(APIView):
    # Missing request type hint — loses IDE autocompletion and parameter clarity
    def post(self, request):
        return Response({})
```

**Correct (Context-Aware Selection & Module Import):**

```python
# ./apps/users/views/login.py

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from apps.users.serializers import UserLoginSerializer

class UserLoginAPIView(APIView):
    def post(self, request: Request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # ... logic ...
        return Response({"foo": "bar"})
```

```python
# ./apps/users/urls.py

from django.urls import path

# Standard: Import the module, not the class
from . import views

urlpatterns = [
    path("login/", views.UserLoginAPIView.as_view()),
]
```

Reference: [Django REST Framework Class-based Views](https://www.django-rest-framework.org/api-guide/views)
