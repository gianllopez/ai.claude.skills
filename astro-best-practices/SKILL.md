---
name: astro-best-practices
description: Standards for production Astro 7 websites — static output by default, .astro components before framework components, hydration directives matched to a component's position, typed content through the Content Layer API, SEO generated from the content schema, the built-in image, font, prefetch and view-transition APIs, TailwindCSS v4 theming in CSS, and the version, environment and CSP configuration a project needs. Use when writing or reviewing .astro files, astro.config.mjs, content collections and their schemas, client:* directives, route and layout structure, or a project's SEO, asset and deployment configuration. In a project that uses React islands, react-core-best-practices loads alongside this skill and owns everything inside those components.
license: MIT
metadata:
  author: gianllopez
  version: 1.0.0
---

# Astro Best Practices

Standards for building production websites with _Astro_, where nearly every decision that matters reduces to one question: how much of this page has to reach the browser as _JavaScript_? _Astro_ answers it well by default — it renders _HTML_ at build time and ships nothing else until you ask — so most defects in an _Astro_ codebase are not things the framework did, they are defaults that were opted out of without a reason.

That shape is what these rules encode. Static output unless a page proves it needs the server. An `.astro` component unless interactivity proves it needs a framework. `client:visible` unless position proves it needs `client:load`. A typed collection unless content proves it needs a _CMS_. In each pair the first is free and the second is paid for, and the rule is not "never pay" — it is that the payment is a decision someone made, visible in the diff, rather than a default nobody questioned.

Every rule names a defect concrete enough to point at in a diff — a `<img>` where `<Image />` applies, a `client:load` on a component below the fold, a collection without a `loader`, two trailing-slash conventions in one site — and shows the correct shape beside it. That is what makes the same rule usable in both directions: the **Correct** block is what to write, the defect is what to look for.

**Reference version: Astro 7.** The framework moves fast and its recent majors removed real _APIs_ — `Astro.glob()`, legacy content collections, `<ViewTransitions />`, `@astrojs/db`. Every rule that names a config key, import path or component states the version it belongs to, so the guidance degrades into a stale reference rather than silently teaching a removed _API_. Where a rule's intent outlives its _API_, the intent is stated first and the _API_ second.

**Scope.** The framework and what it emits. In a project that renders _React_ islands, `react-core-best-practices` loads alongside this skill and owns what happens inside those components — effects, state, the query layer, composition and typing; this skill owns only the boundary: whether the island should exist and how it hydrates. Visual design direction is deliberately out of scope — it is not verifiable against a diff — and so is accessibility auditing, matching the call `react-best-practices` already makes: semantic and structural rules here are justified by machine-readability and maintainability instead.

## When to Apply

Reference these guidelines when:

- Deciding whether a page renders at build time or on demand, or adding an adapter
- Writing a component, and choosing between `.astro` and a framework component
- Adding a `client:*` directive, or reviewing one that is already there
- Defining a content collection, its `loader`, or its schema
- Adding metadata, canonicals, a sitemap, a feed, redirects or structured data
- Placing an image, a font, an embed or a third-party tag on a page
- Deciding where a route, layout or component file lives, or what a route file may contain
- Setting up _TailwindCSS_ in an _Astro_ project, or writing component styles
- Touching `astro.config.mjs` — i18n, logging, environment variables, _CSP_, deployment target

## Rule Categories by Priority

| Priority | Category              | Peak impact | Prefix     |
| :------- | :-------------------- | :---------- | :--------- |
| 1        | Rendering & Hydration | CRITICAL    | `isl-`     |
| 2        | Content Model         | CRITICAL    | `content-` |
| 3        | SEO System            | CRITICAL    | `seo-`     |
| 4        | Assets & Performance  | HIGH        | `perf-`    |
| 5        | Project Structure     | HIGH        | `arch-`    |
| 6        | Styling               | HIGH        | `style-`   |
| 7        | Build & Configuration | HIGH        | `build-`   |

Priority orders where to look first; peak impact is the strongest rule in the section, matching the table of contents in `AGENTS.md`. They disagree on purpose — a section can hold one blocking rule and several that only ever produce suggestions.

## Quick Reference

### 1. Rendering & Hydration (CRITICAL)

- `isl-static-by-default` - `output: 'static'` stated explicitly; on-demand rendering opted into per route, never globally by accident
- `isl-astro-components-first` - `.astro` until interactivity proves otherwise; a framework component is a decision, not a habit
- `isl-hydration-directives` - The directive matches the component's position; the island boundary wraps what is interactive, not the section around it

### 2. Content Model (CRITICAL)

- `content-collections-required` - Content Layer API: `src/content.config.ts`, every collection with a `loader`, entries keyed by `id`
- `content-schema-contract` - The schema is where a required field becomes a build failure; validation at build time, not a missing tag in production
- `content-authoring-format` - Markdown for text, MDX only when components are needed; `<Code />` for build-time-dynamic code; the processor configured for v7

### 3. SEO System (CRITICAL)

- `seo-site-and-canonical` - `site` is always set; canonicals and metadata come from shared helpers, never hand-built per page
- `seo-url-hygiene` - One trailing-slash convention; old URLs redirected before launch and internal links pointing at final targets
- `seo-sitemap-and-feeds` - Only canonical, indexable URLs; drafts, previews and redirect sources excluded; last-modified dates never faked
- `seo-structured-data` - JSON-LD generated from the content model, describing what is actually on the page

### 4. Assets & Performance (HIGH)

- `perf-images` - `<Image />` / `<Picture />` over raw `<img>`; explicit dimensions, deliberate LCP handling, lazy below the fold
- `perf-fonts` - The built-in Fonts API self-hosts, subsets and preloads; no third-party font CDN
- `perf-third-party-scripts` - No global tags by default; embeds scoped to the pages that need them
- `perf-navigation` - Built-in `prefetch` and `<ClientRouter />`; transitions expressed in CSS rather than a JavaScript animation runtime

### 5. Project Structure (HIGH)

- `arch-route-responsibility` - Route files assemble; layouts own repeated structure and expose it through slots
- `arch-component-reuse` - Extract what repeats, keep what is genuinely one-off local; neither copy-paste nor abstraction for its own sake
- `arch-path-aliases` - Aliases declared in `tsconfig.json`, not `../../../` chains
- `arch-markup-discipline` - Under the v7 compiler unclosed tags are build errors and whitespace is compressed; markup correctness is now a build concern

### 6. Styling (HIGH)

- `style-tailwind-v4-setup` - `@tailwindcss/vite`, never the deprecated `@astrojs/tailwind`; tokens declared in `@theme`, wired to the Fonts API variable
- `style-scoped-css` - Component styles stay scoped; `is:global` is an escape hatch that names its reason

### 7. Build & Configuration (HIGH)

- `build-i18n-day-one` - Configured before routes exist; internal links built with `getRelativeLocaleUrl()`
- `build-logging` - `Astro.logger` and the stable top-level `logger` field over `console.log`
- `build-env-and-csp` - `astro:env` types the environment and keeps secrets server-side; CSP is configured, not omitted
- `build-deployment-target` - Static output to an edge CDN; the adapter, output mode and toolchain floor stated explicitly

## How to Use

Read individual rule files for detailed explanations and code examples:

```plaintext
rules/*.md
```

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md` (generated — see `README.md`).
