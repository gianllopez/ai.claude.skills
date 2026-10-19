---
title: Define One Focus Ring and Fixed Hover and Disabled States
impact: HIGH
description: Focus, hover and disabled states are system-wide constants, not per-component inventions
tags: states, focus, hover, disabled, accessibility
---

## Define One Focus Ring and Fixed Hover and Disabled States

**Impact (HIGH):** Different focus styles per component confuse keyboard users and fail audits; fixed states also make derived designs predictable.

**Guidelines:**

1. Focus: one ring, `outline: 2px solid secondary-800` with `outline-offset: 2px`; on `secondary-800`, `secondary-900` or `secondary-950` surfaces the ring is `primary-500`
2. Hover: filled elements go one step lighter (`primary-500` → `primary-400`); transparent or `white` elements take `secondary-100`, and `secondary-700` on dark surfaces; hover styles go inside `@media (hover: hover)` so they do not stick on touch screens
3. Disabled: background `secondary-100`, text `secondary-400`, border `neutral-300` (`neutral-200` on buttons)
4. Never remove the outline without replacing it

**Incorrect (removed outline):**

```css
.button:focus {
  outline: none;
}
```

**Correct (single ring):**

```css
.button:focus-visible {
  outline: 2px solid var(--secondary-800);
  outline-offset: 2px;
}
.footer :focus-visible {
  outline-color: var(--primary-500);
}
@media (hover: hover) {
  .button--primary:hover {
    background: var(--primary-400);
  }
}
```

Reference: [WCAG 2.2 focus visible](https://www.w3.org/TR/WCAG22/#focus-visible)
