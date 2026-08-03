---
title: Class Attribute Formatting & Order
impact: MEDIUM
description: Delegates class ordering to prettier-plugin-tailwindcss and keeps long class attributes readable rather than hand-sorted.
tags: tailwind, tooling, formatting
---

## Class Attribute Formatting & Order

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
