---
title: Sitemap & Feed Hygiene
impact: HIGH
description: Requires generated sitemaps and feeds to list only canonical, indexable URLs, excluding drafts, noindex routes and redirect sources, with last-modified dates that reflect real changes.
tags: seo, sitemap, rss, feeds, indexing
---

## Sitemap & Feed Hygiene

**Impact (HIGH):** Installing `@astrojs/sitemap` is the easy half and the half everyone does; what it emits by default is every route the build produced. That includes the thank-you page, the internal search results route, the `noindex` staging page, the paginated archive nobody wants indexed, and — after a migration — the old _URLs_ still present as redirect sources. A sitemap is a statement that these are the pages worth crawling, so submitting one that contradicts the site's own canonical and robots directives is asking a crawler to choose between two answers. Feeds carry the same problem with an extra failure: a feed built from the wrong entry property produces links that 404 for every subscriber at once, and feed readers cache aggressively enough that the broken version outlives the fix.

**Guidelines:**

1.  **Filter the sitemap to what should actually be indexed:**
    - `@astrojs/sitemap` accepts a `filter` predicate, and it is not optional configuration on any real site
    - Exclude what the site itself marks as excluded: `noindex` routes, thank-you and confirmation pages, internal search, filtered or faceted listings, preview routes
    - Exclude redirect sources. A _URL_ that 301s belongs in the redirect map, never in the sitemap
    - Drafts are already excluded upstream, by the collection filter — a draft that reaches a route is a content-model defect, not a sitemap one
2.  **The sitemap agrees with the canonical, or it is wrong:**
    - Same origin, same trailing-slash convention, same _URL_ for the same page
    - `site` must be set for the integration to emit at all, which the metadata rule already requires
3.  **`lastmod` means the content changed:**
    - Emit it from the content's own `updatedDate`, not from the build timestamp — a build-stamped sitemap claims every page changed on every deploy, and a consumer that believes it learns to ignore it
    - Where there is no reliable modification date, omitting `lastmod` is better than fabricating one
4.  **Segment large sites rather than emitting one flat list:**
    - The integration paginates automatically past its entry limit, and `customPages`, `serialize` and per-section entries let a site express priority and change frequency where it genuinely differs
    - A blog archive and a service page do not change at the same rate, and saying so is the point of the fields
5.  **Feeds are built from the same filtered source as the pages:**
    - `@astrojs/rss` takes the collection, so it takes the same draft filter and the same sort
    - Links are built from `context.site` and the entry's `id` — Content Layer entries have no `slug`, and a feed built against `post.slug` emits `/blog/undefined/` for every item
    - Set the item's `pubDate` from the schema's date field, not from the file's mtime, which changes on checkout
6.  **Both are generated artifacts, so they are reviewed at the source:**
    - Nothing about a sitemap or feed should be hand-maintained; a hand-added entry is a fact that will stop being true
    - After a launch, fetch the emitted `/sitemap-index.xml` and confirm the count roughly matches the number of indexable pages — an order-of-magnitude gap is the fastest signal that a filter is missing

**Incorrect (everything the build emitted, and a feed built on a removed property):**

```js
// astro.config.mjs
export default defineConfig({
  site: 'https://example.com',
  // Bad: no filter. Thank-you pages, internal search, preview routes and the
  // old URLs kept for redirects are all submitted as canonical
  integrations: [sitemap()],
});
```

```js
// src/pages/rss.xml.js
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  // Bad: drafts included, and `post.slug` does not exist on Content Layer
  // entries — every link in the feed resolves to /blog/undefined/
  const posts = await getCollection('blog');

  return rss({
    title: 'Example Blog',
    description: 'Notes from the team',
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.pubDate,
      link: `/blog/${post.slug}/`,
    })),
  });
}
```

**Correct (filtered to indexable URLs, feed built from `id`):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

const EXCLUDED = ['/thank-you', '/search', '/preview'];

export default defineConfig({
  site: 'https://example.com',
  trailingSlash: 'never',
  integrations: [
    sitemap({
      // Only canonical, indexable URLs reach the sitemap
      filter: (page) => {
        const { pathname } = new URL(page);
        return !EXCLUDED.some((prefix) => pathname.startsWith(prefix));
      },
    }),
  ],
});
```

```js
// src/pages/rss.xml.js
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  // Same filter the routes use, so the feed cannot contain what the site does not
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  const sorted = posts.sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf(),
  );

  return rss({
    title: 'Example Blog',
    description: 'Notes from the team',
    site: context.site,
    items: sorted.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      // `id`, and the site's trailing-slash convention
      link: `/blog/${post.id}`,
    })),
  });
}
```

Reference: [@astrojs/sitemap](https://docs.astro.build/en/guides/integrations-guide/sitemap/)
