---
title: 'Content Elements: Lists, Tables & Media'
impact: MEDIUM
description: Requires list, table, figure, and time elements for the data they represent instead of styled div collections.
tags: semantics, content, jsx
---

## Content Elements: Lists, Tables & Media

**Impact (MEDIUM):** Utilities describe layout, not meaning. A `grid grid-cols-4` of `div`s renders like a table and is one nowhere else: no column association, no sortable header, nothing a scraper or an export routine can read. Choosing the element that matches the data costs the same number of lines and keeps the utilities purely presentational.

**Guidelines:**

1.  **Collections:**
    - A `map()` over data almost always produces a `ul` or `ol`; only `li` may be a direct child
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
    - Every human-facing date string comes from `dayjs`, never from `toLocaleDateString` or hand-assembled formatting, so format and locale are decided in one place instead of per component
    - The configured instance — plugins and locale — lives in `core/lib/dayjs.ts`, and components import that rather than the package (see the folder-structure rule)

**Incorrect (div grid imitating a table, div list, unformatted date):**

```tsx
type Props = { invoices: Invoice[] };

export function InvoiceList({ invoices }: Props) {
  return (
    <>
      {/* Bad: no header/cell association, nothing extractable */}
      <div className="grid grid-cols-3 gap-y-2">
        <div className="font-semibold">Invoice</div>
        <div className="font-semibold">Date</div>
        <div className="font-semibold">Total</div>
        {invoices.map((i) => (
          <Fragment key={i.id}>
            <div>{i.number}</div>
            <div>{i.issuedAt.toLocaleDateString()}</div>
            <div>{i.total}</div>
          </Fragment>
        ))}
      </div>
      {/* Bad: the caption is a sibling div, so nothing ties it to the image */}
      <div className="mb-6">
        <img src={chartUrl} className="mb-2 w-full rounded-lg" />
        <div className="text-sm text-muted-foreground">Monthly totals</div>
      </div>
      {/* Bad: a list that is not a list */}
      <div className="space-y-1">
        <div>Draft saved automatically</div>
        <div>Exports include line items</div>
      </div>
    </>
  );
}
```

**Correct (real table, real list, machine-readable date):**

```tsx
import { dayjs } from '~/core/lib/dayjs';

type Props = { invoices: Invoice[] };

export function InvoiceList({ invoices }: Props) {
  return (
    <>
      <table className="mb-6 w-full border-separate border-spacing-0 text-left">
        <caption className="pb-2 text-sm text-muted-foreground">
          Recent invoices
        </caption>
        <thead>
          <tr>
            <th scope="col" className="font-semibold">
              Invoice
            </th>
            <th scope="col" className="font-semibold">
              Date
            </th>
            <th scope="col" className="font-semibold">
              Total
            </th>
          </tr>
        </thead>
        <tbody>
          {invoices.map((i) => (
            <tr key={i.id}>
              <td>{i.number}</td>
              <td>
                <time dateTime={dayjs(i.issuedAt).toISOString()}>
                  {dayjs(i.issuedAt).format('L')}
                </time>
              </td>
              <td>{i.total}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <figure className="mb-6">
        <img src={chartUrl} className="mb-2 w-full rounded-lg" />
        <figcaption className="text-sm text-muted-foreground">
          Monthly totals
        </figcaption>
      </figure>
      <ul className="list-none space-y-1">
        <li>Draft saved automatically</li>
        <li>Exports include line items</li>
      </ul>
    </>
  );
}
```

Reference: [The table element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table)
