---
title: TailwindCSS v4 Setup & Font Wiring
impact: HIGH
description: Installs TailwindCSS through the Vite plugin rather than the deprecated Astro integration, imports the stylesheet once from the base layout, and wires the theme's font token to the variable the Fonts API generates.
tags: tailwind, styling, vite, fonts
---

## TailwindCSS v4 Setup & Font Wiring

**Impact (HIGH):** In v4 there are two ways to install _TailwindCSS_ in an _Astro_ project and only one of them is current: `@astrojs/tailwind` is the deprecated v3-era integration, and `@tailwindcss/vite` runs the engine inside _Vite_'s own pipeline. A project on the old path gets a separate _PostCSS_ pass, slower rebuilds, and configuration in a file that v4 no longer treats as the source of truth. The theme itself — what belongs in `@theme`, how the token layer is sized, when arbitrary values are a defect — is framework-agnostic and lives in `html-best-practices`; what is _Astro_-specific is the installation path and one seam the framework itself creates: the Fonts _API_ produces a _CSS_ variable, and the theme's font token has to be defined as that variable, or the project has two names for one typeface with no guarantee they agree.

**Guidelines:**

1.  **Install through _Vite_:**
    - `tailwindcss` and `@tailwindcss/vite`, registered as `vite: { plugins: [tailwindcss()] }` in `astro.config.mjs`
    - `@astrojs/tailwind` is deprecated. A project still listing it in `integrations` is on the v3 path and should migrate before anything else here applies
    - There is no `tailwind.config.js` by default; a _JS_ config returns only through `@config`, and only when a legacy plugin requires it
2.  **One global stylesheet, imported once:**
    - `@import 'tailwindcss'` at the top of `src/styles/global.css`, and that file imported in the base layout — not in each page, and not in each component
    - The base layout is the single entry point, which matches the route-responsibility rule: the layout owns what every page shares
3.  **Wire the font token to the Fonts _API_ variable:**
    - The `cssVariable` declared in the `fonts` config is the only reference to the family, and `--font-sans: var(--font-inter), system-ui, sans-serif` in `@theme` is what makes `font-sans` resolve to it
    - Naming the family again in _CSS_ creates a second source of truth the font config cannot keep correct
4.  **Where this skill stops:**
    - The `@theme` block's own contents, the arbitrary-values review flag, and class-attribute formatting belong to `html-best-practices`, which a _TailwindCSS_-using _Astro_ project loads alongside this one. What is stated here is the installation path and the one wiring seam that only exists because this is _Astro_

**Incorrect (deprecated integration, a JS config v4 does not read, the font named a second time):**

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
      fontFamily: { sans: ['Inter', 'sans-serif'] },
    },
  },
};
```

```astro
---
// src/components/Badge.astro
---

<!-- Bad: the font family named a second time, disconnected from the Fonts
     API variable -->
<span class="rounded-badge bg-brand px-3 py-1 text-badge text-white" style="font-family: 'Inter', sans-serif">
  <slot />
</span>
```

**Correct (Vite plugin, one stylesheet import, font wired to the generated variable):**

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
// src/components/Badge.astro — the font resolves through the token, not a
// second declaration
---

<span class="text-badge rounded-badge bg-brand px-3 py-1 text-white">
  <slot />
</span>
```

Reference: [Install Tailwind CSS with Astro](https://tailwindcss.com/docs/installation/framework-guides/astro)
