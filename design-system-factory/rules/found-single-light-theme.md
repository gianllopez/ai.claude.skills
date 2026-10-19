---
title: Ship One Light Theme by Default
impact: HIGH
description: The system has a single light theme by default, with dark surfaces only as contrast blocks inside it; a dark theme is added only when the user asks for it
tags: theme, color, dark mode
---

## Ship One Light Theme by Default

**Impact (HIGH):** Maintaining a dark theme doubles every color decision and every print and document piece, for little brand value.

**Guidelines:**

1. One light theme by default for web, apps and documents (reference: _ASKIT_ has no dark mode)
2. A dark theme only when the user asks for it for the brand, with its own measured contrast pairs and every component checked in both themes
3. Dark tones (`secondary-800` to `secondary-950`) as backgrounds only for bands, footers, covers, card backs and similar contrast blocks; as text and icons they follow `color-text-on-light`
4. Every component is designed and checked on the light theme
5. While the system has only the light theme, declare `color-scheme: light` (CSS and `<meta name="color-scheme" content="light">`) so browsers do not darken the pages; check email pieces in the dark mode of _Gmail_ and _Outlook_, which may invert them anyway

**Incorrect (a dark theme switch the user did not ask for):**

```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0a0a0a;
    --text: #fafafa;
  }
}
```

**Correct (a dark block inside the light theme):**

```css
.footer {
  background: var(--secondary-800);
  color: var(--white);
}
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
