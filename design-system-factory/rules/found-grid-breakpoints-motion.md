---
title: Use Standard Breakpoints, Grid and Motion
impact: MEDIUM
description: Layout follows the Tailwind CSS mobile-first breakpoints and a 4/8/12-column grid, and motion uses three durations that respect reduced motion
tags: layout, grid, breakpoints, motion
---

## Use Standard Breakpoints, Grid and Motion

**Impact (MEDIUM):** Custom breakpoints and animations make every derived design solve the same problems differently.

**Guidelines:**

1. Breakpoints `sm` 40rem (640px), `md` 48rem (768px), `lg` 64rem (1024px), `xl` 80rem (1280px), `2xl` 96rem (1536px), mobile first
2. Page container `max-w-7xl` with `px-6 lg:px-8`; running text up to `container-2xl`; grid 4 columns, 8 from `md`, 12 from `lg`, gap `spacing-6`
3. Motion: `duration-150 ease-out` hover and focus; `duration-200 ease-out` menus, tooltips, toasts; `duration-300 ease-in-out` modals and panels
4. Nothing loops except loaders; `prefers-reduced-motion` removes movement; with reduced motion, loaders keep a non-moving indicator (the text "Cargando…")

**Incorrect (custom values):**

```css
@media (max-width: 900px) { … }
.menu { transition: all 0.45s cubic-bezier(.2,.9,.3,1.4); }
```

**Correct (scale values):**

```css
.h1 {
  font-size: 1.875rem;
} /* phone */
@media (min-width: 48rem) {
  .h1 {
    font-size: 3rem;
  }
} /* from md */
.menu {
  transition: opacity 200ms ease-out;
}
@media (prefers-reduced-motion: reduce) {
  * {
    transition: none;
    animation: none;
  }
}
```

Reference: [Tailwind CSS responsive design](https://tailwindcss.com/docs/responsive-design)
