---
title: .astro Components Before Framework Components
impact: CRITICAL
description: Makes the .astro component the default unit of composition and turns reaching for React, Vue or Svelte into a decision that has to name the interactivity it needs.
tags: components, islands, javascript, composition
---

## .astro Components Before Framework Components

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
