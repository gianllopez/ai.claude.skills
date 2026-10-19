---
title: Use the Spacing and Radius Scales With Fixed Assignments
impact: MEDIUM
description: Spacing uses the whole 4px steps of the Tailwind CSS scale and each radius step has an assigned use; brand graphics take the corner of the logo feature they derive from
tags: spacing, radius, layout, tokens
---

## Use the Spacing and Radius Scales With Fixed Assignments

**Impact (MEDIUM):** Without assignments every component picks its own padding and corner, and the family stops looking related.

**Guidelines:**

1. Spacing: multiples of 4px, only whole steps (`spacing-1`, `spacing-2`, `spacing-3`…); half steps (`0.5`, `1.5`, `2.5`, `3.5`) break the 4px grid; `spacing-1`/`2` icon gaps, `spacing-4` inside controls, `spacing-6` inside cards, `spacing-8` between blocks, `spacing-16`/`24` between sections
2. Radius: `sm` checkboxes; `lg` buttons, fields, icon boxes, menu options, tooltips, skeletons; `xl` alerts, menus, tables, toasts; `2xl` cards, panels; `3xl` modals; `full` pills, avatars, switches, counters; `md` (6px) is not used because it breaks the 4px grid
3. Patterns and brand graphics take the corner of the logo feature they derive from (reference: `radius-none` in _ASKIT_, from the square dot)
4. No values outside the scales

**Incorrect (arbitrary values):**

```css
.card {
  padding: 22px;
  border-radius: 10px;
}
.progression__step {
  border-radius: 2px;
}
```

**Correct (scale values):**

```css
.card {
  padding: var(--spacing-6);
  border-radius: var(--radius-2xl);
}
.progression__step {
  border-radius: 0;
}
```

Reference: [Tailwind CSS theme variables](https://tailwindcss.com/docs/theme)
