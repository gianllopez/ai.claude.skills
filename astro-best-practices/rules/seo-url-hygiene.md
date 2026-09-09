---
title: URL Hygiene, Redirects & Migration
impact: HIGH
description: Requires one trailing-slash convention across the site, and old URLs mapped and redirected before launch with internal links updated to their final targets.
tags: seo, urls, redirects, migration, routing
---

## URL Hygiene, Redirects & Migration

**Impact (HIGH):** A _URL_ is an identifier, and a site that serves the same page under two identifiers has told search engines it has two pages. `/blog` and `/blog/` is the common case, and no search engine cares which convention a site picks — it only cares that the site picks one. Mixed conventions arrive by accident: `trailingSlash` left at its default while links are typed both ways, so internal links, canonicals and the sitemap disagree with each other and with what the host actually serves. Migration is the same defect at scale. A relaunch that changes _URL_ structure without a redirect map does not lose ranking gradually; it drops every indexed _URL_ to a 404 at once, and the pages that took years to earn their position start over. Both are cheap to prevent before launch and expensive to repair after.

**Guidelines:**

1.  **Choose `trailingSlash` explicitly and let everything follow it:**
    - `trailingSlash: 'always'` or `'never'` in `astro.config.mjs` — the value matters far less than it being stated
    - Internal links, canonicals, sitemap entries and feed links all have to agree with it. A derived canonical (see the metadata rule) inherits this for free; hand-typed links do not
    - Confirm the host agrees: some platforms rewrite or redirect one form to the other, and a config that disagrees with the host produces a redirect on every internal navigation
2.  **Slugs are part of the content model, not an afterthought:**
    - Lowercase, hyphenated, no dates or ids unless they carry meaning, no stop words added for length
    - The entry `id` produces the slug by default; where a _URL_ has to differ from the filename, the override belongs in frontmatter so it is reviewable
    - A slug change is a _URL_ change, which means it is a redirect — not a rename
3.  **A migration starts with an inventory, before any code:**
    - Export the existing _URL_ list from analytics, the old sitemap and search console — not from the old codebase, which does not know which _URLs_ are actually indexed
    - Map every one to its new target, and preserve the path where there is no reason to change it. "While we are here" restructuring is how migrations lose pages
    - _URLs_ with no successor get a redirect to the nearest genuine equivalent, or are allowed to 404 deliberately — a blanket redirect of everything to the home page is treated as a soft 404 and helps nothing
4.  **Declare redirects in configuration, not in markup:**
    - `redirects` in `astro.config.mjs` keeps the map in one reviewable place and emits the right thing for the target platform
    - A meta-refresh tag or a client-side `location.replace()` is not a redirect: it costs a page load, and it does not pass the signal a 301 does
    - Use a permanent status for a permanent move; a temporary redirect on a permanent change keeps the old _URL_ alive indefinitely
5.  **Update internal links to the final target:**
    - Links pointing at a redirect still work, which is why they survive — each one is a wasted round trip and a diluted signal
    - After a migration, the internal link set is part of what gets updated, not something the redirects excuse
6.  **Verify after deployment, not before:**
    - Redirect behaviour depends on the host as much as the config, so the check that matters runs against production
    - Spot-check the highest-traffic old _URLs_ for a single-hop redirect to a 200, and watch for chains — a redirect to a redirect is a configuration that has been edited twice and reconciled zero times

**Incorrect (mixed conventions, and a relaunch with no map):**

```js
// astro.config.mjs
export default defineConfig({
  site: 'https://example.com',
  // Bad: unstated. Links are typed both ways and nothing reconciles them
});
```

```astro
<!-- Bad: three conventions in one nav, and a client-side redirect standing in
     for the old URL structure -->
<a href="/blog">Blog</a>
<a href="/services/">Services</a>
<a href="https://example.com/about">About</a>

<script>
  if (location.pathname.startsWith('/old-blog')) {
    location.replace('/blog');
  }
</script>
```

**Correct (one convention, redirects declared, links pointing at final targets):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
  trailingSlash: 'never',

  // The migration map, reviewable in one place. Permanent moves, permanent status
  redirects: {
    '/old-blog/[...slug]': {
      status: 301,
      destination: '/blog/[...slug]',
    },
    '/services/website-migration-2024': {
      status: 301,
      destination: '/services/migration',
    },
  },
});
```

```astro
---
// src/components/SiteNav.astro — one convention, links to final targets
const links = [
  { href: '/blog', label: 'Blog' },
  { href: '/services', label: 'Services' },
  { href: '/about', label: 'About' },
];
---

<nav>
  {links.map(({ href, label }) => <a href={href}>{label}</a>)}
</nav>
```

Reference: [Configured redirects](https://docs.astro.build/en/guides/routing/)
