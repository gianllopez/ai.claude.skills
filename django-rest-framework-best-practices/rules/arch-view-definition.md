---
title: View Selection, Typing & Registration
impact: MEDIUM
description: Enforces generic views usage, strict typing for APIViews, and module-level imports for views registration.
tags: django-rest-framework, views
---

## View Selection, Typing & Registration

**Impact (MEDIUM):** Standardization prevents boilerplate code. Using generic views reduces maintenance. Purposeful typing in _APIViews_ improves IDE support and communicates intent. Module-level imports in `urls.py` prevent naming conflicts and circular dependencies.

**Guidelines:**

1.  **Selection Criteria:**
    - **Generic Views:** Must be the default choice for standard _CRUD_ operations (e.g., `ListCreateAPIView`).
    - **APIView:** Use only when standard Generics are insufficient (e.g., complex business logic, Auth, RPC).
2.  **Typing (APIView):**
    - Always type-hint `request` as `Request` — it adds real value by enabling IDE autocompletion and making the parameter contract explicit.
    - Omit return type annotations when the `return` statement is self-documenting (e.g., `return Response(...)`); add them only when branching logic makes the return type non-obvious.
    - Use explicit imports (e.g., `from rest_framework.request import Request`).
3.  **URL Registration:**
    - In `urls.py`, import the views module relatively: `from . import views`.
    - Register paths referencing the module: `views.MyClassName.as_view()`.

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
