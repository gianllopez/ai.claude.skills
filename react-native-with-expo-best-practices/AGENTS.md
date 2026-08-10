# React Native & Expo Best Practices

**Version 1.0.0**  
_Gian López_  
_August 2026_

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring _React Native_ (_Expo_) codebases. Humans  
> may also find it useful, but guidance here is optimized for automation  
> and consistency by AI-assisted workflows.

---

## Abstract

Standards for the part of a _React_ application that only exists on mobile: the _Expo Router_ directory whose filenames are the navigation graph, the styling layer _NativeWind_ provides over _React Native_ primitives, and the native configuration _Expo_ generates from `app.json`. What the platform dictates, and nothing that _React_ already decides — effects, state, the query layer, component composition, file structure and typing live in `react-core-best-practices`, which an _Expo_ project loads alongside this one.

---

## Table of Contents

1. [Project Structure](#1-project-structure) — `HIGH`
   - [1.1 The App Directory & Expo Router](#11-the-app-directory--expo-router)
2. [UI & Design System](#2-ui--design-system) — `HIGH`
   - [2.1 NativeWind Styling Standards](#21-nativewind-styling-standards)
3. [Environment](#3-environment) — `HIGH`
   - [3.1 Expo & Environment Configuration](#31-expo--environment-configuration)

---

## 1. Project Structure

### 1.1 The App Directory & Expo Router

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

---

## 2. UI & Design System

### 2.1 NativeWind Styling Standards

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

---

## 3. Environment

### 3.1 Expo & Environment Configuration

**Impact (HIGH):** Standardization of code style (imports/formatting) and project configuration reduces cognitive load. Using `plugins` in `app.json` for native capabilities (fonts, splash screens) ensures native projects are generated consistently during prebuild. Custom scripts facilitate rapid testing cycles.

**Guidelines:**

1.  **Code Formatting:**
    - Must use `prettier` with `@trivago/prettier-plugin-sort-imports` and `prettier-plugin-tailwindcss`
2.  **Custom Scripts:**
    - Include `ios:uninstall` and `android:uninstall` commands to quickly wipe the app from simulators/emulators for clean install testing
3.  **Expo Configuration (`app.json`):**
    - **Identifiers:** Use strict _Reverse Domain_ notation (`com.org.project`)
    - **Assets:** Store assets in `./public/` (not `./assets/`)
    - **Plugins:** Configuration for splash screen and fonts must be done via the `plugins` array (not top-level props) to ensure granular control, especially for _Android_ font weights/styles

**Incorrect (Default Config & Missing Plugins):**

```json
// ./package.json (Missing uninstall scripts)

{
  "scripts": {
    "start": "expo start",
    "android": "expo run:android"
  }
}
```

```json
// ./app.json (Basic config, assets in root, missing plugins)

{
  "expo": {
    "splash": {
      "image": "./assets/splash.png" // Bad: Use plugin for control
    }
  }
}
```

**Correct (Plugin-Based & Strict Formatting):**

```yaml
# .prettierrc.yml

printWidth: 80
tabWidth: 2
trailingComma: 'all'
singleQuote: true
semi: true
importOrderSeparation: true
importOrderSortSpecifiers: true
importOrder:
  - '^react-native$'
  - '^react$'
  - '^@?expo(.*)$'
  - '<THIRD_PARTY_MODULES>'
  - '~/components'
  - '~/core'
  - '^[./]'
plugins:
  - '@trivago/prettier-plugin-sort-imports'
  - 'prettier-plugin-tailwindcss'
```

```json
// ./package.json

{
  "scripts": {
    "android:uninstall": "adb uninstall com.example.project",
    "ios:uninstall": "xcrun simctl uninstall booted com.example.project"
  }
}
```

```json
// ./app.json

{
  "expo": {
    "ios": {
      "bundleIdentifier": "com.example.project"
    },
    "android": {
      "package": "com.example.project",
      "adaptiveIcon": {
        "foregroundImage": "./public/images/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      }
    },
    "plugins": [
      [
        "expo-splash-screen",
        {
          "image": "./public/images/splash-icon.png",
          "imageWidth": 200,
          "resizeMode": "contain",
          "backgroundColor": "#ffffff"
        }
      ],
      [
        "expo-font",
        {
          "fonts": ["./public/fonts/CustomFont.ttf"],
          "android": {
            "fonts": [
              {
                "fontFamily": "CustomFont",
                "fontDefinitions": [
                  {
                    "path": "./public/fonts/CustomFont-Regular.ttf",
                    "weight": 400
                  },
                  {
                    "path": "./public/fonts/CustomFont-Bold.ttf",
                    "weight": 700
                  },
                  {
                    "path": "./public/fonts/CustomFont-BoldItalic.ttf",
                    "weight": 700,
                    "style": "italic"
                  }
                ]
              }
            ]
          }
        }
      ]
    ]
  }
}
```

Reference: [Expo Config Plugins](https://docs.expo.dev/config-plugins/introduction)
