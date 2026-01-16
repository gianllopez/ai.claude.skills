---
title: Standard Model Definition
impact: HIGH
description: Enforces strict ordering, translation, and file isolation for Django models.
tags: django, orm
---

## Standard Model Definition

**Impact (HIGH):** Consistency in model definition drastically reduces cognitive load when navigating the data layer. Enforcing "one model per file" prevents massive `models.py` files, while strict ordering and typing ensure predictable and self-documenting code.

**Guidelines:**

1.  **File Isolation:** Each model must reside in its own file within the `models/` package (e.g., `apps/users/models/user.py`).
2.  **Field Definition:** The first argument of every non-relational field must be the translated `verbose_name` (using `gettext_lazy`).
3.  **Class Structure:** Adhere to the following order inside the class:
    1.  `Choices` (Enums/TextChoices)
    2.  Database Fields
    3.  Custom Managers (`objects = ...`)
    4.  `class Meta`
    5.  Properties / Custom Methods
    6.  `def __str__(self) -> str:`
4.  **Metadata:**
    - Explicitly define `verbose_name` and `verbose_name_plural`.
    - Explicitly define `db_table` (Conditional) for models with multi-word names (e.g., `UserAsset`), you **MUST** explicitly define `db_table` to enforce _snake_case_ separation (e.g., `users_user_asset`). For single-word models, the default behavior is acceptable.
5.  **Typing:** The `__str__` method must strictly include the return type hint `-> str`.

**Incorrect (Mixed structure, missing translations/types):**

```python
# apps/users/models/asset.py
class UserAsset(models.Model):
    # Implicit table: "users_userasset" (Hard to read)
    class Meta:
        verbose_name = _("user asset")
        verbose_name_plural = _("user assets")
        # Missing db_table -> Data inconsistency in naming convention
```

**Correct (Conditional logic applied)**

```python
# apps/users/models/user.py
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
    def is_premium(self) -> bool:
        return self.role == self.Role.CUSTOMER

    # 6. String representation (with type hint for return)
    def __str__(self) -> str:
        return self.email or self.username
```

Reference: [Django Model Meta Options](https://docs.djangoproject.com/en/6.0/ref/models/options)
