---
title: Apply Explicit Choices, Flag Conflicts
impact: HIGH
description: Grant the user's explicit design choices, but stop to flag any conflict with the system rules or with contrast before applying them
tags: process, decisions, contrast, conflicts
---

## Apply Explicit Choices, Flag Conflicts

**Impact (HIGH):** The user owns the brand decisions, yet a silent violation (low contrast, a rule broken in one piece) erodes the system. Flagging the conflict with concrete numbers keeps both the authority and the consistency.

**Guidelines:**

1. Apply what the user explicitly chose, in the user's words, without reinterpreting it
2. If the choice breaks a rule or a contrast threshold, say which rule and give the measured value (1.94:1 versus the 3:1 required)
3. Offer the conflicting option plus compliant alternatives as a multiple-choice question, recommended option first; legal requirements (tax ID, address and fiscal block on legal documents; see `piece-contact-data`, `piece-digital-documents`) are not offered as an option: explain why and keep them
4. When the user confirms a rule exception, document it as an exception in the affected component file
5. When the request is ambiguous and a wrong guess is cheap to redo, implement the most reasonable reading and say which reading was taken

**Incorrect (silently applying a low-contrast request):**

```text
User: "Íconos en tono 50 sobre el cuadro naranja."
Agent: applies secondary-50 on primary-500 (1.94:1) and publishes
```

**Correct (flagging with numbers and options):**

```text
Agent: "secondary-50 sobre primary-500 da 1.94:1; la regla de íconos pide 3:1."
Options: 1 · Sin cuadro, secondary-50 sobre secondary-800 (13.8:1) (Recommended)
         2 · Ícono secondary-950 (9.8:1) · 3 · Lo que pediste (1.94:1)
```

Reference: [WCAG 2.2 non-text contrast](https://www.w3.org/TR/WCAG22/#non-text-contrast)
