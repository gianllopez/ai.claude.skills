---
title: Modular App Structure
impact: HIGH
description: Enforces package-based structure for models/views and specific AppConfig settings.
tags: django, configuration
---

## Modular App Structure & Configuration

**Impact (HIGH):** Ensures scalability and organization by grouping applications under an `apps/` directory and converting monolithic `models.py` and `views.py` into _Python_ packages. This facilitates better separation of concerns and cleaner imports via the _Facade_ pattern.

**Guidelines:**

1.  **Directory Location:** All _Django_ apps must reside inside the project's `apps/` folder, not the project root.
2.  **Package Conversion:** `models`, `serializers`, and `views` must be directories (packages) containing an `__init__.py`.
3.  **Public API:** Use `__init__.py` to explicitly export only the public classes/functions.
4.  **File Cleanup:** `admin.py` and `tests.py` should be cleared or reset upon creation; `urls.py` must be created if missing.
5.  **App Configuration:** The `apps.py` file must use the full path in `name` (e.g., `apps.users`) and include a translatable `verbose_name`.

**Incorrect (Flat structure & Default Config):**

```plaintext
users/models.py
users/views.py
users/apps.py
users/apps.py (missing)
```

```python
# users/apps.py
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"  # Missing namespace
```

**Correct (Modular Structure & Custom Config):**

```plaintext
apps/users/models/__init__.py
apps/users/models/user.py
apps/users/serializers/__init__.py
apps/users/views/__init__.py
apps/users/urls.py
apps/users/apps.py
```

```python
# apps/users/apps.py
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"  # Correct namespace
    verbose_name = _("Users")  # Translatable name
```

```python
# apps/my_app/models/__init__.py
# Facade pattern: Import internal implementations
from .users import User

# Export only what is public
__all__ = ["User"]
```

Reference: [Django AppConfig Documentation](https://docs.djangoproject.com/en/6.0/ref/applications)
