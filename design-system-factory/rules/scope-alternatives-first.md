---
title: Propose Rendered Alternatives Before Building
impact: HIGH
description: For every new or redesigned communication piece or graphic device, show several distinct rendered alternatives, let the user choose, then implement only the chosen one
tags: process, alternatives, review, decisions
---

## Propose Rendered Alternatives Before Building

**Impact (HIGH):** Brand pieces are judged by eye. Building one design directly forces rework when it misses; a sheet of options lets the user decide in one pass and leaves a record of why.

**Guidelines:**

1. Applies to communication pieces and graphic devices; interface components follow the rules directly
2. Render three or four alternatives that differ in concept, not only in color or size, at real proportions and with real brand assets
3. Aim for designs innovative enough to stand out without exaggeration; when the user rejects a round, the next round must be genuinely different
4. Label each option with a letter and a short name (A · Pie como la hoja carta) and state its trade-off in one line
5. Deliver the sheets as images or PDFs the user can open on the phone, and notify when they are ready
6. Implement only the chosen option, apply the user's follow-up adjustments literally, and record the decision in the changelog entry of the version that implements it, with the letter, the name and the adjustments (see `gov-versioning`)

**Incorrect (a single design built straight into the system):**

```text
User: "Necesito la carpeta."
Agent: builds folder v1 into bundle.css, regenerates the PDF and publishes it
```

**Correct (options first, implementation after the choice):**

```text
User: "Necesito la carpeta."
Agent: sends sheet__folder.png with A · Progresión, B · Eslogan a escala, C · Patrón de cuadrados
User: "Vamos con la B."
Agent: implements B, publishes, records "folder: B · Eslogan a escala (eslogan grande en la portada)" in the changelog
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
