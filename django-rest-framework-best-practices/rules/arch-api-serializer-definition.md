---
title: Serializer Definition, Naming & Delegation
impact: HIGH
description: Enforces conditional imports, action-based naming conventions, and response delegation for write serializers using `DelegateRepresentationMixin`.
tags: django-rest-framework, serializers
---

## Serializer Definition, Naming & Delegation

**Impact (HIGH):** Separating serializers by action (Read vs. Write) prevents leaky abstractions. Using a delegation mixin for write operations ensures that responses contain rich data without code duplication or manual `to_representation` overrides.

**Guidelines:**

1.  **Conditional Imports:**
    - **Simple:** If inheriting _only_ from `ModelSerializer` with no custom fields, import `ModelSerializer` directly.
    - **Complex:** If using custom fields (e.g., `CharField`), import the `serializers` module and use `serializers.ModelSerializer`.
2.  **Naming Convention:** Use specific suffixes:
    - `*ListSerializer`: Optimized for collections.
    - `*RetrieveSerializer`: Detailed single-object read.
    - `*CreateSerializer` / `*UpdateSerializer`: For write operations.
3.  **Response Delegation (Write Operations):**
    - When a write serializer (`Create`/`Update`) needs to return a different representation than its input (e.g., return the full `UserRetrieveSerializer` structure after creating a user), must inherit from `DelegateRepresentationMixin`.
    - Define the target serializer in `Meta.representation`.

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
