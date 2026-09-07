---
name: react-best-practices
description: Standards for what React renders to on the web — semantic HTML markup, forms through react-hook-form and the shadcn/ui Form components, TailwindCSS v4 theming over theme tokens, layout stability, and the contract with the shadcn/ui generator. Use when reviewing, writing, or refactoring markup, forms, class attributes, theme tokens, or shadcn/ui setup in a web project. Everything independent of the renderer — effects, state, the query layer, component composition and typing — lives in react-core-best-practices, which a web project loads alongside this one.
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

| Priority | Category                 | Peak impact | Prefix  |
| :------- | :----------------------- | :---------- | :------ |
| 1        | Semantic Markup          | CRITICAL    | `sem-`  |
| 2        | Styling with TailwindCSS | CRITICAL    | `tw-`   |
| 3        | View Structure           | HIGH        | `arch-` |
| 4        | Performance & Robustness | HIGH        | `perf-` |

Priority orders where to look first; peak impact is the strongest rule in the section, matching the table of contents in `AGENTS.md`. They disagree on purpose — a section can hold one blocking rule and several that only ever produce suggestions.

## Quick Reference

### 1. Semantic Markup (CRITICAL)

- `sem-interactive-elements` - Native `button` / `a` instead of click handlers on `div`; `type` on every form button
- `sem-document-landmarks` - Landmarks belong to the layout route; heading rank is structure, not size; every page declares its own title and description
- `sem-form-markup` - Every form goes through `react-hook-form` and the Form components; no field state of your own, real submission through `handleSubmit`
- `sem-content-elements` - Lists, tables, `figure`, and `time` for the data they represent; `dayjs` formats what `time` carries

### 2. Styling with TailwindCSS (CRITICAL)

- `tw-theme-tokens` - Design decisions live in `@theme`; the variable-backed semantic layer only where `shadcn` or a theme swap reads it; arbitrary values are review flags
- `tw-state-driven-styling` - Style from `data-*` with variants instead of toggling classes in _JavaScript_; an arbitrary variant is a selector hiding in a class attribute
- `tw-variants-and-responsive` - Mobile-first, `group`/`peer`, container queries; dark mode is resolved in the theme, so `dark:` in a component is a signal
- `tw-apply-and-custom-layers` - `@apply` as an escape hatch only; `@utility` for real primitives, registered with `extendTailwindMerge`
- `tw-class-formatting` - `prettier-plugin-tailwindcss` owns class order; review catches what it cannot

### 3. View Structure (HIGH)

- `arch-view-structure` - `components/ui/` is the generator's target; `components.json` is part of the structure, and `core/lib/shadcn/` is read-only

### 4. Performance & Robustness (HIGH)

- `perf-layout-stability` - Intrinsic media sizing, `h-dvh` over `h-screen`, `min-w-0` on flex children
- `perf-css-footprint` - v4 automatic source detection, `@source inline()` over broad safelists

## How to Use

Read individual rule files for detailed explanations and code examples:

```plaintext
rules/*.md
```

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md` (generated — see `README.md`).
