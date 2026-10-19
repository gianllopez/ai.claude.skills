---
title: Generate Print Files Reproducibly
impact: MEDIUM
description: Print PDFs are generated from the component previews by a scripted pipeline (HTML at real size, headless browser PDF, CMYK conversion, page boxes) and verified visually
tags: print, pipeline, pdf, automation, verification
---

## Generate Print Files Reproducibly

**Impact (MEDIUM):** Hand-exported files drift from the components; a pipeline regenerates every piece identically after each change.

**Guidelines:**

1. Build one HTML page per face from the component preview, at real size (see `print-real-size`), with bleed rectangles and crop marks
2. Render with a headless browser (_Playwright_ + _Chromium_) using `preferCSSPageSize` and `printBackground`, fonts loaded from absolute local paths
3. Convert colors with a PDF library that rewrites operators (for example _pikepdf_), handling shadings inside patterns; avoid tools that rasterize gradients
4. Set `TrimBox` and `BleedBox`, merge faces, then rasterize each page and inspect it before publishing: reference marks absent, text 5 mm inside the trim and text below 12pt in K only (see `print-pdf-spec`, `print-dielines`)
5. Check that fonts are embedded (no Type 3 fallback) and compare file sizes with the previous version; a much larger file usually means a rasterized gradient

**Incorrect (manual export):**

```text
Open preview → Print → Save as PDF → send to the print shop
```

**Correct (scripted and verified):**

```text
build one HTML page per face from the preview, at real size, with absolute font paths
render each page to PDF with Chromium
convert to CMYK, set TrimBox and BleedBox, merge the faces
pdffonts print__folder--229x305.pdf                   # fonts embedded
pdftoppm -r 40 -png print__folder--229x305.pdf check  # visual check
```

Reference: [Playwright page.pdf](https://playwright.dev/docs/api/class-page#page-pdf) · [pikepdf](https://pikepdf.readthedocs.io/)
