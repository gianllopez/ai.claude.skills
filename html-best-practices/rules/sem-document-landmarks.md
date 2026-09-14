---
title: Document Outline & Sectioning
impact: HIGH
description: Enforces landmark elements, one main region per page, an unbroken heading rank, and a title and description declared per page, instead of generic div nesting.
tags: semantics, structure, html
---

## Document Outline & Sectioning

**Impact (HIGH):** The element carries the meaning; the utility class carries the presentation. When every block is a `div`, the only structure a page has left is its class names, and the outline has to be reconstructed by whoever reads it next. Nothing breaks visibly, which is exactly why this decays quietly and is expensive to retrofit — but three of its failures are concrete rather than abstract: a page that adds its own `main` on top of the layout's leaves the document with two, a skipped heading rank makes the outline lie about what contains what, and pages that never declare a title are indistinguishable in the tab bar and the history.

**Guidelines:**

1.  **Page skeleton:**
    - Build the page from `header`, `nav`, `main`, `footer`, and `aside`
    - Exactly one `main` per rendered page, and it is not nested inside another landmark
2.  **Landmarks belong to the shared layout:**
    - The skeleton lives in the layout template, wrapped around the slot where each page's content is inserted
    - A page that opens with its own `main` is how a document ends up with two
3.  **Sectioning rules:**
    - `section` requires a heading — a `section` with no heading should be a `div`
    - `article` is for self-contained content that would still make sense extracted (a post, a comment, a product card)
    - Nesting a `section` inside an `article` is fine; using either purely to attach padding is not
4.  **Heading rank is structure, not size:**
    - Ranks descend one at a time; never skip from `h1` to `h4` to get a smaller font
    - Visual size comes from utilities (`text-2xl`, `text-sm`), rank comes from the tag
    - One `h1` per page, describing the page — not the site name on every route
5.  **Every page declares its own title and description:**
    - Both are set per page, through whatever mechanism the framework provides; a page that inherits them from the layout is indistinguishable from every other one in the tab bar, the history, and a bookmark
    - The title names the page the same thing its `h1` does — when the two disagree, one of them is wrong
    - The description summarises that page in a sentence, not the product's tagline repeated everywhere
6.  **When `div` is right:**
    - A `div` is the correct element when no other element carries the meaning: a flex/grid container, a positioning context, an overflow clip

**Incorrect (div soup, skipped heading rank, section used as a padding box, no title or description):**

```html
<!-- Bad: no page-specific title or description, so the tab and the history
     entry repeat whatever the layout said -->
<div class="mx-auto max-w-5xl">
  <div class="flex items-center justify-between py-4">
    <div class="text-xl font-bold">Acme</div>
    <div class="flex gap-4">
      <a href="/pricing">Pricing</a>
      <a href="/docs">Docs</a>
    </div>
  </div>
  <div class="py-10">
    <h1 class="text-4xl font-bold">Reports</h1>
    <!-- Bad: rank skipped to get a smaller size -->
    <h4 class="text-lg font-medium">Latest activity</h4>
    <!-- Bad: section with no heading, used only for spacing -->
    <section class="space-y-4">
      <div class="rounded-lg border p-4">
        <div class="font-semibold">Q3 summary</div>
        <p>Revenue grew 12% quarter over quarter.</p>
      </div>
    </section>
  </div>
</div>
```

**Correct (skeleton in the layout, content in the page, descending ranks):**

```html
<!-- layout — owns the landmarks -->
<div class="mx-auto max-w-5xl">
  <header class="flex items-center justify-between py-4">
    <span class="text-xl font-bold">Acme</span>
    <nav class="flex gap-4">
      <a href="/pricing">Pricing</a>
      <a href="/docs">Docs</a>
    </nav>
  </header>
  <div class="flex gap-8 py-10">
    <main class="flex-1">
      <!-- page content is inserted here -->
    </main>
    <aside class="w-64">
      <!-- recent activity -->
    </aside>
  </div>
  <footer class="py-6 text-sm text-muted-foreground">© Acme</footer>
</div>
```

```html
<!-- reports page — content only, no second main -->
<!-- Good: the title says what the h1 says, and the description is about this
     page rather than about the product -->
<title>Reports · Acme</title>
<meta
  name="description"
  content="Activity and summaries for the current quarter."
/>

<h1 class="mb-6 text-4xl font-bold">Reports</h1>
<section class="space-y-4">
  <!-- Good: rank descends, size is a utility -->
  <h2 class="text-lg font-medium">Latest activity</h2>
  <article class="rounded-lg border p-4">
    <h3 class="font-semibold">Q3 summary</h3>
    <p>Revenue grew 12% quarter over quarter.</p>
  </article>
</section>
```

Reference: [HTML sections and outlines](https://html.spec.whatwg.org/multipage/sections.html)
