---
name: react-core-best-practices
description: React standards that hold on any platform — effect and state discipline, derived values, list identity, a typed React Query data layer, component composition, file structure, typing, and merge-aware class composition. Every rule shows its examples in both React DOM and React Native. Use when writing or reviewing React components, hooks, effects, state, queries, stores, or component files, whether the target is the web or Expo. Platform-specific guidance lives elsewhere: react-best-practices for the DOM, semantic HTML, TailwindCSS v4 and shadcn/ui; react-native-with-expo-best-practices for NativeWind and Expo configuration.
license: MIT
metadata:
  author: gianllopez
  version: 1.2.0
---

# React Core Best Practices

Standards for writing and reviewing _React_ itself — the parts that do not change when the renderer does. An effect that should not exist, a second source of truth, an index key on a reorderable list, a component configured by flags: none of these become different defects because the tree renders to `View` instead of `div`.

Every rule names a defect concrete enough to point at in a diff and shows the correct shape beside it. Where the correct shape is written differently on each platform, the rule shows **both** — a web block and a _React Native_ block — so it is never abstract for the reader who has to apply it.

**Scope:** _React_ as a technology. What belongs to a renderer does not live here: semantic _HTML_, _TailwindCSS_ v4 and `shadcn/ui` are in `react-best-practices`; _NativeWind_ and _Expo_ configuration are in `react-native-with-expo-best-practices`. A project loads this skill plus the one for its platform.

## When to Apply

Reference these guidelines when:

- Writing or refactoring a `useEffect`, or deciding where a piece of state belongs
- Loading data for a screen, or handling its pending, empty, and error branches
- Designing a component's props: composition, variants, and typing
- Deciding how a component's own files are organized, or what its barrel exports
- Deciding whether shared state earns a `zustand` store, and which slice a component subscribes to
- Composing class names conditionally, or reaching for a variant API
- Placing a module under `core/`, or naming a file or a component
- Reviewing a diff that touches components, hooks, or the query layer

## Rule Categories by Priority

| Priority | Category                 | Peak impact | Prefix   |
| :------- | :----------------------- | :---------- | :------- |
| 1        | State & Effects          | CRITICAL    | `state-` |
| 2        | Component Architecture   | CRITICAL    | `arch-`  |
| 3        | Data Flow                | HIGH        | `data-`  |
| 4        | Performance & Robustness | MEDIUM      | `perf-`  |

Priority orders where to look first; peak impact is the strongest rule in the section. They disagree on purpose — a section can hold one blocking rule and several that only ever produce suggestions.

## Quick Reference

### 1. State & Effects (CRITICAL)

- `state-effect-discipline` - Effects synchronize with external systems only; never derive, never react to events, never fetch
- `state-derived-values` - Compute in render instead of storing a second source of truth
- `state-colocation` - Push state down; the router owns what must survive a reload; shared state goes to a `zustand` store, never to a context of your own
- `state-identity-and-keys` - Keys come from the data; `key` is the reset mechanism, not an effect

### 2. Component Architecture (CRITICAL)

- `arch-folder-structure` - `core/` owns logic and data, the view composes it; imports flow one direction, and a `core/lib/` module waits for its second consumer
- `arch-components-structure` - One file, a folder with an `index.ts` barrel, or base and presets; names stay singular and never repeat their folder
- `arch-markup-minimalism` - Delete wrappers that only carry classes; spacing comes from the parent, margins flow one way
- `arch-composition-patterns` - Slots and children over a boolean per screen; compound components for structure, render props only for internal state
- `arch-component-extraction` - When repeated markup becomes a component, and how `cva` exposes its variants
- `arch-typing-conventions` - `ComponentProps` over hand-rolled props; unions over impossible boolean combinations
- `arch-typing-system` - `core/types/` for domains, `core/typings/` for library augmentations; `import type` throughout
- `arch-core-utilities` - Functional helpers over static classes; constants centralized instead of scattered as magic strings
- `arch-syntax-conventions` - Short-hand iterators, `handle*` implementations, `function` for components and hand-written hooks, braces on every conditional, ternary over `&&`
- `arch-class-composition` - `cn()` with `tailwind-merge`; never build class names by interpolation
- `arch-member-ordering` - Props ordered by the direction they flow — data, configuration, flags, callbacks — with `children` last and the body read outside-in

### 3. Data Flow (HIGH)

- `data-query-layer` - Typed `react-query-kit` hooks per domain; hierarchical keys declared once; auth in interceptors, not components
- `data-async-states` - Every outcome the query can produce is answered; empty exists only for collections, and the surface decides whether the answer is a branch or a property

### 4. Performance & Robustness (MEDIUM)

- `perf-render-stability` - The compiler owns identity; subscribe to a store slice, hoist constants, justify every hand-written memo

## How to Use

Read individual rule files for detailed explanations and code examples:

```plaintext
rules/*.md
```

Each rule carries a rationale, its guidelines, an _Incorrect_ example, and a _Correct_ example — shown per platform where the platforms differ. See `README.md` for how much of a rule is duplicated and when.

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md` (generated — see `README.md`).
