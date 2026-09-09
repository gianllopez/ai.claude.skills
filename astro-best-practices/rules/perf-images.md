---
title: Image Handling & Layout Stability
impact: HIGH
description: Requires images to go through the built-in Image and Picture components with intrinsic dimensions, deliberate LCP handling for the hero, and lazy loading everywhere below the fold.
tags: images, assets, performance, cls, lcp
---

## Image Handling & Layout Stability

**Impact (HIGH):** A raw `<img src="/hero.png">` in an _Astro_ project skips everything the framework already does: no modern format, no compression, no generated `srcset`, and — because the file is served from `public/` untouched — no intrinsic `width` and `height` in the markup. That last one is the expensive part. Without dimensions the browser reserves no space, so every image on the page shifts the content below it when it decodes, and the reader loses their place on a page that had already rendered. The mirror defect is treating every image the same: lazy-loading the hero delays the largest element on the page past the point where it is measured, so the fix for one problem becomes the cause of another. Images are usually most of a page's bytes, so this is where a build-time framework either pays for itself or does not.

**Guidelines:**

1.  **Import local images and render them through `<Image />`:**
    - `import hero from '../assets/hero.png'` gives _Astro_ the dimensions and the file, so it emits a modern format, compresses, and writes `width` and `height` into the markup
    - Images in `public/` are copied verbatim and optimised by nothing. That is the correct place for a favicon or an _OG_ image referenced by _URL_, and the wrong place for content images
    - `alt` is required by the component, which is the point: an image with no alternative text has to say so with `alt=""`
2.  **`<Picture />` when the browser should choose:**
    - `formats={['avif', 'webp']}` emits `<source>` elements and lets the browser take the best it supports
    - It is also the tool for art direction — a different crop on small screens, rather than the same wide image scaled down
3.  **The hero is not lazy:**
    - The largest above-the-fold image is usually the element that decides the page's largest-contentful-paint, and it should load eagerly: `loading="eager"` with `fetchpriority="high"`
    - Everything below the fold is `loading="lazy"`, which is the component's default — so the rule in practice is "mark the hero, leave the rest alone"
    - `decoding="async"` on non-critical images keeps decode work off the path to first paint
4.  **Describe the layout so the right file is served:**
    - `widths` and `sizes` together tell the browser which candidate to fetch; `sizes` describes the rendered width at each breakpoint, and getting it wrong means a phone downloads the desktop file
    - `densities` covers the simpler case of a fixed-width image on high-density screens
    - The `layout` prop applies a responsive behaviour without hand-writing either
5.  **Remote images need authorisation to be optimised:**
    - An image from another origin is not processed unless that origin is listed in `image.domains` or matched by `image.remotePatterns`
    - Even unoptimised, routing it through `<Image />` with explicit `width` and `height` still buys layout stability — which is most of the benefit
6.  **Treat image handling as a build standard on image-heavy pages:**
    - A gallery, a case-study index or a product grid multiplies every one of these decisions by the number of items, so the component and its props belong in one card component rather than at each call site
    - A page that renders images from content should get its dimensions from the content model, not from markup written per entry

**Incorrect (raw tags from `public/`, no dimensions, hero lazy-loaded):**

```astro
---
// src/pages/index.astro
---

<!-- Bad: served untouched from public/, no width or height, so the page
     reflows when it decodes — and the hero is lazy, so it is fetched late -->
<img src="/hero.png" alt="Product screenshot" loading="lazy" />

<section class="gallery">
  <!-- Bad: same problem, once per item -->
  {items.map((item) => <img src={item.image} alt={item.name} />)}
</section>
```

**Correct (imported, sized, hero prioritised, the rest lazy):**

```astro
---
// src/pages/index.astro
import { Image, Picture } from 'astro:assets';
import hero from '../assets/hero.png';
import GalleryCard from '@components/GalleryCard.astro';

const items = await getItems();
---

<!-- The LCP candidate: eager, high priority, and sized for the viewport -->
<Image
  src={hero}
  alt="The dashboard showing a completed migration"
  loading="eager"
  fetchpriority="high"
  widths={[480, 960, 1440]}
  sizes="(max-width: 768px) 100vw, 960px"
/>

<!-- Below the fold: the browser picks the format, the component lazy-loads -->
<Picture
  src={diagram}
  formats={['avif', 'webp']}
  alt="How the ingest pipeline is structured"
  decoding="async"
/>

<section class="gallery">
  {items.map((item) => <GalleryCard item={item} />)}
</section>
```

```astro
---
// src/components/GalleryCard.astro — the props are decided once, not per call
import { Image } from 'astro:assets';

interface Props {
  item: { name: string; image: ImageMetadata };
}

const { item } = Astro.props;
---

<article>
  <Image
    src={item.image}
    alt={item.name}
    widths={[240, 480]}
    sizes="(max-width: 768px) 50vw, 240px"
    decoding="async"
  />
  <h3>{item.name}</h3>
</article>
```

Reference: [Images](https://docs.astro.build/en/guides/images/)
