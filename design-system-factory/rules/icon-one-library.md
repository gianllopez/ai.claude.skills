---
title: Use One Icon Library and Store Only Used Icons
impact: HIGH
description: All icons come from one open library at a pinned version; the system stores only the icons its components use and projects fetch any other icon on demand
tags: icons, library, assets, reicon
---

## Use One Icon Library and Store Only Used Icons

**Impact (HIGH):** Mixed icon sets look inconsistent, and bundling a whole library bloats every project and the system itself.

**Guidelines:**

1. Pick one library with an open license and pin the version (reference: _Reicon_ 1.2.5, `Outline` weight)
2. Store only the icons used by components, as `icon__<kebab-name>--<weight>.svg` (reference: `--outline` and `--filled` in _Reicon_), with a table of where each is used in the icons group file
3. When a component stops using an icon, delete the file and the row (major version)
4. Projects import other icons one by one from the library (`npm i reicon-react@1.2.5`, CDN per icon); they are never added to the system
5. Never draw custom glyphs when the library has one; control marks such as checkbox ticks use the library path too; when the library lacks a glyph, draw it on the library's grid and stroke width, and register it like any other icon, marked as custom in the group file

**Incorrect (custom glyph and unused files):**

```css
.checkbox__control:checked {
  background-image: url("…path d='M5 12.5l4.5 4.5L19 7.5'…");
}
/* assets/icons/ also keeps icon__call--outline.svg, used by nothing */
```

**Correct (library glyph, used files only):**

```md
| Archivo                    | Ícono en _Reicon_ | Dónde se usa                   |
| -------------------------- | ----------------- | ------------------------------ |
| `icon__check--outline.svg` | `Check`           | `stepper`; marca de `checkbox` |
```

Reference: [Reicon icons](https://reicon.dev/icons)
