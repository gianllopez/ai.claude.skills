---
title: Third-Party Scripts & Embeds
impact: HIGH
description: Keeps analytics tags, widgets and embeds out of the global layout, scoped to the routes that need them and loaded so they cannot block or shift the page.
tags: performance, scripts, embeds, analytics, layout
---

## Third-Party Scripts & Embeds

**Impact (HIGH):** A third-party script is code from another origin, of unknown size, on an unknown release schedule, that a project has agreed to execute on every page. Put in the base layout — which is where it always goes, because that is the one file that covers the whole site — a chat widget added for the pricing page also loads on every blog post, and a tag manager becomes a hole through which any number of further scripts arrive without ever appearing in a diff. The effect is that a site built to ship almost no _JavaScript_ ends up shipping several hundred kilobytes of someone else's, and the framework's entire advantage is spent. Embeds are the same problem in visible form: a video iframe or a social post pulls its own runtime and, having no reserved space, shifts the article around it when it loads.

**Guidelines:**

1.  **Nothing third-party goes in the base layout by default:**
    - The question for every tag is which routes actually need it, and the answer is rarely "all of them"
    - A widget that belongs on one page belongs in that page, or in a component that page renders
    - Where a tag genuinely is site-wide — a single analytics beacon — it is still one deliberate entry, not an open-ended container that can load more
2.  **Scope by route, and make the scope visible:**
    - A layout prop (`<Base showChat>`) or a per-page component keeps the decision readable at the call site
    - The alternative — a script that checks `location.pathname` before doing anything — has already been downloaded and executed by the time it decides not to run
3.  **Load them so they cannot block:**
    - `is:inline` opts a `<script>` out of bundling, which is what a third-party snippet usually requires; everything else stays bundled and processed by _Vite_
    - Non-critical tags load `async` or `defer`, and the ones that only matter after interaction can wait for it
    - A synchronous third-party script in the head is a render-blocking request to an origin you do not control
4.  **Give every embed reserved space:**
    - An iframe with a fixed aspect ratio and explicit dimensions does not move the content below it when it loads
    - The heavier the embed, the better the case for a facade — a static poster image that swaps in the real embed on click, so the runtime arrives only for readers who wanted it
5.  **A tag manager is a delegation of this rule, not an exemption from it:**
    - It is one script that can load arbitrarily many more, none of which pass through review
    - If one is required, the constraint has to be enforced where the container is edited, and the site's own performance budget is what it is measured against
6.  **Review flags:**
    - A `<script src>` pointing at another origin, added to a layout rather than a page
    - An iframe with no width, height or aspect ratio
    - Any new third-party origin in the network waterfall that no diff introduced explicitly

**Incorrect (everything in the base layout, blocking, and an unsized embed):**

```astro
---
// src/layouts/Base.astro
---

<html lang="en">
  <head>
    <!-- Bad: render-blocking, on every page, from an origin you do not control -->
    <script src="https://cdn.example-analytics.com/tag.js"></script>

    <!-- Bad: a container that can load any number of further scripts, none of
         which will ever appear in a diff -->
    <script is:inline>
      (function (w, d, s, l, i) {
        /* tag manager bootstrap */
      })(window, document, 'script', 'dataLayer', 'GTM-XXXX');
    </script>
  </head>
  <body>
    <slot />

    <!-- Bad: a chat widget needed on one page, loaded on all of them -->
    <script src="https://widget.example-chat.com/loader.js" is:inline></script>
  </body>
</html>
```

```astro
<!-- Bad: no dimensions, so the article reflows when the player loads -->
<iframe src="https://www.youtube.com/embed/VIDEO_ID"></iframe>
```

**Correct (scoped to the routes that need it, non-blocking, embeds sized):**

```astro
---
// src/layouts/Base.astro — third-party surface is a prop, visible at the call site
interface Props {
  title: string;
  description: string;
  showChat?: boolean;
}

const { showChat = false, ...seo } = Astro.props;
---

<html lang="en">
  <head>
    <SeoHead {...seo} />
    <!-- The one site-wide beacon: deferred, and it is the only one -->
    <script
      is:inline
      defer
      src="https://cdn.example-analytics.com/tag.js"
      data-site="example"></script>
  </head>
  <body>
    <slot />
    {
      showChat && (
        <script
          is:inline
          async
          src="https://widget.example-chat.com/loader.js"
        />
      )
    }
  </body>
</html>
```

```astro
---
// src/pages/pricing.astro — the page that needs the widget asks for it
import Base from '@layouts/Base.astro';
---

<Base title="Pricing" description="Plans and pricing." showChat>
  <h1>Pricing</h1>
</Base>
```

```astro
---
// src/components/VideoEmbed.astro — space reserved, loaded lazily
interface Props {
  id: string;
  title: string;
}

const { id, title } = Astro.props;
---

<div class="aspect-video w-full">
  <iframe
    src={`https://www.youtube-nocookie.com/embed/${id}`}
    title={title}
    width="560"
    height="315"
    loading="lazy"
    class="h-full w-full"
    allowfullscreen></iframe>
</div>
```

Reference: [Scripts and event handling](https://docs.astro.build/en/guides/client-side-scripts/)
