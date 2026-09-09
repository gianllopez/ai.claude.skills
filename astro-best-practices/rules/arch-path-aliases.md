---
title: TypeScript Path Aliases
impact: LOW
description: Declares import aliases in tsconfig.json so modules are referenced by their place in the project rather than by a relative path that breaks when a file moves.
tags: typescript, imports, configuration, structure
---

## TypeScript Path Aliases

**Impact (LOW):** `../../../components/Card.astro` encodes the importing file's location into the import, so the import breaks when either file moves — and the failure is silent in the sense that a bulk move produces dozens of them at once, each fixed by counting directory levels. It also makes imports unreadable: a reader has to resolve the path mentally to learn what is being imported, and a reviewer cannot tell whether two files are importing the same module. Aliases are a few lines in `tsconfig.json` that _Astro_ and _Vite_ both honour, and they turn every import into a statement about where a module lives in the project rather than where it sits relative to the file quoting it. This is the lowest-impact rule here — nothing breaks in production because of it — but it is also the cheapest to adopt and the most annoying to retrofit.

**Guidelines:**

1.  **Declare the aliases in `tsconfig.json`:**
    - `baseUrl` set to the project root, and a `paths` entry per top-level directory the project imports from
    - _Astro_ reads this configuration through _Vite_, so no second declaration is needed for the bundler
2.  **One alias per meaningful directory, not one catch-all:**
    - `@components/*`, `@layouts/*`, `@lib/*`, `@styles/*` say something at the import site; a lone `@/*` restates the relative path with a different prefix
    - Keep a general `@/*` alongside them for the occasional module that fits nowhere, not as the primary mechanism
    - The alias set mirrors the directory conventions in the route-responsibility rule — if a new alias does not correspond to a real directory, the structure is the thing to fix
3.  **Use them consistently:**
    - A file that imports one sibling relatively and another by alias makes both harder to scan. Same-directory imports are the reasonable exception: `./Card.astro` beside the file that uses it is clearer than an absolute path
    - Content collection imports (`astro:content`) and built-in modules are not aliased; they are already absolute names
4.  **Apply them everywhere they work:**
    - Component and layout imports in `.astro` frontmatter, modules in `.ts` files, and imports inside framework components
    - `@styles/global.css` in a layout is the same idea: the stylesheet has a location in the project, not relative to whoever imports it

**Incorrect (relative chains that encode the importer's location):**

```astro
---
// src/pages/blog/tags/[tag].astro
import Layout from '../../../layouts/Base.astro';
import Card from '../../../components/ContentCard.astro';
import { formatDate } from '../../../lib/dates';
import '../../../styles/global.css';
---
```

**Correct (aliases declared once, imports readable anywhere):**

```json
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@layouts/*": ["src/layouts/*"],
      "@lib/*": ["src/lib/*"],
      "@styles/*": ["src/styles/*"]
    }
  }
}
```

```astro
---
// src/pages/blog/tags/[tag].astro — the same imports, from anywhere
import Layout from '@layouts/Base.astro';
import Card from '@components/ContentCard.astro';
import { formatDate } from '@lib/dates';
import '@styles/global.css';
---
```

Reference: [TypeScript in Astro](https://docs.astro.build/en/guides/typescript/)
