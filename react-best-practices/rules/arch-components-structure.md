---
title: Component File Structure
impact: HIGH
description: Fixes how one component's own files are organized — a single file, a folder with an index, or base and presets when variants differ in structure — and forbids a filename that repeats its folder.
tags: architecture, components, structure
---

## Component File Structure

**Impact (HIGH):** The folder-structure rule decides where a component lives in the project; this one decides what happens inside its own folder. Left undecided, the same component arrives in three different shapes across a codebase — a four-hundred-line file that should have been split, a folder of six siblings with no entry point, and a variant matrix expressed as a chain of conditionals — and every reader has to open the folder to find out which one they got. The shape is also what makes a diff reviewable: a new file under `presets/` is a new variant, and that is legible before reading a line of it.

**Guidelines:**

1.  **Three shapes, chosen by what the component contains:**
    - **Integral** — one file, `components/invoice-badge.tsx`, when there are no sub-components
    - **Grouped** — a folder with `index.tsx` as the entry point and one file per internal piece
    - **Base and presets** — a folder that splits the logic container from its visual implementations, for a component whose variants differ in structure
2.  **A folder earns its index when a second file appears:**
    - Promote from integral to grouped the moment a sub-component is extracted, not in anticipation of one
    - `index.tsx` holds the component the folder is named after; nothing else leaves the folder unless another module actually imports it
3.  **A filename never repeats the folder that contains it:**
    - `invoice-table/row.tsx`, never `invoice-table/invoice-table-row.tsx`; `button/presets/text.tsx`, never `button/presets/button-text.tsx`
    - The path already states the parent, so repeating it turns every rename of the component into a rename of every file beneath it
    - Only the filename drops the prefix. The exported component keeps its full name — `presets/text.tsx` exports `ButtonText`, because that name is read at a call site where no folder is in view
4.  **Base and presets is for structural variation, never for styling:**
    - When the variants differ only in which classes they carry, they are one component with a `cva` matrix (see the extraction-threshold rule); splitting those into presets multiplies files to express what one variant prop already expresses
    - The pattern earns its place when the variants render **different children** — a confirm dialog and a form dialog share open state, focus handling and the overlay, and share nothing about what sits inside them
    - `base/` holds the logic container and hands down what it owns through a `render` prop, which is exactly the case the composition rule reserves render props for
5.  **The barrels decide what is reachable:**
    - `base/index.ts` and `presets/index.ts` are internal; the folder's own `index.ts` decides what the rest of the codebase may import
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
./app/components/invoice-table/
├── invoice-table.tsx          ← no index, so the folder has no entry point
├── invoice-table-row.tsx      ← the folder already said "invoice-table"
└── invoice-table-header.tsx
```

**Correct (grouped folder with an index, internal files named for what they are):**

```plaintext
./app/components/invoice-table/
├── index.tsx    ← exports `InvoiceTable`
├── row.tsx      ← exports `InvoiceRow`
└── header.tsx   ← exports `InvoiceTableHeader`
```

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

  const handleClose = () => {
    setOpen(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        {render(handleClose)}
      </DialogContent>
    </Dialog>
  );
}
```

```tsx
// ./app/components/dialog/presets/confirm.tsx

import { DialogContainer } from '../base';

type Props = {
  title: string;
  description: string;
  trigger: React.ReactNode;
  onConfirm: () => void;
};

// Good: the preset owns presentation only — every shared behavior is in the base
export function ConfirmDialog({ title, description, trigger, onConfirm }: Props) {
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

```tsx
// Bad: presets for something the variant matrix already covers — these three
// differ by class alone, so they belong in one component with a cva axis
./app/components/badge/presets/success.tsx
./app/components/badge/presets/warning.tsx
./app/components/badge/presets/danger.tsx
```

Reference: [Importing and exporting components](https://react.dev/learn/importing-and-exporting-components)
