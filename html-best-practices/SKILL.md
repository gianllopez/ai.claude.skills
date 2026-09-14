---
name: html-best-practices
description: Standards for markup and styling that hold regardless of the meta-framework rendering them — semantic HTML elements, document landmarks and heading structure, content elements for lists/tables/media, TailwindCSS v4 theme tokens, state-driven styling with data attributes, responsive and dark-mode variants, @apply/@utility discipline, class-attribute formatting, layout stability, and CSS source-detection footprint. Use when reviewing, writing, or refactoring HTML markup, class attributes, theme tokens, or Tailwind configuration in any web project. Framework-specific concerns live elsewhere: react-best-practices for react-hook-form/shadcn-generated forms and the shadcn view-structure contract; astro-best-practices for scoped component styles, the Astro compiler, and content collections. A web project loads this skill alongside whichever of those applies.
license: MIT
metadata:
  author: gianllopez
  version: 1.0.0
---

# HTML Best Practices

Standards for the part of a web _UI_ that is the same no matter which meta-framework compiles it down to _HTML_: the element that carries the meaning, the _CSS_ that presents it, and the _TailwindCSS_ v4 theme it presents through.

This skill deliberately says nothing about a specific renderer's forms library, generator contract, or compiler. `react-best-practices` and `astro-best-practices` each load this skill alongside their own — one project rarely needs both — and add only what genuinely does not survive the move from one to the other.

Every rule names a defect concrete enough to point at in a diff — the wrong element for the content, a class string the build cannot see, a palette step standing in for a role — and shows the correct shape beside it.

**Scope:** the _DOM_ and what styles it, independent of the framework. Accessibility auditing is deliberately out of scope — semantic rules are justified by structural correctness, machine-readability, and maintainability. Examples use plain _HTML_ and _TailwindCSS_ v4 syntax, which reads the same whether the surrounding file is `.tsx`, `.astro`, or anything else that emits markup.

## When to Apply

Reference these guidelines when:

- Choosing the element for a block of markup (sectioning, interactive controls, tabular data)
- Adding colors, fonts, or breakpoints, or reaching for an arbitrary value
- Writing a class attribute: variants, responsive behavior, state-driven styling
- Deciding whether `@apply` or a new `@utility` is the right tool
- Configuring source detection or `prettier-plugin-tailwindcss`
- Sizing media, or bounding a container that can receive long content

## Rule Categories by Priority

| Priority | Category                 | Peak impact | Prefix  |
| :------- | :----------------------- | :---------- | :------ |
| 1        | Semantic Markup          | CRITICAL    | `sem-`  |
| 2        | Styling with TailwindCSS | CRITICAL    | `tw-`   |
| 3        | Performance & Robustness | HIGH        | `perf-` |

Priority orders where to look first; peak impact is the strongest rule in the section, matching the table of contents in `AGENTS.md`. They disagree on purpose — a section can hold one blocking rule and several that only ever produce suggestions.

## Quick Reference

### 1. Semantic Markup (CRITICAL)

- `sem-interactive-elements` - Native `button` / `a` instead of click handlers on `div`; `type` on every form button
- `sem-document-landmarks` - Landmarks belong to the shared layout; heading rank is structure, not size; every page declares its own title and description
- `sem-content-elements` - Lists, tables, `figure`, and `time` for the data they represent

### 2. Styling with TailwindCSS (CRITICAL)

- `tw-theme-tokens` - Design decisions live in `@theme`; the variable-backed semantic layer only where a generator or a theme swap reads it; arbitrary values are review flags
- `tw-state-driven-styling` - Style from `data-*` with variants instead of toggling classes imperatively; an arbitrary variant is a selector hiding in a class attribute
- `tw-variants-and-responsive` - Mobile-first, `group`/`peer`, container queries; dark mode is resolved in the theme, so `dark:` in a component is a signal
- `tw-apply-and-custom-layers` - `@apply` as an escape hatch only; `@utility` for real primitives, registered with a merge helper's `extendTailwindMerge` where one is used
- `tw-class-formatting` - `prettier-plugin-tailwindcss` owns class order; review catches what it cannot

### 3. Performance & Robustness (HIGH)

- `perf-layout-stability` - Intrinsic media sizing, `h-dvh` over `h-screen`, `min-w-0` on flex children
- `perf-css-footprint` - v4 automatic source detection, `@source inline()` over broad safelists

## How to Use

Read individual rule files for detailed explanations and code examples:

```plaintext
rules/*.md
```

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md` (generated — see `README.md`).
