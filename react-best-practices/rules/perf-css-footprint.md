---
title: Source Detection & CSS Footprint
impact: MEDIUM
description: Keeps the generated stylesheet correct and small by relying on v4 automatic source detection and declaring dynamic classes explicitly instead of broad safelists.
tags: performance, build, tailwind
---

## Source Detection & CSS Footprint

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
