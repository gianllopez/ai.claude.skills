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
