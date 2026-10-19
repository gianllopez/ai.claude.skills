---
title: Cover the Standard Component Catalog
impact: HIGH
description: A brand design system ships a fixed set of component groups, from brand rules to communication pieces, so any derived design finds its building blocks
tags: components, catalog, groups, coverage
---

## Cover the Standard Component Catalog

**Impact (HIGH):** A system with only buttons and forms leaves letters, invoices, signatures and social posts to improvisation, which is where brands usually break.

**Guidelines:**

1. "Marca": `logo` (usage rules) plus one component per graphic device of the brand (reference: `pattern`, `progression`, `slogan` in _ASKIT_)
2. "Acciones": `button`
3. "Formularios": `field`, `select`, `checkbox` (with radio), `toggle`, `date`, `dropzone`, `search`
4. "Contenido": `badge`, `alert`, `card`, `accordion`
5. "Datos": `table`, `chart`, `avatar`
6. "Navegación": `tabs`, `navbar`, `sidebar`, `footer`, `pagination`, `breadcrumb`, `stepper`
7. "Superposiciones": `modal`, `menu`, `tooltip`, `toast`
8. "Retroalimentación": `loader`, `empty`
9. "Comunicación": `titleslide`, `slide`, `letterhead`, `report`, `quote` and `invoice` (sharing the `document` block), `signature`, `newsletter`, `post`, `banner`, `businesscard`, `letter`, `envelope`, `folder`
10. Add or drop components only when the brand needs it, and keep the catalog list in the overview in sync

**Incorrect (interface-only catalog):**

```text
components/ button  field  card  modal
```

**Correct (_ASKIT_ reference catalog by group):**

```md
- **Marca**: `logo`, `pattern`, `progression`, `slogan`.
- **Comunicación**: `titleslide` y `slide`, `letterhead`, `report`, `quote` e `invoice`, `signature` y `newsletter`, `post` y `banner`, `businesscard`, `letter`, `envelope` y `folder`.
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
