---
title: Build the Palette on Tailwind CSS Scales
impact: CRITICAL
description: The palette is 50–950 scales with a DEFAULT step (primary, secondary and any additional brand scales, plus Tailwind status and neutral scales) plus white, used as flat tones, and nothing outside them
tags: color, palette, tailwind, tokens
---

## Build the Palette on Tailwind CSS Scales

**Impact (CRITICAL):** Loose hex values multiply with every piece and cannot be translated to utilities. Fixed scales keep every color nameable, auditable and directly usable as a class.

**Guidelines:**

1. Brand scales: `primary`, the main brand color, always; `secondary`, the dark or gray scale for text and dark blocks, always (the brand's own gray when it has one, otherwise a gray the user chooses); `tertiary`, `quaternary`… only for additional brand colors
2. Each brand scale goes from 50 to 950 with a `DEFAULT` equal to the brand value (at `-800` when the gray is chosen)
3. The user provides every step of each brand scale, never generated (see `scope-brand-intake`)
4. Status scales taken from _Tailwind CSS_ unchanged: `success` (`emerald`), `error` (`red`), `warning` (`yellow`), `info` (`sky`), each with `DEFAULT` at `-700`
5. `neutral` (`gray`) for borders on `white`, `DEFAULT` `neutral-200`; plus `white`
6. When a status scale is confusable with a brand color, replace it with the nearest _Tailwind CSS_ scale that is not and record the change (reference: orange brand → warning `yellow`, never `amber` or `orange`); when no clear alternative exists, tell the user
7. Chart colors (`chart-1` … `chart-5`) are aliases of palette tones, never new colors
8. Color is flat: no gradients and no semi-transparent tones (such as `primary-500/10`), except the gradients the brand defines (reference: _ASKIT_, only in the logo files) and the modal backdrop (see `surf-no-shadows`)
9. Base the whole system on _Tailwind CSS_ v4.3 scales and names (text sizes, spacing, radius, breakpoints) and ship a theme file that replaces the default palette

**Incorrect (loose values and a gradient):**

```css
.badge {
  background: #ffe9c7;
  color: #8a4b00;
}
.alert--warning {
  background: #fff4e5;
} /* amber, confusable with the brand */
.post {
  background: linear-gradient(135deg, var(--primary-500), var(--primary-700));
}
```

**Correct (_ASKIT_ reference scales):**

```css
--primary-500: #ffa10b; /* DEFAULT primary */
--secondary-800: #2a2a2a; /* DEFAULT secondary */
--warning-50: oklch(98.7% 0.026 102.212); /* Tailwind yellow-50 */
.badge--brand {
  background: var(--primary-100);
  color: var(--secondary-950);
  border: 1px solid var(--primary-200);
}
```

Reference: [Tailwind CSS colors](https://tailwindcss.com/docs/colors) · [Tailwind CSS theme variables](https://tailwindcss.com/docs/theme)
