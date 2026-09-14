---
title: Comment Language, Structure & Necessity
impact: MEDIUM
description: All code comments and docstrings must be written in English, follow a standard structure, and exist only where they carry information the code cannot express by itself — never restate what the code already says.
tags: django-rest-framework, comments, docstrings, documentation, style
---

## Comment Language, Structure & Necessity

**Impact (MEDIUM):** With most of the implementation delegated to AI agents, comments are the main place intent survives past the prompt that produced it. A comment that restates the line below it is noise a reviewer has to read and discard every time; a missing comment on a non-obvious workaround or side effect turns into a mystery the next person — human or agent — has to re-derive from scratch. Tying comments to a fixed language and structure keeps them scannable and prevents both failure modes at once.

**Guidelines:**

1.  **English only.** Every comment and docstring is written in English regardless of the spoken language used elsewhere in the conversation or the project — this matches the language the rest of the codebase (identifiers, commit messages) is already written in
2.  **Default to no comment.** Well-named models, fields, serializers, and views communicate the _what_. Add a comment only when it carries something the code cannot express on its own:
    - A non-obvious business rule or constraint (e.g., why a field is nullable, why an order of operations matters)
    - A workaround for a specific library/ORM limitation or bug, ideally naming the constraint that forces it
    - A side effect not visible at the call site (a signal receiver it triggers, a cache it invalidates, an external call a manager method makes)
3.  **Never restate the code.** A comment that only repeats the identifier or operation below it (`# save the user` above `user.save()`) adds no information and must be omitted
4.  **Comments explain WHY, not WHAT.** If a comment describes what the next line does, delete it; keep it only if it describes why that line exists in that form
5.  **Standard docstring structure:** a one-line summary in imperative mood (`"""Recompute the invoice total after a line item changes."""`); only add a body when the summary is not enough, separated from it by a blank line. Do not write multi-paragraph docstrings for behavior the name and signature already make obvious
6.  **Placement:** an inline `#` comment sits on its own line directly above the code it explains, not trailing at the end of a long statement
7.  **No process commentary in source.** Comments must never reference a task, a ticket, a previous version, or a caller (`# fix for issue #123`, `# added for the export flow`, `# removed old validation`) — that context belongs in the commit message or PR description, not in code that outlives them

**Incorrect (redundant comments, no comment where one is needed, wrong placement):**

```python
# ./apps/invoices/models/invoice.py

class Invoice(models.Model):
    # the total field
    total = models.DecimalField(_("total"), max_digits=10, decimal_places=2)

    def recompute_total(self):
        # loop over the items
        for item in self.items.all():
            # add item total to running total
            self.total += item.subtotal
        self.save()  # save the invoice

    def cancel(self):
        self.status = self.Status.CANCELLED
        # Bad: no comment — this call has a non-obvious side effect
        # (it fires the `invoice_cancelled` signal that reverses stock)
        self.save()
```

```python
# ./apps/users/serializers/user_create_serializer.py

class UserCreateSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        from .user_retrieve_serializer import UserRetrieveSerializer  # added for the export flow

        return UserRetrieveSerializer(instance, context=self.context).data
```

**Correct (comments limited to what the code cannot say, English, standard structure):**

```python
# ./apps/invoices/models/invoice.py

class Invoice(models.Model):
    total = models.DecimalField(_("total"), max_digits=10, decimal_places=2)

    def recompute_total(self):
        for item in self.items.all():
            self.total += item.subtotal
        self.save()

    def cancel(self):
        self.status = self.Status.CANCELLED
        # Triggers `invoice_cancelled`, which reverses the stock reservation
        self.save()
```

```python
# ./apps/users/serializers/user_create_serializer.py

class UserCreateSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        # Deferred import breaks the circular reference with UserRetrieveSerializer
        from .user_retrieve_serializer import UserRetrieveSerializer

        return UserRetrieveSerializer(instance, context=self.context).data
```

```python
# ./apps/payments/services/gateway.py

def charge(order: Order) -> PaymentResult:
    """Charge the order total through the payment gateway.

    Retries once on a network timeout because the gateway's sandbox
    drops roughly 1 in 20 requests without processing the charge.
    """
    ...
```

Reference: [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
