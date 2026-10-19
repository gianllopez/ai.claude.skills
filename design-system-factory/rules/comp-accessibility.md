---
title: Build Accessible Semantics Into Every Component
impact: HIGH
description: Components use native elements and ARIA roles, give names to icon-only controls and charts, and support keyboard use
tags: components, accessibility, aria, keyboard
---

## Build Accessible Semantics Into Every Component

**Impact (HIGH):** Accessibility retrofitted in each derived design is inconsistent; baked into the component it comes for free.

**Guidelines:**

1. Native elements first (`button`, `label` + `input`, `nav`, `table`); _ARIA_ roles where needed (`tablist`/`tab`, `switch`, `alert`, `dialog`)
2. Icon-only controls with `aria-label`; decorative graphics with `aria-hidden="true"`
3. Charts: `svg` with `role="img"` and an `aria-label` stating the conclusion and key figures; in apps, data also in a `table`
4. Keyboard: tabs move with arrows, menus with arrows and `Esc`, sidebar panel closes with `Esc`; modals close with `Esc`, keep focus inside while open and return it to the control that opened them
5. Text fields (`field`, `select`, `search`, `date`) use at least 16px font, so phones do not zoom in on focus
6. Interactive targets at least 24 × 24px; 44 × 44px on touch screens

**Incorrect (div soup):**

```html
<div class="tabs"><div onclick="show(1)">Resumen</div></div>
<svg class="chart__plot">…</svg>
```

**Correct (semantic and named):**

```html
<div class="tabs" role="tablist">
  <button class="tabs__tab" role="tab" aria-selected="true">Resumen</button>
</div>
<svg
  class="chart__plot"
  role="img"
  aria-label="Las facturas procesadas crecieron un 41 % en seis meses: de 310 a 436."
>
  …
</svg>
```

Reference: [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
