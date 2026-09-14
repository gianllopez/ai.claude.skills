---
title: 'Content Elements: Lists, Tables & Media'
impact: MEDIUM
description: Requires list, table, figure, and time elements for the data they represent instead of styled div collections.
tags: semantics, content, html
---

## Content Elements: Lists, Tables & Media

**Impact (MEDIUM):** Utilities describe layout, not meaning. A `grid grid-cols-4` of `div`s renders like a table and is one nowhere else: no column association, no sortable header, nothing a scraper or an export routine can read. Choosing the element that matches the data costs the same number of lines and keeps the utilities purely presentational.

**Guidelines:**

1.  **Collections:**
    - A loop over data almost always produces a `ul` or `ol`; only `li` may be a direct child
    - Drop the marker with `list-none`, not by switching to `div`
    - Key/value pairs are a `dl` with `dt` / `dd`
2.  **Tabular data:**
    - Real tabular data uses `table` with `thead`, `tbody`, `th` carrying `scope`, and a `caption`
    - Conversely, never use `table` for page layout — that is what `grid` is for
    - Utilities still apply: `w-full`, `text-left`, `border-separate`, `border-spacing-0`
3.  **Media:**
    - `figure` + `figcaption` when an image, chart, or code block has a caption
    - Decorative shapes belong in CSS (background utilities), not in an `img`
4.  **Dates carry both values:**
    - Dates and durations use `time` with a `dateTime` attribute — the formatted string is the child, the _ISO_ value is the attribute
    - Every human-facing date string is produced by one date-formatting utility, imported from the one module that configures it — never `toLocaleDateString` or hand-assembled formatting scattered per component, which decides format and locale differently in each place

**Incorrect (div grid imitating a table, div list, unformatted date):**

```html
<!-- Bad: no header/cell association, nothing extractable -->
<div class="grid grid-cols-3 gap-y-2">
  <div class="font-semibold">Invoice</div>
  <div class="font-semibold">Date</div>
  <div class="font-semibold">Total</div>
  <div>INV-001</div>
  <div>3/14/2026</div>
  <div>$420.00</div>
</div>

<!-- Bad: the caption is a sibling div, so nothing ties it to the image -->
<div class="mb-6">
  <img src="/chart.png" class="mb-2 w-full rounded-lg" />
  <div class="text-sm text-muted-foreground">Monthly totals</div>
</div>

<!-- Bad: a list that is not a list -->
<div class="space-y-1">
  <div>Draft saved automatically</div>
  <div>Exports include line items</div>
</div>
```

**Correct (real table, real list, machine-readable date):**

```html
<table class="mb-6 w-full border-separate border-spacing-0 text-left">
  <caption class="pb-2 text-sm text-muted-foreground">
    Recent invoices
  </caption>
  <thead>
    <tr>
      <th scope="col" class="font-semibold">Invoice</th>
      <th scope="col" class="font-semibold">Date</th>
      <th scope="col" class="font-semibold">Total</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>INV-001</td>
      <td><time datetime="2026-03-14">Mar 14, 2026</time></td>
      <td>$420.00</td>
    </tr>
  </tbody>
</table>

<figure class="mb-6">
  <img src="/chart.png" class="mb-2 w-full rounded-lg" />
  <figcaption class="text-sm text-muted-foreground">Monthly totals</figcaption>
</figure>

<ul class="list-none space-y-1">
  <li>Draft saved automatically</li>
  <li>Exports include line items</li>
</ul>
```

Reference: [The table element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table)
