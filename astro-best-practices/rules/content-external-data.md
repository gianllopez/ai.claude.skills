---
title: External API Requests at Build Time
impact: HIGH
description: Requires an external fetch in the frontmatter to be bounded by a timeout, validated against a schema, and handled deliberately on failure, instead of an unbounded, unvalidated request that can hang or silently break the build.
tags: content, fetch, api, build, data
---

## External API Requests at Build Time

**Impact (HIGH):** A frontmatter `fetch()` runs at build time, and unlike a request a visitor's browser makes, nothing about its failure is visible until the build itself succeeds or fails. An API with no timeout hangs the build indefinitely instead of failing fast; an API that changes its response shape renders `undefined` where a number used to be, and the page ships that way because nothing checked; an API that is down takes every page depending on it down with it — including pages that have nothing to do with the data that failed. None of this is hypothetical for a site built around a handful of external calls: it is the first production incident that data source causes, and it always looks the same, a change on someone else's server breaking a build nobody touched.

**Guidelines:**

1.  **Fetch in the frontmatter, at build time by default:**
    - It runs on the server, so an external request belongs there like any other build-time data, resolved before the page renders
    - Fetch from the client only when the data is genuinely request-specific or interactive — that is an island's concern, not this rule's
2.  **Collection-shaped data still goes through a loader; a one-off value is a plain fetch:**
    - A list of entries with a stable schema is content — `glob()`, `file()` or a custom loader in `src/content.config.ts`, per the content collections rule
    - A single value with no collection behind it — a star count, a stock level, an exchange rate — does not need one; a plain `fetch()` in the frontmatter that needs it is the right size
3.  **Decide explicitly what a failed request does to the build:**
    - A field the page cannot render without — a required data source — is left to throw, so the build fails loudly at the file that needs it
    - A non-critical enrichment — a stat, a badge, a "trending" strip — is wrapped in `try`/`catch` with an explicit fallback, so a third-party outage degrades one section instead of blocking every page
    - What is never acceptable is catching the error and letting the page render `undefined` where the value should be — that is the failure with no signal at all
4.  **Bound every request with an explicit timeout:**
    - `fetch(url, { signal: AbortSignal.timeout(5000) })` on every external call — an API with no SLA can otherwise hang the build indefinitely, which is worse than a slow page: the whole site never deploys
    - A timeout that fires is still a failure, and guideline 3 decides what happens next
5.  **Validate the response before using it:**
    - Parse it with the same tool the content schema rule uses — a `z.object()` shape checked against the payload — so an API that changed its fields is a build error naming the field, not a silent `undefined` three components downstream
    - `response.ok` is checked before the body is read; a 404 or 500 with a JSON error body still parses as JSON if nothing checks the status first
6.  **Centralize the fetch in one function, and reach for on-demand rendering when the data is genuinely too volatile:**
    - One function per external source, in `src/lib/`, called from every page or component that needs it — not the same `fetch()` retyped at each call site with a slightly different timeout or none at all
    - Data too volatile to rebuild for is the on-demand case the rendering rule already names — `prerender = false` reads the same data at request time instead of trying to keep a static build fresh

**Incorrect (unbounded, unvalidated, duplicated, and silent on failure):**

```astro
---
// src/pages/index.astro
// Bad: no timeout, no schema, no try/catch — a slow or changed API hangs or
// silently breaks this page, and the same fetch is retyped on every page
// that shows this stat
const res = await fetch('https://api.github.com/repos/withastro/astro');
const data = await res.json();
---

<p>{data.stargazers_count} stars</p>
```

**Correct (centralized, bounded, validated, and explicit about failure):**

```ts
// src/lib/github-stats.ts
import { z } from 'astro/zod';

const RepoStatsSchema = z.object({ stargazers_count: z.number() });

export async function getRepoStats(repo: string) {
  try {
    const response = await fetch(`https://api.github.com/repos/${repo}`, {
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      throw new Error(`GitHub API responded ${response.status}`);
    }

    return RepoStatsSchema.parse(await response.json());
  } catch (error) {
    // Non-critical enrichment: degrade this section, do not fail the build
    console.warn(`Could not fetch stats for ${repo}:`, error);
    return null;
  }
}
```

```astro
---
// src/pages/index.astro
import { getRepoStats } from '@lib/github-stats';

const stats = await getRepoStats('withastro/astro');
---

{stats && <p>{stats.stargazers_count} stars</p>}
```

Reference: [Fetching data](https://docs.astro.build/en/guides/data-fetching/)
