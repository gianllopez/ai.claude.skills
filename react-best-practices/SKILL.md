---
name: react-best-practices
description: Standards for what React itself adds on top of plain HTML on the web — forms wired through react-hook-form and the shadcn/ui Form components, and the contract with the shadcn/ui generator that keeps a declared view-layer structure from being undone. Use when reviewing, writing, or refactoring forms, or when installing or theming shadcn/ui components. Framework-agnostic semantic HTML, TailwindCSS v4 theming, and layout/CSS-footprint rules live in html-best-practices, and everything independent of the renderer — effects, state, the query layer, component composition and typing — lives in react-core-best-practices. A web project loads all three alongside each other.
license: MIT
metadata:
  author: gianllopez
  version: 2.0.0
---

# React Best Practices

Standards for the part of a _React_ application on the web that is neither plain _HTML_/_CSS_ nor renderer-agnostic _React_: the forms library and Form components a `react-hook-form` project standardizes on, and the generator that writes `shadcn/ui` components into the project.

Framework-agnostic markup and styling — semantic elements, `TailwindCSS` v4 theming, layout stability, CSS footprint — is in `html-best-practices`. Everything that does not change with the renderer — effect and state discipline, the typed query layer, component composition, file structure and typing — is in `react-core-best-practices`. **A web project loads all three.** This skill assumes both are present and never restates them.

Every rule names a defect concrete enough to point at in a diff — a component that keeps its own field state, a patched file inside generated territory — and shows the correct shape beside it. That is what makes the same rule usable in both directions: the **Correct** block is what to write, the defect is what to look for.

**Scope:** the two things that only exist because this is a _React_ project — the forms library's contract, and the component generator's contract. Accessibility auditing is deliberately out of scope. The reference stack is _React Router_ in SPA mode with `react-hook-form` and `shadcn/ui` over _TailwindCSS_ v4.

## When to Apply

Reference these guidelines when:

- Building or reviewing a form, its fields, its validation, and its submission
- Installing or theming a `shadcn/ui` component, or touching `components.json`
- Deciding where a view-layer file lives, or whether something under `core/lib/shadcn/` may be edited

## Rule Categories by Priority

| Priority | Category        | Peak impact | Prefix  |
| :------- | :-------------- | :---------- | :------ |
| 1        | Semantic Markup | HIGH        | `sem-`  |
| 2        | View Structure  | HIGH        | `arch-` |

Priority orders where to look first; peak impact is the strongest rule in the section, matching the table of contents in `AGENTS.md`. They disagree on purpose — a section can hold one blocking rule and several that only ever produce suggestions.

## Quick Reference

### 1. Semantic Markup (HIGH)

- `sem-form-markup` - Every form goes through `react-hook-form` and the Form components; no field state of your own, real submission through `handleSubmit`

### 2. View Structure (HIGH)

- `arch-view-structure` - `components/ui/` is the generator's target; `components.json` is part of the structure, and `core/lib/shadcn/` is read-only

## How to Use

Read individual rule files for detailed explanations and code examples:

```plaintext
rules/*.md
```

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md` (generated — see `README.md`).
