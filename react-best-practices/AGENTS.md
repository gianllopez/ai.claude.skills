# React Best Practices

**Version 2.0.0**  
_Gian López_  
_September 2026_

> **Note:**
> This document is mainly for agents and LLMs to follow when maintaining,
> generating, or refactoring _React_ codebases built with `react-hook-form`
> and `shadcn/ui`. Humans may also find it useful, but guidance here is
> optimized for automation and consistency by AI-assisted workflows.

---

## Abstract

Standards for the two things a _React_ web project adds on top of plain _HTML_ and _TailwindCSS_: a forms library — `react-hook-form` and the `shadcn/ui` Form components — that owns every field's value and its validation message, and the generator that writes `shadcn/ui` components into the project under a structure it has to be told about, or it undoes that structure the next time it runs. Framework-agnostic semantic _HTML_, _TailwindCSS_ v4 theming, layout stability, and CSS footprint are covered in `html-best-practices`, which a web project loads alongside this one. Everything independent of the renderer — effects, state, the query layer, component composition and typing — lives in `react-core-best-practices`, also loaded alongside this one. Accessibility auditing is excluded by design.

---

## Table of Contents

1. [Semantic Markup](#1-semantic-markup) — `HIGH`
   - [1.1 Form Markup & Field Association](#11-form-markup--field-association)
2. [View Structure](#2-view-structure) — `HIGH`
   - [2.1 View Structure & Generated Code](#21-view-structure--generated-code)

---

## 1. Semantic Markup

### 1.1 Form Markup & Field Association

**Impact (HIGH):** A form built from `div`s and a click handler loses submission on _Enter_, autofill, and the correct mobile keyboard. These are behaviors users expect and nobody reimplements completely. The same holds one level up: a component that keeps its own field state and its own error strings rebuilds what the form library already does, and the two copies drift — the label stops matching its control, the message stops matching the field.

**Guidelines:**

1.  **Every form goes through `react-hook-form`:**
    - The form instance owns every value; no component keeps field state of its own
    - Reading values back out of the _DOM_ by hand — `FormData`, a ref per input, `event.target.elements` — means the form was built twice
2.  **Fields are declared through the Form components:**
    - `FormField` / `FormItem` / `FormLabel` / `FormControl` / `FormMessage` wire the label to the control and the message to the field; writing `htmlFor` and an id by hand duplicates what they already do
    - A control rendered outside `FormControl` loses that wiring, and nothing reports it
    - The placeholder stays an example value (`jane@acme.co`) — the label is the label
3.  **A group of controls carries a label of its own:**
    - Related controls that only make sense together — radio groups, address blocks, date ranges — get one label for the group and one per option
    - The `Form` components express that with a group-level `FormLabel` and a nested `FormItem` per option; they emit no `fieldset` / `legend`, and wrapping one around them only declares the grouping twice
    - What review checks is that the group is named at all — an option list whose only labels are its options is a group nobody named
4.  **Type and name:**
    - Use the specific `type` (`email`, `tel`, `url`, `number`, `date`, `search`); it selects the mobile keyboard and parses the value
    - The `name` on `FormField` is what identifies the value — keep it identical to the key the mutation expects, so no mapping layer appears between them
5.  **Validation speaks once, and it is the form library:**
    - The `form` carries `noValidate`, so the browser's own checking never interrupts and every message the user reads comes from `FormMessage`
    - Constraints live on `FormField`'s `rules` and nowhere else — alongside `noValidate` a `required` attribute does nothing, and a component holding its own error string is a second source of truth
    - The `type` still earns its place through the mobile keyboard and the parsing; with native checking off it is no longer a validator, so it never competes for the message
6.  **Submission stays a real submission:**
    - A `form` element with `button type="submit"`, wrapping `handleSubmit`; never an action bound only to a button's `onClick`
    - The mutation hook is what the submit handler calls, not what replaces the form

**Incorrect (hand-held field state, no form element, no association, parallel error string):**

```tsx
export function SignupForm() {
  // Bad: field state by hand — the form library already owns this
  const [email, setEmail] = useState('');
  const [plan, setPlan] = useState('basic');
  const [emailError, setEmailError] = useState('');

  // Bad: not a form, so Enter does nothing and autofill has no context
  return (
    <div className="space-y-4">
      {/* Bad: placeholder used as the field name, no label, no association */}
      <input
        type="text"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full rounded-md border px-3 py-2"
      />
      {/* Bad: an error string tracked in parallel to the field it describes */}
      <p className="text-sm text-destructive">{emailError}</p>
      {/* Bad: the options are labelled, the group they belong to is not */}
      <div className="flex gap-4">
        <input type="radio" value="basic" onChange={() => setPlan('basic')} />{' '}
        Basic
        <input type="radio" value="pro" onChange={() => setPlan('pro')} /> Pro
      </div>
      <button onClick={submitForm} className="rounded-md bg-primary px-4 py-2">
        Continue
      </button>
    </div>
  );
}
```

**Correct (the form owns the values, the Form components own the wiring and the grouping):**

```tsx
type FormValues = {
  email: string;
  phone: string;
  plan: 'basic' | 'pro';
};

export function SignupForm() {
  const createAccount = useCreateAccount();
  const form = useForm<FormValues>({
    defaultValues: {
      email: '',
      phone: '',
      plan: 'basic',
    },
  });

  return (
    <Form {...form}>
      {/* Good: noValidate hands every message to the form library */}
      <form
        noValidate
        onSubmit={form.handleSubmit((values) => createAccount.mutate(values))}
        className="space-y-4"
      >
        <FormField
          control={form.control}
          name="email"
          rules={{ required: 'Email is required' }}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" placeholder="jane@acme.co" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="phone"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Phone</FormLabel>
              <FormControl>
                <Input type="tel" {...field} />
              </FormControl>
            </FormItem>
          )}
        />
        {/* Good: the group is named by its own FormLabel, each option by its own */}
        <FormField
          control={form.control}
          name="plan"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Plan</FormLabel>
              <FormControl>
                <RadioGroup
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                  className="flex gap-4"
                >
                  <FormItem className="flex items-center gap-2">
                    <FormControl>
                      <RadioGroupItem value="basic" />
                    </FormControl>
                    <FormLabel className="font-normal">Basic</FormLabel>
                  </FormItem>
                  <FormItem className="flex items-center gap-2">
                    <FormControl>
                      <RadioGroupItem value="pro" />
                    </FormControl>
                    <FormLabel className="font-normal">Pro</FormLabel>
                  </FormItem>
                </RadioGroup>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={createAccount.isPending}>
          Continue
        </Button>
      </form>
    </Form>
  );
}
```

Reference: [shadcn/ui Form](https://ui.shadcn.com/docs/components/form)

---

## 2. View Structure

### 2.1 View Structure & Generated Code

**Impact (HIGH):** The layer boundary itself — `core/`, `shared/`, and the direction imports flow — belongs to `react-core-best-practices`, because none of it changes with the renderer. What is left here is what only the web has: a view layer with a design-system folder inside it, and a generator that writes files into the project on its own terms. Both decay the same way, and the second decays faster — a structure the generator does not know about is undone the first time someone runs `shadcn add`.

**Guidelines:**

1.  **The view layer splits by responsibility:**
    - `components/` holds reusable presentation, with the design-system primitives under `components/ui/`
    - `components/ui/` is the generator's target and nothing else lands there; a component the project wrote sits beside it, not inside it
    - That route modules compose and never fetch is the core skill's rule; this one only fixes where the components they arrange live
2.  **The tooling has to agree with the structure:**
    - `tsconfig` resolves `~/*` to the source root, and every generator reads the alias from there
    - `components.json` decides where the next generated file lands, so its aliases are part of the structure and not a detail
    - Its `tailwind` block is part of the same contract: `cssVariables: true` is what makes generated components read the semantic tokens instead of arriving with the palette baked in, and `baseColor` seeds those variables at generation time (see the theme-tokens rule in `html-best-practices`)
    - Point `ui` and `components` at the view layer, `utils` at `~/core/lib/utils`, and `lib` and `hooks` into `~/core/lib/shadcn/`. The generator then writes the component into `components/ui/`, rewrites its `cn` import to our path, and drops everything else it brings — its own helpers and hooks — under `core/lib/shadcn/`
    - Its `hooks` alias deliberately does not point at `core/hooks/`: those are ours to edit, and anything the generator writes is not
3.  **`core/lib/shadcn/` is generated territory, and read-only:**
    - The folder is listed in `.prettierignore`, so the formatter never rewrites it — which means any diff inside it is a deliberate edit and never noise
    - Editing a file there is a review finding, however small the change: the file is regenerable and not ours, so the edit is silently lost the next time the generator writes over it
    - When the generated behavior is not what the project needs, add a module beside it — a new component or hook that wraps or replaces it — instead of patching in place
    - If the generated file genuinely has to change, promote it: move the behavior into a module the project owns, and stop pretending the generator still governs it

**Incorrect (a structure the generator does not know about, and a patched generated file):**

```json
// ./components.json
{
  "tailwind": {
    "css": "app/styles/app.css",
    "cssVariables": false
  },
  "aliases": {}
}
```

With `cssVariables: false` every component installed from then on ships with the palette baked in and the semantic layer stops existing; with no aliases the generator writes to its own defaults, so `shadcn add` undoes the project's layout on the next run.

```ts
// ./app/core/lib/shadcn/hooks/use-mobile.ts

// Bad: a deliberate edit inside generated territory. It is lost the next time
// the generator writes this file, and nothing warns anyone
const MOBILE_BREAKPOINT = 640;
```

**Correct (the generator writes where the project says, and what it wrote stays untouched):**

```plaintext
app/
├─ core/
│  └─ lib/
│     ├─ utils.ts                  ← cn(), the tailwind-merge adapter
│     └─ shadcn/                   ← whatever the generator brings besides components
│        └─ hooks/
│           └─ use-mobile.ts       ← generated, read-only
├─ components/
│  ├─ ui/
│  │  └─ button.tsx                ← the generator's target
│  └─ invoice-table.tsx            ← ours, beside it rather than inside it
└─ routes/
   └─ invoices.tsx
```

```json
// ./components.json — the generator has to know the structure, or it will not follow it
{
  "tailwind": {
    "css": "app/styles/app.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "aliases": {
    "components": "~/components",
    "ui": "~/components/ui",
    "utils": "~/core/lib/utils",
    "lib": "~/core/lib/shadcn",
    "hooks": "~/core/lib/shadcn/hooks"
  }
}
```

```tsx
// ./app/components/mobile-nav.tsx

// Good: the generated hook is consumed, never edited. A behavior the project
// needs differently gets a module of its own beside it
import { useIsMobile } from '~/core/lib/shadcn/hooks/use-mobile';

export function MobileNav() {
  const isMobile = useIsMobile();

  return isMobile ? <NavDrawer /> : <NavBar />;
}
```

Reference: [shadcn/ui components.json](https://ui.shadcn.com/docs/components-json)
