---
title: The App Directory & Expo Router
impact: HIGH
description: Fixes what belongs to the Expo Router directory, how feature components are grouped, and the alias every cross-module import resolves through.
tags: architecture, folders, expo
---

## The App Directory & Expo Router

**Impact (HIGH):** The layer boundary itself — `core/`, `shared/`, what lives inside each, and the direction imports flow — belongs to `react-core-best-practices`, because none of it changes with the renderer. What is left here is the part _Expo Router_ dictates: a directory whose file names **are** the navigation graph, so anything filed there that is not a route quietly becomes one.

**Guidelines:**

1.  **`app/` is the navigation graph, not a folder:**
    - It holds only _Expo Router_ files — `_layout`, `index`, `[id]`, and the group directories in parentheses. No business logic, no helpers, no types
    - A file placed there is a route whether or not it was meant to be one: that is what makes this stricter than an ordinary view folder
    - Route modules take a `default` export, which the router requires. That is the one place the named-export convention gives way, and it applies to nothing else in the project
2.  **`components/` groups by domain:**
    - Feature components are grouped by domain and named with the entity in singular — `product-list`, `feature-sheet` — containing their own sub-components when they have them
    - How one component's own files are organized, including the base/presets pattern, is the component-structure rule in `react-core-best-practices`
3.  **Imports resolve through the alias, never relatively:**
    - `~/core/api/products`, never a chain of `../..` — the prefix is `~/` here as in every project this collection governs, and the path after it does not vary by platform
    - _Expo_ scaffolds `@/` by default, so this is configured once in `tsconfig` and in the _Babel_ module resolver rather than inherited

**Incorrect (business logic inside the navigation graph, relative imports):**

```typescript
// ./app/index.tsx

// Bad: an API call and a domain type declared inside a route, so nothing else
// can reuse either and the file does two jobs
import { View, Text } from 'react-native';

interface Product {
  id: string;
}

export default function Screen() {
  const fetchData = async () => { ... };

  return <View>...</View>;
}
```

```typescript
// ./app/(tabs)/products.tsx

// Bad: a hop instead of a destination, and it breaks when the file moves
import { ProductList } from '../../components/product-list';
```

**Correct (the graph only routes, and everything else is reached by alias):**

```plaintext
./app/
├── _layout.tsx
└── (tabs)/
    └── index.tsx        <-- consumption only
./core/
├── api/
│   └── products/
└── types/
    └── products/
./shared/
└── types/
    └── api.ts           <-- the response envelope, owned by no domain
./components/
├── product-list/
│   ├── index.ts
│   ├── list.tsx
│   └── item.tsx
└── button/
    ├── base/
    ├── presets/
    └── index.ts
```

```typescript
// ./app/(tabs)/index.tsx

import { ProductList } from '~/components/product-list';
import { useProducts } from '~/core/api/products';

// Good: the route reads through the hook and arranges components — nothing else.
// `default` because the router requires it, which is this file's one exception
export default function Screen() {
  const products = useProducts();

  return <ProductList data={products.data} />;
}
```

Reference: [Expo Router](https://docs.expo.dev/router/introduction/)
