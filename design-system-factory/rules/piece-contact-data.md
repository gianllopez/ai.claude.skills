---
title: Put the Right Contact Data on Each Piece
impact: HIGH
description: Each piece carries a subset of the identity data chosen with the user, legal documents always keep tax ID and address, every value comes from the identity table, and data order and weights are consistent
tags: print, documents, identity, contact data, legal
---

## Put the Right Contact Data on Each Piece

**Impact (HIGH):** Copying every datum everywhere clutters pieces; dropping legal data from invoices or quotes makes them invalid.

**Guidelines:**

1. Legal documents (`quote`, `invoice`, contracts, email footer of marketing mail): legal name, tax ID and full address always
2. The subset for each non-legal piece is chosen with the user (reference: _ASKIT_ business card and envelope with full address; letter with only phone and email, one per line, linked (`tel:`, `mailto:`); folder with phone, email and website)
3. Order: legal name first in 600 `secondary-950`, then data in 400 `secondary-500` (`secondary-600` where the piece needs more weight)
4. Each piece shows its own subset, but every value comes from the identity table (see `scope-brand-intake`); never retype a value in a piece
5. Personal data (name, role, personal email) appears only as sample data in templates

**Incorrect (legal data dropped from an invoice):**

```html
<p class="letterhead__company">
  <span class="letterhead__legal-name">ASK TECHNOLOGY S.A.S.</span
  ><br />info@askit.com.co
</p>
```

**Correct (_ASKIT_ reference invoice header):**

```html
<p class="letterhead__company">
  <span class="letterhead__legal-name">ASK TECHNOLOGY S.A.S.</span><br />NIT
  901.425.503-6<br />
  Carrera 64 #66-07, Barranquilla, Atlántico, Colombia<br /><a
    href="tel:+573185170879"
    >+57 (318) 517 0879</a
  ><br />
  <a href="mailto:info@askit.com.co">info@askit.com.co</a>
</p>
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
