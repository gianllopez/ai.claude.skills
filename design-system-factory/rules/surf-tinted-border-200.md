---
title: Border Tinted Pieces With Their Own Scale at 200
impact: HIGH
description: A piece with a -50 or -100 background has a border of the same scale at step 200, including its inner dividers
tags: surfaces, borders, tinted, badges, alerts
---

## Border Tinted Pieces With Their Own Scale at 200

**Impact (HIGH):** A gray border cuts a tinted surface; a border from the same hue frames it and keeps tinted pieces consistent.

**Guidelines:**

1. `<status>-50` → border `<status>-200` (alerts, status badges)
2. Any brand scale (`primary`, `tertiary`…) `-50`/`-100` → its own `-200` (reference: `primary` in the brand badge, avatar, icon boxes, callouts)
3. `secondary-50`/`100` → `secondary-200` (neutral badge, counters, sidebar, table header, email footer, legal block)
4. Inner dividers of a tinted piece use the same `-200`
5. Hover fills, disabled controls and skeleton loaders are states, not pieces: hover and disabled follow `surf-interaction-states` and skeletons their component file; controls keep their neutral border on a tint (see `surf-neutral-borders`)
6. List every tinted piece in the Borders section of the overview

**Incorrect (tint without border or with gray):**

```css
.card__icon {
  background: var(--primary-100);
}
.alert--info {
  background: var(--info-50);
  border: 1px solid var(--neutral-200);
}
```

**Correct (same-scale border):**

```css
.card__icon {
  background: var(--primary-100);
  border: 1px solid var(--primary-200);
}
.alert--info {
  background: var(--info-50);
  border: 1px solid var(--info-200);
}
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
