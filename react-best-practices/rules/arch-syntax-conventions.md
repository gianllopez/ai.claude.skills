---
title: Syntax & Conciseness Conventions
impact: LOW
description: Enforces specific syntax patterns for iterators, type definitions, handler naming, and conditionals to prioritize scanning speed and explicit control flow.
tags: architecture, syntax, conventions
---

## Syntax & Conciseness Conventions

**Impact (LOW):** Improves conciseness and reduces visual noise in high-frequency patterns, while enforcing explicit control flow in conditionals to prevent logic bugs and rendering accidents.

These conventions maximize the information density of the code, so logic can be scanned without getting lost in boilerplate.

### 1. Iterator Naming (Short-Hand Convention)

For inline array methods (`.map`, `.filter`, `.find`, `.forEach`), use the first letter of the collection's item name as the argument. This keeps the line short and puts the attention on the operation rather than on the binding.

**Exceptions:**

- **Block bodies:** when the callback body is a `{ … }` block, or it needs destructuring, use the full singular name — at that point the binding is read far from where it was bound
- **Nested iteration:** inside another iterator, use full names so the two bindings cannot be confused
- **The index keeps its name:** when the callback also takes the index it is always `index`, never `i` — the abbreviation belongs to the item

_JSX_ is not an exception: a multi-line element still takes the abbreviation, because the binding stays visible at the head of the same expression.

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

```tsx
// JSX keeps the abbreviation, however many lines the element takes
{
  invoices.map((i) => (
    <tr key={i.id}>
      <td>{i.number}</td>
      <td>{i.total}</td>
    </tr>
  ));
}

// The index is never the abbreviation
{
  steps.map((s, index) => (
    <li key={s.id}>
      {index + 1}. {s.label}
    </li>
  ));
}
```

### 2. Type and Object Literals

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

### 3. Event Handler Naming

Handler implementations use the `handle` prefix; event props keep the `on` prefix that the _DOM_ already uses. The distinction makes it immediately clear which side of the boundary a function is on — `onClick` is what the component accepts, `handleClick` is what this component does. Using `on` for both leaves the reader guessing.

**Incorrect (implementation named like a prop):**

```tsx
export function InvoiceRow({ invoice }: Props) {
  const onDownload = () => {
    downloadInvoice(invoice.id);
  };

  return <Button onClick={onDownload}>Download</Button>;
}
```

**Correct:**

```tsx
export function InvoiceRow({ invoice }: Props) {
  const handleDownload = () => {
    downloadInvoice(invoice.id);
  };

  return <Button onClick={handleDownload}>Download</Button>;
}
```

### 4. Function Declarations

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
  function handleDownload() {
    downloadInvoice(invoice.id);
  }

  async function handleArchive() {
    await archiveInvoice(invoice.id);
  }

  return <RowActions onDownload={handleDownload} onArchive={handleArchive} />;
}
```

**Correct (one function, the component; everything else an arrow on a const):**

```tsx
const formatAmount = (invoice: Invoice) =>
  `${invoice.currency} ${invoice.amount.toFixed(2)}`;

export function InvoiceRow({ invoice }: Props) {
  const handleDownload = () => {
    downloadInvoice(invoice.id);
  };

  const handleArchive = async () => {
    await archiveInvoice(invoice.id);
  };

  return <RowActions onDownload={handleDownload} onArchive={handleArchive} />;
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

### 5. Conditional Syntax

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

### 6. Blank Lines Inside JSX

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

**Correct (one continuous tree):**

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

Reference: [TypeScript Handbook - Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)
