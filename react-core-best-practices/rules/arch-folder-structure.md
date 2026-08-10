---
title: Folder Structure & Layer Boundary
impact: HIGH
description: Separates the core layer (data, configured libraries, domain types, helpers) from the view layer, and fixes where each kind of module lives regardless of what the view renders to.
tags: architecture, structure, boundaries
---

## Folder Structure & Layer Boundary

**Impact (HIGH):** Where a file lives is the cheapest documentation a codebase has, and the first thing that decays. Once a query hook lands next to a component and a domain type is declared inside a route, nobody can tell what depends on what, and the answer to "can I reuse this?" becomes "read it and find out". A declared structure also makes review possible: a misplaced file is a finding anyone can point at, while "this feels disorganized" is not.

The renderer changes none of this. A screen is a route module on both platforms, `core/` means the same thing on both, and the direction imports flow is a property of the architecture rather than of the _DOM_.

**Guidelines:**

1.  **Three folders, imports in one direction:**
    - `core/` holds everything that is not the view: data access, configured libraries, domain types, pure helpers
    - `shared/` sits beside it, at the same level, and holds what no domain owns at all
    - The view layer — routes and components — imports from `core/`; `core/` never imports from the view
    - Both of them import from `shared/`, and `shared/` imports from neither: the moment something there reaches into `core/` it has picked a domain and stopped being shared
    - A file under `core/` that imports a component is a boundary violation, and usually means presentation leaked into logic
2.  **What lives under `core/` and `shared/`:**
    - `core/api/<domain>/` — one file per query or mutation hook (see the query-layer rule)
    - `core/hooks/` — hooks the project writes, with the `zustand` stores under `core/hooks/stores/`
    - `core/lib/` — third-party libraries that need initialization or configuration, and the adapters over them, once more than one module depends on that setup
    - `core/types/<domain>/` — domain types, one folder per domain with an `index.ts` barrel (see the type-system rule)
    - `core/typings/` — augmentations for third-party libraries, which are not ours and do not belong beside the domains
    - `core/config/` — the constants the project agrees on, and nothing that has to be computed (see the core-utilities rule)
    - `core/helpers/` — our own functions, which use what is already configured instead of configuring it. Importing a third-party package is fine; owning its setup is what sends a module to `lib/`
    - `shared/types/` — the shapes no domain owns: the API's response envelope, pagination, generic utilities. `core/types/` segments by domain, so filing these under `core/types/shared/` invents a domain called "shared" — which is the thing this folder exists to avoid
    - The line between `lib/` and `helpers/`: `lib/` owns a library's configuration, `helpers/` consumes it. Neither is decided by whether the file imports a package
3.  **A module under `core/lib/` earns its place with a second consumer:**
    - The folder is where a third-party library is initialized, not where every third-party library gets a file of its own — when a single hook is the only place the package is ever touched, a module that sets a global and re-exports it is a boundary around a boundary
    - Until there is a second consumer — or an initialization that has to be guaranteed before either of two modules runs — the side effects live at the top of the one module that owns the library: the access token, the stylesheet, the locale
    - A re-export that transforms nothing is the tell. A line that only forwards what it imported states a boundary the import path already stated, and everything the file adds is indirection
    - Adapters are the exception and earn the file at one consumer: a module that narrows the package's surface, renames it into the project's vocabulary, or holds configuration the library reads at call time is holding something of ours. `core/lib/axios.ts` with its interceptors is that; a re-export is not
    - The move is cheap, and that is the argument: the day a second module reaches for the package, the initialization goes to `core/lib/` and both import it. One commit, paid when the need is real instead of guessed
    - None of this licenses the opposite defect. The initialization still leaves the view layer: a route that imports a library's setup on behalf of a hook three levels below it is the finding, and moving that import into the hook fixes it without a new module
4.  **Files are named in kebab case, whatever they export:**
    - `invoice-table.tsx` for a component, `use-invoices.ts` for a hook, `format.ts` for helpers — the casing never follows the export, so `InvoiceTable.tsx` is a finding even though the component inside it is `InvoiceTable`
    - One convention across the tree is what makes a path predictable before opening it
    - Hooks under `core/api/` carry their own shape on top of this — `use-<members|action>.ts` (see the query-layer rule)
    - Names stay singular for components and plural for domains, and a filename never repeats its folder (see the component-structure rule)
5.  **The root varies, the shape does not:**
    - Where `core/` sits depends on the technology and the layout it dictates — beside the router's directory on one platform, inside it on another
    - What must not vary between projects is what goes inside `core/` and which direction imports flow
    - The `~` alias resolves to that root, so every import reads the same regardless of which root it is. The prefix is the one part a platform may configure; everything after it does not move
6.  **Route modules compose, they do not fetch:**
    - A route module reads data through hooks and arranges components — that is its whole job
    - A route that declares a fetcher, or a component that reaches for `axios`, is in the wrong layer
    - What the router calls that module, and what the view renders to, is the platform's business and not this rule's — the view-structure rule on the web, the app-directory rule under _Expo_

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
│  │  └─ react-query/
│  │     ├─ client.ts
│  │     └─ middlewares.ts
│  ├─ types/
│  │  └─ invoices/                 ← one folder per domain, reached through its barrel
│  │     ├─ index.ts
│  │     └─ invoice.ts
│  ├─ typings/
│  │  └─ axios.d.ts
│  ├─ config/
│  │  └─ constants.ts
│  └─ helpers/
│     └─ format.ts
├─ shared/
│  └─ types/
│     └─ api.ts                    ← the response envelope, owned by no domain
└─ components/
   └─ invoice-table.tsx
```

Everything above is identical on both platforms. What differs is only where the router's own directory sits and what a route module is called, which each platform's own folder-structure rule states.

**Correct (React DOM):**

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

**Correct (React Native):**

```tsx
// ./app/(tabs)/invoices.tsx

import { useInvoices } from '~/core/api/invoices/use-invoices';
import { InvoiceTable } from '~/components/invoice-table';

// Good: same job, same import paths — only the router's directory differs
export default function InvoicesScreen() {
  const invoices = useInvoices({ variables: { status: 'open' } });

  return <InvoiceTable invoices={invoices.data} />;
}
```

**Incorrect (a `core/lib/` module with a single consumer, re-exporting what it received):**

```ts
// ./app/core/lib/chart.ts

import { LicenseManager } from 'chart-vendor-enterprise';

LicenseManager.setLicenseKey(CHART_KEY);

// Bad: nothing here is ours, and the only importer already owns the boundary
export { Chart } from 'chart-vendor';
```

**Correct (the initialization sits with the one module that owns the library):**

```tsx
// ./app/components/invoice-chart.tsx — the only file that touches the vendor

import { LicenseManager } from 'chart-vendor-enterprise';
import { Chart } from 'chart-vendor';

// Good: read once at module evaluation, before the chart can mount
LicenseManager.setLicenseKey(CHART_KEY);

type Props = { invoices: Invoice[] };

export function InvoiceChart({ invoices }: Props) {
  return <Chart data={invoices} />;
}
```

Reference: [Thinking in React](https://react.dev/learn/thinking-in-react)
