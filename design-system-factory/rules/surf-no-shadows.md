---
title: Separate Surfaces With Borders, Never Shadows
impact: CRITICAL
description: No shadow of any kind is used; every surface that needs separation gets a 1px border
tags: surfaces, borders, shadows, elevation
---

## Separate Surfaces With Borders, Never Shadows

**Impact (CRITICAL):** Shadows disappear in print, render differently per screen and conflict with the flat language of the brand.

**Guidelines:**

1. No `box-shadow`, `drop-shadow`, `text-shadow` or inset shadows, including on overlays (menus, modals, toasts); _Tailwind CSS_ `ring-*` utilities are shadows too, so use `outline-*` (see `surf-interaction-states`)
2. Every card, menu, modal, table, tooltip and toast has a 1px border
3. Modals and side panels sit on a backdrop of `secondary-950` at 50 % opacity
4. The logo never gets shadows or effects either

**Incorrect (shadow for elevation):**

```css
.menu {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}
```

**Correct (border for separation):**

```css
.menu {
  border: 1px solid var(--neutral-200);
}
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
