---
title: 'Pending, Empty & Error States'
impact: HIGH
description: Requires every outcome a query can produce to have a defined presentation, as a branch of the region it owns, as a property of the control it feeds, or in the boundary above.
tags: data, error-handling, rendering
---

## Pending, Empty & Error States

**Impact (HIGH):** An async view has up to four outcomes and most components implement one. The missing ones are exactly what users hit: a blank panel that never explains itself, a crash on `data.items.map` when the request failed, a spinner that wipes content already on screen during a background refetch. Review should be able to point at where each outcome the query can produce is answered — as a branch here, as a property of the control the query feeds, or in the boundary above. What review does not accept is an outcome nobody decided.

**Guidelines:**

1.  **Every outcome the query can produce has a defined presentation:**
    - Pending, error and success always exist. Empty exists only when a successful response can be empty — a collection
    - A query for one entity has no empty outcome: the entity is there or the request failed, so an `if (!invoice)` sitting after the error branch is dead code that reads as caution
    - _React Query_ names three of them for you (`isPending`, `isError`, `data`); the empty one is the one you have to write
2.  **The surface decides the shape of the answer, never whether there is one:**
    - When the query is the reason a region exists, each outcome is a branch of that region, with its own `return`
    - When the query feeds a control inside a region owned by something else — the options of a select, a count on a badge — the outcomes are properties of that control. Pending is `disabled`, and failure is the control saying it has nothing to offer. Replacing the form around it is the defect, not the fix
    - Delegating is the third shape: `throwOnError` sends failure to an `ErrorBoundary`, `useSuspenseQuery` sends pending to a `Suspense` fallback. The outcome is still answered, one level up. Pick one shape per surface, so no outcome is answered twice and none falls between the two
3.  **Read the query through its name, do not destructure it:**
    - Give the query a meaningful name and reach its parts by dot notation — `reports.isPending`, `reports.data`
    - This is not only style: the query result is a discriminated union, so `if (reports.isPending) { … }` narrows `reports.data` to a defined value for the rest of the function. Destructuring severs that link, and `data` stays possibly-undefined no matter how many flags you checked
4.  **`isPending` is not `isFetching`:**
    - `isPending` is the first load, when there is genuinely nothing to show — the only state that may render a skeleton
    - `isFetching` is also true for background refetches, so gating the skeleton on it makes content the user is reading disappear and come back on every revalidation
    - A page change is neither of those: the key itself changes, so `isPending` is legitimately true and the skeleton fires again. Where the query serves the previous page as placeholder data, `isPlaceholderData` is the flag to dim on — the option that enables it belongs to the query layer
    - A disabled query is pending forever: `enabled: false` leaves `status` at `pending` with `fetchStatus` at `idle`, so a skeleton gated on `isPending` never leaves a screen that is waiting on its own precondition. `isLoading` is `isPending && isFetching` — the flag that means in flight — and it, or the enabling condition itself, is what gates the skeleton there
5.  **The empty branch must exist wherever the outcome can:**
    - A successful response with zero rows is a distinct outcome, not a shorter list
    - What it says is a product decision; that it exists at all is a review one
    - A virtualized list gives it a dedicated slot — `ListEmptyComponent` — which renders in place of the rows. Passing it is how the branch stops being something each screen remembers to write
6.  **Errors surface, they do not vanish:**
    - Either an `isError` branch or `throwOnError` with an `ErrorBoundary` — pick one per surface and stay consistent
    - A fetcher that catches and returns `[]` makes this branch unreachable (see the query-layer rule)
7.  **Do not collapse the branches:**
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

**Correct (React DOM) — all four branches, and a refetch that does not wipe the list:**

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
      {reports.data.map((r) => (
        <li key={r.id}>{r.name}</li>
      ))}
    </ul>
  );
}
```

**Correct (React Native) — the same four branches, two of them handed to the list:**

```tsx
export default function ReportsScreen() {
  const reports = useReports();

  // Good: only the first load has nothing to show yet
  if (reports.isPending) {
    return <ReportListSkeleton />;
  }

  if (reports.isError) {
    return <ErrorState title="Reports could not be loaded" />;
  }

  return (
    <FlatList
      data={reports.data}
      keyExtractor={(r) => r.id}
      renderItem={({ item }) => <ReportRow report={item} />}
      // Good: the empty branch is a slot rather than something this screen has
      // to remember to write before the list
      ListEmptyComponent={
        <EmptyState
          title="No reports yet"
          description="Create one to start tracking activity."
          action={<Button>New report</Button>}
        />
      }
      // Good: a background refetch is a pull indicator, not a skeleton that
      // replaces content the user is reading
      refreshControl={
        <RefreshControl
          refreshing={reports.isFetching}
          onRefresh={reports.refetch}
        />
      }
    />
  );
}
```

Both screens above own their region, so every outcome is a `return`. A query that only feeds a control answers the same outcomes as properties of that control, and the region around it never disappears. Nothing here is a host element, so the shape is the same on either platform.

**Correct (a query that feeds a control) — the same outcomes, none of them a `return`:**

```tsx
// ./components/customer-field.tsx

export function CustomerField() {
  const customers = useCustomers();

  return (
    <Field label="Customer">
      {/* Good: the outcomes are answered on the control, so the form around it
          renders once instead of being replaced by a skeleton */}
      <Select
        disabled={!customers.isSuccess || customers.data.length === 0}
        options={customers.isSuccess ? customers.data : []}
        placeholder={getPlaceholder(customers)}
      />
    </Field>
  );
}

// Declared with function so it hoists: the control above names it before this line
function getPlaceholder(customers: ReturnType<typeof useCustomers>) {
  if (customers.isPending) {
    return 'Loading customers…';
  }

  if (customers.isError) {
    return 'Customers could not be loaded';
  }

  // Good: the empty outcome exists here too — it just reads as a label instead
  // of taking over the screen
  if (customers.data.length === 0) {
    return 'No customers yet';
  }

  return 'Select a customer';
}
```

Reference: [Query status and fetch status](https://tanstack.com/query/latest/docs/framework/react/guides/queries)
