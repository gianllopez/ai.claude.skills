---
name: react-best-practices
description: React application standards for writing and reviewing code — effect and state discipline, a typed React Query data layer, component composition and typing, semantic JSX markup, and TailwindCSS v4 utility usage over shadcn/ui semantic tokens. Reference stack is React Router in SPA mode with react-query-kit, react-hook-form and zustand. Use when reviewing, writing, or refactoring React components, hooks, queries, routes, forms, stores, class attributes, or shadcn/ui setup and theming.
license: MIT
metadata:
  author: gianllopez
  version: 1.0.0
---

# React Best Practices

Standards for writing and reviewing _React_ applications. Framework-agnostic — examples use _React Router_ because that is the reference stack, but the principles hold for any router that owns navigation data.

Every rule names a defect concrete enough to point at in a diff — an effect that should not exist, a second source of truth, a request that starts after paint, the wrong element for the content, a class string the build cannot see — and shows the correct shape beside it. That is what makes the same rule usable in both directions: the **Correct** block is what to write, the defect is what to look for.

**Scope:** _React_ application code and the markup and styling it renders. Accessibility auditing is deliberately out of scope — semantic rules are justified by structural correctness, machine-readability, and maintainability.

## When to Apply

Reference these guidelines when:

- Reviewing a diff that touches components, hooks, route modules, or `className` attributes
- Writing or refactoring a `useEffect`, or deciding where a piece of state belongs
- Loading data for a route, or handling its pending, empty, and error branches
- Designing a component's props: composition, variants, and typing
- Choosing the element for a block of markup (sectioning, interactive controls, forms, tabular data)
- Building or reviewing a form, its fields, its validation, and its submission
- Deciding whether a piece of shared state earns a `zustand` store, and which slice a component subscribes to
- Adding colors, fonts, or breakpoints, or reaching for an arbitrary value
- Installing or theming a `shadcn/ui` component, or touching `components.json`
- Configuring source detection, custom utilities, or `prettier-plugin-tailwindcss`

## Rule Categories by Priority

| Priority | Category                 | Peak impact | Prefix   |
| :------- | :----------------------- | :---------- | :------- |
| 1        | State & Effects          | CRITICAL    | `state-` |
| 2        | Component Architecture   | HIGH        | `arch-`  |
| 3        | Data Flow                | HIGH        | `data-`  |
| 4        | Semantic Markup          | CRITICAL    | `sem-`   |
| 5        | Styling with TailwindCSS | CRITICAL    | `tw-`    |
| 6        | Performance & Robustness | HIGH        | `perf-`  |

Priority orders where to look first; peak impact is the strongest rule in the section, matching the table of contents in `AGENTS.md`. They disagree on purpose — a section can hold one blocking rule and several that only ever produce suggestions.

## Quick Reference

### 1. Component Architecture (HIGH)

- `arch-folder-structure` - `core/` owns logic and data, the view composes it; imports flow one direction
- `arch-composition-patterns` - Slots and children over a boolean per screen; compound components for structure, render props only for internal state
- `arch-component-extraction` - When repeated markup becomes a component, and how `cva` exposes its variants
- `arch-typing-conventions` - `ComponentProps` over hand-rolled props; unions over impossible boolean combinations
- `arch-markup-minimalism` - Delete wrappers that only carry classes; spacing comes from the parent
- `arch-syntax-conventions` - Short-hand iterators, `handle*` implementations, arrow functions inside components, braces on every conditional, ternary over `&&`

### 2. State & Effects (CRITICAL)

- `state-effect-discipline` - Effects synchronize with external systems only; never derive, never react to events, never fetch
- `state-derived-values` - Compute in render instead of storing a second source of truth
- `state-colocation` - Push state down; the _URL_ owns what must survive a reload; shared state goes to a `zustand` store, never to a context of your own
- `state-identity-and-keys` - Keys come from the data; `key` is the reset mechanism, not an effect

### 3. Data Flow (HIGH)

- `data-query-layer` - Typed `react-query-kit` hooks per domain; keys declared once; auth in interceptors, not components
- `data-async-states` - Pending, empty, error, and success are four branches, not one

### 4. Semantic Markup (CRITICAL)

- `sem-interactive-elements` - Native `button` / `a` instead of click handlers on `div`; `type` on every form button
- `sem-document-landmarks` - Landmarks belong to the layout route; heading rank is structure, not size; every page declares its own title and description
- `sem-form-markup` - Every form goes through `react-hook-form` and the Form components; no field state of your own, real submission through `handleSubmit`
- `sem-content-elements` - Lists, tables, `figure`, and `time` for the data they represent; `dayjs` formats what `time` carries

### 5. Styling with TailwindCSS (CRITICAL)

- `tw-theme-tokens` - Two layers: the semantic tokens `shadcn` writes and a plain `@theme` for the rest; arbitrary values and palette steps in semantic roles are review flags
- `tw-class-composition` - `cn()` with `tailwind-merge`; never build class names by interpolation
- `tw-state-driven-styling` - Style from `data-*` with variants instead of toggling classes in _JavaScript_
- `tw-variants-and-responsive` - Mobile-first, `group`/`peer`, container queries; dark mode is resolved in the theme, so `dark:` in a component is a signal
- `tw-apply-and-custom-layers` - `@apply` as an escape hatch only; `@utility` for real primitives
- `tw-class-formatting` - `prettier-plugin-tailwindcss` owns class order; review catches what it cannot

### 6. Performance & Robustness (HIGH)

- `perf-render-stability` - The compiler owns identity; subscribe to a store slice, hoist constants, justify every hand-written memo
- `perf-layout-stability` - Intrinsic media sizing, `h-dvh` over `h-screen`, `min-w-0` on flex children
- `perf-css-footprint` - v4 automatic source detection, `@source inline()` over broad safelists

## Applying These Rules

### While writing

There is no triage. The **Correct** block of every rule is the target, including everything the _Do not report_ list below forgives: that list keeps review proportionate to what a diff can justify, and never licenses a lower standard while authoring.

Where a rule states a convention rather than a defect — where a file lives, how it is named, which library owns a concern — it is the decision already made, not one of several options.

### While reviewing

Findings are only worth raising when they change behavior, break the design system, or add maintenance cost. Triage each one:

**Block the change when:**

- An effect derives state, reacts to an event, or fetches route data
- A dependency array was trimmed to stop a loop
- Index keys appear on a list that can reorder, filter, or hold state
- A class name is assembled at runtime (`bg-${color}-500`) — it ships unstyled
- An interactive element is a `div` with `onClick`, or a form button has no `type`
- A new color or radius value bypasses `@theme`, or a spacing value steps off _Tailwind_'s scale (`p-[13px]`)
- A palette step stands in for a role the semantic layer owns (`text-neutral-500` for `text-muted-foreground`, `text-red-600` for `text-destructive`)
- `components.json` sets `cssVariables: false` — every component generated from then on ships with the palette baked in
- A reusable component ignores an incoming `className`
- An async view has no error or empty branch
- A diff edits anything under `core/lib/shadcn/` — that folder is generated and read-only

**Raise as a suggestion when:**

- State could be derived, or belongs in the _URL_ instead of a component
- A component is configured by flags where composition would do
- Props are hand-rolled instead of extending `ComponentProps`
- A wrapper element exists only to carry classes
- `@apply` is used where a component would do
- Media has no reserved box, or a flex child can overflow without `min-w-0`

**Do not report:**

- Class ordering, when `prettier-plugin-tailwindcss` is configured — the formatter owns it
- A missing `useMemo` / `useCallback` with no measured cost, especially where the _React Compiler_ is enabled
- Re-renders that are cheap and cross no memoization boundary
- Utility repetition that appears once or twice, or repetition inside a `map()`
- An arbitrary value that is genuinely one-off geometry (`grid-cols-[auto_1fr]`, a `mask`)
- A theme token declared ahead of its first consumer — a design system defines its scale before every step is used

State the impact level with each finding so the author can sort blocking defects from polish.

### Reporting findings

Resolve the target first, because it fixes what may be reported:

- A commit SHA, or "the last commit" — only the lines that commit changed
- A file or a path — the whole file, not just its recent history
- Neither — the working diff

Reading is never limited by that scope: open the rest of the file whenever context is what makes a finding judgeable. On a commit review, a defect that predates the change is not a finding unless the change makes it worse — otherwise every review reopens the whole file.

Nothing else belongs in the answer. No summary of what the change does, no preamble, no restating a rule's rationale. Findings are ordered by impact, blocking first, and each one is four things: where it is, which rule it breaks, what is wrong in one sentence, and the fix as code.

> **`app/routes/invoices.tsx:24`** — `state-effect-discipline` (`CRITICAL`)
> The effect copies the computed total into state, so it renders stale for one pass every time `invoice` changes.
>
> ```tsx
> const total = invoice.items.reduce((sum, i) => sum + i.price, 0);
> ```

When a file breaks no rule, say so in one line and stop. If the project tracks review state and that file sits at `pending`, offer to mark it `done` — the assertion that something was reviewed is the user's to make, never one to act on unprompted.

## How to Use

Read individual rule files for detailed explanations and code examples:

```plaintext
rules/*.md
```

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md` (generated — see `README.md`).
