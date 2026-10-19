---
title: Start From Verified Brand Data
impact: HIGH
description: Gather the identity, palette, logo, slogan, typeface and form of address from official sources and the user before designing, and never invent missing brand data
tags: scope, intake, identity, legal data
---

## Start From Verified Brand Data

**Impact (HIGH):** Legal names, tax IDs and addresses end up on invoices, contracts and letterheads. One invented or outdated value propagates to every piece and can make documents invalid.

**Guidelines:**

1. Take legal name, tax ID (NIT) and address from the official registration certificate (in _Colombia_, the _Cámara de Comercio_ certificate); confirm with the user the phone, email and website for the pieces, since the certificate records the ones for legal notices; record everything in an Identity table
2. Distinguish the legal name (contracts, invoices, the system name) from the commercial brand (logo, product, communication)
3. Ask for the palette sheet with every 50–950 step of each brand scale and its CMYK values (see `color-tailwind-scales`, `color-cmyk-print`), the brand gray or the choice of one, the original logo vectors, the slogan, the typeface and any heading family (see `found-single-typeface`), and the form of address (see `write-voice`)
4. Advance step by step: finish the intake before proposing any visual piece
5. When a value is missing or contradictory, ask for it; never fill gaps with guesses

**Incorrect (invented data presented as fact):**

```md
| Dato      | Valor         | Problema   |
| --------- | ------------- | ---------- |
| NIT       | 900.123.456-7 | inventado  |
| Domicilio | Barranquilla  | incompleto |
```

**Correct (_ASKIT_ reference: identity from the certificate, contact data confirmed with the user):**

```md
| Dato         | Valor                                                      |
| ------------ | ---------------------------------------------------------- |
| Razón social | _ASK TECHNOLOGY S.A.S._                                    |
| Sigla        | _ASKIT_                                                    |
| NIT          | 901.425.503-6                                              |
| Domicilio    | Carrera 64 #66-07, _Barranquilla_, _Atlántico_, _Colombia_ |
| Teléfono     | +57 (318) 517 0879                                         |
| Correo       | info@askit.com.co                                          |
| Sitio web    | askit.com.co                                               |
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
