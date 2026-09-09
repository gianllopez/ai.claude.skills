---
title: Serializer Definition, Naming & Delegation
impact: HIGH
description: Enforces conditional imports, action-based naming conventions, explicit field declaration one per exploded line, and response delegation extracted into DelegateRepresentationMixin once three write serializers need it.
tags: django-rest-framework, serializers
---

## Serializer Definition, Naming & Delegation

**Impact (HIGH):** Separating serializers by action (Read vs. Write) prevents leaky abstractions. Response delegation is worth abstracting only once repetition proves it: a lone write serializer that reshapes its response reads better with a local `to_representation`, while a third copy of that override turns the mechanism, rather than the mapping, into what the project maintains.

**Guidelines:**

1.  **Conditional Imports:**
    - **Simple:** If inheriting _only_ from `ModelSerializer` with no custom fields, import `ModelSerializer` directly
    - **Complex:** If using custom fields (e.g., `CharField`), import the `serializers` module and use `serializers.ModelSerializer`
2.  **Naming Convention:** Use specific suffixes:
    - `*ListSerializer`: Optimized for collections
    - `*RetrieveSerializer`: Detailed single-object read
    - `*CreateSerializer` / `*UpdateSerializer`: For write operations
3.  **Response Delegation (Write Operations):**
    - A write serializer (`Create`/`Update`) that must return a representation different from its input (e.g., the full `UserRetrieveSerializer` structure after creating a user) overrides `to_representation` locally while the project holds fewer than three such serializers
    - At the third one, extract `DelegateRepresentationMixin` into `apps/common/mixins` and migrate every delegating serializer to it — the count is project-wide and independent of which serializer each one targets, because the mixin factors out the mechanism and not the mapping
    - Once the mixin exists it is the only accepted form: a manual override left behind is exactly the duplication the extraction removed
    - Declare the target serializer in `Meta.representation`
4.  **Field Declaration:**
    - `Meta.fields` must always be an explicit list `[...]`. Never use `"__all__"` or any other shorthand
    - The order of fields in the list must match the order in which they are defined in the model
    - Every field goes on its own line, with a trailing comma after the last one, however short the list is. The trailing comma is what pins that layout: any _Black_-compatible formatter keeps an exploded literal exploded once it is present, so a two-field serializer does not collapse back onto one line while a five-field one stays expanded

**Incorrect (Implicit fields, arbitrary order, or a collapsed list):**

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
        # Bad: Order does not match model definition
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
        # Bad: short enough to fit on one line, so it reads differently from
        # every longer serializer, and the next field added rewrites this line
        fields = ["id", "number"]
```

**Correct (Explicit list ordered by model definition):**

```python
# Model definition order: id, phone, name, role
class UserRetrieveSerializer(ModelSerializer):
    class Meta:
        model = User
        # Matches model field order
        fields = [
            "id",
            "phone",
            "name",
            "role",
        ]
```

**Incorrect (Abstraction without repetition, or repetition without abstraction):**

```python
# ./apps/users/serializers/user_create_serializer.py — the only delegating serializer

from apps.common.mixins import DelegateRepresentationMixin

# Bad: a shared mixin in apps/common/ carrying a single call site.
# The indirection costs more than the three lines it replaces
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
# ./apps/invoices/serializers/invoice_create_serializer.py — the third override of its kind

class InvoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "number",
            "customer",
            "total",
        ]

    # Bad: UserCreateSerializer and PaymentCreateSerializer already carry these
    # same lines. The delegation mechanism is now what the project maintains
    def to_representation(self, instance):
        from .invoice_retrieve_serializer import InvoiceRetrieveSerializer

        return InvoiceRetrieveSerializer(instance, context=self.context).data
```

**Correct (Local override below the threshold, extracted mixin at it):**

```python
# ./apps/users/serializers/user_create_serializer.py — one of two delegating serializers

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

    # Local, obvious, and cheap to delete once a mixin replaces it.
    # The import is deferred to break the circular reference between serializers
    def to_representation(self, instance):
        from .user_retrieve_serializer import UserRetrieveSerializer

        return UserRetrieveSerializer(instance, context=self.context).data
```

```python
# ./apps/invoices/serializers/invoice_create_serializer.py — the third one: extract and migrate

from rest_framework import serializers

from apps.common.mixins import DelegateRepresentationMixin
from apps.invoices.models import Invoice
from apps.invoices.serializers.invoice_retrieve_serializer import InvoiceRetrieveSerializer

# Inherits from Mixin + Serializer
class InvoiceCreateSerializer(DelegateRepresentationMixin, serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "number",
            "customer",
            "total",
        ]
        # Transforms the response using the Retrieve serializer
        representation = InvoiceRetrieveSerializer
```

Reference: [DRF Customizing Serialization](https://www.django-rest-framework.org/api-guide/serializers/#customizing-serialization)
