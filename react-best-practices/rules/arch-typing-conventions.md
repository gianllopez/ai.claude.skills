---
title: Component Typing Conventions
impact: HIGH
description: Types component props from the underlying element, models mutually exclusive props as unions, and keeps any and non-null assertions out of the component surface.
tags: architecture, typescript, components
---

## Component Typing Conventions

**Impact (HIGH):** A component's props are its _API_. Hand-written prop types inevitably forget `id`, `onBlur`, or `data-*`, forcing every caller to patch around the component; independent optional booleans let the compiler accept combinations the component cannot render. Deriving the type from the element and modelling exclusivity turns those into compile errors instead of review comments.

**Guidelines:**

1.  **The props type is always declared, and it is always `Props`:**
    - Declare it even when it is a bare alias — `type Props = React.ComponentProps<'button'>` — so every component file has the same shape and the component's surface has one obvious place to look
    - Annotating props inline in the signature buries the surface inside the parameter list; a bespoke name (`ButtonProps`, `CardProps`) costs a lookup and carries no information the filename does not
    - Export it only when another module actually consumes it
    - When a module holds more than one component — a compound set like `Card` / `CardHeader` / `CardBody` — every type is qualified with its own component's name (`CardProps`, `CardHeaderProps`, `CardBodyProps`), so no two of them compete for the same name
    - Route components are the exception: the framework generates their props type — the params it parsed and whatever else it injects — so annotate with that generated type directly instead of aliasing it
2.  **Extend the underlying element:**
    - `React.ComponentProps<'button'>` or `React.ComponentProps<typeof Link>` instead of redeclaring `onClick`, `disabled`, and `className` by hand
3.  **Model exclusivity, do not hope for it:**
    - Props that cannot coexist are a discriminated union, not three optional booleans
4.  **No `React.FC`:**
    - It adds nothing over typing the props parameter, and historically dragged an implicit `children` along
5.  **Derive from the source of truth:**
    - `VariantProps<typeof BUTTON_VARIANTS>` for variants, the `Data` type a query hook already declares for server data, `keyof typeof MAP` for lookup keys
    - A type that restates a value can drift from it; a type derived from it cannot
6.  **`any` and `!` are review flags in a signature:**
    - `unknown` plus a narrowing check is the honest version; a non-null assertion is a claim the compiler could not verify
7.  **Type the input, infer the output:**
    - Annotating the return adds noise and breaks the moment the component returns `null`

**Incorrect (hand-rolled surface, impossible states allowed, `any` in the handler):**

```tsx
// Bad: a bespoke name for the one thing every component file already has
type ButtonProps = {
  children: ReactNode;
  onClick: (e: any) => void;
  isPrimary?: boolean;
  isDanger?: boolean;
  isGhost?: boolean;
};

// Bad: React.FC, and callers cannot pass id, type, form, disabled or data-* at all
export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  isPrimary,
  isDanger,
}) => (
  <button
    onClick={onClick}
    className={cn(isPrimary && 'bg-primary', isDanger && 'bg-destructive')}
  >
    {children}
  </button>
);

// Compiles cleanly, renders something nobody designed
<Button isPrimary isDanger onClick={handleDelete}>
  Delete
</Button>;
```

**Correct (element props plus a single variant axis derived from the variants function):**

```tsx
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

// Every native prop works, and the impossible combination no longer type-checks
<Button
  type="button"
  variant="danger"
  size="sm"
  form="invoice-form"
  onClick={handleDelete}
>
  Delete
</Button>;
```

Reference: [TypeScript with React components](https://react.dev/learn/typescript#typescript-with-react-components)
