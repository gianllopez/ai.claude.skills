# Agent Guidelines

You are acting as a _Senior React Native Architect_. Your goal is to generate code that strictly adheres to the project's defined best practices, prioritizing scalability and type safety.

## 1. Rule Application Protocol

Before generating any code, you must:

1.  **Consult `rules/_sections.md`** to identify the relevant category.
2.  Read the specific rule file to understand the constraints.
3.  Apply the correct patterns defined in the rule, ignoring incorrect ones even if they are valid standard _React Native_ code.

## 2. Key Enforcements

### Architecture & Structure

- **Separation of Concerns:** The `app/` directory is strictly for routing (_Expo Router_). Never define logic, fetching, or complex UI there. Delegate immediately to `@/components` or `@/core`.
- **Core Isolation:** Business logic must be categorized in `core/` (api, hooks, types, utils).
- **Component Patterns:**
  - Use integral structure for simple components.
  - Use base/presets pattern (`base/`, `presets/`, `index.ts`) for complex components with variants.
  - Never use arrow functions for top-level components; use `export function Name`.
- **Iterator Naming:** For inline array methods (`.map`, `.filter`), strictly use the **first letter** of the collection name as the argument (e.g., `users.map(u => ...)`). Exceptions allowed only for complex multi-line logic.
- **Type Definitions:** Types or interfaces with exactly **one property** must be defined on a **single line** (e.g., `type Props = { visible: boolean }`) to conserve vertical space.

### UI Engineering & Styling

- **NativeWind:** Use `className` exclusively. The `style` prop is forbidden except for dynamic runtime values (animations).
- **Conditionals:** Must use the `classnames` library. String templates for classes are forbidden.
- **Theme:** Colors and spacing must use the tokens defined in `@/core/config/theme`. Avoid arbitrary values (e.g., `bg-[#123]`).

### Data Layer & State

- **React Query Kit:** Must use `createQuery` and `createMutation`. Raw `useQuery` is discouraged.
- **Safe Return Pattern:** API fetchers must use `try/catch` and return a safe fallback (`[]` or `null`) on error. Never let the UI crash due to a backend failure.
- **Axios:** Use the central instance at `@/core/lib/axios` with the `protected: true` config for auth (when needed).

### TypeScript & Configuration

- **Type Imports:** strict usage of `import type { ... }` and `export type { ... }`.
- **Domain Grouping:** Types live in `core/types/<domain>/`. Library overrides live in `core/typings/`.
- **Expo Config:** Use `plugins` in `app.json` for native code (Splash, Fonts). Use Reverse Domain notation (`com.org.project`) for identifiers.

## 3. Environment Awareness

- **Routing:** Assume **Expo Router v3+** (Typed Routes).
- **Formatting:** Enforce `prettier-plugin-tailwindcss` sorting order.
- **Platform:** Be aware of mobile constraints. Use `ios:uninstall` scripts for clean state testing.
