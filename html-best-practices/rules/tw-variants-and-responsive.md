---
title: Responsive & Variant Usage
impact: HIGH
description: Enforces mobile-first breakpoints, group and peer variants, container queries, and single-tree dark mode instead of duplicated markup.
tags: tailwind, responsive, variants, css
---

## Responsive & Variant Usage

**Impact (HIGH):** Rendering the same content twice — once for mobile, once for desktop — doubles the DOM, duplicates every future edit, and guarantees the two copies drift. The same applies to a second template for dark mode. Variants exist so one tree covers every context; reaching for a script-driven breakpoint check moves layout decisions off the platform and into a render cycle that runs after paint.

**Guidelines:**

1.  **Mobile-first:**
    - Unprefixed utilities are the base; `sm:` / `md:` / `lg:` apply from that breakpoint up
    - `max-*` variants only when the design genuinely inverts at a breakpoint, not as a default style
2.  **One tree per content:**
    - `block md:hidden` paired with `hidden md:block` for the same content is duplication — restyle the single tree instead
    - Acceptable only when mobile and desktop render genuinely different content, not a different arrangement of the same content
3.  **Relationship variants over lifted state:**
    - Parent hover / focus: mark the parent `group`, style children with `group-hover:`
    - Sibling state: mark the input `peer`, style with `peer-checked:` / `peer-disabled:`
    - These replace state that only existed to drive a class
4.  **Container queries for components:**
    - When a component's width is not the viewport's (sidebar, modal, grid cell), use `@container` on the wrapper and `@sm:` / `@md:` on children
    - A card that must look right in two column widths is a container-query problem, not a breakpoint problem
5.  **Dark mode belongs to the theme, not to the components:**
    - `bg-card` is already right in both themes, because `--card` is what changes under `.dark` (see the theme-tokens rule for the variant that wires it)
    - A `dark:` inside a component is therefore a signal: it says the element was painted with something that does not change — a palette step — and the fix is the token, not the variant
    - Where `dark:` genuinely earns its place — a raster image, a shadow, a third-party surface that cannot be tokenised — it is a variant on the same element, never a parallel template
6.  **No script-driven breakpoints for layout:**
    - A media-query hook or listener driving pure layout duplicates CSS in _JavaScript_ and flashes on first render

**Incorrect (duplicated trees, dark mode as a second template):**

```html
<!-- Bad: a whole second template for a colour the theme already swaps -->
<template id="product-card-dark"> ... </template>

<!-- Bad: the same content rendered twice -->
<div class="block bg-card p-4 md:hidden">
  <h3 class="text-base">Wireless Mouse</h3>
  <p class="text-sm">$29.99</p>
</div>
<div class="hidden bg-card p-8 md:block">
  <h3 class="text-xl">Wireless Mouse</h3>
  <p class="text-base">$29.99</p>
</div>
```

**Correct (one tree, mobile-first variants, container query, dark resolved in the theme):**

```html
<div class="@container">
  <!-- Good: no dark: anywhere — the token already changes with the theme -->
  <article class="bg-card p-4 @md:p-8">
    <h3 class="text-base @md:text-xl">Wireless Mouse</h3>
    <p class="text-sm @md:text-base">$29.99</p>
  </article>
</div>
```

```html
<!-- group and peer replace state that only drove a class -->
<a
  href="/reports"
  class="group flex items-center gap-2 rounded-md p-3 hover:bg-accent"
>
  <span class="text-muted-foreground group-hover:text-primary">Reports</span>
</a>

<label class="flex items-center gap-2">
  <input type="checkbox" name="archived" class="peer sr-only" />
  <span
    class="rounded-md border px-3 py-1 peer-checked:border-primary peer-checked:bg-accent"
  >
    Include archived
  </span>
</label>
```

Reference: [Responsive design](https://tailwindcss.com/docs/responsive-design)
