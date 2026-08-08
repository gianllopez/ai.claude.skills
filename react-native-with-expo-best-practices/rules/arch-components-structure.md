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
    - Must use function declarations (`export function Name() {}`)
    - Must use named exports exclusively (No `export default`)
    - Arrow functions are forbidden for top-level components
2.  **Props Definition:**
    - Must use `type Props = { ... }`
    - If exported, rename to `ComponentNameProps`
3.  **File Structure Strategy:**
    - **Integral Component:** Single file (`components/my-component.tsx`) if it has no sub-components
    - **Grouped Component:** Directory where every component has its own file (`list.tsx`, `item.tsx`) and an `index.ts` barrel states which of them are public. Never `index.tsx`: the barrel only re-exports, so it holds no JSX and no component lives inside it
    - **Complex Component (base/presets):** For components with multiple variants (e.g., _Buttons_, _Inputs_), strictly follow the respective pattern
      - `base/`: Contains the logic container (state, theme injection, layout). Uses `render` props to pass data to children
      - `presets/`: Contains visual implementations consuming the `base`
      - `index.ts`: Multiple barrel files to control visibility
4.  **Names stay singular, and never repeat the folder:**
    - The entity in a component's name is singular whatever the component renders — `ProductList`, `ProductRow`, `ProductCard`. The suffix already carries the plurality, so `ProductsList` states it twice
    - Singular is what keeps a family consistent: with a plural prefix the name changes shape depending on the suffix — `ProductsList` beside `ProductRow` — and there is no convention left, only a decision to make per component
    - Domain folders are the opposite and stay plural: `core/api/products/` holds everything about the domain rather than one product
    - Inside `presets/`, the file is named after what distinguishes that variant and nothing else — `text.tsx`, `icon.tsx`, never `button-text.tsx`
    - The path already states the parent: `button/presets/text.tsx` reads the parent twice when the file carries the prefix, and every rename of the component turns into a rename of every file under it
    - Only the filename drops the prefix. The component it exports keeps its full name — `presets/text.tsx` exports `ButtonText`, because that name is read at the call site where no folder is in view

**Incorrect (Arrow functions, Defaults, Flat logic):**

```typescript
// ./components/button.tsx

// Bad: Flat structure for complex logic, Arrow function, Default export
const Button = ({ theme, ...props }) => { ... };
export default Button;
```

**Correct (Integral & Grouped):**

```plaintext
./components/product-list/
├── index.ts   (Barrel — exports `ProductList` and nothing else)
├── list.tsx   (Exports `ProductList`)
└── item.tsx   (Exports `ProductItem`, rendered only by its sibling)
```

**Correct (Complex - Base/Presets Pattern):**

```plaintext
./components/button/
├── base/
│   ├── button-container.tsx (Logic & Layout)
│   └── index.ts
├── presets/
│   ├── text.tsx  (Variant 1 — exports `ButtonText`)
│   ├── icon.tsx  (Variant 2 — exports `ButtonIcon`)
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
// ./components/button/presets/text.tsx

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
