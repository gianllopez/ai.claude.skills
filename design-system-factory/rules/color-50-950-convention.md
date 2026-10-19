---
title: Pair -50 Backgrounds With -950 Text
impact: HIGH
description: In every scale, a -50 background takes -950 text and a -950 background takes -50 text; lower emphasis moves two steps toward the background; on secondary-800 and -900 blocks, text is white and lower emphasis secondary-200
tags: color, contrast, convention, tinted surfaces
---

## Pair -50 Backgrounds With -950 Text

**Impact (HIGH):** A single pairing rule removes per-component guessing and guarantees contrast in tinted pieces (alerts, badges, callouts).

**Guidelines:**

1. On `-50`: text and icons `-950`; lower emphasis `-800`
2. On `-950`: text and icons `-50`; lower emphasis `-200`
3. On `secondary-800` and `secondary-900` blocks: text and icons `white`; lower emphasis `secondary-200`; measure both (see `color-measure-contrast`)
4. Never combine a `-50` or `-950` background with text from another scale; the only exception is `primary-500` on dark `secondary` blocks (see `color-brand-fill-only`)
5. Icons take the tone of the text they accompany

**Incorrect (mixed scales on a tint):**

```css
.report__callout {
  background: var(--primary-50);
  color: var(--secondary-600);
}
```

**Correct (same-scale pairing):**

```css
.report__callout {
  background: var(--primary-50);
  color: var(--primary-950);
  border: 1px solid var(--primary-200);
}
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
