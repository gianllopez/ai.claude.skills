---
title: Content Collections Through the Content Layer API
impact: CRITICAL
description: Requires all structured content to go through typed collections defined in src/content.config.ts with an explicit loader, and rejects the removed legacy shapes and ad-hoc file reading.
tags: content, collections, content-layer, zod, typescript
---

## Content Collections Through the Content Layer API

**Impact (CRITICAL):** Content read by hand is content with no contract. A page that does `post.data.title` against a hand-globbed _Markdown_ file gets `undefined` for the one post where the frontmatter key was misspelled, renders an empty `<h1>`, and ships — because nothing in the pipeline knew that field was required. A collection turns that into a build failure with the file path in it. The second cost is that this _API_ has moved twice: the pre-v6 shape (`src/content/config.ts`, collections without a `loader`) was **removed**, not deprecated, so tutorials and generated code still teaching it produce a project that does not build. Getting the current shape written down is what keeps a codebase from being rebuilt against documentation that no longer applies.

**Guidelines:**

1.  **One config file, at the root of `src/`:**
    - The file is `src/content.config.ts` — not `src/content/config.ts`, which was the pre-v6 location and no longer works
    - It exports a single `collections` object mapping each collection name to a `defineCollection()` call
2.  **Every collection declares a `loader`:**
    - `glob()` from `astro/loaders` for files on disk: `glob({ pattern: '**/*.md', base: './src/data/blog' })`
    - `file()` for a single data file holding many entries
    - A custom or third-party loader for a _CMS_ or _API_ — this is the seam that makes the source of the content swappable without touching the pages that read it
    - There is no implicit loader. Legacy collections and the `legacy.collections` flag were removed in v6, so a collection without one is not a legacy collection, it is a broken one
3.  **Import `z` from `astro/zod`:**
    - `astro/zod` is the re-export that tracks the version _Astro_ ships
    - `import { z } from 'astro:content'` and `astro:schema` are deprecated paths that still appear throughout older material
    - The bundled _Zod_ is **v4**, whose top-level string formats replaced the chained ones: `z.email()`, `z.url()`, `z.uuid()` rather than `z.string().email()` and friends
4.  **Entries are keyed by `id`:**
    - Content Layer entries expose `id`, generated from the filename unless frontmatter overrides it. The `slug` property belonged to the removed legacy collections
    - So dynamic routes are `[id].astro` and build their params from `post.id`, and anything constructing a URL — a feed, a sitemap entry, an internal link — reads `id`
5.  **Never read content files directly:**
    - `import.meta.glob()` is the correct tool for globbing modules generally, and it is the replacement for the removed `Astro.glob()`, but content is not a general module: reaching for either to load _Markdown_ bypasses the schema, the type generation and the caching
    - Reading `src/content/` with `fs` in a page's frontmatter has the same problem and additionally breaks whenever the content moves
6.  **Reach for live collections when the content must not wait for a rebuild:**
    - `defineLiveCollection()` in `src/live.config.ts` fetches at request time, so _CMS_ edits appear without redeploying — stable since v6
    - It is the tool for genuinely live content, not a way to avoid configuring a build hook

**Incorrect (the removed legacy shape, and content read by hand):**

```ts
// ⚠️ src/content/config.ts — this path stopped being read in v6
import { defineCollection } from 'astro:content';
import { z } from 'astro:content'; // deprecated import path

const blog = defineCollection({
  // Bad: no loader. Legacy collections were removed, so this does not build
  schema: z.object({
    title: z.string(),
    contact: z.string().email(), // Zod 3 chaining; v4 wants z.email()
    pubDate: z.coerce.date(),
  }),
});

export const collections = { blog };
```

```astro
---
// src/pages/blog/[slug].astro
// Bad: bypasses the schema entirely — a missing title is undefined at runtime,
// and `slug` no longer exists on collection entries
const posts = Object.values(import.meta.glob('../../content/blog/*.md', { eager: true }));

export async function getStaticPaths() {
  return posts.map((post) => ({ params: { slug: post.frontmatter.slug } }));
}
---

<h1>{Astro.props.post.frontmatter.title}</h1>
```

**Correct (current Content Layer shape, typed end to end):**

```ts
// src/content.config.ts
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/data/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
```

```astro
---
// src/pages/blog/[id].astro — params come from the entry id
import { getCollection, render } from 'astro:content';
import Layout from '@layouts/Article.astro';

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);

  return posts.map((post) => ({
    params: { id: post.id },
    props: { post },
  }));
}

const { post } = Astro.props;
const { Content } = await render(post);
---

<Layout title={post.data.title} description={post.data.description}>
  <h1>{post.data.title}</h1>
  <Content />
</Layout>
```

Reference: [Content collections](https://docs.astro.build/en/guides/content-collections/)
