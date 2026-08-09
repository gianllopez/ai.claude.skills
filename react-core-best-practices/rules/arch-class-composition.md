---
title: Class Composition & Conditional Classes
impact: CRITICAL
description: Requires a merge-aware helper for conditional classes and forbids class names built by interpolation, which the Tailwind scanner cannot see.
tags: architecture, styling, composition
---

## Class Composition & Conditional Classes

**Impact (CRITICAL):** _TailwindCSS_ scans source files as plain text — it never executes them. A class assembled at runtime (`bg-${color}-500`) does not exist at build time, so the CSS is never generated and the element ships unstyled. The failure is invisible in development with a cached stylesheet and shows up in production. Separately, string concatenation produces conflicting utilities whose winner is decided by stylesheet order, not by which class was written last: `"p-2" + " p-4"` is not reliably `p-4`.

**Guidelines:**

1.  **One composition helper:**
    - Compose with `cn()` — `clsx` for conditionals, `tailwind-merge` for conflict resolution
    - `tailwind-merge` makes "last one wins" true, which is what every caller assumes
    - Neither platform gives you that for free, and for the same reason. On the web the stylesheet settles a conflict, not the order the classes were written in. _NativeWind_ resolves `className` styles in CSS specificity order too — by design, to keep native and web identical — so `bg-slate-500 bg-red-500` does not reliably paint red there either
    - `cva` also exports `cx`: it is `clsx` renamed and it merges nothing, so importing it instead of `cn()` silently reintroduces the conflict this rule exists to prevent. `classnames` is the same trap under another name — it concatenates conditionally and resolves nothing
    - One helper per project. Where a generator writes it — `shadcn init` on the web, its _React Native_ equivalents — that file is the one, and a second declared beside it is duplication rather than a preference
    - `tailwind-merge` only knows the framework's own conflict groups, so anything the project adds is invisible to it and two conflicting ones both survive. Register them with `extendTailwindMerge` in that same file
2.  **Never build class names dynamically:**
    - No interpolation, no concatenation of fragments, no `` `text-${size}` ``
    - Map values to **complete** static class strings in a lookup object
3.  **Variant APIs:**
    - Declare the variant matrix once — a lookup record for a single axis, `cva` beyond that — never nested ternaries inside the attribute
    - This rule keeps the record form; the `cva` matrix is written out in the extraction-threshold rule and used again in the custom-layers one
    - Either way the result is wrapped in `cn()`, so a caller's `className` still wins; `cva` composes its own base and variant strings without merging them
    - A combination that needs classes of its own is `compoundVariants` — `{ variant: 'danger', size: 'sm', class: 'ring-1 ring-destructive' }` — because a crossing of two axes is exactly what sends people back to the nested ternary
4.  **Reusable components accept `className`:** - Take a `className` prop and merge it **last**, so callers can override defaults - A component that ignores `className` forces the next developer to wrap it in a `div`
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

**Correct (React DOM) — static maps, `cn()` merge, caller override wins:**

```ts
// ./app/core/lib/utils.ts — one per project, wherever the platform's generator
// puts it. Identical on both, which is why it is declared once here
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

**Correct (React Native) — the same helper, the same maps, the same merge:**

```tsx
import { cn } from '~/core/lib/utils';

export const TONES = {
  info: 'bg-info',
  danger: 'bg-destructive',
} as const;

export const SIZES = {
  sm: 'p-3',
  lg: 'p-6',
} as const;

type Props = React.ComponentProps<typeof View> & {
  tone: keyof typeof TONES;
  size: keyof typeof SIZES;
};

export function Alert({ tone, size, className, ...props }: Props) {
  return (
    <View
      // Good: complete static strings, className merged last. Without the merge
      // NativeWind settles p-6 against p-8 by specificity, not by who wrote last
      className={cn('rounded-md', TONES[tone], SIZES[size], className)}
      {...props}
    />
  );
}

<Alert tone="info" size="lg" className="p-8" />;
```

Reference: [tailwind-merge](https://github.com/dcastil/tailwind-merge) · [NativeWind style specificity](https://www.nativewind.dev/docs/core-concepts/style-specificity)
