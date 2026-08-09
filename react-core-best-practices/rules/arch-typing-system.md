---
title: TypeScript Type System & Domain Organization
impact: HIGH
description: Enforces a strict separation between application types (core/types) and library augmentations (core/typings), utilizing domain-based grouping and explicit type-only import/export syntax.
tags: architecture, core, types
---

## TypeScript Type System & Domain Organization

**Impact (HIGH):** A structured type system prevents circular dependencies and naming collisions. Separating external library overrides (`typings`) from business logic definitions (`types`) ensures that the application's contract remains clear. Enforcing `import type` and `export type` aids the compiler in tree-shaking and type erasure.

**Guidelines:**

1.  **Directory Separation:**
    - `core/types/`: Contains application-specific definitions grouped by domain (e.g., `users`, `products`)
    - `core/typings/`: Contains global overrides and module augmentations for third-party libraries (e.g., `axios.d.ts`, `environment.d.ts`)
2.  **Definition Strategy:**
    - **Interfaces:** Must be used for defining the shape of objects, especially _API_ responses and external services (extensible)
    - **Types:** Must be used for unions, intersections, mapped types (`Pick`, `Omit`), and aliases
3.  **Domain Grouping:**
    - A domain is a folder, always — `core/types/products/` — however few files it holds. The folder is the boundary, and a boundary does not appear and disappear with a file count
    - Every domain folder carries an `index.ts` barrel exporting its members, so consumers import the domain and never a file inside it. That indirection is the point: splitting `product.ts` later changes nothing at any call site
    - The folder is named for the domain in plural; the files inside are named for the entities they hold
    - This is deliberately not the threshold a component folder uses, where a second file is what earns the folder (see the component-structure rule). A component folder groups files that happen to belong together; a domain folder declares a boundary that exists whether or not it has been filled yet
4.  **Import/Export Syntax:**
    - **Imports:** Must use `import type { ... }` when importing interfaces or types
    - **Exports:** Must use `export type { ... }` in barrel files (`index.ts`)
5.  **Naming Convention:**
    - Do not prefix interfaces with `I`
    - Files should be named after the entity (e.g., `user.ts`) or the group (e.g., `cart.ts`)

**Incorrect (Flat structure, loose typing, value imports for types):**

```typescript
// ./core/types.ts

// Bad: Global file, mixing library overrides with app logic
declare module 'axios' { ... }

export type User = { id: string };
```

```typescript
// ./features/profile.tsx

// Bad: Importing a type as a value
import { User } from '~/core/types/users';
```

**Correct (Separated, Structured, Explicit Type Imports):**

```plaintext
./core/
├── types/
│   ├── config/                ← a folder even with one member beside its barrel
│   │   ├── index.ts
│   │   └── item.ts
│   └── products/
│       ├── index.ts
│       ├── product.ts
│       └── variant.ts
└── typings/
    ├── axios.d.ts
    └── environment.d.ts
```

```typescript
// ./core/types/products/product.ts

export interface Product {
  id: string;
  name: string;
  price: number;
}
```

```typescript
// ./core/types/products/index.ts

// Explicit type export
export type { Product } from './product';
```

```typescript
// ./app/products.tsx

// Explicit type import, reaching the domain through its barrel rather than the
// file inside it
import type { Product } from '~/core/types/products';
```

Reference: [TypeScript Handbook — Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)
