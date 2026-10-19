---
title: Deliver Print-Ready PDFs
impact: CRITICAL
description: Every printed piece ships as a PDF at real size with 3 mm bleed, crop marks, CMYK colors, embedded fonts and trim and bleed boxes
tags: print, pdf, bleed, cmyk, production
---

## Deliver Print-Ready PDFs

**Impact (CRITICAL):** A screen PDF sent to a print shop comes back with white edges, shifted colors or substituted fonts.

**Guidelines:**

1. Real size, 3 mm bleed on every edge that has color, crop marks 3 mm off the trim and 6 mm long at 0.25pt, inside a 12 mm slug
2. A slug label with brand, piece, face, size, bleed and color mode
3. Colors converted to CMYK with `color-cmyk-print`; text below 12pt prints in K only (if its tone converts with C, M or Y, use its K value alone and tell the user); fonts embedded as subsets; `TrimBox` and `BleedBox` set on every page
4. Elements that should bleed extend 3 mm past the trim; nothing else touches the edge, and text, logos and data stay at least 5 mm inside the trim
5. One file per piece in the `print` asset group (`print__<piece>--<format>.pdf`), multi-page when the piece has faces
6. Name the format honestly: if the file is not PDF/X, say so and let the print shop convert with its profile

**Incorrect (screen export):**

```text
tarjeta.pdf — RGB, no bleed, no crop marks, fonts not embedded
```

**Correct (_ASKIT_ reference):**

```text
print__businesscard--85x55.pdf — 85 × 55 mm, 2 pages (front, back), 3 mm bleed, crop marks,
CMYK (primary-500 C0 M37 Y96 K0; secondary-800 K84), Lexend embedded, TrimBox and BleedBox
```

Reference: [Bleed (printing)](<https://en.wikipedia.org/wiki/Bleed_(printing)>)
