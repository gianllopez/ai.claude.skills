---
title: Hydration Directives & Island Boundaries
impact: CRITICAL
description: Requires the client:* directive to match the component's position and priority, and the island boundary to wrap only what is actually interactive.
tags: islands, hydration, client-directives, performance
---

## Hydration Directives & Island Boundaries

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
