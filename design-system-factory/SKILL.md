---
name: design-system-factory
description: Standard for creating, extending and auditing a company's brand design system, covering the tokens, assets, components, print stationery, digital documents and governance that every piece derived from the brand must follow. It is not for building a specific website, app or presentation. Use when starting a design system from a brand (identity, palette, logo, slogan), designing or redesigning brand pieces (business card, envelope, letterhead, folder, quote, invoice, email signature, newsletter, social posts, slides), defining color, typography, borders, icons or naming conventions, preparing print-ready PDFs, versioning changes, or running a final audit. Includes ASK TECHNOLOGY S.A.S. (ASKIT) as the worked reference. Triggers on design system, sistema de diseño, brand, marca, manual de marca, papelería, tokens, BEM, CMYK, impresos.
license: MIT
metadata:
  author: gianllopez
  version: 1.0.0
---

# Design System Factory

Standard for building and maintaining the design system of a company brand: a single source that describes how every piece derived from the brand must look and be written, from tokens and components to printed stationery, digital documents, email and social templates. The system is brand-level, not a product: websites, apps, real presentations and personalized pieces are derived designs built from it. The rules optimize for one recognizable family across media, accessible contrast, print-ready output, predictable naming, and changes that are versioned and reviewable. The _ASK TECHNOLOGY S.A.S._ (_ASKIT_) system is the worked reference for every rule.

**Scope.** Every brand built with this skill is a Colombian company, so the formats for money, dates, time and phones and the legal references (_Cámara de Comercio_, _DIAN_) are fixed. The form of address, the number of brand colors and every identity value come from each brand's intake; a new brand reuses the method and structure of _ASKIT_, never its values.

## When to Apply

Reference these guidelines when:

- Starting a design system for a company from its identity data, palette sheet, logo and slogan
- Defining or changing color scales, typography, spacing, radius, borders, states, icons or naming conventions
- Designing or redesigning brand pieces: business card, envelope, letterhead sheet, presentation folder, letterhead, quote, invoice, report, email signature, newsletter, social posts, profile banners, slides
- Preparing print-ready PDFs (bleed, crop marks, CMYK, embedded fonts) for stationery
- Writing or reviewing component documentation, the overview or the changelog of a design system
- Publishing a new version of a design system artifact, or running the final audit before closing it

## Workflow

1. **Intake:** collect verified identity, palette (with print values), logo files, slogan, typeface and form of address; ask for anything missing (`scope-brand-intake`)
2. **Foundations:** palette scales, typeface, roles, spacing, radius, borders, states and naming (Color, Foundations, Surfaces and States, Naming)
3. **Brand assets:** logo variants and minimums, graphic devices, slogan form, imagery criteria, icon set (Brand Assets, Iconography)
4. **Components:** the full catalog with one documentation file and one preview each, and the overview that ties the system together (Components)
5. **Communication pieces:** propose rendered alternatives, implement the chosen one, keep stationery and documents as one family (Scope and Process, Communication Pieces)
6. **Print:** generate and verify print-ready PDFs from the previews (Print Production)
7. **Publish:** version and changelog entry, regenerated files, review list for the user (`gov-versioning`, `gov-generated-files`, `scope-report-changes`)
8. **Close:** run `gov-final-audit` and fix every finding before declaring the system finished

## Rule Categories by Priority

| Priority | Category                 | Peak impact | Prefix   |
| :------- | :----------------------- | :---------- | :------- |
| 1        | Scope and Process        | CRITICAL    | `scope-` |
| 2        | Naming                   | CRITICAL    | `name-`  |
| 3        | Color                    | CRITICAL    | `color-` |
| 4        | Surfaces and States      | CRITICAL    | `surf-`  |
| 5        | Brand Assets             | CRITICAL    | `brand-` |
| 6        | Print Production         | CRITICAL    | `print-` |
| 7        | Foundations              | HIGH        | `found-` |
| 8        | Writing and Voice        | HIGH        | `write-` |
| 9        | Iconography              | HIGH        | `icon-`  |
| 10       | Components               | HIGH        | `comp-`  |
| 11       | Communication Pieces     | HIGH        | `piece-` |
| 12       | Governance               | HIGH        | `gov-`   |
| 13       | Reference Implementation | MEDIUM      | `ref-`   |

Priority orders where to look first; peak impact is the strongest rule in the section, matching the table of contents in `AGENTS.md`.

## Quick Reference

### 1. Scope and Process (CRITICAL)

- `scope-brand-not-product` - A brand design system defines how every piece derived from a company brand must look; it is not a website, an app or a slide deck
- `scope-templates-only` - The system stores templates with sample data; pieces personalized for a person, client or project are derived designs
- `scope-brand-intake` - Gather the identity, palette, logo, slogan, typeface and form of address from official sources and the user before designing, and never invent missing brand data
- `scope-alternatives-first` - For every new or redesigned communication piece or graphic device, show several distinct rendered alternatives, let the user choose, then implement only the chosen one
- `scope-user-choice-flag-conflicts` - Grant the user's explicit design choices, but stop to flag any conflict with the system rules or with contrast before applying them
- `scope-report-changes` - After each published change, state the version, what changed and exactly which overview sections and files the user must review word by word
- `scope-answer-style` - Reply in short Spanish prose, avoid long lists, and put the question as a subtitle when answering direct questions

### 2. Naming (CRITICAL)

- `name-bem-english` - Classes, files and folders use BEM in English, custom properties, ids and attributes use English kebab-case, and only human-facing text is in Spanish
- `name-files-bem` - Every asset file follows `block__element--modifier.ext`, with `key_value` modifiers for measures
- `name-component-block` - Each component is named by its BEM block in one lowercase word, and its folder, its file and its root class share that name
- `name-modifier-with-base` - A modifier class always accompanies its block or element class, and a base class defined in CSS must be used

### 3. Color (CRITICAL)

- `color-tailwind-scales` - The palette is 50–950 scales with a DEFAULT step (primary, secondary and any additional brand scales, plus Tailwind status and neutral scales) plus white, used as flat tones, and nothing outside them
- `color-text-on-light` - All text on white uses the darkest secondary step; supporting text uses secondary-600 or, at minimum, the lightest step that measures 4.5:1; tinted backgrounds follow color-50-950-convention
- `color-50-950-convention` - In every scale, a -50 background takes -950 text and a -950 background takes -50 text; lower emphasis moves two steps toward the background; on secondary-800 and -900 blocks, text is white and lower emphasis secondary-200
- `color-brand-fill-only` - When the main brand color fails text contrast on light backgrounds, it is a fill there (buttons, tags, bands, squares), never text or an icon; text on it is the tone that passes the measured contrast
- `color-state-not-color-only` - Success, error, warning and information never rely on color alone; they always carry text or a sign, components that announce a state add the status icon, and each step of the status scale has a fixed role
- `color-measure-contrast` - Every text, icon and control color pair is checked numerically (4.5:1 text, 3:1 icons, control borders and large text) and the ratio is cited
- `color-cmyk-print` - Printed pieces use the CMYK values of the company palette sheet and convert every other tone with one documented formula

### 4. Surfaces and States (CRITICAL)

- `surf-no-shadows` - No shadow of any kind is used; every surface that needs separation gets a 1px border
- `surf-tinted-border-200` - A piece with a -50 or -100 background has a border of the same scale at step 200, including its inner dividers
- `surf-neutral-borders` - Pieces on white and every form control use neutral borders at fixed steps; controls stay neutral even on colored fills
- `surf-interaction-states` - Focus, hover and disabled states are system-wide constants, not per-component inventions

### 5. Brand Assets (CRITICAL)

- `brand-logo-variants` - The logo comes as a primary lockup and a symbol, each in fixed color variants, with text outlined and every derived format (PNG, favicon, app icons, manifest) generated from them
- `brand-logo-size-protection` - The logo keeps a clear space of 2X, never goes below its minimum screen and print sizes, and is never distorted, rotated or placed on the brand color
- `brand-graphic-devices` - Brand graphics (pattern, progression, scaled slogan) come from a logo feature, keep that feature's corners, never sit behind text, and only one is used per piece
- `brand-slogan-form` - The slogan keeps its exact wording, composed in two sizes at a 2–2.5 ratio and closed by a square brand-color dot where it works as a graphic, and as plain text with no period everywhere else
- `brand-imagery` - Photographs and illustrations follow documented selection criteria, record their source and license, and are named in BEM

### 6. Print Production (CRITICAL)

- `print-pdf-spec` - Every printed piece ships as a PDF at real size with 3 mm bleed, crop marks, CMYK colors, embedded fonts and trim and bleed boxes
- `print-minimum-sizes` - Printed text is never below 9pt, sizes are multiples of 3pt, and printed logos never go below their minimum height
- `print-real-size` - Print components are written at real size in CSS mm and pt, so the 4px = 3pt grid holds on every piece and the PDF needs no conversion; previews only enlarge them with zoom
- `print-pipeline` - Print PDFs are generated from the component previews by a scripted pipeline (HTML at real size, headless browser PDF, CMYK conversion, page boxes) and verified visually
- `print-dielines` - Die-cut slots, safe zones and reference areas are shown in previews as dashed neutral-400 marks and are excluded from print files

### 7. Foundations (HIGH)

- `found-single-typeface` - One open-licensed family by default (a second one for headings only when the brand defines it) covers headings, text and interface, in weights 400, 500 and 600, shipped as local WOFF2 files
- `found-type-roles` - Text uses a fixed set of roles (display to h5, lead, body, body-sm, label, caption, overline) on the Tailwind CSS size scale, with headings stepping down on mobile
- `found-single-light-theme` - The system has a single light theme by default, with dark surfaces only as contrast blocks inside it; a dark theme is added only when the user asks for it
- `found-spacing-radius` - Spacing uses the whole 4px steps of the Tailwind CSS scale and each radius step has an assigned use; brand graphics take the corner of the logo feature they derive from
- `found-grid-breakpoints-motion` - Layout follows the Tailwind CSS mobile-first breakpoints and a 4/8/12-column grid, and motion uses three durations that respect reduced motion
- `found-tailwind-theme` - A theme file for Tailwind CSS v4.3 loads the local fonts, replaces the default palette with the system scales and disables shadows

### 8. Writing and Voice (HIGH)

- `write-spanish-docs` - Documentation, interface copy and every human-facing name are in Spanish; code names and code comments stay in English
- `write-voice` - Brand copy keeps one form of address chosen with the user ("tú" or "usted"), speaks as "nosotros", avoids regionalisms and absolute promises, and follows fixed formats for dates, money, time, phones, percentages and decimals
- `write-inline-formatting` - In documentation, proper nouns go in italics; tones, hexadecimal and CMYK values, classes, tokens and file names go as inline code; measures, units and contrast ratios stay plain text
- `write-conclusion-titles` - Titles of report sections, charts and data slides say the finding, not the topic, and every figure carries its source

### 9. Iconography (HIGH)

- `icon-one-library` - All icons come from one open library at a pinned version; the system stores only the icons its components use and projects fetch any other icon on demand
- `icon-size-color` - Icons use three sizes, inherit the tone of their text, keep fixed gaps and carry an accessible name when they stand alone

### 10. Components (HIGH)

- `comp-catalog` - A brand design system ships a fixed set of component groups, from brand rules to communication pieces, so any derived design finds its building blocks
- `comp-documentation` - Each component has a Spanish documentation file (description, classes, measures or composition, Tailwind CSS equivalent when it applies, rules) and a preview
- `comp-overview` - The overview (the body of README.md) is the system's entry document, in Spanish, with the same sections in the same order for every brand; each section states the brand's decisions on its topic and links the component files that apply them
- `comp-tokens-bundle` - Component CSS lives in one bundle of BEM classes built only from tokens, plus a minimal script for interaction the HTML cannot provide
- `comp-accessibility` - Components use native elements and ARIA roles, give names to icon-only controls and charts, and support keyboard use
- `comp-charts` - Charts use up to five palette series in a fixed order, label series directly, start column and bar axes at zero and always cite a source

### 11. Communication Pieces (HIGH)

- `piece-print-family` - Business card, envelope, letterhead sheet and presentation folder share layout logic, graphic devices and typography so they read as one family
- `piece-contact-data` - Each piece carries a subset of the identity data chosen with the user, legal documents always keep tax ID and address, every value comes from the identity table, and data order and weights are consistent
- `piece-digital-documents` - Letterhead, quote, invoice and report pages reuse the print family decisions and keep legal and fiscal content intact
- `piece-email` - Signatures and newsletters use tables with inline styles, hex colors, hosted PNG logos and a font fallback, because email clients ignore stylesheets and SVG
- `piece-social-slides` - Social posts, profile banners and slide templates follow fixed formats, safe zones and one-idea-per-piece rules

### 12. Governance (HIGH)

- `gov-versioning` - Renaming or removing a token, class or file is major, adding is minor and fixing is patch, and each version is published with a dated Spanish changelog entry that names every touched class, file and asset
- `gov-assets-registry` - Every stored file is registered in the index and documented in its group file, replacements are swapped safely, and nothing unregistered or unused remains
- `gov-final-audit` - Before declaring the system finished, sweep files, classes, assets and conventions, fix every finding and publish the result as one version
- `gov-generated-files` - Files generated from the sources (tokens stylesheet, manifest, API pages, the generated tail of the overview) are rebuilt on every publish, and the index is published last

### 13. Reference Implementation (MEDIUM)

- `ref-askit` - The ASK TECHNOLOGY S.A.S. (ASKIT) system is the worked example of every rule; reuse its structure for new brands and its values only for ASKIT

## How to Use

Read individual rule files for detailed explanations and examples:

```plaintext
rules/*.md
```

Each rule contains a brief rationale, guidelines, an _Incorrect_ example, a _Correct_ example (often taken from the _ASKIT_ reference), and a reference.

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md` (generated — see `README.md`).
