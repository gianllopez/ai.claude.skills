---
title: View Selection, Typing & Security
impact: MEDIUM
description: Enforces generic views usage, strict typing for APIViews, and explicit declaration of authentication and permission classes on every view.
tags: django-rest-framework, views
---

## View Selection, Typing & Security

**Impact (MEDIUM):** Standardization prevents boilerplate code. Using generic views reduces maintenance. Purposeful typing in _APIViews_ improves IDE support and communicates intent. Explicit declaration of `authentication_classes` and `permission_classes` prevents relying on implicit global defaults, making the security contract of every view self-documenting.

**Guidelines:**

1.  **Selection Criteria:**
    - **_Generic Views_:** Must be the default choice for standard _CRUD_ operations (e.g., `ListCreateAPIView`)
    - **_APIView_:** Use only when standard Generics are insufficient (e.g., complex business logic, Auth, RPC)
2.  **Typing (_APIView_):**
    - Always type-hint `request` as `Request` — it adds real value by enabling IDE autocompletion and making the parameter contract explicit
    - Omit return type annotations when the `return` statement is self-documenting (e.g., `return Response(...)`); add them only when branching logic makes the return type non-obvious
    - Use explicit imports (e.g., `from rest_framework.request import Request`)
3.  **Security Declaration:**
    - Every view (_APIView_, _Generic View_, or _ViewSet_) must explicitly declare both `authentication_classes` and `permission_classes`
    - When a view requires no authentication or permissions, declare empty lists explicitly — never rely on implicit global defaults
    - The two attributes must be declared together, separated from `queryset` and `serializer_class` by a blank line

How these views are then registered in `urls.py` is covered by `arch-url-registration`.

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

**Incorrect (Missing Types):**

```python
# ./apps/users/views/login.py

class UserLoginAPIView(APIView):
    # Missing request type hint — loses IDE autocompletion and parameter clarity
    def post(self, request):
        return Response({})
```

**Correct (Context-Aware Selection & Explicit Typing):**

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

Reference: [Django REST Framework Class-based Views](https://www.django-rest-framework.org/api-guide/views)
