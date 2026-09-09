---
title: Structured Data Generated From Content
impact: MEDIUM
description: Requires JSON-LD to be generated from the content model and to describe only what is actually rendered on the page, never hand-copied per page or asserted about content that is not there.
tags: seo, json-ld, structured-data, schema-org
---

## Structured Data Generated From Content

**Impact (MEDIUM):** Structured data is a machine-readable claim about what a page contains, and its only value is being true. Hand-copied into each template it stops being true almost immediately: the `datePublished` still says the date of the page it was copied from, the `author` names someone who left, the `headline` disagrees with the `<h1>` because one of them was edited. None of this shows up in the rendered page, so nothing catches it — the page looks correct and describes itself incorrectly. Generated from the same content entry the page renders, the two cannot disagree, because there is one source. The other half of the rule is a boundary: markup that claims things the page does not show — an FAQ block with no visible FAQ, reviews nobody wrote — is not an optimisation with a risk attached, it is a misrepresentation, and it is the kind of thing that costs a site its rich results entirely.

**Guidelines:**

1.  **Generate from the entry, in one helper:**
    - A function that takes the content entry and returns the object, rendered by the layout through a single `<script type="application/ld+json">` — the same shape as the metadata rule, for the same reason
    - Every field it emits reads from the schema. A value typed into the helper as a literal is a value that will be wrong on some page
    - Serialise with `JSON.stringify` and let the template insert it, rather than assembling the _JSON_ as a string
2.  **Use the types that match what the page actually is:**
    - `Article` (or `BlogPosting`) for editorial content, `BreadcrumbList` for a page inside a hierarchy, `Organization` once for the business identity, `Service` for a real service page, `Product` for a real product
    - One page usually carries two: what it is, plus its breadcrumb. More than that is usually a page describing itself as several things at once
3.  **Only describe what is rendered:**
    - `FAQPage` requires the questions and answers to be visible on the page, not hidden behind a toggle that never opens and not present only in the markup
    - A rating requires real, collected ratings; an `Organization` address requires a real one
    - The test is whether a person opening the page can see every claim the markup makes. If they cannot, the markup is the defect
4.  **Absolute _URLs_, derived like the canonical:**
    - `url`, `image`, `@id` and every reference are absolute, built from `Astro.site` — a relative _URL_ in _JSON-LD_ is not resolved the way it is in _HTML_
    - The page's `url` is its canonical. If the helper computes it separately, the two will drift
5.  **Dates come from the schema and follow its meaning:**
    - `datePublished` from `pubDate`, `dateModified` from `updatedDate` — and the content rule against faking freshness applies here first, because this is where the claim is made explicitly
    - Emit them as _ISO_ strings; a locale-formatted date is not valid here
6.  **Validate the output, not the template:**
    - A helper that produces valid _JSON_ can still produce invalid structured data, so the check runs against a rendered page
    - Do this once per page type rather than once per page — the point of generating it is that one correct type is correct everywhere

**Incorrect (hand-copied per page, claiming content the page does not have):**

```astro
---
// src/pages/blog/introducing-our-api.astro
---

<!-- Bad: copied from another post. The dates, author and headline are that
     post's, and nothing on this page will ever correct them -->
<script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Scaling our ingest pipeline",
    "datePublished": "2025-11-04",
    "author": { "@type": "Person", "name": "A. Former-Employee" },
    "image": "/images/og.png",
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "4.9",
      "reviewCount": "218"
    }
  }
</script>

<!-- ...and there is no FAQ anywhere on this page -->
<script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "Is the API free?",
        "acceptedAnswer": { "@type": "Answer", "text": "Yes." }
      }
    ]
  }
</script>
```

**Correct (derived from the entry, describing what is rendered):**

```ts
// src/lib/structured-data.ts
import type { CollectionEntry } from 'astro:content';

export function articleSchema(post: CollectionEntry<'blog'>, site: URL) {
  const url = new URL(`/blog/${post.id}`, site).href;

  return {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.data.title,
    description: post.data.description,
    url,
    mainEntityOfPage: url,
    datePublished: post.data.pubDate.toISOString(),
    // Only present when the content actually records a modification
    ...(post.data.updatedDate && {
      dateModified: post.data.updatedDate.toISOString(),
    }),
    author: { '@type': 'Person', name: post.data.author },
    publisher: { '@type': 'Organization', name: 'Example' },
  };
}
```

```astro
---
// src/layouts/Article.astro
import type { CollectionEntry } from 'astro:content';
import { articleSchema } from '@lib/structured-data';
import Base from '@layouts/Base.astro';

interface Props {
  post: CollectionEntry<'blog'>;
}

const { post } = Astro.props;
const schema = articleSchema(post, Astro.site!);
---

<Base
  title={post.data.title}
  description={post.data.description}
  pageType="article"
>
  <script
    type="application/ld+json"
    set:html={JSON.stringify(schema)}
    is:inline
  />

  <article>
    <h1>{post.data.title}</h1>
    <slot />
  </article>
</Base>
```

Reference: [Astro.site and absolute URLs](https://docs.astro.build/en/reference/api-reference/)
