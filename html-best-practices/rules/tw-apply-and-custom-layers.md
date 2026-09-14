---
title: '@apply, Custom Utilities & Overrides'
impact: HIGH
description: Restricts @apply to genuine escape hatches, routes real reuse through components or @utility, and forbids important-flag overrides.
tags: tailwind, css, layers
---

## @apply, Custom Utilities & Overrides

**Impact (HIGH):** `@apply` recreates the exact problem utility CSS removes — a growing semantic class layer with its own naming debate, its own specificity conflicts, and its own dead code that nobody dares delete. Where a project merges class strings with a helper such as `tailwind-merge`, an `@apply` class is also invisible to it, so `.btn` and a caller's `bg-red-500` fight by stylesheet order instead of merging correctly. Reuse belongs in a component or template partial; a genuinely new primitive belongs in `@utility`.

**Guidelines:**

1.  **Reuse is a component boundary:**
    - Repeating a utility set means a component is missing, not that a CSS class is missing
    - This holds in template languages too: a partial or include is the reuse unit
2.  **When `@apply` is acceptable:**
    - Markup you do not control: third-party widgets, rich text from a CMS, generated output
    - A handful of base element styles inside `@layer base`
    - Not for building an in-house component library out of class names
3.  **Real primitives use `@utility`:**
    - A custom utility declared with `@utility` participates in variants (`hover:`, `md:`, `dark:`) and in merge ordering
    - A plain `@layer components` class does neither, which is why it eventually needs the important flag
    - Where a merge helper such as `tailwind-merge` is used, register the custom utility with `extendTailwindMerge` or the merge stops working for it — it only knows _Tailwind_'s own conflict groups, so a custom `@utility` is invisible to it and two conflicting ones both survive
4.  **Never win with the important flag:**
    - In v4 it is a suffix (`bg-red-500!`, not `!bg-red-500`)
    - Its presence in a diff signals a composition problem — usually a component that ignores the class it is given, or an `@apply` class outranking a utility
    - Against a generated component it signals the same thing and has a different fix: pass the utility through the class prop and let the merge helper resolve it, never edit the generated file and never add a defeating class beside it
5.  **`@reference` in separate stylesheets:**
    - `@apply` inside a separate _CSS_ module needs `@reference "…/app.css"` so the theme resolves; without it the build fails or silently drops the styles

**Incorrect (semantic class layer built with @apply, important flag to override it):**

```css
/* ./app/styles/app.css */
@import 'tailwindcss';

/* Bad: a component library made of class names */
@layer components {
  .btn {
    @apply rounded-md px-4 py-2 font-medium;
  }
  .btn-primary {
    @apply btn bg-primary text-primary-foreground;
  }
}
```

```html
<!-- Bad: the utility loses to .btn-primary, so it needs the important flag -->
<button type="button" class="btn-primary bg-red-600!">Delete</button>
```

**Correct (component owns the reuse, @utility for a real primitive, @apply only for foreign markup):**

```css
/* ./app/styles/app.css */
@import 'tailwindcss';

/* Good: a new primitive that composes with variants — hover:scrollbar-none works */
@utility scrollbar-none {
  scrollbar-width: none;
  &::-webkit-scrollbar {
    display: none;
  }
}

@layer base {
  /* Good: element defaults, in the one layer every utility still outranks */
  body {
    @apply bg-background text-foreground antialiased;
  }

  /* Good: the only markup that cannot be restructured — CMS rich text. mt-8
     is a deliberate exception to a mb-* spacing convention: the preceding
     sibling is not owned by this component */
  .prose-cms h2 {
    @apply mt-8 text-xl font-semibold;
  }
}
```

```html
<!-- No important flag needed: a merge helper resolves the conflict when the
     button component composes its base classes with a caller's override -->
<button type="button" class="bg-red-600">Delete</button>
```

Reference: [Functions and directives](https://tailwindcss.com/docs/functions-and-directives)
