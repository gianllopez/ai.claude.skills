---
title: Build Components Only From Tokens in One Bundle
impact: HIGH
description: Component CSS lives in one bundle of BEM classes built only from tokens, plus a minimal script for interaction the HTML cannot provide
tags: components, css, tokens, javascript
---

## Build Components Only From Tokens in One Bundle

**Impact (HIGH):** Hard-coded values inside components drift from the tokens; scattered stylesheets make the system impossible to load consistently.

**Guidelines:**

1. `components/bundle.css`: _BEM_ classes, `var(--token)` values only; spacing, radius and text-size tokens carry the _Tailwind CSS_ value as fallback; color tokens have none, because they come only from `tokens.css`
2. Root helper `ds-base` on the container (font, color, box sizing, focus ring)
3. `components/bundle.js` adds behavior only (toggles, tabs, menu keyboard, modal focus and `Esc`, dropzone highlight, toast dismissal, sidebar on mobile); it never draws
4. Load order: `tokens.css`, `bundle.css`, `bundle.js`
5. Every class defined in the bundle is used in a preview or the script, or documented in its component file; anything else is removed (see `gov-final-audit`)

**Incorrect (hard-coded values):**

```css
.toast {
  background: #2b2b2b;
  padding: 15px;
  border-radius: 11px;
}
```

**Correct (tokens with fallbacks):**

```css
.toast {
  background: var(--secondary-800);
  padding: var(--spacing-4, 1rem);
  border-radius: var(--radius-xl, 0.75rem);
  border: 1px solid var(--neutral-950);
}
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
