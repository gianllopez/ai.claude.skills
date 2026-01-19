---
title: Modular Settings Configuration
impact: MEDIUM
description: Enforces splitting *Django* settings into a modular structure (base, development, production) to ensure security and environment isolation.
tags: django, configuration
---

## Modular Settings Configuration

**Impact (MEDIUM):** Splitting settings prevents accidental deployment of insecure configurations (like `DEBUG=True`) to production. It cleanly separates shared logic (database connections, apps) from environment-specific overrides.

**Guidelines:**

1.  **Directory Structure:** Do not use a single `settings.py`. Create a `settings/` package inside the project configuration directory.
2.  **File Organization:**
    - `settings.py`: Contains shared configurations (Apps, Middleware, Database connection logic, I18N, Auth).
    - `development.py`: Imports base (`from .settings import *`) and sets `DEBUG = True` and permissive access.
    - `production.py`: Imports base (`from .settings import *`) and sets `DEBUG = False` and restricted access.
3.  **Path Adjustment:** In `settings.py`, `BASE_DIR` must calculate the parent three times (`.parent.parent.parent`) to compensate for the new subdirectory depth.
4.  **Environment Variables:** Sensitive data (`SECRET_KEY`, `DB_PASSWORD`) must be loaded via `os.environ` in the base settings.

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
