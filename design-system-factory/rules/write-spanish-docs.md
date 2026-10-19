---
title: Document in Spanish, Name in English
impact: HIGH
description: Documentation, interface copy and every human-facing name are in Spanish; code names and code comments stay in English
tags: writing, language, spanish, documentation
---

## Document in Spanish, Name in English

**Impact (HIGH):** The audience of the brand pieces and of the documentation is Spanish-speaking, while the code is consumed by tools and developers. Mixing the two directions produces Spanish class names and English labels on screen.

**Guidelines:**

1. Write overview, component files, asset group files, changelog and every visible text (titles, labels, sample content) in Spanish
2. Keep file names, classes, tokens, variables and attributes in English (see `name-bem-english`)
3. Generated sections that the platform writes in English (for example "Consuming this system") stay as generated
4. Comments inside code are in English, like the names

**Incorrect (English copy and Spanish names):**

```html
<button class="boton boton--principal">Schedule a meeting</button>
```

**Correct (Spanish copy and English names):**

```html
<button class="button button--primary">Agenda una reunión</button>
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
