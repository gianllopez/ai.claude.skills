# Astro Best Practices

**Version 1.0.0**  
_Gian López_  
_September 2026_

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring _Astro_ codebases. Humans  
> may also find it useful, but guidance here is optimized for automation  
> and consistency by AI-assisted workflows.

---

## Abstract

Standards for building production websites with _Astro_ 7, where the defining decision is how little of the page reaches the browser as _JavaScript_. Static output is the default and on-demand rendering is the exception that has to justify itself; a component is an `.astro` component until interactivity proves otherwise, and an island carries the hydration directive its position earns rather than `client:load` everywhere. Content is a typed collection through the Content Layer API, because a schema is the only place a required field becomes a build failure instead of a missing tag in production. SEO is treated as a system generated from that schema — one canonical rule, one trailing-slash convention, a sitemap that lists only indexable URLs, JSON-LD derived from the content model — never assembled page by page. Assets, fonts, third-party scripts and navigation follow the built-in APIs that already solve them, styling resolves through _TailwindCSS_ v4 theme tokens declared in CSS, and configuration covers the version floor, environment boundary and content security policy the sources omit. The reference version is _Astro_ 7; every rule that names a config key or import path carries the version it belongs to. Visual design direction and accessibility auditing are out of scope by design.

---

## Table of Contents

1. [Rendering & Hydration](#1-rendering--hydration) — `CRITICAL`
   - 1.1 [Static Output by Default](#11-static-output-by-default)
   - 1.2 [.astro Components Before Framework Components](#12-astro-components-before-framework-components)
   - 1.3 [Hydration Directives & Island Boundaries](#13-hydration-directives--island-boundaries)
2. [Content Model](#2-content-model) — `CRITICAL`
   - 2.1 [Content Collections Through the Content Layer API](#21-content-collections-through-the-content-layer-api)
   - 2.2 [The Schema Is the Publishing Contract](#22-the-schema-is-the-publishing-contract)
   - 2.3 [Markdown, MDX & the Code Component](#23-markdown-mdx--the-code-component)
3. [SEO System](#3-seo-system) — `CRITICAL`
   - 3.1 [Site URL, Metadata & Canonicals](#31-site-url-metadata--canonicals)
   - 3.2 [URL Hygiene, Redirects & Migration](#32-url-hygiene-redirects--migration)
   - 3.3 [Sitemap & Feed Hygiene](#33-sitemap--feed-hygiene)
   - 3.4 [Structured Data Generated From Content](#34-structured-data-generated-from-content)
4. [Assets & Performance](#4-assets--performance) — `HIGH`
   - 4.1 [Image Handling & Layout Stability](#41-image-handling--layout-stability)
   - 4.2 [Fonts Through the Built-in API](#42-fonts-through-the-built-in-api)
   - 4.3 [Third-Party Scripts & Embeds](#43-third-party-scripts--embeds)
   - 4.4 [Prefetching & View Transitions](#44-prefetching--view-transitions)
5. [Project Structure](#5-project-structure) — `HIGH`
   - 5.1 [Route Responsibility, Layouts & Slots](#51-route-responsibility-layouts--slots)
   - 5.2 [Reusable & Page-Specific Components](#52-reusable--page-specific-components)
   - 5.3 [TypeScript Path Aliases](#53-typescript-path-aliases)
   - 5.4 [Markup Discipline Under the v7 Compiler](#54-markup-discipline-under-the-v7-compiler)
6. [Styling](#6-styling) — `HIGH`
   - 6.1 [TailwindCSS v4 Setup & Theme Tokens](#61-tailwindcss-v4-setup--theme-tokens)
   - 6.2 [Scoped Component Styles](#62-scoped-component-styles)
7. [Build & Configuration](#7-build--configuration) — `HIGH`
   - 7.1 [Internationalization on Day One](#71-internationalization-on-day-one)
   - 7.2 [Structured Build Logging](#72-structured-build-logging)
   - 7.3 [Typed Environment & Content Security Policy](#73-typed-environment--content-security-policy)
   - 7.4 [Deployment Target & Toolchain Floor](#74-deployment-target--toolchain-floor)

---

## 1. Rendering & Hydration

### 1.1 Static Output by Default

**Impact (CRITICAL):** This is the decision every other performance rule inherits. A prerendered page is a file on a CDN — it has no cold start, no runtime dependency, no per-request cost, and it cannot fail at request time because there is nothing to run. An on-demand page gives all of that up, and it gives it up per request, forever. The defect is almost never a deliberate choice to render on the server; it is `output: 'server'` set once so that one route could read a cookie, silently converting an entire marketing site into a runtime. Stating the mode explicitly is what makes the mismatch visible: when the config says the site is static and a route needs the server, the opt-out appears in that route's diff, where a reviewer can ask what request-time data justifies it.

**Guidelines:**

1.  **State the mode, even though it is the default:**
    - `output: 'static'` is what _Astro_ does with no configuration, and writing it down is still worth the line — it declares the architecture, so a later `output: 'server'` reads as a change to it rather than as setup
    - Prerendering is the whole point of choosing _Astro_. A project that renders everything on demand has bought a build step and given up the reason for it
2.  **Opt into on-demand rendering one route at a time:**
    - With an adapter installed, `export const prerender = false` in a single page or endpoint renders that route on demand and leaves every other route static
    - The inverse exists for projects that genuinely are server-first: under `output: 'server'`, `export const prerender = true` pulls a route back to build time. Reach for that mode only when most routes need the server
    - An adapter is required for on-demand rendering, and also for server islands (`server:defer`) — installing one does not by itself make the site dynamic
3.  **The bar for a route to leave build time:**
    - It needs data that only exists at request time: the signed-in user, a session, a cookie, a query the build cannot know
    - It needs data too volatile to rebuild for: inventory, prices, live availability
    - It accepts a request body — a form endpoint, a webhook receiver
    - None of these is "the content changes sometimes". Content that changes on a schedule is a rebuild, not a render; content that changes from a _CMS_ is a build hook or a live collection
4.  **Marketing pages, blogs, documentation and landing pages are static, without exception:**
    - They are exactly the pages whose value depends on being fast and indexable, and exactly the pages with no request-time input
    - A personalised greeting on an otherwise static page is an island, not a reason to render the page on the server
5.  **Read the mode as a review signal:**
    - A diff that adds `output: 'server'` should name the routes that need it. If the answer is "one", the answer is `prerender = false` on that one
    - A diff that adds an adapter to a fully static project is either preparing for a specific on-demand route or is unnecessary

**Incorrect (one dynamic route converts the whole site to a runtime):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  // Bad: set so that /account could read a session. Every marketing page,
  // every blog post and every landing page is now rendered per request
  output: 'server',
  adapter: node({ mode: 'standalone' }),
});
```

```astro
---
// src/pages/index.astro — nothing here needs a server, and it gets one anyway
import Layout from '@layouts/Base.astro';
import { getCollection } from 'astro:content';

const services = await getCollection('services');
---

<Layout title="Home">
  {services.map((service) => <ServiceCard service={service.data} />)}
</Layout>
```

**Correct (static everywhere, on demand where the request is the input):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  // Declared, not assumed: the site is prerendered
  output: 'static',
  // Present only so individual routes can opt out below
  adapter: node({ mode: 'standalone' }),
});
```

```astro
---
// src/pages/account/index.astro — the session is request-time input,
// so this one route leaves build time and says so
export const prerender = false;

import Layout from '@layouts/Base.astro';

const user = await getUserFromSession(Astro.request.headers.get('cookie'));
---

<Layout title="Your account">
  <h1>Welcome back, {user.name}</h1>
</Layout>
```

Reference: [On-demand rendering](https://docs.astro.build/en/guides/on-demand-rendering/)

### 1.2 .astro Components Before Framework Components

**Impact (CRITICAL):** An `.astro` component runs at build time and ships zero bytes of _JavaScript_ — and it still takes props, renders slots, holds scoped styles, and composes exactly like any other component. So the question is never "can this be an `.astro` component"; for headers, cards, footers, navs, sections and grids the answer is always yes. The defect is habit: a team arriving from _Next.js_ writes `Card.tsx` because that is what a component looks like to them, adds `client:load` because otherwise it does not render the way they expect, and ships a framework runtime plus a component bundle to render markup that never changes. Nothing fails, which is why it survives review — the page just carries a runtime it has no use for, and the cost compounds with every component written the same way.

**Guidelines:**

1.  **`.astro` is the default, and the default covers most of the page:**
    - Layouts, headers, navbars, footers, cards, grids, hero sections, tables, lists, breadcrumbs, article bodies — anything whose output is decided by its props
    - Props, slots, named slots and scoped styles all work; there is no expressive gap to route around
    - The frontmatter runs on the server at build time, so data fetching, filesystem access and secrets belong there
2.  **A framework component earns its place with client-side state:**
    - Real interactivity: a form with live validation, a filterable list, a carousel, a chart the user manipulates, a search box, a stateful widget
    - An existing component from the project's design system that already exists in _React_ and is not worth rewriting
    - A browser _API_ the component wraps — a map, an editor, a player
3.  **Interactivity is not the same as a framework:**
    - A disclosure, a menu toggle, a copy-to-clipboard button and a theme switch are `.astro` plus a `<script>` tag or a few lines of _CSS_ — a framework runtime for a class toggle is the heaviest possible answer
    - `<script>` in an `.astro` file is bundled and processed by _Vite_ like any other module; it is not a fallback, it is the small-interaction tool
4.  **A framework component that is not hydrated is still an `.astro` component with extra steps:**
    - Rendered without a `client:*` directive it produces static _HTML_ and ships nothing — which works, but means the framework bought nothing and the file now needs that framework's toolchain to be understood
    - If a component is never hydrated anywhere it is imported, it should be `.astro`
5.  **Keep the framework boundary as small as the interactivity:**
    - Where an interactive control sits inside a static section, the framework component is the control, not the section — see the hydration-directives rule
    - Static content passes into an island through slots, so it renders once at build time instead of being re-rendered by the client runtime
6.  **What this skill does not own:**
    - Once a _React_ island exists, everything inside it — effects, state, derived values, the query layer, typing — is governed by `react-core-best-practices`, which a project rendering islands loads alongside this skill

**Incorrect (a framework component and a runtime to render static markup):**

```tsx
// src/components/ServiceCard.tsx — no state, no effects, no events
type Props = { title: string; description: string; href: string };

export function ServiceCard({ title, description, href }: Props) {
  return (
    <article className="card">
      <h3>{title}</h3>
      <p>{description}</p>
      <a href={href}>Learn more</a>
    </article>
  );
}
```

```astro
---
// src/pages/services.astro
import { ServiceCard } from '@components/ServiceCard';
const services = await getServices();
---

<!-- Bad: ships the React runtime plus this component's bundle so the browser
     can re-render markup that was already correct in the HTML response -->
{services.map((service) => <ServiceCard client:load {...service} />)}
```

**Correct (`.astro` for the markup, a framework component only for the stateful part):**

```astro
---
// src/components/ServiceCard.astro — zero JavaScript, same capability
interface Props {
  title: string;
  description: string;
  href: string;
}

const { title, description, href } = Astro.props;
---

<article class="card">
  <h3>{title}</h3>
  <p>{description}</p>
  <a href={href}>Learn more</a>
</article>

<style>
  .card {
    display: grid;
    gap: 0.5rem;
  }
</style>
```

```astro
---
// src/pages/services.astro
import ServiceCard from '@components/ServiceCard.astro';
import ServiceFilter from '@components/ServiceFilter'; // React: real client state
const services = await getServices();
---

<!-- The filter is interactive, so it is an island; the cards are not -->
<ServiceFilter client:visible categories={categories} />

{services.map((service) => <ServiceCard {...service} />)}
```

Reference: [Astro components](https://docs.astro.build/en/basics/astro-components/)

### 1.3 Hydration Directives & Island Boundaries

**Impact (CRITICAL):** A `client:*` directive is a purchase order for _JavaScript_, and the directive decides when the browser pays. `client:load` means the bundle is requested and executed during the initial page load, competing with everything else, whether or not the user ever sees the component; `client:visible` means it is not even requested until the component scrolls into view, so a chart at the bottom of a long page costs a reader who never scrolls exactly nothing. The two look identical in review and identical in the rendered page — the difference only shows up in the network waterfall, which is why `client:load` spreads: it is the one that always works, so it becomes the one that is always used. The second half of the defect is the boundary. Marking a whole section as the island to make one button work hydrates every static paragraph inside it, and the framework re-renders on the client markup that was already correct in the response.

**Guidelines:**

1.  **Match the directive to the component's position and priority:**
    - `client:load` — above the fold and immediately interactive: the primary search box, a header cart, a control the page is about
    - `client:idle` — needed soon but not first: secondary widgets, non-critical enhancements that can wait for the main thread to settle
    - `client:visible` — anything below the fold. This is the correct default for most islands, and it accepts a `rootMargin` so hydration can start slightly before the component enters the viewport
    - `client:media` — a component that only exists at some breakpoints, typically a mobile-only drawer or a desktop-only panel. Hydrating a mobile menu on desktop is paying for a component the user cannot reach
    - `client:only` — no server render at all, for components that cannot run outside the browser. It requires naming the framework and it costs a blank space until hydration, so it is a last resort, not a way to silence a mismatch error
2.  **`client:load` is a claim that has to be true:**
    - The claim is "the user can interact with this before scrolling". If they cannot, the directive is wrong
    - A component reachable only after a click on something else is not above the fold in any meaningful sense
    - When auditing an existing site, the fastest win is usually re-reading every `client:load` in the codebase and asking that one question
3.  **Draw the island around the interactivity, not around the section:**
    - The island is the filter control, not the results section; the tab buttons, not the tab panels; the form, not the page that contains it
    - Static content reaches an island through slots, so it is rendered once at build time and passed in as _HTML_ rather than re-rendered by the client
4.  **Islands hydrate independently, and that is a structural property to use:**
    - Unlike a single-page application, a heavy island low on the page does not block a light island at the top — each is requested and hydrated on its own schedule
    - So the correct structure is not "fewer islands", it is "each island priced correctly". Several small, well-directed islands beat one large one that hydrates everything at once
5.  **Defer server work with server islands instead of shipping it to the client:**
    - `server:defer` renders a component on demand after the static shell, keeping the page prerendered while a personalised or slow fragment arrives separately
    - This is the answer to "the page is static except for this one dynamic strip" — it needs an adapter, and it does not hydrate anything on the client
6.  **A directive is a review flag when it is absent from the diff's reasoning:**
    - The finding is not "this uses `client:load`"; it is "this uses `client:load` and sits below the fold"
    - A component with no directive at all is static _HTML_ — correct and free when the component has no behaviour, and a bug only when the component was supposed to be interactive

**Incorrect (everything hydrated immediately, and the island drawn around static content):**

```astro
---
// src/pages/pricing.astro
import PricingSection from '@components/PricingSection'; // React
import ComparisonChart from '@components/ComparisonChart'; // React, heavy
import MobileNav from '@components/MobileNav'; // React
---

<!-- Bad: the whole section is an island so that one toggle inside it works.
     Every heading, paragraph and price in it is re-rendered on the client -->
<PricingSection client:load plans={plans} />

<!-- Bad: below the fold, and its bundle is requested during initial load -->
<ComparisonChart client:load data={comparison} />

<!-- Bad: hydrated on every viewport, including the ones that never show it -->
<MobileNav client:load links={links} />
```

**Correct (the boundary wraps the interactive part, and each directive is priced):**

```astro
---
// src/pages/pricing.astro
import PlanCard from '@components/PlanCard.astro'; // static markup, zero JS
import BillingToggle from '@components/BillingToggle'; // React: the only state here
import ComparisonChart from '@components/ComparisonChart'; // React, heavy
import MobileNav from '@components/MobileNav'; // React
---

<section>
  <h2>Pricing</h2>

  <!-- The island is the toggle, not the section around it -->
  <BillingToggle client:load />

  <!-- Static cards stay static -->
  {plans.map((plan) => <PlanCard plan={plan} />)}
</section>

<!-- Below the fold: its JavaScript is not requested until the reader gets there -->
<ComparisonChart client:visible={{ rootMargin: '200px' }} data={comparison} />

<!-- Only hydrated on the viewports that can actually open it -->
<MobileNav client:media="(max-width: 768px)" links={links} />
```

Reference: [Template directives reference](https://docs.astro.build/en/reference/directives-reference/)

---

## 2. Content Model

### 2.1 Content Collections Through the Content Layer API

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

### 2.2 The Schema Is the Publishing Contract

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

### 2.3 Markdown, MDX & the Code Component

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

---

## 3. SEO System

### 3.1 Site URL, Metadata & Canonicals

**Impact (CRITICAL):** `site` is one line of configuration that several unrelated things silently depend on: `Astro.site`, every absolute _URL_ built from it, the sitemap integration (which refuses to run without it), and canonical tags. Omitted, none of them fail loudly — the sitemap is simply absent and canonicals are relative or missing, which is exactly the failure mode nobody notices until a crawl report arrives. The larger defect is metadata assembled by hand in each page. It starts as three tags copied between templates and becomes a site where a third of the pages share one description, two pages claim the same canonical, and a route that was duplicated for a campaign is competing with its own original. Metadata is generated content — derived from the content model by one component — and the moment it is typed per page it begins to drift.

**Guidelines:**

1.  **Set `site` in `astro.config.mjs`, always:**
    - It is the production origin, with no trailing slash: `site: 'https://example.com'`
    - Without it `Astro.site` is `undefined`, absolute _URLs_ silently become relative, and `@astrojs/sitemap` does not emit
2.  **One head component owns metadata for the whole site:**
    - It takes `title`, `description` and the optional overrides as props, and every layout renders it — there is no second place a `<title>` is written
    - Defaults live in it: the site name suffix, the fallback social image, the default `robots` value
    - Per-page-type rules live in it too. A blog post's title pattern, a service page's, the home page's — expressed once as a function of the page type, not retyped per file
3.  **Derive the canonical, do not write it:**
    - `new URL(Astro.url.pathname, Astro.site)` is the canonical for almost every page, and being derived it cannot disagree with the route it sits on
    - Accept an override prop for the genuine exceptions — a migrated _URL_, a syndicated copy, a filtered view that should point at its unfiltered parent — and let it come from the content schema, so the exception is data and reviewable
    - A hand-typed canonical is the single most common way two pages end up claiming to be the same page
4.  **Make `noindex` a decision with a reason:**
    - Thank-you pages, filtered or faceted listings, internal search results, staging routes, paginated pages beyond the first where the site does not want them indexed
    - It belongs in the same component as a prop, so a `noindex` page is visible as such at the call site rather than hidden in a stray meta tag
    - The inverse defect is real and worse: a `noindex` left over from a staging deploy on a page that should rank
5.  **Open Graph and social tags come from the same source as the page's own:**
    - `og:title` restating the page title and `og:description` restating the description is correct — what is not correct is a second, hand-written pair that drifts from the first
    - `og:url` is the canonical. If they can disagree, they eventually will
6.  **Titles and descriptions are content, so they belong to the schema:**
    - The content rules already require them; this rule is what consumes them
    - A page type with no content entry behind it — a landing page written as a route — still passes explicit props, and still through the same component

**Incorrect (`site` missing, metadata typed per page, canonical hand-written):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  // Bad: no `site`. Astro.site is undefined and the sitemap emits nothing
  integrations: [sitemap()],
});
```

```astro
---
// src/pages/services/migration.astro
---

<html lang="en">
  <head>
    <!-- Bad: three tags copied from another page, one of them not updated.
         The canonical is typed by hand and points at the page it was copied from -->
    <title>Migration services</title>
    <meta name="description" content="We help teams move their site." />
    <link rel="canonical" href="https://example.com/services/redesign" />
    <meta property="og:title" content="Website migration | Example" />
  </head>
  <body>
    <slot />
  </body>
</html>
```

**Correct (`site` set, one head component, canonical derived):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://example.com',
  integrations: [sitemap()],
});
```

```astro
---
// src/components/SeoHead.astro — the only place metadata is written
interface Props {
  title: string;
  description: string;
  pageType?: 'home' | 'article' | 'service';
  canonicalOverride?: string;
  noindex?: boolean;
  image?: string;
}

const {
  title,
  description,
  pageType = 'service',
  canonicalOverride,
  noindex = false,
  image = '/og-default.png',
} = Astro.props;

const SITE_NAME = 'Example';

// Title rules per page type, stated once
const fullTitle = pageType === 'home' ? SITE_NAME : `${title} | ${SITE_NAME}`;

// Derived, so it cannot disagree with the route it renders on
const canonical = canonicalOverride ?? new URL(Astro.url.pathname, Astro.site);
const socialImage = new URL(image, Astro.site);
---

<title>{fullTitle}</title>
<meta name="description" content={description} />
<link rel="canonical" href={canonical} />
{noindex && <meta name="robots" content="noindex, nofollow" />}

<meta property="og:title" content={fullTitle} />
<meta property="og:description" content={description} />
<meta property="og:url" content={canonical} />
<meta property="og:image" content={socialImage} />
<meta name="twitter:card" content="summary_large_image" />
```

```astro
---
// src/layouts/Base.astro — every page reaches metadata through here
import SeoHead from '@components/SeoHead.astro';

interface Props {
  title: string;
  description: string;
  pageType?: 'home' | 'article' | 'service';
  canonicalOverride?: string;
  noindex?: boolean;
}

const props = Astro.props;
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <SeoHead {...props} />
  </head>
  <body>
    <slot />
  </body>
</html>
```

Reference: [Configuration reference: site](https://docs.astro.build/en/reference/configuration-reference/)

### 3.2 URL Hygiene, Redirects & Migration

**Impact (HIGH):** A _URL_ is an identifier, and a site that serves the same page under two identifiers has told search engines it has two pages. `/blog` and `/blog/` is the common case, and no search engine cares which convention a site picks — it only cares that the site picks one. Mixed conventions arrive by accident: `trailingSlash` left at its default while links are typed both ways, so internal links, canonicals and the sitemap disagree with each other and with what the host actually serves. Migration is the same defect at scale. A relaunch that changes _URL_ structure without a redirect map does not lose ranking gradually; it drops every indexed _URL_ to a 404 at once, and the pages that took years to earn their position start over. Both are cheap to prevent before launch and expensive to repair after.

**Guidelines:**

1.  **Choose `trailingSlash` explicitly and let everything follow it:**
    - `trailingSlash: 'always'` or `'never'` in `astro.config.mjs` — the value matters far less than it being stated
    - Internal links, canonicals, sitemap entries and feed links all have to agree with it. A derived canonical (see the metadata rule) inherits this for free; hand-typed links do not
    - Confirm the host agrees: some platforms rewrite or redirect one form to the other, and a config that disagrees with the host produces a redirect on every internal navigation
2.  **Slugs are part of the content model, not an afterthought:**
    - Lowercase, hyphenated, no dates or ids unless they carry meaning, no stop words added for length
    - The entry `id` produces the slug by default; where a _URL_ has to differ from the filename, the override belongs in frontmatter so it is reviewable
    - A slug change is a _URL_ change, which means it is a redirect — not a rename
3.  **A migration starts with an inventory, before any code:**
    - Export the existing _URL_ list from analytics, the old sitemap and search console — not from the old codebase, which does not know which _URLs_ are actually indexed
    - Map every one to its new target, and preserve the path where there is no reason to change it. "While we are here" restructuring is how migrations lose pages
    - _URLs_ with no successor get a redirect to the nearest genuine equivalent, or are allowed to 404 deliberately — a blanket redirect of everything to the home page is treated as a soft 404 and helps nothing
4.  **Declare redirects in configuration, not in markup:**
    - `redirects` in `astro.config.mjs` keeps the map in one reviewable place and emits the right thing for the target platform
    - A meta-refresh tag or a client-side `location.replace()` is not a redirect: it costs a page load, and it does not pass the signal a 301 does
    - Use a permanent status for a permanent move; a temporary redirect on a permanent change keeps the old _URL_ alive indefinitely
5.  **Update internal links to the final target:**
    - Links pointing at a redirect still work, which is why they survive — each one is a wasted round trip and a diluted signal
    - After a migration, the internal link set is part of what gets updated, not something the redirects excuse
6.  **Verify after deployment, not before:**
    - Redirect behaviour depends on the host as much as the config, so the check that matters runs against production
    - Spot-check the highest-traffic old _URLs_ for a single-hop redirect to a 200, and watch for chains — a redirect to a redirect is a configuration that has been edited twice and reconciled zero times

**Incorrect (mixed conventions, and a relaunch with no map):**

```js
// astro.config.mjs
export default defineConfig({
  site: 'https://example.com',
  // Bad: unstated. Links are typed both ways and nothing reconciles them
});
```

```astro
<!-- Bad: three conventions in one nav, and a client-side redirect standing in
     for the old URL structure -->
<a href="/blog">Blog</a>
<a href="/services/">Services</a>
<a href="https://example.com/about">About</a>

<script>
  if (location.pathname.startsWith('/old-blog')) {
    location.replace('/blog');
  }
</script>
```

**Correct (one convention, redirects declared, links pointing at final targets):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
  trailingSlash: 'never',

  // The migration map, reviewable in one place. Permanent moves, permanent status
  redirects: {
    '/old-blog/[...slug]': {
      status: 301,
      destination: '/blog/[...slug]',
    },
    '/services/website-migration-2024': {
      status: 301,
      destination: '/services/migration',
    },
  },
});
```

```astro
---
// src/components/SiteNav.astro — one convention, links to final targets
const links = [
  { href: '/blog', label: 'Blog' },
  { href: '/services', label: 'Services' },
  { href: '/about', label: 'About' },
];
---

<nav>
  {links.map(({ href, label }) => <a href={href}>{label}</a>)}
</nav>
```

Reference: [Configured redirects](https://docs.astro.build/en/guides/routing/)

### 3.3 Sitemap & Feed Hygiene

**Impact (HIGH):** Installing `@astrojs/sitemap` is the easy half and the half everyone does; what it emits by default is every route the build produced. That includes the thank-you page, the internal search results route, the `noindex` staging page, the paginated archive nobody wants indexed, and — after a migration — the old _URLs_ still present as redirect sources. A sitemap is a statement that these are the pages worth crawling, so submitting one that contradicts the site's own canonical and robots directives is asking a crawler to choose between two answers. Feeds carry the same problem with an extra failure: a feed built from the wrong entry property produces links that 404 for every subscriber at once, and feed readers cache aggressively enough that the broken version outlives the fix.

**Guidelines:**

1.  **Filter the sitemap to what should actually be indexed:**
    - `@astrojs/sitemap` accepts a `filter` predicate, and it is not optional configuration on any real site
    - Exclude what the site itself marks as excluded: `noindex` routes, thank-you and confirmation pages, internal search, filtered or faceted listings, preview routes
    - Exclude redirect sources. A _URL_ that 301s belongs in the redirect map, never in the sitemap
    - Drafts are already excluded upstream, by the collection filter — a draft that reaches a route is a content-model defect, not a sitemap one
2.  **The sitemap agrees with the canonical, or it is wrong:**
    - Same origin, same trailing-slash convention, same _URL_ for the same page
    - `site` must be set for the integration to emit at all, which the metadata rule already requires
3.  **`lastmod` means the content changed:**
    - Emit it from the content's own `updatedDate`, not from the build timestamp — a build-stamped sitemap claims every page changed on every deploy, and a consumer that believes it learns to ignore it
    - Where there is no reliable modification date, omitting `lastmod` is better than fabricating one
4.  **Segment large sites rather than emitting one flat list:**
    - The integration paginates automatically past its entry limit, and `customPages`, `serialize` and per-section entries let a site express priority and change frequency where it genuinely differs
    - A blog archive and a service page do not change at the same rate, and saying so is the point of the fields
5.  **Feeds are built from the same filtered source as the pages:**
    - `@astrojs/rss` takes the collection, so it takes the same draft filter and the same sort
    - Links are built from `context.site` and the entry's `id` — Content Layer entries have no `slug`, and a feed built against `post.slug` emits `/blog/undefined/` for every item
    - Set the item's `pubDate` from the schema's date field, not from the file's mtime, which changes on checkout
6.  **Both are generated artifacts, so they are reviewed at the source:**
    - Nothing about a sitemap or feed should be hand-maintained; a hand-added entry is a fact that will stop being true
    - After a launch, fetch the emitted `/sitemap-index.xml` and confirm the count roughly matches the number of indexable pages — an order-of-magnitude gap is the fastest signal that a filter is missing

**Incorrect (everything the build emitted, and a feed built on a removed property):**

```js
// astro.config.mjs
export default defineConfig({
  site: 'https://example.com',
  // Bad: no filter. Thank-you pages, internal search, preview routes and the
  // old URLs kept for redirects are all submitted as canonical
  integrations: [sitemap()],
});
```

```js
// src/pages/rss.xml.js
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  // Bad: drafts included, and `post.slug` does not exist on Content Layer
  // entries — every link in the feed resolves to /blog/undefined/
  const posts = await getCollection('blog');

  return rss({
    title: 'Example Blog',
    description: 'Notes from the team',
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.pubDate,
      link: `/blog/${post.slug}/`,
    })),
  });
}
```

**Correct (filtered to indexable URLs, feed built from `id`):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

const EXCLUDED = ['/thank-you', '/search', '/preview'];

export default defineConfig({
  site: 'https://example.com',
  trailingSlash: 'never',
  integrations: [
    sitemap({
      // Only canonical, indexable URLs reach the sitemap
      filter: (page) => {
        const { pathname } = new URL(page);
        return !EXCLUDED.some((prefix) => pathname.startsWith(prefix));
      },
    }),
  ],
});
```

```js
// src/pages/rss.xml.js
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  // Same filter the routes use, so the feed cannot contain what the site does not
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  const sorted = posts.sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf(),
  );

  return rss({
    title: 'Example Blog',
    description: 'Notes from the team',
    site: context.site,
    items: sorted.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      // `id`, and the site's trailing-slash convention
      link: `/blog/${post.id}`,
    })),
  });
}
```

Reference: [@astrojs/sitemap](https://docs.astro.build/en/guides/integrations-guide/sitemap/)

### 3.4 Structured Data Generated From Content

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

---

## 4. Assets & Performance

### 4.1 Image Handling & Layout Stability

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

### 4.2 Fonts Through the Built-in API

**Impact (HIGH):** A web font is on the critical path for text, so every decision about it is a decision about when the page becomes readable. Loading one from a third-party font _CDN_ costs a _DNS_ lookup, a connection and a round trip to an origin the site does not control, before the first glyph can be requested — and it hands every visitor's request to that third party, which is a privacy question in several jurisdictions before it is a performance one. Hand-rolling the alternative is worse in a different direction: `@font-face` blocks written by hand routinely omit `font-display`, so text stays invisible while the file downloads, and omit a metric-matched fallback, so the page reflows when the real face arrives. The built-in _API_ makes all of that a config entry — it downloads and self-hosts the file, subsets it, generates the fallback, sets `font-display`, and emits the preload hint.

**Guidelines:**

1.  **Declare fonts in `fonts` in `astro.config.mjs`:**
    - Each entry names a `provider`, the family `name`, and the `cssVariable` the rest of the project will use
    - `fontProviders.fontsource()` and `fontProviders.google()` fetch at build time and self-host the result — the family comes from the provider, the bytes come from your own origin
    - A local file is declared the same way, so a licensed face and a public one are configured identically
2.  **Render `<Font />` once, in the base layout:**
    - It emits the `@font-face` rules and the preload hints for that variable
    - `preload` belongs on the face that renders above the fold, and only on that one — preloading every weight puts them all on the critical path and defeats the purpose
3.  **Consume the family through its variable, never by name:**
    - The `cssVariable` is the single reference. A stylesheet that also writes `font-family: 'Inter', sans-serif` by hand has a second source of truth that the config cannot keep correct
    - In a _TailwindCSS_ project this is the seam to the theme: the `@theme` token is defined as that variable, so `font-sans` resolves to the configured face — see the _TailwindCSS_ setup rule
4.  **Load the weights and styles the design uses, and no others:**
    - Each additional weight is another file; a variable font is usually one file covering the range
    - The design's actual set is a short list, and shipping the full family because it was easier is a cost paid on every first visit
5.  **What this replaces:**
    - `<link>` tags to a font _CDN_ in the document head
    - Hand-written `@font-face` blocks and the `font-display`, `unicode-range` and fallback-metric details that go with them
    - Font files committed to `public/` and referenced by _URL_

**Incorrect (third-party CDN, plus a hand-written face that reflows):**

```astro
---
// src/layouts/Base.astro
---

<head>
  <!-- Bad: DNS lookup, connection and round trip to an origin you do not
       control, before the first glyph is requested -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap"
    rel="stylesheet"
  />

  <style is:global>
    /* Bad: no font-display, so text is invisible while this downloads, and no
       metric-matched fallback, so the page reflows when it arrives */
    @font-face {
      font-family: 'Satoshi';
      src: url('/fonts/satoshi.woff2') format('woff2');
    }

    body {
      /* Bad: the family named by hand, in a second place */
      font-family: 'Inter', system-ui, sans-serif;
    }
  </style>
</head>
```

**Correct (declared once, self-hosted, consumed through its variable):**

```js
// astro.config.mjs
import { defineConfig, fontProviders } from 'astro/config';

export default defineConfig({
  fonts: [
    {
      name: 'Inter',
      cssVariable: '--font-inter',
      provider: fontProviders.fontsource(),
      // Only what the design uses
      weights: [400, 600],
      styles: ['normal'],
      subsets: ['latin'],
    },
  ],
});
```

```astro
---
// src/layouts/Base.astro
import { Font } from 'astro:assets';
import '../styles/global.css';
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <!-- preload only the face that renders above the fold -->
    <Font cssVariable="--font-inter" preload />
  </head>
  <body>
    <slot />
  </body>
</html>
```

```css
/* src/styles/global.css — the variable is the only reference to the family */
@import 'tailwindcss';

@theme {
  --font-sans: var(--font-inter), system-ui, sans-serif;
}
```

Reference: [Fonts](https://docs.astro.build/en/guides/fonts/)

### 4.3 Third-Party Scripts & Embeds

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

### 4.4 Prefetching & View Transitions

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

---

## 5. Project Structure

### 5.1 Route Responsibility, Layouts & Slots

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

### 5.2 Reusable & Page-Specific Components

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

### 5.3 TypeScript Path Aliases

**Impact (LOW):** `../../../components/Card.astro` encodes the importing file's location into the import, so the import breaks when either file moves — and the failure is silent in the sense that a bulk move produces dozens of them at once, each fixed by counting directory levels. It also makes imports unreadable: a reader has to resolve the path mentally to learn what is being imported, and a reviewer cannot tell whether two files are importing the same module. Aliases are a few lines in `tsconfig.json` that _Astro_ and _Vite_ both honour, and they turn every import into a statement about where a module lives in the project rather than where it sits relative to the file quoting it. This is the lowest-impact rule here — nothing breaks in production because of it — but it is also the cheapest to adopt and the most annoying to retrofit.

**Guidelines:**

1.  **Declare the aliases in `tsconfig.json`:**
    - `baseUrl` set to the project root, and a `paths` entry per top-level directory the project imports from
    - _Astro_ reads this configuration through _Vite_, so no second declaration is needed for the bundler
2.  **One alias per meaningful directory, not one catch-all:**
    - `@components/*`, `@layouts/*`, `@lib/*`, `@styles/*` say something at the import site; a lone `@/*` restates the relative path with a different prefix
    - Keep a general `@/*` alongside them for the occasional module that fits nowhere, not as the primary mechanism
    - The alias set mirrors the directory conventions in the route-responsibility rule — if a new alias does not correspond to a real directory, the structure is the thing to fix
3.  **Use them consistently:**
    - A file that imports one sibling relatively and another by alias makes both harder to scan. Same-directory imports are the reasonable exception: `./Card.astro` beside the file that uses it is clearer than an absolute path
    - Content collection imports (`astro:content`) and built-in modules are not aliased; they are already absolute names
4.  **Apply them everywhere they work:**
    - Component and layout imports in `.astro` frontmatter, modules in `.ts` files, and imports inside framework components
    - `@styles/global.css` in a layout is the same idea: the stylesheet has a location in the project, not relative to whoever imports it

**Incorrect (relative chains that encode the importer's location):**

```astro
---
// src/pages/blog/tags/[tag].astro
import Layout from '../../../layouts/Base.astro';
import Card from '../../../components/ContentCard.astro';
import { formatDate } from '../../../lib/dates';
import '../../../styles/global.css';
---
```

**Correct (aliases declared once, imports readable anywhere):**

```json
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@layouts/*": ["src/layouts/*"],
      "@lib/*": ["src/lib/*"],
      "@styles/*": ["src/styles/*"]
    }
  }
}
```

```astro
---
// src/pages/blog/tags/[tag].astro — the same imports, from anywhere
import Layout from '@layouts/Base.astro';
import Card from '@components/ContentCard.astro';
import { formatDate } from '@lib/dates';
import '@styles/global.css';
---
```

Reference: [TypeScript in Astro](https://docs.astro.build/en/guides/typescript/)

### 5.4 Markup Discipline Under the v7 Compiler

**Impact (HIGH):** For most of _Astro_'s history the compiler was forgiving: an unclosed `<div>` was accepted, invalid nesting was silently restructured into something valid, and the page rendered close enough to what the author meant that nobody investigated. In v7 the _Rust_ compiler is the default and the only option, and it is strict — **unclosed tags are errors** and semantically invalid _HTML_ is **no longer auto-corrected**. So markup that a codebase has carried for years, rendering fine, can fail the build on an upgrade with no change to the file that contains it. The whitespace default moved at the same time: `compressHTML` is now `'jsx'`, which strips space using _JSX_ rules, so the space between two inline elements that used to survive can disappear and run two words together. Both are cheap to satisfy deliberately and confusing to diagnose after the fact.

**Guidelines:**

1.  **Close every tag:**
    - Including the ones _HTML_ historically allowed to be left open — `<li>`, `<p>`, `<td>`, `<tr>`, `<option>` — because the compiler no longer infers where they end
    - Void elements are self-closed or written as single tags consistently: `<br />`, `<img ... />`, `<meta ... />`
    - Component tags follow the same rule, and an unclosed component is the version of this that is hardest to spot in a long template
2.  **Respect nesting rules instead of relying on repair:**
    - A `<div>` inside a `<p>`, a `<p>` inside a `<p>`, block content inside inline elements, a `<td>` outside a `<tr>` — previously restructured, now left as written or rejected
    - Interactive elements do not nest: a `<button>` inside an `<a>`, an `<a>` inside an `<a>`
    - Table structure is explicit — `<thead>`, `<tbody>`, `<tr>`, `<td>` — rather than assumed
3.  **Be explicit about significant whitespace:**
    - Under `compressHTML: 'jsx'`, the space between `</a>` and the next inline element on a separate line is removed, so `<a>Read</a> <span>more</span>` split across lines can render as "Readmore"
    - Where a space is meaningful, write it: `{' '}` between the elements, or keep them on one line
    - The failure is visual and easy to miss in review, so it shows up on pages with inline links inside paragraphs first
4.  **Reserved filenames are part of the routing surface:**
    - `src/fetch.ts` (and `src/fetch.js`) is reserved in v7 for advanced routing; a project using that path for its own helper must rename it or set `fetchFile`
    - This is the kind of collision that produces a confusing error rather than an obvious one, so it is worth knowing before the upgrade
5.  **Let the build be the check:**
    - This rule needs no separate linter — the compiler now enforces most of it, which is the change
    - The practical consequence is upgrade sequencing: run the build early against real templates rather than discovering the strictness at deploy time

**Incorrect (markup the old compiler repaired, and a space the new default removes):**

```astro
---
// src/components/ArticleList.astro
---

<ul>
  <!-- Bad: unclosed <li> — previously inferred, now a build error -->
  <li><a href="/blog/one">One</a>
  <li><a href="/blog/two">Two</a>
</ul>

<!-- Bad: a div cannot live inside a p. Previously restructured, now left
     invalid -->
<p>
  Introduction text.
  <div class="callout">A note about the above.</div>
</p>

<!-- Bad: interactive elements nested -->
<a href="/pricing"><button>See pricing</button></a>

<p>
  Read the
  <a href="/guide">migration guide</a>
  <em>before</em> starting.
</p>
<!-- Under compressHTML: 'jsx' the newline between the inline elements is not a
     space, so this renders as "…migration guidebefore starting." -->
```

**Correct (well-formed, correctly nested, whitespace stated):**

```astro
---
// src/components/ArticleList.astro
---

<ul>
  <li><a href="/blog/one">One</a></li>
  <li><a href="/blog/two">Two</a></li>
</ul>

<p>Introduction text.</p>
<aside class="callout">A note about the above.</aside>

<a href="/pricing" class="button">See pricing</a>

<p>
  Read the <a href="/guide">migration guide</a>{' '}
  <em>before</em> starting.
</p>
```

Reference: [Upgrade to Astro v7](https://docs.astro.build/en/guides/upgrade-to/v7/)

---

## 6. Styling

### 6.1 TailwindCSS v4 Setup & Theme Tokens

**Impact (HIGH):** In v4 there are two ways to install _TailwindCSS_ in an _Astro_ project and only one of them is current: `@astrojs/tailwind` is the deprecated v3-era integration, and `@tailwindcss/vite` runs the engine inside _Vite_'s own pipeline. A project on the old path gets a separate _PostCSS_ pass, slower rebuilds, and configuration in a file that v4 no longer treats as the source of truth. That is the setup half. The token half is what the setup exists for: in v4 the theme **is** the stylesheet, so a declared token generates its utilities and exposes a _CSS_ variable at once, and every arbitrary value written at a call site is a design decision made outside that system. The _Astro_-specific seam is the font: the Fonts _API_ produces a variable, and the theme token has to be defined as that variable, or the project has two names for one typeface and no guarantee they agree.

**Guidelines:**

1.  **Install through _Vite_:**
    - `tailwindcss` and `@tailwindcss/vite`, registered as `vite: { plugins: [tailwindcss()] }` in `astro.config.mjs`
    - `@astrojs/tailwind` is deprecated. A project still listing it in `integrations` is on the v3 path and should migrate before anything else here applies
    - There is no `tailwind.config.js` by default; a _JS_ config returns only through `@config`, and only when a legacy plugin requires it
2.  **One global stylesheet, imported once:**
    - `@import 'tailwindcss'` at the top of `src/styles/global.css`, and that file imported in the base layout — not in each page, and not in each component
    - The base layout is the single entry point, which matches the route-responsibility rule: the layout owns what every page shares
3.  **Declare design decisions in `@theme`:**
    - Colors, radii, fonts, breakpoints, shadows and type steps live in the `@theme` block, and each token generates its utilities automatically — `--color-brand` yields `bg-brand`, `text-brand`, `border-brand`
    - The spacing scale is the exception and is not redeclared: `--spacing` is _Tailwind_'s, and redefining it changes every margin, gap and size at once
    - Size the token layer to the project. A plain `@theme` is a complete system for most sites; the variable-backed `:root` / `.dark` layer earns its indirection only where something reads it — a theme swap, or a component generator
4.  **Wire the font token to the Fonts _API_ variable:**
    - The `cssVariable` declared in the `fonts` config is the only reference to the family, and `--font-sans: var(--font-inter), system-ui, sans-serif` in `@theme` is what makes `font-sans` resolve to it
    - Naming the family again in _CSS_ creates a second source of truth the font config cannot keep correct
5.  **Arbitrary values are a review flag:**
    - `bg-[#1d4ed8]`, `p-[13px]`, `text-[15px]` mean either the token exists and was not used, or the token is missing and should be added
    - Genuinely one-off geometry — `grid-cols-[auto_1fr]`, a mask _URL_, a third-party offset — is legitimate. A color almost never is, and a spacing value never is
6.  **Let the formatter own class order:**
    - `prettier-plugin-tailwindcss` sorts class attributes, including in `.astro` files, so ordering is never a review comment
    - Conflicting utilities inside one string still resolve by stylesheet order rather than by intent, which sorting does not fix — that is a defect to remove, not to reorder
7.  **Where this skill stops:**
    - Class composition inside a _React_ island, and the merge-aware helper that makes it safe, belong to the _React_ skills a project loads alongside this one. What is stated here is the project's setup and its token layer

**Incorrect (deprecated integration, a JS config v4 does not read, tokens invented at the call site):**

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind'; // deprecated v3 integration

export default defineConfig({
  integrations: [tailwind()],
});
```

```js
// tailwind.config.js — not the source of truth in v4
module.exports = {
  theme: {
    extend: {
      colors: { brand: '#1d4ed8' },
      fontFamily: { sans: ['Inter', 'sans-serif'] },
    },
  },
};
```

```astro
---
// src/components/Badge.astro
---

<!-- Bad: the brand color and the spacing invented here, and the font family
     named a second time, disconnected from the Fonts API variable -->
<span
  class="rounded-[7px] bg-[#1d4ed8] px-[13px] py-[5px] text-[13px] text-white"
  style="font-family: 'Inter', sans-serif"
>
  <slot />
</span>
```

**Correct (Vite plugin, tokens in CSS, font wired to the generated variable):**

```js
// astro.config.mjs
import { defineConfig, fontProviders } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://example.com',
  vite: { plugins: [tailwindcss()] },
  fonts: [
    {
      name: 'Inter',
      cssVariable: '--font-inter',
      provider: fontProviders.fontsource(),
    },
  ],
});
```

```css
/* src/styles/global.css — the theme is the stylesheet */
@import 'tailwindcss';

@theme {
  /* The seam: the token is defined as the variable the Fonts API generates */
  --font-sans: var(--font-inter), system-ui, sans-serif;

  --color-brand: oklch(0.53 0.19 262);
  --color-brand-strong: oklch(0.44 0.19 262);
  --radius-badge: 0.4375rem;
  --text-badge: 0.8125rem;
}
```

```astro
---
// src/layouts/Base.astro — imported once, for the whole site
import { Font } from 'astro:assets';
import '@styles/global.css';
---

<html lang="en">
  <head>
    <Font cssVariable="--font-inter" preload />
  </head>
  <body class="font-sans">
    <slot />
  </body>
</html>
```

```astro
---
// src/components/Badge.astro — every value resolves through a token
---

<span
  class="text-badge rounded-badge bg-brand px-3 py-1 text-white"
>
  <slot />
</span>
```

Reference: [Install Tailwind CSS with Astro](https://tailwindcss.com/docs/installation/framework-guides/astro)

### 6.2 Scoped Component Styles

**Impact (MEDIUM):** A `<style>` block in an `.astro` file is scoped to that component automatically, and only the rules the component actually renders are emitted — so component styles cannot leak, cannot be overridden by an unrelated file, and cannot accumulate into a global stylesheet nobody is willing to delete from. `is:global` opts out of all three at once. It is the correct tool for the handful of things that genuinely are global — resets, `body` rules, styling markup the component does not own, such as _Markdown_ output rendered through `<Content />` — and it is also the fastest way to turn a scoped system into the global one it replaced, because it makes a stubborn selector work immediately. The related defect is the inline `style` attribute used to pass a value: it bypasses the stylesheet entirely, so the value cannot be a token, cannot respond to a media query, and cannot be overridden by anything short of `!important`.

**Guidelines:**

1.  **Utilities first, scoped styles for what utilities cannot express:**
    - In a _TailwindCSS_ project most component styling is class attributes, and a scoped block is not a way to avoid them
    - It earns its place for keyframes, complex selectors, `::view-transition` rules, container-specific behaviour, and anything genuinely local that would be noise as a utility string
2.  **`is:global` names its reason:**
    - Legitimate: resets and base rules in the layout's stylesheet, styling `<Content />` output the component did not author, third-party markup the component wraps
    - Not legitimate: making a selector match because scoping got in the way. If a style has to reach a child component, the child should own it, or the value should travel as a prop
    - `:global()` around a single selector is the narrower tool when only part of a rule must escape
3.  **Pass dynamic values with `define:vars`, not inline styles:**
    - `define:vars={{ accent }}` exposes a frontmatter value to the scoped block as a _CSS_ variable, so the value stays in the stylesheet where variants and media queries can still reach it
    - An inline `style` attribute is reserved for values genuinely computed at runtime in the browser
4.  **Global stylesheets stay small and stay in one place:**
    - `src/styles/global.css` holds the _Tailwind_ import, the theme, and the handful of base rules — it is not where component styles go
    - A component style that has been promoted to global because two components needed it is usually a third component waiting to be extracted
5.  **Style what the component owns:**
    - A component reaching into a child's internals with a descendant selector is coupling that survives every refactor of the child
    - Where a parent must influence a child's appearance, the child exposes it — a prop, a `class` prop merged into its root, a data attribute it styles from

**Incorrect (global escape hatches and an inline value):**

```astro
---
// src/components/Callout.astro
const { accent } = Astro.props;
---

<div class="callout">
  <!-- Bad: the value bypasses the stylesheet, so no variant or media query
       can reach it -->
  <span class="callout__bar" style={`background: ${accent}`}></span>
  <slot />
</div>

<style is:global>
  /* Bad: global because a selector was not matching. Every .callout on the
     site is now styled by this component, including ones it never rendered */
  .callout {
    border-left: 4px solid;
    padding: 1rem;
  }

  /* Bad: reaching into a child component's internals */
  .callout .card__title {
    font-weight: 700;
  }
</style>
```

**Correct (scoped by default, variables for dynamic values, global only where it must be):**

```astro
---
// src/components/Callout.astro
interface Props {
  accent?: string;
}

const { accent = 'var(--color-brand)' } = Astro.props;
---

<div class="callout">
  <span class="callout__bar"></span>
  <slot />
</div>

<!-- Scoped: these rules cannot leak, and only what renders is emitted -->
<style define:vars={{ accent }}>
  .callout {
    border-left: 4px solid var(--accent);
    padding: 1rem;
  }

  .callout__bar {
    background: var(--accent);
  }
</style>
```

```astro
---
// src/layouts/Article.astro — global, with a reason: this styles Markdown
// output the layout renders but does not author
import { render } from 'astro:content';

const { Content } = await render(Astro.props.post);
---

<article class="prose">
  <Content />
</article>

<style is:global>
  .prose h2 {
    margin-block-start: 2rem;
  }

  .prose :where(a) {
    text-decoration: underline;
  }
</style>
```

Reference: [Styling and CSS](https://docs.astro.build/en/guides/styling/)

---

## 7. Build & Configuration

### 7.1 Internationalization on Day One

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

### 7.2 Structured Build Logging

**Impact (LOW):** A `console.log` in an `.astro` frontmatter runs at build time and prints into the middle of the build output with no level, no source and no timestamp, indistinguishable from the framework's own lines — so it is either lost in the noise or left behind as noise for everyone else. Worse, a warning printed that way is not a warning: it goes to stdout like everything else, so a _CI_ job filtering stderr never sees it, and a condition worth reporting — a collection that came back empty, a page built with no items — passes silently. `Astro.logger` gives the levels, routes errors to stderr, and labels the source; the stable top-level `logger` option decides the format, so the same code produces readable output locally and machine-parsable output in _CI_.

**Guidelines:**

1.  **Use `Astro.logger` in pages, components and endpoints:**
    - `info` for something worth stating once per build, `warn` for a condition that should be looked at, `error` for one that should fail a review
    - Errors go to stderr and everything else to stdout, which is what makes level filtering work downstream
    - Integrations receive their own logger through the hook parameters rather than reaching for the global one
2.  **Log conditions, not progress:**
    - The valuable lines are the ones that report something unexpected: a collection with zero entries, a page rendered with a missing optional field, a fallback that had to be used
    - A line printed unconditionally on every build is a line everyone learns to skip
3.  **Configure the handler at the top level:**
    - `logger` is a stable top-level config field as of v7 — not `experimental.logger`, which is what pre-v7 material shows
    - `logHandlers.json({ level: 'info' })` from `astro/config` produces structured output for _CI_ and log aggregation; a custom handler is declared with `{ entrypoint, config }`, and the entrypoint must be a _JavaScript_ file
    - The `--json` _CLI_ flag switches the format for a single run without touching the config
4.  **Do not log what does not belong in a build log:**
    - Secrets, request data, and full objects that will be dumped on every page of a collection
    - A build log is read by whoever is diagnosing a failure; volume is what makes it useless
5.  **Client-side logging is a different problem:**
    - Frontmatter runs at build time, so `Astro.logger` never reaches the browser. A `console` call inside a `<script>` or an island is client code, and belongs to the rules that govern that code

**Incorrect (unlabelled progress lines, and a warning that is not one):**

```astro
---
// src/pages/blog/index.astro
import { getCollection } from 'astro:content';

const posts = await getCollection('blog', ({ data }) => !data.draft);

// Bad: no level, no source, printed on every build, lost in the framework's
// own output
console.log('Building blog index');
console.log(posts);

// Bad: this is a warning printed to stdout, so CI filtering never sees it
if (posts.length === 0) {
  console.log('no posts!');
}
---
```

**Correct (levels that mean something, handler configured for the environment):**

```js
// astro.config.mjs
import { defineConfig, logHandlers } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
  // Stable top-level field in v7. Structured output for CI; the --json CLI
  // flag switches a single run without editing this
  logger: logHandlers.json({ level: 'info' }),
});
```

```astro
---
// src/pages/blog/index.astro
import { getCollection } from 'astro:content';

const posts = await getCollection('blog', ({ data }) => !data.draft);

// Reports a condition, at a level that routes correctly
if (posts.length === 0) {
  Astro.logger.warn('Blog index built with no published posts');
}
---

<Layout title="Blog" description="Notes from the team">
  {posts.map((post) => <PostCard post={post} />)}
</Layout>
```

Reference: [Configuration reference: logger](https://docs.astro.build/en/reference/configuration-reference/)

### 7.3 Typed Environment & Content Security Policy

**Impact (HIGH):** `import.meta.env` is untyped and unvalidated: a missing variable is `undefined` at the point of use rather than an error at startup, a typo produces the same, and the rule keeping secrets out of the browser is a naming convention — a variable that should have been server-only reaches the client bundle by being read in the wrong file, and nothing reports it. `astro:env` replaces the convention with a schema: each variable declares its context and its access, secrets are excluded from the bundle by construction, and a missing one fails the build. The second half of this rule is what a static site ships without noticing. _CSP_ has been stable since v6 as `security.csp` and works in every render mode, computing hashes for the site's own scripts and styles — so the reason it is absent from most _Astro_ projects is not that it is hard, it is that nothing prompts for it.

**Guidelines:**

1.  **Declare every variable in `env.schema`:**
    - `envField.string()`, `.number()`, `.boolean()`, `.enum()` with a `context` and an `access`
    - `context: 'client'` variables are available in both bundles and are therefore public, always
    - `context: 'server'` with `access: 'public'` stays in the server bundle; with `access: 'secret'` it is not bundled at all and is read at runtime
    - There is no secret client variable, because there is no safe way to send one — a value the browser needs is a public value, and treating it otherwise is the mistake this schema prevents
2.  **Import from the context-specific module:**
    - `import { API_URL } from 'astro:env/client'` and `import { API_SECRET } from 'astro:env/server'`
    - The import path is the check: a server-only value pulled into a component that hydrates is a build error rather than a leak
    - `import.meta.env` still works and still has none of this — it is the fallback for values outside the schema, which should be close to none
3.  **Mark optional values as optional, with a default:**
    - A variable declared required is one a broken deploy cannot skip past, which is the point
    - `optional: true` plus `default:` for the ones that genuinely have a sensible fallback
4.  **Turn `security.csp` on:**
    - `security: { csp: true }` is the baseline and works for prerendered and on-demand pages alike
    - The object form takes `algorithm`, `directives`, and `scriptDirective` / `styleDirective` with their own `hashes` and `resources` — which is how a site declares the third-party origins it actually loads
    - Every allowed origin should correspond to a script or embed the third-party rule already justified. A policy listing origins nobody can account for is a policy that has stopped meaning anything
5.  **A policy is verified in a browser, not in the config:**
    - The failure mode is a directive too narrow, which breaks a widget silently in production and shows up only in the console
    - Check the pages that carry embeds first — they are where the policy and the site disagree

**Incorrect (untyped access, a secret read where it can be bundled, no policy):**

```astro
---
// src/components/ContactForm.astro
// Bad: untyped, unvalidated. A missing or misspelled variable is `undefined`
const endpoint = import.meta.env.PUBLIC_API_URL;

// Bad: a secret read in a component that is passed to a hydrated island —
// nothing in the pipeline prevents it reaching the browser bundle
const apiKey = import.meta.env.CRM_API_KEY;
---

<ContactWidget client:visible endpoint={endpoint} apiKey={apiKey} />
```

```js
// astro.config.mjs
export default defineConfig({
  site: 'https://example.com',
  // Bad: no env schema, and no content security policy at all
});
```

**Correct (schema-declared, context-separated, policy enabled):**

```js
// astro.config.mjs
import { defineConfig, envField } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',

  env: {
    schema: {
      // Public: safe in both bundles, and the browser genuinely needs it
      PUBLIC_API_URL: envField.string({ context: 'client', access: 'public' }),
      // Server-only, non-sensitive
      PORT: envField.number({
        context: 'server',
        access: 'public',
        optional: true,
        default: 4321,
      }),
      // Secret: never bundled, read at runtime on the server
      CRM_API_KEY: envField.string({ context: 'server', access: 'secret' }),
    },
  },

  security: {
    csp: {
      algorithm: 'SHA-256',
      scriptDirective: {
        // Matches the one third-party tag the site actually loads
        resources: ["'self'", 'https://cdn.example-analytics.com'],
      },
      styleDirective: {
        resources: ["'self'"],
      },
    },
  },
});
```

```astro
---
// src/components/ContactForm.astro — the public value, from the client module
import { PUBLIC_API_URL } from 'astro:env/client';
---

<ContactWidget client:visible endpoint={PUBLIC_API_URL} />
```

```ts
// src/pages/api/contact.ts — the secret stays on the server, by import path
export const prerender = false;

import { CRM_API_KEY } from 'astro:env/server';

export async function POST({ request }: { request: Request }) {
  const response = await fetch('https://crm.example.com/leads', {
    method: 'POST',
    headers: { authorization: `Bearer ${CRM_API_KEY}` },
    body: await request.text(),
  });

  return new Response(null, { status: response.ok ? 204 : 502 });
}
```

Reference: [Environment variables](https://docs.astro.build/en/guides/environment-variables/)

### 7.4 Deployment Target & Toolchain Floor

**Impact (MEDIUM):** A prerendered _Astro_ site is a directory of files, and the whole point of producing it at build time is that serving it needs nothing more than a _CDN_ — no origin server, no cold start, no runtime to patch, and a copy in the data centre nearest each visitor. Deploying that output to a long-running server keeps every cost of a server and none of its benefits. The mirror defect is an adapter installed because a tutorial had one, which quietly opts the project into on-demand rendering it never needed. The toolchain floor is the other half: v7 requires **Node v22.12.0 or higher** and does not support odd-numbered majors, so a _CI_ image or a host default on an older or odd release fails in a way that reads as a code error. Stating the version in the project is what turns that into an immediate, obvious failure instead of a confusing one.

**Guidelines:**

1.  **Deploy static output to an edge platform:**
    - _Cloudflare Pages_, _Netlify_ and _Vercel_ all build and serve _Astro_ with no configuration, and the output is files
    - The choice among them is an operational one — this rule only requires that the target serves from an edge network rather than a single origin
2.  **The adapter follows the rendering decision, not the other way round:**
    - A fully prerendered site with no on-demand routes and no server islands needs no adapter
    - Install one when a route sets `prerender = false`, when a component uses `server:defer`, or when the platform's own features require it — and let its presence signal that something on the site renders on demand
    - Adapter and `output` are read together: the static-output rule owns which routes render where, and this rule owns where the result is served
3.  **State the platform's expectations in the project:**
    - `engines.node` in `package.json`, and the same version in the _CI_ configuration and the host's build settings — three places that will otherwise drift
    - Even-numbered majors only; v22.12.0 is the current floor
    - Lock the package manager version too where the host respects it, so a local build and a deploy build resolve the same tree
4.  **Build the way the platform builds:**
    - Run `astro build` in _CI_ on the same _Node_ version the host uses, and treat a warning-free local build on a different major as unverified
    - `astro check` in the same pipeline catches the type and template errors that a build alone can let through
5.  **Keep the deploy output reviewable:**
    - The build emits `dist/`; nothing should be edited there, and nothing generated should be committed
    - Where a host needs headers, redirects or a routing file, generate it from configuration — the redirect map already lives in `astro.config.mjs`

**Incorrect (an adapter and a server for output that is entirely static, versions unstated):**

```json
{
  "name": "example-site",
  "scripts": {
    "build": "astro build",
    "start": "node ./dist/server/entry.mjs"
  }
}
```

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  site: 'https://example.com',
  // Bad: every page is static, and they are being served by a long-running
  // Node process that has to be deployed, monitored and patched
  output: 'server',
  adapter: node({ mode: 'standalone' }),
});
```

**Correct (static output to an edge CDN, versions pinned):**

```json
{
  "name": "example-site",
  "engines": {
    "node": ">=22.12.0"
  },
  "packageManager": "yarn@4.5.0",
  "scripts": {
    "build": "astro check && astro build",
    "preview": "astro preview"
  }
}
```

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
  trailingSlash: 'never',
  // Prerendered output, served as files from the edge. No adapter, because
  // no route on this site renders on demand
  output: 'static',
});
```

```yaml
# .github/workflows/deploy.yml — the same floor the host uses
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22.12.0'
      - run: yarn install --immutable
      - run: yarn build
```

Reference: [Deploy your Astro site](https://docs.astro.build/en/guides/deploy/)
