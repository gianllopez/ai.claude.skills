---
title: View Selection, Typing & Registration
impact: MEDIUM
description: Enforces generic views usage, strict typing for APIViews, and module-level imports for views registration.
tags: django-rest-framework, views
---

## View Selection, Typing & Registration

**Impact (MEDIUM-HIGH):** Standardization prevents boilerplate code. Using generic views reduces maintenance. Strict typing in _APIViews_ ensures clarity. Module-level imports in `urls.py` prevent naming conflicts and circular dependencies.

**Guidelines:**

1.  **Selection Criteria:**
    - **Generic Views:** Must be the default choice for standard _CRUD_ operations (e.g., `ListCreateAPIView`).
    - **APIView:** Use only when standard Generics are insufficient (e.g., complex business logic, Auth, RPC).
2.  **Strict Typing (APIView):**
    - Explicitly type-hint `request` (`Request`) and the return value (`Response`).
    - Use explicit imports: `from rest_framework.request import Request`.
3.  **URL Registration:**
    - In `urls.py`, import the views module relatively: `from . import views`.
    - Register paths referencing the module: `views.MyClassName.as_view()`.

**Incorrect (Direct imports & Missing Types):**

```python
# urls.py
from .views import UserLoginAPIView # Potential name conflict

urlpatterns = [
    path("login/", UserLoginAPIView.as_view()),
]
```

```python
# views.py
class UserLoginAPIView(APIView):
    # Missing Type Hints
    def post(self, request):
        return Response({})
```

**Correct (Context-Aware Selection & Module Import):**

```python
# apps/users/views.py
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from apps.users.serializers import UserLoginSerializer

class UserLoginAPIView(APIView):
    def post(self, request: Request) -> Response:
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # ... logic ...
        return Response({"foo": "bar"})
```

```python
# apps/users/urls.py
from django.urls import path

# Standard: Import the module, not the class
from . import views

urlpatterns = [
    path("login/", views.UserLoginAPIView.as_view()),
]
```

Reference: [Django URL Dispatcher](https://docs.djangoproject.com/en/stable/topics/http/urls)
