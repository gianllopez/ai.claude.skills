---
title: Rule Sections
description: Index of all enforced best practices for React applications, framework-agnostic with React Router as the reference router.
---

## Component Architecture

- **Structure:** [Folder Structure & Layer Boundary](./arch-folder-structure.md)
- **Composition:** [Composition Over Configuration](./arch-composition-patterns.md)
- **Reuse:** [Component Extraction Threshold](./arch-component-extraction.md)
- **Typing:** [Component Typing Conventions](./arch-typing-conventions.md)
- **Depth:** [Minimal Markup Depth](./arch-markup-minimalism.md)
- **Syntax:** [Syntax & Conciseness Conventions](./arch-syntax-conventions.md)

## State & Effects

- **Effects:** [Effect Discipline](./state-effect-discipline.md)
- **Derivation:** [Derived Values Over Stored State](./state-derived-values.md)
- **Ownership:** [State Colocation & Ownership](./state-colocation.md)
- **Identity:** [List Keys & Component Identity](./state-identity-and-keys.md)

## Data Flow

- **Query Layer:** [Query Layer & Data Ownership](./data-query-layer.md)
- **Async States:** [Pending, Empty & Error States](./data-async-states.md)

## Semantic Markup

- **Interaction:** [Correct Interactive Elements](./sem-interactive-elements.md)
- **Outline:** [Document Outline & Sectioning](./sem-document-landmarks.md)
- **Forms:** [Form Markup & Field Association](./sem-form-markup.md)
- **Content:** [Content Elements: Lists, Tables & Media](./sem-content-elements.md)

## Styling with TailwindCSS

- **Tokens:** [Theme Tokens Over Arbitrary Values](./tw-theme-tokens.md)
- **Composition:** [Class Composition & Conditional Classes](./tw-class-composition.md)
- **State:** [State-Driven Styling With Data Attributes](./tw-state-driven-styling.md)
- **Responsive:** [Responsive & Variant Usage](./tw-variants-and-responsive.md)
- **Custom CSS:** [@apply, Custom Utilities & Overrides](./tw-apply-and-custom-layers.md)
- **Formatting:** [Class Attribute Formatting & Order](./tw-class-formatting.md)

## Performance & Robustness

- **Rendering:** [Render Stability & Memoization](./perf-render-stability.md)
- **Layout:** [Layout Stability & Overflow](./perf-layout-stability.md)
- **Build:** [Source Detection & CSS Footprint](./perf-css-footprint.md)
