---
title: Name Everything in English With BEM
impact: CRITICAL
description: Classes, files and folders use BEM in English, custom properties, ids and attributes use English kebab-case, and only human-facing text is in Spanish
tags: naming, bem, english, classes, files
---

## Name Everything in English With BEM

**Impact (CRITICAL):** Mixed languages and ad-hoc names make the system impossible to search, extend or consume from code. One methodology in one language keeps every name predictable.

**Guidelines:**

1. Classes, files and folders use `block__element--modifier`, lowercase, no accents or spaces, single hyphens between words of the same part; measured values in file names use `key_value` (see `name-files-bem`)
2. Custom properties (`--slogan-lead`), ids (`modal-1-title`) and data attributes use lowercase kebab-case in English
3. Never use Spanish words or abbreviations as names (`titulo`, `p5`, `s8`), except the _Tailwind CSS_ scale names (`xs`, `sm`, `lg`, `2xl`…) and the `ds-` helper prefix
4. Keep platform-imposed names as documented exceptions (for example a `Cover` folder required by the artifact type)

**Incorrect (Spanish and cryptic names):**

```css
.tarjeta-titulo {
}
.p5 {
  fill: var(--primary-500);
}
--slogan-principal: 24px;
```

**Correct (_BEM_ in English):**

```css
.card__title {
}
.cover__primary {
  fill: var(--primary-500);
}
--slogan-main: 24px;
```

Reference: [BEM naming](https://getbem.com/naming/)
