---
title: Route Responsibility, Layouts & Slots
impact: HIGH
description: Keeps route files to assembling data and composing components, with repeated structure owned by layouts and exposed through slots rather than repeated per page.
tags: architecture, routing, layouts, slots, structure
---

## Route Responsibility, Layouts & Slots

**Impact (HIGH):** A route file's job is to answer one question — what is on this page — and the moment it also contains the header markup, the metadata tags, the footer and three inlined sections, that answer is buried in a file nobody can scan. The cost is not aesthetic. Repeated structure means a change to the site's framing is a change to every route that copied it, so the header gets updated in eleven files and missed in the twelfth, and the missed one is discovered by a reader. The same applies to metadata: page framing is where `<title>` and canonicals live, and a route that assembles its own head is a route that can drift from the site's rules. Layouts exist precisely so that the repeated part has one definition and the varying part arrives through slots.

**Guidelines:**

1.  **A route file assembles; it does not contain:**
    - Fetch or read the page's data in the frontmatter, choose a layout, pass props, compose components
    - Section markup written inline in a route is a component that has not been extracted yet — it stays inline only while it is genuinely single-use, which the component rule covers
    - A route that has grown past roughly a screen of markup is usually holding something that belongs elsewhere
2.  **Layouts own everything that repeats:**
    - The document shell, the metadata component, global navigation, breadcrumbs, footer, skip links, the structured-data hook
    - Layouts compose: a `Base` layout holding the document, an `Article` layout wrapping it with the parts every article shares. Nesting them beats duplicating either
    - Defaults live in the layout, so a page that does not care gets a correct value without stating one
3.  **Slots are the interface between the two:**
    - The default slot for the page's content, and named slots for the framing a page can fill — an aside, a hero, a set of actions in the header
    - `<slot name="x" />` with fallback content inside it means a page that provides nothing still renders correctly
    - A layout that takes markup as a prop instead of a slot is working around the mechanism designed for it
4.  **Directory conventions carry meaning, so keep them:**
    - `src/pages/` is routing and nothing else — every file in it is a _URL_
    - `src/layouts/` for page framing, `src/components/` for everything composable, `src/content.config.ts` with the content it describes, `src/lib/` (or `src/utils/`) for logic that is not a component, `src/styles/` for global stylesheets
    - Group routes by section (`src/pages/blog/`, `src/pages/services/`) so a directory listing describes the site's shape
5.  **Data belongs at the top of the route, not scattered through it:**
    - Everything the page needs is resolved in the frontmatter, so a reader knows the page's inputs without scanning its markup
    - `getStaticPaths()` returns both `params` and `props`, so a dynamic route hands its entry down rather than re-fetching it lower
6.  **The test:**
    - Adding a new page of an existing type should require writing only what makes it different. If it requires copying framing, metadata or navigation, the layout is not doing its job

**Incorrect (a route that contains the whole document, and metadata assembled per page):**

```astro
---
// src/pages/services/migration.astro
const testimonials = await getTestimonials();
---

<!-- Bad: the document shell, the nav, the metadata and every section inline.
     Changing the header means editing this file and every sibling like it -->
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Migration services | Example</title>
    <meta name="description" content="We help teams move their site." />
    <link rel="canonical" href="https://example.com/services/migration" />
  </head>
  <body>
    <header class="site-header">
      <a href="/">Example</a>
      <nav>
        <a href="/blog">Blog</a>
        <a href="/services">Services</a>
      </nav>
    </header>

    <main>
      <section class="hero">
        <h1>Website migration</h1>
        <p>Move without losing what you have built.</p>
      </section>

      <section class="testimonials">
        {
          testimonials.map((t) => (
            <figure>
              <blockquote>{t.quote}</blockquote>
              <figcaption>{t.author}</figcaption>
            </figure>
          ))
        }
      </section>
    </main>

    <footer class="site-footer">© Example</footer>
  </body>
</html>
```

**Correct (the layout owns the framing, the route assembles the page):**

```astro
---
// src/layouts/Base.astro — the shell, once
import SeoHead from '@components/SeoHead.astro';
import SiteHeader from '@components/SiteHeader.astro';
import SiteFooter from '@components/SiteFooter.astro';

interface Props {
  title: string;
  description: string;
  pageType?: 'home' | 'article' | 'service';
}

const props = Astro.props;
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <SeoHead {...props} />
    <slot name="head" />
  </head>
  <body>
    <SiteHeader />
    <main>
      <slot />
    </main>
    <SiteFooter />
  </body>
</html>
```

```astro
---
// src/pages/services/migration.astro — only what makes this page different
import Base from '@layouts/Base.astro';
import Hero from '@components/Hero.astro';
import TestimonialList from '@components/TestimonialList.astro';

const testimonials = await getTestimonials();
---

<Base
  title="Website migration"
  description="Move without losing what you have built."
  pageType="service"
>
  <Hero
    title="Website migration"
    subtitle="Move without losing what you have built."
  />
  <TestimonialList items={testimonials} />
</Base>
```

Reference: [Project structure](https://docs.astro.build/en/basics/project-structure/)
