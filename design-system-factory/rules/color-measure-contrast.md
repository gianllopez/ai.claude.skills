---
title: Measure Contrast Before Choosing a Pair
impact: HIGH
description: Every text, icon and control color pair is checked numerically (4.5:1 text, 3:1 icons, control borders and large text) and the ratio is cited
tags: color, contrast, accessibility, wcag
---

## Measure Contrast Before Choosing a Pair

**Impact (HIGH):** Contrast judged by eye fails on dim screens and cheap print. Measured ratios make conflicts objective when discussing a user's request.

**Guidelines:**

1. Compute the _WCAG_ relative-luminance ratio for each new pair
2. Text ≥ 4.5:1; icons, control borders and text ≥ 24px at any weight ≥ 3:1; compare the unrounded value (4.47:1 fails 4.5:1)
3. Cite the ratio in the documentation next to the rule (`secondary-500` 4.5:1 on `white`)
4. When a requested pair fails, flag it with the number (see `scope-user-choice-flag-conflicts`)

**Incorrect (unverified pair):**

```md
- Íconos en `secondary-50` sobre `primary-500`.
```

**Correct (measured pair):**

```python
def L(h):
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def ratio(a, b):
    a, b = sorted((L(a), L(b)), reverse=True)
    return (a + 0.05) / (b + 0.05)
ratio('fafafa', 'ffa10b')  # secondary-50 on primary-500: 1.94 → fails 3:1
ratio('fafafa', '2a2a2a')  # secondary-50 on secondary-800: 13.8 → passes
```

Reference: [WCAG 2.2 contrast (minimum)](https://www.w3.org/TR/WCAG22/#contrast-minimum)
