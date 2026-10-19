---
title: Print With the Palette Sheet CMYK Values
impact: HIGH
description: Printed pieces use the CMYK values of the company palette sheet and convert every other tone with one documented formula
tags: color, print, cmyk, production
---

## Print With the Palette Sheet CMYK Values

**Impact (HIGH):** Converting with arbitrary profiles makes the printed orange drift from the brand sheet; one formula makes every printed tone reproducible.

**Guidelines:**

1. Copy the brand values from the palette sheet (reference: `primary-500` `C0 M37 Y96 K0`, `secondary-800` `C0 M0 Y0 K84`)
2. If the brand has no palette sheet with CMYK values, ask for it; never invent them (see `scope-brand-intake`)
3. Convert the remaining tones without a color profile: K = 1 − max(R, G, B); C, M and Y computed on the remainder; tones defined in `oklch` (the status scales) are converted to sRGB hex first
4. Check that the formula reproduces the sheet values before using it (`#FFA10B` → `C0 M37 Y96 K0`; `#2A2A2A` → `K84`); if it does not, the brand tones keep the sheet values and the user is told before the other tones are converted
5. Document the CMYK value of every tone used in a printed piece in the color section of the overview

**Incorrect (profile-dependent conversion):**

```text
Export PDF with "Convert to destination: Coated FOGRA39" → the printed orange shifts away from the sheet value
```

**Correct (formula that matches the sheet):**

```python
def rgb_to_cmyk(r, g, b):
    r, g, b = r / 255, g / 255, b / 255
    k = 1 - max(r, g, b)
    if k == 1:
        return 0, 0, 0, 100
    c, m, y = ((1 - x - k) / (1 - k) for x in (r, g, b))
    return tuple(round(v * 100) for v in (c, m, y, k))

rgb_to_cmyk(0xFF, 0xA1, 0x0B)  # (0, 37, 96, 0)
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
