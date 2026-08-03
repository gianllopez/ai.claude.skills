---
title: Render Stability & Memoization
impact: MEDIUM
description: Leaves identity to the React Compiler, and keeps review focused on what it cannot do — analyzable code, store subscriptions, and constants that never belonged in render.
tags: performance, rendering, hooks
---

## Render Stability & Memoization

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
