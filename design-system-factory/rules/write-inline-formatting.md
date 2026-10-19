---
title: Italicize Proper Nouns and Write Values as Code
impact: MEDIUM
description: In documentation, proper nouns go in italics; tones, hexadecimal and CMYK values, classes, tokens and file names go as inline code; measures, units and contrast ratios stay plain text
tags: writing, markdown, italics, proper nouns, color, tokens
---

## Italicize Proper Nouns and Write Values as Code

**Impact (MEDIUM):** Values written as plain text get misread, auto-corrected or mistaken for prose, and unmarked names blend into ordinary Spanish words. Inline code for values and italics for names make every term unambiguous and keep a single visual convention across dozens of files.

**Guidelines:**

1. Italicize proper nouns: companies, brands, products, typefaces, places and methodologies (reference: _ASKIT_, _ASK TECHNOLOGY S.A.S._, _Lexend_, _Tailwind CSS_, _Reicon_, _BEM_, _DIAN_, _Barranquilla_, _Outlook_, _LinkedIn_)
2. Do not italicize names inside headings, code, link text or generated sections, nor in the visible text of brand pieces (cards, documents, slides, emails)
3. Write as inline code every tone (`primary-500`, `<status>-200`), hexadecimal value (`#FFA10B`, uppercase in documentation as on the palette sheet and lowercase in code), CMYK value (`C0 M37 Y96 K0`, `K84`), class or token (`button--primary`, `spacing-6`, `text-sm font-medium`) and file name (`logo__symbol--gradient.svg`); never as italics or plain text, not even in the changelog
4. Measures, units and contrast ratios stay plain text (16px, 3 mm, 4.5:1)

**Incorrect (plain names and values):**

```md
La validez legal la dan el proveedor tecnológico y la DIAN; la tipografía es Lexend.
Fondo primary 500 (#FFA10B, C0 M37 Y96 K0) con texto secondary-950.
```

**Correct (italic names, values as inline code):**

```md
La validez legal la dan el proveedor tecnológico y la _DIAN_; la tipografía es _Lexend_.
Fondo `primary-500` (`#FFA10B`, `C0 M37 Y96 K0`) con texto `secondary-950`.
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
