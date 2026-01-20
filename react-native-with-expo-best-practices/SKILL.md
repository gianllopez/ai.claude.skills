---
name: react-native-with-expo-best-practices
description: Expo and React Native architectural guidelines. This skill defines the standards for the mobile front-end, focusing on separation of concerns, type safety, atomic component composition, and efficient data handling.
license: MIT
metadata:
  author: gianllopez
  version: 1.0.0
---

# React Native & Expo Best Practices

Comprehensive guide for _Expo_ and _React Native_ development using _TypeScript_. Contains rules prioritized by impact on maintainability, performance, and scalability.

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
| 2        | Project Configuration         | MEDIUM-HIGH | `conf-` |

## Quick Reference

### 1. Architecture & Core Structure (HIGH)

- `arch-folder-structure` - Enforce strict separation of `app` (_Expo Router_), `core` (Logic), and `components` (UI)
- `arch-components-structure` - Standards for Integral components vs the base/presets pattern for variants
- `arch-typing-system` - Segregate domain `types` from library `typings` using explicit imports
- `arch-core-utilities` - Functional helpers, centralized config constants, and library adapters

### 2. UI Engineering & Styling (HIGH)

- `arch-style-nativewind` - Use `className` with _NativeWind_ and `classnames` for conditional logic

### 3. Data & Configuration (MEDIUM-HIGH)

- `arch-api-data-layer` - Centralized _Axios_ and `react-query-kit` with safe return patterns
- `conf-expo` - Native config via plugins, strict _Prettier_ sorting, and clean-state scripts

## How to Use

Read individual rule files for detailed explanations and code examples:

```plaintext
rules/*.md
```
