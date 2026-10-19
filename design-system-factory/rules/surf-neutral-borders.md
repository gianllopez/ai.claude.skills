---
title: Use the Neutral Scale for Borders on White and for Controls
impact: HIGH
description: Pieces on white and every form control use neutral borders at fixed steps; controls stay neutral even on colored fills
tags: surfaces, borders, neutral, controls
---

## Use the Neutral Scale for Borders on White and for Controls

**Impact (HIGH):** Form controls need 3:1 border contrast to be found; using the piece's tint for them makes inputs vanish.

**Guidelines:**

1. `neutral-200` (DEFAULT): cards, menus, dropdowns, modals, table outlines, dividers
2. `neutral-300`: disabled controls and tab hover
3. `neutral-400`: dashed reference zones (die-cut slots, safe areas)
4. `neutral-500`: form controls at rest (4.8:1 on `white`), never lighter
5. `neutral-800`: secondary button, checked controls, hover of controls and interactive cards, total rule in quotes and invoices; a field in error takes `error-700` (6.42:1 on `white`)
6. On `secondary-800`, `secondary-900` or `secondary-950` surfaces: `neutral-950` to separate surfaces (tooltip, toast); `neutral-400` for controls (5.52:1)

**Incorrect (light borders on controls):**

```css
.field__control {
  border: 1px solid var(--neutral-200);
} /* 1.2:1 */
.dropzone {
  border: 2px dashed var(--primary-200);
}
```

**Correct (neutral controls):**

```css
.field__control {
  border: 1px solid var(--neutral-500);
}
.dropzone {
  border: 2px dashed var(--neutral-500);
  background: var(--secondary-50);
}
.tooltip__text {
  background: var(--secondary-800);
  border: 1px solid var(--neutral-950);
}
```

Reference: [WCAG 2.2 non-text contrast](https://www.w3.org/TR/WCAG22/#non-text-contrast)
