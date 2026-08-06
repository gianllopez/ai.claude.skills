---
title: Folder Structure & Layer Boundary
impact: HIGH
description: Separates the core layer (data, configured libraries, domain types, helpers) from the view layer, and fixes where each kind of module lives.
tags: architecture, structure, boundaries
---

## Folder Structure & Layer Boundary

**Impact (HIGH):** Where a file lives is the cheapest documentation a codebase has, and the first thing that decays. Once a query hook lands next to a component and a domain type is declared inside a route, nobody can tell what depends on what, and the answer to "can I reuse this?" becomes "read it and find out". A declared structure also makes review possible: a misplaced file is a finding anyone can point at, while "this feels disorganized" is not.

**Guidelines:**

1.  **Three folders, imports in one direction:**
    - `core/` holds everything that is not the view: data access, configured libraries, domain types, pure helpers
    - `shared/` sits beside it and holds what no domain owns at all
    - The view layer — routes and components — imports from `core/`; `core/` never imports from the view
    - Both of them import from `shared/`, and `shared/` imports from neither: the moment something there reaches into `core/` it has picked a domain and stopped being shared
    - A file under `core/` that imports a component is a boundary violation, and usually means presentation leaked into logic
2.  **What lives under `core/` and `shared/`:**
    - `core/api/<domain>/` — one file per query or mutation hook (see the query-layer rule)
    - `core/hooks/` — hooks the project writes, with the `zustand` stores under `core/hooks/stores/`
    - `core/lib/` — third-party libraries that need initialization or configuration, and the adapters over them, once more than one module depends on that setup
    - `core/types/` — domain types, one file per domain, separate from any library's own typings
    - `core/helpers/` — own pure functions, with no third-party dependency
    - `shared/types/` — the shapes no domain owns: the API's response envelope, pagination, generic utilities. `core/types/` segments by domain, so filing these under `core/types/shared.ts` invents a domain called "shared" — which is the thing this folder exists to avoid
    - The line between `lib/` and `helpers/`: `lib/` wraps something external, `helpers/` depends on nothing
3.  **A module under `core/lib/` earns its place with a second consumer:**
    - The folder is where a third-party library is initialized, not where every third-party library gets a file of its own — when a single hook is the only place the package is ever touched, a module that sets a global and re-exports it is a boundary around a boundary
    - Until there is a second consumer — or an initialization that has to be guaranteed before either of two modules runs — the side effects live at the top of the one module that owns the library: the access token, the stylesheet, the locale
    - A re-export that transforms nothing is the tell. `export { AgGridReact } from 'ag-grid-react'` states a boundary the import path already stated, and everything the file adds is indirection
    - Adapters are the exception and earn the file at one consumer: a module that narrows the package's surface, renames it into the project's vocabulary, or holds configuration the library reads at call time is holding something of ours. `core/lib/axios.ts` with its interceptors is that; a re-export is not
    - The move is cheap, and that is the argument: the day a second module reaches for the package, the initialization goes to `core/lib/` and both import it. One commit, paid when the need is real instead of guessed
    - None of this licenses the opposite defect. The initialization still leaves the view layer: a route that imports a library's stylesheet on behalf of a hook three levels below it is the finding, and moving that import into the hook fixes it without a new module
4.  **Files are named in kebab case, whatever they export:**
    - `invoice-table.tsx` for a component, `use-invoices.ts` for a hook, `format.ts` for helpers — the casing never follows the export, so `InvoiceTable.tsx` is a finding even though the component inside it is `InvoiceTable`
    - One convention across the tree is what makes a path predictable before opening it, and it is what the generator already writes into `components/ui/`
    - Hooks under `core/api/` carry their own shape on top of this — `use-<members|action>.ts` (see the query-layer rule)
5.  **The root varies, the shape does not:**
    - Where `core/` sits depends on the technology and the layout it dictates
    - What must not vary between projects is what goes inside `core/` and which direction imports flow
    - The `~` alias resolves to that root, so every import inside the project reads the same regardless of which root it is
6.  **The view layer splits by responsibility:**
    - Route modules compose a screen: they read data through hooks and arrange components
    - `components/` holds reusable presentation, with the design-system primitives under `components/ui/`
    - A route module that declares a fetcher, or a component that reaches for `axios`, is in the wrong layer
7.  **The tooling has to agree with the structure:**
    - `tsconfig` resolves `~/*` to the source root, and every generator reads the alias from there
    - With `shadcn/ui`, `components.json` decides where the next generated file lands, so its aliases are part of the structure and not a detail
    - Its `tailwind` block is part of the same contract: `cssVariables: true` is what makes generated components read the semantic tokens instead of arriving with the palette baked in, and `baseColor` seeds those variables at generation time (see the theme-tokens rule)
    - Point `ui` and `components` at the view layer, `utils` at `~/core/lib/utils`, and `lib` and `hooks` into `~/core/lib/shadcn/`. The generator then writes the component into `components/ui/`, rewrites its `cn` import to our path, and drops everything else it brings — its own helpers and hooks — under `core/lib/shadcn/`
    - Its `hooks` alias deliberately does not point at `core/hooks/`: those are ours to edit, and anything the generator writes is not
    - A structure the generator does not know about is undone the first time someone runs `shadcn add`
8.  **`core/lib/shadcn/` is generated territory, and read-only:**
    - The folder is listed in `.prettierignore`, so the formatter never rewrites it — which means any diff inside it is a deliberate edit and never noise
    - Editing a file there is a review finding, however small the change: the file is regenerable and not ours, so the edit is silently lost the next time the generator writes over it
    - When the generated behavior is not what the project needs, add a module beside it — a new component or hook that wraps or replaces it — instead of patching in place
    - If the generated file genuinely has to change, promote it: move the behavior into a module the project owns, and stop pretending the generator still governs it

**Incorrect (layers mixed, types inline, data access inside the view):**

```plaintext
app/
├─ components/
│  ├─ invoice-table.tsx
│  ├─ use-invoices.ts        ← data access in the view layer
│  └─ invoice.ts             ← domain type next to a component
├─ routes/
│  └─ invoices.tsx           ← declares its own axios call
└─ utils.ts                  ← configured client and pure helpers in one file
```

```tsx
// ./app/routes/invoices.tsx

// Bad: the route builds its own request, so nothing else can reuse it
import axios from 'axios';

type Invoice = {
  id: string;
  total: number;
};

export default function InvoicesRoute() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  // ...
}
```

**Correct (core owns logic and data, the view composes it):**

```plaintext
app/
├─ core/
│  ├─ api/
│  │  └─ invoices/
│  │     ├─ use-invoices.ts
│  │     └─ use-mark-paid.ts
│  ├─ hooks/
│  │  └─ stores/
│  │     └─ settings.ts
│  ├─ lib/
│  │  ├─ axios.ts
│  │  ├─ utils.ts                  ← cn(), the tailwind-merge adapter
│  │  ├─ react-query/
│  │  │  ├─ client.ts
│  │  │  └─ middlewares.ts
│  │  └─ shadcn/                   ← whatever the generator brings besides components
│  │     └─ hooks/
│  │        └─ use-mobile.ts
│  ├─ types/
│  │  └─ invoices.ts               ← one file per domain
│  └─ helpers/
│     └─ format.ts
├─ shared/
│  └─ types/
│     └─ api.ts                    ← the response envelope, owned by no domain
├─ components/
│  ├─ ui/
│  │  └─ button.tsx
│  └─ invoice-table.tsx
└─ routes/
   ├─ protected-layout.tsx
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
// ./app/routes/invoices.tsx

import { useInvoices } from '~/core/api/invoices/use-invoices';
import { InvoiceTable } from '~/components/invoice-table';

// Good: the route reads through the hook and arranges components — nothing else
export default function InvoicesRoute() {
  const invoices = useInvoices({ variables: { status: 'open' } });

  return <InvoiceTable invoices={invoices.data} />;
}
```

**Incorrect (a `core/lib/` module with a single consumer, re-exporting what it received):**

```ts
// ./app/core/lib/ag-grid.ts

import { LicenseManager } from 'ag-grid-enterprise';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-quartz.css';

LicenseManager.setLicenseKey(import.meta.env.VITE_AG_GRID_KEY);

// Bad: nothing here is ours, and the only importer already owns the boundary
export { AgGridReact } from 'ag-grid-react';
```

```tsx
// ./app/components/invoice-grid.tsx — the only file that touches the grid

import { AgGridReact } from '~/core/lib/ag-grid';
```

**Correct (the initialization sits with the one module that owns the library):**

```tsx
// ./app/components/invoice-grid.tsx

import { LicenseManager } from 'ag-grid-enterprise';
import { AgGridReact } from 'ag-grid-react';
// Good: the stylesheets travel with the module that needs them, so no route imports them
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-quartz.css';

// Good: read once at module evaluation, before the grid can mount
LicenseManager.setLicenseKey(import.meta.env.VITE_AG_GRID_KEY);

type Props = { invoices: Invoice[] };

export function InvoiceGrid({ invoices }: Props) {
  return <AgGridReact rowData={invoices} className="ag-theme-quartz" />;
}
```

Reference: [shadcn/ui components.json](https://ui.shadcn.com/docs/components-json)
