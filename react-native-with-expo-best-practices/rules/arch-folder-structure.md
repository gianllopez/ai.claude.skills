---
title: Modular Project Structure
impact: HIGH
description: Enforces a strict separation of concerns using *Expo*, atomic/feature components, and a central core for business logic.
tags: architecture, folders
---

## Modular Project Structure

**Impact (HIGH):** Standardization ensures scalability. Separating specific framework logic (_Expo Router_ in `app/`) from business logic (`core/`) and UI (`components/`) allows for easier testing, reuse, and migration.

**Guidelines:**

1.  **Root Directory:**
    - `app/`: Contains **ONLY** _Expo Router_ files (`_layout`, `index`, `[id]`). No business logic here.
    - `components/`: Contains UI elements.
    - `core/`: Contains all non-UI logic.
2.  **Core Organization (`core/`):**
    - Logic must be categorized by type: `api/`, `config/`, `constants/`, `hooks/`, `i18n/`, `lib/`, `store/`, `theme/`, `types/`, and `utils/`.
    - **Types:** All TypeScript definitions reside in `core/types/` (grouped by domain like `entity`, `user`).
    - **API:** API services must be grouped by domain (e.g., `core/api/entity/`).
3.  **Component Organization (`components/`):**
    - **Feature Components:** Grouped by domain (e.g., `feature-sheet`, `entity-list`) containing their own sub-components if necessary.
    - **Atomic/Complex Components:** If a component has multiple variants, use the **Base/Presets Pattern**:
      - `base/`: Logic and containers (e.g., `touchable.tsx`).
      - `presets/`: Visual variants (e.g., `primary.tsx`, `secondary.tsx`).
      - `index.tsx`: Public exports.
4.  **Imports:** Use strict aliases (e.g., `@/core/api/...`) instead of relative paths for cross-module imports.

**Incorrect (Mixed concerns & unstructured):**

```typescriptreact
// ./app/index.tsx

// Bad: Defining API logic and Types inside a route
import { View, Text } from 'react-native';

interface Entity { id: string }

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
│   └── entity/
├── types/
│   └── entity/
./components/
├── complex-component/
│   ├── base/
│   ├── presets/
│   └── index.tsx
```

```typescriptreact
// ./app/(tabs)/index.tsx

import { EntityList } from '@/components/entity-list';
import { useEntity } from '@/core/api/entity';

export default function Screen() {
  const { data } = useEntity();

  return <EntityList data={data} />;
}
```
