# React Native & Expo Best Practices

**Version 1.0.0**  
_Gian López_  
_January 2026_

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring _React Native_ (_Expo_) codebases. Humans  
> may also find it useful, but guidance here is optimized for automation  
> and consistency by AI-assisted workflows.

---

## Abstract

Standard architectural guidelines for scalable _React Native_ (_Expo_) applications. This manifest enforces strict separation of concerns between the View layer (app/components) and the Business Core (core), utilizes a domain-segregated _TypeScript_ typing system, and adopts modern design patterns like 'Base/Presets' for UI components and 'Safe Return' for the data layer. Configuration prioritizes performance and maintainability through the use of _NativeWind_, _React Query Kit_, and native configuration plugins.

---

## Table of Contents

1. [Architecture & Core](#1-architecture--core) — `HIGH`
   - 1.1 [Modular Project Structure](#11-modular-project-structure)
   - 1.2 [Core Utilities & Configuration Structure](#12-core-utilities--configuration-structure)
   - 1.3 [TypeScript Type System & Domain Organization](#13-typescript-type-system--domain-organization)
   - 1.4 [API Data Layer & Query Management](#14-api-data-layer--query-management)
2. [Conventions](#2-conventions) — `LOW`
   - 2.1 [Syntax & Conciseness Conventions](#21-syntax--conciseness-conventions)
3. [UI & Design System](#3-ui--design-system) — `HIGH`
   - 3.1 [Component Structure & Composition](#31-component-structure--composition)
   - 3.2 [Tailwind CSS & Styling Standards](#32-tailwind-css--styling-standards)
4. [Environment](#4-environment) — `HIGH`
   - 4.1 [Expo & Environment Configuration](#41-expo--environment-configuration)

---

## 1. Architecture & Core

### 1.1 Modular Project Structure

**Impact (HIGH):** Standardization ensures scalability. Separating specific framework logic (_Expo Router_ in `app/`) from business logic (`core/`) and UI (`components/`) allows for easier testing, reuse, and migration.

**Guidelines:**

1.  **Root Directory:**
    - `app/`: Contains only _Expo Router_ files (`_layout`, `index`, `[id]`). No business logic here
    - `components/`: Contains UI elements
    - `core/`: Contains all non-UI logic
2.  **Core Organization (`core/`):**
    - Logic must be categorized by type: `api/`, `config/`, `constants/`, `hooks/`, `i18n/`, `lib/`, `store/`, `theme/`, `types/`, and `utils/`
    - **Types:** All _TypeScript_ definitions reside in `core/types/` (grouped by domain like `entity`, `user`)
    - **API:** _API_ services must be grouped by domain (e.g., `core/api/entity/`)
3.  **Component Organization (`components/`):**
    - **Feature Components:** Grouped by domain (e.g., `feature-sheet`, `entity-list`) containing their own sub-components if necessary
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
│   └── index.ts
```

```typescript
// ./app/(tabs)/index.tsx

import { EntityList } from '@/components/entity-list';
import { useEntity } from '@/core/api/entity';

export default function Screen() {
  const { data } = useEntity();

  return <EntityList data={data} />;
}
```

### 1.2 Core Utilities & Configuration Structure

**Impact (MEDIUM):** Centralizing configuration constants prevents magic strings. Using functional helpers instead of static classes improves tree-shaking. Isolating third-party logic in `lib/` prevents vendor lock-in leaking into business logic.

**Guidelines:**

1.  **Configuration (`./core/config/`):**
    - Must store global constants (storage keys, UI metrics, query timings) and theme definitions
    - **Theme:** Colors must be explicitly defined (e.g., mapping _TailwindCSS_ colors to semantic names), avoiding raw hex codes in components
2.  **Helpers (`./core/helpers/`):**
    - **Functional Approach:** Must use top-level named exports (`export const login = ...`)
    - **Forbidden:** Do not use `class` with `static` methods for helpers. This is an _OOP_ pattern not suitable for modern tree-shakable JS/TS bundles
3.  **Hooks (`./core/hooks/`):**
    - Contains global, reusable hooks (e.g., `use-screen-spacing`, `use-debounce`) and global state stores (`stores/`)
    - Domain-specific hooks (like `use-create-asset`) belong in `./core/api/`, not here
4.  **Libraries (`./core/lib/`):**
    - Contains configuration and adapters for third-party libraries (e.g., `axios`, `react-native-mmkv`)
    - If a library requires complex setup, create a subfolder (e.g., `./core/lib/react-query/client.ts`)

**Incorrect (Static Classes, Magic Strings, Scattered Config):**

```typescript
// ./core/helpers/session.ts

// Bad: Wrapper class pattern (OOP style in functional ecosystem)
export class SessionHelper {
  static login(token: string) { ... }
}
```

```typescript
// ./components/card.tsx

// Bad: Magic string and raw hex
AsyncStorage.setItem('my-token', '...');
<View style={{ backgroundColor: '#e43636' }} />
```

**Correct (Functional, Centralized, Modular):**

```typescript
// ./core/config/constants.ts

export const STORAGE = {
  SESSION: { JSON_WEB_TOKEN: '@session/jwt/token' },
};

export const QUERY = {
  TIME: { MEDIUM: 300000 },
};
```

```typescript
// ./core/helpers/session.ts

// Good: Direct module exports (Tree-shakable)
import { STORAGE } from '@/core/config/constants';
import { storage } from '@/core/lib/react-native-mmkv';

export const login = (token: string) => {
  storage.set(STORAGE.SESSION.JSON_WEB_TOKEN, token);
};

export const isLoggedIn = (): boolean => {
  return storage.contains(STORAGE.SESSION.JSON_WEB_TOKEN);
};
```

```typescript
// ./core/hooks/use-screen-spacing.ts

import { useSafeAreaInsets } from 'react-native-safe-area-context';

// ... logic shared across screens
export function useScreenSpacing() { ... }
```

### 1.3 TypeScript Type System & Domain Organization

**Impact (HIGH):** A structured type system prevents circular dependencies and naming collisions. Separating external library overrides (`typings`) from business logic definitions (`types`) ensures that the application's contract remains clear. Enforcing `import type` and `export type` aids the compiler in tree-shaking and type erasure.

**Guidelines:**

1.  **Directory Separation:**
    - `core/types/`: Contains application-specific definitions grouped by domain (e.g., `users`, `products`)
    - `core/typings/`: Contains global overrides and module augmentations for third-party libraries (e.g., `axios.d.ts`, `environment.d.ts`)
2.  **Definition Strategy:**
    - **Interfaces:** Must be used for defining the shape of objects, especially _API_ responses and external services (extensible)
    - **Types:** Must be used for unions, intersections, mapped types (`Pick`, `Omit`), and aliases
3.  **Domain Grouping:**
    - Types must be grouped in folders matching their domain (e.g., `core/types/config/`)
    - Each domain folder must have an `index.ts` exporting its members
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

### 1.4 API Data Layer & Query Management

**Impact (HIGH):** Centralizing _API_ logic ensures consistent caching strategies, type safety across network boundaries, and unified authentication handling. Letting errors propagate naturally to _React Query_ enables proper error state handling via `isError` and `error` in the consuming component.

**Guidelines:**

1.  **Library Standard:** Must use `react-query-kit` (`createQuery`, `createMutation`) to encapsulate _Query Keys_ and _Fetchers_
2.  **Directory Structure:**
    - _API_ hooks must be grouped by domain in `@/core/api/<domain>/`
    - Files should be named `use-<members|action>.ts` (e.g., `use-assets.ts`, `use-create-asset.ts`)
3.  **Type Definitions:**
    - Define `Response` (_API_ Contract), `Data` (UI consumption), and `Variables`
    - Return types must be explicit
4.  **Query Keys:**
    - Format: `'@<domain>/<hook-name>'`
    - Example: `'@users/use-assets'`
5.  **Axios Configuration:**
    - Use a central instance (`@/core/lib/axios`)
    - Implement `protected: true` via interceptors to inject the `Authorization` header
    - Augment `AxiosRequestConfig` to support the custom `protected` property

**Incorrect (Inline fetch, raw keys):**

```typescript
// ./app/users.tsx

// Bad: Inline fetching, no types, hardcoded key, error suppressed with fallback
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export function Users() {
  const { data } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      try {
        return (await axios.get('/users')).data;
      } catch {
        return []; // Bad: Suppresses error — isError will never be true
      }
    },
  });
}
```

**Correct (Structured, Typed, Protected):**

```typescript
// ./core/lib/axios.ts

import axios, { HttpStatusCode } from 'axios';
import * as SessionHelper from '@/core/helpers/session'; // Module import (Best Practice)

export const api = axios.create({ baseURL: process.env.EXPO_PUBLIC_API_URL });

api.interceptors.request.use(
  (config) => {
    if (config.protected) {
      const token = SessionHelper.getToken();
      if (token) {
        config.headers.set('Authorization', `Bearer ${token}`);
      }
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// ... Response interceptor for 401 logout ...
```

```typescript
// ./core/api/users/use-assets.ts

import { createQuery } from 'react-query-kit';
import { QUERY } from '@/core/config/constants';
import { api } from '@/core/lib/axios';
import type { Asset } from '@/core/types/users';

type Response = Asset[];

type Data = Response;

type Variables = string;

export const useAssets = createQuery<Data, Variables>({
  queryKey: ['@users/use-assets'],
  fetcher: request,
  staleTime: QUERY.TIME.NONE,
});

async function request(id: Variables) {
  const { data } = await api.get<Response>(`/users/${id}/assets/`, {
    protected: true,
  });
  return data;
}
```

```typescript
// ./core/typings/axios.d.ts

import 'axios';

declare module 'axios' {
  export interface AxiosRequestConfig {
    protected?: boolean;
  }
}
```

Reference: [React Query Kit](https://tanstack.com/query/v4/docs/framework/react/community/liaoliao666-react-query-kit)

---

## 2. Conventions

### 2.1 Syntax & Conciseness Conventions

**Impact (LOW):** Improves code conciseness and reduces visual noise in high-frequency patterns, while enforcing explicit control flow in conditionals to prevent logic bugs and improve readability.

These rules aim to maximize the information density of the code, making it easier to scan logic without getting lost in verbose boilerplate.

#### 1. Iterator Naming (Short-Hand Convention)

For inline array methods (`.map`, `.filter`, `.forEach`, etc.), strictly use the first letter of the collection's item name as the argument. This reduces horizontal scrolling and focuses attention on the logic.

**Exceptions:**

- **Complex Logic:** If the callback body requires a multi-line block (`{ ... }`) or complex destructuring, use the full descriptive singular name to maintain context
- **Nested Loops:** If iterating within another iterator, use full names to avoid confusion (e.g., avoid `u` inside another `u`)

**Incorrect (verbose for simple logic):**

```typescript
// Too noisy for a simple ID extraction
const userIds = users.map((user) => user.id);

// Redundant naming
const activeItems = items.filter((item) => item.isActive);
```

**Correct (concise):**

```typescript
// Clean and focused on the operation
const userIds = users.map((u) => u.id);

const activeItems = items.filter((i) => i.isActive);
```

**Correct (exception for complex logic):**

```typescript
// Complex logic warrants a descriptive name
const richData = users.map((user) => {
  const isEligible = checkEligibility(user);
  return { ...user, isEligible };
});
```

#### 2. Single-Property Type Definitions

To conserve vertical screen space, _TypeScript_ types (not interfaces) that contain exactly one property must be defined on a single line.

**Incorrect (wasted vertical space):**

```typescript
// Wastes 3 lines for 1 property
type Props = {
  visible: boolean;
};
```

**Correct (optimized):**

```typescript
// Efficient use of space
type Props = { visible: boolean };
```

#### 3. Event Handler Naming Convention

Event handler implementations must use the `handle` prefix to distinguish them semantically from event props (which use the `on` prefix). This creates a clear visual distinction between the prop interface (what events the component accepts) and the implementation (what happens when the event fires). Using `on` for both the prop and the implementation creates ambiguity. The `handle` prefix makes it immediately clear that this is the concrete implementation being passed to the event prop.

**Incorrect (ambiguous naming):**

```typescript
export function MyScreen() {
  // Bad: Using 'on' prefix for implementation
  const onChangeText = (text: string) => {
    console.log(text);
  };

  const onPress = () => {
    console.log('Pressed');
  };

  return (
    <View>
      <Input onChangeText={onChangeText} />
      <Button onPress={onPress}>Continue<Button />
    </View>
  );
}
```

**Correct (semantic clarity):**

```typescript
export function MyScreen() {
  // Good: Using 'handle' prefix for implementations
  const handleChangeText = (text: string) => {
    console.log(text);
  };

  const handlePress = () => {
    console.log('Pressed');
  };

  return (
    <View>
      <Input onChangeText={handleChangeText} />
      <Button onPress={handlePress} />
    </View>
  );
}
```

#### 4. Conditional Syntax

All conditionals must use braces `{}` and line breaks — even for single-line bodies and early returns. This applies to every context: functions, components, and JSX rendering. Omitting braces is forbidden regardless of how simple the condition is.

For conditional rendering in JSX, the ternary operator must always be used. The `&&` shorthand is forbidden because it can render unintended values (e.g., `0`, `NaN`). When the negative case renders nothing, use `null` explicitly.

**Incorrect (braceless conditions, `&&` in JSX):**

```typescript
// Bad: Braceless early return
if (!user) return null;

// Bad: Braceless single-line body
if (isLoading) return <Spinner />;

// Bad: && shorthand — renders '0' if items.length is 0
{items.length && <List items={items} />}

// Bad: && shorthand with no explicit negative case
{isVisible && <Modal />}
```

**Correct (braces + line breaks, ternary with null):**

```typescript
// Good: Early return with braces
if (!user) {
  return null;
}

// Good: Single-line body with braces
if (isLoading) {
  return <Spinner />;
}

// Good: Ternary with explicit null — no unintended renders
{items.length > 0 ? <List items={items} /> : null}

// Good: Ternary for toggle visibility
{isVisible ? <Modal /> : null}
```

Reference: [TypeScript Handbook - Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)

---

## 3. UI & Design System

### 3.1 Component Structure & Composition

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
    - **Grouped Component:** Directory with `index.tsx` (main) and helper files (e.g., `item.tsx`). Helper components must have generic names internal to the folder but specific implementation details
    - **Complex Component (base/presets):** For components with multiple variants (e.g., _Buttons_, _Inputs_), strictly follow the respective pattern
      - `base/`: Contains the logic container (state, theme injection, layout). Uses `render` props to pass data to children
      - `presets/`: Contains visual implementations consuming the `base`
      - `index.ts`: Multiple barrel files to control visibility

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

### 3.2 Tailwind CSS & Styling Standards

**Impact (HIGH):** Unified styling via utility classes reduces bundle size (no _StyleSheet_ objects) and improves readability. Using a dedicated library for conditional classes prevents messy template literals and ensures consistent class resolution.

**Guidelines:**

1.  **Primary Styling Approach:**
    - Must use the `className` prop for all component styling
    - The `style` prop is reserved strictly for dynamic values that _TailwindCSS_ cannot handle (e.g., interpolated animations, dynamic safe-area insets calculated at runtime) or 3rd party components not compatible with _NativeWind_
2.  **Conditional Classes:**
    - Must use the `classnames` library for handling conditional logic
    - **Forbidden:** Do not use template literals or string concatenation for classes (e.g., `` `flex-1 ${active ? 'bg-red' : ''}` ``)
3.  **Theme Restrictions:**
    - Must utilize the tokens defined in `./core/config/theme/colors.ts`
    - Avoid arbitrary values (e.g., `bg-[#123456]`) unless absolutely necessary for one-off generic values
4.  **Formatting:**
    - Class names must be sorted automatically via `prettier-plugin-tailwindcss`

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

---

## 4. Environment

### 4.1 Expo & Environment Configuration

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
  - '@/components'
  - '@/core'
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
