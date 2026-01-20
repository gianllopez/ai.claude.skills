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
    - `core/types/`: Contains application-specific definitions grouped by domain (e.g., `users`, `products`).
    - `core/typings/`: Contains global overrides and module augmentations for third-party libraries (e.g., `axios.d.ts`, `environment.d.ts`).
2.  **Definition Strategy:**
    - **Interfaces:** Must be used for defining the shape of objects, especially _API_ responses and external services (extensible).
    - **Types:** Must be used for unions, intersections, mapped types (`Pick`, `Omit`), and aliases.
3.  **Domain Grouping:**
    - Types must be grouped in folders matching their domain (e.g., `core/types/config/`).
    - Each domain folder must have an `index.ts` exporting its members.
4.  **Import/Export Syntax:**
    - **Imports:** Must use `import type { ... }` when importing interfaces or types.
    - **Exports:** Must use `export type { ... }` in barrel files (`index.ts`).
5.  **Naming Convention:**
    - Do not prefix interfaces with `I`.
    - Files should be named after the entity (e.g., `user.ts`) or the group (e.g., `cart.ts`).

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
import { User } from '@/core/types/users';
```

**Correct (Separated, Structured, Explicit Type Imports):**

```plaintext
./core/
├── types/
│   ├── config/
│   │   ├── index.ts
│   │   └── item.ts
│   └── products/
│       ├── index.ts
│       └── product.ts
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

// Explicit type import
import type { Product } from '@/core/types/products';
```
