---
title: Ship the Full Logo Variant Set
impact: CRITICAL
description: The logo comes as a primary lockup and a symbol, each in fixed color variants, with text outlined and every derived format (PNG, favicon, app icons, manifest) generated from them
tags: logo, brand, assets, favicon, app icon
---

## Ship the Full Logo Variant Set

**Impact (CRITICAL):** Missing variants push people to recolor or screenshot the logo, which is the most visible brand error.

**Guidelines:**

1. `logo__primary--*` (full logo, default) and `logo__symbol--*` (symbol only: app icon, favicon, avatar, watermark)
2. Modifiers: `--gradient` (light backgrounds, default), `--gradient-negative` (dark backgrounds, primary only), `--flat` (solid brand colors, small sizes and print), `--negative` (all white), `--black` (one-ink print)
3. Text converted to outlines; never retyped with the font
4. Derived files: PNG for email (`--width_480`), symbol PNG for signatures (`--width_112`), SVG favicon = the symbol file, PNG favicon `--width_32`, app icons 180/192/512 light and 512 dark, and a `site.webmanifest`
5. Remove duplicates (one SVG serving as both symbol and favicon is one file)

**Incorrect (one logo file for everything):**

```text
logo.png            # 2000 px, used in email, favicon, print and dark backgrounds
```

**Correct (_ASKIT_ reference set):**

```text
logo__primary--gradient.svg            logo__symbol--gradient.svg   (also the SVG favicon)
logo__primary--gradient-negative.svg   logo__symbol--flat.svg
logo__primary--flat.svg                logo__symbol--negative.svg
logo__primary--negative.svg            logo__symbol--black.svg
logo__primary--black.svg               logo__favicon--gradient--width_32.png
logo__primary--gradient--width_480.png logo__app-icon--light--width_180.png / _192 / _512
logo__symbol--gradient--width_112.png  logo__app-icon--dark--width_512.png
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
