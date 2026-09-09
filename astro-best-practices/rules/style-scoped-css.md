---
title: Scoped Component Styles
impact: MEDIUM
description: Keeps component CSS inside the component's scoped style block, reserves is:global for styles that must escape it, and passes dynamic values through define:vars rather than inline style attributes.
tags: styling, css, scoped, global, astro
---

## Scoped Component Styles

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
