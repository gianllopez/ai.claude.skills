---
title: 'Pending, Empty & Error States'
impact: HIGH
description: Treats pending, empty, and error branches as required output of any async view instead of assuming the data arrived.
tags: data, error-handling, rendering
---

## Pending, Empty & Error States

**Impact (HIGH):** An async view has four outcomes and most components implement one. The missing branches are exactly what users hit: a blank panel that never explains itself, a crash on `data.items.map` when the request failed, a spinner that wipes content already on screen during a background refetch. Review should be able to point at each of the four branches in the code — if one is not there, it was not designed, it was forgotten.

**Guidelines:**

1.  **Four questions, always answered:**
    - What shows while pending, what shows when the result is empty, what shows when it fails, and what shows on success
    - _React Query_ names three of them for you (`isPending`, `isError`, `data`); the empty one is the one you have to write
2.  **Read the query through its name, do not destructure it:**
    - Give the query a meaningful name and reach its parts by dot notation — `reports.isPending`, `reports.data`
    - This is not only style: the query result is a discriminated union, so `if (reports.isPending) { … }` narrows `reports.data` to a defined value for the rest of the function. Destructuring severs that link, and `data` stays possibly-undefined no matter how many flags you checked
3.  **`isPending` is not `isFetching`:**
    - `isPending` is the first load, when there is genuinely nothing to show — the only state that may render a skeleton
    - `isFetching` is also true for background refetches, so gating the skeleton on it makes content the user is reading disappear and come back on every revalidation
    - A page change is neither of those: the key itself changes, so `isPending` is legitimately true and the skeleton fires again. Where the query serves the previous page as placeholder data, `isPlaceholderData` is the flag to dim on — the option that enables it belongs to the query layer
4.  **The empty branch must exist:**
    - A successful response with zero rows is a distinct outcome, not a shorter list
    - What it says is a product decision; that it exists at all is a review one
5.  **Errors surface, they do not vanish:**
    - Either an `isError` branch or `throwOnError` with an `ErrorBoundary` — pick one per surface and stay consistent
    - A fetcher that catches and returns `[]` makes this branch unreachable (see the query-layer rule)
6.  **Do not collapse the branches:**
    - `data ?? []` renders pending, error, and empty as the same empty list, which is how a broken screen ends up looking like a working one

**Incorrect (one branch of four — pending, failure and empty all render the same empty list):**

```tsx
export default function ReportsRoute() {
  const { data } = useReports();

  return (
    <ul>
      {(data ?? []).map((report) => (
        <li key={report.id}>{report.name}</li>
      ))}
    </ul>
  );
}
```

**Correct (all four branches, and a refetch that does not wipe the list):**

```tsx
export default function ReportsRoute() {
  const reports = useReports();

  // Good: only the first load has nothing to show yet
  if (reports.isPending) {
    return <ReportListSkeleton />;
  }

  if (reports.isError) {
    return <ErrorState title="Reports could not be loaded" />;
  }

  // Good: a successful empty result is its own outcome, with a way forward
  if (reports.data.length === 0) {
    return (
      <EmptyState
        title="No reports yet"
        description="Create one to start tracking activity."
        action={<Button>New report</Button>}
      />
    );
  }

  // Good: a background refetch dims the list instead of replacing it with a skeleton
  return (
    <ul className={cn(reports.isFetching && 'opacity-60')}>
      {reports.data.map((report) => (
        <li key={report.id}>{report.name}</li>
      ))}
    </ul>
  );
}
```

Reference: [Query status and fetch status](https://tanstack.com/query/latest/docs/framework/react/guides/queries)
