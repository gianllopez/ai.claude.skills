---
title: Never Communicate State With Color Alone
impact: HIGH
description: Success, error, warning and information never rely on color alone; they always carry text or a sign, components that announce a state add the status icon, and each step of the status scale has a fixed role
tags: color, status, accessibility, icons
---

## Never Communicate State With Color Alone

**Impact (HIGH):** Color-blind readers and grayscale prints lose color-only meaning. Fixed step roles keep status pieces consistent across components.

**Guidelines:**

1. State is never color alone: it always carries text or a sign; components that announce a state (`alert`, `toast`, field error) also carry the status icon (success `tick-circle`, error `close-circle`, warning `danger`, info `info-circle` in the reference library)
2. Step roles: `-50` background (text on it follows `color-50-950-convention`); `-200` border of that background; `-800` text and icons on `white`; `-700` lower emphasis on `white` and solid fill with `white` text; `-300` to `-600` only for charts and illustration
3. Gain and loss figures use `success-700` and `error-700` and always carry a sign (+/−)

**Incorrect (red text only):**

```html
<p style="color:red">Pago rechazado</p>
```

**Correct (icon, text and scale roles):**

```html
<div class="alert alert--error" role="alert">
  <svg class="alert__icon" aria-hidden="true">…close-circle…</svg>
  <div class="alert__content">
    <p class="alert__title">Pago rechazado</p>
    Revisa los datos de la tarjeta.
  </div>
</div>
```

Reference: [WCAG 2.2 use of color](https://www.w3.org/TR/WCAG22/#use-of-color)
