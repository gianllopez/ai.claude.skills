---
title: Scoped Verification & No Unsolicited Tests
impact: HIGH
description: Ties the verification method strictly to what was implemented, including the security contract of a view and the side effects of a signal — never write automated test files unless explicitly requested.
tags: django-rest-framework, testing, verification, scope
---

## Scoped Verification & No Unsolicited Tests

**Impact (HIGH):** Verifying beyond what changed wastes effort and drifts into unrequested scope — writing a `pytest` suite, adding assertions for fields nobody asked to validate, or exercising layers a change never touched. Tying the verification method to the actual change surface keeps confirmation fast, reproducible, and limited to what was asked.

**Guidelines:**

1.  **Never write automated test files unless explicitly requested.** `pytest`/`unittest` suites, fixtures, or files under `tests/` are a deliverable the user asks for by name — not a default step after implementing a model, serializer, or view
2.  **Verification is ephemeral**, not committed code: a one-off `manage.py shell -c "..."` snippet or a `curl` call, run and reported, then discarded
3.  **The verification method follows the change surface** — never verify a layer the change did not touch:

    | Change surface                                                             | How to verify                                                                                                                                                                 |
    | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | Model only                                                                 | `manage.py makemigrations --check --dry-run`, then `migrate` — nothing further                                                                                                |
    | Serializer only (view untouched)                                           | `manage.py shell -c "..."` instantiating the serializer with a representative payload; inspect `.is_valid()`, `.errors`, `.validated_data`                                    |
    | The view changed — alone, or as part of a model + serializer + view flow   | `curl` against the resulting endpoint. Do not additionally verify the model or serializer in isolation                                                                        |
    | The view declares or changed `authentication_classes`/`permission_classes` | In addition to the happy-path `curl`, a second `curl` without credentials (or with an invalid token) confirming a `401`/`403` — the security contract is part of what changed |
    | A signal/receiver was added or changed                                     | `manage.py shell -c "..."` triggering the event that fires the signal (e.g. saving the instance) and inspecting the side effect it produces                                   |

4.  **Do not add validation beyond what was requested** (extra field checks, edge cases, error-handling branches) as a side effect of "testing" — if the implementation needs a validation, that is a design decision to raise with the user, not something to smuggle in while verifying

**Incorrect (composite flow verified with an unrequested test file):**

```python
# ./apps/users/tests.py — nobody asked for this file

from rest_framework.test import APITestCase

class UserCreateTests(APITestCase):
    def test_create_user(self):
        response = self.client.post("/api/users/", {"name": "Ada"})
        self.assertEqual(response.status_code, 201)

    def test_create_user_missing_name(self):
        # Bad: an edge case nobody asked to cover
        response = self.client.post("/api/users/", {})
        self.assertEqual(response.status_code, 400)
```

**Correct (model + serializer + view implemented together — verified with one curl call against the view):**

```bash
$ curl -X POST http://localhost:8000/api/users/ \
    -H "Content-Type: application/json" \
    -d '{"name": "Ada", "phone": "555-0100"}'

{"id": 1, "name": "Ada", "phone": "555-0100"}
```

**Incorrect (serializer-only change verified by hitting the endpoint):**

```bash
# Bad: only the serializer changed — the view and URL were already exercised
# and stable. Going through curl re-verifies untouched layers.
$ curl -X POST http://localhost:8000/api/users/ -d '{"name": "Ada"}'
```

**Correct (serializer-only change verified in isolation via shell):**

```bash
$ python manage.py shell -c "
from apps.users.serializers import UserCreateSerializer
s = UserCreateSerializer(data={'name': 'Ada', 'phone': '555-0100'})
print(s.is_valid(), s.errors, s.validated_data)
"

True {} {'name': 'Ada', 'phone': '555-0100'}
```

**Incorrect (permission change verified only through the happy path):**

```bash
# Bad: confirms the endpoint works, but never confirms the permission
# actually rejects an unauthenticated request — the security contract is untested
$ curl -X POST http://localhost:8000/api/users/ -d '{"name": "Ada"}'

{"id": 1, "name": "Ada"}
```

**Correct (both sides of the permission contract verified):**

```bash
$ curl -X POST http://localhost:8000/api/users/ \
    -H "Authorization: Bearer <valid-token>" \
    -d '{"name": "Ada"}'

{"id": 1, "name": "Ada"}

$ curl -X POST http://localhost:8000/api/users/ -d '{"name": "Ada"}'

{"detail": "Authentication credentials were not provided."}
```

**Correct (signal verified by triggering the event and inspecting the side effect):**

```bash
$ python manage.py shell -c "
from apps.users.models import User
u = User.objects.create(name='Ada', email='ada@example.com')
from apps.notifications.models import WelcomeEmailLog
print(WelcomeEmailLog.objects.filter(user=u).exists())
"

True
```

Reference: [Django manage.py shell](https://docs.djangoproject.com/en/6.0/ref/django-admin/#shell)
