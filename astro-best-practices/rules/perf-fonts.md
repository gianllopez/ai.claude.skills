---
title: Fonts Through the Built-in API
impact: HIGH
description: Requires web fonts to be declared in the fonts config and rendered with the Font component, which self-hosts, subsets, preloads and generates fallbacks, instead of a third-party font CDN or hand-written face declarations.
tags: fonts, assets, performance, privacy, tailwind
---

## Fonts Through the Built-in API

**Impact (HIGH):** A web font is on the critical path for text, so every decision about it is a decision about when the page becomes readable. Loading one from a third-party font _CDN_ costs a _DNS_ lookup, a connection and a round trip to an origin the site does not control, before the first glyph can be requested — and it hands every visitor's request to that third party, which is a privacy question in several jurisdictions before it is a performance one. Hand-rolling the alternative is worse in a different direction: `@font-face` blocks written by hand routinely omit `font-display`, so text stays invisible while the file downloads, and omit a metric-matched fallback, so the page reflows when the real face arrives. The built-in _API_ makes all of that a config entry — it downloads and self-hosts the file, subsets it, generates the fallback, sets `font-display`, and emits the preload hint.

**Guidelines:**

1.  **Declare fonts in `fonts` in `astro.config.mjs`:**
    - Each entry names a `provider`, the family `name`, and the `cssVariable` the rest of the project will use
    - `fontProviders.fontsource()` and `fontProviders.google()` fetch at build time and self-host the result — the family comes from the provider, the bytes come from your own origin
    - A local file is declared the same way, so a licensed face and a public one are configured identically
2.  **Render `<Font />` once, in the base layout:**
    - It emits the `@font-face` rules and the preload hints for that variable
    - `preload` belongs on the face that renders above the fold, and only on that one — preloading every weight puts them all on the critical path and defeats the purpose
3.  **Consume the family through its variable, never by name:**
    - The `cssVariable` is the single reference. A stylesheet that also writes `font-family: 'Inter', sans-serif` by hand has a second source of truth that the config cannot keep correct
    - In a _TailwindCSS_ project this is the seam to the theme: the `@theme` token is defined as that variable, so `font-sans` resolves to the configured face — see the _TailwindCSS_ setup rule
4.  **Load the weights and styles the design uses, and no others:**
    - Each additional weight is another file; a variable font is usually one file covering the range
    - The design's actual set is a short list, and shipping the full family because it was easier is a cost paid on every first visit
5.  **What this replaces:**
    - `<link>` tags to a font _CDN_ in the document head
    - Hand-written `@font-face` blocks and the `font-display`, `unicode-range` and fallback-metric details that go with them
    - Font files committed to `public/` and referenced by _URL_

**Incorrect (third-party CDN, plus a hand-written face that reflows):**

```astro
---
// src/layouts/Base.astro
---

<head>
  <!-- Bad: DNS lookup, connection and round trip to an origin you do not
       control, before the first glyph is requested -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap"
    rel="stylesheet"
  />

  <style is:global>
    /* Bad: no font-display, so text is invisible while this downloads, and no
       metric-matched fallback, so the page reflows when it arrives */
    @font-face {
      font-family: 'Satoshi';
      src: url('/fonts/satoshi.woff2') format('woff2');
    }

    body {
      /* Bad: the family named by hand, in a second place */
      font-family: 'Inter', system-ui, sans-serif;
    }
  </style>
</head>
```

**Correct (declared once, self-hosted, consumed through its variable):**

```js
// astro.config.mjs
import { defineConfig, fontProviders } from 'astro/config';

export default defineConfig({
  fonts: [
    {
      name: 'Inter',
      cssVariable: '--font-inter',
      provider: fontProviders.fontsource(),
      // Only what the design uses
      weights: [400, 600],
      styles: ['normal'],
      subsets: ['latin'],
    },
  ],
});
```

```astro
---
// src/layouts/Base.astro
import { Font } from 'astro:assets';
import '../styles/global.css';
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <!-- preload only the face that renders above the fold -->
    <Font cssVariable="--font-inter" preload />
  </head>
  <body>
    <slot />
  </body>
</html>
```

```css
/* src/styles/global.css — the variable is the only reference to the family */
@import 'tailwindcss';

@theme {
  --font-sans: var(--font-inter), system-ui, sans-serif;
}
```

Reference: [Fonts](https://docs.astro.build/en/guides/fonts/)
