---
title: Report What to Review After Every Change
impact: MEDIUM
description: After each published change, state the version, what changed and exactly which overview sections and files the user must review word by word
tags: process, review, communication, changelog
---

## Report What to Review After Every Change

**Impact (MEDIUM):** The overview is long and the user approves its wording. Without a precise list of touched sections, edits slip through unreviewed and the documentation drifts from what the user approved.

**Guidelines:**

1. Close every change with the new version number and one sentence per change
2. List the overview sections to review word by word by their heading, quoting the changed phrase when it is short
3. List the files outside the overview that changed (component files, asset group files, changelog), and the previews and print files that changed, to check by eye
4. When nothing in the overview changed, say so explicitly
5. For a major version, repeat what breaks and what derived designs must update (for example, rename `folder__icon` to `folder__bullet`)

**Incorrect (a vague closing):**

```text
Listo, actualicé la carpeta y la documentación.
```

**Correct (a precise review list):**

```md
Publiqué la versión 8.0.1: la ranura de la tarjeta queda centrada en la altura del bolsillo.
Vista general: no cambia ninguna sección.
Fuera de la vista general: la línea "Ranura de la tarjeta" en la ficha de `folder` y la entrada 8.0.1 del registro de cambios.
Para revisar a ojo: la vista previa de `folder` y `print__folder--229x305.pdf`.
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
