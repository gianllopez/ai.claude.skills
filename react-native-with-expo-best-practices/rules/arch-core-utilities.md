---
title: Core Utilities & Configuration Structure
impact: MEDIUM-HIGH
description: Enforces organization for global configuration, functional helpers (no static classes), shared hooks, and third-party library adapters.
tags: architecture, core
---

## Core Utilities & Configuration Structure

**Impact (MEDIUM-HIGH):** Centralizing configuration constants prevents "magic strings". Using functional helpers instead of static classes improves tree-shaking. Isolating third-party logic in `lib/` prevents vendor lock-in leaking into business logic.

**Guidelines:**

1.  **Configuration (`./core/config/`):**
    - Must store global constants (Storage Keys, UI metrics, Query timings) and theme definitions.
    - **Theme:** Colors must be explicitly defined (e.g., mapping _TailwindCSS_ colors to semantic names), avoiding raw hex codes in components.
2.  **Helpers (`./core/helpers/`):**
    - **Functional Approach:** Must use top-level named exports (`export const login = ...`).
    - **Forbidden:** Do not use `class` with `static` methods for helpers. This is an _OOP_ pattern not suitable for modern tree-shakable JS/TS bundles.
3.  **Hooks (`./core/hooks/`):**
    - Contains global, reusable hooks (e.g., `use-screen-spacing`, `use-debounce`) and global state stores (`stores/`).
    - Domain-specific hooks (like `use-create-asset`) belong in `./core/api/`, not here.
4.  **Libraries (`./core/lib/`):**
    - Contains configuration and adapters for third-party libraries (e.g., `axios`, `react-native-mmkv`).
    - If a library requires complex setup, create a subfolder (e.g., `./core/lib/react-query/client.ts`).

**Incorrect (Static Classes, Magic Strings, Scattered Config):**

```typescript
// ./core/helpers/session.ts

// Bad: Wrapper class pattern (OOP style in functional ecosystem)
export class SessionHelper {
  static login(token: string) { ... }
}
```

```typescriptreact
// ./components/card.tsx

// Bad: Magic string and raw hex
AsyncStorage.setItem('my-token', '...');
<View style={{ backgroundColor: '#e43636' }} />
```

**Correct (Functional, Centralized, Modular):**

```typescript
// ./core/config/constants.ts

export const STORAGE = {
  SESSION: { JSON_WEB_TOKEN: "@session/jwt/token" },
};

export const QUERY = {
  TIME: { MEDIUM: 300000 },
};
```

```typescript
// ./core/helpers/session.ts

// Good: Direct module exports (Tree-shakable)
import { STORAGE } from "@/core/config/constants";
import { storage } from "@/core/lib/react-native-mmkv";

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
