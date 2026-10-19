---
title: Answer Briefly, in Prose
impact: MEDIUM
description: Reply in short Spanish prose, avoid long lists, and put the question as a subtitle when answering direct questions
tags: communication, style, answers
---

## Answer Briefly, in Prose

**Impact (MEDIUM):** The user reviews many changes in a row. Long enumerations and padding hide the one decision they need to make.

**Guidelines:**

1. Answer in Spanish (see `write-spanish-docs`) with the information needed and nothing else: no greetings, apologies or offers of further help
2. Prefer continuous prose; use a list only when the content is genuinely a set of parallel items
3. For direct questions ("¿Qué falta?", "¿Vale la pena…?"), repeat the question as a `###` subtitle and answer in the paragraph below
4. State facts only when they are verifiable; when they are not, say "Datos insuficientes para verificar"

**Incorrect (padded list answer):**

```md
¡Claro! Aquí tienes lo que falta:

1. Primero, ...
2. Además, ...

¿Quieres que te ayude con algo más?
```

**Correct (subtitle plus short prose):**

```md
### ¿Ese componente se usa en algún lado?

Sí, en una sola pieza: el reverso de `businesscard`, con la clase `businesscard__progression`.
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
