---
title: Document Outline & Sectioning
impact: HIGH
description: Enforces landmark elements, one main region per page, an unbroken heading rank, and a title and description declared per page, instead of generic div nesting.
tags: semantics, structure, jsx
---

## Document Outline & Sectioning

**Impact (HIGH):** The element carries the meaning; the utility class carries the presentation. When every block is a `div`, the only structure a page has left is its class names, and the outline has to be reconstructed by whoever reads it next. Nothing breaks visibly, which is exactly why this decays quietly and is expensive to retrofit — but three of its failures are concrete rather than abstract: a route that adds its own `main` leaves the page with two, a skipped heading rank makes the outline lie about what contains what, and pages that never declare a title are indistinguishable in the tab bar and the history.

**Guidelines:**

1.  **Page skeleton:**
    - Build the page from `header`, `nav`, `main`, `footer`, and `aside`
    - Exactly one `main` per rendered page, and it is not nested inside another landmark
2.  **Landmarks belong to the layout route:**
    - In a nested-routing setup the skeleton lives in the layout route, wrapped around the slot where the router inserts the child route
    - A route component that opens with its own `main` is how a page ends up with two
3.  **Sectioning rules:**
    - `section` requires a heading — a `section` with no heading should be a `div`
    - `article` is for self-contained content that would still make sense extracted (a post, a comment, a product card)
    - Nesting a `section` inside an `article` is fine; using either purely to attach padding is not
4.  **Heading rank is structure, not size:**
    - Ranks descend one at a time; never skip from `h1` to `h4` to get a smaller font
    - Visual size comes from utilities (`text-2xl`, `text-sm`), rank comes from the tag
    - One `h1` per page, describing the page — not the site name on every route
5.  **Every page declares its own title and description:**
    - Both are set per page, through whatever mechanism the framework provides; a page that inherits them is indistinguishable from every other one in the tab bar, the history, and a bookmark
    - The title names the page the same thing its `h1` does — when the two disagree, one of them is wrong
    - The description summarises that page in a sentence, not the product's tagline repeated everywhere
6.  **When `div` is right:**
    - A `div` is the correct element when no other element carries the meaning: a flex/grid container, a positioning context, an overflow clip

**Incorrect (div soup, skipped heading rank, section used as a padding box, no title or description):**

```tsx
// Bad: the page declares no title and no description, so the tab and the history
// entry repeat whatever the root said
export default function ReportsRoute() {
  return (
    <div className="mx-auto max-w-5xl">
      <div className="flex items-center justify-between py-4">
        <div className="text-xl font-bold">Acme</div>
        <div className="flex gap-4">
          <Link to="/pricing">Pricing</Link>
          <Link to="/docs">Docs</Link>
        </div>
      </div>
      <div className="py-10">
        <h1 className="text-4xl font-bold">Reports</h1>
        {/* Bad: rank skipped to get a smaller size */}
        <h4 className="text-lg font-medium">Latest activity</h4>
        {/* Bad: section with no heading, used only for spacing */}
        <section className="space-y-4">
          <div className="rounded-lg border p-4">
            <div className="font-semibold">Q3 summary</div>
            <p>Revenue grew 12% quarter over quarter.</p>
          </div>
        </section>
      </div>
    </div>
  );
}
```

**Correct (skeleton in the layout, content in the route, descending ranks):**

```tsx
// ./app/routes/layout.tsx — owns the landmarks
export default function AppLayout() {
  return (
    <div className="mx-auto max-w-5xl">
      <header className="flex items-center justify-between py-4">
        <span className="text-xl font-bold">Acme</span>
        <nav className="flex gap-4">
          <Link to="/pricing">Pricing</Link>
          <Link to="/docs">Docs</Link>
        </nav>
      </header>
      <div className="flex gap-8 py-10">
        <main className="flex-1">
          <Outlet />
        </main>
        <aside className="w-64">
          <RecentActivity />
        </aside>
      </div>
      <footer className="py-6 text-sm text-muted-foreground">© Acme</footer>
    </div>
  );
}
```

```tsx
// ./app/routes/reports.tsx — content only, no second main
export default function ReportsRoute() {
  return (
    <>
      {/* Good: the title says what the h1 says, and the description is about this
          page rather than about the product */}
      <title>Reports · Acme</title>
      <meta
        name="description"
        content="Activity and summaries for the current quarter."
      />
      <h1 className="mb-6 text-4xl font-bold">Reports</h1>
      <section className="space-y-4">
        {/* Good: rank descends, size is a utility */}
        <h2 className="text-lg font-medium">Latest activity</h2>
        <article className="rounded-lg border p-4">
          <h3 className="font-semibold">Q3 summary</h3>
          <p>Revenue grew 12% quarter over quarter.</p>
        </article>
      </section>
    </>
  );
}
```

Reference: [HTML sections and outlines](https://html.spec.whatwg.org/multipage/sections.html)
