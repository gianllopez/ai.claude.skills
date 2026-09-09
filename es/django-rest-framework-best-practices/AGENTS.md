# Buenas prácticas de Django REST Framework

**Versión 1.3.0**  
_Gian López_  
_Enero de 2026_

> **Nota:**  
> Este documento está dirigido principalmente a agentes y LLMs que mantienen,  
> generan o refactorizan bases de código de _Django_ y _Django REST Framework_. Las personas  
> también pueden encontrarlo útil, pero la guía está optimizada para la  
> automatización y la consistencia en flujos asistidos por IA.

---

## Resumen

Una configuración integral para el desarrollo con _Django_ y _Django REST Framework_, optimizada para flujos de trabajo impulsados por IA. Este montaje define patrones arquitectónicos estrictos para la separación de la capa de servicio, la optimización de consultas del _ORM_ (prevención de N+1) y protocolos robustos de validación de datos. Aporta un marco estructurado para la generación automatizada de código, la refactorización y las pruebas unitarias, garantizando sistemas de back-end de alto rendimiento mediante restricciones técnicas precisas.

---

## Tabla de contenidos

1. [Arquitectura y estructura](#1-arquitectura-y-estructura) — `HIGH`
   - [1.1 Estructura y configuración modular de aplicaciones](#11-estructura-y-configuración-modular-de-aplicaciones)
2. [Configuración y DevOps](#2-configuración-y-devops) — `HIGH`
   - [2.1 Configuración modular de ajustes](#21-configuración-modular-de-ajustes)
   - [2.2 Topología de despliegue y contenerización](#22-topología-de-despliegue-y-contenerización)
   - [2.3 Segregación de entorno y dependencias](#23-segregación-de-entorno-y-dependencias)
3. [ORM y base de datos](#3-orm-y-base-de-datos) — `HIGH`
   - [3.1 Definición estándar de modelos](#31-definición-estándar-de-modelos)
4. [API y serialización](#4-api-y-serialización) — `HIGH`
   - [4.1 Definición, nomenclatura y delegación de serializadores](#41-definición-nomenclatura-y-delegación-de-serializadores)
   - [4.2 Selección de vistas, tipado y seguridad](#42-selección-de-vistas-tipado-y-seguridad)
   - [4.3 Registro, agrupación y orden de URLs](#43-registro-agrupación-y-orden-de-urls)

---

## 1. Arquitectura y estructura

### 1.1 Estructura y configuración modular de aplicaciones

**Impacto (HIGH):** Garantiza la escalabilidad y la organización agrupando las aplicaciones bajo un directorio `apps/` y convirtiendo los monolíticos `models.py` y `views.py` en paquetes de _Python_. Esto facilita una mejor separación de responsabilidades e imports más limpios mediante el patrón _Facade_.

**Directrices:**

1.  **Ubicación de directorios:** todas las aplicaciones de _Django_ deben residir dentro de la carpeta `apps/` del proyecto, no en la raíz
2.  **Conversión a paquetes:** `models`, `serializers` y `views` deben ser directorios (paquetes) que contengan un `__init__.py`
3.  **API pública:** usa `__init__.py` para exportar explícitamente solo las clases y funciones públicas
4.  **Limpieza de archivos:** `admin.py` y `tests.py` deben vaciarse o reiniciarse al crearlos; `urls.py` debe crearse si falta
5.  **Configuración de la aplicación:** el archivo `apps.py` debe usar la ruta completa en `name` (p. ej., `apps.users`) e incluir un `verbose_name` traducible

**Incorrecto (estructura plana y configuración por defecto):**

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
    name = "users"  # Falta el espacio de nombres
```

**Correcto (estructura modular y configuración personalizada):**

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
    name = "apps.users"  # Espacio de nombres correcto
    verbose_name = _("Users")  # Nombre traducible
```

```python
# ./apps/app/models/__init__.py

# Patrón Facade: importa las implementaciones internas
from .users import User

# Exporta solo lo que es público
__all__ = ["User"]
```

Referencia: [Django AppConfig Documentation](https://docs.djangoproject.com/en/6.0/ref/applications)

---

## 2. Configuración y DevOps

### 2.1 Configuración modular de ajustes

**Impacto (MEDIUM):** Dividir los ajustes evita desplegar accidentalmente configuraciones inseguras (como `DEBUG=True`) a producción. Separa limpiamente la lógica compartida (conexiones de base de datos, aplicaciones) de las sobrescrituras específicas de cada entorno.

**Directrices:**

1.  **Estructura de directorios:** no uses un único `settings.py`. Crea un paquete `settings/` dentro del directorio de configuración del proyecto
2.  **Organización de archivos:**
    - `settings.py`: contiene las configuraciones compartidas (aplicaciones, middleware, lógica de conexión a la base de datos, I18N, autenticación)
    - `development.py`: importa la base (`from .settings import *`) y define `DEBUG = True` y acceso permisivo
    - `production.py`: importa la base (`from .settings import *`) y define `DEBUG = False` y acceso restringido
3.  **Ajuste de rutas:** en `settings.py`, `BASE_DIR` debe calcular el padre tres veces (`.parent.parent.parent`) para compensar la nueva profundidad de subdirectorio
4.  **Variables de entorno:** los datos sensibles (`SECRET_KEY`, `DB_PASSWORD`) deben cargarse mediante `os.environ` en los ajustes base

**Incorrecto (monolítico e inseguro):**

```plaintext
./project/
└── settings.py
```

```python
# ./project/settings.py

# Riesgo: olvidar cambiar esto antes del despliegue
DEBUG = True
BASE_DIR = Path(__file__).resolve().parent.parent
```

**Correcto (modular y consciente del entorno):**

```plaintext
./project/
└── settings/
    ├── __init__.py
    ├── development.py
    ├── production.py
    └── settings.py
```

```python
# ./project/settings/settings.py (base)

import os
from pathlib import Path

# Nota: 3 padres para llegar a la raíz desde project/settings/settings.py
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

INSTALLED_APPS = [
    # ... aplicaciones de django ...
    "apps.users",  # Aplicaciones locales
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
ALLOWED_HOSTS = [] # Debe definirse explícitamente
```

Referencia: [Django Settings](https://docs.djangoproject.com/en/6.0/ref/settings)

### 2.2 Topología de despliegue y contenerización

**Impacto (HIGH):** Un único método de despliegue con criterio propio elimina la ambigüedad entre entornos y reduce la superficie de ataque en producción. Los archivos de _Compose_ en capas mantienen una sola fuente de verdad por entorno, una imagen sin root con un entrypoint de release garantiza que las migraciones y la recolección de estáticos se ejecuten antes de servir tráfico, y los temporizadores a nivel de host hacen que las copias de seguridad y la reconciliación sean observables en lugar de improvisadas.

La pila es _Docker Compose_ con superposiciones por entorno, con un proxy inverso _Caddy_ al frente (HTTPS automático), ejecutando la aplicación bajo _gunicorn_ como usuario sin privilegios, con las tareas de release en un entrypoint y los trabajos recurrentes del host en temporizadores de _systemd_.

**Directrices:**

1.  **_Compose_ en capas (base + superposiciones):**
    - `compose.yml`: la **base agnóstica al entorno** (servicios, volúmenes con nombre, nombres de contenedor/imagen en dominio inverso, secretos inyectados mediante `${VAR}`). Nunca fijes aquí un comando ni un `DJANGO_SETTINGS_MODULE`
    - `compose.override.yml`: la superposición de **desarrollo**, cargada automáticamente por `docker compose`. Monta el código con bind-mount, expone puertos, define `settings.development`, ejecuta `runserver` y monta el SQL de semilla
    - `compose.prod.yml`: la superposición de **producción**, pasada **explícitamente** con `-f`. Añade `restart: always`, rotación de logs (un ancla `x-logging` compartida), `settings.production` y el servicio `caddy`
2.  **Imagen base y Dockerfile endurecido:**
    - Usa _Python_ `slim` (p. ej. `python:3.13-slim`); define `PYTHONUNBUFFERED=1` y `PYTHONDONTWRITEBYTECODE=1`
    - Copia `requirements/production.txt` e instala **antes** de copiar el código fuente para preservar el cacheo de capas. Instala las dependencias de compilación/ejecución del sistema operativo (p. ej. `gettext`) en una única capa `apt-get` y limpia `/var/lib/apt/lists`
    - Crea un usuario de sistema **sin privilegios** y cambia a él; aplica `chown` al árbol de la aplicación y a su home para ese usuario
    - `ENTRYPOINT` ejecuta el script de release; `CMD` ejecuta _gunicorn_
3.  **Nomenclatura en dominio inverso:** contenedores e imágenes `com.example.project.service` (p. ej. `com.example.project.api`); los volúmenes con nombre usan la variante en kebab-case `com-example-project-service`
4.  **Entrypoint de release (`deploy/scripts/entrypoint.sh`):** espera a la base de datos, después ejecuta `migrate --noinput`, `createcachetable` y `collectstatic --noinput`, y finalmente `exec "$@"` para ceder el control a _gunicorn_. Los archivos estáticos los sirve _WhiteNoise_ dentro de _gunicorn_, no el proxy
5.  **Proxy inverso (_Caddy_):** un `Caddyfile` termina el TLS (HTTPS automático), habilita `zstd`/`gzip`, limita el cuerpo de la solicitud y hace `reverse_proxy` al servicio de la aplicación. El proxy existe **solo** en la superposición de producción y es dueño de los puertos `80`/`443`
6.  **Operaciones programadas del host (_systemd_, no cron):** los trabajos recurrentes viven en `deploy/systemd/` como parejas `oneshot` `*.service` + `*.timer` (`After`/`Requires=docker.service`), cada una notificando a un monitor de tipo **dead-man's-switch** mediante `ExecStartPost`. Las unidades llevan marcadores `<path>`/`<user>`/`<monitor>` que se rellenan en el host. El trabajo portable que todo despliegue debería tener es la **copia de seguridad externa de la base de datos** (`pg_dump` → `gzip` → `scp`, con retención local). Cualquier tarea recurrente específica del proyecto (p. ej. un comando de gestión de reconciliación de datos) reutiliza el mismo patrón `service` + `timer` + monitor — pero solo se incluye cuando ese proyecto realmente la necesita
7.  **Semillas de base de datos:** el SQL de semilla/inicialización se monta en `/docker-entrypoint-initdb.d/`; confía en el **orden de ejecución alfabético** de _Postgres_ (p. ej. `00-init-role.sql` antes que `10-database.sql`) para la secuencia
8.  **Endurecimiento de Django en producción (detrás del proxy):** en `settings/production.py`, confía en el proxy y fuerza el TLS — `SECURE_PROXY_SSL_HEADER`, `USE_X_FORWARDED_HOST`, `SECURE_SSL_REDIRECT`, cookies seguras, HSTS, y `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`/`CORS_ALLOWED_ORIGINS` explícitos. Ver `conf-settings-structure` para la división modular en sí
9.  **Archivos de exclusión:** un `.dockerignore` estricto excluye `.venv.*`, `.env`, `__pycache__` y los archivos del sistema y del editor

**Incorrecto (archivo único, usuario root, sin paso de release, nombres genéricos):**

```dockerfile
# ./Dockerfile

# Mal: imagen pesada, código antes que requisitos (rompe la caché), se ejecuta como root
FROM python:3.13
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "project.wsgi"]
```

```yaml
# ./compose.yml

services:
  db: # Mal: nombre genérico, propenso a colisiones
    image: postgres
  api:
    build: .
    command: python manage.py runserver 0.0.0.0:8000 # Mal: comando de desarrollo fijado en la base
```

**Correcto (imagen endurecida, superposiciones en capas, proxy, entrypoint):**

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

# Cacheo de capas: los requisitos antes que el código fuente
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
# ./compose.yml (base agnóstica al entorno)

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
# ./compose.override.yml (desarrollo, cargado automáticamente)

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
# ./compose.prod.yml (producción, explícita mediante -f)

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
# Reemplaza <path> (raíz del proyecto en el host), <user>/<group> y <monitor> (dirección de notificación).

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
# ./project/settings/production.py (endurecimiento consciente del proxy; ver conf-settings-structure)

from .settings import *

DEBUG = False
ALLOWED_HOSTS = ["api.example.com"]

# Confía en el proxy inverso y fuerza HTTPS
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

#### Referencia de ejecución

**Desarrollo (la superposición se aplica automáticamente):**

```bash
$ docker compose up -d --build
```

**Producción (base + superposición de producción explícita):**

```bash
$ docker compose -f compose.yml -f compose.prod.yml up -d --build
```

**Habilitar un trabajo programado del host (en el servidor):**

```bash
$ sudo systemctl enable --now backup.timer
```

Referencia: [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices) · [Caddy Reverse Proxy](https://caddyserver.com/docs/quick-starts/reverse-proxy) · [systemd Timers](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html) · [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)

### 2.3 Segregación de entorno y dependencias

**Impacto (MEDIUM):** Una separación estricta garantiza que los artefactos de producción se mantengan ligeros y seguros al excluir las herramientas de desarrollo. Usar entornos virtuales distintos evita la "contaminación" accidental del árbol de dependencias de producción durante las pruebas locales.

**Directrices:**

1.  **Entornos virtuales duales:** no uses un `.venv` genérico. Crea dos entornos explícitos en la raíz del proyecto:
    - `.venv.development`: para programar, hacer linting y probar en local
    - `.venv.production`: para simular el proceso de compilación y verificar instalaciones limpias
2.  **Archivos de requisitos:** guarda las dependencias en un directorio `requirements/`, nunca en un `./requirements.txt` en la raíz
    - `./requirements/production.txt`: solo las librerías necesarias para que la aplicación funcione
    - `./requirements/development.txt`: librerías para comprobación de tipos (stubs), formateo y depuración
3.  **Instalación contextual:** antes de instalar un paquete, decide explícitamente: "¿esto hace falta para la lógica de la aplicación o para quien desarrolla?" Instálalo en el entorno/archivo correspondiente
4.  **Pila estándar de desarrollo:** los requisitos de desarrollo deben incluir stubs de tipos para el tipado estricto (p. ej., `django-stubs`, `djangorestframework-stubs`)

**Incorrecto (entorno mezclado y archivo monolítico):**

```bash
# Mal: entorno genérico
$ python3 -m venv .venv

# Mal: archivo en la raíz que mezcla responsabilidades
$ cat ./project/requirements.txt
```

**Correcto (entornos y archivos segregados):**

```bash
# 1. Crear el entorno de producción
$ python3 -m venv .venv.production

# 2. Crear el entorno de desarrollo
$ python3 -m venv .venv.development
```

**Estructura de archivos:**

```plaintext
./project/
├── .venv.development/
├── .venv.production/
└── requirements/
    ├── development.txt
    └── production.txt
```

**Ejemplos de contenido:**

```plaintext
# ./requirements/production.txt (ejemplo)

Django==5.2.6
djangorestframework==3.16.1
gunicorn==23.0.0
psycopg2-binary==2.9.10
```

```plaintext
# ./requirements/development.txt (ejemplo)

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

Referencia: [Python venv Documentation](https://docs.python.org/3/library/venv.html)

---

## 3. ORM y base de datos

### 3.1 Definición estándar de modelos

**Impacto (HIGH):** La consistencia en la definición de modelos reduce drásticamente la carga cognitiva al navegar por la capa de datos. Exigir "un modelo por archivo" evita archivos `models.py` enormes, mientras que un orden y un tipado estrictos garantizan un código predecible y autodocumentado.

**Directrices:**

1.  **Aislamiento por archivo:** cada modelo debe residir en su propio archivo dentro del paquete `models/` (p. ej., `./apps/users/models/user.py`)
2.  **Definición de campos:** el primer argumento de todo campo no relacional debe ser el `verbose_name` traducido (usando `gettext_lazy`)
3.  **Estructura de la clase:** respeta el siguiente orden dentro de la clase:
    1.  `Choices` (Enums/TextChoices)
    2.  Campos de base de datos
    3.  Managers personalizados (`objects = ...`)
    4.  `class Meta`
    5.  Propiedades / métodos personalizados
    6.  `def __str__(self):`
4.  **Metadatos:**
    - Define explícitamente `verbose_name` y `verbose_name_plural`
    - Define explícitamente `db_table` (condicional): para modelos con nombres de varias palabras (p. ej., `UserAsset`), debes definir explícitamente `db_table` para imponer la separación en _snake_case_ (p. ej., `users_user_asset`). Para modelos de una sola palabra, el comportamiento por defecto es aceptable
5.  **Tipado:** añade anotaciones de tipo solo cuando aporten valor real a quien lee. Omite las anotaciones de retorno en los métodos dunder (`__str__`, `__repr__`), ya que su contrato lo define el protocolo, y en las propiedades o métodos cuya expresión de retorno se documenta a sí misma

**Incorrecto (estructura mezclada, faltan traducciones y tipos):**

```python
# ./apps/users/models/asset.py

class UserAsset(models.Model):
    # Tabla implícita: "users_userasset" (difícil de leer)
    class Meta:
        verbose_name = _("user asset")
        verbose_name_plural = _("user assets")
        # Falta `db_table` -> inconsistencia de datos en la convención de nombres
```

**Correcto (lógica condicional aplicada)**

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

    # 2. Campos
    phone = models.CharField(_("phone"), max_length=20, blank=True)
    role = models.CharField(_("role"), max_length=10, choices=Role.choices, default=Role.CUSTOMER)

    # 3. Managers
    objects = UserManager()

    # 4. Meta
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    # 5. Métodos/propiedades
    @property
    def is_premium(self):
        return self.role == self.Role.CUSTOMER

    # 6. Representación en cadena
    def __str__(self):
        return self.email or self.username
```

Referencia: [Django Model Meta Options](https://docs.djangoproject.com/en/6.0/ref/models/options)

---

## 4. API y serialización

### 4.1 Definición, nomenclatura y delegación de serializadores

**Impacto (HIGH):** Separar los serializadores por acción (lectura frente a escritura) evita abstracciones que se filtran. La delegación de la respuesta solo merece abstraerse cuando la repetición lo demuestra: un único serializador de escritura que reconfigura su respuesta se lee mejor con un `to_representation` local, mientras que una tercera copia de esa sobrescritura convierte al mecanismo, y no al mapeo, en lo que el proyecto mantiene.

**Directrices:**

1.  **Imports condicionales:**
    - **Simple:** si se hereda _solo_ de `ModelSerializer` sin campos personalizados, importa `ModelSerializer` directamente
    - **Complejo:** si se usan campos personalizados (p. ej., `CharField`), importa el módulo `serializers` y usa `serializers.ModelSerializer`
2.  **Convención de nombres:** usa sufijos específicos:
    - `*ListSerializer`: optimizado para colecciones
    - `*RetrieveSerializer`: lectura detallada de un solo objeto
    - `*CreateSerializer` / `*UpdateSerializer`: para operaciones de escritura
3.  **Delegación de la respuesta (operaciones de escritura):**
    - Un serializador de escritura (`Create`/`Update`) que deba devolver una representación distinta de su entrada (p. ej., la estructura completa de `UserRetrieveSerializer` tras crear un usuario) sobrescribe `to_representation` localmente mientras el proyecto tenga menos de tres serializadores así
    - Al llegar al tercero, extrae `DelegateRepresentationMixin` a `apps/common/mixins` y migra a él todos los serializadores que delegan — el conteo es a nivel de proyecto e independiente de a qué serializador apunte cada uno, porque el mixin factoriza el mecanismo y no el mapeo
    - Una vez que el mixin existe, es la única forma aceptada: una sobrescritura manual que quede atrás es exactamente la duplicación que la extracción eliminó
    - Declara el serializador de destino en `Meta.representation`
4.  **Declaración de campos:**
    - `Meta.fields` debe ser siempre una lista explícita `[...]`. Nunca uses `"__all__"` ni ninguna otra abreviatura
    - El orden de los campos en la lista debe coincidir con el orden en que están definidos en el modelo
    - Cada campo va en su propia línea, con una coma final después del último, por corta que sea la lista. La coma final es lo que fija esa disposición: cualquier formateador compatible con _Black_ mantiene expandido un literal expandido en cuanto está presente, de modo que un serializador de dos campos no vuelve a colapsarse en una línea mientras uno de cinco se queda expandido

**Incorrecto (campos implícitos, orden arbitrario o una lista colapsada):**

```python
class UserRetrieveSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"  # Mal: expone campos no previstos; el orden no es determinista
```

```python
class UserRetrieveSerializer(ModelSerializer):
    class Meta:
        model = User
        # Mal: el orden no coincide con la definición del modelo
        fields = [
            "name",
            "id",
            "phone",
        ]
```

```python
class InvoiceListSerializer(ModelSerializer):
    class Meta:
        model = Invoice
        # Mal: es lo bastante corta como para caber en una línea, así que se lee
        # distinto de cualquier serializador más largo, y el siguiente campo que
        # se añada reescribirá esta línea
        fields = ["id", "number"]
```

**Correcto (lista explícita ordenada según la definición del modelo):**

```python
# Orden de definición del modelo: id, phone, name, role
class UserRetrieveSerializer(ModelSerializer):
    class Meta:
        model = User
        # Coincide con el orden de campos del modelo
        fields = [
            "id",
            "phone",
            "name",
            "role",
        ]
```

**Incorrecto (abstracción sin repetición, o repetición sin abstracción):**

```python
# ./apps/users/serializers/user_create_serializer.py — el único serializador que delega

from apps.common.mixins import DelegateRepresentationMixin

# Mal: un mixin compartido en apps/common/ con un único punto de uso.
# La indirección cuesta más que las tres líneas que reemplaza
class UserCreateSerializer(DelegateRepresentationMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "identification",
            "name",
            "phone",
        ]
        representation = UserRetrieveSerializer
```

```python
# ./apps/invoices/serializers/invoice_create_serializer.py — la tercera sobrescritura de su tipo

class InvoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "number",
            "customer",
            "total",
        ]

    # Mal: UserCreateSerializer y PaymentCreateSerializer ya cargan estas mismas
    # líneas. El mecanismo de delegación es ahora lo que el proyecto mantiene
    def to_representation(self, instance):
        from .invoice_retrieve_serializer import InvoiceRetrieveSerializer

        return InvoiceRetrieveSerializer(instance, context=self.context).data
```

**Correcto (sobrescritura local por debajo del umbral, mixin extraído al alcanzarlo):**

```python
# ./apps/users/serializers/user_create_serializer.py — uno de los dos serializadores que delegan

from rest_framework import serializers

from apps.users.models import User

class UserCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=6, write_only=True)

    class Meta:
        model = User
        fields = [
            "identification",
            "name",
            "phone",
            "code",
        ]

    # Local, evidente y barato de borrar en cuanto un mixin lo reemplace.
    # El import se difiere para romper la referencia circular entre serializadores
    def to_representation(self, instance):
        from .user_retrieve_serializer import UserRetrieveSerializer

        return UserRetrieveSerializer(instance, context=self.context).data
```

```python
# ./apps/invoices/serializers/invoice_create_serializer.py — el tercero: extraer y migrar

from rest_framework import serializers

from apps.common.mixins import DelegateRepresentationMixin
from apps.invoices.models import Invoice
from apps.invoices.serializers.invoice_retrieve_serializer import InvoiceRetrieveSerializer

# Hereda del Mixin + Serializer
class InvoiceCreateSerializer(DelegateRepresentationMixin, serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "number",
            "customer",
            "total",
        ]
        # Transforma la respuesta usando el serializador Retrieve
        representation = InvoiceRetrieveSerializer
```

Referencia: [DRF Customizing Serialization](https://www.django-rest-framework.org/api-guide/serializers/#customizing-serialization)

### 4.2 Selección de vistas, tipado y seguridad

**Impacto (MEDIUM):** La estandarización evita el código repetitivo. Usar vistas genéricas reduce el mantenimiento. Un tipado con propósito en las _APIViews_ mejora el soporte del IDE y comunica la intención. Declarar explícitamente `authentication_classes` y `permission_classes` evita depender de valores por defecto globales implícitos, y hace que el contrato de seguridad de cada vista se documente a sí mismo.

**Directrices:**

1.  **Criterios de selección:**
    - **_Generic Views_:** deben ser la opción por defecto para operaciones _CRUD_ estándar (p. ej., `ListCreateAPIView`)
    - **_APIView_:** úsala solo cuando las genéricas estándar sean insuficientes (p. ej., lógica de negocio compleja, autenticación, RPC)
2.  **Tipado (_APIView_):**
    - Anota siempre `request` como `Request` — aporta valor real al habilitar el autocompletado del IDE y hacer explícito el contrato del parámetro
    - Omite las anotaciones de tipo de retorno cuando la sentencia `return` se documenta a sí misma (p. ej., `return Response(...)`); añádelas solo cuando la lógica de ramificación vuelva el tipo de retorno no evidente
    - Usa imports explícitos (p. ej., `from rest_framework.request import Request`)
3.  **Declaración de seguridad:**
    - Toda vista (_APIView_, _Generic View_ o _ViewSet_) debe declarar explícitamente tanto `authentication_classes` como `permission_classes`
    - Cuando una vista no requiera autenticación ni permisos, declara listas vacías explícitamente — nunca confíes en los valores por defecto globales implícitos
    - Los dos atributos deben declararse juntos, separados de `queryset` y `serializer_class` por una línea en blanco

Cómo se registran después estas vistas en `urls.py` lo cubre `arch-url-registration`.

**Incorrecto (seguridad implícita — depende de los valores por defecto globales):**

```python
# ./apps/users/views/login.py

class UserLoginAPIView(APIView):
    # Mal: no se declaran authentication_classes ni permission_classes.
    # El comportamiento de seguridad depende por completo de
    # DEFAULT_AUTHENTICATION_CLASSES y DEFAULT_PERMISSION_CLASSES en settings
    # — invisible para quien lee.
    def post(self, request: Request):
        return Response({})
```

```python
# ./apps/users/views/profile.py

class UserProfileListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserRetrieveSerializer
    # Mal: falta la declaración explícita de seguridad en una Generic View
```

**Correcto (seguridad explícita en todos los tipos de vista):**

```python
# ./apps/users/views/login.py — APIView sin autenticación requerida

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
# ./apps/users/views/profile.py — Generic View con autenticación requerida

from rest_framework.generics import ListAPIView

from apps.users.models import User
from apps.users.serializers import UserRetrieveSerializer

class UserProfileListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserRetrieveSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
```

**Incorrecto (faltan tipos):**

```python
# ./apps/users/views/login.py

class UserLoginAPIView(APIView):
    # Falta la anotación de tipo de request — se pierde el autocompletado del IDE
    # y la claridad del parámetro
    def post(self, request):
        return Response({})
```

**Correcto (selección consciente del contexto y tipado explícito):**

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
        # ... lógica ...
        return Response({"foo": "bar"})
```

Referencia: [Django REST Framework Class-based Views](https://www.django-rest-framework.org/api-guide/views)

### 4.3 Registro, agrupación y orden de URLs

**Impacto (MEDIUM):** _Django_ resuelve `urlpatterns` de arriba abajo y devuelve la primera coincidencia, así que el orden no es solo una cuestión de legibilidad: una ruta de detalle con un conversor permisivo colocada por encima de una hermana literal se la traga en silencio, y el endpoint eclipsado falla de una forma que ninguna prueba de la propia vista puede detectar. Agrupar por dominio mantiene navegable una tabla de rutas que crece, un orden de acciones fijo hace visible por su ausencia un endpoint que falta, y un argumento por línea limita los diffs a la línea que realmente cambió.

**Directrices:**

1.  **Import del módulo:** en `urls.py`, importa el módulo de vistas de forma relativa — `from . import views` — y registra las rutas referenciando el módulo: `views.MyClassName.as_view()`. Nunca importes las clases de vista directamente; los imports a nivel de módulo evitan conflictos de nombres y dependencias circulares
2.  **Agrupación por dominio:** dentro de una misma lista `urlpatterns`, todas las rutas que pertenecen al mismo dominio son contiguas, y los dominios consecutivos se separan con una línea en blanco. Nunca intercales dominios
3.  **Orden por acción:** dentro de un grupo de dominio, las rutas se ordenan **creación, listado, detalle** — en ese orden. Los segmentos literales preceden así a los segmentos con conversor, que es lo que impide que un conversor permisivo eclipse a sus hermanas
4.  **Registro a nivel de proyecto:** el urlconf raíz registra un `include()` por aplicación, nunca una vista individual. Las entradas de infraestructura (p. ej. `admin/`) van primero, seguidas de los dominios de las aplicaciones en un orden deliberado y estable
5.  **Disposición de llamadas expandidas:** cada `path()` se escribe con un argumento por línea y una coma final tras el último, por corta que sea la llamada. La coma final es lo que fija la disposición: cualquier formateador compatible con _Black_ mantiene expandida una llamada expandida en cuanto está presente, de modo que la lista se mantiene uniforme en lugar de colapsar las entradas cortas

**Incorrecto (imports directos, dominios intercalados, ruta eclipsada, llamadas colapsadas):**

```python
# ./apps/config/urls.py

from django.urls import path

# Mal: imports directos de clases — conflictos de nombres y riesgo de import circular
from .views import (
    ConfigGroupCreateAPIView,
    ConfigGroupListAPIView,
    ConfigItemCreateAPIView,
    ConfigItemListAPIView,
    ConfigItemRetrieveAPIView,
)

urlpatterns = [
    # Mal: la ruta de detalle primero — "<str:code>" coincide con "new", así que
    # la ruta de creación de abajo es inalcanzable
    path("items/<str:code>/", ConfigItemRetrieveAPIView.as_view()),
    # Mal: dominios intercalados, y sin orden de acciones dentro de ellos
    path("groups/", ConfigGroupListAPIView.as_view()),
    path("items/", ConfigItemListAPIView.as_view()),
    path("items/new/", ConfigItemCreateAPIView.as_view()),
    path("groups/new/", ConfigGroupCreateAPIView.as_view()),
]
```

**Correcto (import del módulo, un dominio por grupo, create → list → detail, expandido):**

```python
# ./apps/config/urls.py

from django.urls import path

# Estándar: importa el módulo, no la clase
from . import views

urlpatterns = [
    path(
        "items/new/",
        views.ConfigItemCreateAPIView.as_view(),
    ),
    path(
        "items/",
        views.ConfigItemListAPIView.as_view(),
    ),
    path(
        "items/<str:code>/",
        views.ConfigItemRetrieveAPIView.as_view(),
    ),

    path(
        "groups/new/",
        views.ConfigGroupCreateAPIView.as_view(),
    ),
    path(
        "groups/",
        views.ConfigGroupListAPIView.as_view(),
    ),
    path(
        "groups/<int:pk>/",
        views.ConfigGroupRetrieveAPIView.as_view(),
    ),
]
```

```python
# ./project/urls.py

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "api/users/",
        include("apps.users.urls"),
    ),
    path(
        "api/config/",
        include("apps.config.urls"),
    ),
]
```

Referencia: [Django URL Dispatcher](https://docs.djangoproject.com/en/6.0/topics/http/urls)
