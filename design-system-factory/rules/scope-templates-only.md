---
title: Hold Templates, Not Personalized Pieces
impact: CRITICAL
description: The system stores templates with sample data; pieces personalized for a person, client or project are derived designs
tags: scope, templates, business card, derived designs
---

## Hold Templates, Not Personalized Pieces

**Impact (CRITICAL):** Storing one business card per employee or one proposal per client turns the system into an archive that goes stale and duplicates the template. The template is the single source; personalized copies live outside.

**Guidelines:**

1. Fill templates with clearly fictitious sample data ("Nombre Apellido", "Comercializadora del Caribe"); personal phone and email use visibly fake values (`+57 (300) 000 0000`, `nombre.apellido@<brand domain>`); company data stays real, from the identity table
2. Say in the component file that personal data is an example and that each personalized piece is a derived design
3. Never add per-person or per-client files to the asset groups

**Incorrect (one print file per employee inside the system):**

```text
assets/print/
├── print__businesscard--ana-gomez.pdf
├── print__businesscard--luis-rojas.pdf
└── print__businesscard--maria-torres.pdf
```

**Correct (one template with sample data):**

```md
- `print__businesscard--85x55.pdf`: `businesscard`, 85 × 55 mm, frente y reverso.
  Los datos son de ejemplo; la tarjeta de cada persona es un diseño derivado de esta plantilla.
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
