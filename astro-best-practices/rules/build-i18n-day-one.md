---
title: Internationalization on Day One
impact: MEDIUM
description: Configures i18n routing before routes and links exist, even for a single-language site, and builds every internal link with getRelativeLocaleUrl().
tags: i18n, routing, links, configuration
---

## Internationalization on Day One

**Impact (MEDIUM):** Internationalization is the one configuration decision whose cost is almost entirely in when it is made. Configured at the start it is a handful of lines and a helper used for internal links — the site has one locale, the routing behaves exactly as it did, and nothing about day-to-day work changes. Retrofitted, it is a restructure: `src/pages/` gains a level, every route moves, every internal link in every component and content file has to be found and rewritten, the content collections are reorganised by locale, and redirects have to preserve the _URLs_ that were already indexed. The work is not difficult, it is broad and mechanical, and it touches files that had no other reason to change. Since the up-front version is cheap even for a site that never adds a second language, the default is to configure it.

**Guidelines:**

1.  **Configure `i18n` before the routes exist:**
    - `defaultLocale`, the `locales` list, and the routing behaviour
    - `routing: { prefixDefaultLocale: false }` keeps the default locale unprefixed, so a single-language site has exactly the _URLs_ it would have had anyway — `/blog`, not `/en/blog`
    - Adding a locale later is then a list entry and a content directory, not a migration
2.  **Build internal links with the helper, always:**
    - `getRelativeLocaleUrl(locale, path)` produces the correct _URL_ for the current locale, so a link written once keeps working when a second locale arrives
    - `Astro.currentLocale` is the locale for the page being rendered
    - A hardcoded `href="/blog"` is the thing that has to be found and rewritten later, and there are always more of them than expected — navigation, footers, cards, calls to action, and links inside content
3.  **Organise content by locale from the start:**
    - A locale segment in the collection's directory structure (`src/data/blog/en/`, `src/data/blog/es/`) keeps entries addressable per language without a second collection
    - The locale becomes part of the route params, so the dynamic route builds both languages from one file
4.  **Say which language a page is in:**
    - The `lang` attribute on `<html>` comes from the current locale, not from a hardcoded string in the base layout
    - A site serving two languages under one hardcoded `lang` is misdescribing every page in the other one
5.  **Where a second locale is genuinely never coming:**
    - The configuration still costs one block and prevents the retrofit if that assumption changes
    - The one thing not worth building ahead of time is the translation machinery — dictionaries, locale switchers, `hreflang` output. Those arrive with the second locale; the routing is what has to exist before it

**Incorrect (no configuration, links hardcoded, language asserted):**

```astro
---
// src/layouts/Base.astro
---

<!-- Bad: hardcoded. Every page in a second language will claim to be English -->
<html lang="en">
  <body>
    <nav>
      <!-- Bad: absolute paths that will each need rewriting when a locale
           prefix appears -->
      <a href="/blog">Blog</a>
      <a href="/services">Services</a>
      <a href="/contact">Contact</a>
    </nav>
    <slot />
  </body>
</html>
```

**Correct (configured up front, links and language derived):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'es'],
    routing: {
      // The default locale stays unprefixed: /blog, not /en/blog
      prefixDefaultLocale: false,
    },
  },
});
```

```astro
---
// src/layouts/Base.astro
import { getRelativeLocaleUrl } from 'astro:i18n';

const locale = Astro.currentLocale ?? 'en';

const links = [
  { path: '/blog', label: 'Blog' },
  { path: '/services', label: 'Services' },
  { path: '/contact', label: 'Contact' },
];
---

<html lang={locale}>
  <body>
    <nav>
      {
        links.map(({ path, label }) => (
          <a href={getRelativeLocaleUrl(locale, path)}>{label}</a>
        ))
      }
    </nav>
    <slot />
  </body>
</html>
```

```astro
---
// src/pages/[...locale]/blog/[id].astro — both locales from one route file
import { getCollection } from 'astro:content';

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);

  return posts.map((post) => {
    const [locale, ...rest] = post.id.split('/');

    return {
      params: { locale: locale === 'en' ? undefined : locale, id: rest.join('/') },
      props: { post },
    };
  });
}
---
```

Reference: [Internationalization](https://docs.astro.build/en/guides/internationalization/)
