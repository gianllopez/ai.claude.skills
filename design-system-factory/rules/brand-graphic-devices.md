---
title: Derive Graphic Devices From the Logo, One per Piece
impact: HIGH
description: Brand graphics (pattern, progression, scaled slogan) come from a logo feature, keep that feature's corners, never sit behind text, and only one is used per piece
tags: brand, graphics, pattern, progression, slogan
---

## Derive Graphic Devices From the Logo, One per Piece

**Impact (HIGH):** Stacking devices turns pieces into collages; inventing unrelated shapes weakens the link with the logo.

**Guidelines:**

1. Derive each device from one logo feature and the brand promise (reference: the square dot of the "i" and "Innovación local, impacto global")
2. Pattern (reference): 16px `primary-500` squares every 48px, in corners or bands, on `white` or `secondary-800`
3. Progression (reference): seven `primary-500` squares, each 1.5× the previous, gap 0.7× its own side, bottom-aligned, the last one cut by the edge; unit set by `--progression-unit`
4. Scaled slogan (reference): the slogan set large as the main graphic of the piece, in the form of `brand-slogan-form`; the slogan at text size (footer, signature, card back) is copy, not a device
5. One device per piece; never combined with another device; never on photographs or on `primary-500`; corners from the logo feature (see `found-spacing-radius`; reference: `radius-none`)
6. Never place text over a device; text and device occupy separate areas of the piece
7. Each device gets its own component file (`pattern`, `progression`, `slogan`) even when few pieces use it, because derived designs need its exact construction

**Incorrect (two devices and text on the pattern):**

```html
<section class="post">
  <svg class="post__pattern">…</svg>
  <ol class="progression">
    …
  </ol>
  <h2 class="post__title" style="position:absolute;top:0">sobre el patrón</h2>
</section>
```

**Correct (one device, clear of text):**

```html
<section class="businesscard businesscard--back">
  <p class="businesscard__slogan">Innovación local,<br />impacto global</p>
  <ol class="progression businesscard__progression" aria-hidden="true">
    <li class="progression__step"></li>
    … seven steps …
  </ol>
</section>
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
