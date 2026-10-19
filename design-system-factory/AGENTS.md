# Design System Factory

**Version 1.0.0**  
_Gian López_  
_October 2026_

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring brand design systems (tokens, components, print and digital pieces). Humans  
> may also find it useful, but guidance here is optimized for automation  
> and consistency by AI-assisted workflows.

---

## Abstract

Standard for creating, extending and auditing a company's brand design system: process, naming, color, surfaces, brand assets, print production, foundations, writing, iconography, components, communication pieces and governance. It describes how every piece derived from a brand must look and be documented, not a specific website, app or presentation, and uses the _ASK TECHNOLOGY S.A.S._ (_ASKIT_) system as the worked reference.

---

## Table of Contents

1. [Scope and Process](#1-scope-and-process) — `CRITICAL`
   - [1.1 Describe Brand Pieces, Not a Product](#11-describe-brand-pieces-not-a-product)
   - [1.2 Hold Templates, Not Personalized Pieces](#12-hold-templates-not-personalized-pieces)
   - [1.3 Start From Verified Brand Data](#13-start-from-verified-brand-data)
   - [1.4 Propose Rendered Alternatives Before Building](#14-propose-rendered-alternatives-before-building)
   - [1.5 Apply Explicit Choices, Flag Conflicts](#15-apply-explicit-choices-flag-conflicts)
   - [1.6 Report What to Review After Every Change](#16-report-what-to-review-after-every-change)
   - [1.7 Answer Briefly, in Prose](#17-answer-briefly-in-prose)
2. [Naming](#2-naming) — `CRITICAL`
   - [2.1 Name Everything in English With BEM](#21-name-everything-in-english-with-bem)
   - [2.2 Name Asset Files as block\_\_element--modifier](#22-name-asset-files-as-blockelement--modifier)
   - [2.3 One Component, One Block Name](#23-one-component-one-block-name)
   - [2.4 Never Use a Modifier Without Its Base](#24-never-use-a-modifier-without-its-base)
3. [Color](#3-color) — `CRITICAL`
   - [3.1 Build the Palette on Tailwind CSS Scales](#31-build-the-palette-on-tailwind-css-scales)
   - [3.2 Text on White Is secondary-950](#32-text-on-white-is-secondary-950)
   - [3.3 Pair -50 Backgrounds With -950 Text](#33-pair--50-backgrounds-with--950-text)
   - [3.4 Use the Brand Color as Fill, Not as Text on Light](#34-use-the-brand-color-as-fill-not-as-text-on-light)
   - [3.5 Never Communicate State With Color Alone](#35-never-communicate-state-with-color-alone)
   - [3.6 Measure Contrast Before Choosing a Pair](#36-measure-contrast-before-choosing-a-pair)
   - [3.7 Print With the Palette Sheet CMYK Values](#37-print-with-the-palette-sheet-cmyk-values)
4. [Surfaces and States](#4-surfaces-and-states) — `CRITICAL`
   - [4.1 Separate Surfaces With Borders, Never Shadows](#41-separate-surfaces-with-borders-never-shadows)
   - [4.2 Border Tinted Pieces With Their Own Scale at 200](#42-border-tinted-pieces-with-their-own-scale-at-200)
   - [4.3 Use the Neutral Scale for Borders on White and for Controls](#43-use-the-neutral-scale-for-borders-on-white-and-for-controls)
   - [4.4 Define One Focus Ring and Fixed Hover and Disabled States](#44-define-one-focus-ring-and-fixed-hover-and-disabled-states)
5. [Brand Assets](#5-brand-assets) — `CRITICAL`
   - [5.1 Ship the Full Logo Variant Set](#51-ship-the-full-logo-variant-set)
   - [5.2 Respect Logo Minimum Sizes, Clear Space and Misuse Rules](#52-respect-logo-minimum-sizes-clear-space-and-misuse-rules)
   - [5.3 Derive Graphic Devices From the Logo, One per Piece](#53-derive-graphic-devices-from-the-logo-one-per-piece)
   - [5.4 Set the Slogan in Its Fixed Form](#54-set-the-slogan-in-its-fixed-form)
   - [5.5 Choose Licensed Imagery With Written Criteria](#55-choose-licensed-imagery-with-written-criteria)
6. [Print Production](#6-print-production) — `CRITICAL`
   - [6.1 Deliver Print-Ready PDFs](#61-deliver-print-ready-pdfs)
   - [6.2 Keep Printed Text and Logos Above Their Minimums](#62-keep-printed-text-and-logos-above-their-minimums)
   - [6.3 Compose Print Pieces at Real Size](#63-compose-print-pieces-at-real-size)
   - [6.4 Generate Print Files Reproducibly](#64-generate-print-files-reproducibly)
   - [6.5 Mark Die-Cut and Reference Zones Without Printing Them](#65-mark-die-cut-and-reference-zones-without-printing-them)
7. [Foundations](#7-foundations) — `HIGH`
   - [7.1 Use One Typeface by Default, in Three Weights](#71-use-one-typeface-by-default-in-three-weights)
   - [7.2 Map Text to Named Roles](#72-map-text-to-named-roles)
   - [7.3 Ship One Light Theme by Default](#73-ship-one-light-theme-by-default)
   - [7.4 Use the Spacing and Radius Scales With Fixed Assignments](#74-use-the-spacing-and-radius-scales-with-fixed-assignments)
   - [7.5 Use Standard Breakpoints, Grid and Motion](#75-use-standard-breakpoints-grid-and-motion)
   - [7.6 Ship a Tailwind CSS Theme That Restricts the Palette](#76-ship-a-tailwind-css-theme-that-restricts-the-palette)
8. [Writing and Voice](#8-writing-and-voice) — `HIGH`
   - [8.1 Document in Spanish, Name in English](#81-document-in-spanish-name-in-english)
   - [8.2 Use One Warm, Neutral Voice](#82-use-one-warm-neutral-voice)
   - [8.3 Italicize Proper Nouns and Write Values as Code](#83-italicize-proper-nouns-and-write-values-as-code)
   - [8.4 Titles State the Conclusion](#84-titles-state-the-conclusion)
9. [Iconography](#9-iconography) — `HIGH`
   - [9.1 Use One Icon Library and Store Only Used Icons](#91-use-one-icon-library-and-store-only-used-icons)
   - [9.2 Size and Color Icons With the Text They Accompany](#92-size-and-color-icons-with-the-text-they-accompany)
10. [Components](#10-components) — `HIGH`
    - [10.1 Cover the Standard Component Catalog](#101-cover-the-standard-component-catalog)
    - [10.2 Document Every Component With the Same Sections](#102-document-every-component-with-the-same-sections)
    - [10.3 Document the System in One Overview With Fixed Sections](#103-document-the-system-in-one-overview-with-fixed-sections)
    - [10.4 Build Components Only From Tokens in One Bundle](#104-build-components-only-from-tokens-in-one-bundle)
    - [10.5 Build Accessible Semantics Into Every Component](#105-build-accessible-semantics-into-every-component)
    - [10.6 Draw Charts With Palette Series and Direct Labels](#106-draw-charts-with-palette-series-and-direct-labels)
11. [Communication Pieces](#11-communication-pieces) — `HIGH`
    - [11.1 Design the Stationery as One Family](#111-design-the-stationery-as-one-family)
    - [11.2 Put the Right Contact Data on Each Piece](#112-put-the-right-contact-data-on-each-piece)
    - [11.3 Align Digital Documents With the Print Family](#113-align-digital-documents-with-the-print-family)
    - [11.4 Build Email Pieces for Email Clients](#114-build-email-pieces-for-email-clients)
    - [11.5 Keep Social and Slide Templates on the Brand Grid](#115-keep-social-and-slide-templates-on-the-brand-grid)
12. [Governance](#12-governance) — `HIGH`
    - [12.1 Version Every Change and Record It in the Changelog](#121-version-every-change-and-record-it-in-the-changelog)
    - [12.2 Register Every Asset and Leave No Orphans](#122-register-every-asset-and-leave-no-orphans)
    - [12.3 Run a Final Audit Before Closing the System](#123-run-a-final-audit-before-closing-the-system)
    - [12.4 Regenerate Generated Files Before Every Publish](#124-regenerate-generated-files-before-every-publish)
13. [Reference Implementation](#13-reference-implementation) — `MEDIUM`
    - [13.1 Use ASKIT as the Resolved Reference](#131-use-askit-as-the-resolved-reference)

---

## 1. Scope and Process

### 1.1 Describe Brand Pieces, Not a Product

**Impact (CRITICAL):** When the system turns into a website, an app or a presentation, its rules start serving one product and stop being reusable. Every later project then inherits product decisions as if they were brand rules.

**Guidelines:**

1. Write every rule, token and component as a brand-level guideline that any derived piece can apply (web, app, print, email, social, documents)
2. Keep product pages, app screens and real presentations out of the system; they are derived designs built from it
3. Components show how a pattern looks with the brand (a `navbar`, a `slide`), not a finished screen of a specific product
4. A component enters the system only when any derived design could use it without product content (a `hero` yes; a pricing table with the brand's plans no); otherwise offer to build it as a derived design, outside the system

**Incorrect (the system ships a finished landing page):**

```text
components/
├── home/                 # full marketing site for askit.com.co
└── pricing/              # ASKIT plans and prices
```

**Correct (the system ships brand-level patterns; the site is a derived design):**

```text
components/
├── navbar/               # how a top bar looks with the brand
├── footer/
└── card/
# askit.com.co is built in its own project from these components
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 1.2 Hold Templates, Not Personalized Pieces

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

### 1.3 Start From Verified Brand Data

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

### 1.4 Propose Rendered Alternatives Before Building

**Impact (HIGH):** Brand pieces are judged by eye. Building one design directly forces rework when it misses; a sheet of options lets the user decide in one pass and leaves a record of why.

**Guidelines:**

1. Applies to communication pieces and graphic devices; interface components follow the rules directly
2. Render three or four alternatives that differ in concept, not only in color or size, at real proportions and with real brand assets
3. Aim for designs innovative enough to stand out without exaggeration; when the user rejects a round, the next round must be genuinely different
4. Label each option with a letter and a short name (A · Pie como la hoja carta) and state its trade-off in one line
5. Deliver the sheets as images or PDFs the user can open on the phone, and notify when they are ready
6. Implement only the chosen option, apply the user's follow-up adjustments literally, and record the decision in the changelog entry of the version that implements it, with the letter, the name and the adjustments (see `gov-versioning`)

**Incorrect (a single design built straight into the system):**

```text
User: "Necesito la carpeta."
Agent: builds folder v1 into bundle.css, regenerates the PDF and publishes it
```

**Correct (options first, implementation after the choice):**

```text
User: "Necesito la carpeta."
Agent: sends sheet__folder.png with A · Progresión, B · Eslogan a escala, C · Patrón de cuadrados
User: "Vamos con la B."
Agent: implements B, publishes, records "folder: B · Eslogan a escala (eslogan grande en la portada)" in the changelog
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 1.5 Apply Explicit Choices, Flag Conflicts

**Impact (HIGH):** The user owns the brand decisions, yet a silent violation (low contrast, a rule broken in one piece) erodes the system. Flagging the conflict with concrete numbers keeps both the authority and the consistency.

**Guidelines:**

1. Apply what the user explicitly chose, in the user's words, without reinterpreting it
2. If the choice breaks a rule or a contrast threshold, say which rule and give the measured value (1.94:1 versus the 3:1 required)
3. Offer the conflicting option plus compliant alternatives as a multiple-choice question, recommended option first; legal requirements (tax ID, address and fiscal block on legal documents; see `piece-contact-data`, `piece-digital-documents`) are not offered as an option: explain why and keep them
4. When the user confirms a rule exception, document it as an exception in the affected component file
5. When the request is ambiguous and a wrong guess is cheap to redo, implement the most reasonable reading and say which reading was taken

**Incorrect (silently applying a low-contrast request):**

```text
User: "Íconos en tono 50 sobre el cuadro naranja."
Agent: applies secondary-50 on primary-500 (1.94:1) and publishes
```

**Correct (flagging with numbers and options):**

```text
Agent: "secondary-50 sobre primary-500 da 1.94:1; la regla de íconos pide 3:1."
Options: 1 · Sin cuadro, secondary-50 sobre secondary-800 (13.8:1) (Recommended)
         2 · Ícono secondary-950 (9.8:1) · 3 · Lo que pediste (1.94:1)
```

Reference: [WCAG 2.2 non-text contrast](https://www.w3.org/TR/WCAG22/#non-text-contrast)

### 1.6 Report What to Review After Every Change

**Impact (MEDIUM):** The overview is long and the user approves its wording. Without a precise list of touched sections, edits slip through unreviewed and the documentation drifts from what the user approved.

**Guidelines:**

1. Close every change with the new version number and one sentence per change
2. List the overview sections to review word by word by their heading, quoting the changed phrase when it is short
3. List the files outside the overview that changed (component files, asset group files, changelog), and the previews and print files that changed, to check by eye
4. When nothing in the overview changed, say so explicitly
5. For a major version, repeat what breaks and what derived designs must update (for example, rename `folder__icon` to `folder__bullet`)

**Incorrect (a vague closing):**

```text
Listo, actualicé la carpeta y la documentación.
```

**Correct (a precise review list):**

```md
Publiqué la versión 8.0.1: la ranura de la tarjeta queda centrada en la altura del bolsillo.
Vista general: no cambia ninguna sección.
Fuera de la vista general: la línea "Ranura de la tarjeta" en la ficha de `folder` y la entrada 8.0.1 del registro de cambios.
Para revisar a ojo: la vista previa de `folder` y `print__folder--229x305.pdf`.
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 1.7 Answer Briefly, in Prose

**Impact (MEDIUM):** The user reviews many changes in a row. Long enumerations and padding hide the one decision they need to make.

**Guidelines:**

1. Answer in Spanish (see `write-spanish-docs`) with the information needed and nothing else: no greetings, apologies or offers of further help
2. Prefer continuous prose; use a list only when the content is genuinely a set of parallel items
3. For direct questions ("¿Qué falta?", "¿Vale la pena…?"), repeat the question as a `###` subtitle and answer in the paragraph below
4. State facts only when they are verifiable; when they are not, say "Datos insuficientes para verificar"

**Incorrect (padded list answer):**

```md
¡Claro! Aquí tienes lo que falta:

1. Primero, ...
2. Además, ...

¿Quieres que te ayude con algo más?
```

**Correct (subtitle plus short prose):**

```md
### ¿Ese componente se usa en algún lado?

Sí, en una sola pieza: el reverso de `businesscard`, con la clase `businesscard__progression`.
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

---

## 2. Naming

### 2.1 Name Everything in English With BEM

**Impact (CRITICAL):** Mixed languages and ad-hoc names make the system impossible to search, extend or consume from code. One methodology in one language keeps every name predictable.

**Guidelines:**

1. Classes, files and folders use `block__element--modifier`, lowercase, no accents or spaces, single hyphens between words of the same part; measured values in file names use `key_value` (see `name-files-bem`)
2. Custom properties (`--slogan-lead`), ids (`modal-1-title`) and data attributes use lowercase kebab-case in English
3. Never use Spanish words or abbreviations as names (`titulo`, `p5`, `s8`), except the _Tailwind CSS_ scale names (`xs`, `sm`, `lg`, `2xl`…) and the `ds-` helper prefix
4. Keep platform-imposed names as documented exceptions (for example a `Cover` folder required by the artifact type)

**Incorrect (Spanish and cryptic names):**

```css
.tarjeta-titulo {
}
.p5 {
  fill: var(--primary-500);
}
--slogan-principal: 24px;
```

**Correct (_BEM_ in English):**

```css
.card__title {
}
.cover__primary {
  fill: var(--primary-500);
}
--slogan-main: 24px;
```

Reference: [BEM naming](https://getbem.com/naming/)

### 2.2 Name Asset Files as block\_\_element--modifier

**Impact (CRITICAL):** Assets are referenced from code, docs, manifests and print shops. A consistent pattern lets anyone predict the file name for a variant without opening a folder.

**Guidelines:**

1. Block = family (`logo`, `icon`, `pattern`, `print`, `image`, `font`)
2. Element = concrete piece (`primary`, `symbol`, `businesscard`, `lexend`)
3. Modifier = version (`gradient`, `flat`, `negative`, `outline`, `400`); a measured value uses `key_value` (`--width_512`); several modifiers go version first, then measured values (`--gradient--width_112`)
4. Print files encode the format, as its standard name (`dl`, `letter`) or width × height in mm (`85x55`, `229x305`): `print__businesscard--85x55.pdf`, `print__envelope--dl.pdf`
5. Icons keep the library name in kebab-case: `icon__chevron-down--outline.svg`

**Incorrect (free-form names):**

```text
Logo Final (2).svg
favicon32.png
tarjeta presentacion.pdf
```

**Correct (_ASKIT_ reference):**

```text
logo__primary--gradient.svg
logo__symbol--gradient--width_112.png
font__lexend--600.woff2
print__folder--229x305.pdf
```

Reference: [BEM naming](https://getbem.com/naming/)

### 2.3 One Component, One Block Name

**Impact (HIGH):** When the folder says `logo` but the classes say `logo-usage`, people cannot find the CSS from the docs or the docs from the CSS.

**Guidelines:**

1. Folder `components/<block>/`, root class `.<block>`, documentation title `# <block>`, except the platform's `Cover` folder (see `name-bem-english`)
2. One word, no hyphens, in English (`businesscard`, `titleslide`, `letterhead`), because the artifact type requires component folders to be _JavaScript_ identifiers
3. Shared blocks are allowed only when documented in the overview (for example `quote` and `invoice` sharing `document`); each component keeps its own folder and title, and both use the shared root class (`components/quote/` → `.document`)
4. Rename every class of the block when the block name changes, and treat it as a major version

**Incorrect (folder and block disagree):**

```text
components/logo/preview.html   → <div class="logo-usage"> … </div>
```

**Correct (folder, file and block agree):**

```text
components/logo/README.md      → # logo
components/logo/preview.html   → <div class="logo"> <div class="logo__row"> …
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 2.4 Never Use a Modifier Without Its Base

**Impact (MEDIUM):** A lone modifier hides which element it modifies and leaves the base rule unused, which the final audit then reports as dead code.

**Guidelines:**

1. Write `class="chart__delta chart__delta--negative"`, never only the modifier
2. If the base class carries no styles, still keep it in markup when the modifier is defined on it
3. Modifiers with no CSS of their own are allowed only as documented hooks, listed under **Clases** in the component file (for example `folder--outside` marking a face)
4. States the markup already expresses (`disabled`, `aria-selected`, `aria-expanded`, `aria-current`) are styled from the attribute, not with a modifier

**Incorrect (modifier alone):**

```html
<text class="chart__value chart__delta--negative">−8 %</text>
```

**Correct (base plus modifier):**

```html
<text class="chart__value chart__delta chart__delta--negative">−8 %</text>
```

Reference: [BEM naming](https://getbem.com/naming/)

---

## 3. Color

### 3.1 Build the Palette on Tailwind CSS Scales

**Impact (CRITICAL):** Loose hex values multiply with every piece and cannot be translated to utilities. Fixed scales keep every color nameable, auditable and directly usable as a class.

**Guidelines:**

1. Brand scales: `primary`, the main brand color, always; `secondary`, the dark or gray scale for text and dark blocks, always (the brand's own gray when it has one, otherwise a gray the user chooses); `tertiary`, `quaternary`… only for additional brand colors
2. Each brand scale goes from 50 to 950 with a `DEFAULT` equal to the brand value (at `-800` when the gray is chosen)
3. The user provides every step of each brand scale, never generated (see `scope-brand-intake`)
4. Status scales taken from _Tailwind CSS_ unchanged: `success` (`emerald`), `error` (`red`), `warning` (`yellow`), `info` (`sky`), each with `DEFAULT` at `-700`
5. `neutral` (`gray`) for borders on `white`, `DEFAULT` `neutral-200`; plus `white`
6. When a status scale is confusable with a brand color, replace it with the nearest _Tailwind CSS_ scale that is not and record the change (reference: orange brand → warning `yellow`, never `amber` or `orange`); when no clear alternative exists, tell the user
7. Chart colors (`chart-1` … `chart-5`) are aliases of palette tones, never new colors
8. Color is flat: no gradients and no semi-transparent tones (such as `primary-500/10`), except the gradients the brand defines (reference: _ASKIT_, only in the logo files) and the modal backdrop (see `surf-no-shadows`)
9. Base the whole system on _Tailwind CSS_ v4.3 scales and names (text sizes, spacing, radius, breakpoints) and ship a theme file that replaces the default palette

**Incorrect (loose values and a gradient):**

```css
.badge {
  background: #ffe9c7;
  color: #8a4b00;
}
.alert--warning {
  background: #fff4e5;
} /* amber, confusable with the brand */
.post {
  background: linear-gradient(135deg, var(--primary-500), var(--primary-700));
}
```

**Correct (_ASKIT_ reference scales):**

```css
--primary-500: #ffa10b; /* DEFAULT primary */
--secondary-800: #2a2a2a; /* DEFAULT secondary */
--warning-50: oklch(98.7% 0.026 102.212); /* Tailwind yellow-50 */
.badge--brand {
  background: var(--primary-100);
  color: var(--secondary-950);
  border: 1px solid var(--primary-200);
}
```

Reference: [Tailwind CSS colors](https://tailwindcss.com/docs/colors) · [Tailwind CSS theme variables](https://tailwindcss.com/docs/theme)

### 3.2 Text on White Is secondary-950

**Impact (CRITICAL):** Mid-gray or brand-colored body text fails contrast on print and screens. One dark text tone gives maximum legibility and a consistent page.

**Guidelines:**

1. Main text: `secondary-950` (19.8:1 on `white` in the reference)
2. Supporting text: `secondary-600`; the lightest allowed is the lightest step that measures ≥ 4.5:1 on `white` (reference: `secondary-500` in _ASKIT_)
3. Links are distinguished by underline, not by color
4. Disabled text (`secondary-400`) is the only lighter exception
5. On tinted backgrounds, text follows `color-50-950-convention`

**Incorrect (gray body text):**

```css
.card__text {
  color: var(--secondary-400);
} /* 2.5:1 */
a {
  color: var(--primary-500);
}
```

**Correct (dark text, gray support):**

```css
.card__title {
  color: var(--secondary-950);
}
.card__text {
  color: var(--secondary-600);
}
a {
  color: inherit;
  text-decoration: underline;
}
```

Reference: [WCAG 2.2 contrast (minimum)](https://www.w3.org/TR/WCAG22/#contrast-minimum)

### 3.3 Pair -50 Backgrounds With -950 Text

**Impact (HIGH):** A single pairing rule removes per-component guessing and guarantees contrast in tinted pieces (alerts, badges, callouts).

**Guidelines:**

1. On `-50`: text and icons `-950`; lower emphasis `-800`
2. On `-950`: text and icons `-50`; lower emphasis `-200`
3. On `secondary-800` and `secondary-900` blocks: text and icons `white`; lower emphasis `secondary-200`; measure both (see `color-measure-contrast`)
4. Never combine a `-50` or `-950` background with text from another scale; the only exception is `primary-500` on dark `secondary` blocks (see `color-brand-fill-only`)
5. Icons take the tone of the text they accompany

**Incorrect (mixed scales on a tint):**

```css
.report__callout {
  background: var(--primary-50);
  color: var(--secondary-600);
}
```

**Correct (same-scale pairing):**

```css
.report__callout {
  background: var(--primary-50);
  color: var(--primary-950);
  border: 1px solid var(--primary-200);
}
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 3.4 Use the Brand Color as Fill, Not as Text on Light

**Impact (HIGH):** Saturated brand colors such as orange rarely reach 4.5:1 on white, and white text on them fails too. Using the brand color as a surface keeps it visible without harming legibility.

**Guidelines:**

1. When `primary-500` fails 4.5:1 on light backgrounds (reference: the _ASKIT_ orange), use it there only as fill, never as text or an icon
2. Text on the brand fill is the palette tone that passes the measured contrast (see `color-measure-contrast`); reference: `secondary-950` on `primary-500` and `primary-600` (9.8:1 and 7.6:1), never `white`, which fails on orange
3. On `secondary-800`, `secondary-900` or `secondary-950`, `primary-500` may be text, a title or a link
4. The brand scale is never a status color

**Incorrect (orange text and white on orange):**

```css
.eyebrow {
  color: var(--primary-500);
} /* on white */
.button--primary {
  background: var(--primary-500);
  color: var(--white);
}
```

**Correct (orange as fill):**

```css
.button--primary {
  background: var(--primary-500);
  color: var(--secondary-950);
}
.footer__title {
  color: var(--primary-500);
} /* on secondary-800 */
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 3.5 Never Communicate State With Color Alone

**Impact (HIGH):** Color-blind readers and grayscale prints lose color-only meaning. Fixed step roles keep status pieces consistent across components.

**Guidelines:**

1. State is never color alone: it always carries text or a sign; components that announce a state (`alert`, `toast`, field error) also carry the status icon (success `tick-circle`, error `close-circle`, warning `danger`, info `info-circle` in the reference library)
2. Step roles: `-50` background (text on it follows `color-50-950-convention`); `-200` border of that background; `-800` text and icons on `white`; `-700` lower emphasis on `white` and solid fill with `white` text; `-300` to `-600` only for charts and illustration
3. Gain and loss figures use `success-700` and `error-700` and always carry a sign (+/−)

**Incorrect (red text only):**

```html
<p style="color:red">Pago rechazado</p>
```

**Correct (icon, text and scale roles):**

```html
<div class="alert alert--error" role="alert">
  <svg class="alert__icon" aria-hidden="true">…close-circle…</svg>
  <div class="alert__content">
    <p class="alert__title">Pago rechazado</p>
    Revisa los datos de la tarjeta.
  </div>
</div>
```

Reference: [WCAG 2.2 use of color](https://www.w3.org/TR/WCAG22/#use-of-color)

### 3.6 Measure Contrast Before Choosing a Pair

**Impact (HIGH):** Contrast judged by eye fails on dim screens and cheap print. Measured ratios make conflicts objective when discussing a user's request.

**Guidelines:**

1. Compute the _WCAG_ relative-luminance ratio for each new pair
2. Text ≥ 4.5:1; icons, control borders and text ≥ 24px at any weight ≥ 3:1; compare the unrounded value (4.47:1 fails 4.5:1)
3. Cite the ratio in the documentation next to the rule (`secondary-500` 4.5:1 on `white`)
4. When a requested pair fails, flag it with the number (see `scope-user-choice-flag-conflicts`)

**Incorrect (unverified pair):**

```md
- Íconos en `secondary-50` sobre `primary-500`.
```

**Correct (measured pair):**

```python
def L(h):
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def ratio(a, b):
    a, b = sorted((L(a), L(b)), reverse=True)
    return (a + 0.05) / (b + 0.05)
ratio('fafafa', 'ffa10b')  # secondary-50 on primary-500: 1.94 → fails 3:1
ratio('fafafa', '2a2a2a')  # secondary-50 on secondary-800: 13.8 → passes
```

Reference: [WCAG 2.2 contrast (minimum)](https://www.w3.org/TR/WCAG22/#contrast-minimum)

### 3.7 Print With the Palette Sheet CMYK Values

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

---

## 4. Surfaces and States

### 4.1 Separate Surfaces With Borders, Never Shadows

**Impact (CRITICAL):** Shadows disappear in print, render differently per screen and conflict with the flat language of the brand.

**Guidelines:**

1. No `box-shadow`, `drop-shadow`, `text-shadow` or inset shadows, including on overlays (menus, modals, toasts); _Tailwind CSS_ `ring-*` utilities are shadows too, so use `outline-*` (see `surf-interaction-states`)
2. Every card, menu, modal, table, tooltip and toast has a 1px border
3. Modals and side panels sit on a backdrop of `secondary-950` at 50 % opacity
4. The logo never gets shadows or effects either

**Incorrect (shadow for elevation):**

```css
.menu {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}
```

**Correct (border for separation):**

```css
.menu {
  border: 1px solid var(--neutral-200);
}
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 4.2 Border Tinted Pieces With Their Own Scale at 200

**Impact (HIGH):** A gray border cuts a tinted surface; a border from the same hue frames it and keeps tinted pieces consistent.

**Guidelines:**

1. `<status>-50` → border `<status>-200` (alerts, status badges)
2. Any brand scale (`primary`, `tertiary`…) `-50`/`-100` → its own `-200` (reference: `primary` in the brand badge, avatar, icon boxes, callouts)
3. `secondary-50`/`100` → `secondary-200` (neutral badge, counters, sidebar, table header, email footer, legal block)
4. Inner dividers of a tinted piece use the same `-200`
5. Hover fills, disabled controls and skeleton loaders are states, not pieces: hover and disabled follow `surf-interaction-states` and skeletons their component file; controls keep their neutral border on a tint (see `surf-neutral-borders`)
6. List every tinted piece in the Borders section of the overview

**Incorrect (tint without border or with gray):**

```css
.card__icon {
  background: var(--primary-100);
}
.alert--info {
  background: var(--info-50);
  border: 1px solid var(--neutral-200);
}
```

**Correct (same-scale border):**

```css
.card__icon {
  background: var(--primary-100);
  border: 1px solid var(--primary-200);
}
.alert--info {
  background: var(--info-50);
  border: 1px solid var(--info-200);
}
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 4.3 Use the Neutral Scale for Borders on White and for Controls

**Impact (HIGH):** Form controls need 3:1 border contrast to be found; using the piece's tint for them makes inputs vanish.

**Guidelines:**

1. `neutral-200` (DEFAULT): cards, menus, dropdowns, modals, table outlines, dividers
2. `neutral-300`: disabled controls and tab hover
3. `neutral-400`: dashed reference zones (die-cut slots, safe areas)
4. `neutral-500`: form controls at rest (4.8:1 on `white`), never lighter
5. `neutral-800`: secondary button, checked controls, hover of controls and interactive cards, total rule in quotes and invoices; a field in error takes `error-700` (6.42:1 on `white`)
6. On `secondary-800`, `secondary-900` or `secondary-950` surfaces: `neutral-950` to separate surfaces (tooltip, toast); `neutral-400` for controls (5.52:1)

**Incorrect (light borders on controls):**

```css
.field__control {
  border: 1px solid var(--neutral-200);
} /* 1.2:1 */
.dropzone {
  border: 2px dashed var(--primary-200);
}
```

**Correct (neutral controls):**

```css
.field__control {
  border: 1px solid var(--neutral-500);
}
.dropzone {
  border: 2px dashed var(--neutral-500);
  background: var(--secondary-50);
}
.tooltip__text {
  background: var(--secondary-800);
  border: 1px solid var(--neutral-950);
}
```

Reference: [WCAG 2.2 non-text contrast](https://www.w3.org/TR/WCAG22/#non-text-contrast)

### 4.4 Define One Focus Ring and Fixed Hover and Disabled States

**Impact (HIGH):** Different focus styles per component confuse keyboard users and fail audits; fixed states also make derived designs predictable.

**Guidelines:**

1. Focus: one ring, `outline: 2px solid secondary-800` with `outline-offset: 2px`; on `secondary-800`, `secondary-900` or `secondary-950` surfaces the ring is `primary-500`
2. Hover: filled elements go one step lighter (`primary-500` → `primary-400`); transparent or `white` elements take `secondary-100`, and `secondary-700` on dark surfaces; hover styles go inside `@media (hover: hover)` so they do not stick on touch screens
3. Disabled: background `secondary-100`, text `secondary-400`, border `neutral-300` (`neutral-200` on buttons)
4. Never remove the outline without replacing it

**Incorrect (removed outline):**

```css
.button:focus {
  outline: none;
}
```

**Correct (single ring):**

```css
.button:focus-visible {
  outline: 2px solid var(--secondary-800);
  outline-offset: 2px;
}
.footer :focus-visible {
  outline-color: var(--primary-500);
}
@media (hover: hover) {
  .button--primary:hover {
    background: var(--primary-400);
  }
}
```

Reference: [WCAG 2.2 focus visible](https://www.w3.org/TR/WCAG22/#focus-visible)

---

## 5. Brand Assets

### 5.1 Ship the Full Logo Variant Set

**Impact (CRITICAL):** Missing variants push people to recolor or screenshot the logo, which is the most visible brand error.

**Guidelines:**

1. `logo__primary--*` (full logo, default) and `logo__symbol--*` (symbol only: app icon, favicon, avatar, watermark)
2. Modifiers: `--gradient` (light backgrounds, default), `--gradient-negative` (dark backgrounds, primary only), `--flat` (solid brand colors, small sizes and print), `--negative` (all white), `--black` (one-ink print)
3. Text converted to outlines; never retyped with the font
4. Derived files: PNG for email (`--width_480`), symbol PNG for signatures (`--width_112`), SVG favicon = the symbol file, PNG favicon `--width_32`, app icons 180/192/512 light and 512 dark, and a `site.webmanifest`
5. Remove duplicates (one SVG serving as both symbol and favicon is one file)

**Incorrect (one logo file for everything):**

```text
logo.png            # 2000 px, used in email, favicon, print and dark backgrounds
```

**Correct (_ASKIT_ reference set):**

```text
logo__primary--gradient.svg            logo__symbol--gradient.svg   (also the SVG favicon)
logo__primary--gradient-negative.svg   logo__symbol--flat.svg
logo__primary--flat.svg                logo__symbol--negative.svg
logo__primary--negative.svg            logo__symbol--black.svg
logo__primary--black.svg               logo__favicon--gradient--width_32.png
logo__primary--gradient--width_480.png logo__app-icon--light--width_180.png / _192 / _512
logo__symbol--gradient--width_112.png  logo__app-icon--dark--width_512.png
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 5.2 Respect Logo Minimum Sizes, Clear Space and Misuse Rules

**Impact (CRITICAL):** An undersized or crowded logo becomes illegible in print and on small screens; misuse breaks recognition faster than any other error.

**Guidelines:**

1. Clear space: 2X on every side, where X is a defined logo measure (reference: the width of the square dot of the "i")
2. Minimums (reference): primary 24px on screen and 8 mm printed; symbol 16px and 5 mm; below the primary minimum, use the symbol
3. Check every component: any logo element below the minimum is a defect (reference: `report__symbol` raised from 12pt, 4.2 mm, to 15pt, 5.3 mm)
4. Never distort, rotate, separate or reorder parts, add shadows or effects, retype the text, or place it on `primary-500`

**Incorrect (undersized symbol):**

```css
.report__symbol {
  height: 12pt;
} /* 4.2 mm, below the 5 mm symbol minimum */
```

**Correct (minimum respected):**

```css
.report__symbol {
  height: 15pt;
} /* 5.3 mm ≥ 5 mm */
.letter__logo {
  height: 24pt;
} /* 8.5 mm ≥ 8 mm */
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 5.3 Derive Graphic Devices From the Logo, One per Piece

**Impact (HIGH):** Stacking devices turns pieces into collages; inventing unrelated shapes weakens the link with the logo.

**Guidelines:**

1. Derive each device from one logo feature and the brand promise (reference: the square dot of the "i" and "Innovación local, impacto global")
2. Pattern (reference): 16px `primary-500` squares every 48px, in corners or bands, on `white` or `secondary-800`
3. Progression (reference): seven `primary-500` squares, each 1.5× the previous, gap 0.7× its own side, bottom-aligned, the last one cut by the edge; unit set by `--progression-unit`
4. Scaled slogan (reference): the slogan set large as the main graphic of the piece, in the form of `brand-slogan-form`; the slogan at text size (footer, signature, card back) is copy, not a device
5. One device per piece; never combined with another device; never on photographs or on `primary-500`; corners from the logo feature (see `found-spacing-radius`; reference: `radius-none`)
6. Never place text over a device; text and device occupy separate areas of the piece
7. Each device gets its own component file (`pattern`, `progression`, `slogan`) even when few pieces use it, because derived designs need its exact construction

**Incorrect (two devices and text on the pattern):**

```html
<section class="post">
  <svg class="post__pattern">…</svg>
  <ol class="progression">
    …
  </ol>
  <h2 class="post__title" style="position:absolute;top:0">sobre el patrón</h2>
</section>
```

**Correct (one device, clear of text):**

```html
<section class="businesscard businesscard--back">
  <p class="businesscard__slogan">Innovación local,<br />impacto global</p>
  <ol class="progression businesscard__progression" aria-hidden="true">
    <li class="progression__step"></li>
    … seven steps …
  </ol>
</section>
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 5.4 Set the Slogan in Its Fixed Form

**Impact (HIGH):** Slogans rewritten per piece ("Innovación local e impacto global.") stop being a brand asset.

**Guidelines:**

1. Composed form: split the slogan at its natural pause into a lead line, small in `secondary-600`, and a main line, 2–2.5× larger in 600 `secondary-950` (reference: "Innovación local," / "impacto global"); a slogan with no natural pause is set as a single main line
2. In the composed form, a `primary-500` square of 0.2em replaces the final period
3. Plain-text form: the size of the surrounding text, on one line or broken at the natural pause, with no period and no square (footer, email signature, business card back, the system's `Cover`)
4. Use the composed form when the slogan stands as a graphic element of the piece (the scaled slogan of `brand-graphic-devices`, stationery footers) and the plain-text form everywhere else
5. Sizes through `--slogan-lead` and `--slogan-main`; on `secondary-800` use `slogan--negative` (`secondary-200` and `white`)
6. Left aligned; in print the lead line never goes below 9pt (12px, on the 4px scale)

**Incorrect (rewritten slogan with a period):**

```html
<p class="footer__slogan">Innovación local, impacto global.</p>
<p style="font-size:18px">Innovación local e impacto global</p>
```

**Correct (fixed form):**

```html
<p class="slogan letter__slogan">
  <span class="slogan__lead">Innovación local,</span>
  <span class="slogan__main"
    >impacto global<span class="slogan__dot"></span
  ></span>
</p>
<p class="footer__slogan">Innovación local, impacto global</p>
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 5.5 Choose Licensed Imagery With Written Criteria

**Impact (MEDIUM):** Unrecorded stock images become legal risks, and unguided choices produce clichés that weaken the brand.

**Guidelines:**

1. Write criteria tied to the brand (reference: real people working, natural light, local context; avoid hands on keyboards, unreadable code, handshakes)
2. Natural color, no filters; text over photos goes in a dark band or with the negative logo on a dark area
3. Illustrations flat and geometric; vector files recolored to the brand gray with brand-color accents; no gradients
4. Store the source link and license with each file; name it `image__<topic>--width_<px>.jpg`

**Incorrect (unrecorded cliché):**

```text
hero-final.jpg   # hands on keyboard, unknown source, blue filter
```

**Correct (recorded and named):**

```text
image__case--width_1200.jpg   # source URL + commercial license recorded next to it
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

---

## 6. Print Production

### 6.1 Deliver Print-Ready PDFs

**Impact (CRITICAL):** A screen PDF sent to a print shop comes back with white edges, shifted colors or substituted fonts.

**Guidelines:**

1. Real size, 3 mm bleed on every edge that has color, crop marks 3 mm off the trim and 6 mm long at 0.25pt, inside a 12 mm slug
2. A slug label with brand, piece, face, size, bleed and color mode
3. Colors converted to CMYK with `color-cmyk-print`; text below 12pt prints in K only (if its tone converts with C, M or Y, use its K value alone and tell the user); fonts embedded as subsets; `TrimBox` and `BleedBox` set on every page
4. Elements that should bleed extend 3 mm past the trim; nothing else touches the edge, and text, logos and data stay at least 5 mm inside the trim
5. One file per piece in the `print` asset group (`print__<piece>--<format>.pdf`), multi-page when the piece has faces
6. Name the format honestly: if the file is not PDF/X, say so and let the print shop convert with its profile

**Incorrect (screen export):**

```text
tarjeta.pdf — RGB, no bleed, no crop marks, fonts not embedded
```

**Correct (_ASKIT_ reference):**

```text
print__businesscard--85x55.pdf — 85 × 55 mm, 2 pages (front, back), 3 mm bleed, crop marks,
CMYK (primary-500 C0 M37 Y96 K0; secondary-800 K84), Lexend embedded, TrimBox and BleedBox
```

Reference: [Bleed (printing)](<https://en.wikipedia.org/wiki/Bleed_(printing)>)

### 6.2 Keep Printed Text and Logos Above Their Minimums

**Impact (CRITICAL):** Text below 9pt and undersized logos become unreadable on paper even when they look fine on screen.

**Guidelines:**

1. Sizes in multiples of 3pt (4px = 3pt): 9pt for footers, notes and senders; 12pt for body and tables
2. Business card: name 12pt; role and contact data 9pt, with the address split in two lines (street; city and country); slogan 9pt
3. Logo ≥ 8 mm high printed; symbol ≥ 5 mm
4. Write sizes in `pt` and `mm` at real size (see `print-real-size`) and check them before publishing

**Incorrect (small print):**

```css
.letter__footer {
  font-size: 6pt;
}
```

**Correct (minimums respected):**

```css
.letter__footer {
  font-size: 9pt;
}
.businesscard__role {
  font-size: 9pt;
}
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 6.3 Compose Print Pieces at Real Size

**Impact (MEDIUM):** Per-piece px scales give "4px" a different real size in every piece, force decimal conversions and keep minimums from being checked at a glance.

**Guidelines:**

1. Write print components at real size with CSS `mm` and `pt`, on the standard CSS scale (1px = 0.75pt, 96px = 25.4 mm); never a per-piece px scale
2. Text sizes, spacing, logos and graphic devices in multiples of 3pt (4px = 3pt); `mm` only for physical measures (format, slots, bleed, safety margin)
3. Enlarge the preview with `zoom` inside `@media screen`, never by changing the measures
4. Render the PDF from the same CSS, where the screen zoom does not apply

**Incorrect (a per-piece px scale):**

```css
/* envelope DL at 3px = 1 mm */
.envelope {
  width: 660px;
  height: 330px;
}
.envelope__logo {
  height: 24px;
} /* 8 mm */
```

**Correct (real size, enlarged only on screen):**

```css
.envelope {
  width: 220mm;
  height: 110mm;
}
.envelope__logo {
  height: 24pt; /* 8.5 mm */
}
.envelope__sender {
  font-size: 9pt;
}
@media screen {
  .envelope {
    zoom: 1.5;
  }
}
```

Reference: [CSS absolute lengths](https://www.w3.org/TR/css-values-4/#absolute-lengths)

### 6.4 Generate Print Files Reproducibly

**Impact (MEDIUM):** Hand-exported files drift from the components; a pipeline regenerates every piece identically after each change.

**Guidelines:**

1. Build one HTML page per face from the component preview, at real size (see `print-real-size`), with bleed rectangles and crop marks
2. Render with a headless browser (_Playwright_ + _Chromium_) using `preferCSSPageSize` and `printBackground`, fonts loaded from absolute local paths
3. Convert colors with a PDF library that rewrites operators (for example _pikepdf_), handling shadings inside patterns; avoid tools that rasterize gradients
4. Set `TrimBox` and `BleedBox`, merge faces, then rasterize each page and inspect it before publishing: reference marks absent, text 5 mm inside the trim and text below 12pt in K only (see `print-pdf-spec`, `print-dielines`)
5. Check that fonts are embedded (no Type 3 fallback) and compare file sizes with the previous version; a much larger file usually means a rasterized gradient

**Incorrect (manual export):**

```text
Open preview → Print → Save as PDF → send to the print shop
```

**Correct (scripted and verified):**

```text
build one HTML page per face from the preview, at real size, with absolute font paths
render each page to PDF with Chromium
convert to CMYK, set TrimBox and BleedBox, merge the faces
pdffonts print__folder--229x305.pdf                   # fonts embedded
pdftoppm -r 40 -png print__folder--229x305.pdf check  # visual check
```

Reference: [Playwright page.pdf](https://playwright.dev/docs/api/class-page#page-pdf) · [pikepdf](https://pikepdf.readthedocs.io/)

### 6.5 Mark Die-Cut and Reference Zones Without Printing Them

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

---

## 7. Foundations

### 7.1 Use One Typeface by Default, in Three Weights

**Impact (HIGH):** Several families or weights dilute the brand and inflate files; a font loaded only from a third-party CDN breaks offline, in PDFs and in strict environments.

**Guidelines:**

1. Choose one family with an open license (_OFL_) and record its source and license
2. One family by default; a second one only when the brand defines it, for headings, with the same weights and file rules
3. Weights: 400 running text, 500 labels, buttons and navigation, 600 headings; no others
4. Ship local files named in _BEM_ (`fonts/font__<family>--<weight>.woff2`) and embed them in print PDFs
5. Email and other restricted contexts declare a fallback stack (`<Family>, Arial, sans-serif`)

**Incorrect (families the brand does not define and weights outside the scale):**

```css
h1 {
  font-family: 'Montserrat';
  font-weight: 800;
}
body {
  font-family: 'Open Sans';
  font-weight: 300;
}
```

**Correct (_ASKIT_ reference):**

```css
@font-face {
  font-family: 'Lexend';
  font-weight: 600;
  src: url('../fonts/font__lexend--600.woff2') format('woff2');
}
--font-brand: 'Lexend', system-ui, sans-serif;
```

Reference: [Lexend on Google Fonts](https://fonts.google.com/specimen/Lexend)

### 7.2 Map Text to Named Roles

**Impact (HIGH):** Arbitrary font sizes per piece break hierarchy across documents and screens. Named roles make every size intentional and translatable.

**Guidelines:**

1. Roles: `display` `text-6xl`, `h1` `text-5xl`, `h2` `text-4xl`, `h3` `text-3xl`, `h4` `text-2xl`, `h5` `text-xl` (all 600), `lead` `text-lg`, `body` `text-base`, `body-sm` `text-sm`, `label` `text-sm font-medium`, `caption` `text-xs`, `overline` `text-xs font-medium tracking-widest uppercase`
2. On screen, the 4px grid applies to line heights, which are all multiples of 4 in the _Tailwind CSS_ scale; font sizes keep the _Tailwind CSS_ values (including `text-sm` 14px, `text-lg` 18px and `text-3xl` 30px)
3. Below `md`, `display` to `h3` drop two steps; `h4` and `h5` stay
4. Print uses points on the 4px grid (4px = 3pt, so multiples of 3): 12pt body and tables, 9pt notes, footers and senders
5. No sizes outside the scale

**Incorrect (ad-hoc sizes):**

```css
.hero-title {
  font-size: 53px;
  font-weight: 700;
}
```

**Correct (role classes):**

```html
<h1 class="h1">Automatización de la facturación</h1>
<p class="overline">Propuesta comercial</p>
```

Reference: [Tailwind CSS font size](https://tailwindcss.com/docs/font-size)

### 7.3 Ship One Light Theme by Default

**Impact (HIGH):** Maintaining a dark theme doubles every color decision and every print and document piece, for little brand value.

**Guidelines:**

1. One light theme by default for web, apps and documents (reference: _ASKIT_ has no dark mode)
2. A dark theme only when the user asks for it for the brand, with its own measured contrast pairs and every component checked in both themes
3. Dark tones (`secondary-800` to `secondary-950`) as backgrounds only for bands, footers, covers, card backs and similar contrast blocks; as text and icons they follow `color-text-on-light`
4. Every component is designed and checked on the light theme
5. While the system has only the light theme, declare `color-scheme: light` (CSS and `<meta name="color-scheme" content="light">`) so browsers do not darken the pages; check email pieces in the dark mode of _Gmail_ and _Outlook_, which may invert them anyway

**Incorrect (a dark theme switch the user did not ask for):**

```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0a0a0a;
    --text: #fafafa;
  }
}
```

**Correct (a dark block inside the light theme):**

```css
.footer {
  background: var(--secondary-800);
  color: var(--white);
}
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 7.4 Use the Spacing and Radius Scales With Fixed Assignments

**Impact (MEDIUM):** Without assignments every component picks its own padding and corner, and the family stops looking related.

**Guidelines:**

1. Spacing: multiples of 4px, only whole steps (`spacing-1`, `spacing-2`, `spacing-3`…); half steps (`0.5`, `1.5`, `2.5`, `3.5`) break the 4px grid; `spacing-1`/`2` icon gaps, `spacing-4` inside controls, `spacing-6` inside cards, `spacing-8` between blocks, `spacing-16`/`24` between sections
2. Radius: `sm` checkboxes; `lg` buttons, fields, icon boxes, menu options, tooltips, skeletons; `xl` alerts, menus, tables, toasts; `2xl` cards, panels; `3xl` modals; `full` pills, avatars, switches, counters; `md` (6px) is not used because it breaks the 4px grid
3. Patterns and brand graphics take the corner of the logo feature they derive from (reference: `radius-none` in _ASKIT_, from the square dot)
4. No values outside the scales

**Incorrect (arbitrary values):**

```css
.card {
  padding: 22px;
  border-radius: 10px;
}
.progression__step {
  border-radius: 2px;
}
```

**Correct (scale values):**

```css
.card {
  padding: var(--spacing-6);
  border-radius: var(--radius-2xl);
}
.progression__step {
  border-radius: 0;
}
```

Reference: [Tailwind CSS theme variables](https://tailwindcss.com/docs/theme)

### 7.5 Use Standard Breakpoints, Grid and Motion

**Impact (MEDIUM):** Custom breakpoints and animations make every derived design solve the same problems differently.

**Guidelines:**

1. Breakpoints `sm` 40rem (640px), `md` 48rem (768px), `lg` 64rem (1024px), `xl` 80rem (1280px), `2xl` 96rem (1536px), mobile first
2. Page container `max-w-7xl` with `px-6 lg:px-8`; running text up to `container-2xl`; grid 4 columns, 8 from `md`, 12 from `lg`, gap `spacing-6`
3. Motion: `duration-150 ease-out` hover and focus; `duration-200 ease-out` menus, tooltips, toasts; `duration-300 ease-in-out` modals and panels
4. Nothing loops except loaders; `prefers-reduced-motion` removes movement; with reduced motion, loaders keep a non-moving indicator (the text "Cargando…")

**Incorrect (custom values):**

```css
@media (max-width: 900px) { … }
.menu { transition: all 0.45s cubic-bezier(.2,.9,.3,1.4); }
```

**Correct (scale values):**

```css
.h1 {
  font-size: 1.875rem;
} /* phone */
@media (min-width: 48rem) {
  .h1 {
    font-size: 3rem;
  }
} /* from md */
.menu {
  transition: opacity 200ms ease-out;
}
@media (prefers-reduced-motion: reduce) {
  * {
    transition: none;
    animation: none;
  }
}
```

Reference: [Tailwind CSS responsive design](https://tailwindcss.com/docs/responsive-design)

### 7.6 Ship a Tailwind CSS Theme That Restricts the Palette

**Impact (MEDIUM):** Projects using utilities otherwise keep `text-red-500` and `shadow-lg` available and drift from the system on day one.

**Guidelines:**

1. `code/tailwind__theme.css` with `@theme { --color-*: initial; … }` and only the system scales, `white` and `chart-1` … `chart-5`
2. Keep text sizes, spacing, radius and breakpoints as _Tailwind CSS_ ships them
3. Set `--font-sans` to the brand family, with `@font-face` pointing at the local files of `found-single-typeface`; a second family, when the brand defines one, as `--font-heading`
4. Reset `--shadow-*`, `--inset-shadow-*`, `--drop-shadow-*` and `--text-shadow-*`
5. With _Tailwind CSS_, projects load only the theme and build each component from the _Tailwind CSS_ equivalent in its component file; they do not load `components/bundle.css`
6. Without _Tailwind CSS_, projects load `tokens.css` and `components/bundle.css`

**Incorrect (default palette left in place):**

```css
@import 'tailwindcss';
/* text-red-500, shadow-lg and bg-amber-400 still exist */
```

**Correct (restricted theme):**

```css
@import 'tailwindcss';
@import './tailwind__theme.css';
/* @theme { --color-*: initial; --color-primary-500: #ffa10b; … --font-sans: "Lexend", system-ui, sans-serif; --shadow-*: initial; } */
```

Reference: [Tailwind CSS theme variables](https://tailwindcss.com/docs/theme)

---

## 8. Writing and Voice

### 8.1 Document in Spanish, Name in English

**Impact (HIGH):** The audience of the brand pieces and of the documentation is Spanish-speaking, while the code is consumed by tools and developers. Mixing the two directions produces Spanish class names and English labels on screen.

**Guidelines:**

1. Write overview, component files, asset group files, changelog and every visible text (titles, labels, sample content) in Spanish
2. Keep file names, classes, tokens, variables and attributes in English (see `name-bem-english`)
3. Generated sections that the platform writes in English (for example "Consuming this system") stay as generated
4. Comments inside code are in English, like the names

**Incorrect (English copy and Spanish names):**

```html
<button class="boton boton--principal">Schedule a meeting</button>
```

**Correct (Spanish copy and English names):**

```html
<button class="button button--primary">Agenda una reunión</button>
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 8.2 Use One Warm, Neutral Voice

**Impact (HIGH):** Voice is part of the brand. Formal "usted" in one piece and slang in another breaks recognition as much as a wrong color.

**Guidelines:**

1. Choose one form of address with the user, "tú" or "usted", and use it in every piece (reference: _ASKIT_ uses tú: "tú", "tu empresa", "te ayudamos"); the company speaks in first person plural
2. Neutral Spanish with no regionalisms or slang; explain technical terms in the same sentence when the reader does not use them; no absolute promises ("100 % garantizado"): say what is actually done
3. Short sentences in active voice; sentence-case headings, never all caps (except `overline`)
4. Derive three brand values from the brand message and write "Así sí / Así no" examples for them
5. Formats: dates "12 de octubre de 2026"; money "COP $1.200.000"; time "02:30 PM", with a leading zero on single-digit hours; phone "+57 (318) 517 0879"; percent with a space before the sign ("63 %"); decimals with a comma and thousands with a period ("4,2 horas", "2,5 %", "1.200 usuarios")

**Incorrect (_ASKIT_ reference: usted, a regionalism and an absolute promise):**

```text
Ingrese sus datos y nosotros le cuadramos todo, tranquilo. Seguridad 100 % garantizada.
```

**Correct (_ASKIT_ reference voice):**

```text
Escribe tus datos y te acompañamos antes, durante y después del lanzamiento.
Tus datos se cifran y se respaldan todos los días.
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 8.3 Italicize Proper Nouns and Write Values as Code

**Impact (MEDIUM):** Values written as plain text get misread, auto-corrected or mistaken for prose, and unmarked names blend into ordinary Spanish words. Inline code for values and italics for names make every term unambiguous and keep a single visual convention across dozens of files.

**Guidelines:**

1. Italicize proper nouns: companies, brands, products, typefaces, places and methodologies (reference: _ASKIT_, _ASK TECHNOLOGY S.A.S._, _Lexend_, _Tailwind CSS_, _Reicon_, _BEM_, _DIAN_, _Barranquilla_, _Outlook_, _LinkedIn_)
2. Do not italicize names inside headings, code, link text or generated sections, nor in the visible text of brand pieces (cards, documents, slides, emails)
3. Write as inline code every tone (`primary-500`, `<status>-200`), hexadecimal value (`#FFA10B`, uppercase in documentation as on the palette sheet and lowercase in code), CMYK value (`C0 M37 Y96 K0`, `K84`), class or token (`button--primary`, `spacing-6`, `text-sm font-medium`) and file name (`logo__symbol--gradient.svg`); never as italics or plain text, not even in the changelog
4. Measures, units and contrast ratios stay plain text (16px, 3 mm, 4.5:1)

**Incorrect (plain names and values):**

```md
La validez legal la dan el proveedor tecnológico y la DIAN; la tipografía es Lexend.
Fondo primary 500 (#FFA10B, C0 M37 Y96 K0) con texto secondary-950.
```

**Correct (italic names, values as inline code):**

```md
La validez legal la dan el proveedor tecnológico y la _DIAN_; la tipografía es _Lexend_.
Fondo `primary-500` (`#FFA10B`, `C0 M37 Y96 K0`) con texto `secondary-950`.
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 8.4 Titles State the Conclusion

**Impact (MEDIUM):** A topic title ("Resultados") forces the reader to work out the message; a conclusion title delivers it and makes the piece scannable.

**Guidelines:**

1. Sections that present findings or data, and charts, state the finding with the key figure ("El tiempo de facturación bajó un 63 %"); structural sections (index, methodology, annexes, contact) keep their plain name
2. The subtitle says what is measured and in which unit
3. Every figure has a number, a description and a source; never a figure without a source
4. Decisions the client must take go in a highlighted block with the date by which the client must decide ("Decisión pendiente: aprobar el piloto antes del 30 de octubre de 2026")

**Incorrect (topic titles):**

```md
## Resultados

Figura: horas por mes
```

**Correct (conclusion titles):**

```md
## El tiempo de facturación bajó un 63 % en cuatro meses

Figura 1. Horas dedicadas a facturar por mes. Fuente: registro de tiempos del cliente, enero a abril de 2026.
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

---

## 9. Iconography

### 9.1 Use One Icon Library and Store Only Used Icons

**Impact (HIGH):** Mixed icon sets look inconsistent, and bundling a whole library bloats every project and the system itself.

**Guidelines:**

1. Pick one library with an open license and pin the version (reference: _Reicon_ 1.2.5, `Outline` weight)
2. Store only the icons used by components, as `icon__<kebab-name>--<weight>.svg` (reference: `--outline` and `--filled` in _Reicon_), with a table of where each is used in the icons group file
3. When a component stops using an icon, delete the file and the row (major version)
4. Projects import other icons one by one from the library (`npm i reicon-react@1.2.5`, CDN per icon); they are never added to the system
5. Never draw custom glyphs when the library has one; control marks such as checkbox ticks use the library path too; when the library lacks a glyph, draw it on the library's grid and stroke width, and register it like any other icon, marked as custom in the group file

**Incorrect (custom glyph and unused files):**

```css
.checkbox__control:checked {
  background-image: url("…path d='M5 12.5l4.5 4.5L19 7.5'…");
}
/* assets/icons/ also keeps icon__call--outline.svg, used by nothing */
```

**Correct (library glyph, used files only):**

```md
| Archivo                    | Ícono en _Reicon_ | Dónde se usa                   |
| -------------------------- | ----------------- | ------------------------------ |
| `icon__check--outline.svg` | `Check`           | `stepper`; marca de `checkbox` |
```

Reference: [Reicon icons](https://reicon.dev/icons)

### 9.2 Size and Color Icons With the Text They Accompany

**Impact (MEDIUM):** Icons in arbitrary sizes and colors look pasted on; icon-only buttons without names are invisible to screen readers.

**Guidelines:**

1. Sizes: `ds-icon` 24px, the default; `ds-icon--sm` 20px next to `text-sm`; `ds-icon--xs` 16px next to `text-xs`
2. Color: `currentColor`; `secondary-950` on `white`, `white` on `secondary-800`, the 50/950 pair on tinted surfaces, `<status>-800` for status on `white`
3. Gap `spacing-2` (in tags `spacing-1`)
4. `Filled` weight only for active or selected states
5. Icon-only controls get `aria-label`; decorative icons get `aria-hidden="true"`

**Incorrect (arbitrary size and brand color):**

```html
<button><svg width="30" style="color:#ffa10b">…</svg></button>
```

**Correct (sized, inherited and named):**

```html
<button class="button button--icon-only" aria-label="Buscar">
  <svg class="ds-icon" aria-hidden="true" stroke="currentColor">…search…</svg>
</button>
```

Reference: [Reicon icons](https://reicon.dev/icons)

---

## 10. Components

### 10.1 Cover the Standard Component Catalog

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

### 10.2 Document Every Component With the Same Sections

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

### 10.3 Document the System in One Overview With Fixed Sections

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

### 10.4 Build Components Only From Tokens in One Bundle

**Impact (HIGH):** Hard-coded values inside components drift from the tokens; scattered stylesheets make the system impossible to load consistently.

**Guidelines:**

1. `components/bundle.css`: _BEM_ classes, `var(--token)` values only; spacing, radius and text-size tokens carry the _Tailwind CSS_ value as fallback; color tokens have none, because they come only from `tokens.css`
2. Root helper `ds-base` on the container (font, color, box sizing, focus ring)
3. `components/bundle.js` adds behavior only (toggles, tabs, menu keyboard, modal focus and `Esc`, dropzone highlight, toast dismissal, sidebar on mobile); it never draws
4. Load order: `tokens.css`, `bundle.css`, `bundle.js`
5. Every class defined in the bundle is used in a preview or the script, or documented in its component file; anything else is removed (see `gov-final-audit`)

**Incorrect (hard-coded values):**

```css
.toast {
  background: #2b2b2b;
  padding: 15px;
  border-radius: 11px;
}
```

**Correct (tokens with fallbacks):**

```css
.toast {
  background: var(--secondary-800);
  padding: var(--spacing-4, 1rem);
  border-radius: var(--radius-xl, 0.75rem);
  border: 1px solid var(--neutral-950);
}
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 10.5 Build Accessible Semantics Into Every Component

**Impact (HIGH):** Accessibility retrofitted in each derived design is inconsistent; baked into the component it comes for free.

**Guidelines:**

1. Native elements first (`button`, `label` + `input`, `nav`, `table`); _ARIA_ roles where needed (`tablist`/`tab`, `switch`, `alert`, `dialog`)
2. Icon-only controls with `aria-label`; decorative graphics with `aria-hidden="true"`
3. Charts: `svg` with `role="img"` and an `aria-label` stating the conclusion and key figures; in apps, data also in a `table`
4. Keyboard: tabs move with arrows, menus with arrows and `Esc`, sidebar panel closes with `Esc`; modals close with `Esc`, keep focus inside while open and return it to the control that opened them
5. Text fields (`field`, `select`, `search`, `date`) use at least 16px font, so phones do not zoom in on focus
6. Interactive targets at least 24 × 24px; 44 × 44px on touch screens

**Incorrect (div soup):**

```html
<div class="tabs"><div onclick="show(1)">Resumen</div></div>
<svg class="chart__plot">…</svg>
```

**Correct (semantic and named):**

```html
<div class="tabs" role="tablist">
  <button class="tabs__tab" role="tab" aria-selected="true">Resumen</button>
</div>
<svg
  class="chart__plot"
  role="img"
  aria-label="Las facturas procesadas crecieron un 41 % en seis meses: de 310 a 436."
>
  …
</svg>
```

Reference: [WCAG 2.2](https://www.w3.org/TR/WCAG22/)

### 10.6 Draw Charts With Palette Series and Direct Labels

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

---

## 11. Communication Pieces

### 11.1 Design the Stationery as One Family

**Impact (HIGH):** Stationery designed piece by piece ends up with four unrelated looks; a family multiplies brand recognition when the pieces travel together.

**Guidelines:**

1. Same margin logic, logo position and data alignment across pieces (reference: _ASKIT_ logo top left, data left aligned); one graphic device per piece
2. Reference family (_ASKIT_): business card with the progression on a `secondary-800` back; envelope DL, letter and folder with the scaled slogan
3. Letter (reference: _ASKIT_): logo top left, body from 144pt (5.08 cm), footer stacked (data above, slogan below, `spacing-6` between), no rule
4. Folder (reference: _ASKIT_): cover with logo top left and large slogan at the bottom; back cover on the same grid with the symbol top left and data bottom left; inside left blank; pocket `secondary-800` with negative slogan, data with square bullets and a card slot reference
5. Validate each face with the user and record the approved face before redesigning the others

**Incorrect (unrelated pieces):**

```text
businesscard: centered logo, blue stripe
envelope: orange band on top
letter: right-aligned header with a thick rule
```

**Correct (one family):**

```text
businesscard back: secondary-800 + progression
envelope DL: sender top left + scaled slogan bottom left (9pt / 21pt)
letter: logo top left + data and slogan stacked bottom left (9pt / 18pt)
folder: cover slogan 24pt / 60pt · back cover symbol + data · pocket slogan 12pt / 30pt
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 11.2 Put the Right Contact Data on Each Piece

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

### 11.3 Align Digital Documents With the Print Family

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

### 11.4 Build Email Pieces for Email Clients

**Impact (HIGH):** A signature built with the component CSS renders broken in _Outlook_ and _Gmail_.

**Guidelines:**

1. Markup as `<table role="presentation">` with inline styles and hex values of the palette tones
2. Logo as a hosted PNG at least 2× the displayed size (`--width_480` shown at 120px; symbol `--width_112` shown at 56px)
3. Font stack `<Family>, Arial, sans-serif`; check the piece in _Arial_, which most clients show; buttons as table cells with background
4. Signature: symbol, vertical separator, name, role, legal name, contact and slogan; no quotes, banners or inactive networks
5. Newsletter: 600px fluid, one topic, one button, optional image with `alt`, footer with legal name, tax ID, address and unsubscribe link
6. Check every piece in _Gmail_ and _Outlook_ dark mode (see `found-single-light-theme`)

**Incorrect (component CSS in an email):**

```html
<link rel="stylesheet" href="bundle.css" /><img
  src="logo__symbol--gradient.svg"
/>
```

**Correct (email-safe markup):**

```html
<table role="presentation" cellpadding="0" cellspacing="0">
  <tr>
    <td>
      <img
        src="https://askit.com.co/firma/logo__symbol--gradient--width_112.png"
        width="56"
        height="56"
        alt="ASKIT"
      />
    </td>
    <td style="font-family:Lexend,Arial,sans-serif;color:#0a0a0a">…</td>
  </tr>
</table>
```

Reference: [Can I email](https://www.caniemail.com/)

### 11.5 Keep Social and Slide Templates on the Brand Grid

**Impact (MEDIUM):** Social and presentation pieces are produced most often and by the most people; without templates they are where the brand degrades first.

**Guidelines:**

1. Posts 1080 × 1080 and 1080 × 1920; logo top left; headline up to 8 words; margins 96px; in stories, nothing important in the top and bottom 252px
2. Profile banners at the platform sizes checked on a stated date; slogan and website only, no logo; keep the profile-photo zone free
3. Slides 16:9 (960 × 540 scaled to 1920 × 1080): cover, interior, section, highlighted figure and closing slide with a call to action and contact data
4. One idea per slide, up to 5 one-line bullets drawn from the logo feature of the graphic devices (reference: _ASKIT_ `primary-500` squares; see `brand-graphic-devices`), sections numbered 01, 02…
5. Besides `white` and the `secondary` scale (text and dark blocks), at most two brand scales per piece

**Incorrect (crowded post):**

```text
Post: 3 headlines, 2 logos, photo under the pattern, CTA in the bottom 120px of a story
```

**Correct (templated post):**

```text
Post: logo top left · pattern top right (light version) · headline ≤ 8 words · one supporting sentence · one CTA button
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

---

## 12. Governance

### 12.1 Version Every Change and Record It in the Changelog

**Impact (HIGH):** Derived designs depend on names: an unannounced rename breaks them silently, and a vague changelog cannot tell them what to update.

**Guidelines:**

1. Major: rename or remove a token, class, component or file (including deleting an unused icon or a duplicate logo)
2. Minor: add a token, class, component, asset or rule
3. Patch: fix a value, a wording, a position or a bug without changing names
4. Group the changes of one request in one version; adjustments stay in the same version only while it is unpublished; once published, every adjustment is a new version
5. Each version gets one Spanish entry in `changelog.md`, newest first, headed `## <version> · <day> de <month> de <year>`; a major adds one line saying what breaks
6. One bullet per change naming the classes, files and assets involved as inline code; removals name their replacement ("Sale `folder__icon` y entra `folder__bullet`")
7. Update the index `lastChange` (author, date, note with the version)
8. Never rewrite past entries: a change reverted before it is published leaves no version and no entry; reverting a published change is a new version with its own entry, classified like any other change

**Incorrect (removed classes published as a patch, with a vague entry):**

```md
## 7.1.1

- Mejoras en la carpeta.
```

**Correct (a major with a precise entry):**

```md
## 8.0.0 · 15 de octubre de 2026

Cambio mayor: se eliminan clases de `folder` y tres archivos del grupo `icons`.

- `folder`, bolsillo: misma distribución, sin íconos; cada dato lleva como viñeta un cuadrado `primary-500` de 1.6 mm. Sale `folder__icon` y entra `folder__bullet`.
- Íconos: salen `icon__call--outline.svg`, `icon__sms--outline.svg` e `icon__global--outline.svg`; el grupo vuelve a 25.
```

Reference: [Semantic Versioning](https://semver.org/) · [Keep a Changelog](https://keepachangelog.com/)

### 12.2 Register Every Asset and Leave No Orphans

**Impact (HIGH):** Orphan files and broken references accumulate silently and make the system look larger and less trustworthy than it is.

**Guidelines:**

1. The index (`design-system.json`) holds one record per stored file (blob); each asset group also has a `README.md` listing every file with its use
2. To replace a file: upload the new one, update the index record (blob id and size), publish, verify, and only then delete the old blob
3. After any removal, search the whole system for references to the old name (except the changelog) and update or remove every reference found
4. The number of stored blobs must equal the number of index records
5. A file no component or piece uses is removed, as a major version (see `gov-versioning`), except the logo variant set that `brand-logo-variants` requires for derived designs

**Incorrect (delete first, update later):**

```text
delete blob 3710751f…  →  index still points to it  →  print file broken until the next publish
```

**Correct (safe swap):**

```text
upload print__folder--229x305.pdf → blob 81f1a4bd… (44173 bytes)
update design-system.json print record → publish → read back and verify → delete old blob ab8feac7…
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 12.3 Run a Final Audit Before Closing the System

**Impact (HIGH):** Small inconsistencies (an unused class, a lone modifier, a gray border on a tint, a slogan with a period) are invisible one by one and obvious together.

**Guidelines:**

1. Files: compare the published list with the local tree; every file is expected (platform files, sources, generated files)
2. Assets: every index record is used, except the logo variant set of `brand-logo-variants`, and documented; blob count equals record count
3. Classes: every class in the bundle appears in a preview, the script or a component file; every documented class exists; no lone modifiers; every component uses its own block
4. Conventions: _BEM_ English names; Spanish docs; italic proper nouns; values as inline code; one form of address; no shadows; tinted borders at 200; neutral control borders; logo and print minimums; icons from the library or registered as custom; slogan form; templates only; 4px grid (whole spacing steps, no `radius-md`, print sizes in multiples of 3pt); measured contrast for every text and icon pair
5. Claims: every sentence in the overview that says "cada", "todos" or a count is checked against the files
6. Fix, render the affected previews, publish one version and report findings, fixes and documented exceptions

**Incorrect (closing without a sweep):**

```text
User: "¿Ya todo está listo?"
Agent: "Sí." (an unused class, a 14px symbol and a period after the slogan remain)
```

**Correct (sweep, fix, report):**

```text
Audit 9.0.0: 47 assets = 47 blobs · chart__delta now used with its modifiers · logo-usage → logo ·
checkbox tick from the icon library · borders added to card__icon, empty__icon, tabs__count,
newsletter footer and tooltip · report__symbol 12pt → 15pt · slogan without period ·
exceptions documented (Cover folder, shared document block, folder--outside/--inside hooks)
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

### 12.4 Regenerate Generated Files Before Every Publish

**Impact (MEDIUM):** Generated files update only when the system is saved from its page; publishing sources without them leaves the manifest and API pages out of date.

**Guidelines:**

1. The system lives in a claude.ai artifact of the Design System type; publishing means updating that artifact, with the index (`design-system.json`) as its main file
2. Edit only sources: the overview body (`README.md`), component files, `tokens.json`, `components/bundle.css`, `components/bundle.js`, asset group files, `changelog.md`, `code/tailwind__theme.css` and the index
3. Regenerate from the sources before publishing: `tokens.css` (compiled from `tokens.json`), `manifest.json`, `api/**` and the generated tail of the overview
4. Publish changed sources plus regenerated files in one call, with the index as the main file (sent last)
5. Read the published index back to confirm records, then clean up replaced blobs

**Incorrect (hand-edited manifest):**

```text
edit manifest.json by hand → publish only bundle.css → api/components/*.md describe the old classes
```

**Correct (regenerate then publish):**

```text
regenerate tokens.css (from tokens.json), manifest.json, api/** and the README tail with a regeneration script
publish: changed sources + regenerated files, index (design-system.json) last
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)

---

## 13. Reference Implementation

### 13.1 Use ASKIT as the Resolved Reference

**Impact (MEDIUM):** A worked example shortens every decision for a new brand, but copying its values into another brand produces a clone instead of a system.

**Guidelines:**

1. Identity: legal name _ASK TECHNOLOGY S.A.S._, brand _ASKIT_, NIT 901.425.503-6, Carrera 64 #66-07, _Barranquilla_, _Atlántico_; info@askit.com.co; +57 (318) 517 0879; askit.com.co
2. Brand: slogan "Innovación local, impacto global"; logo with the symbol as the "A" and a square orange dot on the "i"; symbol gradient `primary-600` → `primary-500`
3. Color: `primary` orange, `primary-500` `#FFA10B` (`C0 M37 Y96 K0`); `secondary` gray, `secondary-800` `#2A2A2A` (`K84`); status scales from _Tailwind CSS_ (warning `yellow`)
4. Type: _Lexend_ 400/500/600; icons: _Reicon_ 1.2.5, `Outline` weight, only the icons the components use; base: _Tailwind CSS_ v4.3; one light theme; no shadows
5. Chosen pieces: business card with the progression on a `secondary-800` back; envelope and letter with the scaled slogan (letter data above it, phone and email only); folder with the large slogan on the cover and square bullets on the pocket; digital documents with data in the letterhead, no rule, slogan at the foot
6. For another brand (for example one using _Manrope_), keep the method, the scales and the rules; replace identity, palette values, typeface, logo, slogan and devices after intake

**Incorrect (copying _ASKIT_ values into another brand):**

```css
/* Another brand */
--primary-500: #ffa10b; /* ASKIT orange */
--font-brand: 'Lexend'; /* ASKIT typeface */
```

**Correct (same structure, own values):**

```css
/* Another brand: values from its own intake */
--primary-500: <its palette sheet value>;
--font-brand: 'Manrope', system-ui, sans-serif;
/* same scales, roles, borders, naming and governance as ASKIT */
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
