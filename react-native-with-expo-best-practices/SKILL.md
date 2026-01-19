---
name: react-native-best-practices
description: Expo and React Native architectural guidelines. This skill defines the standards for the mobile front-end, focusing on separation of concerns, type safety, atomic component composition, and efficient data handling.
license: MIT
metadata:
  author: gianllopez
  version: 1.0.0
---

# React Native & Expo Best Practices

Comprehensive guide for _Expo_ and _React Native_ development using TypeScript. Contains rules prioritized by impact on maintainability, performance, and scalability.

## When to Apply

Reference these guidelines when:

- Structuring the project folders or adding new features (`app/` vs `core/` vs `components/`).
- Creating UI components, deciding between integral or base/presets patterns.
- Implementing data fetching logic using `react-query-kit` and `axios`.
- Defining _TypeScript_ interfaces or segregating domain types from library typings.
- Styling components using _NativeWind_ (`className`) and handling conditional styles.
- Configuring _Expo_ plugins, environment variables, or native directories.
- Writing functional helpers or configuring global store hooks.

## Rule Categories by Priority

| Priority | Category                      | Impact      | Prefix  |
| :------- | :---------------------------- | :---------- | :------ |
| 1        | Architecture & Core Structure | CRITICAL    | `arch-` |
| 2        | API Data Layer & Fetching     | HIGH        | `api-`  |
| 3        | Project Configuration         | MEDIUM-HIGH | `conf-` |

## Quick Reference

### 1. Architecture (`arch-`)

- **Folder Structure:** [Modular Project Structure](./rules/arch-folder-structure.md)
- **Component Structure:** [Component Structure (Base/Presets)](./rules/arch-comp-structure.md)
- **Core Utilities:** [Core Utilities & Config](./rules/arch-core-utilities.md)
- **Typing System:** [TypeScript Domain System](./rules/arch-typing-system.md)
- **Styling Standards:** [Tailwind CSS & NativeWind](./rules/arch-style-nativewind.md)

### 2. Data (`api-`)

- **API Layer:** [Data Fetching & Axios](./rules/api-data-layer.md)

### 3. Configuration (`conf-`)

- **Expo Config:** [Environment & Plugins](./rules/conf-expo.md)

## How to Use

Read individual rule files for detailed explanations and code examples:

```plaintext
rules/*.md
```
