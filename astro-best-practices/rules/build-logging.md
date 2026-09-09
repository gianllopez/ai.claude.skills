---
title: Structured Build Logging
impact: LOW
description: Uses Astro.logger for build-time diagnostics and configures the stable top-level logger handler, instead of console.log lines that carry no level and no context.
tags: logging, build, diagnostics, configuration
---

## Structured Build Logging

**Impact (LOW):** A `console.log` in an `.astro` frontmatter runs at build time and prints into the middle of the build output with no level, no source and no timestamp, indistinguishable from the framework's own lines — so it is either lost in the noise or left behind as noise for everyone else. Worse, a warning printed that way is not a warning: it goes to stdout like everything else, so a _CI_ job filtering stderr never sees it, and a condition worth reporting — a collection that came back empty, a page built with no items — passes silently. `Astro.logger` gives the levels, routes errors to stderr, and labels the source; the stable top-level `logger` option decides the format, so the same code produces readable output locally and machine-parsable output in _CI_.

**Guidelines:**

1.  **Use `Astro.logger` in pages, components and endpoints:**
    - `info` for something worth stating once per build, `warn` for a condition that should be looked at, `error` for one that should fail a review
    - Errors go to stderr and everything else to stdout, which is what makes level filtering work downstream
    - Integrations receive their own logger through the hook parameters rather than reaching for the global one
2.  **Log conditions, not progress:**
    - The valuable lines are the ones that report something unexpected: a collection with zero entries, a page rendered with a missing optional field, a fallback that had to be used
    - A line printed unconditionally on every build is a line everyone learns to skip
3.  **Configure the handler at the top level:**
    - `logger` is a stable top-level config field as of v7 — not `experimental.logger`, which is what pre-v7 material shows
    - `logHandlers.json({ level: 'info' })` from `astro/config` produces structured output for _CI_ and log aggregation; a custom handler is declared with `{ entrypoint, config }`, and the entrypoint must be a _JavaScript_ file
    - The `--json` _CLI_ flag switches the format for a single run without touching the config
4.  **Do not log what does not belong in a build log:**
    - Secrets, request data, and full objects that will be dumped on every page of a collection
    - A build log is read by whoever is diagnosing a failure; volume is what makes it useless
5.  **Client-side logging is a different problem:**
    - Frontmatter runs at build time, so `Astro.logger` never reaches the browser. A `console` call inside a `<script>` or an island is client code, and belongs to the rules that govern that code

**Incorrect (unlabelled progress lines, and a warning that is not one):**

```astro
---
// src/pages/blog/index.astro
import { getCollection } from 'astro:content';

const posts = await getCollection('blog', ({ data }) => !data.draft);

// Bad: no level, no source, printed on every build, lost in the framework's
// own output
console.log('Building blog index');
console.log(posts);

// Bad: this is a warning printed to stdout, so CI filtering never sees it
if (posts.length === 0) {
  console.log('no posts!');
}
---
```

**Correct (levels that mean something, handler configured for the environment):**

```js
// astro.config.mjs
import { defineConfig, logHandlers } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
  // Stable top-level field in v7. Structured output for CI; the --json CLI
  // flag switches a single run without editing this
  logger: logHandlers.json({ level: 'info' }),
});
```

```astro
---
// src/pages/blog/index.astro
import { getCollection } from 'astro:content';

const posts = await getCollection('blog', ({ data }) => !data.draft);

// Reports a condition, at a level that routes correctly
if (posts.length === 0) {
  Astro.logger.warn('Blog index built with no published posts');
}
---

<Layout title="Blog" description="Notes from the team">
  {posts.map((post) => <PostCard post={post} />)}
</Layout>
```

Reference: [Configuration reference: logger](https://docs.astro.build/en/reference/configuration-reference/)
