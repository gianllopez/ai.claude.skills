---
title: Use the Brand Color as Fill, Not as Text on Light
impact: HIGH
description: When the main brand color fails text contrast on light backgrounds, it is a fill there (buttons, tags, bands, squares), never text or an icon; text on it is the tone that passes the measured contrast
tags: color, brand, buttons, contrast
---

## Use the Brand Color as Fill, Not as Text on Light

**Impact (HIGH):** Saturated brand colors such as orange rarely reach 4.5:1 on white, and white text on them fails too. Using the brand color as a surface keeps it visible without harming legibility.

**Guidelines:**

1. When `primary-500` fails 4.5:1 on light backgrounds (reference: the _ASKIT_ orange), use it there only as fill, never as text or an icon
2. Text on the brand fill is the palette tone that passes the measured contrast (see `color-measure-contrast`); reference: `secondary-950` on `primary-500` and `primary-600` (9.8:1 and 7.6:1), never `white`, which fails on orange
3. On `secondary-800`, `secondary-900` or `secondary-950`, `primary-500` may be text, a title or a link
4. The brand scale is never a status color

**Incorrect (orange text and white on orange):**

```css
.eyebrow {
  color: var(--primary-500);
} /* on white */
.button--primary {
  background: var(--primary-500);
  color: var(--white);
}
```

**Correct (orange as fill):**

```css
.button--primary {
  background: var(--primary-500);
  color: var(--secondary-950);
}
.footer__title {
  color: var(--primary-500);
} /* on secondary-800 */
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
