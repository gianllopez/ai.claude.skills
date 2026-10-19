---
title: Size and Color Icons With the Text They Accompany
impact: MEDIUM
description: Icons use three sizes, inherit the tone of their text, keep fixed gaps and carry an accessible name when they stand alone
tags: icons, size, color, accessibility
---

## Size and Color Icons With the Text They Accompany

**Impact (MEDIUM):** Icons in arbitrary sizes and colors look pasted on; icon-only buttons without names are invisible to screen readers.

**Guidelines:**

1. Sizes: `ds-icon` 24px, the default; `ds-icon--sm` 20px next to `text-sm`; `ds-icon--xs` 16px next to `text-xs`
2. Color: `currentColor`; `secondary-950` on `white`, `white` on `secondary-800`, the 50/950 pair on tinted surfaces, `<status>-800` for status on `white`
3. Gap `spacing-2` (in tags `spacing-1`)
4. `Filled` weight only for active or selected states
5. Icon-only controls get `aria-label`; decorative icons get `aria-hidden="true"`

**Incorrect (arbitrary size and brand color):**

```html
<button><svg width="30" style="color:#ffa10b">…</svg></button>
```

**Correct (sized, inherited and named):**

```html
<button class="button button--icon-only" aria-label="Buscar">
  <svg class="ds-icon" aria-hidden="true" stroke="currentColor">…search…</svg>
</button>
```

Reference: [Reicon icons](https://reicon.dev/icons)
