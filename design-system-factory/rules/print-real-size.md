---
title: Compose Print Pieces at Real Size
impact: MEDIUM
description: Print components are written at real size in CSS mm and pt, so the 4px = 3pt grid holds on every piece and the PDF needs no conversion; previews only enlarge them with zoom
tags: print, scale, preview, measures
---

## Compose Print Pieces at Real Size

**Impact (MEDIUM):** Per-piece px scales give "4px" a different real size in every piece, force decimal conversions and keep minimums from being checked at a glance.

**Guidelines:**

1. Write print components at real size with CSS `mm` and `pt`, on the standard CSS scale (1px = 0.75pt, 96px = 25.4 mm); never a per-piece px scale
2. Text sizes, spacing, logos and graphic devices in multiples of 3pt (4px = 3pt); `mm` only for physical measures (format, slots, bleed, safety margin)
3. Enlarge the preview with `zoom` inside `@media screen`, never by changing the measures
4. Render the PDF from the same CSS, where the screen zoom does not apply

**Incorrect (a per-piece px scale):**

```css
/* envelope DL at 3px = 1 mm */
.envelope {
  width: 660px;
  height: 330px;
}
.envelope__logo {
  height: 24px;
} /* 8 mm */
```

**Correct (real size, enlarged only on screen):**

```css
.envelope {
  width: 220mm;
  height: 110mm;
}
.envelope__logo {
  height: 24pt; /* 8.5 mm */
}
.envelope__sender {
  font-size: 9pt;
}
@media screen {
  .envelope {
    zoom: 1.5;
  }
}
```

Reference: [CSS absolute lengths](https://www.w3.org/TR/css-values-4/#absolute-lengths)
