---
title: '@apply, Custom Utilities & Overrides'
impact: HIGH
description: Restricts @apply to genuine escape hatches, routes real reuse through components or @utility, and forbids important-flag overrides.
tags: tailwind, css, layers
---

## @apply, Custom Utilities & Overrides

**Impact (HIGH):** `@apply` recreates the exact problem utility CSS removes — a growing semantic class layer with its own naming debate, its own specificity conflicts, and its own dead code that nobody dares delete. It is also invisible to `tailwind-merge`, so `.btn` and a caller's `bg-red-500` fight by stylesheet order. Reuse belongs in a component; a genuinely new primitive belongs in `@utility`.

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
4.  **Never win with the important flag:**
    - In v4 it is a suffix (`bg-red-500!`, not `!bg-red-500`)
    - Its presence in a diff signals a composition problem — usually a component that ignores `className`, or an `@apply` class outranking a utility
    - Against a generated component it signals the same thing and has a different fix: pass the utility through `className` and let `tailwind-merge` resolve it, never edit the file under `core/lib/shadcn/` and never add a defeating class beside it (see the folder-structure rule)
5.  **`@reference` in separate stylesheets:**
    - `@apply` inside a _CSS_ module needs `@reference "…/app.css"` so the theme resolves; without it the build fails or silently drops the styles

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

```tsx
// Bad: the utility loses to .btn-primary, so it needs the important flag
<button type="button" className="btn-primary bg-red-600!">
  Delete
</button>
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

  /* Good: the only markup we cannot restructure — CMS rich text. mt-8 is the
     declared exception to the mb-* convention: the preceding sibling is not
     ours to space */
  .prose-cms h2 {
    @apply mt-8 text-xl font-semibold;
  }
}
```

```tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '~/core/lib/utils';

export const BUTTON_VARIANTS = cva(
  'inline-flex items-center gap-2 rounded-md font-medium [&_svg]:size-4',
  {
    variants: {
      variant: {
        primary: 'bg-primary text-primary-foreground',
        danger: 'bg-destructive text-destructive-foreground',
      },
      size: {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  },
);

type Props = React.ComponentProps<'button'> &
  VariantProps<typeof BUTTON_VARIANTS>;

export function Button({ variant, size, className, ...props }: Props) {
  return (
    <button
      className={cn(BUTTON_VARIANTS({ variant, size }), className)}
      {...props}
    />
  );
}

// No important flag needed: tailwind-merge resolves the conflict
<Button type="button" variant="primary" className="bg-red-600">
  Delete
</Button>;
```

Reference: [Functions and directives](https://tailwindcss.com/docs/functions-and-directives)
