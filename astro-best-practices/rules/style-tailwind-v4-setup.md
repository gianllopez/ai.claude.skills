---
title: TailwindCSS v4 Setup & Theme Tokens
impact: HIGH
description: Installs TailwindCSS through the Vite plugin rather than the deprecated Astro integration, declares design tokens in the @theme block, and wires the font token to the variable the Fonts API generates.
tags: tailwind, styling, theme, tokens, vite
---

## TailwindCSS v4 Setup & Theme Tokens

**Impact (HIGH):** In v4 there are two ways to install _TailwindCSS_ in an _Astro_ project and only one of them is current: `@astrojs/tailwind` is the deprecated v3-era integration, and `@tailwindcss/vite` runs the engine inside _Vite_'s own pipeline. A project on the old path gets a separate _PostCSS_ pass, slower rebuilds, and configuration in a file that v4 no longer treats as the source of truth. That is the setup half. The token half is what the setup exists for: in v4 the theme **is** the stylesheet, so a declared token generates its utilities and exposes a _CSS_ variable at once, and every arbitrary value written at a call site is a design decision made outside that system. The _Astro_-specific seam is the font: the Fonts _API_ produces a variable, and the theme token has to be defined as that variable, or the project has two names for one typeface and no guarantee they agree.

**Guidelines:**

1.  **Install through _Vite_:**
    - `tailwindcss` and `@tailwindcss/vite`, registered as `vite: { plugins: [tailwindcss()] }` in `astro.config.mjs`
    - `@astrojs/tailwind` is deprecated. A project still listing it in `integrations` is on the v3 path and should migrate before anything else here applies
    - There is no `tailwind.config.js` by default; a _JS_ config returns only through `@config`, and only when a legacy plugin requires it
2.  **One global stylesheet, imported once:**
    - `@import 'tailwindcss'` at the top of `src/styles/global.css`, and that file imported in the base layout — not in each page, and not in each component
    - The base layout is the single entry point, which matches the route-responsibility rule: the layout owns what every page shares
3.  **Declare design decisions in `@theme`:**
    - Colors, radii, fonts, breakpoints, shadows and type steps live in the `@theme` block, and each token generates its utilities automatically — `--color-brand` yields `bg-brand`, `text-brand`, `border-brand`
    - The spacing scale is the exception and is not redeclared: `--spacing` is _Tailwind_'s, and redefining it changes every margin, gap and size at once
    - Size the token layer to the project. A plain `@theme` is a complete system for most sites; the variable-backed `:root` / `.dark` layer earns its indirection only where something reads it — a theme swap, or a component generator
4.  **Wire the font token to the Fonts _API_ variable:**
    - The `cssVariable` declared in the `fonts` config is the only reference to the family, and `--font-sans: var(--font-inter), system-ui, sans-serif` in `@theme` is what makes `font-sans` resolve to it
    - Naming the family again in _CSS_ creates a second source of truth the font config cannot keep correct
5.  **Arbitrary values are a review flag:**
    - `bg-[#1d4ed8]`, `p-[13px]`, `text-[15px]` mean either the token exists and was not used, or the token is missing and should be added
    - Genuinely one-off geometry — `grid-cols-[auto_1fr]`, a mask _URL_, a third-party offset — is legitimate. A color almost never is, and a spacing value never is
6.  **Let the formatter own class order:**
    - `prettier-plugin-tailwindcss` sorts class attributes, including in `.astro` files, so ordering is never a review comment
    - Conflicting utilities inside one string still resolve by stylesheet order rather than by intent, which sorting does not fix — that is a defect to remove, not to reorder
7.  **Where this skill stops:**
    - Class composition inside a _React_ island, and the merge-aware helper that makes it safe, belong to the _React_ skills a project loads alongside this one. What is stated here is the project's setup and its token layer

**Incorrect (deprecated integration, a JS config v4 does not read, tokens invented at the call site):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind'; // deprecated v3 integration

export default defineConfig({
  integrations: [tailwind()],
});
```

```js
// tailwind.config.js — not the source of truth in v4
module.exports = {
  theme: {
    extend: {
      colors: { brand: '#1d4ed8' },
      fontFamily: { sans: ['Inter', 'sans-serif'] },
    },
  },
};
```

```astro
---
// src/components/Badge.astro
---

<!-- Bad: the brand color and the spacing invented here, and the font family
     named a second time, disconnected from the Fonts API variable -->
<span
  class="rounded-[7px] bg-[#1d4ed8] px-[13px] py-[5px] text-[13px] text-white"
  style="font-family: 'Inter', sans-serif"
>
  <slot />
</span>
```

**Correct (Vite plugin, tokens in CSS, font wired to the generated variable):**

```js
// astro.config.mjs
import { defineConfig, fontProviders } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://example.com',
  vite: { plugins: [tailwindcss()] },
  fonts: [
    {
      name: 'Inter',
      cssVariable: '--font-inter',
      provider: fontProviders.fontsource(),
    },
  ],
});
```

```css
/* src/styles/global.css — the theme is the stylesheet */
@import 'tailwindcss';

@theme {
  /* The seam: the token is defined as the variable the Fonts API generates */
  --font-sans: var(--font-inter), system-ui, sans-serif;

  --color-brand: oklch(0.53 0.19 262);
  --color-brand-strong: oklch(0.44 0.19 262);
  --radius-badge: 0.4375rem;
  --text-badge: 0.8125rem;
}
```

```astro
---
// src/layouts/Base.astro — imported once, for the whole site
import { Font } from 'astro:assets';
import '@styles/global.css';
---

<html lang="en">
  <head>
    <Font cssVariable="--font-inter" preload />
  </head>
  <body class="font-sans">
    <slot />
  </body>
</html>
```

```astro
---
// src/components/Badge.astro — every value resolves through a token
---

<span
  class="text-badge rounded-badge bg-brand px-3 py-1 text-white"
>
  <slot />
</span>
```

Reference: [Install Tailwind CSS with Astro](https://tailwindcss.com/docs/installation/framework-guides/astro)
