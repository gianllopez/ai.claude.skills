# React Core Best Practices

**Version 1.0.0**  
_Gian López_  
_August 2026_

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring _React_ codebases. Humans  
> may also find it useful, but guidance here is optimized for automation  
> and consistency by AI-assisted workflows.

---

## Abstract

Standards for _React_ itself — the parts that do not change when the renderer does. Ordered by what actually breaks under review: effects and state first, because a misplaced `useEffect` or a duplicated source of truth is a behavioral defect on any platform; then the architecture of a component, from where its files live to how its props are typed and composed; then data ownership, where a typed query layer holds the cache and components consume state instead of orchestrating requests; and finally the identity work the _React Compiler_ does not reach. Every rule that reads differently on web and on _React Native_ shows both, so it is never abstract for the reader applying it. What belongs to a renderer is deliberately absent: semantic _HTML_, _TailwindCSS_ v4 and `shadcn/ui` live in `react-best-practices`, _NativeWind_ and _Expo_ configuration in `react-native-with-expo-best-practices`. A project loads this skill plus the one for its platform.

---

## Table of Contents

1. [State & Effects](#1-state--effects) — `CRITICAL`
   - [1.1 Effect Discipline](#11-effect-discipline)
   - [1.2 Derived Values Over Stored State](#12-derived-values-over-stored-state)
   - [1.3 State Colocation & Ownership](#13-state-colocation--ownership)
   - [1.4 List Keys & Component Identity](#14-list-keys--component-identity)
2. [Component Architecture](#2-component-architecture) — `CRITICAL`
   - [2.1 Folder Structure & Layer Boundary](#21-folder-structure--layer-boundary)
   - [2.2 Minimal Markup Depth](#22-minimal-markup-depth)
   - [2.3 Component File Structure](#23-component-file-structure)
   - [2.4 Composition Over Configuration](#24-composition-over-configuration)
   - [2.5 Component Extraction Threshold](#25-component-extraction-threshold)
   - [2.6 Component Typing Conventions](#26-component-typing-conventions)
   - [2.7 TypeScript Type System & Domain Organization](#27-typescript-type-system--domain-organization)
   - [2.8 Core Utilities & Configuration](#28-core-utilities--configuration)
   - [2.9 Syntax & Conciseness Conventions](#29-syntax--conciseness-conventions)
   - [2.10 Class Composition & Conditional Classes](#210-class-composition--conditional-classes)
3. [Data Flow](#3-data-flow) — `HIGH`
   - [3.1 Query Layer & Data Ownership](#31-query-layer--data-ownership)
   - [3.2 Pending, Empty & Error States](#32-pending-empty--error-states)
4. [Performance & Robustness](#4-performance--robustness) — `MEDIUM`
   - [4.1 Render Stability & Memoization](#41-render-stability--memoization)

---

## 1. State & Effects

### 1.1 Effect Discipline

**Impact (CRITICAL):** `useEffect` is an escape hatch for synchronizing with systems outside _React_ — the _DOM_, a subscription, a timer, a third-party _SDK_. Used for anything else it produces the defects that dominate _React_ review: a second render pass with a visible flash, cascades of effects firing in an order nobody controls, stale closures reading last render's values, and infinite loops when a dependency is recreated every render. Most effects in a codebase should not exist.

**Guidelines:**

1.  **What an effect is actually for:**
    - Subscribing to something outside _React_ that offers no hook of its own — an `EventTarget`, a socket, a browser _API_ — with a cleanup that unsubscribes
    - Imperatively driving a non-_React_ widget (a map, a chart, a media element)
    - A store that already exposes a hook is not one of these: it is read through its selector, never through an effect
    - Nothing else qualifies by default
2.  **What belongs in an event handler:**
    - Anything that happens _because the user did something_ — sending the request, showing the toast, navigating
    - An effect that watches a state flag to detect that an event happened is an event handler written backwards
3.  **What belongs in render:**
    - Any value computable from props or state (see the derived-values rule)
4.  **Dependencies are not negotiable:**
    - Never silence the linter with an incomplete array; an omitted dependency is a stale closure waiting for a bug report
    - If a complete array causes a loop, the fix is to move the value out of the effect — into a handler, a ref, or a reducer — not to trim the array
5.  **Cleanup is mandatory for anything ongoing:**
    - Subscriptions, timers, and in-flight requests are cancelled in the cleanup, which also runs between re-renders and on _StrictMode_'s double invocation
6.  **Do not fetch on mount:**
    - Component-level data belongs to the query layer, never to an effect (see the query-layer rule)
    - An effect that fetches also has to reimplement caching, cancellation, retries, and an error branch — and it usually reimplements none of them

**Incorrect (fetch on mount, effect deriving state, effect acting as an event handler, trimmed dependencies):**

```tsx
type Props = {
  cart: Cart;
  onPurchased: () => void;
};

export function CheckoutPanel({ cart, onPurchased }: Props) {
  const [status, setStatus] = useState<'idle' | 'submitting' | 'done'>('idle');
  const [total, setTotal] = useState(0);
  const [coupons, setCoupons] = useState<Coupon[]>([]);

  // Bad: fetching on mount — no cache, no cancellation, no error branch
  useEffect(() => {
    fetch('/api/coupons')
      .then((r) => r.json())
      .then(setCoupons);
  }, []);

  // Bad: derived value stored in state — renders twice and flashes 0 on the first pass
  useEffect(() => {
    setTotal(cart.items.reduce((sum, i) => sum + i.price * i.quantity, 0));
  }, [cart]);

  // Bad: an event handler written backwards — it reacts to state instead of to the click
  useEffect(() => {
    if (status === 'done') {
      onPurchased();
      toast.success('Order placed');
    }
    // Bad: onPurchased omitted to stop the loop, so it is now a stale closure
  }, [status]);

  return (
    <button type="button" onClick={() => setStatus('submitting')}>
      Pay {total}
    </button>
  );
}
```

**Correct (React DOM) — the query layer loads, the mutation tracks its own pending state, the handler owns the consequences:**

```tsx
type Props = {
  cart: Cart;
  onPurchased: () => void;
};

export function CheckoutPanel({ cart, onPurchased }: Props) {
  const coupons = useCoupons();
  const purchase = usePurchase();

  // Good: derived during render, so it can never disagree with the cart
  const total = cart.items.reduce((sum, i) => sum + i.price * i.quantity, 0);

  // Good: what happens because of the click lives in the click
  const handlePay = () => {
    purchase.mutate(cart, {
      onSuccess: () => {
        onPurchased();
        toast.success('Order placed');
      },
    });
  };

  return (
    <>
      <CouponPicker coupons={coupons} />
      <Button type="button" onClick={handlePay} disabled={purchase.isPending}>
        Pay {total}
      </Button>
    </>
  );
}
```

**Correct (React Native) — the same three moves, in the platform's idiom:**

```tsx
type Props = {
  cart: Cart;
  onPurchased: () => void;
};

export function CheckoutPanel({ cart, onPurchased }: Props) {
  const coupons = useCoupons();
  const purchase = usePurchase();

  // Good: derived during render, so it can never disagree with the cart
  const total = cart.items.reduce((sum, i) => sum + i.price * i.quantity, 0);

  // Good: what happens because of the press lives in the press
  const handlePay = () => {
    purchase.mutate(cart, {
      onSuccess: () => {
        onPurchased();
        Toast.show('Order placed');
      },
    });
  };

  return (
    <>
      <CouponPicker coupons={coupons} />
      <Button onPress={handlePay} disabled={purchase.isPending}>
        Pay {total}
      </Button>
    </>
  );
}
```

The effects that survive review are the ones talking to something outside _React_ that offers no hook of its own. The platforms differ only in which systems those are.

```tsx
// Good (web): an external system, complete deps, real cleanup
useEffect(() => {
  const socket = connectToRoom(roomId);
  socket.on('message', onMessage);

  return () => socket.close();
}, [roomId, onMessage]);
```

```tsx
// Good (React Native): the same shape. The platform's own systems are what
// qualify here — AppState, Keyboard, Linking, Dimensions — and each returns a
// subscription whose remove() is the cleanup
useEffect(() => {
  const subscription = AppState.addEventListener('change', onAppStateChange);

  return () => subscription.remove();
}, [onAppStateChange]);
```

Reference: [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)

### 1.2 Derived Values Over Stored State

**Impact (HIGH):** Every piece of state that could have been computed is a second source of truth, and two sources of truth eventually disagree. The disagreement reaches users as a stale total, a filter one keystroke behind, or a row that survives its own deletion. Deriving during render makes the inconsistent state impossible to represent, which is a stronger guarantee than remembering to synchronize it.

**Guidelines:**

1.  **If it can be computed, compute it:**
    - A value derived from props or state is calculated in render, not stored
2.  **Props copied into state freeze at mount:**
    - `useState(props.value)` captures the first value and stops responding to the prop; the component then works right up until the prop changes, which is what makes it hard to spot in review
    - Use the prop directly, or remount deliberately with `key` when a reset is the actual intent (see the identity rule)
3.  **Store the minimal representation:**
    - An `id`, not the selected object; a sort key, not a sorted copy; a filter string, not the filtered array
    - Storing the object means holding a snapshot that goes stale when the source updates
4.  **Deriving is not a performance question:**
    - An unmemoized derivation is correct, and the compiler memoizes what render produces anyway
    - A hand-written `useMemo` around a derivation is the exception, and it has to say what the compiler could not see (see the render-stability rule)
5.  **Flags derived from status stay in render:**
    - `const isPending = status === 'submitting'` is a variable, never its own state

**Incorrect (a prop frozen into state, two states an effect has to keep in sync, a stale snapshot):**

```tsx
type Props = {
  users: User[];
  query: string;
};

export function UserPicker({ users, query }: Props) {
  // Bad: a prop copied into state — nothing ever calls setLocalQuery, so from the
  // second render on this can only be stale
  const [localQuery, setLocalQuery] = useState(query);
  const [filtered, setFiltered] = useState(users);
  const [hasResults, setHasResults] = useState(true);
  // Bad: holds a snapshot — after the user is renamed upstream this still shows the old name
  const [selected, setSelected] = useState<User | null>(null);

  useEffect(() => {
    const next = users.filter((u) => u.name.includes(localQuery));
    setFiltered(next);
    setHasResults(next.length > 0);
  }, [users, localQuery]);

  return (
    <Results
      items={filtered}
      empty={!hasResults}
      selectedName={selected?.name}
      onSelect={setSelected}
    />
  );
}
```

**Correct (the prop is read as a prop, one state for the one real input, the rest derived):**

```tsx
type Props = {
  users: User[];
  query: string;
};

export function UserPicker({ users, query }: Props) {
  // Good: store the identity, not the object
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Good: cannot disagree with users or query, because it is recomputed from them
  const filtered = users.filter((u) => u.name.includes(query));
  const selected = users.find((u) => u.id === selectedId) ?? null;

  return (
    <Results
      items={filtered}
      selectedName={selected?.name}
      onSelect={setSelectedId}
    />
  );
}
```

Reference: [Choosing the state structure](https://react.dev/learn/choosing-the-state-structure)

### 1.3 State Colocation & Ownership

**Impact (HIGH):** State placed too high re-renders subtrees that do not care about it and turns every component in between into a prop conduit. State kept in a component when it belongs to the _URL_ produces links that do not restore what the user was looking at and a back button that does nothing. Ownership is a design decision, and review should be able to name the owner of every piece of state on screen.

**Guidelines:**

1.  **Push it down:**
    - State lives in the lowest component that reads it — a row's menu flag belongs to the row, not to the page
2.  **Lift only to the nearest common ancestor:**
    - Of the components that actually need it, which is usually one or two levels, not the route
    - When the nearest common ancestor turns out to be the root, that is the signal for the store — not for a prop that travels five levels to get there
3.  **The route is state:**
    - Anything that should survive a reload, a deep link, or the back button belongs to the router's params: filters, tabs, pagination, sort order, the open detail panel
    - Read and write it through the router's own params _API_ — `useSearchParams` on the web, `useLocalSearchParams` with `router.setParams` under _Expo Router_. A `useState` mirror of a param is a bug in waiting either way
    - The params shape is declared above the component as `SearchParams`, never as a literal inside the generic. A type literal in a type argument is a declaration hiding in an expression: it cannot be referenced by the handler that writes those same params, and it is read at the widest point of the line instead of at the top of the file
    - What the param buys differs by platform and the ownership does not. On the web it is a shareable link and a working back button; on mobile it is a deep link that opens the screen already filtered, and state that survives the OS reclaiming the process
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

**Correct (React DOM) — the URL owns what must be shareable:**

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

**Correct (React Native) — the route params own the same thing:**

```tsx
// Good: the params shape is a declaration, not a literal buried in a generic
type SearchParams = {
  status?: string;
  sort?: string;
};

export default function InvoicesScreen() {
  // Good: a deep link opens this screen already filtered, and the state
  // survives the OS reclaiming the process
  const { status = 'all', sort = 'date' } =
    useLocalSearchParams<SearchParams>();

  return (
    <InvoiceTable
      status={status}
      sort={sort}
      // Good: one expression, so it stays at the prop
      onFilterChange={(next) => router.setParams(next)}
    />
  );
}
```

Below the route the platforms stop differing: the two levels of ownership that follow are the same on both, and only the elements change.

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

### 1.4 List Keys & Component Identity

**Impact (HIGH):** `key` is not a lint requirement to satisfy — it is how _React_ decides which component instance corresponds to which item. An index key on a list that can be reordered, filtered, or prepended attaches the wrong state to the wrong row: an open menu jumps, an input keeps the previous row's draft, a checkbox stays checked on a different item. The list looks correct right up until state enters it.

**Guidelines:**

1.  **The key is identity from the data:**
    - `item.id` — never the array index, never `Math.random()`, never the position in a composite string
    - A virtualized list takes that same identity through its own prop instead of through `key`: `keyExtractor={(t) => t.id}`. The prop changes, the rule does not — and the cost of getting it wrong is higher there, because recycled rows carry state from the item they used to show
2.  **Index keys are only safe on a static list:**
    - Never reordered, never filtered, never prepended, and holding no internal state
3.  **A key that changes every render destroys the subtree:**
    - Focus, scroll position, uncontrolled input values, and animation state all reset, on every render
    - This is what a random key buys: the warning goes away and the defect gets worse
4.  **Use `key` deliberately to reset:**
    - `<TaskEditor key={task.id} />` restarts the editor's internal state when the task changes — this replaces the effect that copied the prop into state
5.  **Keys are scoped to siblings:**
    - They need to be unique among their siblings, not globally
6.  **A missing identity is a data problem:**
    - Concatenating the index to silence the warning hides it; if the payload has no stable id, fix the payload

**Incorrect (index keys on a filterable list):**

```tsx
type Props = {
  tasks: Task[];
  query: string;
};

export function TaskList({ tasks, query }: Props) {
  const visible = tasks.filter((t) => t.title.includes(query));

  return (
    <ul>
      {/* Bad: filtering shifts every index — row state follows the wrong task */}
      {visible.map((t, index) => (
        <TaskRow key={index} task={t} />
      ))}
    </ul>
  );
}
```

**Incorrect (a random key, which silences the warning and rebuilds every row):**

```tsx
type Props = { entries: LogEntry[] };

export function LogList({ entries }: Props) {
  return (
    <ul>
      {/* Bad: the payload has no id, so the warning was silenced with a random key.
          Every render produces new keys, so every row is destroyed and rebuilt —
          focus, scroll position and any uncontrolled input inside them reset */}
      {entries.map((e) => (
        <LogRow key={Math.random()} entry={e} />
      ))}
    </ul>
  );
}
```

**Incorrect (an effect undoing the defaults that mounting already applied):**

```tsx
type Props = { task: Task };

function TaskEditor({ task }: Props) {
  const form = useForm<FormValues>({
    defaultValues: { title: task.title },
  });

  // Bad: defaultValues are read at mount, so this effect exists only to patch an
  // instance that should have been a new one
  useEffect(() => {
    form.reset({ title: task.title });
  }, [task.id, form]);

  return <TaskForm form={form} />;
}
```

**Correct (React DOM) — identity from the data:**

```tsx
type Props = {
  tasks: Task[];
  query: string;
};

export function TaskList({ tasks, query }: Props) {
  const visible = tasks.filter((t) => t.title.includes(query));

  return (
    <ul>
      {visible.map((t) => (
        <TaskRow key={t.id} task={t} />
      ))}
    </ul>
  );
}
```

**Correct (React Native) — the same identity, declared through `keyExtractor`:**

```tsx
type Props = {
  tasks: Task[];
  query: string;
};

export function TaskList({ tasks, query }: Props) {
  const visible = tasks.filter((t) => t.title.includes(query));

  return (
    <FlatList
      data={visible}
      // Good: identity from the data. With the index here, recycling hands a
      // row's open swipe state to whichever task slid into that position
      keyExtractor={(t) => t.id}
      renderItem={({ item }) => <TaskRow task={item} />}
    />
  );
}
```

```tsx
type Props = {
  tasks: Task[];
  query: string;
};

export function TaskPanel({ tasks, query }: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selected = tasks.find((t) => t.id === selectedId) ?? null;

  return (
    <>
      <TaskList tasks={tasks} query={query} onSelect={setSelectedId} />
      {/* Good: a new identity remounts the editor, so no effect has to reset it */}
      {selected ? <TaskEditor key={selected.id} task={selected} /> : null}
    </>
  );
}
```

```tsx
type Props = { task: Task };

function TaskEditor({ task }: Props) {
  // Good: defaultValues are read once at mount, and mounting is what the key controls
  const form = useForm<FormValues>({
    defaultValues: { title: task.title },
  });

  return <TaskForm form={form} />;
}
```

Reference: [Why does React need keys?](https://react.dev/learn/rendering-lists#why-does-react-need-keys)

---

## 2. Component Architecture

### 2.1 Folder Structure & Layer Boundary

**Impact (HIGH):** Where a file lives is the cheapest documentation a codebase has, and the first thing that decays. Once a query hook lands next to a component and a domain type is declared inside a route, nobody can tell what depends on what, and the answer to "can I reuse this?" becomes "read it and find out". A declared structure also makes review possible: a misplaced file is a finding anyone can point at, while "this feels disorganized" is not.

The renderer changes none of this. A screen is a route module on both platforms, `core/` means the same thing on both, and the direction imports flow is a property of the architecture rather than of the _DOM_.

**Guidelines:**

1.  **Three folders, imports in one direction:**
    - `core/` holds everything that is not the view: data access, configured libraries, domain types, pure helpers
    - `shared/` sits beside it, at the same level, and holds what no domain owns at all
    - The view layer — routes and components — imports from `core/`; `core/` never imports from the view
    - Both of them import from `shared/`, and `shared/` imports from neither: the moment something there reaches into `core/` it has picked a domain and stopped being shared
    - A file under `core/` that imports a component is a boundary violation, and usually means presentation leaked into logic
2.  **What lives under `core/` and `shared/`:**
    - `core/api/<domain>/` — one file per query or mutation hook (see the query-layer rule)
    - `core/hooks/` — hooks the project writes, with the `zustand` stores under `core/hooks/stores/`
    - `core/lib/` — third-party libraries that need initialization or configuration, and the adapters over them, once more than one module depends on that setup
    - `core/types/<domain>/` — domain types, one folder per domain with an `index.ts` barrel (see the type-system rule)
    - `core/typings/` — augmentations for third-party libraries, which are not ours and do not belong beside the domains
    - `core/config/` — the constants the project agrees on, and nothing that has to be computed (see the core-utilities rule)
    - `core/helpers/` — own pure functions, with no third-party dependency
    - `shared/types/` — the shapes no domain owns: the API's response envelope, pagination, generic utilities. `core/types/` segments by domain, so filing these under `core/types/shared/` invents a domain called "shared" — which is the thing this folder exists to avoid
    - The line between `lib/` and `helpers/`: `lib/` wraps something external, `helpers/` depends on nothing
3.  **A module under `core/lib/` earns its place with a second consumer:**
    - The folder is where a third-party library is initialized, not where every third-party library gets a file of its own — when a single hook is the only place the package is ever touched, a module that sets a global and re-exports it is a boundary around a boundary
    - Until there is a second consumer — or an initialization that has to be guaranteed before either of two modules runs — the side effects live at the top of the one module that owns the library: the access token, the stylesheet, the locale
    - A re-export that transforms nothing is the tell. A line that only forwards what it imported states a boundary the import path already stated, and everything the file adds is indirection
    - Adapters are the exception and earn the file at one consumer: a module that narrows the package's surface, renames it into the project's vocabulary, or holds configuration the library reads at call time is holding something of ours. `core/lib/axios.ts` with its interceptors is that; a re-export is not
    - The move is cheap, and that is the argument: the day a second module reaches for the package, the initialization goes to `core/lib/` and both import it. One commit, paid when the need is real instead of guessed
    - None of this licenses the opposite defect. The initialization still leaves the view layer: a route that imports a library's setup on behalf of a hook three levels below it is the finding, and moving that import into the hook fixes it without a new module
4.  **Files are named in kebab case, whatever they export:**
    - `invoice-table.tsx` for a component, `use-invoices.ts` for a hook, `format.ts` for helpers — the casing never follows the export, so `InvoiceTable.tsx` is a finding even though the component inside it is `InvoiceTable`
    - One convention across the tree is what makes a path predictable before opening it
    - Hooks under `core/api/` carry their own shape on top of this — `use-<members|action>.ts` (see the query-layer rule)
    - Names stay singular for components and plural for domains, and a filename never repeats its folder (see the component-structure rule)
5.  **The root varies, the shape does not:**
    - Where `core/` sits depends on the technology and the layout it dictates — beside the router's directory on one platform, inside it on another
    - What must not vary between projects is what goes inside `core/` and which direction imports flow
    - The `~` alias resolves to that root, so every import reads the same regardless of which root it is. The prefix is the one part a platform may configure; everything after it does not move
6.  **Route modules compose, they do not fetch:**
    - A route module reads data through hooks and arranges components — that is its whole job
    - A route that declares a fetcher, or a component that reaches for `axios`, is in the wrong layer
    - What the router calls that module, and what the view renders to, is the platform's business and not this rule's — the view-structure rule on the web, the app-directory rule under _Expo_

**Incorrect (layers mixed, types inline, data access inside the view):**

```plaintext
app/
├─ components/
│  ├─ invoice-table.tsx
│  ├─ use-invoices.ts        ← data access in the view layer
│  └─ invoice.ts             ← domain type next to a component
├─ routes/
│  └─ invoices.tsx           ← declares its own axios call
└─ utils.ts                  ← configured client and pure helpers in one file
```

```tsx
// Bad: the route builds its own request, so nothing else can reuse it
import axios from 'axios';

type Invoice = {
  id: string;
  total: number;
};

export default function InvoicesRoute() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  // ...
}
```

**Correct (core owns logic and data, the view composes it):**

```plaintext
app/
├─ core/
│  ├─ api/
│  │  └─ invoices/
│  │     ├─ use-invoices.ts
│  │     └─ use-mark-paid.ts
│  ├─ hooks/
│  │  └─ stores/
│  │     └─ settings.ts
│  ├─ lib/
│  │  ├─ axios.ts
│  │  ├─ utils.ts                  ← cn(), the tailwind-merge adapter
│  │  └─ react-query/
│  │     ├─ client.ts
│  │     └─ middlewares.ts
│  ├─ types/
│  │  └─ invoices/                 ← one folder per domain, reached through its barrel
│  │     ├─ index.ts
│  │     └─ invoice.ts
│  ├─ typings/
│  │  └─ axios.d.ts
│  ├─ config/
│  │  └─ constants.ts
│  └─ helpers/
│     └─ format.ts
├─ shared/
│  └─ types/
│     └─ api.ts                    ← the response envelope, owned by no domain
└─ components/
   └─ invoice-table.tsx
```

Everything above is identical on both platforms. What differs is only where the router's own directory sits and what a route module is called, which each platform's own folder-structure rule states.

**Correct (React DOM):**

```tsx
// ./app/routes/invoices.tsx

import { useInvoices } from '~/core/api/invoices/use-invoices';
import { InvoiceTable } from '~/components/invoice-table';

// Good: the route reads through the hook and arranges components — nothing else
export default function InvoicesRoute() {
  const invoices = useInvoices({ variables: { status: 'open' } });

  return <InvoiceTable invoices={invoices.data} />;
}
```

**Correct (React Native):**

```tsx
// ./app/(tabs)/invoices.tsx

import { useInvoices } from '~/core/api/invoices/use-invoices';
import { InvoiceTable } from '~/components/invoice-table';

// Good: same job, same import paths — only the router's directory differs
export default function InvoicesScreen() {
  const invoices = useInvoices({ variables: { status: 'open' } });

  return <InvoiceTable invoices={invoices.data} />;
}
```

**Incorrect (a `core/lib/` module with a single consumer, re-exporting what it received):**

```ts
// ./app/core/lib/chart.ts

import { LicenseManager } from 'chart-vendor-enterprise';

LicenseManager.setLicenseKey(CHART_KEY);

// Bad: nothing here is ours, and the only importer already owns the boundary
export { Chart } from 'chart-vendor';
```

**Correct (the initialization sits with the one module that owns the library):**

```tsx
// ./app/components/invoice-chart.tsx — the only file that touches the vendor

import { LicenseManager } from 'chart-vendor-enterprise';
import { Chart } from 'chart-vendor';

// Good: read once at module evaluation, before the chart can mount
LicenseManager.setLicenseKey(CHART_KEY);

type Props = { invoices: Invoice[] };

export function InvoiceChart({ invoices }: Props) {
  return <Chart data={invoices} />;
}
```

Reference: [Thinking in React](https://react.dev/learn/thinking-in-react)

### 2.2 Minimal Markup Depth

**Impact (HIGH):** Utility classes make it cheap to add a wrapper, so wrappers accumulate. Each one is another node to render, another indentation level to read, and another place where a future style can be attached at the wrong depth. Most of them are removable: their classes belong on the element they wrap.

The element changes with the renderer and the defect does not. A chain of `div`s that each add one class is the same chain of `View`s, costs the same extra nodes, and is removed the same way.

**Guidelines:**

1.  **A wrapper needs a job:**
    - Justified when it creates a layout context (a `flex` parent), a positioning context (`relative`), an overflow clip, or a stacking context
    - Not justified when its classes could sit on the child
2.  **Fragments over structural noise:**
    - Use `<>` when a wrapper exists only to satisfy a single-root requirement
3.  **Spacing comes from the parent:**
    - `gap-4` on the container, not a wrapper per child carrying `mb-4`. On the web `space-y-4` is the other spelling of the same idea
    - Margins per child leak into every context where the child is reused: the child decides its own spacing, so a second call site inherits a decision it never made
4.  **Margins flow in one direction:**
    - When a margin is unavoidable, it goes on the element **above** as `mb-*`, never on the element below as `mt-*`
    - One direction is what stops two elements from both claiming the same gap — `mb-4` above and `mt-4` below is eight units of space nobody asked for
    - The web has a second reason on top of that: adjacent vertical margins collapse, and which of the two survives is a rule nobody recalls under pressure. Under _React Native_ they simply add, which makes the defect more predictable and no less wrong
    - The exception is markup whose preceding sibling you do not control, which in practice only happens on the web — rich text from a _CMS_, where a heading has to reserve its own space above
5.  **Centering is one element:**
    - `items-center justify-center` on a single flex parent, or `mx-auto` on the child — not three nested containers, each contributing one axis
6.  **Passthrough wrappers are removable:**
    - A wrapper whose only class is `w-full` around a block element, or whose only class is `flex-1`, almost always belongs on the child instead

**Incorrect (five levels of wrappers, per-child margins, nested centering):**

```tsx
export function EmptyState() {
  return (
    // Bad: wrapper chain, each level adding one class
    <div className="w-full">
      <div className="flex">
        <div className="mx-auto">
          <div className="flex flex-col items-center">
            <div className="mb-2">
              <h2 className="text-lg font-semibold">No reports yet</h2>
            </div>
            <div className="mb-4">
              <p className="text-sm text-muted-foreground">
                Create one to get started.
              </p>
            </div>
            <div>
              <Button>New report</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

**Correct (React DOM) — one layout container, gap for spacing, classes on the elements themselves:**

```tsx
export function EmptyState() {
  return (
    <div className="flex flex-col items-center gap-2">
      <h2 className="text-lg font-semibold">No reports yet</h2>
      {/* Good: the extra space before the button belongs to the element above it */}
      <p className="mb-2 text-sm text-muted-foreground">
        Create one to get started.
      </p>
      <Button>New report</Button>
    </div>
  );
}
```

**Correct (React Native) — the same single container, the same one-directional margin:**

```tsx
export function EmptyState() {
  return (
    <View className="items-center gap-2">
      <Text className="text-lg font-semibold">No reports yet</Text>
      {/* Good: same convention, and here the two margins would have added up
          rather than collapsed — the wrong version is simply eight units */}
      <Text className="mb-2 text-sm text-muted-foreground">
        Create one to get started.
      </Text>
      <Button>New report</Button>
    </View>
  );
}
```

Reference: [Styling with utility classes](https://tailwindcss.com/docs/styling-with-utilities)

### 2.3 Component File Structure

**Impact (HIGH):** The folder-structure rule decides where a component lives in the project; this one decides what happens inside its own folder. Left undecided, the same component arrives in three different shapes across a codebase — a four-hundred-line file that should have been split, a folder of six siblings with no entry point, and a variant matrix expressed as a chain of conditionals — and every reader has to open the folder to find out which one they got. The shape is also what makes a diff reviewable: a new file under `presets/` is a new variant, and that is legible before reading a line of it.

**Guidelines:**

1.  **Three shapes, chosen by what the component contains:**
    - **Integral** — one file, `components/invoice-badge.tsx`, when there are no sub-components
    - **Grouped** — a folder where every component has its own file, and an `index.ts` barrel states which of them are public
    - **Base and presets** — a folder that splits the logic container from its visual implementations, for a component whose variants differ in structure
2.  **A folder earns its barrel when a second file appears:**
    - Promote from integral to grouped the moment a sub-component is extracted, not in anticipation of one
    - The barrel is `index.ts` and never `index.tsx`: it re-exports and does nothing else, so it holds no JSX and there is no component to find inside it
    - No file is "the main one". Every component gets its own file named for what it is — `list.tsx`, `item.tsx` — and the barrel is what says which of them the rest of the codebase may reach
3.  **Names stay singular, and never repeat the folder:**
    - The entity in a component's name is singular whatever the component renders — `InvoiceList`, `InvoiceTable`, `InvoiceRow`, `InvoiceCard`. The suffix already carries the plurality, so `InvoicesList` states it twice
    - Singular is what keeps a family consistent: with a plural prefix the name changes shape depending on the suffix — `InvoicesList` beside `InvoiceRow` — and there is no convention left, only a decision to make per component
    - Domain folders are the opposite and stay plural: `core/api/invoices/` holds everything about the domain rather than one invoice (see the `folder-structure` rule)
    - A filename never repeats its folder: `invoice-list/item.tsx`, never `invoice-list/invoice-list-item.tsx`; `button/presets/text.tsx`, never `button/presets/button-text.tsx`
    - The path already states the parent, so repeating it turns every rename of the component into a rename of every file beneath it
    - Only the filename drops the prefix. The exported component keeps its full name — `presets/text.tsx` exports `ButtonText`, because that name is read at a call site where no folder is in view
4.  **Base and presets is for structural variation, never for styling:**
    - When the variants differ only in which classes they carry, they are one component with a `cva` matrix (see the extraction-threshold rule); splitting those into presets multiplies files to express what one variant prop already expresses
    - The pattern earns its place when the variants render **different children** — a confirm dialog and a form dialog share open state, focus handling and the overlay, and share nothing about what sits inside them
    - `base/` holds the logic container and hands down what it owns through a `render` prop, which is exactly the case the composition rule reserves render props for
5.  **The barrels decide what is reachable:**
    - The folder's `index.ts` exports only what the rest of the codebase may import — `InvoiceList` and not `InvoiceItem`, even though both live in the folder
    - A piece that only its siblings ever render is not re-exported. The day another module needs it, that is a deliberate line added to the barrel rather than an import that happened to resolve
    - `base/index.ts` and `presets/index.ts` follow the same rule one level down
    - A preset reaches `base/` through that barrel and by absolute path — `~/components/button/base`, never `../base`. The relative form states a hop instead of a destination: it hides which component the import belongs to, it reads the same from every folder at that depth, and it breaks the day the folder moves
    - Inside one folder, a sibling is still `./list` — there is no boundary to cross and no ambiguity to resolve
    - A preset that imports another preset is a signal the shared part belongs in `base/`

**Incorrect (a flag per screen inside one file, and a folder whose files repeat its name):**

```tsx
// ./app/components/dialog.tsx

// Bad: three unrelated bodies in one component, selected by a flag, with a prop
// per screen that only half the flags ever read
type Props = {
  kind: 'confirm' | 'form' | 'alert';
  title: string;
  description?: string;
  onConfirm?: () => void;
  fields?: FieldConfig[];
  onSubmit?: (values: FormValues) => void;
};

export function Dialog({ kind, title, description, onConfirm, fields }: Props) {
  return (
    <DialogShell title={title}>
      {kind === 'confirm' ? (
        <ConfirmBody description={description} onConfirm={onConfirm} />
      ) : null}
      {kind === 'form' ? <FormBody fields={fields} /> : null}
      {kind === 'alert' ? <AlertBody description={description} /> : null}
    </DialogShell>
  );
}
```

```plaintext
./app/components/invoice-list/
├── invoice-list.tsx        ← the folder already said "invoice-list"
├── invoice-list-item.tsx   ← and said it again
└── (no barrel, so every importer reaches straight into the files and
    nothing marks which of them was meant to be internal)
```

**Correct (grouped folder, files named for what they are, barrel naming what is public):**

```plaintext
./app/components/invoice-list/
├── index.ts    ← barrel: exports `InvoiceList` and nothing else
├── list.tsx    ← exports `InvoiceList`
└── item.tsx    ← exports `InvoiceItem`, rendered only by its sibling
```

```ts
// ./app/components/invoice-list/index.ts

// Good: the row is not here, so no route can import it by accident
export { InvoiceList } from './list';
```

The folder shapes above are the same on both platforms — a folder is a folder — so only the code below splits.

**Correct (base and presets, because the variants render different children):**

```plaintext
./app/components/dialog/
├── base/
│   ├── container.tsx   ← open state, focus, overlay — exports `DialogContainer`
│   └── index.ts
├── presets/
│   ├── confirm.tsx     ← exports `ConfirmDialog`
│   ├── form.tsx        ← exports `FormDialog`
│   └── index.ts
└── index.ts            ← what the rest of the codebase may import
```

**Correct (React DOM):**

```tsx
// ./app/components/dialog/base/container.tsx

type Props = {
  title: string;
  trigger: React.ReactNode;
  // Good: the preset needs state this container owns, which is what justifies a
  // render prop instead of children (see the composition rule)
  render: (close: () => void) => React.ReactNode;
};

export function DialogContainer({ title, trigger, render }: Props) {
  const [isOpen, setOpen] = useState(false);

  return (
    <Dialog open={isOpen} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        {render(() => setOpen(false))}
      </DialogContent>
    </Dialog>
  );
}
```

```tsx
// ./app/components/dialog/presets/confirm.tsx

import { DialogContainer } from '~/components/dialog/base';

type Props = {
  title: string;
  description: string;
  trigger: React.ReactNode;
  onConfirm: () => void;
};

// Good: the preset owns presentation only — every shared behavior is in the base
export function ConfirmDialog({
  title,
  description,
  trigger,
  onConfirm,
}: Props) {
  return (
    <DialogContainer
      title={title}
      trigger={trigger}
      render={(close) => (
        <>
          <p className="text-sm text-muted-foreground">{description}</p>
          <DialogFooter>
            <Button type="button" variant="ghost" onClick={close}>
              Cancel
            </Button>
            <Button type="button" variant="danger" onClick={onConfirm}>
              Delete
            </Button>
          </DialogFooter>
        </>
      )}
    />
  );
}
```

**Correct (React Native) — the pattern is at its most useful here, where a pressable has to resolve its own colour and press state before any preset can paint with them:**

```tsx
// ./app/components/button/base/container.tsx

import colors from '~/core/config/theme/colors';

type Props = {
  tone?: keyof typeof colors;
  // Good: the presets need what this container resolved — the same render-prop
  // justification, one level down
  render: (color: string) => React.ReactNode;
};

export function ButtonContainer({ tone = 'primary', render, ...rest }: Props) {
  const color = colors[tone][500];

  return (
    <Pressable className="rounded-xl" {...rest}>
      {render(color)}
    </Pressable>
  );
}
```

```tsx
// ./app/components/button/presets/text.tsx

import { ButtonContainer } from '~/components/button/base';

export function ButtonText({ children, ...rest }: Props) {
  // Good: the preset is presentation only, and its filename does not repeat
  // the folder that already said "button"
  return (
    <ButtonContainer
      {...rest}
      render={(color) => <Text style={{ color }}>{children}</Text>}
    />
  );
}
```

```tsx
// Bad (both platforms): presets for something the variant matrix already
// covers — these three differ by class alone, so they belong in one component
// with a cva axis
./app/components/badge/presets/success.tsx
./app/components/badge/presets/warning.tsx
./app/components/badge/presets/danger.tsx
```

Reference: [Importing and exporting components](https://react.dev/learn/importing-and-exporting-components)

### 2.4 Composition Over Configuration

**Impact (HIGH):** A component configured by flags grows one prop per request until its signature encodes every screen that ever used it, and its body becomes a chain of conditionals nobody can change safely. Composition moves that variation to the call site, where it is visible in the markup, and leaves the component with a single job. The test is simple: if adding a screen means adding a prop, the component is configured rather than composed.

**Guidelines:**

1.  **Slots over flags:**
    - `children` and named slot props (`header`, `actions`, `footer`) instead of booleans that toggle internal markup
2.  **Mutually exclusive booleans are not independent props:**
    - Two flags that are never true together are one discriminated union, or two components
3.  **Compound components express structure:**
    - `Card` / `CardHeader` / `CardBody` lets the caller assemble what this screen needs without the parent configuring it
4.  **Render props only for internal state:**
    - A `renderX` function is justified when the child needs state the parent holds; otherwise `children` already works
5.  **Passthrough props signal a broken boundary:**
    - Props that exist only to travel deeper mean you should be passing the element, not its data

**Incorrect (a flag per screen, conditionals stacking inside):**

```tsx
type Props = {
  title: string;
  showHeader?: boolean;
  showFooter?: boolean;
  isCompact?: boolean;
  hasBorder?: boolean;
  headerAction?: ReactNode;
  renderFooter?: () => ReactNode;
  footerAlign?: 'left' | 'right';
};

export function Card(props: Props) {
  return (
    <div
      className={cn(
        'rounded-lg',
        props.hasBorder && 'border',
        props.isCompact ? 'p-2' : 'p-4',
      )}
    >
      {props.showHeader && (
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">{props.title}</h3>
          {props.headerAction}
        </div>
      )}
      {props.children}
      {props.showFooter && (
        <div
          className={props.footerAlign === 'right' ? 'text-right' : 'text-left'}
        >
          {props.renderFooter?.()}
        </div>
      )}
    </div>
  );
}
```

**Correct (React DOM) — structure assembled at the call site, one job per component:**

```tsx
// Several components in one module, so each type is qualified by its own name
type CardProps = React.ComponentProps<'div'>;

export function Card({ className, ...props }: CardProps) {
  return <div className={cn('rounded-lg border p-4', className)} {...props} />;
}

type CardHeaderProps = React.ComponentProps<'div'>;

export function CardHeader({ className, ...props }: CardHeaderProps) {
  return (
    <div
      className={cn('mb-3 flex items-center justify-between', className)}
      {...props}
    />
  );
}

type CardBodyProps = React.ComponentProps<'div'>;

export function CardBody({ className, ...props }: CardBodyProps) {
  return (
    <div
      className={cn('text-sm text-muted-foreground', className)}
      {...props}
    />
  );
}
```

```tsx
// The screen composes exactly what it needs — no prop was added to support it
<Card className="p-2">
  <CardHeader>
    <h3 className="font-semibold">Q3 summary</h3>
    <Button variant="ghost">Export</Button>
  </CardHeader>
  <CardBody>
    <p>Revenue grew 12% quarter over quarter.</p>
  </CardBody>
</Card>
```

**Correct (React Native) — the same compound set over the platform's primitives:**

```tsx
type CardProps = React.ComponentProps<typeof View>;

export function Card({ className, ...props }: CardProps) {
  return <View className={cn('rounded-lg border p-4', className)} {...props} />;
}

type CardHeaderProps = React.ComponentProps<typeof View>;

export function CardHeader({ className, ...props }: CardHeaderProps) {
  return (
    <View
      className={cn('mb-3 flex-row items-center justify-between', className)}
      {...props}
    />
  );
}

type CardBodyProps = React.ComponentProps<typeof View>;

export function CardBody({ className, ...props }: CardBodyProps) {
  return <View className={cn('gap-1', className)} {...props} />;
}
```

```tsx
<Card className="p-2">
  <CardHeader>
    <Text className="font-semibold">Q3 summary</Text>
    <Button variant="ghost">Export</Button>
  </CardHeader>
  <CardBody>
    <Text>Revenue grew 12% quarter over quarter.</Text>
  </CardBody>
</Card>
```

Mutually exclusive props follow the same principle one level down, in the type: the union makes the invalid combination impossible to write rather than something the component has to defend against.

```tsx
// Three alternatives for the same Banner component, not three coexisting declarations

// Bad: three independent booleans describe eight states, five of which are meaningless
type Props = {
  isInfo?: boolean;
  isWarning?: boolean;
  isError?: boolean;
  message: string;
};

// Good: one axis, three valid states, nothing else type-checks
type Props = {
  tone: 'info' | 'warning' | 'error';
  message: string;
};

// Good: when a case carries data the others do not, discriminate on the same axis
type Props =
  | { tone: 'info' | 'warning'; message: string }
  | { tone: 'error'; message: string; onRetry: () => void };
```

Reference: [Passing JSX as children](https://react.dev/learn/passing-props-to-a-component#passing-jsx-as-children)

### 2.5 Component Extraction Threshold

**Impact (HIGH):** Utility CSS trades CSS duplication for markup duplication — that trade is only worth it if the markup is extracted at the right moment. Extract too early and the codebase fills with single-use wrappers that add indirection without removing anything. Extract too late and a design change means editing the same string in eleven files, missing two.

**Guidelines:**

1.  **The threshold:**
    - Extract on the third occurrence, or on the first occurrence that carries behavior or state
    - Two occurrences are cheaper to read inline than to look up
2.  **Extract decisions, not layout:**
    - A repeated string that encodes a decision — a variant, a size, a brand surface — is a component
    - A repeated `flex items-center gap-2` is not; it is generic layout and extracting it hides what the markup does
3.  **A loop is not duplication:**
    - Markup repeated inside `map()` or a template loop is already defined once — no extraction is needed
4.  **The component owns its defaults:**
    - Defaults live inside; callers pass `className` and it is merged **last** through `cn()`
    - A component that ignores `className` forces wrapper `div`s at every call site
5.  **Variants are an API, not a class string:**
    - Expose `variant="danger"` / `size="sm"`; do not let callers assemble the visual state from utilities
    - One axis of variation is fine as a lookup record; two or more declare the matrix with `cva` and derive the props from `VariantProps`, so the variants stay typed and live in one place
    - Name the constant in upper snake case — `STATUS_PILL_VARIANTS`, `BUTTON_VARIANTS`, `STATUS_STYLES` — because it is a module-level constant, not a component or a hook, and the casing keeps that distinction visible at the call site
    - Export it next to the component so another element can borrow the styling — `<a className={BUTTON_VARIANTS({ variant: 'ghost' })}>` styles a real link without wrapping it in a `button`
    - The moment a caller needs `bg-red-600!` to override, the variant was missing
6.  **Do not extract a passthrough:**
    - A component that forwards props and adds one static class is a wrapper — inline it (see minimal markup depth)

**Incorrect (extracted too early as a passthrough, and duplicated where it mattered):**

```tsx
// Bad: a component that adds one class and hides nothing
export const Row = ({ children }: PropsWithChildren) => (
  <div className="flex items-center gap-2">{children}</div>
);

// Bad: the real decision — the status pill — is duplicated verbatim at each call site
<span className="rounded-full bg-success px-2 py-0.5 text-xs font-medium text-success-foreground">
  Active
</span>
<span className="rounded-full bg-destructive px-2 py-0.5 text-xs font-medium text-destructive-foreground">
  Failed
</span>
<span className="rounded-full bg-warning px-2 py-0.5 text-xs font-medium text-warning-foreground">
  Pending
</span>
```

**Correct (React DOM) — generic layout stays inline, the decision becomes a component with a typed variant API:**

```tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '~/core/lib/utils';

export const STATUS_PILL_VARIANTS = cva(
  'inline-flex items-center rounded-full font-medium',
  {
    variants: {
      status: {
        active: 'bg-success text-success-foreground',
        failed: 'bg-destructive text-destructive-foreground',
        pending: 'bg-warning text-warning-foreground',
      },
      size: {
        sm: 'px-2 py-0.5 text-xs',
        md: 'px-3 py-1 text-sm',
      },
    },
    defaultVariants: { status: 'active', size: 'sm' },
  },
);

type Props = React.ComponentProps<'span'> &
  VariantProps<typeof STATUS_PILL_VARIANTS>;

export function StatusPill({ status, size, className, ...props }: Props) {
  return (
    <span
      className={cn(STATUS_PILL_VARIANTS({ status, size }), className)}
      {...props}
    />
  );
}
```

```tsx
// Generic layout stays inline — no Row component needed
<div className="flex items-center gap-2">
  <StatusPill status="active">Active</StatusPill>
  <StatusPill status="pending" className="ml-auto">
    Pending
  </StatusPill>
</div>
```

**Correct (React Native) — the same threshold, the same variant matrix:**

```tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '~/core/lib/utils';

export const STATUS_PILL_VARIANTS = cva('items-center rounded-full', {
  variants: {
    status: {
      active: 'bg-success',
      failed: 'bg-destructive',
      pending: 'bg-warning',
    },
    size: {
      sm: 'px-2 py-0.5',
      md: 'px-3 py-1',
    },
  },
  defaultVariants: { status: 'active', size: 'sm' },
});

type Props = React.ComponentProps<typeof View> &
  VariantProps<typeof STATUS_PILL_VARIANTS>;

export function StatusPill({ status, size, className, ...props }: Props) {
  return (
    <View
      className={cn(STATUS_PILL_VARIANTS({ status, size }), className)}
      {...props}
    />
  );
}
```

```tsx
// Generic layout stays inline here too — no Row component needed
<View className="flex-row items-center gap-2">
  <StatusPill status="active">
    <Text>Active</Text>
  </StatusPill>
  <StatusPill status="pending" className="ml-auto">
    <Text>Pending</Text>
  </StatusPill>
</View>
```

Reference: [Managing duplication](https://tailwindcss.com/docs/styling-with-utilities#managing-duplication)

### 2.6 Component Typing Conventions

**Impact (HIGH):** A component's props are its _API_. Hand-written prop types inevitably forget `id`, `onBlur`, or `data-*`, forcing every caller to patch around the component; independent optional booleans let the compiler accept combinations the component cannot render. Deriving the type from the element and modelling exclusivity turns those into compile errors instead of review comments.

**Guidelines:**

1.  **The props type is always declared, and it is always `Props`:**
    - Declare it even when it is a bare alias — `type Props = React.ComponentProps<'button'>` — so every component file has the same shape and the component's surface has one obvious place to look
    - Annotating props inline in the signature buries the surface inside the parameter list; a bespoke name (`ButtonProps`, `CardProps`) costs a lookup and carries no information the filename does not
    - Export it only when another module actually consumes it
    - When a module holds more than one component — a compound set like `Card` / `CardHeader` / `CardBody` — every type is qualified with its own component's name (`CardProps`, `CardHeaderProps`, `CardBodyProps`), so no two of them compete for the same name
    - Route components are the exception: the framework generates their props type — the params it parsed and whatever else it injects — so annotate with that generated type directly instead of aliasing it
2.  **Extend the underlying element or primitive:**
    - `React.ComponentProps<'button'>` on the web, `React.ComponentProps<typeof Pressable>` under _React Native_ — instead of redeclaring `onClick`/`onPress`, `disabled`, and `className` by hand
    - The utility is the same either way: whatever the component renders at its root is what its props extend, and `typeof` is what reaches a component rather than an intrinsic element
3.  **Model exclusivity, do not hope for it:**
    - Props that cannot coexist are a discriminated union, not three optional booleans
4.  **No `React.FC`:**
    - It adds nothing over typing the props parameter, and historically dragged an implicit `children` along
5.  **Derive from the source of truth:**
    - `VariantProps<typeof BUTTON_VARIANTS>` for variants, the `Data` type a query hook already declares for server data, `keyof typeof MAP` for lookup keys
    - A type that restates a value can drift from it; a type derived from it cannot
6.  **`any` and `!` are review flags in a signature:**
    - `unknown` plus a narrowing check is the honest version; a non-null assertion is a claim the compiler could not verify
7.  **Type the input, infer the output:**
    - Annotating the return adds noise and breaks the moment the component returns `null`

**Incorrect (hand-rolled surface, impossible states allowed, `any` in the handler):**

```tsx
// Bad: a bespoke name for the one thing every component file already has
type ButtonProps = {
  children: ReactNode;
  onClick: (e: any) => void;
  isPrimary?: boolean;
  isDanger?: boolean;
  isGhost?: boolean;
};

// Bad: React.FC, and callers cannot pass id, type, form, disabled or data-* at all
export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  isPrimary,
  isDanger,
}) => (
  <button
    onClick={onClick}
    className={cn(isPrimary && 'bg-primary', isDanger && 'bg-destructive')}
  >
    {children}
  </button>
);

// Compiles cleanly, renders something nobody designed
<Button isPrimary isDanger onClick={handleDelete}>
  Delete
</Button>;
```

**Correct (React DOM) — element props plus a single variant axis derived from the variants function:**

```tsx
type Props = React.ComponentProps<'button'> &
  VariantProps<typeof BUTTON_VARIANTS>;

export function Button({ variant, size, className, ...props }: Props) {
  return (
    <button
      className={cn(BUTTON_VARIANTS({ variant, size }), className)}
      {...props}
    />
  );
}

// Every native prop works, and the impossible combination no longer type-checks
<Button
  type="button"
  variant="danger"
  size="sm"
  form="invoice-form"
  onClick={handleDelete}
>
  Delete
</Button>;
```

**Correct (React Native) — the same shape, reaching the primitive with `typeof`:**

```tsx
type Props = React.ComponentProps<typeof Pressable> &
  VariantProps<typeof BUTTON_VARIANTS>;

export function Button({ variant, size, className, ...props }: Props) {
  return (
    <Pressable
      className={cn(BUTTON_VARIANTS({ variant, size }), className)}
      {...props}
    />
  );
}

// Good: onPress, disabled, testID and hitSlop all arrive without being declared
<Button
  variant="danger"
  size="sm"
  testID="delete-invoice"
  onPress={handleDelete}
>
  Delete
</Button>;
```

Reference: [TypeScript with React components](https://react.dev/learn/typescript#typescript-with-react-components)

### 2.7 TypeScript Type System & Domain Organization

**Impact (HIGH):** A structured type system prevents circular dependencies and naming collisions. Separating external library overrides (`typings`) from business logic definitions (`types`) ensures that the application's contract remains clear. Enforcing `import type` and `export type` aids the compiler in tree-shaking and type erasure.

**Guidelines:**

1.  **Directory Separation:**
    - `core/types/`: Contains application-specific definitions grouped by domain (e.g., `users`, `products`)
    - `core/typings/`: Contains global overrides and module augmentations for third-party libraries (e.g., `axios.d.ts`, `environment.d.ts`)
2.  **Definition Strategy:**
    - **Interfaces:** Must be used for defining the shape of objects, especially _API_ responses and external services (extensible)
    - **Types:** Must be used for unions, intersections, mapped types (`Pick`, `Omit`), and aliases
3.  **Domain Grouping:**
    - A domain is a folder, always — `core/types/products/` — however few files it holds. The folder is the boundary, and a boundary does not appear and disappear with a file count
    - Every domain folder carries an `index.ts` barrel exporting its members, so consumers import the domain and never a file inside it. That indirection is the point: splitting `product.ts` later changes nothing at any call site
    - The folder is named for the domain in plural; the files inside are named for the entities they hold
    - This is deliberately not the threshold a component folder uses, where a second file is what earns the folder (see the component-structure rule). A component folder groups files that happen to belong together; a domain folder declares a boundary that exists whether or not it has been filled yet
4.  **Import/Export Syntax:**
    - **Imports:** Must use `import type { ... }` when importing interfaces or types
    - **Exports:** Must use `export type { ... }` in barrel files (`index.ts`)
5.  **Naming Convention:**
    - Do not prefix interfaces with `I`
    - Files should be named after the entity (e.g., `user.ts`) or the group (e.g., `cart.ts`)

**Incorrect (Flat structure, loose typing, value imports for types):**

```typescript
// ./core/types.ts

// Bad: Global file, mixing library overrides with app logic
declare module 'axios' { ... }

export type User = { id: string };
```

```typescript
// ./features/profile.tsx

// Bad: Importing a type as a value
import { User } from '~/core/types/users';
```

**Correct (Separated, Structured, Explicit Type Imports):**

```plaintext
./core/
├── types/
│   ├── config/                ← a folder even with one member beside its barrel
│   │   ├── index.ts
│   │   └── item.ts
│   └── products/
│       ├── index.ts
│       ├── product.ts
│       └── variant.ts
└── typings/
    ├── axios.d.ts
    └── environment.d.ts
```

```typescript
// ./core/types/products/product.ts

export interface Product {
  id: string;
  name: string;
  price: number;
}
```

```typescript
// ./core/types/products/index.ts

// Explicit type export
export type { Product } from './product';
```

```typescript
// ./app/products.tsx

// Explicit type import, reaching the domain through its barrel rather than the
// file inside it
import type { Product } from '~/core/types/products';
```

Reference: [TypeScript Handbook — Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)

### 2.8 Core Utilities & Configuration

**Impact (MEDIUM):** Two small habits decide whether `core/` stays useful. A helper written as a class with `static` methods drags the whole class into every bundle that touches one of its methods, because a class is a single binding and nothing can tree-shake half of it. And a key written inline — `'@session/jwt/token'` at the call site — is a value with no definition: the day it changes, correctness depends on a find-and-replace catching every copy, and a typo produces a miss rather than an error.

**Guidelines:**

1.  **Helpers are exported functions:**
    - `export const login = (token: string) => …`, one binding per behavior
    - A `class` with only `static` methods is an object pretending to be a namespace. It cannot be tree-shaken, it cannot be partially imported, and it buys nothing over the module system that already provides both
    - Import the module when the group is what matters — `import * as SessionHelper from '~/core/helpers/session'` — which gives the namespace without the class
2.  **Constants are declared once, in `core/config/`:**
    - Storage keys, cache timings, and any string the code compares against belong there, grouped by what they configure
    - The test is whether a typo would be caught: `STORAGE.SESSION.TOKEN` fails to compile when misspelled, `'@session/jwt/token'` fails silently at runtime
    - This is not a rule about magic numbers in general. A `setTimeout(..., 300)` inside the one component that debounces is fine; the value that two modules must agree on is what needs a name
3.  **A constant is not a type:**
    - Where a value set is also a type, derive the type from the constant rather than declaring both — `keyof typeof STORAGE` (see the typing-conventions rule)
    - Two declarations of the same set drift, and the compiler cannot tell you which one was right

**Incorrect (a static-class namespace, and keys written wherever they are needed):**

```ts
// ./core/helpers/session.ts

// Bad: a class used as a namespace — importing `login` pulls in `logout`,
// `refresh` and everything else this class ever grows
export class SessionHelper {
  static login(token: string) {
    storage.set('@session/jwt/token', token);
  }

  static isLoggedIn(): boolean {
    return storage.contains('@session/jwt/token');
  }
}
```

```ts
// ./core/api/session/use-refresh.ts

// Bad: the same key, written again. Nothing connects these two literals, and a
// typo here logs every user out instead of failing the build
const token = storage.getString('@session/jwt/tokens');
```

**Correct (plain exported functions, keys declared once):**

```ts
// ./core/config/constants.ts

export const STORAGE = {
  SESSION: { JSON_WEB_TOKEN: '@session/jwt/token' },
};

export const QUERY = {
  TIME: {
    NONE: 0,
    MEDIUM: 300_000,
  },
};
```

```ts
// ./core/helpers/session.ts

import { STORAGE } from '~/core/config/constants';
import { storage } from '~/core/lib/storage';

// Good: one binding per behavior, so a consumer takes only what it imports
export const login = (token: string) => {
  storage.set(STORAGE.SESSION.JSON_WEB_TOKEN, token);
};

export const isLoggedIn = (): boolean => {
  return storage.contains(STORAGE.SESSION.JSON_WEB_TOKEN);
};
```

```ts
// ./core/api/session/use-refresh.ts

// Good: the namespace without the class, and the key has exactly one definition
import * as SessionHelper from '~/core/helpers/session';
import { STORAGE } from '~/core/config/constants';

const token = storage.getString(STORAGE.SESSION.JSON_WEB_TOKEN);
```

Reference: [Tree shaking](https://developer.mozilla.org/en-US/docs/Glossary/Tree_shaking)

### 2.9 Syntax & Conciseness Conventions

**Impact (LOW):** Improves conciseness and reduces visual noise in high-frequency patterns, while enforcing explicit control flow in conditionals to prevent logic bugs and rendering accidents.

These conventions maximize the information density of the code, so logic can be scanned without getting lost in boilerplate.

#### 1. Iterator Naming (Short-Hand Convention)

For inline array methods (`.map`, `.filter`, `.find`, `.forEach`), use the first letter of the collection's item name as the argument. This keeps the line short and puts the attention on the operation rather than on the binding.

**Exceptions:**

- **Block bodies:** when the callback body is a `{ … }` block, or it needs destructuring, use the full singular name — at that point the binding is read far from where it was bound
- **Nested iteration:** inside another iterator, use full names so the two bindings cannot be confused
- **The index keeps its name:** when the callback also takes the index it is always `index`, never `i` — the abbreviation belongs to the item

_JSX_ is not an exception: a multi-line element still takes the abbreviation, because the binding stays visible at the head of the same expression.

A virtualized list is not one either, but it is not this rule's business — `renderItem={({ item }) => …}` destructures a parameter the library names, so there is no binding of ours to abbreviate.

**Incorrect (verbose for simple logic):**

```tsx
const reportIds = reports.map((report) => report.id);

const openInvoices = invoices.filter((invoice) => invoice.isOpen);
```

**Correct (concise, with the exception spelled out):**

```tsx
const reportIds = reports.map((r) => r.id);

const openInvoices = invoices.filter((i) => i.isOpen);

// Exception: a block body warrants the descriptive name
const enriched = invoices.map((invoice) => {
  const isOverdue = checkOverdue(invoice);
  return { ...invoice, isOverdue };
});
```

**Correct (React DOM) — JSX keeps the abbreviation, and the index keeps its name:**

```tsx
{
  invoices.map((i) => (
    <tr key={i.id}>
      <td>{i.number}</td>
      <td>{i.total}</td>
    </tr>
  ));
}

{
  steps.map((s, index) => (
    <li key={s.id}>
      {index + 1}. {s.label}
    </li>
  ));
}
```

**Correct (React Native) — the same, plus the one case the rule does not reach:**

```tsx
{
  invoices.map((i) => (
    <View key={i.id} className="flex-row justify-between">
      <Text>{i.number}</Text>
      <Text>{i.total}</Text>
    </View>
  ));
}
```

```tsx
// Good: nothing here is ours to name. `item` is the parameter FlatList hands
// down, so the abbreviation convention has nothing to apply to — and renaming
// it on destructure would be noise, not concision
<FlatList
  data={invoices}
  keyExtractor={(i) => i.id}
  renderItem={({ item }) => <InvoiceRow invoice={item} />}
/>
```

#### 2. Type and Object Literals

A _TypeScript_ type (not an interface) or an object literal with exactly one property is written on a single line. With more than one, each property takes its own line. One property reads as a single fact; several read as a list, and a list crammed onto one line has to be parsed instead of skimmed.

`prettier` does not decide this for you — it keeps whatever already fits inside the print width — so it only ever surfaces in review.

**Incorrect (one property spread over three lines, and two lists pretending to be one fact):**

```tsx
type Props = {
  invoice: Invoice;
};

type FormValues = { email: string; phone: string; plan: 'basic' | 'pro' };

const form = useForm<FormValues>({
  defaultValues: { email: '', phone: '', plan: 'basic' },
});
```

**Correct (one property inline, several one per line):**

```tsx
type Props = { invoice: Invoice };

type FormValues = {
  email: string;
  phone: string;
  plan: 'basic' | 'pro';
};

const form = useForm<FormValues>({
  defaultValues: {
    email: '',
    phone: '',
    plan: 'basic',
  },
});
```

#### 3. Event Handler Naming

Handler implementations use the `handle` prefix; event props keep the `on` prefix both platforms already use. The distinction makes it immediately clear which side of the boundary a function is on — `onClick` and `onPress` are what the component accepts, `handleClick` and `handlePress` are what this component does. Using `on` for both leaves the reader guessing.

The prop names differ by platform and the convention does not: whatever the event is called, the implementation passed to it is `handle` plus that name.

The convention decides the name, not that a name is needed. A body that is one expression stays inline at the prop — a state setter, a call to a function that already reads well, firing a mutation. `onPress={() => setMenuOpen(true)}` says everything a `handleOpenMenu` would say, and says it where it happens; the extracted version costs a declaration above, a jump back up to read it, and a name that only restates its single line.

Extract the moment the body earns it: a second statement, arguments of its own to prepare, or the same implementation passed to more than one prop. Below that threshold a named handler is indirection wearing the costume of a convention.

Performance is not part of this decision. An inline arrow is precisely what the compiler memoizes (see the render-stability rule), so extracting one to stabilize its identity solves a problem that no longer exists.

**Incorrect (implementation named like a prop):**

```tsx
export function InvoiceRow({ invoice }: Props) {
  // Bad: named after the prop it will be passed to, not after what it does
  const onDownload = async () => {
    const file = await buildInvoicePdf(invoice);
    save(file, `${invoice.number}.pdf`);
  };

  return <Button onClick={onDownload}>Download</Button>;
}
```

**Correct (React DOM):**

```tsx
export function InvoiceRow({ invoice }: Props) {
  // Good: the body does several things, so it earns both a declaration and a name
  const handleDownload = async () => {
    const file = await buildInvoicePdf(invoice);
    save(file, `${invoice.number}.pdf`);
  };

  return <Button onClick={handleDownload}>Download</Button>;
}
```

**Correct (React Native):**

```tsx
export function InvoiceRow({ invoice }: Props) {
  const handleDownload = async () => {
    const file = await buildInvoicePdf(invoice);
    await Share.share({ url: file.uri });
  };

  return (
    <>
      {/* Good: nothing to name — the setter is already the implementation */}
      <Input onChangeText={setNote} />
      <Button onPress={handleDownload}>Download</Button>
    </>
  );
}
```

**Incorrect (a named handler that only restates its one line):**

```tsx
export function InvoiceRow({ invoice }: Props) {
  // Bad: three declarations that add a name and nothing else
  const handleOpenMenu = () => {
    setMenuOpen(true);
  };

  const handleSelect = () => {
    onSelect(invoice.id);
  };

  const handleArchive = () => {
    archive.mutate(invoice.id);
  };

  return (
    <RowActions
      onOpenMenu={handleOpenMenu}
      onSelect={handleSelect}
      onArchive={handleArchive}
    />
  );
}
```

**Correct (one expression stays at the prop; the one that does more keeps its name):**

```tsx
export function InvoiceRow({ invoice }: Props) {
  // Good: the only body that earns a declaration is the one doing several things
  const handleDownload = async () => {
    const file = await buildInvoicePdf(invoice);
    save(file, `${invoice.number}.pdf`);
    toast.success('Invoice downloaded');
  };

  return (
    <RowActions
      onOpenMenu={() => setMenuOpen(true)}
      onSelect={() => onSelect(invoice.id)}
      onArchive={() => archive.mutate(invoice.id)}
      onDownload={handleDownload}
    />
  );
}
```

#### 4. Function Declarations

`function` declares what _React_ itself calls — a component or a hook — and nothing else. Every other function in the file, at any scope, is an arrow assigned to a `const`.

A hook built by a factory is the one shape that cannot follow this, and it does not have to: `createQuery`, `createMutation` and `zustand`'s `create` **return** the hook, so `const useInvoices = createQuery(…)` is an assignment by nature rather than a declaration that chose the wrong keyword (see the query-layer rule). A hook written by hand has no such excuse.

The scope is what makes the rest worth stating. Inside the body it is obvious; at module level it is where the convention leaks, because a helper written as `function formatAmount()` beside the component reads like a second component until you reach its body. A module holding a compound set is not an exception either — it has one `function` per component and nothing else (see the composition rule).

There is one exception, and it is a runtime requirement rather than a preference: **when hoisting is what makes the module load**, `function` is the only correct declaration. A query file names its fetcher inside the `createQuery` config and declares it below, so a `const` there is a `ReferenceError` in the temporal dead zone, not a style choice (see the query-layer rule). Reordering to avoid it would put the private detail above the exported hook, so the declaration is what gives way. What does not qualify is a helper that merely happens to sit below its caller inside a function body — nothing runs before that body does.

The arrow may be wrapped. `const handleSelect = useCallback(() => …, [])` satisfies this convention exactly as well as a bare arrow does, because the convention is about the binding and not about the arrow being unadorned. Whether a wrapper is needed at all is the render-stability rule's decision; this one only fixes the shape.

Three reasons this matters beyond taste: the file reads as one shape all the way down, nothing is hoisted above the values it closes over, and `function` becomes a reliable signal — where it appears, something _React_ will call is being declared.

**Incorrect (a module-level helper and two declarations inside the body):**

```tsx
function formatAmount(invoice: Invoice) {
  return `${invoice.currency} ${invoice.amount.toFixed(2)}`;
}

export function InvoiceRow({ invoice }: Props) {
  async function handleArchive() {
    await archiveInvoice(invoice.id);
    toast.success('Invoice archived');
  }

  return (
    <RowActions
      onDownload={() => downloadInvoice(invoice.id)}
      onArchive={handleArchive}
    />
  );
}
```

**Correct (one function, the component; everything else an arrow on a const):**

```tsx
const formatAmount = (invoice: Invoice) =>
  `${invoice.currency} ${invoice.amount.toFixed(2)}`;

export function InvoiceRow({ invoice }: Props) {
  const handleArchive = async () => {
    await archiveInvoice(invoice.id);
    toast.success('Invoice archived');
  };

  return (
    <RowActions
      onDownload={() => downloadInvoice(invoice.id)}
      onArchive={handleArchive}
    />
  );
}
```

```ts
// Good: a hook is a declaration too, and only its internals are arrows
export function useDebouncedValue(value: string, delay: number) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}
```

#### 5. Conditional Syntax

Every conditional uses braces and line breaks — including early returns and single-statement bodies. Omitting them is forbidden no matter how short the condition reads, because the next person to add a second statement is the one who pays for it.

For conditional rendering in _JSX_, always use a ternary with an explicit `null`. The `&&` shorthand is forbidden: when the left side is a number, `0` renders as the text "0" instead of nothing, and when it is an empty string the same happens.

**Incorrect (braceless conditions, `&&` shorthand):**

```tsx
// Bad: braceless early return
if (!invoice) return null;

// Bad: braceless single-statement body
if (invoices.isPending) return <Spinner />;

// Bad: renders the text "0" when the list is empty
{
  invoices.data.length && <InvoiceTable invoices={invoices.data} />;
}

// Bad: no explicit negative case
{
  isMenuOpen && <RowMenu />;
}
```

**Correct (braces, line breaks, ternary with null):**

```tsx
if (!invoice) {
  return null;
}

if (invoices.isPending) {
  return <Spinner />;
}

{
  invoices.data.length > 0 ? <InvoiceTable invoices={invoices.data} /> : null;
}

{
  isMenuOpen ? <RowMenu /> : null;
}
```

#### 6. Blank Lines Inside JSX

Sibling elements are not separated by blank lines. The tree already states its own structure through indentation and tags, so a blank line adds a second grouping signal that competes with the first — and it stretches a component across more screens than it needs.

This one is a convention rather than a formatting artifact: `prettier` preserves a single blank line wherever it finds one, so nothing enforces it automatically. It only ever surfaces in review.

**Incorrect (blank lines competing with the indentation):**

```tsx
export function AttachmentRow({ file }: Props) {
  return (
    <>
      <img src={file.previewUrl} className="w-full rounded-lg" />

      <section className="py-12">
        <p>{file.name}</p>

        <button type="button">Download</button>
      </section>
    </>
  );
}
```

**Correct (React DOM) — one continuous tree:**

```tsx
export function AttachmentRow({ file }: Props) {
  return (
    <>
      <img src={file.previewUrl} className="w-full rounded-lg" />
      <section className="py-12">
        <p>{file.name}</p>
        <button type="button">Download</button>
      </section>
    </>
  );
}
```

**Correct (React Native) — the elements change, the shape does not:**

```tsx
export function AttachmentRow({ file }: Props) {
  return (
    <>
      <Image source={{ uri: file.previewUrl }} className="w-full rounded-lg" />
      <View className="py-12">
        <Text>{file.name}</Text>
        <Button onPress={() => download(file)}>Download</Button>
      </View>
    </>
  );
}
```

Reference: [TypeScript Handbook - Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)

### 2.10 Class Composition & Conditional Classes

**Impact (CRITICAL):** _TailwindCSS_ scans source files as plain text — it never executes them. A class assembled at runtime (`bg-${color}-500`) does not exist at build time, so the CSS is never generated and the element ships unstyled. The failure is invisible in development with a cached stylesheet and shows up in production. Separately, string concatenation produces conflicting utilities whose winner is decided by stylesheet order, not by which class was written last: `"p-2" + " p-4"` is not reliably `p-4`.

**Guidelines:**

1.  **One composition helper:**
    - Compose with `cn()` — `clsx` for conditionals, `tailwind-merge` for conflict resolution
    - `tailwind-merge` makes "last one wins" true, which is what every caller assumes
    - Neither platform gives you that for free, and for the same reason. On the web the stylesheet settles a conflict, not the order the classes were written in. _NativeWind_ resolves `className` styles in CSS specificity order too — by design, to keep native and web identical — so `bg-slate-500 bg-red-500` does not reliably paint red there either
    - `cva` also exports `cx`: it is `clsx` renamed and it merges nothing, so importing it instead of `cn()` silently reintroduces the conflict this rule exists to prevent. `classnames` is the same trap under another name — it concatenates conditionally and resolves nothing
    - One helper per project. Where a generator writes it — `shadcn init` on the web, its _React Native_ equivalents — that file is the one, and a second declared beside it is duplication rather than a preference
    - `tailwind-merge` only knows the framework's own conflict groups, so anything the project adds is invisible to it and two conflicting ones both survive. Register them with `extendTailwindMerge` in that same file
2.  **Never build class names dynamically:**
    - No interpolation, no concatenation of fragments, no `` `text-${size}` ``
    - Map values to **complete** static class strings in a lookup object
3.  **Variant APIs:**
    - Declare the variant matrix once — a lookup record for a single axis, `cva` beyond that — never nested ternaries inside the attribute
    - This rule keeps the record form; the `cva` matrix is written out in the extraction-threshold rule and used again in the custom-layers one
    - Either way the result is wrapped in `cn()`, so a caller's `className` still wins; `cva` composes its own base and variant strings without merging them
    - A combination that needs classes of its own is `compoundVariants` — `{ variant: 'danger', size: 'sm', class: 'ring-1 ring-destructive' }` — because a crossing of two axes is exactly what sends people back to the nested ternary
4.  **Reusable components accept `className`:** - Take a `className` prop and merge it **last**, so callers can override defaults - A component that ignores `className` forces the next developer to wrap it in a `div`
    **Incorrect (interpolated class, template-literal concatenation, unmergeable override):**

```tsx
type Props = {
  tone: 'info' | 'danger';
  size: 'sm' | 'lg';
  className?: string;
};

export function Alert({ tone, size, className }: Props) {
  return (
    <div
      // Bad: these classes never exist at build time
      className={`rounded-md bg-${tone}-100 text-${tone}-800 p-${size === 'lg' ? 6 : 3} ${className}`}
    >
      ...
    </div>
  );
}

// The caller's p-8 may or may not win — it depends on stylesheet order
<Alert tone="info" size="lg" className="p-8" />;
```

**Correct (React DOM) — static maps, `cn()` merge, caller override wins:**

```ts
// ./app/core/lib/utils.ts — one per project, wherever the platform's generator
// puts it. Identical on both, which is why it is declared once here
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs));
```

```tsx
import { cn } from '~/core/lib/utils';

export const TONES = {
  info: 'bg-info text-info-foreground',
  danger: 'bg-destructive text-destructive-foreground',
} as const;

export const SIZES = {
  sm: 'p-3 text-sm',
  lg: 'p-6 text-base',
} as const;

type Props = React.ComponentProps<'div'> & {
  tone: keyof typeof TONES;
  size: keyof typeof SIZES;
};

export function Alert({ tone, size, className, ...props }: Props) {
  return (
    <div
      // Good: complete static strings, className merged last
      className={cn('rounded-md', TONES[tone], SIZES[size], className)}
      {...props}
    />
  );
}

// p-8 reliably wins: tailwind-merge drops the conflicting p-6
<Alert tone="info" size="lg" className="p-8" />;
```

**Correct (React Native) — the same helper, the same maps, the same merge:**

```tsx
import { cn } from '~/core/lib/utils';

export const TONES = {
  info: 'bg-info',
  danger: 'bg-destructive',
} as const;

export const SIZES = {
  sm: 'p-3',
  lg: 'p-6',
} as const;

type Props = React.ComponentProps<typeof View> & {
  tone: keyof typeof TONES;
  size: keyof typeof SIZES;
};

export function Alert({ tone, size, className, ...props }: Props) {
  return (
    <View
      // Good: complete static strings, className merged last. Without the merge
      // NativeWind settles p-6 against p-8 by specificity, not by who wrote last
      className={cn('rounded-md', TONES[tone], SIZES[size], className)}
      {...props}
    />
  );
}

<Alert tone="info" size="lg" className="p-8" />;
```

Reference: [tailwind-merge](https://github.com/dcastil/tailwind-merge) · [NativeWind style specificity](https://www.nativewind.dev/docs/core-concepts/style-specificity)

---

## 3. Data Flow

### 3.1 Query Layer & Data Ownership

**Impact (HIGH):** A component that fetches takes on a problem it cannot finish: caching, deduplication, cancellation, retry, and invalidation. Spread across components, each one solves a different subset, and the same endpoint ends up requested three times per screen under three different key strings. A typed query layer answers all of that once and leaves the component consuming state instead of orchestrating requests.

**Guidelines:**

1.  **One way to reach the network:**
    - Every request goes through `createQuery` / `createMutation` from `react-query-kit`; components never call `useQuery`, `useMutation`, or `axios` directly
2.  **Structure by domain, keys declared once:**
    - Hooks live under `core/api/<domain>/`, named `use-<members|action>.ts` (see the folder-structure rule)
    - Query keys follow `'@<domain>/<hook-name>'`, declared in the hook itself — a bare `['invoices']` written at a call site is how two components end up with two caches of the same data
    - Invalidate with the owning hook's `getKey()`, never a hand-written copy of the key
3.  **The client and the middlewares are configured once:**
    - The _Axios_ instance, the query client, and the mutation middlewares are configured library instances, so they live where the folder-structure rule puts them: `core/lib/`
    - Nothing outside that folder constructs one of these; the rest of the codebase imports the already-configured instance, so there is exactly one cache and one interceptor chain per process
4.  **Types at the boundary, in request order:**
    - Declare `Variables`, then `Response`, then `Data` — the order follows the request's own direction: what goes out, what comes back, what the _UI_ consumes
    - When the payload needs no transform, `Data` is an alias and says so: `type Data = Response`
    - When they diverge, the transform belongs in the fetcher, so every consumer sees the same shape
5.  **Let errors propagate:**
    - A `try`/`catch` in the fetcher that returns `[]` makes `isError` permanently false and the error branch unreachable — the screen then reports "no results" for what was actually a failure
6.  **Auth is not a component concern:**
    - Token injection and 401 handling live in the _Axios_ interceptors, declared once
    - Access control before render belongs to the protected layout route, driven by the session query and a declarative redirect
    - A `useEffect` that navigates is the wrong tool for both: it paints the protected screen first and redirects after
7.  **Parallel by default, dependent only when it is:**
    - Independent hooks called in the same component already run in parallel — nothing to arrange
    - Chaining with `enabled` makes the second request wait for the first, so use it only when the second genuinely needs the first's result
8.  **Paginated queries hold the previous page:**
    - When the page is part of the key, every page change is a fresh cache entry with no data, so the consumer's pending branch fires and the whole table blanks on each step
    - `placeholderData: keepPreviousData` in the hook definition serves the previous page while the next one resolves, which turns that blank into an `isPlaceholderData` dim (see the async-states rule)
9.  **Mutations invalidate through a middleware:**
    - Compose invalidation with `use` on `createMutation`, so it is declared beside the mutation instead of hand-written into every `onSuccess`
    - Pass the keys the mutation actually affects; a mutation that invalidates everything is a cache with extra steps
    - Calling a query's `refetch()` from a mutation, or writing the response into local state, forks the cache

**Incorrect (inline query, hand-written key, swallowed error, effect that redirects, needless waterfall):**

```tsx
// ./app/routes/invoices.tsx
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export default function InvoicesRoute() {
  const navigate = useNavigate();
  const session = useSessionStore((s) => s.session);

  // Bad: the protected screen paints, then navigates away
  useEffect(() => {
    if (!session) {
      navigate('/login');
    }
  }, [session, navigate]);

  // Bad: inline query, key written at the call site, error swallowed so isError never fires
  const { data } = useQuery({
    queryKey: ['invoices'],
    queryFn: async () => {
      try {
        return (await axios.get('/invoices')).data;
      } catch {
        return [];
      }
    },
  });

  // Bad: enabled turns two independent requests into a waterfall
  const { data: customers } = useQuery({
    queryKey: ['customers'],
    queryFn: fetchCustomers,
    enabled: Boolean(data),
  });

  return <InvoiceTable invoices={data} customers={customers} />;
}
```

**Correct (typed hook per domain, types in request order, key declared once):**

```ts
// ./app/core/api/invoices/use-invoices.ts

import { createQuery } from 'react-query-kit';
import { api } from '~/core/lib/axios';
import type { Invoice } from '~/core/types/invoices';

type Variables = { status: string };

type Response = Invoice[];

type Data = Response;

export const useInvoices = createQuery<Data, Variables>({
  queryKey: ['@invoices/use-invoices'],
  fetcher: request,
});

// Declared with function so it hoists: the config above names it before this line
async function request({ status }: Variables) {
  const { data } = await api.get<Response>('/invoices/', {
    params: { status },
    protected: true,
  });

  return data;
}
```

```ts
// ./app/core/typings/axios.d.ts

// Good: what makes `protected: true` a real option instead of an ignored extra.
// A library augmentation, so it lives in typings/ and not in types/ (see the
// type-system rule)
import 'axios';

declare module 'axios' {
  export interface AxiosRequestConfig {
    protected?: boolean;
  }
}
```

```ts
// ./app/shared/types/api.ts

// Good: no domain owns this shape, so it does not belong in core/types/
export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};
```

```ts
// ./app/core/api/invoices/use-invoice-page.ts

import { keepPreviousData } from '@tanstack/react-query';
import { createQuery } from 'react-query-kit';
import { api } from '~/core/lib/axios';
import type { Invoice } from '~/core/types/invoices';
import type { Paginated } from '~/shared/types/api';

type Variables = { page: number };

type Response = Paginated<Invoice>;

type Data = Response;

export const useInvoicePage = createQuery<Data, Variables>({
  queryKey: ['@invoices/use-invoice-page'],
  fetcher: request,
  // Good: the previous page stays on screen instead of blanking the table
  placeholderData: keepPreviousData,
});

// Declared with function so it hoists: the config above names it before this line
async function request({ page }: Variables) {
  const { data } = await api.get<Response>('/invoices/', {
    params: { page },
    protected: true,
  });

  return data;
}
```

```ts
// ./app/core/lib/react-query/middlewares.ts

export const withInvalidation = (...keys: QueryKey[]): MiddlewareFn => {
  return (useMutationNext) => {
    return (options) => {
      return useMutationNext({
        ...options,
        onSuccess: (_data, _variables, _onMutateResult, context) => {
          for (const key of keys) {
            context.client.invalidateQueries({ queryKey: key });
          }

          options.onSuccess?.(_data, _variables, _onMutateResult, context);
        },
      });
    };
  };
};
```

```ts
// ./app/core/api/invoices/use-mark-paid.ts

import { createMutation } from 'react-query-kit';
import { api } from '~/core/lib/axios';
import { withInvalidation } from '~/core/lib/react-query/middlewares';
import type { Invoice } from '~/core/types/invoices';
import { useInvoices } from './use-invoices';

type Variables = {
  id: string;
  reference: string;
};

type Response = Invoice;

type Data = Response;

export const useMarkPaid = createMutation<Data, Variables>({
  mutationFn: request,
  // Good: invalidation declared beside the mutation, with the key its owner exposes
  use: [withInvalidation(useInvoices.getKey())],
});

// Declared with function so it hoists: the config above names it before this line
async function request({ id, reference }: Variables) {
  const { data } = await api.patch<Response>(
    `/invoices/${id}/paid/`,
    { reference },
    { protected: true },
  );

  return data;
}
```

```tsx
// ./app/routes/invoices.tsx

export default function InvoicesRoute() {
  // Good: two independent hooks, so both requests start together
  const invoices = useInvoices({ variables: { status: 'open' } });
  const customers = useCustomers();

  return <InvoiceTable invoices={invoices.data} customers={customers.data} />;
}
```

The protected layout is the one place this rule reaches the router, so it is the one place the two platforms diverge. The shape is identical — read the session, hold the paint while it resolves, redirect from the render output — and only the elements change.

**Correct (React DOM):**

```tsx
// ./app/routes/protected-layout.tsx

export default function ProtectedLayout() {
  const session = useSession();

  if (session.isPending) {
    return <AppSkeleton />;
  }

  // Good: the redirect is part of the render output, so nothing protected paints first
  if (!session.data) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
```

**Correct (React Native):**

```tsx
// ./app/(protected)/_layout.tsx

export default function ProtectedLayout() {
  const session = useSession();

  if (session.isPending) {
    return <AppSkeleton />;
  }

  // Good: same shape — Redirect renders, so no protected screen mounts first
  if (!session.data) {
    return <Redirect href="/login" />;
  }

  return <Stack />;
}
```

Reference: [React Query Kit](https://github.com/liaoliao666/react-query-kit)

### 3.2 Pending, Empty & Error States

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
    - A virtualized list gives it a dedicated slot — `ListEmptyComponent` — which renders in place of the rows. Passing it is how the branch stops being something each screen remembers to write
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

Reference: [Query status and fetch status](https://tanstack.com/query/latest/docs/framework/react/guides/queries)

---

## 4. Performance & Robustness

### 4.1 Render Stability & Memoization

**Impact (MEDIUM):** Re-rendering is normal and usually cheap, and with the _React Compiler_ enabled the identity of values created during render is no longer the developer's problem. What review is left with is a different, smaller set of defects: memoization written by hand that only duplicates what the compiler already did, code the compiler cannot analyze and therefore silently skips, and a component subscribed to more of the store than it ever reads — which no amount of memoization fixes.

**Guidelines:**

1.  **The compiler memoizes, you do not:**
    - Objects, arrays, and functions created during render are memoized for you; `useMemo`, `useCallback`, and `memo` are the exception rather than the baseline
    - An inline literal in props is not a defect — `options={{ columns: 3 }}` is precisely the case the compiler covers
    - A hand-written memo has to say, in a comment, what the compiler could not see; without that, review cannot tell a real need from a habit carried over
2.  **Write code the compiler can analyze:**
    - It skips any component whose code might break the Rules of React rather than risk changing its behavior; with the recommended `panicThreshold: 'none'` that skip does not fail the build and leaves nothing in the source to read
    - The reverse failure matters more: when a violation is subtle enough that the _ESLint_ plugin misses it, the compiler optimizes a component it should have skipped, and the defect surfaces at runtime
    - Either way the finding is the rule violation itself, never a missing memo — and a `"use no memo"` left in the code is a violation someone worked around instead of fixing
    - What actually compiled is measurable rather than guessable: `react-compiler-healthcheck` reports the ratio, the `logger` option logs per-file compilation events, and _React DevTools_ badges the components that were compiled
3.  **Subscribe to a slice, not to the store:**
    - Reading the whole store re-renders the component on every change in it, whatever changed; a selector narrows that to the field the component actually reads
    - A selector that builds an object — `useStore((s) => ({ a: s.a, b: s.b }))` — returns a fresh reference on every call and re-renders every time, which is a subscription bug wearing the costume of a memoization bug. When several fields must come from one call, `useShallow` compares them field by field instead of by reference
    - This is the one identity problem the compiler cannot reach: it memoizes what a render produces, not what a component subscribed to
4.  **Constants belong to the module:**
    - A value that depends on neither props nor state has no reason to be built inside a render, compiler or not
    - This is a question of where the value belongs, not of what it costs to create
5.  **Effect dependencies are correctness, not performance:**
    - The compiler stabilizes identities; it does not decide when an effect should re-run
    - A dependency array remains a statement about what the effect reads (see the effect-discipline rule)

**Incorrect (a selector that rebuilds an object, and memoization the compiler already did):**

```tsx
type Props = { widgets: Widget[] };

export function Dashboard({ widgets }: Props) {
  // Bad: the selector returns a new object every call, so this re-renders on
  // every store change — not only when theme or density move
  const { theme, density } = useSettingsStore((s) => ({
    theme: s.theme,
    density: s.density,
  }));

  // Bad: the compiler already memoizes this — the wrapper states nothing
  const handleSelect = useCallback((id: string) => selectWidget(id), []);

  return (
    <WidgetGrid
      widgets={widgets}
      theme={theme}
      density={density}
      onSelect={handleSelect}
    />
  );
}
```

**Correct (one subscription per field, constants hoisted, the rest left to the compiler):**

```tsx
// Good: depends on nothing from render, so it does not belong inside it
const GRID_OPTIONS = { columns: 3 };

type Props = { widgets: Widget[] };

export function Dashboard({ widgets }: Props) {
  // Good: a density change no longer re-renders anything that only reads theme
  const theme = useSettingsStore((s) => s.theme);
  const density = useSettingsStore((s) => s.density);

  return (
    // Good: the literal and the arrow are exactly what the compiler memoizes
    <WidgetGrid
      widgets={widgets}
      theme={theme}
      density={density}
      options={GRID_OPTIONS}
      onSelect={(id) => selectWidget(id)}
    />
  );
}
```

```tsx
// Good: a hand-written memo that states what the compiler could not cover.
// The chart library holds this array by reference and re-initialises whenever it
// changes, so its identity is part of an external contract, not of React's render.
const series = useMemo(() => buildSeries(rows), [rows]);
```

Reference: [React Compiler](https://react.dev/learn/react-compiler)
