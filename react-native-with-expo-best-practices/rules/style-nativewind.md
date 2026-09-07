---
title: NativeWind Styling Standards
impact: HIGH
description: Requires className over StyleSheet, restricts the style prop to what utilities cannot express, and keeps colours in the theme instead of raw hex values in components.
tags: architecture, styles, nativewind
---

## NativeWind Styling Standards

**Impact (HIGH):** _React Native_ gives you two styling systems and they do not compose. A screen that mixes `StyleSheet` objects with `className` has two places to look for why something is the colour it is, and the answer depends on a specificity order neither file states. Committing to one — and reserving the other for what it alone can do — is what keeps that answer in one place.

_How_ conditional classes are composed is not this rule's business: `cn()` and the ban on interpolated class names are in the class-composition rule of `react-core-best-practices`, and they hold here for exactly the reason they hold on the web, since _NativeWind_ resolves `className` by CSS specificity rather than by source order.

**Guidelines:**

1.  **`className` is the styling layer:**
    - Every component styles through `className`; a `StyleSheet.create` in new code is a finding
    - The bundle is smaller for it — no style objects survive to runtime — but the real gain is that one file answers what a component looks like
2.  **The `style` prop is for what utilities cannot express:**
    - A value computed at runtime: an interpolated animation, a safe-area inset measured on the device, a transform driven by a gesture
    - A third-party component _NativeWind_ does not wrap, which never receives `className` at all
    - Anything else in `style` is a utility that was not looked up
3.  **Colours come from the theme:**
    - `core/config/theme/colors.ts` maps the palette to semantic names, and components reach those names — never a raw hex
    - A hex in a component is a decision made outside the design system: the day the brand colour changes, it is a find-and-replace that will miss two
    - The `base/` container of a component is where a resolved colour legitimately enters _JavaScript_, because a preset needs the value rather than the class (see the component-structure rule in `react-core-best-practices`)
4.  **Formatting is the formatter's job:**
    - `prettier-plugin-tailwindcss` sorts every class attribute; class order is never a review comment

**Incorrect (StyleSheet beside className, a raw hex, a utility hiding in the style prop):**

```typescript
// ./components/product-card.tsx

import { StyleSheet, View } from 'react-native';

// Bad: a second styling system, so the answer to "why is this padded" is in
// two files and resolves by an order neither of them states
const styles = StyleSheet.create({
  container: { padding: 16 },
});

export function ProductCard({ isActive }: Props) {
  return (
    <View
      style={[styles.container, { backgroundColor: '#e43636' }]}
      className="rounded-lg"
    />
  );
}
```

**Correct (one styling layer, theme colours, `style` only for the runtime value):**

```typescript
// ./core/config/theme/colors.ts

export default {
  primary: { 500: '#2563eb' },
  danger: { 500: '#e43636' },
};
```

```typescript
// ./components/product-card.tsx

import { View } from 'react-native';
import { cn } from '~/core/lib/utils';

export function ProductCard({ isActive }: Props) {
  return (
    <View
      className={cn('rounded-lg p-4', isActive ? 'bg-primary-500' : 'bg-white')}
    />
  );
}
```

```typescript
// ./components/sheet.tsx

import { useSafeAreaInsets } from 'react-native-safe-area-context';

export function Sheet({ children }: Props) {
  const insets = useSafeAreaInsets();

  return (
    // Good: the inset is measured on the device, so no utility can express it.
    // Everything else stays in className
    <View className="rounded-t-2xl bg-white px-4" style={{ paddingBottom: insets.bottom }}>
      {children}
    </View>
  );
}
```

Reference: [NativeWind](https://www.nativewind.dev/v4/overview)
