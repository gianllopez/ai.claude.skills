---
title: Ship a Tailwind CSS Theme That Restricts the Palette
impact: MEDIUM
description: A theme file for Tailwind CSS v4.3 loads the local fonts, replaces the default palette with the system scales and disables shadows
tags: tailwind, theme, code, tokens
---

## Ship a Tailwind CSS Theme That Restricts the Palette

**Impact (MEDIUM):** Projects using utilities otherwise keep `text-red-500` and `shadow-lg` available and drift from the system on day one.

**Guidelines:**

1. `code/tailwind__theme.css` with `@theme { --color-*: initial; … }` and only the system scales, `white` and `chart-1` … `chart-5`
2. Keep text sizes, spacing, radius and breakpoints as _Tailwind CSS_ ships them
3. Set `--font-sans` to the brand family, with `@font-face` pointing at the local files of `found-single-typeface`; a second family, when the brand defines one, as `--font-heading`
4. Reset `--shadow-*`, `--inset-shadow-*`, `--drop-shadow-*` and `--text-shadow-*`
5. With _Tailwind CSS_, projects load only the theme and build each component from the _Tailwind CSS_ equivalent in its component file; they do not load `components/bundle.css`
6. Without _Tailwind CSS_, projects load `tokens.css` and `components/bundle.css`

**Incorrect (default palette left in place):**

```css
@import 'tailwindcss';
/* text-red-500, shadow-lg and bg-amber-400 still exist */
```

**Correct (restricted theme):**

```css
@import 'tailwindcss';
@import './tailwind__theme.css';
/* @theme { --color-*: initial; --color-primary-500: #ffa10b; … --font-sans: "Lexend", system-ui, sans-serif; --shadow-*: initial; } */
```

Reference: [Tailwind CSS theme variables](https://tailwindcss.com/docs/theme)
