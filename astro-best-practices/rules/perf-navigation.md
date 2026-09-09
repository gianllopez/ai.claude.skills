---
title: Prefetching & View Transitions
impact: MEDIUM
description: Uses the built-in prefetch configuration and the ClientRouter for navigation feel, with transitions expressed in CSS rather than a JavaScript animation runtime, and motion that respects a reduced-motion preference.
tags: navigation, prefetch, view-transitions, motion, performance
---

## Prefetching & View Transitions

**Impact (MEDIUM):** A multi-page site's weakest moment is the gap between clicking a link and the next page painting, and the two things that close it are both built in and both a line of configuration. Prefetching starts the request during the hover or the scroll, so the navigation resolves against a warm cache; the `<ClientRouter />` morphs the shared parts of the page instead of repainting them, so the transition reads as continuous. What makes this a rule rather than a tip is what gets reached for instead: a client-side router, or an animation library pulled in to produce a fade that _CSS_ already does. Both give up the page-per-document model — the reason the site is fast — to solve a problem the framework had already solved for free. The integrations that used to be needed here are gone: `@astrojs/prefetch` was folded into core, and `<ViewTransitions />` was removed in v6 in favour of `<ClientRouter />`.

**Guidelines:**

1.  **Turn prefetching on in configuration, then tune it per link:**
    - `prefetch: { prefetchAll: true, defaultStrategy: 'hover' }` covers a normal content site: links warm on hover, which is early enough to matter and late enough to be cheap
    - `data-astro-prefetch="viewport"` on the links that deserve it — a primary call to action, the next article — and `"tap"` on links whose target is expensive to build
    - `data-astro-prefetch="false"` on links that should never be fetched speculatively: destructive endpoints, anything metered, anything behind a paywall
    - `@astrojs/prefetch` is deprecated; a project still installing it is carrying a package core replaced
2.  **`<ClientRouter />` once, in the base layout:**
    - Imported from `astro:transitions` and rendered in the head, it applies to every page that uses that layout
    - `<ViewTransitions />` was its name before v6 and no longer exists
    - In v7 the `astro:transitions` internals — the event constants, `createAnimationScope()`, the event type guards — were removed. Lifecycle hooks use the string event names (`astro:before-swap`, `astro:after-swap`, `astro:page-load`)
3.  **Name the elements that persist across the navigation:**
    - `transition:name` on the pair of elements that are the same thing on both pages — a card and the article header it opens into, the site header, a hero image — and the browser morphs between them
    - The name must be unique per page, so it is derived from the entry's `id` rather than hardcoded on a component rendered in a list
    - `transition:persist` for elements that must survive the swap with their state intact: a playing media element, an open menu
4.  **Express the motion in CSS:**
    - View transitions are a _CSS_ mechanism; the animation belongs in a stylesheet, not in a _JavaScript_ animation runtime loaded to do what the browser does natively
    - A transition that needs a library is usually a transition doing too much — the useful ones are short, and they exist to make a change legible, not to be noticed
    - Any interactive flourish that does need scripting is an island, and pays for its `client:*` directive like any other
5.  **Motion is opt-out for the people who asked:**
    - Wrap the animation in `@media (prefers-reduced-motion: no-preference)`, or disable transitions with `<ClientRouter fallback="none" />` behind that query
    - This is not decoration: for some readers, unrequested motion is a symptom trigger
6.  **The router does not change what the site is:**
    - Pages are still documents, still prerendered, still independently addressable. The `<ClientRouter />` swaps the document; it does not introduce client-side routing state, and nothing should be built assuming it did

**Incorrect (a router and an animation library replacing what is built in):**

```astro
---
// src/layouts/Base.astro
import { ViewTransitions } from 'astro:transitions'; // removed in v6
import gsap from 'gsap'; // pulled in for a cross-fade
---

<head>
  <ViewTransitions />
</head>
<body>
  <slot />

  <!-- Bad: an animation runtime shipped to every page to do what a CSS
       keyframe already does, on a transition the browser can drive itself -->
  <script>
    document.addEventListener('astro:after-swap', () => {
      gsap.from('main', { opacity: 0, duration: 0.3 });
    });
  </script>
</body>
```

```astro
<!-- Bad: prefetch integration that core replaced, and a transition name
     hardcoded on a component rendered once per item in a list -->
<a href={`/blog/${post.id}`} transition:name="card">{post.data.title}</a>
```

**Correct (built-in prefetch and router, motion in CSS, reduced-motion respected):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
  prefetch: {
    prefetchAll: true,
    defaultStrategy: 'hover',
  },
});
```

```astro
---
// src/layouts/Base.astro
import { ClientRouter } from 'astro:transitions';
---

<html lang="en">
  <head>
    <ClientRouter />
  </head>
  <body>
    <slot />
  </body>
</html>

<style is:global>
  /* The transition is CSS, and only for readers who have not asked otherwise */
  @media (prefers-reduced-motion: no-preference) {
    ::view-transition-old(root) {
      animation: fade-out 120ms ease-out;
    }
    ::view-transition-new(root) {
      animation: fade-in 160ms ease-in;
    }
  }

  @keyframes fade-out {
    to {
      opacity: 0;
    }
  }
  @keyframes fade-in {
    from {
      opacity: 0;
    }
  }
</style>
```

```astro
---
// src/components/PostCard.astro
interface Props {
  post: { id: string; data: { title: string } };
}

const { post } = Astro.props;
---

<!-- Unique per entry, so the card morphs into the right article header -->
<a
  href={`/blog/${post.id}`}
  data-astro-prefetch="viewport"
  transition:name={`post-${post.id}`}
>
  {post.data.title}
</a>
```

Reference: [View transitions](https://docs.astro.build/en/guides/view-transitions/)
