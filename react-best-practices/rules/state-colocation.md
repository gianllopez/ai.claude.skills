---
title: State Colocation & Ownership
impact: HIGH
description: Keeps state at the lowest component that reads it and assigns shared state to its real owner — the URL, the query cache, the nearest common ancestor, or the store.
tags: state, architecture, routing
---

## State Colocation & Ownership

**Impact (HIGH):** State placed too high re-renders subtrees that do not care about it and turns every component in between into a prop conduit. State kept in a component when it belongs to the _URL_ produces links that do not restore what the user was looking at and a back button that does nothing. Ownership is a design decision, and review should be able to name the owner of every piece of state on screen.

**Guidelines:**

1.  **Push it down:**
    - State lives in the lowest component that reads it — a row's menu flag belongs to the row, not to the page
2.  **Lift only to the nearest common ancestor:**
    - Of the components that actually need it, which is usually one or two levels, not the route
    - When the nearest common ancestor turns out to be the root, that is the signal for the store — not for a prop that travels five levels to get there
3.  **The _URL_ is state:**
    - Anything that should survive a reload or be shareable belongs in the query string: filters, tabs, pagination, sort order, the open detail panel
    - Read and write it through the router's own search-param _API_; a `useState` mirror of a search param is a bug in waiting
4.  **Server data has an owner already:**
    - The query cache owns it; do not copy it into `useState` (see the query-layer rule)
5.  **Shared state goes to the store, never to a context of your own:**
    - `zustand` is the answer for state read across the tree, in every case: a selector subscribes a component to one slice, so an update re-renders only what reads that slice (see the render-stability rule)
    - A context you author to share state is a store with worse ergonomics — it re-renders every consumer whatever changed inside the value, and splitting it only postpones the problem
    - Libraries that use context internally are not this decision. What the rule forbids is reaching for `createContext` to move your own state around

**Incorrect (page owns everything, filters vanish on reload, one menu re-renders the table):**

```tsx
export default function InvoicesRoute() {
  const [status, setStatus] = useState('all');
  const [sort, setSort] = useState('date');
  // Bad: opening a row menu re-renders the entire page
  const [openRowId, setOpenRowId] = useState<string | null>(null);

  return (
    <InvoiceTable
      status={status}
      sort={sort}
      openRowId={openRowId}
      onOpenRow={setOpenRowId}
      onStatusChange={setStatus}
      onSortChange={setSort}
    />
  );
}
```

**Correct (the URL owns what must be shareable, the table owns what its children share, the row owns its own menu):**

```tsx
export default function InvoicesRoute() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Good: reload, share, and the back button all work
  const status = searchParams.get('status') ?? 'all';
  const sort = searchParams.get('sort') ?? 'date';

  return (
    <InvoiceTable
      status={status}
      sort={sort}
      onFilterChange={setSearchParams}
    />
  );
}
```

```tsx
type Props = {
  status: string;
  sort: string;
};

function InvoiceTable({ status, sort }: Props) {
  const invoices = useInvoices({ variables: { status, sort } });

  // Good: lifted exactly one level — the header checkbox and the rows both read
  // it, and nothing above this table does
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  return (
    <table>
      <thead>
        <SelectAll
          rows={invoices.data}
          selected={selectedIds}
          onChange={setSelectedIds}
        />
      </thead>
      <tbody>
        {invoices.data.map((i) => (
          <InvoiceRow
            key={i.id}
            invoice={i}
            isSelected={selectedIds.includes(i.id)}
          />
        ))}
      </tbody>
    </table>
  );
}
```

```tsx
type Props = {
  invoice: Invoice;
  isSelected: boolean;
};

function InvoiceRow({ invoice, isSelected }: Props) {
  // Good: opening this menu re-renders one row and nothing above it
  const [isMenuOpen, setMenuOpen] = useState(false);

  return (
    <tr className={cn(isSelected && 'bg-accent')}>
      <td>{invoice.number}</td>
      <td>
        <RowMenu open={isMenuOpen} onOpenChange={setMenuOpen} />
      </td>
    </tr>
  );
}
```

```ts
// ./app/core/hooks/stores/settings.ts

import { create } from 'zustand';

type SettingsStore = {
  theme: 'light' | 'dark';
  density: 'compact' | 'comfortable';
  setTheme: (theme: SettingsStore['theme']) => void;
  setDensity: (density: SettingsStore['density']) => void;
};

// Good: read across the tree and owned by nobody in particular, so it is a store
export const useSettingsStore = create<SettingsStore>((set) => ({
  theme: 'light',
  density: 'comfortable',
  setTheme: (theme) => set({ theme }),
  setDensity: (density) => set({ density }),
}));
```

```tsx
// Good: one selector, one subscription — this re-renders on density, not on theme
const density = useSettingsStore((s) => s.density);
```

Reference: [Sharing state between components](https://react.dev/learn/sharing-state-between-components)
