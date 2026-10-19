---
title: Mark Die-Cut and Reference Zones Without Printing Them
impact: MEDIUM
description: Die-cut slots, safe zones and reference areas are shown in previews as dashed neutral-400 marks and are excluded from print files
tags: print, die cut, folder, reference zones
---

## Mark Die-Cut and Reference Zones Without Printing Them

**Impact (MEDIUM):** Reference marks printed by mistake ruin a run; missing marks make the die-cut position a guess.

**Guidelines:**

1. Dashed 1px `neutral-400` for slots and reference zones, documented as not printed
2. Exclude them from the print pipeline with `@media print { display: none; }`; the print shop defines the die (pocket shape, slots, spine)
3. Place slots on the piece grid and document the position in mm (reference: 85 × 55 mm card slot centered on the pocket height, 18 mm from the right edge); slots and reference zones keep the real measures of the die in `mm` (see `print-real-size`)
4. Know which side of the sheet each face prints on (the folder pocket face prints with the outside, so a blank inside keeps the job one-sided, 4/0: four colors on one side and none on the other)
5. Pieces printed on office printers or already assembled (letter, envelope) keep everything off the edge

**Incorrect (printed reference mark):**

```html
<div class="folder__pocket">… <span class="folder__slot"></span></div>
<!-- included in the PDF -->
```

**Correct (reference only):**

```css
.folder__slot {
  position: absolute;
  right: 18mm;
  top: 50%;
  transform: translateY(-50%);
  width: 85mm;
  height: 55mm;
  border: 1px dashed var(--neutral-400);
}
@media print {
  .folder__slot {
    display: none;
  }
}
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
