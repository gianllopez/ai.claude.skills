---
title: Align Digital Documents With the Print Family
impact: HIGH
description: Letterhead, quote, invoice and report pages reuse the print family decisions and keep legal and fiscal content intact
tags: documents, letterhead, quote, invoice, report
---

## Align Digital Documents With the Print Family

**Impact (HIGH):** Digital documents are what clients keep; if they look different from the stationery, the family breaks where it matters most.

**Guidelines:**

1. The letterhead layout is chosen with the user (reference: _ASKIT_ letterhead without a rule, logo left, data right, one datum per line, slogan at the foot of the first page only); following pages show only logo and page number
2. Quote: number `COT-<year>-<number>` (`COT-2026-014`), date and validity, client, items with quantity, unit and total, subtotal, VAT and total in COP, payment terms, notes
3. Invoice: the graphic representation only; the legal block (CUFE, resolution, numbering range, QR) is filled by the authorized provider and the template never invents it
4. Report pages: header with document title and symbol (≥ 5 mm printed), conclusion titles, figures with sources, callouts for client decisions, footer with legal name 600 and page number
5. Margins 72pt (2.54 cm) on letter and A4, on the 4px grid (4px = 3pt)

**Incorrect (invented fiscal data):**

```html
<div class="document__legal">CUFE: 3fa8b2… Resolución 18760000001 del 2026</div>
```

**Correct (reserved legal block):**

```html
<div class="document__legal">
  <span class="document__qr">QR de la DIAN</span>
  <span
    >Representación gráfica de la factura electrónica. CUFE, resolución de
    facturación, rango de numeración y código QR: datos que entrega el proveedor
    tecnológico autorizado.</span
  >
</div>
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
