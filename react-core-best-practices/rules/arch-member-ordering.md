---
title: Prop & Member Ordering
impact: LOW
description: Fixes the order of a component's props by the direction they flow — data, configuration, boolean state, callbacks — and the order of the members inside its body, so the same component reads the same way at every site.
tags: architecture, conventions, props
---

## Prop & Member Ordering

**Impact (LOW):** A component's surface is read far more often than it is written, and with no order there is nothing to read it against: finding whether a component reports anything back means scanning every line of its type, and a prop added in review lands wherever the diff happened to open. The same component then appears in one order in its declaration, another in its signature, and a third at each call site, so no two of them can be compared. None of this breaks at runtime — which is why it never gets fixed unless a rule can be pointed at.

**Guidelines:**

1.  **Four groups, ordered by the direction each one flows:**
    - **Data** — the domain values the component renders: `invoice`, `customer`
    - **Configuration** — what modulates that rendering with a value: `variant`, `size`, `tone`, `placeholder`
    - **Boolean state** — what only toggles: `isDisabled`, `isLoading`, `isPending`
    - **Callbacks** — the one group that flows outward: `onSelect`, `onPress`, `onConfirm`
    - The sequence is the request's own direction, the same argument that fixes `Variables` → `Response` → `Data` in the query-layer rule. A component is identified by its data, qualified by its configuration, toggled by its flags, and only then reports back
2.  **`children` closes the type:**
    - It is written as real JSX children rather than an attribute, so it has no position at a call site and only ever appears in the declaration
    - Placing it last keeps the four groups contiguous instead of splitting the data group around a prop no caller ever writes by name
3.  **Alphabetical inside each group:**
    - The groups carry the meaning; alphabetical is only the tiebreaker, and it exists so the order is fully determined rather than left to whoever typed first
    - Without it the rule stops halfway: two components with the same four groups still list them differently, and review has nothing to point at
4.  **The same order in all three places:**
    - The `Props` type, the destructuring in the signature, and the attributes at every call site
    - No blank lines anywhere: the type, the signature and the JSX are each one continuous list. A blank line between groups is a second grouping signal competing with the order itself, which is the same reason the syntax-conventions rule keeps them out of JSX
    - `key` and `ref` are not props and never reach the component, so they lead the attribute list, ahead of the data group
5.  **Only the object literal is ordered:**
    - When the type is an intersection — `React.ComponentProps<'button'> & VariantProps<typeof BUTTON_VARIANTS>` — there is no list of ours to sort, and the typing-conventions rule already requires that shape
    - The order applies to the properties written by hand, wherever they appear in the intersection
6.  **One axis of this is enforceable, and the project must turn it on:**
    - `react/jsx-sort-props` ships with `eslint-plugin-react` but is off by default. Declare it as `['error', { callbacksLast: true, noSortAlphabetically: true }]`, and confirm it is actually active before trusting any of it — an unconfigured project enforces none of this, and the rule is silently review-only
    - That is the only setting that does not contradict this rule. `callbacksLast` maps exactly: the implementation detects a callback as `/^on[A-Z]/`, which is the outward group and nothing else
    - `shorthandLast` does not reach the flag group, so it stays off. Shorthand there means an attribute carrying no value at all — `<Button isDisabled />` — and `isDisabled={!canEdit}` is an ordinary prop to the rule, sorted among the data and configuration ones
    - Alphabetical is off for the same reason: it cannot be scoped to a group, and left on it rejects the correct examples below, wanting `isDisabled` between `invoice` and `size`
    - `reservedFirst` stays off too: it hoists `children` to the front, contradicting the second guideline
    - Nothing checks the type declaration at all. With the callbacks automated, review owns the remaining three groups and the whole of the declaration
7.  **Inside the body, the same outside-in reading:**
    - **Hooks**, in the order of what owns the value: the environment first (router params, context), then queries and mutations, then local `useState` and `useRef`, and `useEffect` last — the only one that acts instead of reading
    - **Guards** — the early returns for the outcomes the query can produce. They sit immediately after the hooks because every hook must run before any return
    - **Derived values**, after the guards and not before: the guards are what narrow the query result, so a derived value written above them carries a fallback that is dead one line down (see the async-states rule)
    - **Handlers** — the `handle*` implementations, when there are any. A one-expression body stays inline at its prop, so this group is often empty by design (see the syntax-conventions rule)
    - **The `return`**

**Incorrect (three orders for one component, and nothing that says where the next prop goes):**

```tsx
// ./app/components/invoice-row/index.tsx

// Bad: a callback between two data props, the toggles scattered through the
// list, and `children` buried in the middle
type Props = {
  onArchive: () => void;
  invoice: Invoice;
  isLoading?: boolean;
  size: 'sm' | 'lg';
  children: React.ReactNode;
  customer: Customer;
  onSelect: (id: string) => void;
  isDisabled?: boolean;
  variant: 'ghost' | 'solid';
};

// Bad: the signature reorders them again, so the type is no longer a map of it
export function InvoiceRow({
  invoice,
  onSelect,
  isDisabled,
  size,
  customer,
  variant,
  onArchive,
  isLoading,
  children,
}: Props) {
```

```tsx
// Bad: and the call site invents a third order — this cannot be read against
// either of the two above
<InvoiceRow
  isDisabled={!canEdit}
  invoice={invoice}
  onSelect={handleSelect}
  size="sm"
  customer={invoice.customer}
  onArchive={() => archive.mutate(invoice.id)}
  variant="ghost"
/>
```

**Correct (the four groups, alphabetical within each, `children` last):**

```tsx
// ./app/components/invoice-row/index.tsx

type Props = {
  customer: Customer;
  invoice: Invoice;
  size: 'sm' | 'lg';
  variant: 'ghost' | 'solid';
  isDisabled?: boolean;
  isLoading?: boolean;
  onArchive: () => void;
  onSelect: (id: string) => void;
  children: React.ReactNode;
};

// Good: the signature is the type read straight down, in the same order
export function InvoiceRow({
  customer,
  invoice,
  size,
  variant,
  isDisabled,
  isLoading,
  onArchive,
  onSelect,
  children,
}: Props) {
```

**Correct (React DOM) — the same order at the call site, with `key` ahead of it:**

```tsx
{
  invoices.map((i) => (
    <InvoiceRow
      key={i.id}
      customer={i.customer}
      invoice={i}
      size="sm"
      variant="ghost"
      isDisabled={!canEdit}
      onArchive={() => archive.mutate(i.id)}
      onSelect={handleSelect}
    >
      <InvoiceStatus status={i.status} />
    </InvoiceRow>
  ));
}
```

**Correct (React Native) — the group is defined by the direction, not by the prop's name, so `onPress` sorts with the rest:**

```tsx
{
  invoices.map((i) => (
    <InvoiceRow
      key={i.id}
      customer={i.customer}
      invoice={i}
      size="sm"
      variant="ghost"
      isDisabled={!canEdit}
      onLongPress={() => setSelected(i.id)}
      onPress={() => handleSelect(i.id)}
    >
      <InvoiceStatus status={i.status} />
    </InvoiceRow>
  ));
}
```

**Incorrect (a body with no reading order):**

```tsx
export function InvoiceListScreen() {
  // Bad: a handler declared before anything it closes over exists
  const handleArchive = async (id: string) => {
    await archive.mutateAsync(id);
    toast.success('Invoice archived');
  };

  // Bad: the effect sits above the state it is here to synchronize
  useEffect(() => {
    const subscription = listenForInvoicePushes();

    return () => subscription.remove();
  }, []);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const archive = useArchiveInvoice();

  // Bad: derived above the guards, so it carries a fallback for a state that
  // cannot reach this line once the guards exist
  const total = invoices.data?.reduce((acc, i) => acc + i.amount, 0) ?? 0;

  const { status } = useSearchParams();
  const invoices = useInvoices({ variables: { status } });

  if (invoices.isPending) {
    return <InvoiceListSkeleton />;
  }

  return <InvoiceTable invoices={invoices.data} total={total} />;
}
```

**Correct (hooks outside-in, guards, derived, handlers, return):**

```tsx
export function InvoiceListScreen() {
  const { status } = useSearchParams();

  const invoices = useInvoices({ variables: { status } });
  const archive = useArchiveInvoice();

  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    const subscription = listenForInvoicePushes();

    return () => subscription.remove();
  }, []);

  if (invoices.isPending) {
    return <InvoiceListSkeleton />;
  }

  if (invoices.isError) {
    return <InvoiceListError onRetry={invoices.refetch} />;
  }

  // Good: the guards already narrowed `data`, so there is nothing to fall back to
  const total = invoices.data.reduce((acc, i) => acc + i.amount, 0);

  const handleArchive = async (id: string) => {
    await archive.mutateAsync(id);
    toast.success('Invoice archived');
  };

  return (
    <InvoiceTable
      invoices={invoices.data}
      selectedId={selectedId}
      total={total}
      onArchive={handleArchive}
      onSelect={setSelectedId}
    />
  );
}
```

Reference: [react/jsx-sort-props](https://github.com/jsx-eslint/eslint-plugin-react/blob/master/docs/rules/jsx-sort-props.md)
