---
title: View Structure & Generated Code
impact: HIGH
description: Fixes where the view layer's own files live and holds the contract with the component generator, so a declared structure survives the next time someone runs it.
tags: architecture, structure, shadcn
---

## View Structure & Generated Code

**Impact (HIGH):** The layer boundary itself — `core/`, `shared/`, and the direction imports flow — belongs to `react-core-best-practices`, because none of it changes with the renderer. What is left here is what only the web has: a view layer with a design-system folder inside it, and a generator that writes files into the project on its own terms. Both decay the same way, and the second decays faster — a structure the generator does not know about is undone the first time someone runs `shadcn add`.

**Guidelines:**

1.  **The view layer splits by responsibility:**
    - `components/` holds reusable presentation, with the design-system primitives under `components/ui/`
    - `components/ui/` is the generator's target and nothing else lands there; a component the project wrote sits beside it, not inside it
    - That route modules compose and never fetch is the core skill's rule; this one only fixes where the components they arrange live
2.  **The tooling has to agree with the structure:**
    - `tsconfig` resolves `~/*` to the source root, and every generator reads the alias from there
    - `components.json` decides where the next generated file lands, so its aliases are part of the structure and not a detail
    - Its `tailwind` block is part of the same contract: `cssVariables: true` is what makes generated components read the semantic tokens instead of arriving with the palette baked in, and `baseColor` seeds those variables at generation time (see the theme-tokens rule)
    - Point `ui` and `components` at the view layer, `utils` at `~/core/lib/utils`, and `lib` and `hooks` into `~/core/lib/shadcn/`. The generator then writes the component into `components/ui/`, rewrites its `cn` import to our path, and drops everything else it brings — its own helpers and hooks — under `core/lib/shadcn/`
    - Its `hooks` alias deliberately does not point at `core/hooks/`: those are ours to edit, and anything the generator writes is not
3.  **`core/lib/shadcn/` is generated territory, and read-only:**
    - The folder is listed in `.prettierignore`, so the formatter never rewrites it — which means any diff inside it is a deliberate edit and never noise
    - Editing a file there is a review finding, however small the change: the file is regenerable and not ours, so the edit is silently lost the next time the generator writes over it
    - When the generated behavior is not what the project needs, add a module beside it — a new component or hook that wraps or replaces it — instead of patching in place
    - If the generated file genuinely has to change, promote it: move the behavior into a module the project owns, and stop pretending the generator still governs it

**Incorrect (a structure the generator does not know about, and a patched generated file):**

```json
// ./components.json
{
  "tailwind": {
    "css": "app/styles/app.css",
    "cssVariables": false
  },
  "aliases": {}
}
```

With `cssVariables: false` every component installed from then on ships with the palette baked in and the semantic layer stops existing; with no aliases the generator writes to its own defaults, so `shadcn add` undoes the project's layout on the next run.

```ts
// ./app/core/lib/shadcn/hooks/use-mobile.ts

// Bad: a deliberate edit inside generated territory. It is lost the next time
// the generator writes this file, and nothing warns anyone
const MOBILE_BREAKPOINT = 640;
```

**Correct (the generator writes where the project says, and what it wrote stays untouched):**

```plaintext
app/
├─ core/
│  └─ lib/
│     ├─ utils.ts                  ← cn(), the tailwind-merge adapter
│     └─ shadcn/                   ← whatever the generator brings besides components
│        └─ hooks/
│           └─ use-mobile.ts       ← generated, read-only
├─ components/
│  ├─ ui/
│  │  └─ button.tsx                ← the generator's target
│  └─ invoice-table.tsx            ← ours, beside it rather than inside it
└─ routes/
   └─ invoices.tsx
```

```json
// ./components.json — the generator has to know the structure, or it will not follow it
{
  "tailwind": {
    "css": "app/styles/app.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "aliases": {
    "components": "~/components",
    "ui": "~/components/ui",
    "utils": "~/core/lib/utils",
    "lib": "~/core/lib/shadcn",
    "hooks": "~/core/lib/shadcn/hooks"
  }
}
```

```tsx
// ./app/components/mobile-nav.tsx

// Good: the generated hook is consumed, never edited. A behavior the project
// needs differently gets a module of its own beside it
import { useIsMobile } from '~/core/lib/shadcn/hooks/use-mobile';

export function MobileNav() {
  const isMobile = useIsMobile();

  return isMobile ? <NavDrawer /> : <NavBar />;
}
```

Reference: [shadcn/ui components.json](https://ui.shadcn.com/docs/components-json)
