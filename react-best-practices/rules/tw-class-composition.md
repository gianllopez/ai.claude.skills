---
title: Class Composition & Conditional Classes
impact: CRITICAL
description: Requires a merge-aware helper for conditional classes and forbids class names built by interpolation, which the Tailwind scanner cannot see.
tags: tailwind, jsx, composition
---

## Class Composition & Conditional Classes

**Impact (CRITICAL):** _TailwindCSS_ scans source files as plain text — it never executes them. A class assembled at runtime (`bg-${color}-500`) does not exist at build time, so the CSS is never generated and the element ships unstyled. The failure is invisible in development with a cached stylesheet and shows up in production. Separately, string concatenation produces conflicting utilities whose winner is decided by stylesheet order, not by which class was written last: `"p-2" + " p-4"` is not reliably `p-4`.

**Guidelines:**

1.  **One composition helper:**
    - Compose with `cn()` — `clsx` for conditionals, `tailwind-merge` for conflict resolution
    - `tailwind-merge` makes "last one wins" true, which is what every caller assumes
    - `shadcn init` already wrote it at the path `components.json` points to, so a second helper declared beside it is duplication and not a preference
    - `cva` also exports `cx`: it is `clsx` renamed and it merges nothing, so importing it instead of `cn()` silently reintroduces the conflict this rule exists to prevent
    - `tailwind-merge` only knows _Tailwind_'s own conflict groups — a custom `@utility` is invisible to it and two conflicting ones both survive. Register them with `extendTailwindMerge` in that same file
2.  **Never build class names dynamically:**
    - No interpolation, no concatenation of fragments, no `` `text-${size}` ``
    - Map values to **complete** static class strings in a lookup object
3.  **Variant APIs:**
    - Declare the variant matrix once — a lookup record for a single axis, `cva` beyond that — never nested ternaries inside the attribute
    - This rule keeps the record form; the `cva` matrix is written out in the extraction-threshold rule and used again in the custom-layers one
    - Either way the result is wrapped in `cn()`, so a caller's `className` still wins; `cva` composes its own base and variant strings without merging them
    - A combination that needs classes of its own is `compoundVariants` — `{ variant: 'danger', size: 'sm', class: 'ring-1 ring-destructive' }` — because a crossing of two axes is exactly what sends people back to the nested ternary
4.  **Reusable components accept `className`:**
    - Take a `className` prop and merge it **last**, so callers can override defaults
    - A component that ignores `className` forces the next developer to wrap it in a `div`
5.  **An arbitrary variant is a selector living in a class attribute:**
    - `[&>*:nth-child(3)]:mt-0` styles by position, so it breaks the moment an element is inserted, and nothing in the markup says why the third child is special
    - The legitimate case is a slot this component does not render — `[&_svg]:size-4` on a button that accepts any icon
    - A cluster of them on one element is a structural finding: the child needs a component or a prop, not a longer selector

**Incorrect (interpolated class, template-literal concatenation, unmergeable override):**

```tsx
type Props = {
  tone: 'info' | 'danger';
  size: 'sm' | 'lg';
  className?: string;
};

export function Alert({ tone, size, className }: Props) {
  return (
    <div
      // Bad: these classes never exist at build time
      className={`rounded-md bg-${tone}-100 text-${tone}-800 p-${size === 'lg' ? 6 : 3} ${className}`}
    >
      ...
    </div>
  );
}

// The caller's p-8 may or may not win — it depends on stylesheet order
<Alert tone="info" size="lg" className="p-8" />;
```

```tsx
// Bad: every selector here targets a child this component renders itself, and the
// third-child rule silently moves to another row the moment one is inserted
<ul className="[&>li]:px-3 [&>li:first-child]:rounded-t-md [&>li:nth-child(3)]:mt-0">
  <li>Draft</li>
  <li>In review</li>
  <li>Published</li>
</ul>
```

**Correct (static maps, cn() merge, caller override wins):**

```ts
// ./app/core/lib/utils.ts — written by `shadcn init`, not by hand
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs));
```

```tsx
import { cn } from '~/core/lib/utils';

export const TONES = {
  info: 'bg-info text-info-foreground',
  danger: 'bg-destructive text-destructive-foreground',
} as const;

export const SIZES = {
  sm: 'p-3 text-sm',
  lg: 'p-6 text-base',
} as const;

type Props = React.ComponentProps<'div'> & {
  tone: keyof typeof TONES;
  size: keyof typeof SIZES;
};

export function Alert({ tone, size, className, ...props }: Props) {
  return (
    <div
      // Good: complete static strings, className merged last
      className={cn('rounded-md', TONES[tone], SIZES[size], className)}
      {...props}
    />
  );
}

// p-8 reliably wins: tailwind-merge drops the conflicting p-6
<Alert tone="info" size="lg" className="p-8" />;
```

```tsx
export const BUTTON_VARIANTS = cva(
  // Good: the icon arrives as a child, so no element in this file can carry its
  // size — reaching it with a selector is the case the syntax exists for, and it
  // belongs in the variant base rather than in a caller's cn()
  'inline-flex items-center gap-2 rounded-md font-medium [&_svg]:size-4',
  {
    // ...
  },
);

<Button type="button" variant="danger" size="sm">
  <TrashIcon />
  Delete
</Button>;
```

Reference: [tailwind-merge](https://github.com/dcastil/tailwind-merge)
