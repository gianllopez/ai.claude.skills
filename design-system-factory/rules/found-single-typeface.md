---
title: Use One Typeface by Default, in Three Weights
impact: HIGH
description: One open-licensed family by default (a second one for headings only when the brand defines it) covers headings, text and interface, in weights 400, 500 and 600, shipped as local WOFF2 files
tags: typography, fonts, weights, licensing
---

## Use One Typeface by Default, in Three Weights

**Impact (HIGH):** Several families or weights dilute the brand and inflate files; a font loaded only from a third-party CDN breaks offline, in PDFs and in strict environments.

**Guidelines:**

1. Choose one family with an open license (_OFL_) and record its source and license
2. One family by default; a second one only when the brand defines it, for headings, with the same weights and file rules
3. Weights: 400 running text, 500 labels, buttons and navigation, 600 headings; no others
4. Ship local files named in _BEM_ (`fonts/font__<family>--<weight>.woff2`) and embed them in print PDFs
5. Email and other restricted contexts declare a fallback stack (`<Family>, Arial, sans-serif`)

**Incorrect (families the brand does not define and weights outside the scale):**

```css
h1 {
  font-family: 'Montserrat';
  font-weight: 800;
}
body {
  font-family: 'Open Sans';
  font-weight: 300;
}
```

**Correct (_ASKIT_ reference):**

```css
@font-face {
  font-family: 'Lexend';
  font-weight: 600;
  src: url('../fonts/font__lexend--600.woff2') format('woff2');
}
--font-brand: 'Lexend', system-ui, sans-serif;
```

Reference: [Lexend on Google Fonts](https://fonts.google.com/specimen/Lexend)
