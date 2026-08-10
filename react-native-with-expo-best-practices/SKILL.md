---
name: react-native-with-expo-best-practices
description: Standards for what React renders to on mobile — NativeWind styling over StyleSheet, the Expo Router directory and what may live in it, and native configuration through app.json plugins. Use when reviewing, writing, or refactoring screens under app/, className attributes in a React Native project, theme colors, or Expo configuration and build scripts. Everything independent of the renderer — effects, state, the query layer, component composition, file structure and typing — lives in react-core-best-practices, which an Expo project loads alongside this one.
license: MIT
metadata:
  author: gianllopez
  version: 1.0.0
---

# React Native & Expo Best Practices

Standards for the part of a _React_ application that only exists on mobile: the router directory whose filenames are the navigation graph, the styling layer _NativeWind_ provides, and the native configuration _Expo_ generates from `app.json`.

Everything that does not change with the renderer — effect and state discipline, the typed query layer, component composition, file structure and typing — is in `react-core-best-practices`. **An Expo project loads both.** This skill assumes that one is present and never restates it.

**Scope:** _Expo_ and _React Native_ with _TypeScript_. What the platform dictates, and nothing that _React_ already decides.

## When to Apply

Reference these guidelines when:

- Adding a screen, a layout, or a route group under `app/`
- Styling with `className`, or deciding whether a value belongs in the `style` prop instead
- Adding a colour to the theme, or reaching for a raw hex in a component
- Configuring `app.json` — plugins, identifiers, splash screen, fonts, adaptive icons
- Setting up _Prettier_ import ordering, or the clean-install scripts

## Rule Categories by Priority

| Priority | Category           | Peak impact | Prefix  |
| :------- | :----------------- | :---------- | :------ |
| 1        | Project Structure  | HIGH        | `arch-` |
| 2        | UI & Design System | HIGH        | `arch-` |
| 3        | Environment        | HIGH        | `conf-` |

## Quick Reference

### 1. Project Structure (HIGH)

- `arch-app-directory` - `app/` is the navigation graph, not a folder; components group by domain; imports resolve through `~/`

### 2. UI & Design System (HIGH)

- `arch-style-nativewind` - `className` over `StyleSheet`; the `style` prop only for what utilities cannot express; colours come from the theme

### 3. Environment (HIGH)

- `conf-expo` - Native capabilities through `app.json` plugins, strict import sorting, and clean-install scripts

## How to Use

Read individual rule files for detailed explanations and code examples:

```plaintext
rules/*.md
```

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md` (generated — see `README.md`).
