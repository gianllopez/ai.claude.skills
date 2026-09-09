---
title: Typed Environment & Content Security Policy
impact: HIGH
description: Declares every environment variable in the astro:env schema so secrets cannot reach the client bundle, and enables the built-in Content Security Policy instead of shipping without one.
tags: environment, secrets, security, csp, configuration
---

## Typed Environment & Content Security Policy

**Impact (HIGH):** `import.meta.env` is untyped and unvalidated: a missing variable is `undefined` at the point of use rather than an error at startup, a typo produces the same, and the rule keeping secrets out of the browser is a naming convention — a variable that should have been server-only reaches the client bundle by being read in the wrong file, and nothing reports it. `astro:env` replaces the convention with a schema: each variable declares its context and its access, secrets are excluded from the bundle by construction, and a missing one fails the build. The second half of this rule is what a static site ships without noticing. _CSP_ has been stable since v6 as `security.csp` and works in every render mode, computing hashes for the site's own scripts and styles — so the reason it is absent from most _Astro_ projects is not that it is hard, it is that nothing prompts for it.

**Guidelines:**

1.  **Declare every variable in `env.schema`:**
    - `envField.string()`, `.number()`, `.boolean()`, `.enum()` with a `context` and an `access`
    - `context: 'client'` variables are available in both bundles and are therefore public, always
    - `context: 'server'` with `access: 'public'` stays in the server bundle; with `access: 'secret'` it is not bundled at all and is read at runtime
    - There is no secret client variable, because there is no safe way to send one — a value the browser needs is a public value, and treating it otherwise is the mistake this schema prevents
2.  **Import from the context-specific module:**
    - `import { API_URL } from 'astro:env/client'` and `import { API_SECRET } from 'astro:env/server'`
    - The import path is the check: a server-only value pulled into a component that hydrates is a build error rather than a leak
    - `import.meta.env` still works and still has none of this — it is the fallback for values outside the schema, which should be close to none
3.  **Mark optional values as optional, with a default:**
    - A variable declared required is one a broken deploy cannot skip past, which is the point
    - `optional: true` plus `default:` for the ones that genuinely have a sensible fallback
4.  **Turn `security.csp` on:**
    - `security: { csp: true }` is the baseline and works for prerendered and on-demand pages alike
    - The object form takes `algorithm`, `directives`, and `scriptDirective` / `styleDirective` with their own `hashes` and `resources` — which is how a site declares the third-party origins it actually loads
    - Every allowed origin should correspond to a script or embed the third-party rule already justified. A policy listing origins nobody can account for is a policy that has stopped meaning anything
5.  **A policy is verified in a browser, not in the config:**
    - The failure mode is a directive too narrow, which breaks a widget silently in production and shows up only in the console
    - Check the pages that carry embeds first — they are where the policy and the site disagree

**Incorrect (untyped access, a secret read where it can be bundled, no policy):**

```astro
---
// src/components/ContactForm.astro
// Bad: untyped, unvalidated. A missing or misspelled variable is `undefined`
const endpoint = import.meta.env.PUBLIC_API_URL;

// Bad: a secret read in a component that is passed to a hydrated island —
// nothing in the pipeline prevents it reaching the browser bundle
const apiKey = import.meta.env.CRM_API_KEY;
---

<ContactWidget client:visible endpoint={endpoint} apiKey={apiKey} />
```

```js
// astro.config.mjs
export default defineConfig({
  site: 'https://example.com',
  // Bad: no env schema, and no content security policy at all
});
```

**Correct (schema-declared, context-separated, policy enabled):**

```js
// astro.config.mjs
import { defineConfig, envField } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',

  env: {
    schema: {
      // Public: safe in both bundles, and the browser genuinely needs it
      PUBLIC_API_URL: envField.string({ context: 'client', access: 'public' }),
      // Server-only, non-sensitive
      PORT: envField.number({
        context: 'server',
        access: 'public',
        optional: true,
        default: 4321,
      }),
      // Secret: never bundled, read at runtime on the server
      CRM_API_KEY: envField.string({ context: 'server', access: 'secret' }),
    },
  },

  security: {
    csp: {
      algorithm: 'SHA-256',
      scriptDirective: {
        // Matches the one third-party tag the site actually loads
        resources: ["'self'", 'https://cdn.example-analytics.com'],
      },
      styleDirective: {
        resources: ["'self'"],
      },
    },
  },
});
```

```astro
---
// src/components/ContactForm.astro — the public value, from the client module
import { PUBLIC_API_URL } from 'astro:env/client';
---

<ContactWidget client:visible endpoint={PUBLIC_API_URL} />
```

```ts
// src/pages/api/contact.ts — the secret stays on the server, by import path
export const prerender = false;

import { CRM_API_KEY } from 'astro:env/server';

export async function POST({ request }: { request: Request }) {
  const response = await fetch('https://crm.example.com/leads', {
    method: 'POST',
    headers: { authorization: `Bearer ${CRM_API_KEY}` },
    body: await request.text(),
  });

  return new Response(null, { status: response.ok ? 204 : 502 });
}
```

Reference: [Environment variables](https://docs.astro.build/en/guides/environment-variables/)
