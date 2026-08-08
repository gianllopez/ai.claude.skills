---
title: Modular Project Structure
impact: HIGH
description: Enforces a strict separation of concerns using Expo, atomic/feature components, and a central core for business logic.
tags: architecture, folders
---

## Modular Project Structure

**Impact (HIGH):** Standardization ensures scalability. Separating specific framework logic (_Expo Router_ in `app/`) from business logic (`core/`) and UI (`components/`) allows for easier testing, reuse, and migration.

**Guidelines:**

1.  **Root Directory:**
    - `app/`: Contains only _Expo Router_ files (`_layout`, `index`, `[id]`). No business logic here
    - `components/`: Contains UI elements
    - `core/`: Contains all non-UI logic
2.  **Core Organization (`core/`):**
    - Logic must be categorized by type: `api/`, `config/`, `constants/`, `hooks/`, `i18n/`, `lib/`, `store/`, `theme/`, `types/`, and `utils/`
    - **Types:** All _TypeScript_ definitions reside in `core/types/` (grouped by domain like `products`, `users`)
    - **API:** _API_ services must be grouped by domain (e.g., `core/api/products/`)
    - **Domain folders are plural:** they hold everything about the domain rather than one record, which is the opposite of the components that consume them (see the component-structure rule)
3.  **Component Organization (`components/`):**
    - **Feature Components:** Grouped by domain, and named with the entity in singular (e.g., `feature-sheet`, `product-list`) containing their own sub-components if necessary
    - **Atomic/Complex Components:** If a component has multiple variants, use the base/presets pattern:
      - `base/`: Logic and containers (e.g., `touchable.tsx`)
      - `presets/`: Visual variants (e.g., `primary.tsx`, `secondary.tsx`)
      - `index.ts`: Public exports
4.  **Imports:** Use strict aliases (e.g., `@/core/api/...`) instead of relative paths for cross-module imports

**Incorrect (Mixed concerns & unstructured):**

```typescript
// ./app/index.tsx

// Bad: Defining API logic and Types inside a route
import { View, Text } from 'react-native';

interface Product { id: string }

export default function Screen() {
  const fetchData = async () => { ... };
  return <View>...</View>;
}
```

```plaintext
./components/
└── ComplexButton.tsx (Flat structure for a component with many variants)
```

**Correct (Separated & Structured):**

```plaintext
./app/
├── (tabs)/
│   └── index.tsx  <-- Consumption only
./core/
├── api/
│   └── products/
├── types/
│   └── products/
./components/
├── complex-component/
│   ├── base/
│   ├── presets/
│   └── index.ts
```

```typescript
// ./app/(tabs)/index.tsx

import { ProductList } from '@/components/product-list';
import { useProducts } from '@/core/api/products';

export default function Screen() {
  const { data } = useProducts();

  return <ProductList data={data} />;
}
```
