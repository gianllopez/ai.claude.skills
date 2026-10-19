---
title: Document Every Component With the Same Sections
impact: HIGH
description: Each component has a Spanish documentation file (description, classes, measures or composition, Tailwind CSS equivalent when it applies, rules) and a preview
tags: components, documentation, readme, preview
---

## Document Every Component With the Same Sections

**Impact (HIGH):** Irregular component docs hide classes and rules; a fixed shape lets people and agents find the same information in every file.

**Guidelines:**

1. First line after the title: one-sentence purpose
2. **Clases**: every class of the block written in full (no `--error` shorthand), including helper elements and modifiers
3. **Medidas** or **Composición**: sizes, tones and layout; **Tipografía**, **Impresión** and **Archivo de imprenta** for print pieces
4. **Equivalente en _Tailwind CSS_**: for every component in the "Marca" group and the interface groups of `comp-catalog` ("Acciones" to "Retroalimentación"), so projects with _Tailwind CSS_ can build them without `bundle.css`; not for "Comunicación"
5. **Reglas**: short imperative bullets
6. A preview that renders every variant and state, using only bundle classes, sample data in Spanish and a height that keeps open menus, tooltips and modals from being cropped

**Incorrect (incomplete file):**

```md
# badge

Etiqueta. Clases: `badge` + variante (`--error`, `--info`).
```

**Correct (full shape):**

```md
# badge

Etiqueta corta en forma de píldora para estados, categorías o novedades.

**Clases**: `badge`, `badge--success`, `badge--error`, `badge--warning`, `badge--info`; ícono opcional `badge__icon` (16px).

**Medidas**

| Variante                                                          | Uso     | Fondo / texto / borde                                 |
| ----------------------------------------------------------------- | ------- | ----------------------------------------------------- |
| `badge--success`, `badge--error`, `badge--warning`, `badge--info` | estados | `<status>-50` / `<status>-950` / borde `<status>-200` |

**Equivalente en _Tailwind CSS_**: `inline-flex items-center gap-1 rounded-full border px-3 py-1 text-xs font-medium`.

**Reglas**

- Una o dos palabras. No es un botón: no lleva acción.
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
