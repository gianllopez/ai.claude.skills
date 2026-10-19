---
title: Describe Brand Pieces, Not a Product
impact: CRITICAL
description: A brand design system defines how every piece derived from a company brand must look; it is not a website, an app or a slide deck
tags: scope, brand, derived designs
---

## Describe Brand Pieces, Not a Product

**Impact (CRITICAL):** When the system turns into a website, an app or a presentation, its rules start serving one product and stop being reusable. Every later project then inherits product decisions as if they were brand rules.

**Guidelines:**

1. Write every rule, token and component as a brand-level guideline that any derived piece can apply (web, app, print, email, social, documents)
2. Keep product pages, app screens and real presentations out of the system; they are derived designs built from it
3. Components show how a pattern looks with the brand (a `navbar`, a `slide`), not a finished screen of a specific product
4. A component enters the system only when any derived design could use it without product content (a `hero` yes; a pricing table with the brand's plans no); otherwise offer to build it as a derived design, outside the system

**Incorrect (the system ships a finished landing page):**

```text
components/
├── home/                 # full marketing site for askit.com.co
└── pricing/              # ASKIT plans and prices
```

**Correct (the system ships brand-level patterns; the site is a derived design):**

```text
components/
├── navbar/               # how a top bar looks with the brand
├── footer/
└── card/
# askit.com.co is built in its own project from these components
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
