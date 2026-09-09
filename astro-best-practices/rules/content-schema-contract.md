---
title: The Schema Is the Publishing Contract
impact: CRITICAL
description: Requires the fields a page cannot ship without to be declared and validated in the collection schema, so a missing or malformed value fails the build instead of reaching production.
tags: content, schema, zod, validation, seo
---

## The Schema Is the Publishing Contract

**Impact (CRITICAL):** Every page has fields it cannot be correct without — a title, a description, a publication date — and there are exactly two places to enforce them: a schema that fails the build, or a person remembering. The second one works until a site has more than one author, and then it degrades quietly: a post ships with no meta description, a date renders as `Invalid Date`, a draft goes live because nobody filtered it. None of these throw. They are discovered weeks later in a crawl report, and by then the page has been indexed as it is. A schema converts each of them into a build error naming the file and the field, at the moment the content was written, when fixing it costs nothing. This is the concrete payoff of the previous rule: collections are worth configuring because the schema is where publishing requirements become mechanical.

**Guidelines:**

1.  **Declare every field the template reads:**
    - If a layout, feed or component reads `post.data.x`, then `x` belongs in the schema — an optional field the template does not guard is the same defect as an undeclared one
    - Give a field a `.default()` when the site has a sensible fallback, and leave it required when it does not. `draft: z.boolean().default(false)` is right; a defaulted title is not
2.  **The baseline for a content-driven page:**
    - `title` and `description` — the two the document head cannot be assembled without
    - `pubDate`, and `updatedDate` as optional. Coerce both with `z.coerce.date()` so a malformed date is a build error rather than an `Invalid Date` in the rendered output
    - `draft`, defaulted to `false` and filtered at every read, so unfinished work cannot reach a page, a feed or a sitemap
    - A canonical override, optional, for the genuine cases — a migrated URL, a syndicated post. Optional because a required one invites a wrong value on every page
    - `tags` and `author` where the site uses them
3.  **Constrain values, not just types:**
    - `z.string().max(160)` on a description catches the one that will be truncated in a result page, at build time
    - `z.enum([...])` for a category or page type, so a typo cannot create a silent third category
    - `.refine()` for a relationship the type system cannot state — an `updatedDate` that precedes `pubDate` is data corruption, and it is one line to reject
4.  **Never fake freshness:**
    - `updatedDate` means the content changed. Setting it on a build, a reformat or a dependency bump makes it noise, and consumers that trust it (feeds, sitemaps, search) are misled by it
    - This is a rule about what the field means, and the schema can only enforce that it is a date — so it is stated here to be enforced in review
5.  **Model relationships with `reference()`, not free-form strings:**
    - A related entry declared as `reference('blog')` is validated against the collection, so a renamed or deleted entry breaks the build instead of rendering a dead link
    - A plain `z.string()` holding an entry id is a foreign key with no integrity
6.  **A CMS does not remove the contract, it relocates it:**
    - Where editors publish through a _CMS_, the same required fields have to exist as _CMS_ fields, and the loader's schema still validates what comes back — an _API_ response is untrusted input like any other
    - The boundary is worth stating explicitly: editors own content, not layout. A _CMS_ that lets an editor restructure a page is a _CMS_ that will break the page, and the fix is field design, not review
    - This holds regardless of vendor; the choice between a _CMS_ and file-based collections is a workflow decision, not a technical one

**Incorrect (a schema that types nothing the site actually depends on):**

```ts
// src/content.config.ts
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/data/blog' }),
  // Bad: everything optional, nothing constrained. A post with no description
  // builds cleanly and ships with an empty meta tag
  schema: z.object({
    title: z.string().optional(),
    description: z.string().optional(),
    pubDate: z.string().optional(),
    related: z.array(z.string()).optional(),
  }),
});

export const collections = { blog };
```

```astro
---
// src/pages/blog/[id].astro — reads fields the schema never guaranteed
const { post } = Astro.props;
---

<meta name="description" content={post.data.description} />
<time>{new Date(post.data.pubDate).toLocaleDateString()}</time>
```

**Correct (the contract is declared, and violating it fails the build):**

```ts
// src/content.config.ts
import { defineCollection, reference } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/data/blog' }),
  schema: z
    .object({
      title: z.string().min(1),
      // Truncation in a result page is a build error, not a surprise
      description: z.string().max(160),
      pubDate: z.coerce.date(),
      updatedDate: z.coerce.date().optional(),
      // Only for genuine exceptions: migrations, syndicated copies
      canonicalUrl: z.url().optional(),
      category: z.enum(['engineering', 'product', 'company']),
      // Validated against the collection: a renamed entry breaks the build
      related: z.array(reference('blog')).default([]),
      draft: z.boolean().default(false),
    })
    .refine((data) => !data.updatedDate || data.updatedDate >= data.pubDate, {
      message: 'updatedDate cannot precede pubDate',
      path: ['updatedDate'],
    }),
});

export const collections = { blog };
```

```astro
---
// src/pages/blog/[id].astro — every field read here is guaranteed to exist
import { getCollection } from 'astro:content';

export async function getStaticPaths() {
  // Drafts cannot reach a route, a feed or the sitemap
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return posts.map((post) => ({ params: { id: post.id }, props: { post } }));
}

const { post } = Astro.props;
---

<meta name="description" content={post.data.description} />
<time datetime={post.data.pubDate.toISOString()}>
  {post.data.pubDate.toLocaleDateString('en', { dateStyle: 'long' })}
</time>
```

Reference: [Defining a collection schema](https://docs.astro.build/en/guides/content-collections/)
