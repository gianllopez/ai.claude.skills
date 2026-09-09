---
title: Static Output by Default
impact: CRITICAL
description: Requires build-time rendering as the project's default and on-demand rendering as a per-route opt-in that names the request-time data it needs.
tags: rendering, output, prerender, adapter
---

## Static Output by Default

**Impact (CRITICAL):** This is the decision every other performance rule inherits. A prerendered page is a file on a CDN — it has no cold start, no runtime dependency, no per-request cost, and it cannot fail at request time because there is nothing to run. An on-demand page gives all of that up, and it gives it up per request, forever. The defect is almost never a deliberate choice to render on the server; it is `output: 'server'` set once so that one route could read a cookie, silently converting an entire marketing site into a runtime. Stating the mode explicitly is what makes the mismatch visible: when the config says the site is static and a route needs the server, the opt-out appears in that route's diff, where a reviewer can ask what request-time data justifies it.

**Guidelines:**

1.  **State the mode, even though it is the default:**
    - `output: 'static'` is what _Astro_ does with no configuration, and writing it down is still worth the line — it declares the architecture, so a later `output: 'server'` reads as a change to it rather than as setup
    - Prerendering is the whole point of choosing _Astro_. A project that renders everything on demand has bought a build step and given up the reason for it
2.  **Opt into on-demand rendering one route at a time:**
    - With an adapter installed, `export const prerender = false` in a single page or endpoint renders that route on demand and leaves every other route static
    - The inverse exists for projects that genuinely are server-first: under `output: 'server'`, `export const prerender = true` pulls a route back to build time. Reach for that mode only when most routes need the server
    - An adapter is required for on-demand rendering, and also for server islands (`server:defer`) — installing one does not by itself make the site dynamic
3.  **The bar for a route to leave build time:**
    - It needs data that only exists at request time: the signed-in user, a session, a cookie, a query the build cannot know
    - It needs data too volatile to rebuild for: inventory, prices, live availability
    - It accepts a request body — a form endpoint, a webhook receiver
    - None of these is "the content changes sometimes". Content that changes on a schedule is a rebuild, not a render; content that changes from a _CMS_ is a build hook or a live collection
4.  **Marketing pages, blogs, documentation and landing pages are static, without exception:**
    - They are exactly the pages whose value depends on being fast and indexable, and exactly the pages with no request-time input
    - A personalised greeting on an otherwise static page is an island, not a reason to render the page on the server
5.  **Read the mode as a review signal:**
    - A diff that adds `output: 'server'` should name the routes that need it. If the answer is "one", the answer is `prerender = false` on that one
    - A diff that adds an adapter to a fully static project is either preparing for a specific on-demand route or is unnecessary

**Incorrect (one dynamic route converts the whole site to a runtime):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  // Bad: set so that /account could read a session. Every marketing page,
  // every blog post and every landing page is now rendered per request
  output: 'server',
  adapter: node({ mode: 'standalone' }),
});
```

```astro
---
// src/pages/index.astro — nothing here needs a server, and it gets one anyway
import Layout from '@layouts/Base.astro';
import { getCollection } from 'astro:content';

const services = await getCollection('services');
---

<Layout title="Home">
  {services.map((service) => <ServiceCard service={service.data} />)}
</Layout>
```

**Correct (static everywhere, on demand where the request is the input):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  // Declared, not assumed: the site is prerendered
  output: 'static',
  // Present only so individual routes can opt out below
  adapter: node({ mode: 'standalone' }),
});
```

```astro
---
// src/pages/account/index.astro — the session is request-time input,
// so this one route leaves build time and says so
export const prerender = false;

import Layout from '@layouts/Base.astro';

const user = await getUserFromSession(Astro.request.headers.get('cookie'));
---

<Layout title="Your account">
  <h1>Welcome back, {user.name}</h1>
</Layout>
```

Reference: [On-demand rendering](https://docs.astro.build/en/guides/on-demand-rendering/)
