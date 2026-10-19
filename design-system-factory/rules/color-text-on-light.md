---
title: Text on White Is secondary-950
impact: CRITICAL
description: All text on white uses the darkest secondary step; supporting text uses secondary-600 or, at minimum, the lightest step that measures 4.5:1; tinted backgrounds follow color-50-950-convention
tags: color, text, contrast, typography
---

## Text on White Is secondary-950

**Impact (CRITICAL):** Mid-gray or brand-colored body text fails contrast on print and screens. One dark text tone gives maximum legibility and a consistent page.

**Guidelines:**

1. Main text: `secondary-950` (19.8:1 on `white` in the reference)
2. Supporting text: `secondary-600`; the lightest allowed is the lightest step that measures ≥ 4.5:1 on `white` (reference: `secondary-500` in _ASKIT_)
3. Links are distinguished by underline, not by color
4. Disabled text (`secondary-400`) is the only lighter exception
5. On tinted backgrounds, text follows `color-50-950-convention`

**Incorrect (gray body text):**

```css
.card__text {
  color: var(--secondary-400);
} /* 2.5:1 */
a {
  color: var(--primary-500);
}
```

**Correct (dark text, gray support):**

```css
.card__title {
  color: var(--secondary-950);
}
.card__text {
  color: var(--secondary-600);
}
a {
  color: inherit;
  text-decoration: underline;
}
```

Reference: [WCAG 2.2 contrast (minimum)](https://www.w3.org/TR/WCAG22/#contrast-minimum)
