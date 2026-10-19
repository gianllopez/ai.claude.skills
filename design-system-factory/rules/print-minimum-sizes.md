---
title: Keep Printed Text and Logos Above Their Minimums
impact: CRITICAL
description: Printed text is never below 9pt, sizes are multiples of 3pt, and printed logos never go below their minimum height
tags: print, typography, minimum size, logo
---

## Keep Printed Text and Logos Above Their Minimums

**Impact (CRITICAL):** Text below 9pt and undersized logos become unreadable on paper even when they look fine on screen.

**Guidelines:**

1. Sizes in multiples of 3pt (4px = 3pt): 9pt for footers, notes and senders; 12pt for body and tables
2. Business card: name 12pt; role and contact data 9pt, with the address split in two lines (street; city and country); slogan 9pt
3. Logo ≥ 8 mm high printed; symbol ≥ 5 mm
4. Write sizes in `pt` and `mm` at real size (see `print-real-size`) and check them before publishing

**Incorrect (small print):**

```css
.letter__footer {
  font-size: 6pt;
}
```

**Correct (minimums respected):**

```css
.letter__footer {
  font-size: 9pt;
}
.businesscard__role {
  font-size: 9pt;
}
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
