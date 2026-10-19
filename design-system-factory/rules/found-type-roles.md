---
title: Map Text to Named Roles
impact: HIGH
description: Text uses a fixed set of roles (display to h5, lead, body, body-sm, label, caption, overline) on the Tailwind CSS size scale, with headings stepping down on mobile
tags: typography, scale, roles, responsive
---

## Map Text to Named Roles

**Impact (HIGH):** Arbitrary font sizes per piece break hierarchy across documents and screens. Named roles make every size intentional and translatable.

**Guidelines:**

1. Roles: `display` `text-6xl`, `h1` `text-5xl`, `h2` `text-4xl`, `h3` `text-3xl`, `h4` `text-2xl`, `h5` `text-xl` (all 600), `lead` `text-lg`, `body` `text-base`, `body-sm` `text-sm`, `label` `text-sm font-medium`, `caption` `text-xs`, `overline` `text-xs font-medium tracking-widest uppercase`
2. On screen, the 4px grid applies to line heights, which are all multiples of 4 in the _Tailwind CSS_ scale; font sizes keep the _Tailwind CSS_ values (including `text-sm` 14px, `text-lg` 18px and `text-3xl` 30px)
3. Below `md`, `display` to `h3` drop two steps; `h4` and `h5` stay
4. Print uses points on the 4px grid (4px = 3pt, so multiples of 3): 12pt body and tables, 9pt notes, footers and senders
5. No sizes outside the scale

**Incorrect (ad-hoc sizes):**

```css
.hero-title {
  font-size: 53px;
  font-weight: 700;
}
```

**Correct (role classes):**

```html
<h1 class="h1">Automatización de la facturación</h1>
<p class="overline">Propuesta comercial</p>
```

Reference: [Tailwind CSS font size](https://tailwindcss.com/docs/font-size)
