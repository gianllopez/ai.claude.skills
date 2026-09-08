---
title: URL Registration, Grouping & Ordering
impact: MEDIUM
description: Enforces module-level view imports, domain grouping and create/list/detail ordering in every urlpatterns list, and a fully exploded path() call layout.
tags: django, urls, routing
---

## URL Registration, Grouping & Ordering

**Impact (MEDIUM):** _Django_ resolves `urlpatterns` top-down and returns the first match, so ordering is not only a matter of readability: a detail route carrying a permissive converter placed above a literal sibling silently swallows it, and the shadowed endpoint fails in a way no test of the view itself can catch. Grouping by domain keeps a growing routing table navigable, a fixed action order makes a missing endpoint visible by its absence, and one argument per line keeps diffs limited to the line that actually changed.

**Guidelines:**

1.  **Module Import:** In `urls.py`, import the views module relatively — `from . import views` — and register paths referencing the module: `views.MyClassName.as_view()`. Never import the view classes directly; module-level imports prevent naming conflicts and circular dependencies
2.  **Grouping by Domain:** Within a single `urlpatterns` list, all routes belonging to the same domain are contiguous, and consecutive domains are separated by a blank line. Never interleave domains
3.  **Ordering by Action:** Inside a domain group, routes are ordered **creation, listing, detail** — in that order. Literal segments therefore precede converter segments, which is what keeps a permissive converter from shadowing its siblings
4.  **Project-Level Registration:** The root urlconf registers one `include()` per app, never an individual view. Infrastructure entries (e.g. `admin/`) come first, followed by the app domains in a deliberate, stable order
5.  **Exploded Call Layout:** Every `path()` is written with one argument per line and a trailing comma after the last one, regardless of how short the call is. The trailing comma is what pins the layout: any _Black_-compatible formatter keeps an exploded call exploded once it is present, so the list stays uniform instead of collapsing the short entries

**Incorrect (direct imports, interleaved domains, shadowed route, collapsed calls):**

```python
# ./apps/config/urls.py

from django.urls import path

# Bad: direct class imports — name conflicts and circular import risk
from .views import (
    ConfigGroupCreateAPIView,
    ConfigGroupListAPIView,
    ConfigItemCreateAPIView,
    ConfigItemListAPIView,
    ConfigItemRetrieveAPIView,
)

urlpatterns = [
    # Bad: detail route first — "<str:code>" matches "new", so the creation
    # route below is unreachable
    path("items/<str:code>/", ConfigItemRetrieveAPIView.as_view()),
    # Bad: domains interleaved, and no action order within them
    path("groups/", ConfigGroupListAPIView.as_view()),
    path("items/", ConfigItemListAPIView.as_view()),
    path("items/new/", ConfigItemCreateAPIView.as_view()),
    path("groups/new/", ConfigGroupCreateAPIView.as_view()),
]
```

**Correct (module import, one domain per group, create → list → detail, exploded):**

```python
# ./apps/config/urls.py

from django.urls import path

# Standard: import the module, not the class
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

Reference: [Django URL Dispatcher](https://docs.djangoproject.com/en/6.0/topics/http/urls)
