---
title: Document the System in One Overview With Fixed Sections
impact: HIGH
description: The overview (the body of README.md) is the system's entry document, in Spanish, with the same sections in the same order for every brand; each section states the brand's decisions on its topic and links the component files that apply them
tags: components, documentation, overview, readme
---

## Document the System in One Overview With Fixed Sections

**Impact (HIGH):** The overview is the first document people and agents read and the one the user approves word by word. Without a fixed outline every brand's overview differs, and the sections other rules write into (color, borders, components) may not exist.

**Guidelines:**

1. One overview per system: the body of `README.md`, in Spanish (see `write-spanish-docs`), titled with the legal name and opening with one paragraph on what the system covers
2. Sections in this order: "Identidad", "Logo", "Color", "Tipografía", "Espaciado y radios", "Bordes y estados", "Grilla y movimiento", "Iconografía", "Recursos gráficos", "Fotografía e ilustración", "Gráficos y datos", "Tono de voz", "Componentes", "Uso en código", "Gobierno y versiones"; a section the brand has nothing for is dropped, never renamed or moved
3. Each section states the brand's decisions on its topic with their values, cites the measured contrast of every pair (see `color-measure-contrast`) and links the component files that apply them, without repeating their detail
4. Content other rules require: the identity table in "Identidad" (`scope-brand-intake`); the CMYK value of every printed tone in "Color" (`color-cmyk-print`); every tinted piece in "Bordes y estados" (`surf-tinted-border-200`); the catalog by group, the shared blocks and the documented exceptions in "Componentes" (`comp-catalog`, `name-component-block`); the naming conventions and how to load the system with or without _Tailwind CSS_ in "Uso en código" (`name-bem-english`, `found-tailwind-theme`)
5. The generated tail stays as the platform writes it (see `gov-generated-files`)

**Incorrect (sections improvised per brand, with component detail):**

```md
# Sistema de diseño

## Colores

## Botones

## Tarjeta de presentación

## Otros
```

**Correct (_ASKIT_ reference outline):**

```md
# ASK TECHNOLOGY S.A.S.

Sistema de diseño de la marca _ASKIT_: tokens, componentes, papelería, documentos digitales y plantillas de correo, redes y presentaciones.

## Identidad

## Logo

## Color

…

## Uso en código

## Gobierno y versiones
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
