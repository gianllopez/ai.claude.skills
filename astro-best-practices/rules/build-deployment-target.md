---
title: Deployment Target & Toolchain Floor
impact: MEDIUM
description: Ships prerendered output to an edge CDN with the adapter and output mode stated explicitly, and pins the Node and toolchain versions the project is actually built against.
tags: deployment, adapter, cdn, node, toolchain
---

## Deployment Target & Toolchain Floor

**Impact (MEDIUM):** A prerendered _Astro_ site is a directory of files, and the whole point of producing it at build time is that serving it needs nothing more than a _CDN_ — no origin server, no cold start, no runtime to patch, and a copy in the data centre nearest each visitor. Deploying that output to a long-running server keeps every cost of a server and none of its benefits. The mirror defect is an adapter installed because a tutorial had one, which quietly opts the project into on-demand rendering it never needed. The toolchain floor is the other half: v7 requires **Node v22.12.0 or higher** and does not support odd-numbered majors, so a _CI_ image or a host default on an older or odd release fails in a way that reads as a code error. Stating the version in the project is what turns that into an immediate, obvious failure instead of a confusing one.

**Guidelines:**

1.  **Deploy static output to an edge platform:**
    - _Cloudflare Pages_, _Netlify_ and _Vercel_ all build and serve _Astro_ with no configuration, and the output is files
    - The choice among them is an operational one — this rule only requires that the target serves from an edge network rather than a single origin
2.  **The adapter follows the rendering decision, not the other way round:**
    - A fully prerendered site with no on-demand routes and no server islands needs no adapter
    - Install one when a route sets `prerender = false`, when a component uses `server:defer`, or when the platform's own features require it — and let its presence signal that something on the site renders on demand
    - Adapter and `output` are read together: the static-output rule owns which routes render where, and this rule owns where the result is served
3.  **State the platform's expectations in the project:**
    - `engines.node` in `package.json`, and the same version in the _CI_ configuration and the host's build settings — three places that will otherwise drift
    - Even-numbered majors only; v22.12.0 is the current floor
    - Lock the package manager version too where the host respects it, so a local build and a deploy build resolve the same tree
4.  **Build the way the platform builds:**
    - Run `astro build` in _CI_ on the same _Node_ version the host uses, and treat a warning-free local build on a different major as unverified
    - `astro check` in the same pipeline catches the type and template errors that a build alone can let through
5.  **Keep the deploy output reviewable:**
    - The build emits `dist/`; nothing should be edited there, and nothing generated should be committed
    - Where a host needs headers, redirects or a routing file, generate it from configuration — the redirect map already lives in `astro.config.mjs`

**Incorrect (an adapter and a server for output that is entirely static, versions unstated):**

```json
{
  "name": "example-site",
  "scripts": {
    "build": "astro build",
    "start": "node ./dist/server/entry.mjs"
  }
}
```

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  site: 'https://example.com',
  // Bad: every page is static, and they are being served by a long-running
  // Node process that has to be deployed, monitored and patched
  output: 'server',
  adapter: node({ mode: 'standalone' }),
});
```

**Correct (static output to an edge CDN, versions pinned):**

```json
{
  "name": "example-site",
  "engines": {
    "node": ">=22.12.0"
  },
  "packageManager": "yarn@4.5.0",
  "scripts": {
    "build": "astro check && astro build",
    "preview": "astro preview"
  }
}
```

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
  trailingSlash: 'never',
  // Prerendered output, served as files from the edge. No adapter, because
  // no route on this site renders on demand
  output: 'static',
});
```

```yaml
# .github/workflows/deploy.yml — the same floor the host uses
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22.12.0'
      - run: yarn install --immutable
      - run: yarn build
```

Reference: [Deploy your Astro site](https://docs.astro.build/en/guides/deploy/)
