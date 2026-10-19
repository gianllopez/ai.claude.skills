---
title: Draw Charts With Palette Series and Direct Labels
impact: MEDIUM
description: Charts use up to five palette series in a fixed order, label series directly, start column and bar axes at zero and always cite a source
tags: charts, data visualization, color, labels
---

## Draw Charts With Palette Series and Direct Labels

**Impact (MEDIUM):** Ad-hoc chart colors and legend-only labels make data hard to read and off-brand.

**Guidelines:**

1. Series order (reference): `chart-1` `primary-700`, `chart-2` `secondary-800`, `chart-3` `info-700`, `chart-4` `secondary-500`, `chart-5` `primary-900`; each ≥ 3:1 on `white`
2. For another brand, build the order the same way: brand scales first (`primary`, then `tertiary`…), alternating hue and lightness so neighboring series differ, each ≥ 3:1 on `white`; status scales enter only to complete five series
3. With more than five series, keep the four largest and group the rest as "Otros", drawn as the fifth series (`chart-5`); intensity scales use `primary-100` to `primary-900`
4. Label series on the chart; the legend is only support
5. Axes and grid `secondary-200`; labels `secondary-600` `text-xs`; values 12px 500 `secondary-950`
6. Columns and bars start at zero, square corners; deltas use `success-700`/`error-700` with a sign
7. Title states the conclusion, subtitle the measure and unit, caption the source

**Incorrect (default library colors and no source):**

```text
Title: "Solicitudes por canal" · colors: library defaults · legend only · no source
```

**Correct (_ASKIT_ reference chart):**

```html
<figure class="chart">
  <p class="chart__title">El portal ya atiende más solicitudes que el correo</p>
  <p class="chart__subtitle">Solicitudes por canal y mes, 2026</p>
  <svg class="chart__plot" role="img" aria-label="…">…</svg>
  <figcaption class="chart__caption">Fuente: datos de ejemplo.</figcaption>
</figure>
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
