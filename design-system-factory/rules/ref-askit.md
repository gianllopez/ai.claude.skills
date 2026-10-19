---
title: Use ASKIT as the Resolved Reference
impact: MEDIUM
description: The ASK TECHNOLOGY S.A.S. (ASKIT) system is the worked example of every rule; reuse its structure for new brands and its values only for ASKIT
tags: reference, askit, example, values
---

## Use ASKIT as the Resolved Reference

**Impact (MEDIUM):** A worked example shortens every decision for a new brand, but copying its values into another brand produces a clone instead of a system.

**Guidelines:**

1. Identity: legal name _ASK TECHNOLOGY S.A.S._, brand _ASKIT_, NIT 901.425.503-6, Carrera 64 #66-07, _Barranquilla_, _Atlántico_; info@askit.com.co; +57 (318) 517 0879; askit.com.co
2. Brand: slogan "Innovación local, impacto global"; logo with the symbol as the "A" and a square orange dot on the "i"; symbol gradient `primary-600` → `primary-500`
3. Color: `primary` orange, `primary-500` `#FFA10B` (`C0 M37 Y96 K0`); `secondary` gray, `secondary-800` `#2A2A2A` (`K84`); status scales from _Tailwind CSS_ (warning `yellow`)
4. Type: _Lexend_ 400/500/600; icons: _Reicon_ 1.2.5, `Outline` weight, only the icons the components use; base: _Tailwind CSS_ v4.3; one light theme; no shadows
5. Chosen pieces: business card with the progression on a `secondary-800` back; envelope and letter with the scaled slogan (letter data above it, phone and email only); folder with the large slogan on the cover and square bullets on the pocket; digital documents with data in the letterhead, no rule, slogan at the foot
6. For another brand (for example one using _Manrope_), keep the method, the scales and the rules; replace identity, palette values, typeface, logo, slogan and devices after intake

**Incorrect (copying _ASKIT_ values into another brand):**

```css
/* Another brand */
--primary-500: #ffa10b; /* ASKIT orange */
--font-brand: 'Lexend'; /* ASKIT typeface */
```

**Correct (same structure, own values):**

```css
/* Another brand: values from its own intake */
--primary-500: <its palette sheet value>;
--font-brand: 'Manrope', system-ui, sans-serif;
/* same scales, roles, borders, naming and governance as ASKIT */
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
