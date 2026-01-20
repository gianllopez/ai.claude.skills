---
title: Expo & Environment Configuration
impact: HIGH
description: Enforces strict _Prettier_ formatting (import sorting, TailwindCSS), custom lifecycle scripts, and plugin-based Expo configuration for assets and fonts.
tags: configuration, expo
---

## Expo & Environment Configuration

**Impact (HIGH):** Standardization of code style (imports/formatting) and project configuration reduces cognitive load. Using `plugins` in `app.json` for native capabilities (fonts, splash screens) ensures native projects are generated consistently during prebuild. Custom scripts facilitate rapid testing cycles.

**Guidelines:**

1.  **Code Formatting:**
    - Must use `prettier` with `@trivago/prettier-plugin-sort-imports` and `prettier-plugin-tailwindcss`.
2.  **Custom Scripts:**
    - Include `ios:uninstall` and `android:uninstall` commands to quickly wipe the app from simulators/emulators for clean install testing.
3.  **Expo Configuration (`app.json`):**
    - **Identifiers:** Use strict _Reverse Domain_ notation (`com.org.project`).
    - **Assets:** Store assets in `./public/` (not `./assets/`).
    - **Plugins:** Configuration for splash screen and fonts must be done via the `plugins` array (not top-level props) to ensure granular control, especially for _Android_ font weights/styles.

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
