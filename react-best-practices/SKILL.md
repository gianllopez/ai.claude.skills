---
name: react-best-practices
description: Standards for what React renders to on the web — semantic HTML markup, forms through react-hook-form and the shadcn/ui Form components, TailwindCSS v4 theming over semantic tokens, layout stability, and the contract with the shadcn/ui generator. Use when reviewing, writing, or refactoring markup, forms, class attributes, theme tokens, or shadcn/ui setup in a web project. Everything independent of the renderer — effects, state, the query layer, component composition and typing — lives in react-core-best-practices, which a web project loads alongside this one.
license: MIT
metadata:
  author: gianllopez
  version: 1.0.0
---

# React Best Practices

Standards for the part of a _React_ application that only exists on the web: the markup that carries the meaning, the styling that presents it, and the generator that writes components into the project.

Everything that does not change with the renderer — effect and state discipline, the typed query layer, component composition, file structure and typing — is in `react-core-best-practices`. **A web project loads both.** This skill assumes that one is present and never restates it.

Every rule names a defect concrete enough to point at in a diff — the wrong element for the content, a class string the build cannot see, a palette step standing in for a role — and shows the correct shape beside it. That is what makes the same rule usable in both directions: the **Correct** block is what to write, the defect is what to look for.

**Scope:** the _DOM_ and what styles it. Accessibility auditing is deliberately out of scope — semantic rules are justified by structural correctness, machine-readability, and maintainability. The reference stack is _React Router_ in SPA mode with `react-hook-form` and `shadcn/ui` over _TailwindCSS_ v4.

## When to Apply

Reference these guidelines when:

- Choosing the element for a block of markup (sectioning, interactive controls, forms, tabular data)
- Building or reviewing a form, its fields, its validation, and its submission
- Adding colors, fonts, or breakpoints, or reaching for an arbitrary value
- Writing a `className` attribute: variants, responsive behavior, state-driven styling
- Installing or theming a `shadcn/ui` component, or touching `components.json`
- Configuring source detection, custom utilities, or `prettier-plugin-tailwindcss`
- Sizing media, or bounding a container that can receive long content
- Deciding where a view-layer file lives, or whether something under `core/lib/shadcn/` may be edited

## Rule Categories by Priority

| Priority | Category                 | Peak impact | Prefix   |
| :------- | :----------------------- | :---------- | :------- |
| 1        | Semantic Markup          | CRITICAL    | `sem-`   |
| 2        | Styling with TailwindCSS | CRITICAL    | `tw-`    |
| 3        | View Structure           | HIGH        | `arch-`  |
| 4        | Performance & Robustness | HIGH        | `perf-`  |

Priority orders where to look first; peak impact is the strongest rule in the section, matching the table of contents in `AGENTS.md`. They disagree on purpose — a section can hold one blocking rule and several that only ever produce suggestions.

## Quick Reference

### 1. Semantic Markup (CRITICAL)

- `sem-interactive-elements` - Native `button` / `a` instead of click handlers on `div`; `type` on every form button
- `sem-document-landmarks` - Landmarks belong to the layout route; heading rank is structure, not size; every page declares its own title and description
- `sem-form-markup` - Every form goes through `react-hook-form` and the Form components; no field state of your own, real submission through `handleSubmit`
- `sem-content-elements` - Lists, tables, `figure`, and `time` for the data they represent; `dayjs` formats what `time` carries

### 2. Styling with TailwindCSS (CRITICAL)

- `tw-theme-tokens` - Two layers: the semantic tokens `shadcn` writes and a plain `@theme` for the rest; arbitrary values and palette steps in semantic roles are review flags
- `tw-state-driven-styling` - Style from `data-*` with variants instead of toggling classes in _JavaScript_; an arbitrary variant is a selector hiding in a class attribute
- `tw-variants-and-responsive` - Mobile-first, `group`/`peer`, container queries; dark mode is resolved in the theme, so `dark:` in a component is a signal
- `tw-apply-and-custom-layers` - `@apply` as an escape hatch only; `@utility` for real primitives, registered with `extendTailwindMerge`
- `tw-class-formatting` - `prettier-plugin-tailwindcss` owns class order; review catches what it cannot

### 3. View Structure (HIGH)

- `arch-view-structure` - `components/ui/` is the generator's target; `components.json` is part of the structure, and `core/lib/shadcn/` is read-only

### 4. Performance & Robustness (HIGH)

- `perf-layout-stability` - Intrinsic media sizing, `h-dvh` over `h-screen`, `min-w-0` on flex children
- `perf-css-footprint` - v4 automatic source detection, `@source inline()` over broad safelists

## Applying These Rules

### While writing

There is no triage. The **Correct** block of every rule is the target, including everything the _Do not report_ list below forgives: that list keeps review proportionate to what a diff can justify, and never licenses a lower standard while authoring.

Where a rule states a convention rather than a defect — where a file lives, how it is named, which library owns a concern — it is the decision already made, not one of several options.

### While reviewing

Findings are only worth raising when they change behavior, break the design system, or add maintenance cost. The lists below cover this skill's rules; the defects `react-core-best-practices` governs are triaged by that skill.

**Block the change when:**

- An interactive element is a `div` with `onClick`, or a form button has no `type`
- A form keeps its own field state, or submits through a button's `onClick` instead of the form
- A new color or radius value bypasses `@theme`, or a spacing value steps off _Tailwind_'s scale (`p-[13px]`)
- A palette step stands in for a role the semantic layer owns (`text-neutral-500` for `text-muted-foreground`, `text-red-600` for `text-destructive`)
- `components.json` sets `cssVariables: false` — every component generated from then on ships with the palette baked in
- A page renders a second `main`, or skips a heading rank to get a smaller size
- A diff edits anything under `core/lib/shadcn/` — that folder is generated and read-only

**Raise as a suggestion when:**

- `@apply` is used where a component would do
- Media has no reserved box, or a flex child can overflow without `min-w-0`
- A `dark:` variant appears in a component, where a token would already be right in both themes
- The same content is rendered twice to switch at a breakpoint

**Do not report:**

- Class ordering, when `prettier-plugin-tailwindcss` is configured — the formatter owns it
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

> **`app/routes/invoices.tsx:24`** — `sem-interactive-elements` (`CRITICAL`)
> The row action is a `div`, so it cannot be reached by keyboard and the browser gives it none of a button's behavior.
>
> ```tsx
> <button type="button" onClick={handleOpen}>
> ```

When a file breaks no rule, say so in one line and stop. If the project tracks review state and that file sits at `pending`, offer to mark it `done` — the assertion that something was reviewed is the user's to make, never one to act on unprompted.

## How to Use

Read individual rule files for detailed explanations and code examples:

```plaintext
rules/*.md
```

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md` (generated — see `README.md`).
