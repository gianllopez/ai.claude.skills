---
title: Site URL, Metadata & Canonicals
impact: CRITICAL
description: Requires the site option to be set and every page's title, description, canonical and robots behaviour to be produced by one shared component rather than assembled per page.
tags: seo, metadata, canonical, head, configuration
---

## Site URL, Metadata & Canonicals

**Impact (CRITICAL):** `site` is one line of configuration that several unrelated things silently depend on: `Astro.site`, every absolute _URL_ built from it, the sitemap integration (which refuses to run without it), and canonical tags. Omitted, none of them fail loudly — the sitemap is simply absent and canonicals are relative or missing, which is exactly the failure mode nobody notices until a crawl report arrives. The larger defect is metadata assembled by hand in each page. It starts as three tags copied between templates and becomes a site where a third of the pages share one description, two pages claim the same canonical, and a route that was duplicated for a campaign is competing with its own original. Metadata is generated content — derived from the content model by one component — and the moment it is typed per page it begins to drift.

**Guidelines:**

1.  **Set `site` in `astro.config.mjs`, always:**
    - It is the production origin, with no trailing slash: `site: 'https://example.com'`
    - Without it `Astro.site` is `undefined`, absolute _URLs_ silently become relative, and `@astrojs/sitemap` does not emit
2.  **One head component owns metadata for the whole site:**
    - It takes `title`, `description` and the optional overrides as props, and every layout renders it — there is no second place a `<title>` is written
    - Defaults live in it: the site name suffix, the fallback social image, the default `robots` value
    - Per-page-type rules live in it too. A blog post's title pattern, a service page's, the home page's — expressed once as a function of the page type, not retyped per file
3.  **Derive the canonical, do not write it:**
    - `new URL(Astro.url.pathname, Astro.site)` is the canonical for almost every page, and being derived it cannot disagree with the route it sits on
    - Accept an override prop for the genuine exceptions — a migrated _URL_, a syndicated copy, a filtered view that should point at its unfiltered parent — and let it come from the content schema, so the exception is data and reviewable
    - A hand-typed canonical is the single most common way two pages end up claiming to be the same page
4.  **Make `noindex` a decision with a reason:**
    - Thank-you pages, filtered or faceted listings, internal search results, staging routes, paginated pages beyond the first where the site does not want them indexed
    - It belongs in the same component as a prop, so a `noindex` page is visible as such at the call site rather than hidden in a stray meta tag
    - The inverse defect is real and worse: a `noindex` left over from a staging deploy on a page that should rank
5.  **Open Graph and social tags come from the same source as the page's own:**
    - `og:title` restating the page title and `og:description` restating the description is correct — what is not correct is a second, hand-written pair that drifts from the first
    - `og:url` is the canonical. If they can disagree, they eventually will
6.  **Titles and descriptions are content, so they belong to the schema:**
    - The content rules already require them; this rule is what consumes them
    - A page type with no content entry behind it — a landing page written as a route — still passes explicit props, and still through the same component

**Incorrect (`site` missing, metadata typed per page, canonical hand-written):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  // Bad: no `site`. Astro.site is undefined and the sitemap emits nothing
  integrations: [sitemap()],
});
```

```astro
---
// src/pages/services/migration.astro
---

<html lang="en">
  <head>
    <!-- Bad: three tags copied from another page, one of them not updated.
         The canonical is typed by hand and points at the page it was copied from -->
    <title>Migration services</title>
    <meta name="description" content="We help teams move their site." />
    <link rel="canonical" href="https://example.com/services/redesign" />
    <meta property="og:title" content="Website migration | Example" />
  </head>
  <body>
    <slot />
  </body>
</html>
```

**Correct (`site` set, one head component, canonical derived):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://example.com',
  integrations: [sitemap()],
});
```

```astro
---
// src/components/SeoHead.astro — the only place metadata is written
interface Props {
  title: string;
  description: string;
  pageType?: 'home' | 'article' | 'service';
  canonicalOverride?: string;
  noindex?: boolean;
  image?: string;
}

const {
  title,
  description,
  pageType = 'service',
  canonicalOverride,
  noindex = false,
  image = '/og-default.png',
} = Astro.props;

const SITE_NAME = 'Example';

// Title rules per page type, stated once
const fullTitle = pageType === 'home' ? SITE_NAME : `${title} | ${SITE_NAME}`;

// Derived, so it cannot disagree with the route it renders on
const canonical = canonicalOverride ?? new URL(Astro.url.pathname, Astro.site);
const socialImage = new URL(image, Astro.site);
---

<title>{fullTitle}</title>
<meta name="description" content={description} />
<link rel="canonical" href={canonical} />
{noindex && <meta name="robots" content="noindex, nofollow" />}

<meta property="og:title" content={fullTitle} />
<meta property="og:description" content={description} />
<meta property="og:url" content={canonical} />
<meta property="og:image" content={socialImage} />
<meta name="twitter:card" content="summary_large_image" />
```

```astro
---
// src/layouts/Base.astro — every page reaches metadata through here
import SeoHead from '@components/SeoHead.astro';

interface Props {
  title: string;
  description: string;
  pageType?: 'home' | 'article' | 'service';
  canonicalOverride?: string;
  noindex?: boolean;
}

const props = Astro.props;
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <SeoHead {...props} />
  </head>
  <body>
    <slot />
  </body>
</html>
```

Reference: [Configuration reference: site](https://docs.astro.build/en/reference/configuration-reference/)
