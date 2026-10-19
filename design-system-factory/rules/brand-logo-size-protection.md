---
title: Respect Logo Minimum Sizes, Clear Space and Misuse Rules
impact: CRITICAL
description: The logo keeps a clear space of 2X, never goes below its minimum screen and print sizes, and is never distorted, rotated or placed on the brand color
tags: logo, minimum size, clear space, misuse
---

## Respect Logo Minimum Sizes, Clear Space and Misuse Rules

**Impact (CRITICAL):** An undersized or crowded logo becomes illegible in print and on small screens; misuse breaks recognition faster than any other error.

**Guidelines:**

1. Clear space: 2X on every side, where X is a defined logo measure (reference: the width of the square dot of the "i")
2. Minimums (reference): primary 24px on screen and 8 mm printed; symbol 16px and 5 mm; below the primary minimum, use the symbol
3. Check every component: any logo element below the minimum is a defect (reference: `report__symbol` raised from 12pt, 4.2 mm, to 15pt, 5.3 mm)
4. Never distort, rotate, separate or reorder parts, add shadows or effects, retype the text, or place it on `primary-500`

**Incorrect (undersized symbol):**

```css
.report__symbol {
  height: 12pt;
} /* 4.2 mm, below the 5 mm symbol minimum */
```

**Correct (minimum respected):**

```css
.report__symbol {
  height: 15pt;
} /* 5.3 mm ≥ 5 mm */
.letter__logo {
  height: 24pt;
} /* 8.5 mm ≥ 8 mm */
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
