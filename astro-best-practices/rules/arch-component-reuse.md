---
title: Reusable & Page-Specific Components
impact: MEDIUM
description: Extracts a component when a pattern actually repeats and keeps genuinely one-off sections local, rejecting both copy-paste across routes and abstraction built ahead of a second caller.
tags: architecture, components, composition, reuse
---

## Reusable & Page-Specific Components

**Impact (MEDIUM):** This rule has two failure modes and they pull in opposite directions, which is why stating only one of them makes a codebase worse. Copy-paste is the familiar one: a card pattern lives in six routes, a design change lands in five of them, and the site is now subtly inconsistent in a way no single file reveals. The less-discussed one is the correction overshooting — a `Section` component with eleven props and four booleans, built so that one landing page's hero could share code with a pricing block it has nothing in common with. That component is harder to read than the duplication it replaced, and every future page pays a tax to a generalisation that was invented rather than observed. The distinction that resolves both is not "how many times has this appeared" but whether the instances are the same thing or merely look alike today.

**Guidelines:**

1.  **Extract what repeats, when it repeats:**
    - Buttons, cards, card grids, calls to action, FAQ blocks, related-content lists, proof and testimonial sections, form fields — the patterns a site uses everywhere
    - Extract early enough to protect consistency: the second occurrence is usually the right moment, because that is when it becomes possible to see what actually varies
    - The extracted component takes the variation as props, and the props are the things that genuinely differ — not every attribute, in case
2.  **Keep genuinely one-off sections local:**
    - A campaign landing page's hero, a pricing table that exists once, a section built around a specific argument — these belong to their page
    - `src/components/<route>/` or a component beside the route keeps a single-use section out of the shared namespace, where its presence would imply it is reusable
    - Being long is not a reason to extract. Being repeated is
3.  **The test is sameness, not similarity:**
    - Two blocks that look alike but change for different reasons are two components. Merging them produces a component that has to be edited carefully in both directions forever
    - Two blocks that would always be changed together are one component, even if they render slightly differently today
4.  **Composition before configuration:**
    - Where a component starts accumulating booleans (`showIcon`, `isCompact`, `variantLarge`), slots are usually the answer: let the caller pass the differing part instead of describing it
    - A component with more configuration than markup has become a small framework, and reading it costs more than the duplication it prevents
5.  **The goal is publishing speed, not architectural purity:**
    - The measure is whether a new page of an existing type can be created without duplicating layout, metadata or content logic
    - Abstraction that does not serve that measure is not paying for itself, and abstraction built before a second caller exists cannot know what to abstract

**Incorrect (the same card copied across routes, and a section over-generalised into a switchboard):**

```astro
---
// src/pages/blog/index.astro — and again, near-identically, in /services and /case-studies
---

<article class="rounded-lg border p-4">
  <h3 class="text-lg font-semibold">{post.data.title}</h3>
  <p class="text-sm text-neutral-600">{post.data.description}</p>
  <a href={`/blog/${post.id}`}>Read more</a>
</article>
```

```astro
---
// src/components/Section.astro
// Bad: built to unify a hero, a pricing block and a testimonial strip, which
// are three different things that happened to be rectangles
interface Props {
  variant: 'hero' | 'pricing' | 'testimonial' | 'cta' | 'feature';
  title?: string;
  subtitle?: string;
  showIcon?: boolean;
  isCompact?: boolean;
  isCentered?: boolean;
  hasBackground?: boolean;
  columns?: 1 | 2 | 3 | 4;
  items?: unknown[];
  ctaLabel?: string;
  ctaHref?: string;
}
---
```

**Correct (one component for the repeated pattern, slots for what varies, one-offs kept local):**

```astro
---
// src/components/ContentCard.astro — the pattern that genuinely repeats
interface Props {
  title: string;
  description: string;
  href: string;
}

const { title, description, href } = Astro.props;
---

<article class="rounded-lg border p-4">
  <h3 class="text-lg font-semibold">{title}</h3>
  <p class="text-sm text-neutral-600">{description}</p>
  <!-- What varies is passed in, not described by a flag -->
  <slot name="meta" />
  <a href={href}>Read more</a>
</article>
```

```astro
---
// src/pages/blog/index.astro
import ContentCard from '@components/ContentCard.astro';
---

{
  posts.map((post) => (
    <ContentCard
      title={post.data.title}
      description={post.data.description}
      href={`/blog/${post.id}`}
    >
      <time slot="meta" datetime={post.data.pubDate.toISOString()}>
        {post.data.pubDate.toLocaleDateString('en', { dateStyle: 'medium' })}
      </time>
    </ContentCard>
  ))
}
```

```astro
---
// src/components/campaign/SpringLaunchHero.astro
// This exists once, for one page, and says so by where it lives
---

<section class="campaign-hero">
  <h1>Spring launch</h1>
  <slot />
</section>
```

Reference: [Astro components](https://docs.astro.build/en/basics/astro-components/)
