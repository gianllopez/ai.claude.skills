---
title: Tailwind CSS & Styling Standards
impact: HIGH
description: Enforces the use of NativeWind (className) over StyleSheet, strict usage of the classnames library for conditional logic, and theme constraints.
tags: architecture, styles
---

## Tailwind CSS & Styling Standards

**Impact (HIGH):** Unified styling via utility classes reduces bundle size (no _StyleSheet_ objects) and improves readability. Using a dedicated library for conditional classes prevents messy template literals and ensures consistent class resolution.

**Guidelines:**

1.  **Primary Styling Approach:**
    - Must use the `className` prop for all component styling.
    - The `style` prop is reserved strictly for dynamic values that _TailwindCSS_ cannot handle (e.g., interpolated animations, dynamic safe-area insets calculated at runtime) or 3rd party components not compatible with _NativeWind_.
2.  **Conditional Classes:**
    - Must use the `classnames` library for handling conditional logic.
    - **Forbidden:** Do not use template literals or string concatenation for classes (e.g., `` `flex-1 ${active ? 'bg-red' : ''}` ``).
3.  **Theme Restrictions:**
    - Must utilize the tokens defined in `./core/config/theme/colors.ts`.
    - Avoid arbitrary values (e.g., `bg-[#123456]`) unless absolutely necessary for one-off generic values.
4.  **Formatting:**
    - Class names must be sorted automatically via `prettier-plugin-tailwindcss`.

**Incorrect (StyleSheet usage, String interpolation, Arbitrary values):**

```typescript
// ./components/card.tsx

import { StyleSheet, View } from 'react-native';

// Bad: Using StyleSheet
const styles = StyleSheet.create({
  container: { padding: 16 },
  active: { backgroundColor: 'red' },
});

export function Card({ isActive }: { isActive: boolean }) {
  // Bad: String interpolation and arbitrary color
  return (
    <View
      style={styles.container}
      className={`rounded-lg ${isActive ? 'bg-[#ff0000]' : 'bg-white'}`}
    />
  );
}
```

**Correct (ClassName, Library utility, Theme tokens):**

```typescript
// ./components/card.tsx

import classNames from 'classnames';
import { View } from 'react-native';

export function Card({ isActive }: { isActive: boolean }) {
  // Good: Logic encapsulated in classNames
  return (
    <View
      className={classNames('rounded-lg p-4', {
        'bg-primary-500': isActive,
        'bg-white': !isActive,
      })}
    />
  );
}
```

Reference: [NativeWind](https://www.nativewind.dev/v4/overview)
