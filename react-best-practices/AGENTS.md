# React Best Practices

**Version 1.0.0**  
_Gian López_  
_August 2026_

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring _React_ and _TailwindCSS_ codebases. Humans  
> may also find it useful, but guidance here is optimized for automation  
> and consistency by AI-assisted workflows.

---

## Abstract

Review-oriented standards for _React_ applications, ordered by what actually breaks under review: effects and state first, because a misplaced `useEffect` or a duplicated source of truth is a behavioral defect; then data ownership, where a typed query layer holds the cache and components consume state instead of orchestrating requests; then the markup that carries the meaning; and finally the styling that presents it. The reference stack is _React Router_ in SPA mode with `react-query-kit` for every server request, `react-hook-form` for every form, `zustand` for state shared across the tree, and `shadcn/ui` over _TailwindCSS_ v4, where styling resolves through semantic theme tokens and merge-aware composition rather than arbitrary values or interpolated class strings. Rules are written around principles rather than APIs, scoped to defects a reviewer can point at, and exclude accessibility auditing by design.

---

## Table of Contents

1. [Component Architecture](#1-component-architecture) — `HIGH`
   - 1.1 [Folder Structure & Layer Boundary](#11-folder-structure--layer-boundary)
   - 1.2 [Composition Over Configuration](#12-composition-over-configuration)
   - 1.3 [Component Extraction Threshold](#13-component-extraction-threshold)
   - 1.4 [Component Typing Conventions](#14-component-typing-conventions)
   - 1.5 [Minimal Markup Depth](#15-minimal-markup-depth)
   - 1.6 [Syntax & Conciseness Conventions](#16-syntax--conciseness-conventions)
2. [State & Effects](#2-state--effects) — `CRITICAL`
   - 2.1 [Effect Discipline](#21-effect-discipline)
   - 2.2 [Derived Values Over Stored State](#22-derived-values-over-stored-state)
   - 2.3 [State Colocation & Ownership](#23-state-colocation--ownership)
   - 2.4 [List Keys & Component Identity](#24-list-keys--component-identity)
3. [Data Flow](#3-data-flow) — `HIGH`
   - 3.1 [Query Layer & Data Ownership](#31-query-layer--data-ownership)
   - 3.2 [Pending, Empty & Error States](#32-pending-empty--error-states)
4. [Semantic Markup](#4-semantic-markup) — `CRITICAL`
   - 4.1 [Correct Interactive Elements](#41-correct-interactive-elements)
   - 4.2 [Document Outline & Sectioning](#42-document-outline--sectioning)
   - 4.3 [Form Markup & Field Association](#43-form-markup--field-association)
   - 4.4 [Content Elements: Lists, Tables & Media](#44-content-elements-lists-tables--media)
5. [Styling with TailwindCSS](#5-styling-with-tailwindcss) — `CRITICAL`
   - 5.1 [Theme Tokens Over Arbitrary Values](#51-theme-tokens-over-arbitrary-values)
   - 5.2 [Class Composition & Conditional Classes](#52-class-composition--conditional-classes)
   - 5.3 [State-Driven Styling With Data Attributes](#53-state-driven-styling-with-data-attributes)
   - 5.4 [Responsive & Variant Usage](#54-responsive--variant-usage)
   - 5.5 [@apply, Custom Utilities & Overrides](#55-apply-custom-utilities--overrides)
   - 5.6 [Class Attribute Formatting & Order](#56-class-attribute-formatting--order)
6. [Performance & Robustness](#6-performance--robustness) — `HIGH`
   - 6.1 [Render Stability & Memoization](#61-render-stability--memoization)
   - 6.2 [Layout Stability & Overflow](#62-layout-stability--overflow)
   - 6.3 [Source Detection & CSS Footprint](#63-source-detection--css-footprint)

---

## 1. Component Architecture

### 1.1 Folder Structure & Layer Boundary

**Impact (HIGH):** Where a file lives is the cheapest documentation a codebase has, and the first thing that decays. Once a query hook lands next to a component and a domain type is declared inside a route, nobody can tell what depends on what, and the answer to "can I reuse this?" becomes "read it and find out". A declared structure also makes review possible: a misplaced file is a finding anyone can point at, while "this feels disorganized" is not.

**Guidelines:**

1.  **Two layers, imports in one direction:**
    - `core/` holds everything that is not the view: data access, configured libraries, domain types, pure helpers
    - The view layer — routes and components — imports from `core/`; `core/` never imports from the view
    - A file under `core/` that imports a component is a boundary violation, and usually means presentation leaked into logic
2.  **What lives under `core/`:**
    - `core/api/<domain>/` — one file per query or mutation hook (see the query-layer rule)
    - `core/hooks/` — hooks the project writes, with the `zustand` stores under `core/hooks/stores/`
    - `core/lib/` — third-party libraries that need initialization or configuration, and the adapters over them
    - `core/types/` — domain types, separate from any library's own typings
    - `core/helpers/` — own pure functions, with no third-party dependency
    - The line between `lib/` and `helpers/`: `lib/` wraps something external, `helpers/` depends on nothing
3.  **The root varies, the shape does not:**
    - Where `core/` sits depends on the technology and the layout it dictates
    - What must not vary between projects is what goes inside `core/` and which direction imports flow
    - The `~` alias resolves to that root, so every import inside the project reads the same regardless of which root it is
4.  **The view layer splits by responsibility:**
    - Route modules compose a screen: they read data through hooks and arrange components
    - `components/` holds reusable presentation, with the design-system primitives under `components/ui/`
    - A route module that declares a fetcher, or a component that reaches for `axios`, is in the wrong layer
5.  **The tooling has to agree with the structure:**
    - `tsconfig` resolves `~/*` to the source root, and every generator reads the alias from there
    - With `shadcn/ui`, `components.json` decides where the next generated file lands, so its aliases are part of the structure and not a detail
    - Its `tailwind` block is part of the same contract: `cssVariables: true` is what makes generated components read the semantic tokens instead of arriving with the palette baked in, and `baseColor` seeds those variables at generation time (see the theme-tokens rule)
    - Point `ui` and `components` at the view layer, `utils` at `~/core/lib/utils`, and `lib` and `hooks` into `~/core/lib/shadcn/`. The generator then writes the component into `components/ui/`, rewrites its `cn` import to our path, and drops everything else it brings — its own helpers and hooks — under `core/lib/shadcn/`
    - Its `hooks` alias deliberately does not point at `core/hooks/`: those are ours to edit, and anything the generator writes is not
    - A structure the generator does not know about is undone the first time someone runs `shadcn add`
6.  **`core/lib/shadcn/` is generated territory, and read-only:**
    - The folder is listed in `.prettierignore`, so the formatter never rewrites it — which means any diff inside it is a deliberate edit and never noise
    - Editing a file there is a review finding, however small the change: the file is regenerable and not ours, so the edit is silently lost the next time the generator writes over it
    - When the generated behavior is not what the project needs, add a module beside it — a new component or hook that wraps or replaces it — instead of patching in place
    - If the generated file genuinely has to change, promote it: move the behavior into a module the project owns, and stop pretending the generator still governs it

**Incorrect (layers mixed, types inline, data access inside the view):**

```plaintext
app/
├─ components/
│  ├─ invoice-table.tsx
│  ├─ use-invoices.ts        ← data access in the view layer
│  └─ invoice.ts             ← domain type next to a component
├─ routes/
│  └─ invoices.tsx           ← declares its own axios call
└─ utils.ts                  ← configured client and pure helpers in one file
```

```tsx
// ./app/routes/invoices.tsx

// Bad: the route builds its own request, so nothing else can reuse it
import axios from 'axios';

type Invoice = {
  id: string;
  total: number;
};

export default function InvoicesRoute() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  // ...
}
```

**Correct (core owns logic and data, the view composes it):**

```plaintext
app/
├─ core/
│  ├─ api/
│  │  └─ invoices/
│  │     ├─ use-invoices.ts
│  │     └─ use-mark-paid.ts
│  ├─ hooks/
│  │  └─ stores/
│  │     └─ settings.ts
│  ├─ lib/
│  │  ├─ axios.ts
│  │  ├─ utils.ts                  ← cn(), the tailwind-merge adapter
│  │  ├─ react-query/
│  │  │  ├─ client.ts
│  │  │  └─ middlewares.ts
│  │  └─ shadcn/                   ← whatever the generator brings besides components
│  │     └─ hooks/
│  │        └─ use-mobile.ts
│  ├─ types/
│  │  └─ invoices.ts
│  └─ helpers/
│     └─ format.ts
├─ components/
│  ├─ ui/
│  │  └─ button.tsx
│  └─ invoice-table.tsx
└─ routes/
   ├─ protected-layout.tsx
   └─ invoices.tsx
```

```json
// ./components.json — the generator has to know the structure, or it will not follow it
{
  "tailwind": {
    "css": "app/styles/app.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "aliases": {
    "components": "~/components",
    "ui": "~/components/ui",
    "utils": "~/core/lib/utils",
    "lib": "~/core/lib/shadcn",
    "hooks": "~/core/lib/shadcn/hooks"
  }
}
```

```tsx
// ./app/routes/invoices.tsx

import { useInvoices } from '~/core/api/invoices/use-invoices';
import { InvoiceTable } from '~/components/invoice-table';

// Good: the route reads through the hook and arranges components — nothing else
export default function InvoicesRoute() {
  const invoices = useInvoices({ variables: { status: 'open' } });

  return <InvoiceTable invoices={invoices.data} />;
}
```

Reference: [shadcn/ui components.json](https://ui.shadcn.com/docs/components-json)

### 1.2 Composition Over Configuration

**Impact (HIGH):** A component configured by flags grows one prop per request until its signature encodes every screen that ever used it, and its body becomes a chain of conditionals nobody can change safely. Composition moves that variation to the call site, where it is visible in the markup, and leaves the component with a single job. The test is simple: if adding a screen means adding a prop, the component is configured rather than composed.

**Guidelines:**

1.  **Slots over flags:**
    - `children` and named slot props (`header`, `actions`, `footer`) instead of booleans that toggle internal markup
2.  **Mutually exclusive booleans are not independent props:**
    - Two flags that are never true together are one discriminated union, or two components
3.  **Compound components express structure:**
    - `Card` / `CardHeader` / `CardBody` lets the caller assemble what this screen needs without the parent configuring it
4.  **Render props only for internal state:**
    - A `renderX` function is justified when the child needs state the parent holds; otherwise `children` already works
5.  **Passthrough props signal a broken boundary:**
    - Props that exist only to travel deeper mean you should be passing the element, not its data

**Incorrect (a flag per screen, conditionals stacking inside):**

```tsx
type Props = {
  title: string;
  showHeader?: boolean;
  showFooter?: boolean;
  isCompact?: boolean;
  hasBorder?: boolean;
  headerAction?: ReactNode;
  renderFooter?: () => ReactNode;
  footerAlign?: 'left' | 'right';
};

export function Card(props: Props) {
  return (
    <div
      className={cn(
        'rounded-lg',
        props.hasBorder && 'border',
        props.isCompact ? 'p-2' : 'p-4',
      )}
    >
      {props.showHeader && (
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">{props.title}</h3>
          {props.headerAction}
        </div>
      )}
      {props.children}
      {props.showFooter && (
        <div
          className={props.footerAlign === 'right' ? 'text-right' : 'text-left'}
        >
          {props.renderFooter?.()}
        </div>
      )}
    </div>
  );
}
```

**Correct (structure assembled at the call site, one job per component):**

```tsx
// Several components in one module, so each type is qualified by its own name
type CardProps = React.ComponentProps<'div'>;

export function Card({ className, ...props }: CardProps) {
  return <div className={cn('rounded-lg border p-4', className)} {...props} />;
}

type CardHeaderProps = React.ComponentProps<'div'>;

export function CardHeader({ className, ...props }: CardHeaderProps) {
  return (
    <div
      className={cn('mb-3 flex items-center justify-between', className)}
      {...props}
    />
  );
}

type CardBodyProps = React.ComponentProps<'div'>;

export function CardBody({ className, ...props }: CardBodyProps) {
  return (
    <div
      className={cn('text-sm text-muted-foreground', className)}
      {...props}
    />
  );
}
```

```tsx
// The screen composes exactly what it needs — no prop was added to support it
<Card className="p-2">
  <CardHeader>
    <h3 className="font-semibold">Q3 summary</h3>
    <Button variant="ghost">Export</Button>
  </CardHeader>
  <CardBody>
    <p>Revenue grew 12% quarter over quarter.</p>
  </CardBody>
</Card>
```

Mutually exclusive props follow the same principle one level down, in the type: the union makes the invalid combination impossible to write rather than something the component has to defend against.

```tsx
// Three alternatives for the same Banner component, not three coexisting declarations

// Bad: three independent booleans describe eight states, five of which are meaningless
type Props = {
  isInfo?: boolean;
  isWarning?: boolean;
  isError?: boolean;
  message: string;
};

// Good: one axis, three valid states, nothing else type-checks
type Props = {
  tone: 'info' | 'warning' | 'error';
  message: string;
};

// Good: when a case carries data the others do not, discriminate on the same axis
type Props =
  | { tone: 'info' | 'warning'; message: string }
  | { tone: 'error'; message: string; onRetry: () => void };
```

Reference: [Passing JSX as children](https://react.dev/learn/passing-props-to-a-component#passing-jsx-as-children)

### 1.3 Component Extraction Threshold

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

### 1.4 Component Typing Conventions

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

### 1.5 Minimal Markup Depth

**Impact (HIGH):** Utility classes make it cheap to add a wrapper, so wrappers accumulate. Each one is another node to render, another indentation level to read, and another place where a future style can be attached at the wrong depth. Most of them are removable: their classes belong on the element they wrap.

**Guidelines:**

1.  **A wrapper needs a job:**
    - Justified when it creates a layout context (a `flex`/`grid` parent), a positioning context (`relative`), an overflow clip, or a stacking context
    - Not justified when its classes could sit on the child
2.  **Fragments over structural noise:**
    - Use `<>` when a `div` exists only to satisfy a single-root requirement
3.  **Spacing comes from the parent:**
    - `flex gap-4` or `space-y-4` on the container, not a wrapper per child carrying `mb-4`
    - Margins per child leak into every context where the child is reused
4.  **Margins flow with the document:**
    - When a margin is unavoidable, it goes on the element **above** as `mb-*`, never on the element below as `mt-*`
    - One direction throughout keeps two elements from both claiming the same gap, and keeps adjacent vertical margins from collapsing in ways nobody predicted
    - The exception is markup whose preceding sibling you do not control — rich text from a _CMS_, where a heading has to reserve its own space above
5.  **Centering is one element:**
    - `grid place-items-center`, `flex items-center justify-center`, or `mx-auto` — not three nested containers
6.  **Passthrough wrappers are removable:**
    - `<div className="w-full">` around a block element, or a wrapper whose only class is `flex-1`, almost always belongs on the child

**Incorrect (five levels of wrappers, per-child margins, nested centering):**

```tsx
export function EmptyState() {
  return (
    // Bad: wrapper chain, each level adding one class
    <div className="w-full">
      <div className="flex">
        <div className="mx-auto">
          <div className="flex flex-col items-center">
            <div className="mb-2">
              <h2 className="text-lg font-semibold">No reports yet</h2>
            </div>
            <div className="mb-4">
              <p className="text-sm text-muted-foreground">
                Create one to get started.
              </p>
            </div>
            <div>
              <Button>New report</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

**Correct (one layout container, gap for spacing, classes on the elements themselves):**

```tsx
export function EmptyState() {
  return (
    <div className="flex flex-col items-center gap-2">
      <h2 className="text-lg font-semibold">No reports yet</h2>
      {/* Good: the extra space before the button belongs to the element above it */}
      <p className="mb-2 text-sm text-muted-foreground">
        Create one to get started.
      </p>
      <Button>New report</Button>
    </div>
  );
}
```

Reference: [Styling with utility classes](https://tailwindcss.com/docs/styling-with-utilities)

### 1.6 Syntax & Conciseness Conventions

**Impact (LOW):** Improves conciseness and reduces visual noise in high-frequency patterns, while enforcing explicit control flow in conditionals to prevent logic bugs and rendering accidents.

These conventions maximize the information density of the code, so logic can be scanned without getting lost in boilerplate.

#### 1. Iterator Naming (Short-Hand Convention)

For inline array methods (`.map`, `.filter`, `.find`, `.forEach`), use the first letter of the collection's item name as the argument. This keeps the line short and puts the attention on the operation rather than on the binding.

**Exceptions:**

- **Block bodies:** when the callback body is a `{ … }` block, or it needs destructuring, use the full singular name — at that point the binding is read far from where it was bound
- **Nested iteration:** inside another iterator, use full names so the two bindings cannot be confused
- **The index keeps its name:** when the callback also takes the index it is always `index`, never `i` — the abbreviation belongs to the item

_JSX_ is not an exception: a multi-line element still takes the abbreviation, because the binding stays visible at the head of the same expression.

**Incorrect (verbose for simple logic):**

```tsx
const reportIds = reports.map((report) => report.id);

const openInvoices = invoices.filter((invoice) => invoice.isOpen);
```

**Correct (concise, with the exception spelled out):**

```tsx
const reportIds = reports.map((r) => r.id);

const openInvoices = invoices.filter((i) => i.isOpen);

// Exception: a block body warrants the descriptive name
const enriched = invoices.map((invoice) => {
  const isOverdue = checkOverdue(invoice);
  return { ...invoice, isOverdue };
});
```

```tsx
// JSX keeps the abbreviation, however many lines the element takes
{
  invoices.map((i) => (
    <tr key={i.id}>
      <td>{i.number}</td>
      <td>{i.total}</td>
    </tr>
  ));
}

// The index is never the abbreviation
{
  steps.map((s, index) => (
    <li key={s.id}>
      {index + 1}. {s.label}
    </li>
  ));
}
```

#### 2. Type and Object Literals

A _TypeScript_ type (not an interface) or an object literal with exactly one property is written on a single line. With more than one, each property takes its own line. One property reads as a single fact; several read as a list, and a list crammed onto one line has to be parsed instead of skimmed.

`prettier` does not decide this for you — it keeps whatever already fits inside the print width — so it only ever surfaces in review.

**Incorrect (one property spread over three lines, and two lists pretending to be one fact):**

```tsx
type Props = {
  invoice: Invoice;
};

type FormValues = { email: string; phone: string; plan: 'basic' | 'pro' };

const form = useForm<FormValues>({
  defaultValues: { email: '', phone: '', plan: 'basic' },
});
```

**Correct (one property inline, several one per line):**

```tsx
type Props = { invoice: Invoice };

type FormValues = {
  email: string;
  phone: string;
  plan: 'basic' | 'pro';
};

const form = useForm<FormValues>({
  defaultValues: {
    email: '',
    phone: '',
    plan: 'basic',
  },
});
```

#### 3. Event Handler Naming

Handler implementations use the `handle` prefix; event props keep the `on` prefix that the _DOM_ already uses. The distinction makes it immediately clear which side of the boundary a function is on — `onClick` is what the component accepts, `handleClick` is what this component does. Using `on` for both leaves the reader guessing.

**Incorrect (implementation named like a prop):**

```tsx
export function InvoiceRow({ invoice }: Props) {
  const onDownload = () => {
    downloadInvoice(invoice.id);
  };

  return <Button onClick={onDownload}>Download</Button>;
}
```

**Correct:**

```tsx
export function InvoiceRow({ invoice }: Props) {
  const handleDownload = () => {
    downloadInvoice(invoice.id);
  };

  return <Button onClick={handleDownload}>Download</Button>;
}
```

#### 4. Function Declarations Inside Components

A function declared inside a component is always an arrow assigned to a `const`; the `function` keyword stays at module scope. The component itself is a module-level declaration, so it keeps `export function`.

The arrow may be wrapped. `const handleSelect = useCallback(() => …, [])` satisfies this convention exactly as well as a bare arrow does, because the convention is about the binding and not about the arrow being unadorned. Whether a wrapper is needed at all is the render-stability rule's decision; this one only fixes the shape.

Three reasons this matters beyond taste: the component body then reads as one shape all the way down, nothing is hoisted above the props and state it closes over, and the `const` keeps visible that the function is a new reference on every render — which is exactly what matters when it crosses a memoized boundary.

**Incorrect (declarations inside the component body):**

```tsx
export function InvoiceRow({ invoice }: Props) {
  function handleDownload() {
    downloadInvoice(invoice.id);
  }

  async function handleArchive() {
    await archiveInvoice(invoice.id);
  }

  return <RowActions onDownload={handleDownload} onArchive={handleArchive} />;
}
```

**Correct (arrows assigned to a const):**

```tsx
export function InvoiceRow({ invoice }: Props) {
  const handleDownload = () => {
    downloadInvoice(invoice.id);
  };

  const handleArchive = async () => {
    await archiveInvoice(invoice.id);
  };

  return <RowActions onDownload={handleDownload} onArchive={handleArchive} />;
}
```

#### 5. Conditional Syntax

Every conditional uses braces and line breaks — including early returns and single-statement bodies. Omitting them is forbidden no matter how short the condition reads, because the next person to add a second statement is the one who pays for it.

For conditional rendering in _JSX_, always use a ternary with an explicit `null`. The `&&` shorthand is forbidden: when the left side is a number, `0` renders as the text "0" instead of nothing, and when it is an empty string the same happens.

**Incorrect (braceless conditions, `&&` shorthand):**

```tsx
// Bad: braceless early return
if (!invoice) return null;

// Bad: braceless single-statement body
if (invoices.isPending) return <Spinner />;

// Bad: renders the text "0" when the list is empty
{
  invoices.data.length && <InvoiceTable invoices={invoices.data} />;
}

// Bad: no explicit negative case
{
  isMenuOpen && <RowMenu />;
}
```

**Correct (braces, line breaks, ternary with null):**

```tsx
if (!invoice) {
  return null;
}

if (invoices.isPending) {
  return <Spinner />;
}

{
  invoices.data.length > 0 ? <InvoiceTable invoices={invoices.data} /> : null;
}

{
  isMenuOpen ? <RowMenu /> : null;
}
```

#### 6. Blank Lines Inside JSX

Sibling elements are not separated by blank lines. The tree already states its own structure through indentation and tags, so a blank line adds a second grouping signal that competes with the first — and it stretches a component across more screens than it needs.

This one is a convention rather than a formatting artifact: `prettier` preserves a single blank line wherever it finds one, so nothing enforces it automatically. It only ever surfaces in review.

**Incorrect (blank lines competing with the indentation):**

```tsx
export function AttachmentRow({ file }: Props) {
  return (
    <>
      <img src={file.previewUrl} className="w-full rounded-lg" />

      <section className="py-12">
        <p>{file.name}</p>

        <button type="button">Download</button>
      </section>
    </>
  );
}
```

**Correct (one continuous tree):**

```tsx
export function AttachmentRow({ file }: Props) {
  return (
    <>
      <img src={file.previewUrl} className="w-full rounded-lg" />
      <section className="py-12">
        <p>{file.name}</p>
        <button type="button">Download</button>
      </section>
    </>
  );
}
```

Reference: [TypeScript Handbook - Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)

---

## 2. State & Effects

### 2.1 Effect Discipline

**Impact (CRITICAL):** `useEffect` is an escape hatch for synchronizing with systems outside _React_ — the _DOM_, a subscription, a timer, a third-party _SDK_. Used for anything else it produces the defects that dominate _React_ review: a second render pass with a visible flash, cascades of effects firing in an order nobody controls, stale closures reading last render's values, and infinite loops when a dependency is recreated every render. Most effects in a codebase should not exist.

**Guidelines:**

1.  **What an effect is actually for:**
    - Subscribing to something outside _React_ that offers no hook of its own — an `EventTarget`, a socket, a browser _API_ — with a cleanup that unsubscribes
    - Imperatively driving a non-_React_ widget (a map, a chart, a media element)
    - A store that already exposes a hook is not one of these: it is read through its selector, never through an effect
    - Nothing else qualifies by default
2.  **What belongs in an event handler:**
    - Anything that happens _because the user did something_ — sending the request, showing the toast, navigating
    - An effect that watches a state flag to detect that an event happened is an event handler written backwards
3.  **What belongs in render:**
    - Any value computable from props or state (see the derived-values rule)
4.  **Dependencies are not negotiable:**
    - Never silence the linter with an incomplete array; an omitted dependency is a stale closure waiting for a bug report
    - If a complete array causes a loop, the fix is to move the value out of the effect — into a handler, a ref, or a reducer — not to trim the array
5.  **Cleanup is mandatory for anything ongoing:**
    - Subscriptions, timers, and in-flight requests are cancelled in the cleanup, which also runs between re-renders and on _StrictMode_'s double invocation
6.  **Do not fetch on mount:**
    - Component-level data belongs to the query layer, never to an effect (see the query-layer rule)
    - An effect that fetches also has to reimplement caching, cancellation, retries, and an error branch — and it usually reimplements none of them

**Incorrect (fetch on mount, effect deriving state, effect acting as an event handler, trimmed dependencies):**

```tsx
type Props = {
  cart: Cart;
  onPurchased: () => void;
};

export function CheckoutPanel({ cart, onPurchased }: Props) {
  const [status, setStatus] = useState<'idle' | 'submitting' | 'done'>('idle');
  const [total, setTotal] = useState(0);
  const [coupons, setCoupons] = useState<Coupon[]>([]);

  // Bad: fetching on mount — no cache, no cancellation, no error branch
  useEffect(() => {
    fetch('/api/coupons')
      .then((r) => r.json())
      .then(setCoupons);
  }, []);

  // Bad: derived value stored in state — renders twice and flashes 0 on the first pass
  useEffect(() => {
    setTotal(cart.items.reduce((sum, i) => sum + i.price * i.quantity, 0));
  }, [cart]);

  // Bad: an event handler written backwards — it reacts to state instead of to the click
  useEffect(() => {
    if (status === 'done') {
      onPurchased();
      toast.success('Order placed');
    }
    // Bad: onPurchased omitted to stop the loop, so it is now a stale closure
  }, [status]);

  return (
    <button type="button" onClick={() => setStatus('submitting')}>
      Pay {total}
    </button>
  );
}
```

**Correct (the query layer loads, the mutation tracks its own pending state, the handler owns the consequences):**

```tsx
type Props = {
  cart: Cart;
  onPurchased: () => void;
};

export function CheckoutPanel({ cart, onPurchased }: Props) {
  const coupons = useCoupons();
  const purchase = usePurchase();

  // Good: derived during render, so it can never disagree with the cart
  const total = cart.items.reduce((sum, i) => sum + i.price * i.quantity, 0);

  // Good: what happens because of the click lives in the click
  const handlePay = () => {
    purchase.mutate(cart, {
      onSuccess: () => {
        onPurchased();
        toast.success('Order placed');
      },
    });
  };

  return (
    <>
      <CouponPicker coupons={coupons} />
      <Button type="button" onClick={handlePay} disabled={purchase.isPending}>
        Pay {total}
      </Button>
    </>
  );
}
```

```tsx
// Good: the effect that survives review — an external system with no hook of its
// own, complete deps, real cleanup
useEffect(() => {
  const socket = connectToRoom(roomId);
  socket.on('message', onMessage);

  return () => socket.close();
}, [roomId, onMessage]);
```

Reference: [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)

### 2.2 Derived Values Over Stored State

**Impact (HIGH):** Every piece of state that could have been computed is a second source of truth, and two sources of truth eventually disagree. The disagreement reaches users as a stale total, a filter one keystroke behind, or a row that survives its own deletion. Deriving during render makes the inconsistent state impossible to represent, which is a stronger guarantee than remembering to synchronize it.

**Guidelines:**

1.  **If it can be computed, compute it:**
    - A value derived from props or state is calculated in render, not stored
2.  **Props copied into state freeze at mount:**
    - `useState(props.value)` captures the first value and stops responding to the prop; the component then works right up until the prop changes, which is what makes it hard to spot in review
    - Use the prop directly, or remount deliberately with `key` when a reset is the actual intent (see the identity rule)
3.  **Store the minimal representation:**
    - An `id`, not the selected object; a sort key, not a sorted copy; a filter string, not the filtered array
    - Storing the object means holding a snapshot that goes stale when the source updates
4.  **Deriving is not a performance question:**
    - An unmemoized derivation is correct, and the compiler memoizes what render produces anyway
    - A hand-written `useMemo` around a derivation is the exception, and it has to say what the compiler could not see (see the render-stability rule)
5.  **Flags derived from status stay in render:**
    - `const isPending = status === 'submitting'` is a variable, never its own state

**Incorrect (a prop frozen into state, two states an effect has to keep in sync, a stale snapshot):**

```tsx
type Props = {
  users: User[];
  query: string;
};

export function UserPicker({ users, query }: Props) {
  // Bad: a prop copied into state — nothing ever calls setLocalQuery, so from the
  // second render on this can only be stale
  const [localQuery, setLocalQuery] = useState(query);
  const [filtered, setFiltered] = useState(users);
  const [hasResults, setHasResults] = useState(true);
  // Bad: holds a snapshot — after the user is renamed upstream this still shows the old name
  const [selected, setSelected] = useState<User | null>(null);

  useEffect(() => {
    const next = users.filter((u) => u.name.includes(localQuery));
    setFiltered(next);
    setHasResults(next.length > 0);
  }, [users, localQuery]);

  return (
    <Results
      items={filtered}
      empty={!hasResults}
      selectedName={selected?.name}
      onSelect={setSelected}
    />
  );
}
```

**Correct (the prop is read as a prop, one state for the one real input, the rest derived):**

```tsx
type Props = {
  users: User[];
  query: string;
};

export function UserPicker({ users, query }: Props) {
  // Good: store the identity, not the object
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Good: cannot disagree with users or query, because it is recomputed from them
  const filtered = users.filter((u) => u.name.includes(query));
  const selected = users.find((u) => u.id === selectedId) ?? null;

  return (
    <Results
      items={filtered}
      selectedName={selected?.name}
      onSelect={setSelectedId}
    />
  );
}
```

Reference: [Choosing the state structure](https://react.dev/learn/choosing-the-state-structure)

### 2.3 State Colocation & Ownership

**Impact (HIGH):** State placed too high re-renders subtrees that do not care about it and turns every component in between into a prop conduit. State kept in a component when it belongs to the _URL_ produces links that do not restore what the user was looking at and a back button that does nothing. Ownership is a design decision, and review should be able to name the owner of every piece of state on screen.

**Guidelines:**

1.  **Push it down:**
    - State lives in the lowest component that reads it — a row's menu flag belongs to the row, not to the page
2.  **Lift only to the nearest common ancestor:**
    - Of the components that actually need it, which is usually one or two levels, not the route
    - When the nearest common ancestor turns out to be the root, that is the signal for the store — not for a prop that travels five levels to get there
3.  **The _URL_ is state:**
    - Anything that should survive a reload or be shareable belongs in the query string: filters, tabs, pagination, sort order, the open detail panel
    - Read and write it through the router's own search-param _API_; a `useState` mirror of a search param is a bug in waiting
4.  **Server data has an owner already:**
    - The query cache owns it; do not copy it into `useState` (see the query-layer rule)
5.  **Shared state goes to the store, never to a context of your own:**
    - `zustand` is the answer for state read across the tree, in every case: a selector subscribes a component to one slice, so an update re-renders only what reads that slice (see the render-stability rule)
    - A context you author to share state is a store with worse ergonomics — it re-renders every consumer whatever changed inside the value, and splitting it only postpones the problem
    - Libraries that use context internally are not this decision. What the rule forbids is reaching for `createContext` to move your own state around

**Incorrect (page owns everything, filters vanish on reload, one menu re-renders the table):**

```tsx
export default function InvoicesRoute() {
  const [status, setStatus] = useState('all');
  const [sort, setSort] = useState('date');
  // Bad: opening a row menu re-renders the entire page
  const [openRowId, setOpenRowId] = useState<string | null>(null);

  return (
    <InvoiceTable
      status={status}
      sort={sort}
      openRowId={openRowId}
      onOpenRow={setOpenRowId}
      onStatusChange={setStatus}
      onSortChange={setSort}
    />
  );
}
```

**Correct (the URL owns what must be shareable, the table owns what its children share, the row owns its own menu):**

```tsx
export default function InvoicesRoute() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Good: reload, share, and the back button all work
  const status = searchParams.get('status') ?? 'all';
  const sort = searchParams.get('sort') ?? 'date';

  return (
    <InvoiceTable
      status={status}
      sort={sort}
      onFilterChange={setSearchParams}
    />
  );
}
```

```tsx
type Props = {
  status: string;
  sort: string;
};

function InvoiceTable({ status, sort }: Props) {
  const invoices = useInvoices({ variables: { status, sort } });

  // Good: lifted exactly one level — the header checkbox and the rows both read
  // it, and nothing above this table does
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  return (
    <table>
      <thead>
        <SelectAll
          rows={invoices.data}
          selected={selectedIds}
          onChange={setSelectedIds}
        />
      </thead>
      <tbody>
        {invoices.data.map((i) => (
          <InvoiceRow
            key={i.id}
            invoice={i}
            isSelected={selectedIds.includes(i.id)}
          />
        ))}
      </tbody>
    </table>
  );
}
```

```tsx
type Props = {
  invoice: Invoice;
  isSelected: boolean;
};

function InvoiceRow({ invoice, isSelected }: Props) {
  // Good: opening this menu re-renders one row and nothing above it
  const [isMenuOpen, setMenuOpen] = useState(false);

  return (
    <tr className={cn(isSelected && 'bg-accent')}>
      <td>{invoice.number}</td>
      <td>
        <RowMenu open={isMenuOpen} onOpenChange={setMenuOpen} />
      </td>
    </tr>
  );
}
```

```ts
// ./app/core/hooks/stores/settings.ts

import { create } from 'zustand';

type SettingsStore = {
  theme: 'light' | 'dark';
  density: 'compact' | 'comfortable';
  setTheme: (theme: SettingsStore['theme']) => void;
  setDensity: (density: SettingsStore['density']) => void;
};

// Good: read across the tree and owned by nobody in particular, so it is a store
export const useSettingsStore = create<SettingsStore>((set) => ({
  theme: 'light',
  density: 'comfortable',
  setTheme: (theme) => set({ theme }),
  setDensity: (density) => set({ density }),
}));
```

```tsx
// Good: one selector, one subscription — this re-renders on density, not on theme
const density = useSettingsStore((s) => s.density);
```

Reference: [Sharing state between components](https://react.dev/learn/sharing-state-between-components)

### 2.4 List Keys & Component Identity

**Impact (HIGH):** `key` is not a lint requirement to satisfy — it is how _React_ decides which component instance corresponds to which item. An index key on a list that can be reordered, filtered, or prepended attaches the wrong state to the wrong row: an open menu jumps, an input keeps the previous row's draft, a checkbox stays checked on a different item. The list looks correct right up until state enters it.

**Guidelines:**

1.  **The key is identity from the data:**
    - `item.id` — never the array index, never `Math.random()`, never the position in a composite string
2.  **Index keys are only safe on a static list:**
    - Never reordered, never filtered, never prepended, and holding no internal state
3.  **A key that changes every render destroys the subtree:**
    - Focus, scroll position, uncontrolled input values, and animation state all reset, on every render
    - This is what a random key buys: the warning goes away and the defect gets worse
4.  **Use `key` deliberately to reset:**
    - `<TaskEditor key={task.id} />` restarts the editor's internal state when the task changes — this replaces the effect that copied the prop into state
5.  **Keys are scoped to siblings:**
    - They need to be unique among their siblings, not globally
6.  **A missing identity is a data problem:**
    - Concatenating the index to silence the warning hides it; if the payload has no stable id, fix the payload

**Incorrect (index keys on a filterable list):**

```tsx
type Props = {
  tasks: Task[];
  query: string;
};

export function TaskList({ tasks, query }: Props) {
  const visible = tasks.filter((t) => t.title.includes(query));

  return (
    <ul>
      {/* Bad: filtering shifts every index — row state follows the wrong task */}
      {visible.map((t, index) => (
        <TaskRow key={index} task={t} />
      ))}
    </ul>
  );
}
```

**Incorrect (a random key, which silences the warning and rebuilds every row):**

```tsx
type Props = { entries: LogEntry[] };

export function LogList({ entries }: Props) {
  return (
    <ul>
      {/* Bad: the payload has no id, so the warning was silenced with a random key.
          Every render produces new keys, so every row is destroyed and rebuilt —
          focus, scroll position and any uncontrolled input inside them reset */}
      {entries.map((e) => (
        <LogRow key={Math.random()} entry={e} />
      ))}
    </ul>
  );
}
```

**Incorrect (an effect undoing the defaults that mounting already applied):**

```tsx
type Props = { task: Task };

function TaskEditor({ task }: Props) {
  const form = useForm<FormValues>({
    defaultValues: { title: task.title },
  });

  // Bad: defaultValues are read at mount, so this effect exists only to patch an
  // instance that should have been a new one
  useEffect(() => {
    form.reset({ title: task.title });
  }, [task.id, form]);

  return <TaskForm form={form} />;
}
```

**Correct (identity from the data, and `key` as the reset mechanism):**

```tsx
type Props = {
  tasks: Task[];
  query: string;
};

export function TaskList({ tasks, query }: Props) {
  const visible = tasks.filter((t) => t.title.includes(query));

  return (
    <ul>
      {visible.map((t) => (
        <TaskRow key={t.id} task={t} />
      ))}
    </ul>
  );
}
```

```tsx
type Props = {
  tasks: Task[];
  query: string;
};

export function TaskPanel({ tasks, query }: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selected = tasks.find((t) => t.id === selectedId) ?? null;

  return (
    <>
      <TaskList tasks={tasks} query={query} onSelect={setSelectedId} />
      {/* Good: a new identity remounts the editor, so no effect has to reset it */}
      {selected ? <TaskEditor key={selected.id} task={selected} /> : null}
    </>
  );
}
```

```tsx
type Props = { task: Task };

function TaskEditor({ task }: Props) {
  // Good: defaultValues are read once at mount, and mounting is what the key controls
  const form = useForm<FormValues>({
    defaultValues: { title: task.title },
  });

  return <TaskForm form={form} />;
}
```

Reference: [Why does React need keys?](https://react.dev/learn/rendering-lists#why-does-react-need-keys)

---

## 3. Data Flow

### 3.1 Query Layer & Data Ownership

**Impact (HIGH):** A component that fetches takes on a problem it cannot finish: caching, deduplication, cancellation, retry, and invalidation. Spread across components, each one solves a different subset, and the same endpoint ends up requested three times per screen under three different key strings. A typed query layer answers all of that once and leaves the component consuming state instead of orchestrating requests.

**Guidelines:**

1.  **One way to reach the network:**
    - Every request goes through `createQuery` / `createMutation` from `react-query-kit`; components never call `useQuery`, `useMutation`, or `axios` directly
2.  **Structure by domain, keys declared once:**
    - Hooks live under `core/api/<domain>/`, named `use-<members|action>.ts` (see the folder-structure rule)
    - Query keys follow `'@<domain>/<hook-name>'`, declared in the hook itself — a bare `['invoices']` written at a call site is how two components end up with two caches of the same data
    - Invalidate with the owning hook's `getKey()`, never a hand-written copy of the key
3.  **The client and the middlewares are configured once:**
    - The _Axios_ instance, the query client, and the mutation middlewares are configured library instances, so they live where the structure rule puts them: `core/lib/`
    - Nothing outside that folder constructs one of these; the rest of the codebase imports the already-configured instance, so there is exactly one cache and one interceptor chain per process
4.  **Types at the boundary, in request order:**
    - Declare `Variables`, then `Response`, then `Data` — the order follows the request's own direction: what goes out, what comes back, what the _UI_ consumes
    - When the payload needs no transform, `Data` is an alias and says so: `type Data = Response`
    - When they diverge, the transform belongs in the fetcher, so every consumer sees the same shape
5.  **Let errors propagate:**
    - A `try`/`catch` in the fetcher that returns `[]` makes `isError` permanently false and the error branch unreachable — the screen then reports "no results" for what was actually a failure
6.  **Auth is not a component concern:**
    - Token injection and 401 handling live in the _Axios_ interceptors, declared once
    - Access control before render belongs to the protected layout route, driven by the session query and a declarative redirect
    - A `useEffect` that navigates is the wrong tool for both: it paints the protected screen first and redirects after
7.  **Parallel by default, dependent only when it is:**
    - Independent hooks called in the same component already run in parallel — nothing to arrange
    - Chaining with `enabled` makes the second request wait for the first, so use it only when the second genuinely needs the first's result
8.  **Paginated queries hold the previous page:**
    - When the page is part of the key, every page change is a fresh cache entry with no data, so the consumer's pending branch fires and the whole table blanks on each step
    - `placeholderData: keepPreviousData` in the hook definition serves the previous page while the next one resolves, which turns that blank into an `isPlaceholderData` dim (see the async-states rule)
9.  **Mutations invalidate through a middleware:**
    - Compose invalidation with `use` on `createMutation`, so it is declared beside the mutation instead of hand-written into every `onSuccess`
    - Pass the keys the mutation actually affects; a mutation that invalidates everything is a cache with extra steps
    - Calling a query's `refetch()` from a mutation, or writing the response into local state, forks the cache

**Incorrect (inline query, hand-written key, swallowed error, effect that redirects, needless waterfall):**

```tsx
// ./app/routes/invoices.tsx
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export default function InvoicesRoute() {
  const navigate = useNavigate();
  const session = useSessionStore((s) => s.session);

  // Bad: the protected screen paints, then navigates away
  useEffect(() => {
    if (!session) {
      navigate('/login');
    }
  }, [session, navigate]);

  // Bad: inline query, key written at the call site, error swallowed so isError never fires
  const { data } = useQuery({
    queryKey: ['invoices'],
    queryFn: async () => {
      try {
        return (await axios.get('/invoices')).data;
      } catch {
        return [];
      }
    },
  });

  // Bad: enabled turns two independent requests into a waterfall
  const { data: customers } = useQuery({
    queryKey: ['customers'],
    queryFn: fetchCustomers,
    enabled: Boolean(data),
  });

  return <InvoiceTable invoices={data} customers={customers} />;
}
```

**Correct (typed hook per domain, types in request order, key declared once):**

```ts
// ./app/core/api/invoices/use-invoices.ts

import { createQuery } from 'react-query-kit';
import { api } from '~/core/lib/axios';
import type { Invoice } from '~/core/types/invoices';

type Variables = { status: string };

type Response = Invoice[];

type Data = Response;

export const useInvoices = createQuery<Data, Variables>({
  queryKey: ['@invoices/use-invoices'],
  fetcher: request,
});

async function request({ status }: Variables) {
  const { data } = await api.get<Response>('/invoices/', {
    params: { status },
    protected: true,
  });

  return data;
}
```

```ts
// ./app/core/lib/react-query/middlewares.ts

export const withInvalidation = (...keys: QueryKey[]): MiddlewareFn => {
  return (useMutationNext) => {
    return (options) => {
      return useMutationNext({
        ...options,
        onSuccess: (_data, _variables, _onMutateResult, context) => {
          for (const key of keys) {
            context.client.invalidateQueries({ queryKey: key });
          }

          options.onSuccess?.(_data, _variables, _onMutateResult, context);
        },
      });
    };
  };
};
```

```ts
// ./app/core/api/invoices/use-mark-paid.ts

import { createMutation } from 'react-query-kit';
import { api } from '~/core/lib/axios';
import { withInvalidation } from '~/core/lib/react-query/middlewares';
import type { Invoice } from '~/core/types/invoices';
import { useInvoices } from './use-invoices';

type Variables = {
  id: string;
  reference: string;
};

type Response = Invoice;

type Data = Response;

export const useMarkPaid = createMutation<Data, Variables>({
  mutationFn: request,
  // Good: invalidation declared beside the mutation, with the key its owner exposes
  use: [withInvalidation(useInvoices.getKey())],
});

async function request({ id, reference }: Variables) {
  const { data } = await api.patch<Response>(
    `/invoices/${id}/paid/`,
    { reference },
    { protected: true },
  );

  return data;
}
```

```tsx
// ./app/routes/invoices.tsx

export default function InvoicesRoute() {
  // Good: two independent hooks, so both requests start together
  const invoices = useInvoices({ variables: { status: 'open' } });
  const customers = useCustomers();

  return <InvoiceTable invoices={invoices.data} customers={customers.data} />;
}
```

```tsx
// ./app/routes/protected-layout.tsx

export default function ProtectedLayout() {
  const session = useSession();

  if (session.isPending) {
    return <AppSkeleton />;
  }

  // Good: the redirect is part of the render output, so nothing protected paints first
  if (!session.data) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
```

Reference: [React Query Kit](https://github.com/liaoliao666/react-query-kit)

### 3.2 Pending, Empty & Error States

**Impact (HIGH):** An async view has four outcomes and most components implement one. The missing branches are exactly what users hit: a blank panel that never explains itself, a crash on `data.items.map` when the request failed, a spinner that wipes content already on screen during a background refetch. Review should be able to point at each of the four branches in the code — if one is not there, it was not designed, it was forgotten.

**Guidelines:**

1.  **Four questions, always answered:**
    - What shows while pending, what shows when the result is empty, what shows when it fails, and what shows on success
    - _React Query_ names three of them for you (`isPending`, `isError`, `data`); the empty one is the one you have to write
2.  **Read the query through its name, do not destructure it:**
    - Give the query a meaningful name and reach its parts by dot notation — `reports.isPending`, `reports.data`
    - This is not only style: the query result is a discriminated union, so `if (reports.isPending) { … }` narrows `reports.data` to a defined value for the rest of the function. Destructuring severs that link, and `data` stays possibly-undefined no matter how many flags you checked
3.  **`isPending` is not `isFetching`:**
    - `isPending` is the first load, when there is genuinely nothing to show — the only state that may render a skeleton
    - `isFetching` is also true for background refetches, so gating the skeleton on it makes content the user is reading disappear and come back on every revalidation
    - A page change is neither of those: the key itself changes, so `isPending` is legitimately true and the skeleton fires again. Where the query serves the previous page as placeholder data, `isPlaceholderData` is the flag to dim on — the option that enables it belongs to the query layer
4.  **The empty branch must exist:**
    - A successful response with zero rows is a distinct outcome, not a shorter list
    - What it says is a product decision; that it exists at all is a review one
5.  **Errors surface, they do not vanish:**
    - Either an `isError` branch or `throwOnError` with an `ErrorBoundary` — pick one per surface and stay consistent
    - A fetcher that catches and returns `[]` makes this branch unreachable (see the query-layer rule)
6.  **Do not collapse the branches:**
    - `data ?? []` renders pending, error, and empty as the same empty list, which is how a broken screen ends up looking like a working one

**Incorrect (one branch of four — pending, failure and empty all render the same empty list):**

```tsx
export default function ReportsRoute() {
  const { data } = useReports();

  return (
    <ul>
      {(data ?? []).map((report) => (
        <li key={report.id}>{report.name}</li>
      ))}
    </ul>
  );
}
```

**Correct (all four branches, and a refetch that does not wipe the list):**

```tsx
export default function ReportsRoute() {
  const reports = useReports();

  // Good: only the first load has nothing to show yet
  if (reports.isPending) {
    return <ReportListSkeleton />;
  }

  if (reports.isError) {
    return <ErrorState title="Reports could not be loaded" />;
  }

  // Good: a successful empty result is its own outcome, with a way forward
  if (reports.data.length === 0) {
    return (
      <EmptyState
        title="No reports yet"
        description="Create one to start tracking activity."
        action={<Button>New report</Button>}
      />
    );
  }

  // Good: a background refetch dims the list instead of replacing it with a skeleton
  return (
    <ul className={cn(reports.isFetching && 'opacity-60')}>
      {reports.data.map((report) => (
        <li key={report.id}>{report.name}</li>
      ))}
    </ul>
  );
}
```

Reference: [Query status and fetch status](https://tanstack.com/query/latest/docs/framework/react/guides/queries)

---

## 4. Semantic Markup

### 4.1 Correct Interactive Elements

**Impact (CRITICAL):** An interactive `div` throws away behavior the browser provides for free — keyboard activation, form submission, link context menus, middle-click and modifier-click navigation, framework prefetching, and `:disabled` state. Rebuilding any of it costs more code than using the right element, and the reimplementation drifts the moment someone edits it.

**Guidelines:**

1.  **Element by intent:**
    - Navigation that changes the URL is an anchor, and it carries a real `href`
    - An action that stays on the page is a `button`
    - An anchor without `href` is not a link — if there is no destination, it is a `button`
2.  **Button type is mandatory:**
    - Every `button` inside a `form` declares `type`; the default is `submit`, so an unmarked action button silently submits the form
    - Wrapping it in a component changes nothing: a `Button` with no `type` is still a submit button
3.  **No click handlers on inert elements:**
    - `onClick` on `div`, `span`, or `li` as the only interaction path is a defect, not a style choice
    - Utilities like `cursor-pointer` make a `div` look interactive without making it interactive
4.  **Disabled is an attribute:**
    - Use the `disabled` attribute so the control stops firing; `opacity-50 pointer-events-none` only hides the affordance and leaves the handler reachable by other means
    - Style the real state with the `disabled:` variant

**Incorrect (clickable div, untyped form button, fake disabled state):**

```tsx
type Props = { busy: boolean };

export function Toolbar({ busy }: Props) {
  return (
    <form onSubmit={handleSubmit}>
      {/* Bad: a div is not a control */}
      <div
        onClick={handleSave}
        className="cursor-pointer rounded-md bg-primary px-4 py-2"
      >
        Save
      </div>
      {/* Bad: no type — a Button inside a form still defaults to submit */}
      <Button onClick={openHelp}>Help</Button>
      {/* Bad: disabled is only painted, the handler still runs */}
      <Button
        onClick={publish}
        className={busy ? 'pointer-events-none opacity-50' : ''}
      >
        Publish
      </Button>
    </form>
  );
}
```

**Correct (native controls, explicit type, real disabled attribute):**

```tsx
type Props = { busy: boolean };

export function Toolbar({ busy }: Props) {
  return (
    <form onSubmit={handleSubmit}>
      <Button type="submit">Save</Button>
      <Button type="button" onClick={openHelp}>
        Help
      </Button>
      {/* Good: the attribute stops the handler, and the component already
          carries the disabled styling */}
      <Button type="button" onClick={publish} disabled={busy}>
        Publish
      </Button>
    </form>
  );
}
```

Reference: [The button element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button)

### 4.2 Document Outline & Sectioning

**Impact (HIGH):** The element carries the meaning; the utility class carries the presentation. When every block is a `div`, the only structure a page has left is its class names, and the outline has to be reconstructed by whoever reads it next. Nothing breaks visibly, which is exactly why this decays quietly and is expensive to retrofit — but three of its failures are concrete rather than abstract: a route that adds its own `main` leaves the page with two, a skipped heading rank makes the outline lie about what contains what, and pages that never declare a title are indistinguishable in the tab bar and the history.

**Guidelines:**

1.  **Page skeleton:**
    - Build the page from `header`, `nav`, `main`, `footer`, and `aside`
    - Exactly one `main` per rendered page, and it is not nested inside another landmark
2.  **Landmarks belong to the layout route:**
    - In a nested-routing setup the skeleton lives in the layout route, wrapped around the slot where the router inserts the child route
    - A route component that opens with its own `main` is how a page ends up with two
3.  **Sectioning rules:**
    - `section` requires a heading — a `section` with no heading should be a `div`
    - `article` is for self-contained content that would still make sense extracted (a post, a comment, a product card)
    - Nesting a `section` inside an `article` is fine; using either purely to attach padding is not
4.  **Heading rank is structure, not size:**
    - Ranks descend one at a time; never skip from `h1` to `h4` to get a smaller font
    - Visual size comes from utilities (`text-2xl`, `text-sm`), rank comes from the tag
    - One `h1` per page, describing the page — not the site name on every route
5.  **Every page declares its own title and description:**
    - Both are set per page, through whatever mechanism the framework provides; a page that inherits them is indistinguishable from every other one in the tab bar, the history, and a bookmark
    - The title names the page the same thing its `h1` does — when the two disagree, one of them is wrong
    - The description summarises that page in a sentence, not the product's tagline repeated everywhere
6.  **When `div` is right:**
    - A `div` is the correct element when no other element carries the meaning: a flex/grid container, a positioning context, an overflow clip

**Incorrect (div soup, skipped heading rank, section used as a padding box, no title or description):**

```tsx
// Bad: the page declares no title and no description, so the tab and the history
// entry repeat whatever the root said
export default function ReportsRoute() {
  return (
    <div className="mx-auto max-w-5xl">
      <div className="flex items-center justify-between py-4">
        <div className="text-xl font-bold">Acme</div>
        <div className="flex gap-4">
          <Link to="/pricing">Pricing</Link>
          <Link to="/docs">Docs</Link>
        </div>
      </div>
      <div className="py-10">
        <h1 className="text-4xl font-bold">Reports</h1>
        {/* Bad: rank skipped to get a smaller size */}
        <h4 className="text-lg font-medium">Latest activity</h4>
        {/* Bad: section with no heading, used only for spacing */}
        <section className="space-y-4">
          <div className="rounded-lg border p-4">
            <div className="font-semibold">Q3 summary</div>
            <p>Revenue grew 12% quarter over quarter.</p>
          </div>
        </section>
      </div>
    </div>
  );
}
```

**Correct (skeleton in the layout, content in the route, descending ranks):**

```tsx
// ./app/routes/layout.tsx — owns the landmarks
export default function AppLayout() {
  return (
    <div className="mx-auto max-w-5xl">
      <header className="flex items-center justify-between py-4">
        <span className="text-xl font-bold">Acme</span>
        <nav className="flex gap-4">
          <Link to="/pricing">Pricing</Link>
          <Link to="/docs">Docs</Link>
        </nav>
      </header>
      <div className="flex gap-8 py-10">
        <main className="flex-1">
          <Outlet />
        </main>
        <aside className="w-64">
          <RecentActivity />
        </aside>
      </div>
      <footer className="py-6 text-sm text-muted-foreground">© Acme</footer>
    </div>
  );
}
```

```tsx
// ./app/routes/reports.tsx — content only, no second main
export default function ReportsRoute() {
  return (
    <>
      {/* Good: the title says what the h1 says, and the description is about this
          page rather than about the product */}
      <title>Reports · Acme</title>
      <meta
        name="description"
        content="Activity and summaries for the current quarter."
      />
      <h1 className="mb-6 text-4xl font-bold">Reports</h1>
      <section className="space-y-4">
        {/* Good: rank descends, size is a utility */}
        <h2 className="text-lg font-medium">Latest activity</h2>
        <article className="rounded-lg border p-4">
          <h3 className="font-semibold">Q3 summary</h3>
          <p>Revenue grew 12% quarter over quarter.</p>
        </article>
      </section>
    </>
  );
}
```

Reference: [HTML sections and outlines](https://html.spec.whatwg.org/multipage/sections.html)

### 4.3 Form Markup & Field Association

**Impact (HIGH):** A form built from `div`s and a click handler loses submission on _Enter_, autofill, and the correct mobile keyboard. These are behaviors users expect and nobody reimplements completely. The same holds one level up: a component that keeps its own field state and its own error strings rebuilds what the form library already does, and the two copies drift — the label stops matching its control, the message stops matching the field.

**Guidelines:**

1.  **Every form goes through `react-hook-form`:**
    - The form instance owns every value; no component keeps field state of its own
    - Reading values back out of the _DOM_ by hand — `FormData`, a ref per input, `event.target.elements` — means the form was built twice
2.  **Fields are declared through the Form components:**
    - `FormField` / `FormItem` / `FormLabel` / `FormControl` / `FormMessage` wire the label to the control and the message to the field; writing `htmlFor` and an id by hand duplicates what they already do
    - A control rendered outside `FormControl` loses that wiring, and nothing reports it
    - The placeholder stays an example value (`jane@acme.co`) — the label is the label
3.  **A group of controls carries a label of its own:**
    - Related controls that only make sense together — radio groups, address blocks, date ranges — get one label for the group and one per option
    - The `Form` components express that with a group-level `FormLabel` and a nested `FormItem` per option; they emit no `fieldset` / `legend`, and wrapping one around them only declares the grouping twice
    - What review checks is that the group is named at all — an option list whose only labels are its options is a group nobody named
4.  **Type and name:**
    - Use the specific `type` (`email`, `tel`, `url`, `number`, `date`, `search`); it selects the mobile keyboard and parses the value
    - The `name` on `FormField` is what identifies the value — keep it identical to the key the mutation expects, so no mapping layer appears between them
5.  **Validation speaks once, and it is the form library:**
    - The `form` carries `noValidate`, so the browser's own checking never interrupts and every message the user reads comes from `FormMessage`
    - Constraints live on `FormField`'s `rules` and nowhere else — alongside `noValidate` a `required` attribute does nothing, and a component holding its own error string is a second source of truth
    - The `type` still earns its place through the mobile keyboard and the parsing; with native checking off it is no longer a validator, so it never competes for the message
6.  **Submission stays a real submission:**
    - A `form` element with `button type="submit"`, wrapping `handleSubmit`; never an action bound only to a button's `onClick`
    - The mutation hook is what the submit handler calls, not what replaces the form

**Incorrect (hand-held field state, no form element, no association, parallel error string):**

```tsx
export function SignupForm() {
  // Bad: field state by hand — the form library already owns this
  const [email, setEmail] = useState('');
  const [plan, setPlan] = useState('basic');
  const [emailError, setEmailError] = useState('');

  // Bad: not a form, so Enter does nothing and autofill has no context
  return (
    <div className="space-y-4">
      {/* Bad: placeholder used as the field name, no label, no association */}
      <input
        type="text"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full rounded-md border px-3 py-2"
      />
      {/* Bad: an error string tracked in parallel to the field it describes */}
      <p className="text-sm text-destructive">{emailError}</p>
      {/* Bad: the options are labelled, the group they belong to is not */}
      <div className="flex gap-4">
        <input type="radio" value="basic" onChange={() => setPlan('basic')} />{' '}
        Basic
        <input type="radio" value="pro" onChange={() => setPlan('pro')} /> Pro
      </div>
      <button onClick={submitForm} className="rounded-md bg-primary px-4 py-2">
        Continue
      </button>
    </div>
  );
}
```

**Correct (the form owns the values, the Form components own the wiring and the grouping):**

```tsx
type FormValues = {
  email: string;
  phone: string;
  plan: 'basic' | 'pro';
};

export function SignupForm() {
  const createAccount = useCreateAccount();
  const form = useForm<FormValues>({
    defaultValues: {
      email: '',
      phone: '',
      plan: 'basic',
    },
  });

  const handleSubmit = (values: FormValues) => {
    createAccount.mutate(values);
  };

  return (
    <Form {...form}>
      {/* Good: noValidate hands every message to the form library */}
      <form
        noValidate
        onSubmit={form.handleSubmit(handleSubmit)}
        className="space-y-4"
      >
        <FormField
          control={form.control}
          name="email"
          rules={{ required: 'Email is required' }}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" placeholder="jane@acme.co" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="phone"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Phone</FormLabel>
              <FormControl>
                <Input type="tel" {...field} />
              </FormControl>
            </FormItem>
          )}
        />
        {/* Good: the group is named by its own FormLabel, each option by its own */}
        <FormField
          control={form.control}
          name="plan"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Plan</FormLabel>
              <FormControl>
                <RadioGroup
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                  className="flex gap-4"
                >
                  <FormItem className="flex items-center gap-2">
                    <FormControl>
                      <RadioGroupItem value="basic" />
                    </FormControl>
                    <FormLabel className="font-normal">Basic</FormLabel>
                  </FormItem>
                  <FormItem className="flex items-center gap-2">
                    <FormControl>
                      <RadioGroupItem value="pro" />
                    </FormControl>
                    <FormLabel className="font-normal">Pro</FormLabel>
                  </FormItem>
                </RadioGroup>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={createAccount.isPending}>
          Continue
        </Button>
      </form>
    </Form>
  );
}
```

Reference: [shadcn/ui Form](https://ui.shadcn.com/docs/components/form)

### 4.4 Content Elements: Lists, Tables & Media

**Impact (MEDIUM):** Utilities describe layout, not meaning. A `grid grid-cols-4` of `div`s renders like a table and is one nowhere else: no column association, no sortable header, nothing a scraper or an export routine can read. Choosing the element that matches the data costs the same number of lines and keeps the utilities purely presentational.

**Guidelines:**

1.  **Collections:**
    - A `map()` over data almost always produces a `ul` or `ol`; only `li` may be a direct child
    - Drop the marker with `list-none`, not by switching to `div`
    - Key/value pairs are a `dl` with `dt` / `dd`
2.  **Tabular data:**
    - Real tabular data uses `table` with `thead`, `tbody`, `th` carrying `scope`, and a `caption`
    - Conversely, never use `table` for page layout — that is what `grid` is for
    - Utilities still apply: `w-full`, `text-left`, `border-separate`, `border-spacing-0`
3.  **Media:**
    - `figure` + `figcaption` when an image, chart, or code block has a caption
    - Decorative shapes belong in CSS (background utilities), not in an `img`
4.  **Dates carry both values:**
    - Dates and durations use `time` with a `dateTime` attribute — the formatted string is the child, the _ISO_ value is the attribute
    - Every human-facing date string comes from `dayjs`, never from `toLocaleDateString` or hand-assembled formatting, so format and locale are decided in one place instead of per component
    - The configured instance — plugins and locale — lives in `core/lib/dayjs.ts`, and components import that rather than the package (see the folder-structure rule)

**Incorrect (div grid imitating a table, div list, unformatted date):**

```tsx
type Props = { invoices: Invoice[] };

export function InvoiceList({ invoices }: Props) {
  return (
    <>
      {/* Bad: no header/cell association, nothing extractable */}
      <div className="grid grid-cols-3 gap-y-2">
        <div className="font-semibold">Invoice</div>
        <div className="font-semibold">Date</div>
        <div className="font-semibold">Total</div>
        {invoices.map((i) => (
          <Fragment key={i.id}>
            <div>{i.number}</div>
            <div>{i.issuedAt.toLocaleDateString()}</div>
            <div>{i.total}</div>
          </Fragment>
        ))}
      </div>
      {/* Bad: the caption is a sibling div, so nothing ties it to the image */}
      <div className="mb-6">
        <img src={chartUrl} className="mb-2 w-full rounded-lg" />
        <div className="text-sm text-muted-foreground">Monthly totals</div>
      </div>
      {/* Bad: a list that is not a list */}
      <div className="space-y-1">
        <div>Draft saved automatically</div>
        <div>Exports include line items</div>
      </div>
    </>
  );
}
```

**Correct (real table, real list, machine-readable date):**

```tsx
import { dayjs } from '~/core/lib/dayjs';

type Props = { invoices: Invoice[] };

export function InvoiceList({ invoices }: Props) {
  return (
    <>
      <table className="mb-6 w-full border-separate border-spacing-0 text-left">
        <caption className="pb-2 text-sm text-muted-foreground">
          Recent invoices
        </caption>
        <thead>
          <tr>
            <th scope="col" className="font-semibold">
              Invoice
            </th>
            <th scope="col" className="font-semibold">
              Date
            </th>
            <th scope="col" className="font-semibold">
              Total
            </th>
          </tr>
        </thead>
        <tbody>
          {invoices.map((i) => (
            <tr key={i.id}>
              <td>{i.number}</td>
              <td>
                <time dateTime={dayjs(i.issuedAt).toISOString()}>
                  {dayjs(i.issuedAt).format('L')}
                </time>
              </td>
              <td>{i.total}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <figure className="mb-6">
        <img src={chartUrl} className="mb-2 w-full rounded-lg" />
        <figcaption className="text-sm text-muted-foreground">
          Monthly totals
        </figcaption>
      </figure>
      <ul className="list-none space-y-1">
        <li>Draft saved automatically</li>
        <li>Exports include line items</li>
      </ul>
    </>
  );
}
```

Reference: [The table element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table)

---

## 5. Styling with TailwindCSS

### 5.1 Theme Tokens Over Arbitrary Values

**Impact (CRITICAL):** Every arbitrary value is a design decision made outside the design system. Once `bg-[#1d4ed8]` appears in three files, the brand color has no single definition, a theme change becomes a find-and-replace, and dark mode has nothing to swap. In v4 the theme is the stylesheet: tokens declared in `@theme` generate utilities _and_ expose CSS variables, so there is no reason to hardcode.

**Guidelines:**

1.  **Declare once, in `@theme`:**
    - Colors, radii, fonts, breakpoints, and shadows live in the `@theme` block of the main stylesheet
    - A token generates its utilities automatically: `--color-primary` yields `bg-primary`, `text-primary`, `border-primary`
    - The spacing scale is the exception and is never redeclared: `--spacing` is _Tailwind_'s and the design works in its steps, so a diff that redefines it is changing every margin, gap and size in the project at once
2.  **Two token layers, and they do not compete:**
    - `shadcn init` writes the semantic layer and every generated component reads it, so it is not optional decoration: `--background` / `--foreground` for the page, `--card` and `--popover` for raised surfaces, `--primary` and `--secondary` for actions, `--muted` and `--muted-foreground` for de-emphasised fills and text, `--accent` for hover and selection, `--destructive` for danger, and `--border` / `--input` / `--ring` for edges
    - Each pair travels together: a `--*-foreground` is the contrast partner of its surface, so painting `bg-muted` and then picking the text colour by hand breaks the pair the generator maintains
    - The brand colour is declared there and nowhere else: our own components paint with `bg-primary` too, which is the only thing that keeps them in step with every generated one
    - A parallel brand scale is a second source of truth for one decision — the day `--primary` changes, everything painted with the other name quietly stops matching
    - A plain `@theme` sits beside it for what the generator does not decide: the font, type steps, radii of our own
    - Roles the generator has no token for — success, warning, info — are declared the same way it declares its own, as a surface and its foreground, so they behave under `.dark` like everything else. Reaching for `bg-green-100` instead leaves a status colour that no theme can reach
3.  **Turn on the switch that makes all of this real:**
    - `components.json` decides what the generator writes: with `cssVariables: false` every component it installs arrives with the palette baked in — `bg-neutral-900` instead of `bg-primary` — and the semantic layer stops existing
    - `baseColor` picks the neutral ramp those variables are seeded from, and it is read at generation time, so changing it later rewrites nothing that already exists
    - Both belong to the structure, not to the setup ceremony (see the folder-structure rule)
4.  **Reach for the token that names the role:**
    - Muted text is `text-muted-foreground`; a hover or selected row is `bg-accent`; an error message is `text-destructive`. A step off the neutral ramp standing in for any of them is the finding
    - The palette is not arbitrary — every ramp step is a real theme token — which is exactly why this slips through: it looks tokenised and still hardcodes a decision the semantic layer already owns
    - The test is whether the value survives a theme change. A role token does; a ramp step does not
5.  **Arbitrary values are a review flag:**
    - `bg-[#1d4ed8]`, `p-[13px]`, `text-[15px]` mean one of two things: the token exists and was not used, or the token is missing and must be added
    - Legitimate use is genuinely one-off geometry with no reuse — `grid-cols-[auto_1fr]`, `mask-[url(...)]`, a third-party magic offset
    - A color is almost never one-off, and a spacing value never is: `p-[13px]` means the markup drifted off the scale, and the fix is the nearest step — not a token of its own
6.  **A token outlives the diff that stops using it:**
    - The diff that removes a token's last consumer removes the token too — leaving it behind is how a stylesheet accumulates values nobody can tell apart from the live ones
    - Declaring ahead of use is not the same defect and is not a finding: a design system defines its scale before every step has a consumer, and a token waiting for its first caller is design, not debt
    - The generator's tokens are never pruned on either count — `--chart-*` and `--sidebar-*` sit unused until the component that needs them is installed, and removing them breaks the next `shadcn add`
    - The reverse direction is a finding: a value repeated across files and declared nowhere is a token that was never written down
7.  **Do not bypass the utility layer:**
    - `style={{ color: 'var(--color-primary)' }}` skips variants, merge resolution, and the sort order
    - The `style` prop is reserved for values computed at runtime (an animated transform, a measured offset)
8.  **v4 configuration:**
    - There is no `tailwind.config.js` by default; the theme is CSS
    - A JS config is reintroduced only through `@config` when a legacy plugin requires it
    - `@theme inline` is what makes the semantic layer work: it compiles `bg-background` down to `var(--background)` instead of copying the value, so the utility still follows the variable when `.dark` redefines it — a plain `@theme` freezes whatever the variable held at build time

**Incorrect (hardcoded values scattered across components, inline CSS variable):**

```tsx
type Props = React.ComponentProps<'span'>;

export function Badge({ children }: Props) {
  return (
    <span
      // Bad: brand color and spacing invented at the call site
      className="rounded-[7px] bg-[#1d4ed8] px-[13px] py-[5px] text-[13px] text-white"
      // Bad: the token exists, and reaching it through style skips the utility layer
      style={{ borderColor: 'var(--color-primary)' }}
    >
      {children}
    </span>
  );
}
```

**Correct (tokens declared in the theme, utilities resolve to them):**

```css
/* ./app/styles/app.css */
@import 'tailwindcss';

/* The variant that makes every dark: utility resolve against the .dark class */
@custom-variant dark (&:is(.dark *));

/* Written by `shadcn init`: the semantic layer every generated component reads,
   and the only place the brand colour is declared. Each surface ships with the
   foreground that is legible on it */
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary: oklch(0.53 0.19 262);
  --primary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --destructive: oklch(0.577 0.245 27);
  --destructive-foreground: oklch(0.985 0 0);

  /* Ours: the status roles the generator ships no token for */
  --success: oklch(0.55 0.14 150);
  --success-foreground: oklch(0.985 0 0);
  --warning: oklch(0.68 0.15 75);
  --warning-foreground: oklch(0.145 0 0);
  --info: oklch(0.58 0.15 240);
  --info-foreground: oklch(0.985 0 0);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --primary: oklch(0.62 0.19 262);
  --primary-foreground: oklch(0.145 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --destructive: oklch(0.704 0.191 22);
  --destructive-foreground: oklch(0.145 0 0);

  --success: oklch(0.63 0.15 150);
  --success-foreground: oklch(0.145 0 0);
  --warning: oklch(0.75 0.15 75);
  --warning-foreground: oklch(0.145 0 0);
  --info: oklch(0.65 0.15 240);
  --info-foreground: oklch(0.145 0 0);
}

/* inline, so bg-primary compiles to var(--primary) and keeps following the
   variable under .dark — a plain @theme would freeze the light value here */
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-success: var(--success);
  --color-success-foreground: var(--success-foreground);
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
  --color-info: var(--info);
  --color-info-foreground: var(--info-foreground);
}

/* Ours: the decisions the generator does not make. No --spacing here — the
   scale is Tailwind's and the design works in its steps */
@theme {
  --font-sans: 'Inter Variable', sans-serif;
  --radius-badge: 0.4375rem;
  --text-badge: 0.8125rem;
}
```

```tsx
import { cn } from '~/core/lib/utils';

type Props = React.ComponentProps<'span'>;

export function Badge({ className, ...props }: Props) {
  return (
    <span
      className={cn(
        'rounded-badge border border-primary bg-primary px-3 py-1 text-badge text-primary-foreground',
        className,
      )}
      {...props}
    />
  );
}
```

Reference: [Theme variables](https://tailwindcss.com/docs/theme)

### 5.2 Class Composition & Conditional Classes

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

### 5.3 State-Driven Styling With Data Attributes

**Impact (HIGH):** When state lives in a `data-*` attribute, the whole variant matrix is visible on one line of markup and the browser applies it. When state is expressed by swapping class strings in _JavaScript_, presentation scatters across event handlers and effects, `tailwind-merge` cannot resolve conflicts it never sees, and the rendered class list becomes impossible to predict while reading a diff.

**Guidelines:**

1.  **Expose state as data:**
    - Render `data-state="open"` or a boolean `data-active` and style with `data-[state=open]:` / `data-active:` variants
    - This is the convention headless libraries already emit — style their state instead of mirroring it in _React_ state
    - A generated component arrives already emitting it: _Radix_ writes `data-state`, `data-disabled`, `data-side` and `data-orientation` on its own primitives, so styling one means writing the variant, never adding a parallel boolean of ours to track what the component already announces
2.  **Descendants read the parent:**
    - Mark the container `group` and let children use `group-data-[state=open]:rotate-180`
    - Do not prop-drill a boolean whose only purpose is styling
3.  **Structural conditions:**
    - `has-*` styles a parent from its children (`has-[:checked]:border-primary`), removing wrappers that existed only to receive a class
    - `not-*` inverts without a second branch; `group` and `peer` are relationship variants and live in the responsive-and-variants rule
4.  **Never mutate classes imperatively:**
    - `element.classList.add(...)` or assigning `className` in an effect puts design state outside the render output
5.  **Boolean data attributes must be absent, not `"false"`:**
    - `data-active="false"` still matches the `data-active:` variant — the variant tests for presence
    - Render `data-active={isActive || undefined}` so the attribute disappears when false

**Incorrect (class toggling in an effect, prop-drilled styling boolean, data-active="false"):**

```tsx
type Props = {
  steps: Step[];
  currentIndex: number;
};

export function Stepper({ steps, currentIndex }: Props) {
  const barRef = useRef<HTMLDivElement>(null);

  // Bad: presentation applied outside the render output
  useEffect(() => {
    barRef.current?.classList.toggle('hidden', currentIndex === 0);
  }, [currentIndex]);

  return (
    <ol>
      {steps.map((s, index) => (
        <li
          key={s.id}
          // Bad: "false" still matches data-active:
          data-active={index === currentIndex ? 'true' : 'false'}
          className="data-active:bg-accent"
        >
          {s.label}
          {/* Bad: a boolean passed down only to pick a class */}
          <Check filled={index < currentIndex} />
        </li>
      ))}
      <div ref={barRef} />
    </ol>
  );
}
```

**Correct (state on the element, variants do the styling, attribute omitted when false):**

```tsx
type Props = {
  steps: Step[];
  currentIndex: number;
};

export function Stepper({ steps, currentIndex }: Props) {
  const getState = (index: number) => {
    if (index < currentIndex) {
      return 'complete';
    }

    if (index === currentIndex) {
      return 'current';
    }

    return 'upcoming';
  };

  return (
    <ol>
      {steps.map((s, index) => (
        <li
          key={s.id}
          data-state={getState(index)}
          // Good: not-* dims every step that is not the current one, with no
          // second branch and no extra attribute to carry the negation
          className="group flex items-center gap-3 not-data-[state=current]:opacity-60"
        >
          <button
            type="button"
            // Good: attribute is absent when inactive
            data-active={index === currentIndex || undefined}
            className="flex w-full items-center justify-between data-active:bg-accent"
          >
            {s.label}
            {/* Good: the child reads the group's state */}
            <Check className="opacity-0 group-data-[state=complete]:opacity-100" />
          </button>
        </li>
      ))}
    </ol>
  );
}
```

```tsx
// Good: the primitive already announces its own state, so there is nothing to
// mirror — the variant reads what Radix writes, and has-* styles the container
// from its own child instead of a wrapper that existed to carry a class
<AccordionItem value="billing" className="group border-b">
  <AccordionTrigger className="data-[state=open]:text-primary">
    Billing
    <Chevron className="transition-transform group-data-[state=open]:rotate-180" />
  </AccordionTrigger>
  <AccordionContent>{item.body}</AccordionContent>
</AccordionItem>;

<label className="rounded-md border p-3 has-[:checked]:border-primary">
  <input type="checkbox" />
  <span>Enable notifications</span>
</label>;
```

Reference: [Styling based on data attributes](https://tailwindcss.com/docs/hover-focus-and-other-states#data-attributes)

### 5.4 Responsive & Variant Usage

**Impact (HIGH):** Rendering the same content twice — once for mobile, once for desktop — doubles the DOM, duplicates every future edit, and guarantees the two copies drift. The same applies to a second component for dark mode. Variants exist so one tree covers every context; reaching for _JavaScript_ breakpoints moves layout decisions off the platform and into a render cycle that runs after paint.

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
    - These replace `useState` that only existed to drive a class
4.  **Container queries for components:**
    - When a component's width is not the viewport's (sidebar, modal, grid cell), use `@container` on the wrapper and `@sm:` / `@md:` on children
    - A card that must look right in two column widths is a container-query problem, not a breakpoint problem
5.  **Dark mode belongs to the theme, not to the components:**
    - `bg-card` is already right in both themes, because `--card` is what changes under `.dark` (see the theme-tokens rule for the variant that wires it)
    - A `dark:` inside a component is therefore a signal: it says the element was painted with something that does not change — a palette step — and the fix is the token, not the variant
    - Where `dark:` genuinely earns its place — a raster image, a shadow, a third-party surface we cannot tokenise — it is a variant on the same element, never a parallel component
6.  **No JS breakpoints for layout:**
    - A `useMediaQuery` hook driving pure layout duplicates CSS in _JavaScript_ and flashes on first render

**Incorrect (duplicated trees, dark mode as a second component):**

```tsx
type Props = { product: Product };

export function ProductCard({ product }: Props) {
  const theme = useSettingsStore((s) => s.theme);

  // Bad: a whole second component for a colour the theme already swaps
  if (theme === 'dark') {
    return <ProductCardDark product={product} />;
  }

  return (
    <>
      {/* Bad: the same content rendered twice */}
      <div className="block bg-card p-4 md:hidden">
        <h3 className="text-base">{product.name}</h3>
        <p className="text-sm">{product.price}</p>
      </div>
      <div className="hidden bg-card p-8 md:block">
        <h3 className="text-xl">{product.name}</h3>
        <p className="text-base">{product.price}</p>
      </div>
    </>
  );
}
```

**Correct (one tree, mobile-first variants, container query, dark resolved in the theme):**

```tsx
type Props = { product: Product };

export function ProductCard({ product }: Props) {
  return (
    <div className="@container">
      {/* Good: no dark: anywhere — the token already changes with the theme */}
      <article className="bg-card p-4 @md:p-8">
        <h3 className="text-base @md:text-xl">{product.name}</h3>
        <p className="text-sm @md:text-base">{product.price}</p>
      </article>
    </div>
  );
}
```

```tsx
{
  /* group and peer replace state that only drove a class */
}
<Link
  to="/reports"
  className="group flex items-center gap-2 rounded-md p-3 hover:bg-accent"
>
  <span className="text-muted-foreground group-hover:text-primary">
    Reports
  </span>
</Link>;

<label className="flex items-center gap-2">
  <input type="checkbox" name="archived" className="peer sr-only" />
  <span className="rounded-md border px-3 py-1 peer-checked:border-primary peer-checked:bg-accent">
    Include archived
  </span>
</label>;
```

Reference: [Responsive design](https://tailwindcss.com/docs/responsive-design)

### 5.5 @apply, Custom Utilities & Overrides

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

### 5.6 Class Attribute Formatting & Order

**Impact (MEDIUM):** Sorting is not what settles a conflict — the stylesheet is, which is the whole reason `cn()` exists — so order itself is never worth a review comment once the formatter runs. What lifts this above cosmetics is everything around it: a plugin that never sees `cn()` leaves every composed string unsorted, contradictory utilities left inside one string resolve by stylesheet order instead of by intent, and a formatter let loose on generated folders fills diffs with noise that hides the real edits.

**Guidelines:**

1.  **The formatter owns the order:**
    - `prettier-plugin-tailwindcss` is the single authority; never sort by hand and never raise ordering as a review comment when it is configured
2.  **Configure it for composed strings:**
    - Set `tailwindStylesheet` to the main CSS entry point (v4 replaced the `tailwindConfig` option)
    - List helpers in `tailwindFunctions` (`cn`, `cva`) and custom attributes in `tailwindAttributes`, otherwise those strings go unsorted
    - Load it last in `plugins`: it rewrites what the plugins before it produced, and anything registered after it leaves the classes unsorted
    - `core/lib/shadcn/` stays in `.prettierignore`, so the formatter never rewrites generated code and any diff there is a deliberate edit (see the folder-structure rule)
3.  **The plugin's distribution is the distribution:**
    - Never regroup a sorted string by hand into blocks of layout, spacing and colour — the plugin sorts inside each string literal and never across two, so splitting one literal into several is how a hand-made order survives review disguised as readability
    - What earns its own argument is meaning, not appearance: base classes in the first, conditionals after them
    - Where the call wraps is decided by the print width, which makes line breaks a formatting outcome and never a review topic
4.  **What review should still flag:**
    - Dead or contradictory utilities (`flex flex-col block`, `p-4 p-6`) — the formatter sorts, it does not deduplicate
    - Utilities that no longer apply after a refactor, left behind in the string

**Incorrect (unconfigured plugin, hand-grouped literals, contradictory utilities):**

```js
// ./prettier.config.js
// Bad: no stylesheet reference and no helper functions — cn() strings never get sorted
export default { plugins: ['prettier-plugin-tailwindcss'] };
```

```tsx
// Bad: hand-grouped into blocks the plugin can no longer sort against each other,
// with contradictory utilities and a leftover from a previous layout
<div
  className={cn(
    'block flex flex-col md:flex-row',
    'p-6 p-4',
    'text-sm',
    isActive && 'bg-accent',
  )}
>
  ...
</div>
```

**Correct (configured plugin, one base literal in the plugin's order, no dead utilities):**

```js
// ./prettier.config.js
export default {
  plugins: ['prettier-plugin-tailwindcss'],
  tailwindStylesheet: './app/styles/app.css',
  tailwindFunctions: ['cn', 'cva'],
  tailwindAttributes: ['containerClassName'],
};
```

```tsx
<div
  className={cn(
    // Good: one literal for the base, left in whatever order the plugin produced
    'flex flex-col gap-4 p-4 text-sm text-muted-foreground md:flex-row',
    isActive && 'bg-accent',
  )}
>
  ...
</div>
```

Reference: [prettier-plugin-tailwindcss](https://github.com/tailwindlabs/prettier-plugin-tailwindcss)

---

## 6. Performance & Robustness

### 6.1 Render Stability & Memoization

**Impact (MEDIUM):** Re-rendering is normal and usually cheap, and with the _React Compiler_ enabled the identity of values created during render is no longer the developer's problem. What review is left with is a different, smaller set of defects: memoization written by hand that only duplicates what the compiler already did, code the compiler cannot analyze and therefore silently skips, and a component subscribed to more of the store than it ever reads — which no amount of memoization fixes.

**Guidelines:**

1.  **The compiler memoizes, you do not:**
    - Objects, arrays, and functions created during render are memoized for you; `useMemo`, `useCallback`, and `memo` are the exception rather than the baseline
    - An inline literal in props is not a defect — `options={{ columns: 3 }}` is precisely the case the compiler covers
    - A hand-written memo has to say, in a comment, what the compiler could not see; without that, review cannot tell a real need from a habit carried over
2.  **Write code the compiler can analyze:**
    - It skips any component whose code might break the Rules of React rather than risk changing its behavior; with the recommended `panicThreshold: 'none'` that skip does not fail the build and leaves nothing in the source to read
    - The reverse failure matters more: when a violation is subtle enough that the _ESLint_ plugin misses it, the compiler optimizes a component it should have skipped, and the defect surfaces at runtime
    - Either way the finding is the rule violation itself, never a missing memo — and a `"use no memo"` left in the code is a violation someone worked around instead of fixing
    - What actually compiled is measurable rather than guessable: `react-compiler-healthcheck` reports the ratio, the `logger` option logs per-file compilation events, and _React DevTools_ badges the components that were compiled
3.  **Subscribe to a slice, not to the store:**
    - Reading the whole store re-renders the component on every change in it, whatever changed; a selector narrows that to the field the component actually reads
    - A selector that builds an object — `useStore((s) => ({ a: s.a, b: s.b }))` — returns a fresh reference on every call and re-renders every time, which is a subscription bug wearing the costume of a memoization bug. When several fields must come from one call, `useShallow` compares them field by field instead of by reference
    - This is the one identity problem the compiler cannot reach: it memoizes what a render produces, not what a component subscribed to
4.  **Constants belong to the module:**
    - A value that depends on neither props nor state has no reason to be built inside a render, compiler or not
    - This is a question of where the value belongs, not of what it costs to create
5.  **Effect dependencies are correctness, not performance:**
    - The compiler stabilizes identities; it does not decide when an effect should re-run
    - A dependency array remains a statement about what the effect reads (see the effect-discipline rule)

**Incorrect (a selector that rebuilds an object, and memoization the compiler already did):**

```tsx
type Props = { widgets: Widget[] };

export function Dashboard({ widgets }: Props) {
  // Bad: the selector returns a new object every call, so this re-renders on
  // every store change — not only when theme or density move
  const { theme, density } = useSettingsStore((s) => ({
    theme: s.theme,
    density: s.density,
  }));

  // Bad: the compiler already memoizes this — the wrapper states nothing
  const handleSelect = useCallback((id: string) => selectWidget(id), []);

  return (
    <WidgetGrid
      widgets={widgets}
      theme={theme}
      density={density}
      onSelect={handleSelect}
    />
  );
}
```

**Correct (one subscription per field, constants hoisted, the rest left to the compiler):**

```tsx
// Good: depends on nothing from render, so it does not belong inside it
const GRID_OPTIONS = { columns: 3 };

type Props = { widgets: Widget[] };

export function Dashboard({ widgets }: Props) {
  // Good: a density change no longer re-renders anything that only reads theme
  const theme = useSettingsStore((s) => s.theme);
  const density = useSettingsStore((s) => s.density);

  return (
    // Good: the literal and the arrow are exactly what the compiler memoizes
    <WidgetGrid
      widgets={widgets}
      theme={theme}
      density={density}
      options={GRID_OPTIONS}
      onSelect={(id) => selectWidget(id)}
    />
  );
}
```

```tsx
// Good: a hand-written memo that states what the compiler could not cover.
// The chart library holds this array by reference and re-initialises whenever it
// changes, so its identity is part of an external contract, not of React's render.
const series = useMemo(() => buildSeries(rows), [rows]);
```

Reference: [React Compiler](https://react.dev/learn/react-compiler)

### 6.2 Layout Stability & Overflow

**Impact (HIGH):** Layout shift and horizontal overflow are the two defects utility CSS makes easiest to ship. An `img` with no reserved box pushes the page down when it loads; `w-screen` scrolls sideways as soon as a scrollbar exists; a flex child with long content stretches past its container instead of truncating. All three are one utility away from being fixed, and all three are visible in review.

**Guidelines:**

1.  **Reserve the box before load:**
    - Every `img` declares `width` and `height` attributes, or sits in an `aspect-*` container with `object-cover`
    - Attributes plus `h-auto w-full` gives a responsive image that still reserves its ratio
2.  **Loading strategy:**
    - `loading="lazy"` below the fold; the LCP image stays eager and may be preloaded from the route
3.  **Viewport units:**
    - `w-screen` is `100vw`, which ignores the scrollbar and overflows — use `w-full`
    - `h-screen` fights the mobile dynamic toolbar — prefer `h-dvh` (or `min-h-dvh`)
    - Full-bleed inside a constrained container is a deliberate pattern, not a `w-screen` accident
4.  **Fixed heights on text:**
    - `h-[72px]` on a text container clips at other font sizes and languages — use `min-h-*` or let the content size the box
    - `line-clamp-2` bounds the text instead of bounding the box
5.  **Overflow needs a decision:**
    - A flex or grid child that can receive long content needs `min-w-0` — flex items default to `min-width: auto` and refuse to shrink below their content
    - Then choose the behavior: `truncate`, `line-clamp-*`, or `overflow-auto`
6.  **Async content reserves the same box:**
    - A skeleton or pending fallback must occupy the resolved content's box, otherwise the shift only moves from load time to resolve time

**Incorrect (unsized image, w-screen, fixed text height, unshrinkable flex child):**

```tsx
type Props = { file: Attachment };

export function AttachmentRow({ file }: Props) {
  return (
    <>
      {/* Bad: no dimensions — the page jumps when this loads */}
      <img src={file.previewUrl} className="w-full rounded-lg" />
      {/* Bad: 100vw ignores the scrollbar and scrolls the page sideways */}
      <section className="w-screen bg-muted py-12">
        <div className="mx-auto flex max-w-3xl items-center gap-3">
          {/* Bad: no min-w-0, so a long filename blows out the row instead of truncating */}
          <div className="flex-1">
            <p className="h-[24px] truncate">{file.name}</p>
          </div>
          <button type="button">Download</button>
        </div>
      </section>
    </>
  );
}
```

**Correct (reserved ratio, w-full, content-sized text, min-w-0 on the flex child):**

```tsx
type Props = { file: Attachment };

export function AttachmentRow({ file }: Props) {
  return (
    <>
      <img
        src={file.previewUrl}
        width={1200}
        height={630}
        loading="lazy"
        className="h-auto w-full rounded-lg"
      />
      <section className="w-full bg-muted py-12">
        <div className="mx-auto flex max-w-3xl items-center gap-3">
          <div className="min-w-0 flex-1">
            <p className="truncate">{file.name}</p>
          </div>
          <button type="button">Download</button>
        </div>
      </section>
      {/* Unknown intrinsic size: reserve the ratio instead */}
      <figure>
        <div className="mb-2 aspect-video overflow-hidden rounded-lg">
          <img src={file.previewUrl} className="size-full object-cover" />
        </div>
        <figcaption className="text-sm text-muted-foreground">
          Attachment preview
        </figcaption>
      </figure>
    </>
  );
}
```

Reference: [Cumulative Layout Shift](https://web.dev/articles/cls)

### 6.3 Source Detection & CSS Footprint

**Impact (MEDIUM):** _TailwindCSS_ only generates the classes it finds in the sources it scans. Two failure modes follow: a template the scanner never sees ships unstyled in production while looking fine locally, and a defensive safelist added to "fix" it inflates the stylesheet with thousands of unused rules. v4 detects sources automatically, so the correct fix is a targeted declaration, not a wider net.

**Guidelines:**

1.  **Automatic detection is the default:**
    - v4 has no `content` array to maintain; it scans the project, respects `.gitignore`, and skips binaries
    - Do not port a v3 `content` config forward out of habit
2.  **Register sources the scanner cannot reach:**
    - Anything outside the source root, or in a path `.gitignore` excludes — `node_modules` being the common one — needs `@source "…"`
    - This is why a component library installed from npm can ship with its classes missing
3.  **Narrow the scan when it is noisy:**
    - `@source not "…"` excludes vendor or generated directories rather than accepting the scan cost
4.  **Classes that live in data:**
    - When a class name comes from outside the codebase — a CMS field, an API response — declare exactly those with `@source inline("…")`
    - Prefer a static map from data value to a complete class string; inline declaration is the fallback when the value genuinely cannot be mapped

**Incorrect (v3 config ported forward, broad safelist to paper over a missing source):**

```js
// ./tailwind.config.js
// Bad: v4 does not need this, and the safelist ships ~1,500 unused rules
export default {
  content: ['./app/**/*.{ts,tsx}'],
  safelist: [
    { pattern: /(bg|text|border)-(red|green|amber|sky)-(100|500|800)/ },
  ],
};
```

```tsx
// Bad: the class comes from data and is built by interpolation
<span className={`bg-${status.color}-100 text-${status.color}-800`}>
  {status.label}
</span>
```

**Correct (automatic detection, explicit source registration, static map with a scoped inline fallback):**

```css
/* ./app/styles/app.css */
@import 'tailwindcss';

/* Good: a template the scanner cannot reach on its own */
@source "../../node_modules/@acme/ui/dist";

/* Good: exclude a generated directory instead of widening the net */
@source not "../../public/vendor";

/* Good: only these classes come from CMS data */
@source inline("bg-{success,warning,info} text-{success,warning,info}-foreground");
```

```tsx
const STATUS_STYLES = {
  error: 'bg-destructive text-destructive-foreground',
  ok: 'bg-success text-success-foreground',
  warn: 'bg-warning text-warning-foreground',
} as const;

// Good: complete static strings, nothing for the scanner to miss
<span className={STATUS_STYLES[status.kind]}>{status.label}</span>;
```

Reference: [Detecting classes in source files](https://tailwindcss.com/docs/detecting-classes-in-source-files)
