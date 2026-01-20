---
title: Component Structure & Composition
impact: HIGH
description: Enforces function declarations, named exports, and specific folder structures for integral, grouped, and complex (base/preset) components.
tags: architecture, components
---

## Component Structure & Composition

**Impact (HIGH):** Standardization of component definition improves debuggability (hoisting) and refactoring. The separation of base logic from preset visuals ensures a scalable design system where logic is centralized and variants are easy to compose.

**Guidelines:**

1.  **Definition Syntax:**
    - Must use function declarations (`export function Name() {}`).
    - Must use named exports exclusively (No `export default`).
    - Arrow functions are forbidden for top-level components.
2.  **Props Definition:**
    - Must use `type Props = { ... }`.
    - If exported, rename to `ComponentNameProps`.
3.  **File Structure Strategy:**
    - **Integral Component:** Single file (`components/my-component.tsx`) if it has no sub-components.
    - **Grouped Component:** Directory with `index.tsx` (main) and helper files (e.g., `item.tsx`). Helper components must have generic names internal to the folder but specific implementation details.
    - **Complex Component (base/presets):** For components with multiple variants (e.g., _Buttons_, _Inputs_), strictly follow the respective pattern.
      - `base/`: Contains the logic container (state, theme injection, layout). Uses `render` props to pass data to children.
      - `presets/`: Contains visual implementations consuming the `base`.
      - `index.ts`: Multiple barrel files to control visibility.

**Incorrect (Arrow functions, Defaults, Flat logic):**

```typescript
// ./components/button.tsx

// Bad: Flat structure for complex logic, Arrow function, Default export
const Button = ({ theme, ...props }) => { ... };
export default Button;
```

**Correct (Integral & Grouped):**

```plaintext
./components/products-list/
├── index.tsx (Exports `ProductsList`)
└── item.tsx  (Internal generic naming)
```

**Correct (Complex - Base/Presets Pattern):**

```plaintext
./components/button/
├── base/
│   ├── button-container.tsx (Logic & Layout)
│   └── index.ts
├── presets/
│   ├── button-text.tsx (Variant 1)
│   ├── button-icon.tsx (Variant 2)
│   └── index.ts
└── index.ts (Global Exports)
```

```typescript
// ./components/button/base/button-container.tsx

import { View } from 'react-native';
import colors from '@/core/config/theme/colors';

type Props = {
  tone?: keyof typeof colors;
  render: (color: string) => React.ReactNode; // Inversion of Control
};

export function ButtonContainer({ tone = 'primary', render, ...rest }: Props) {
  const color = colors[tone][500];
  // Logic (Loading, Press state) lives here
  return (
    <View className="rounded-xl">
      {render(color)}
    </View>
  );
}
```

```typescript
// ./components/button/presets/button-text.tsx

import { ButtonContainer } from '../base';

export function ButtonText({ children, ...rest }: Props) {
  // Preset strictly handles presentation/composition
  return (
    <ButtonContainer
      {...rest}
      render={(color) => (
        <Text style={{ color }}>{children}</Text>
      )}
    />
  );
}
```
