---
title: Set the Slogan in Its Fixed Form
impact: HIGH
description: The slogan keeps its exact wording, composed in two sizes at a 2–2.5 ratio and closed by a square brand-color dot where it works as a graphic, and as plain text with no period everywhere else
tags: brand, slogan, typography
---

## Set the Slogan in Its Fixed Form

**Impact (HIGH):** Slogans rewritten per piece ("Innovación local e impacto global.") stop being a brand asset.

**Guidelines:**

1. Composed form: split the slogan at its natural pause into a lead line, small in `secondary-600`, and a main line, 2–2.5× larger in 600 `secondary-950` (reference: "Innovación local," / "impacto global"); a slogan with no natural pause is set as a single main line
2. In the composed form, a `primary-500` square of 0.2em replaces the final period
3. Plain-text form: the size of the surrounding text, on one line or broken at the natural pause, with no period and no square (footer, email signature, business card back, the system's `Cover`)
4. Use the composed form when the slogan stands as a graphic element of the piece (the scaled slogan of `brand-graphic-devices`, stationery footers) and the plain-text form everywhere else
5. Sizes through `--slogan-lead` and `--slogan-main`; on `secondary-800` use `slogan--negative` (`secondary-200` and `white`)
6. Left aligned; in print the lead line never goes below 9pt (12px, on the 4px scale)

**Incorrect (rewritten slogan with a period):**

```html
<p class="footer__slogan">Innovación local, impacto global.</p>
<p style="font-size:18px">Innovación local e impacto global</p>
```

**Correct (fixed form):**

```html
<p class="slogan letter__slogan">
  <span class="slogan__lead">Innovación local,</span>
  <span class="slogan__main"
    >impacto global<span class="slogan__dot"></span
  ></span>
</p>
<p class="footer__slogan">Innovación local, impacto global</p>
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
