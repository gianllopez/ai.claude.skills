---
title: Core Utilities & Configuration
impact: MEDIUM
description: Requires helpers to be plain exported functions rather than static classes, and constants to be declared once in core/config instead of written inline at each call site.
tags: architecture, core, helpers
---

## Core Utilities & Configuration

**Impact (MEDIUM):** Two small habits decide whether `core/` stays useful. A helper written as a class with `static` methods drags the whole class into every bundle that touches one of its methods, because a class is a single binding and nothing can tree-shake half of it. And a key written inline — `'@session/jwt/token'` at the call site — is a value with no definition: the day it changes, correctness depends on a find-and-replace catching every copy, and a typo produces a miss rather than an error.

**Guidelines:**

1.  **Helpers are exported functions:**
    - `export const login = (token: string) => …`, one binding per behavior
    - A `class` with only `static` methods is an object pretending to be a namespace. It cannot be tree-shaken, it cannot be partially imported, and it buys nothing over the module system that already provides both
    - Import the module when the group is what matters — `import * as SessionHelper from '~/core/helpers/session'` — which gives the namespace without the class
2.  **Constants are declared once, in `core/config/`:**
    - Storage keys, cache timings, and any string the code compares against belong there, grouped by what they configure
    - The test is whether a typo would be caught: `STORAGE.SESSION.TOKEN` fails to compile when misspelled, `'@session/jwt/token'` fails silently at runtime
    - This is not a rule about magic numbers in general. A `setTimeout(..., 300)` inside the one component that debounces is fine; the value that two modules must agree on is what needs a name
3.  **A constant is not a type:**
    - Where a value set is also a type, derive the type from the constant rather than declaring both — `keyof typeof STORAGE` (see the typing-conventions rule)
    - Two declarations of the same set drift, and the compiler cannot tell you which one was right

**Incorrect (a static-class namespace, and keys written wherever they are needed):**

```ts
// ./core/helpers/session.ts

// Bad: a class used as a namespace — importing `login` pulls in `logout`,
// `refresh` and everything else this class ever grows
export class SessionHelper {
  static login(token: string) {
    storage.set('@session/jwt/token', token);
  }

  static isLoggedIn(): boolean {
    return storage.contains('@session/jwt/token');
  }
}
```

```ts
// ./core/api/session/use-refresh.ts

// Bad: the same key, written again. Nothing connects these two literals, and a
// typo here logs every user out instead of failing the build
const token = storage.getString('@session/jwt/tokens');
```

**Correct (plain exported functions, keys declared once):**

```ts
// ./core/config/constants.ts

export const STORAGE = {
  SESSION: { JSON_WEB_TOKEN: '@session/jwt/token' },
};

export const QUERY = {
  TIME: {
    NONE: 0,
    MEDIUM: 300_000,
  },
};
```

```ts
// ./core/helpers/session.ts

import { STORAGE } from '~/core/config/constants';
import { storage } from '~/core/lib/storage';

// Good: one binding per behavior, so a consumer takes only what it imports
export const login = (token: string) => {
  storage.set(STORAGE.SESSION.JSON_WEB_TOKEN, token);
};

export const isLoggedIn = (): boolean => {
  return storage.contains(STORAGE.SESSION.JSON_WEB_TOKEN);
};
```

```ts
// ./core/api/session/use-refresh.ts

// Good: the namespace without the class, and the key has exactly one definition
import * as SessionHelper from '~/core/helpers/session';
import { STORAGE } from '~/core/config/constants';

const token = storage.getString(STORAGE.SESSION.JSON_WEB_TOKEN);
```

Reference: [Tree shaking](https://developer.mozilla.org/en-US/docs/Glossary/Tree_shaking)
