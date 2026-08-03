---
title: Component Extraction Threshold
impact: HIGH
description: Defines when repeated utility strings become a component and how that component exposes its styling API.
tags: architecture, components, reuse
---

## Component Extraction Threshold

**Impact (HIGH):** Utility CSS trades CSS duplication for markup duplication — that trade is only worth it if the markup is extracted at the right moment. Extract too early and the codebase fills with single-use wrappers that add indirection without removing anything. Extract too late and a design change means editing the same string in eleven files, missing two.

**Guidelines:**

1.  **The threshold:**
    - Extract on the third occurrence, or on the first occurrence that carries behavior or state
    - Two occurrences are cheaper to read inline than to look up
2.  **Extract decisions, not layout:**
    - A repeated string that encodes a decision — a variant, a size, a brand surface — is a component
    - A repeated `flex items-center gap-2` is not; it is generic layout and extracting it hides what the markup does
3.  **A loop is not duplication:**
    - Markup repeated inside `map()` or a template loop is already defined once — no extraction is needed
4.  **The component owns its defaults:**
    - Defaults live inside; callers pass `className` and it is merged **last** through `cn()`
    - A component that ignores `className` forces wrapper `div`s at every call site
5.  **Variants are an API, not a class string:**
    - Expose `variant="danger"` / `size="sm"`; do not let callers assemble the visual state from utilities
    - One axis of variation is fine as a lookup record; two or more declare the matrix with `cva` and derive the props from `VariantProps`, so the variants stay typed and live in one place
    - Name the constant in upper snake case — `STATUS_PILL_VARIANTS`, `BUTTON_VARIANTS`, `STATUS_STYLES` — because it is a module-level constant, not a component or a hook, and the casing keeps that distinction visible at the call site
    - Export it next to the component so another element can borrow the styling — `<a className={BUTTON_VARIANTS({ variant: 'ghost' })}>` styles a real link without wrapping it in a `button`
    - The moment a caller needs `bg-red-600!` to override, the variant was missing
6.  **Do not extract a passthrough:**
    - A component that forwards props and adds one static class is a wrapper — inline it (see minimal markup depth)

**Incorrect (extracted too early as a passthrough, and duplicated where it mattered):**

```tsx
// Bad: a component that adds one class and hides nothing
export const Row = ({ children }: PropsWithChildren) => (
  <div className="flex items-center gap-2">{children}</div>
);

// Bad: the real decision — the status pill — is duplicated verbatim at each call site
<span className="rounded-full bg-success px-2 py-0.5 text-xs font-medium text-success-foreground">
  Active
</span>
<span className="rounded-full bg-destructive px-2 py-0.5 text-xs font-medium text-destructive-foreground">
  Failed
</span>
<span className="rounded-full bg-warning px-2 py-0.5 text-xs font-medium text-warning-foreground">
  Pending
</span>
```

**Correct (generic layout stays inline, the decision becomes a component with a typed variant API):**

```tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '~/core/lib/utils';

export const STATUS_PILL_VARIANTS = cva(
  'inline-flex items-center rounded-full font-medium',
  {
    variants: {
      status: {
        active: 'bg-success text-success-foreground',
        failed: 'bg-destructive text-destructive-foreground',
        pending: 'bg-warning text-warning-foreground',
      },
      size: {
        sm: 'px-2 py-0.5 text-xs',
        md: 'px-3 py-1 text-sm',
      },
    },
    defaultVariants: { status: 'active', size: 'sm' },
  },
);

type Props = React.ComponentProps<'span'> &
  VariantProps<typeof STATUS_PILL_VARIANTS>;

export function StatusPill({ status, size, className, ...props }: Props) {
  return (
    <span
      className={cn(STATUS_PILL_VARIANTS({ status, size }), className)}
      {...props}
    />
  );
}
```

```tsx
// Generic layout stays inline — no Row component needed
<div className="flex items-center gap-2">
  <StatusPill status="active">Active</StatusPill>
  <StatusPill status="pending" className="ml-auto">
    Pending
  </StatusPill>
</div>
```

Reference: [Managing duplication](https://tailwindcss.com/docs/styling-with-utilities#managing-duplication)
