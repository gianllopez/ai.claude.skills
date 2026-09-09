---
title: Markdown, MDX & the Code Component
impact: HIGH
description: Keeps prose in plain Markdown and reserves MDX for content that genuinely embeds components, renders build-time-dynamic code through the Code component, and configures the v7 Markdown processor deliberately.
tags: content, markdown, mdx, shiki, processor
---

## Markdown, MDX & the Code Component

**Impact (HIGH):** _MDX_ is _Markdown_ that can import and execute components, and that capability is not free: every _MDX_ file is compiled as a module, can pull a framework component into the page, and stops being content a non-developer can safely edit. Making it the default authoring format for a blog means a hundred prose files carry the machinery that four of them needed. The mirror defect is reaching for raw `<pre>` blocks or a third-party highlighter when the code being rendered is dynamic, ignoring the highlighter _Astro_ already runs. And in v7 the processor underneath all of this changed: **Sätteri is the default**, it does not run _remark_ or _rehype_ plugins, and `@astrojs/markdown-remark` is no longer installed for you — so a project that carried a plugin pipeline forward without touching the config has silently lost it.

**Guidelines:**

1.  **Plain _Markdown_ is the default for prose:**
    - Articles, documentation pages, changelog entries, legal copy — anything that is text with headings, links, lists and images
    - It stays editable by anyone, diffs cleanly, and cannot import a component that changes the page's cost
2.  **_MDX_ when the content genuinely embeds components:**
    - A live demo, an interactive chart inside an article, a custom callout the site defines, an embedded form
    - Install it deliberately with `npx astro add mdx`, and treat a file's extension as a statement: `.mdx` means this page runs components
    - A component used in every article is not a reason to make every article _MDX_ — that is a layout concern, and the layout is already a component
3.  **Components inside _MDX_ obey the hydration rules:**
    - An imported `.astro` component costs nothing; a framework component still needs a `client:*` directive and still pays for it
    - The most common island smuggled into a site is one that entered through an article
4.  **`<Code />` for code that is dynamic at build time:**
    - Fenced code blocks in _Markdown_ are already highlighted by _Shiki_ — leave them alone
    - `<Code />` from `astro:components` is the same highlighter as a component, and it is the right tool when the source is a variable, a file read at build time, or a value from a _CMS_
    - It does **not** inherit `markdown.shikiConfig`. A `<Code />` block that has to match the theme of the surrounding fenced blocks must be passed `theme` explicitly, or the page renders two different themes
    - `import.meta.glob()` is how a build-time file becomes that variable; `Astro.glob()` was removed in v6
5.  **Configure the processor rather than inheriting it:**
    - **Sätteri** is the default in v7 and needs no configuration; state it explicitly only when passing feature flags
    - It runs _mdast_ and _hast_ plugins, which are its own ecosystem — _remark_ and _rehype_ plugins do not work under it
    - A project with an existing _remark_/_rehype_ pipeline opts back in with `processor: unified()` from `@astrojs/markdown-remark`, which must now be installed explicitly
    - Top-level `markdown.remarkPlugins`, `rehypePlugins`, `remarkRehype`, `gfm` and `smartypants` are deprecated in favour of options passed to the processor. Leaving them in place is a pipeline that will stop being applied

**Incorrect (MDX by default, an unstyled dynamic code block, an orphaned plugin pipeline):**

```js
// astro.config.mjs
export default defineConfig({
  markdown: {
    // Bad: under the v7 default processor these are not applied — the pipeline
    // is configured, inert, and nothing reports it
    remarkPlugins: [remarkToc],
    gfm: true,
    shikiConfig: { theme: 'github-dark' },
  },
});
```

Then, in `src/data/blog/release-notes.mdx` — prose authored as _MDX_ out of habit, with a `<Code />` that never receives a theme, so it renders in the default while every fenced block on the page renders in `github-dark`:

```jsx
import { Code } from 'astro:components';

<Code code={snippet} lang="ts" />;
```

**Correct (format chosen per file, processor stated, theme passed explicitly):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import { unified } from '@astrojs/markdown-remark';
import remarkToc from 'remark-toc';

export default defineConfig({
  markdown: {
    // This project has an existing remark pipeline, so it opts back into
    // unified instead of silently losing it under Sätteri (the v7 default)
    processor: unified({ remarkPlugins: [remarkToc] }),
    shikiConfig: { theme: 'github-dark' },
  },
});
```

The same post as `src/data/blog/release-notes.md` — plain _Markdown_, no imports, its fenced block already highlighted by the configured processor:

````markdown
We shipped a few things this month.

```ts
const client = createClient({ retries: 3 });
```
````

```astro
---
// src/pages/docs/examples.astro — code that is dynamic at build time
import { Code } from 'astro:components';

const modules = import.meta.glob('../../examples/*.ts', {
  eager: true,
  query: '?raw',
  import: 'default',
});
const [path, source] = Object.entries(modules)[0];
---

<!-- theme passed explicitly so it matches the fenced blocks elsewhere -->
<Code code={source} lang="ts" theme="github-dark" />
```

Reference: [Markdown in Astro](https://docs.astro.build/en/guides/markdown-content/)
