# React Best Practices

**Version 1.0.0**  
_Gian López_  
_August 2026_

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring _React_ and _TailwindCSS_ codebases. Humans  
> may also find it useful, but guidance here is optimized for automation  
> and consistency by AI-assisted workflows.

---

## Abstract

Standards for the part of a _React_ application that only exists on the web: the markup that carries the meaning, the styling that presents it, and the generator that writes components into the project. Semantic elements first, because the element is what makes a page machine-readable and a form behave the way users expect; then _TailwindCSS_ v4, where styling resolves through theme tokens rather than arbitrary values, sized to the project — one plain theme by default, the variable-backed semantic layer where `shadcn/ui` or a theme swap reads it; then the view layer's own structure and the contract that keeps a declared layout from being undone the next time the generator runs; and finally the two defects utility CSS makes easiest to ship, layout shift and a stylesheet that never saw half its classes. Everything independent of the renderer — effects, state, the query layer, component composition and typing — lives in `react-core-best-practices`, which a web project loads alongside this one. Accessibility auditing is excluded by design.

---

## Table of Contents

1. [Semantic Markup](#1-semantic-markup) — `CRITICAL`
   - [1.1 Correct Interactive Elements](#11-correct-interactive-elements)
   - [1.2 Document Outline & Sectioning](#12-document-outline--sectioning)
   - [1.3 Form Markup & Field Association](#13-form-markup--field-association)
   - [1.4 Content Elements: Lists, Tables & Media](#14-content-elements-lists-tables--media)
2. [Styling with TailwindCSS](#2-styling-with-tailwindcss) — `CRITICAL`
   - [2.1 Theme Tokens Over Arbitrary Values](#21-theme-tokens-over-arbitrary-values)
   - [2.2 State-Driven Styling With Data Attributes](#22-state-driven-styling-with-data-attributes)
   - [2.3 Responsive & Variant Usage](#23-responsive--variant-usage)
   - [2.4 @apply, Custom Utilities & Overrides](#24-apply-custom-utilities--overrides)
   - [2.5 Class Attribute Formatting & Order](#25-class-attribute-formatting--order)
3. [View Structure](#3-view-structure) — `HIGH`
   - [3.1 View Structure & Generated Code](#31-view-structure--generated-code)
4. [Performance & Robustness](#4-performance--robustness) — `HIGH`
   - [4.1 Layout Stability & Overflow](#41-layout-stability--overflow)
   - [4.2 Source Detection & CSS Footprint](#42-source-detection--css-footprint)

---

## 1. Semantic Markup

### 1.1 Correct Interactive Elements

**Impact (CRITICAL):** An interactive `div` throws away behavior the browser provides for free — keyboard activation, form submission, link context menus, middle-click and modifier-click navigation, framework prefetching, and `:disabled` state. Rebuilding any of it costs more code than using the right element, and the reimplementation drifts the moment someone edits it.

**Guidelines:**

1.  **Element by intent:**
    - Navigation that changes the URL is an anchor, and it carries a real `href`
    - An action that stays on the page is a `button`
    - An anchor without `href` is not a link — if there is no destination, it is a `button`
2.  **Button type is mandatory:**
    - Every `button` inside a `form` declares `type`; the default is `submit`, so an unmarked action button silently submits the form
    - Wrapping it in a component changes nothing: a `Button` with no `type` is still a submit button
3.  **No click handlers on inert elements:**
    - `onClick` on `div`, `span`, or `li` as the only interaction path is a defect, not a style choice
    - Utilities like `cursor-pointer` make a `div` look interactive without making it interactive
4.  **Disabled is an attribute:**
    - Use the `disabled` attribute so the control stops firing; `opacity-50 pointer-events-none` only hides the affordance and leaves the handler reachable by other means
    - Style the real state with the `disabled:` variant

**Incorrect (clickable div, untyped form button, fake disabled state):**

```tsx
type Props = { busy: boolean };

export function Toolbar({ busy }: Props) {
  return (
    <form onSubmit={handleSubmit}>
      {/* Bad: a div is not a control */}
      <div
        onClick={handleSave}
        className="cursor-pointer rounded-md bg-primary px-4 py-2"
      >
        Save
      </div>
      {/* Bad: no type — a Button inside a form still defaults to submit */}
      <Button onClick={openHelp}>Help</Button>
      {/* Bad: disabled is only painted, the handler still runs */}
      <Button
        onClick={publish}
        className={busy ? 'pointer-events-none opacity-50' : ''}
      >
        Publish
      </Button>
    </form>
  );
}
```

**Correct (native controls, explicit type, real disabled attribute):**

```tsx
type Props = { busy: boolean };

export function Toolbar({ busy }: Props) {
  return (
    <form onSubmit={handleSubmit}>
      <Button type="submit">Save</Button>
      <Button type="button" onClick={openHelp}>
        Help
      </Button>
      {/* Good: the attribute stops the handler, and the component already
          carries the disabled styling */}
      <Button type="button" onClick={publish} disabled={busy}>
        Publish
      </Button>
    </form>
  );
}
```

Reference: [The button element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button)

### 1.2 Document Outline & Sectioning

**Impact (HIGH):** The element carries the meaning; the utility class carries the presentation. When every block is a `div`, the only structure a page has left is its class names, and the outline has to be reconstructed by whoever reads it next. Nothing breaks visibly, which is exactly why this decays quietly and is expensive to retrofit — but three of its failures are concrete rather than abstract: a route that adds its own `main` leaves the page with two, a skipped heading rank makes the outline lie about what contains what, and pages that never declare a title are indistinguishable in the tab bar and the history.

**Guidelines:**

1.  **Page skeleton:**
    - Build the page from `header`, `nav`, `main`, `footer`, and `aside`
    - Exactly one `main` per rendered page, and it is not nested inside another landmark
2.  **Landmarks belong to the layout route:**
    - In a nested-routing setup the skeleton lives in the layout route, wrapped around the slot where the router inserts the child route
    - A route component that opens with its own `main` is how a page ends up with two
3.  **Sectioning rules:**
    - `section` requires a heading — a `section` with no heading should be a `div`
    - `article` is for self-contained content that would still make sense extracted (a post, a comment, a product card)
    - Nesting a `section` inside an `article` is fine; using either purely to attach padding is not
4.  **Heading rank is structure, not size:**
    - Ranks descend one at a time; never skip from `h1` to `h4` to get a smaller font
    - Visual size comes from utilities (`text-2xl`, `text-sm`), rank comes from the tag
    - One `h1` per page, describing the page — not the site name on every route
5.  **Every page declares its own title and description:**
    - Both are set per page, through whatever mechanism the framework provides; a page that inherits them is indistinguishable from every other one in the tab bar, the history, and a bookmark
    - The title names the page the same thing its `h1` does — when the two disagree, one of them is wrong
    - The description summarises that page in a sentence, not the product's tagline repeated everywhere
6.  **When `div` is right:**
    - A `div` is the correct element when no other element carries the meaning: a flex/grid container, a positioning context, an overflow clip

**Incorrect (div soup, skipped heading rank, section used as a padding box, no title or description):**

```tsx
// Bad: the page declares no title and no description, so the tab and the history
// entry repeat whatever the root said
export default function ReportsRoute() {
  return (
    <div className="mx-auto max-w-5xl">
      <div className="flex items-center justify-between py-4">
        <div className="text-xl font-bold">Acme</div>
        <div className="flex gap-4">
          <Link to="/pricing">Pricing</Link>
          <Link to="/docs">Docs</Link>
        </div>
      </div>
      <div className="py-10">
        <h1 className="text-4xl font-bold">Reports</h1>
        {/* Bad: rank skipped to get a smaller size */}
        <h4 className="text-lg font-medium">Latest activity</h4>
        {/* Bad: section with no heading, used only for spacing */}
        <section className="space-y-4">
          <div className="rounded-lg border p-4">
            <div className="font-semibold">Q3 summary</div>
            <p>Revenue grew 12% quarter over quarter.</p>
          </div>
        </section>
      </div>
    </div>
  );
}
```

**Correct (skeleton in the layout, content in the route, descending ranks):**

```tsx
// ./app/routes/layout.tsx — owns the landmarks
export default function AppLayout() {
  return (
    <div className="mx-auto max-w-5xl">
      <header className="flex items-center justify-between py-4">
        <span className="text-xl font-bold">Acme</span>
        <nav className="flex gap-4">
          <Link to="/pricing">Pricing</Link>
          <Link to="/docs">Docs</Link>
        </nav>
      </header>
      <div className="flex gap-8 py-10">
        <main className="flex-1">
          <Outlet />
        </main>
        <aside className="w-64">
          <RecentActivity />
        </aside>
      </div>
      <footer className="py-6 text-sm text-muted-foreground">© Acme</footer>
    </div>
  );
}
```

```tsx
// ./app/routes/reports.tsx — content only, no second main
export default function ReportsRoute() {
  return (
    <>
      {/* Good: the title says what the h1 says, and the description is about this
          page rather than about the product */}
      <title>Reports · Acme</title>
      <meta
        name="description"
        content="Activity and summaries for the current quarter."
      />
      <h1 className="mb-6 text-4xl font-bold">Reports</h1>
      <section className="space-y-4">
        {/* Good: rank descends, size is a utility */}
        <h2 className="text-lg font-medium">Latest activity</h2>
        <article className="rounded-lg border p-4">
          <h3 className="font-semibold">Q3 summary</h3>
          <p>Revenue grew 12% quarter over quarter.</p>
        </article>
      </section>
    </>
  );
}
```

Reference: [HTML sections and outlines](https://html.spec.whatwg.org/multipage/sections.html)

### 1.3 Form Markup & Field Association

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

### 1.4 Content Elements: Lists, Tables & Media

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
    - The configured instance — plugins and locale — lives in `core/lib/dayjs.ts`, and components import that rather than the package (see the folder-structure rule in `react-core-best-practices`, which decides when a library earns a module there)

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

---

## 2. Styling with TailwindCSS

### 2.1 Theme Tokens Over Arbitrary Values

**Impact (CRITICAL):** Every arbitrary value is a design decision made outside the design system. Once `bg-[#1d4ed8]` appears in three files, the brand color has no single definition, a theme change becomes a find-and-replace, and dark mode has nothing to swap. In v4 the theme is the stylesheet: tokens declared in `@theme` generate utilities _and_ expose CSS variables, so there is no reason to hardcode. What that does not settle is how many layers the theme has — in one project a single `@theme` is the whole system, in another it sits under the semantic layer `shadcn/ui` writes. Applying the second shape to the first is its own defect: a dozen role names nothing reads, and a review that reports the wrong findings against them.

**Guidelines:**

1.  **Declare once, in `@theme`:**
    - Colors, radii, fonts, breakpoints, and shadows live in the `@theme` block of the main stylesheet
    - A token generates its utilities automatically: `--color-primary` yields `bg-primary`, `text-primary`, `border-primary`
    - The spacing scale is the exception and is never redeclared: `--spacing` is _Tailwind_'s and the design works in its steps, so a diff that redefines it is changing every margin, gap and size in the project at once
2.  **Size the token layer to the project:**
    - The default is one layer. A plain `@theme` holding the colors, radii, fonts and type steps the design actually uses — each named for what it is — is a complete system, and most projects need nothing more
    - The second, variable-backed layer — `:root` / `.dark` pairs mapped in through `@theme inline` — solves exactly one problem: a value that has to change while the same class stays on the element. `shadcn/ui` needs it, because its components are generated against those variable names, and a theme swap needs it — dark mode, per-tenant branding. Nothing else does
    - Without one of those two reasons the indirection returns nothing: `--color-primary: var(--primary)` is a second name for one value, and `bg-background` on a page with one background is a lookup that answers itself
    - So a semantic role name is worth writing when something reads it. `--card`, `--popover`, `--muted-foreground`, `--ring` hand-written into a project with no generator and no theme swap are consumers of nothing — declaring them is the finding, not omitting them
    - The question is never "is this name semantic enough". It is what breaks if the value stays where it is: nothing breaks, leave it; a theme has to reach it, a generated component reads it, or it is repeated across files, it is a token
3.  **Where `shadcn/ui` is installed, the semantic layer is not optional decoration:**
    - `shadcn init` writes it and every generated component reads it: `--background` / `--foreground` for the page, `--card` and `--popover` for raised surfaces, `--primary` and `--secondary` for actions, `--muted` and `--muted-foreground` for de-emphasised fills and text, `--accent` for hover and selection, `--destructive` for danger, and `--border` / `--input` / `--ring` for edges
    - Each pair travels together: a `--*-foreground` is the contrast partner of its surface, so painting `bg-muted` and then picking the text colour by hand breaks the pair the generator maintains
    - The brand colour is declared there and nowhere else: our own components paint with `bg-primary` too, which is the only thing that keeps them in step with every generated one
    - A parallel brand scale is a second source of truth for one decision — the day `--primary` changes, everything painted with the other name quietly stops matching
    - A plain `@theme` sits beside it for what the generator does not decide: the font, type steps, radii of our own
    - Roles it ships no token for — success, warning, info — follow its shape when the project actually needs them: a status colour that has to survive `.dark` earns a surface and its foreground, one that appears once in a single-theme project does not
4.  **Turn on the switch that makes the generated half real:**
    - In a `shadcn/ui` project, `components.json` decides what the generator writes: with `cssVariables: false` every component it installs arrives with the palette baked in — `bg-neutral-900` instead of `bg-primary` — and the semantic layer stops existing
    - `baseColor` picks the neutral ramp those variables are seeded from, and it is read at generation time, so changing it later rewrites nothing that already exists
    - Both belong to the structure, not to the setup ceremony (see the view-structure rule)
5.  **Reach for the token that names the role, where the role has a token:**
    - With a semantic layer present, muted text is `text-muted-foreground`, a hover or selected row is `bg-accent`, an error message is `text-destructive`. A step off the neutral ramp standing in for any of them is the finding
    - The palette is not arbitrary — every ramp step is a real theme token — which is exactly why this slips through: it looks tokenised and still hardcodes a decision the semantic layer already owns
    - The test is whether the value survives a theme change. A role token does; a ramp step does not
    - With no semantic layer and no theme to survive, `text-neutral-500` is not a defect on its own. It becomes one when the same value repeats across files, or when a theme that has to reach it arrives — and the fix then is one token for the value in hand, not a role system built ahead of it
6.  **Arbitrary values are a review flag:**
    - `bg-[#1d4ed8]`, `p-[13px]`, `text-[15px]` mean one of two things: the token exists and was not used, or the token is missing and must be added
    - Legitimate use is genuinely one-off geometry with no reuse — `grid-cols-[auto_1fr]`, `mask-[url(...)]`, a third-party magic offset
    - A color is almost never one-off, and a spacing value never is: `p-[13px]` means the markup drifted off the scale, and the fix is the nearest step — not a token of its own
7.  **A token outlives the diff that stops using it:**
    - The diff that removes a token's last consumer removes the token too — leaving it behind is how a stylesheet accumulates values nobody can tell apart from the live ones
    - Declaring ahead of use is not the same defect and is not a finding: a design system defines its scale before every step has a consumer, and a token waiting for its first caller is design, not debt
    - In a `shadcn/ui` project the generator's own tokens are never pruned on either count — `--chart-*` and `--sidebar-*` sit unused until the component that needs them is installed, and removing them breaks the next `shadcn add`
    - The reverse direction is a finding: a value repeated across files and declared nowhere is a token that was never written down
8.  **Do not bypass the utility layer:**
    - `style={{ color: 'var(--color-primary)' }}` skips variants, merge resolution, and the sort order
    - The `style` prop is reserved for values computed at runtime (an animated transform, a measured offset)
9.  **v4 configuration:**
    - There is no `tailwind.config.js` by default; the theme is CSS
    - A JS config is reintroduced only through `@config` when a legacy plugin requires it
    - Where a variable-backed layer exists, `@theme inline` is what makes it work: it compiles `bg-background` down to `var(--background)` instead of copying the value, so the utility still follows the variable when `.dark` redefines it — a plain `@theme` freezes whatever the variable held at build time. Where there is no such layer there is nothing to follow, and `@theme` is the whole file

**Incorrect (values invented at the call site — and, below, a role layer nothing reads):**

```tsx
type Props = React.ComponentProps<'span'>;

export function Badge({ children }: Props) {
  return (
    <span
      // Bad: brand color and spacing invented at the call site
      className="rounded-[7px] bg-[#1d4ed8] px-[13px] py-[5px] text-[13px] text-white"
      // Bad: the token exists, and reaching it through style skips the utility layer
      style={{ borderColor: 'var(--color-primary)' }}
    >
      {children}
    </span>
  );
}
```

```css
/* ./app/styles/app.css — no generator, no dark mode, no second theme */
@import 'tailwindcss';

/* Bad: the shape of a shadcn stylesheet copied into a project that has none.
   Every one of these names is read by nothing, half of them hold the same
   value, and the indirection has to be maintained anyway */
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --ring: oklch(0.708 0 0);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  /* …one line per name, for a page that renders one surface */
}
```

**Correct — the default shape (one `@theme`, tokens named for the design):**

```css
/* ./app/styles/app.css */
@import 'tailwindcss';

/* The design's own decisions, declared once. No --spacing here — the scale is
   Tailwind's and the design works in its steps */
@theme {
  --font-sans: 'Inter Variable', sans-serif;
  --color-brand: oklch(0.53 0.19 262);
  --color-brand-strong: oklch(0.44 0.19 262);
  --radius-badge: 0.4375rem;
  --text-badge: 0.8125rem;
}
```

```tsx
import { cn } from '~/core/lib/utils';

type Props = React.ComponentProps<'span'>;

export function Badge({ className, ...props }: Props) {
  return (
    <span
      className={cn(
        'rounded-badge bg-brand px-3 py-1 text-badge text-white',
        className,
      )}
      {...props}
    />
  );
}
```

**Correct — with `shadcn/ui` or a theme swap, where the variable-backed layer earns its indirection:**

```css
/* ./app/styles/app.css */
@import 'tailwindcss';

/* The variant that makes every dark: utility resolve against the .dark class */
@custom-variant dark (&:is(.dark *));

/* Written by `shadcn init`: the semantic layer every generated component reads,
   and the only place the brand colour is declared. Each surface ships with the
   foreground that is legible on it */
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary: oklch(0.53 0.19 262);
  --primary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --destructive: oklch(0.577 0.245 27);
  --destructive-foreground: oklch(0.985 0 0);

  /* Ours: a status role the generator ships no token for, added because the
     project paints with it in both themes */
  --success: oklch(0.55 0.14 150);
  --success-foreground: oklch(0.985 0 0);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --primary: oklch(0.62 0.19 262);
  --primary-foreground: oklch(0.145 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --destructive: oklch(0.704 0.191 22);
  --destructive-foreground: oklch(0.145 0 0);

  --success: oklch(0.63 0.15 150);
  --success-foreground: oklch(0.145 0 0);
}

/* inline, so bg-primary compiles to var(--primary) and keeps following the
   variable under .dark — a plain @theme would freeze the light value here */
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-success: var(--success);
  --color-success-foreground: var(--success-foreground);
}

/* Ours: the decisions the generator does not make */
@theme {
  --font-sans: 'Inter Variable', sans-serif;
  --radius-badge: 0.4375rem;
  --text-badge: 0.8125rem;
}
```

```tsx
import { cn } from '~/core/lib/utils';

type Props = React.ComponentProps<'span'>;

export function Badge({ className, ...props }: Props) {
  return (
    <span
      className={cn(
        'rounded-badge bg-primary px-3 py-1 text-badge text-primary-foreground',
        className,
      )}
      {...props}
    />
  );
}
```

Reference: [Theme variables](https://tailwindcss.com/docs/theme)

### 2.2 State-Driven Styling With Data Attributes

**Impact (HIGH):** When state lives in a `data-*` attribute, the whole variant matrix is visible on one line of markup and the browser applies it. When state is expressed by swapping class strings in _JavaScript_, presentation scatters across event handlers and effects, `tailwind-merge` cannot resolve conflicts it never sees, and the rendered class list becomes impossible to predict while reading a diff.

**Guidelines:**

1.  **Expose state as data:**
    - Render `data-state="open"` or a boolean `data-active` and style with `data-[state=open]:` / `data-active:` variants
    - This is the convention headless libraries already emit — style their state instead of mirroring it in _React_ state
    - A generated component arrives already emitting it: _Radix_ writes `data-state`, `data-disabled`, `data-side` and `data-orientation` on its own primitives, so styling one means writing the variant, never adding a parallel boolean of ours to track what the component already announces
2.  **Descendants read the parent:**
    - Mark the container `group` and let children use `group-data-[state=open]:rotate-180`
    - Do not prop-drill a boolean whose only purpose is styling
3.  **Structural conditions:**
    - `has-*` styles a parent from its children (`has-[:checked]:border-primary`), removing wrappers that existed only to receive a class
    - `not-*` inverts without a second branch; `group` and `peer` are relationship variants and live in the variants-and-responsive rule
4.  **Never mutate classes imperatively:**
    - `element.classList.add(...)` or assigning `className` in an effect puts design state outside the render output
5.  **Boolean data attributes must be absent, not `"false"`:**
    - `data-active="false"` still matches the `data-active:` variant — the variant tests for presence
    - Render `data-active={isActive || undefined}` so the attribute disappears when false
6.  **An arbitrary variant is a selector living in a class attribute:**
    - `[&>*:nth-child(3)]:mt-0` styles by position, so it breaks the moment an element is inserted, and nothing in the markup says why the third child is special
    - The legitimate case is a slot this component does not render — `[&_svg]:size-4` on a button that accepts any icon
    - A cluster of them on one element is a structural finding: the child needs a component or a prop, not a longer selector
    - This is the same defect as styling from an effect, one level down: the rule lives in the class attribute instead of in the markup, so nothing at the call site says why it applies

**Incorrect (class toggling in an effect, prop-drilled styling boolean, data-active="false"):**

```tsx
type Props = {
  steps: Step[];
  currentIndex: number;
};

export function Stepper({ steps, currentIndex }: Props) {
  const barRef = useRef<HTMLDivElement>(null);

  // Bad: presentation applied outside the render output
  useEffect(() => {
    barRef.current?.classList.toggle('hidden', currentIndex === 0);
  }, [currentIndex]);

  return (
    <ol>
      {steps.map((s, index) => (
        <li
          key={s.id}
          // Bad: "false" still matches data-active:
          data-active={index === currentIndex ? 'true' : 'false'}
          className="data-active:bg-accent"
        >
          {s.label}
          {/* Bad: a boolean passed down only to pick a class */}
          <Check filled={index < currentIndex} />
        </li>
      ))}
      <div ref={barRef} />
    </ol>
  );
}
```

**Correct (state on the element, variants do the styling, attribute omitted when false):**

```tsx
type Props = {
  steps: Step[];
  currentIndex: number;
};

export function Stepper({ steps, currentIndex }: Props) {
  const getState = (index: number) => {
    if (index < currentIndex) {
      return 'complete';
    }

    if (index === currentIndex) {
      return 'current';
    }

    return 'upcoming';
  };

  return (
    <ol>
      {steps.map((s, index) => (
        <li
          key={s.id}
          data-state={getState(index)}
          // Good: not-* dims every step that is not the current one, with no
          // second branch and no extra attribute to carry the negation
          className="group flex items-center gap-3 not-data-[state=current]:opacity-60"
        >
          <button
            type="button"
            // Good: attribute is absent when inactive
            data-active={index === currentIndex || undefined}
            className="flex w-full items-center justify-between data-active:bg-accent"
          >
            {s.label}
            {/* Good: the child reads the group's state */}
            <Check className="opacity-0 group-data-[state=complete]:opacity-100" />
          </button>
        </li>
      ))}
    </ol>
  );
}
```

```tsx
// Good: the primitive already announces its own state, so there is nothing to
// mirror — the variant reads what Radix writes, and has-* styles the container
// from its own child instead of a wrapper that existed to carry a class
<AccordionItem value="billing" className="group border-b">
  <AccordionTrigger className="data-[state=open]:text-primary">
    Billing
    <Chevron className="transition-transform group-data-[state=open]:rotate-180" />
  </AccordionTrigger>
  <AccordionContent>{item.body}</AccordionContent>
</AccordionItem>;

<label className="rounded-md border p-3 has-[:checked]:border-primary">
  <input type="checkbox" />
  <span>Enable notifications</span>
</label>;
```

Reference: [Styling based on data attributes](https://tailwindcss.com/docs/hover-focus-and-other-states#data-attributes)

### 2.3 Responsive & Variant Usage

**Impact (HIGH):** Rendering the same content twice — once for mobile, once for desktop — doubles the DOM, duplicates every future edit, and guarantees the two copies drift. The same applies to a second component for dark mode. Variants exist so one tree covers every context; reaching for _JavaScript_ breakpoints moves layout decisions off the platform and into a render cycle that runs after paint.

**Guidelines:**

1.  **Mobile-first:**
    - Unprefixed utilities are the base; `sm:` / `md:` / `lg:` apply from that breakpoint up
    - `max-*` variants only when the design genuinely inverts at a breakpoint, not as a default style
2.  **One tree per content:**
    - `block md:hidden` paired with `hidden md:block` for the same content is duplication — restyle the single tree instead
    - Acceptable only when mobile and desktop render genuinely different content, not a different arrangement of the same content
3.  **Relationship variants over lifted state:**
    - Parent hover / focus: mark the parent `group`, style children with `group-hover:`
    - Sibling state: mark the input `peer`, style with `peer-checked:` / `peer-disabled:`
    - These replace `useState` that only existed to drive a class
4.  **Container queries for components:**
    - When a component's width is not the viewport's (sidebar, modal, grid cell), use `@container` on the wrapper and `@sm:` / `@md:` on children
    - A card that must look right in two column widths is a container-query problem, not a breakpoint problem
5.  **Dark mode belongs to the theme, not to the components:**
    - `bg-card` is already right in both themes, because `--card` is what changes under `.dark` (see the theme-tokens rule for the variant that wires it)
    - A `dark:` inside a component is therefore a signal: it says the element was painted with something that does not change — a palette step — and the fix is the token, not the variant
    - Where `dark:` genuinely earns its place — a raster image, a shadow, a third-party surface we cannot tokenise — it is a variant on the same element, never a parallel component
6.  **No JS breakpoints for layout:**
    - A `useMediaQuery` hook driving pure layout duplicates CSS in _JavaScript_ and flashes on first render

**Incorrect (duplicated trees, dark mode as a second component):**

```tsx
type Props = { product: Product };

export function ProductCard({ product }: Props) {
  const theme = useSettingsStore((s) => s.theme);

  // Bad: a whole second component for a colour the theme already swaps
  if (theme === 'dark') {
    return <ProductCardDark product={product} />;
  }

  return (
    <>
      {/* Bad: the same content rendered twice */}
      <div className="block bg-card p-4 md:hidden">
        <h3 className="text-base">{product.name}</h3>
        <p className="text-sm">{product.price}</p>
      </div>
      <div className="hidden bg-card p-8 md:block">
        <h3 className="text-xl">{product.name}</h3>
        <p className="text-base">{product.price}</p>
      </div>
    </>
  );
}
```

**Correct (one tree, mobile-first variants, container query, dark resolved in the theme):**

```tsx
type Props = { product: Product };

export function ProductCard({ product }: Props) {
  return (
    <div className="@container">
      {/* Good: no dark: anywhere — the token already changes with the theme */}
      <article className="bg-card p-4 @md:p-8">
        <h3 className="text-base @md:text-xl">{product.name}</h3>
        <p className="text-sm @md:text-base">{product.price}</p>
      </article>
    </div>
  );
}
```

```tsx
{
  /* group and peer replace state that only drove a class */
}
<Link
  to="/reports"
  className="group flex items-center gap-2 rounded-md p-3 hover:bg-accent"
>
  <span className="text-muted-foreground group-hover:text-primary">
    Reports
  </span>
</Link>;

<label className="flex items-center gap-2">
  <input type="checkbox" name="archived" className="peer sr-only" />
  <span className="rounded-md border px-3 py-1 peer-checked:border-primary peer-checked:bg-accent">
    Include archived
  </span>
</label>;
```

Reference: [Responsive design](https://tailwindcss.com/docs/responsive-design)

### 2.4 @apply, Custom Utilities & Overrides

**Impact (HIGH):** `@apply` recreates the exact problem utility CSS removes — a growing semantic class layer with its own naming debate, its own specificity conflicts, and its own dead code that nobody dares delete. It is also invisible to `tailwind-merge`, so `.btn` and a caller's `bg-red-500` fight by stylesheet order. Reuse belongs in a component; a genuinely new primitive belongs in `@utility`.

**Guidelines:**

1.  **Reuse is a component boundary:**
    - Repeating a utility set means a component is missing, not that a CSS class is missing
    - This holds in template languages too: a partial or include is the reuse unit
2.  **When `@apply` is acceptable:**
    - Markup you do not control: third-party widgets, rich text from a CMS, generated output
    - A handful of base element styles inside `@layer base`
    - Not for building an in-house component library out of class names
3.  **Real primitives use `@utility`:**
    - A custom utility declared with `@utility` participates in variants (`hover:`, `md:`, `dark:`) and in merge ordering
    - A plain `@layer components` class does neither, which is why it eventually needs the important flag
    - Register it with `tailwind-merge` or the merge stops working for it. `tailwind-merge` only knows _Tailwind_'s own conflict groups, so a custom `@utility` is invisible to it and two conflicting ones both survive — `extendTailwindMerge` in the same file that declares `cn()` is what teaches it the new group
4.  **Never win with the important flag:**
    - In v4 it is a suffix (`bg-red-500!`, not `!bg-red-500`)
    - Its presence in a diff signals a composition problem — usually a component that ignores `className`, or an `@apply` class outranking a utility
    - Against a generated component it signals the same thing and has a different fix: pass the utility through `className` and let `tailwind-merge` resolve it, never edit the file under `core/lib/shadcn/` and never add a defeating class beside it (see the view-structure rule)
5.  **`@reference` in separate stylesheets:**
    - `@apply` inside a _CSS_ module needs `@reference "…/app.css"` so the theme resolves; without it the build fails or silently drops the styles

**Incorrect (semantic class layer built with @apply, important flag to override it):**

```css
/* ./app/styles/app.css */
@import 'tailwindcss';

/* Bad: a component library made of class names */
@layer components {
  .btn {
    @apply rounded-md px-4 py-2 font-medium;
  }
  .btn-primary {
    @apply btn bg-primary text-primary-foreground;
  }
}
```

```tsx
// Bad: the utility loses to .btn-primary, so it needs the important flag
<button type="button" className="btn-primary bg-red-600!">
  Delete
</button>
```

**Correct (component owns the reuse, @utility for a real primitive, @apply only for foreign markup):**

```css
/* ./app/styles/app.css */
@import 'tailwindcss';

/* Good: a new primitive that composes with variants — hover:scrollbar-none works */
@utility scrollbar-none {
  scrollbar-width: none;
  &::-webkit-scrollbar {
    display: none;
  }
}

@layer base {
  /* Good: element defaults, in the one layer every utility still outranks */
  body {
    @apply bg-background text-foreground antialiased;
  }

  /* Good: the only markup we cannot restructure — CMS rich text. mt-8 is the declared
     exception to the mb-* convention in `react-core-best-practices`: the
     preceding sibling is not ours to space */
  .prose-cms h2 {
    @apply mt-8 text-xl font-semibold;
  }
}
```

```tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '~/core/lib/utils';

export const BUTTON_VARIANTS = cva(
  'inline-flex items-center gap-2 rounded-md font-medium [&_svg]:size-4',
  {
    variants: {
      variant: {
        primary: 'bg-primary text-primary-foreground',
        danger: 'bg-destructive text-destructive-foreground',
      },
      size: {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  },
);

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

// No important flag needed: tailwind-merge resolves the conflict
<Button type="button" variant="primary" className="bg-red-600">
  Delete
</Button>;
```

Reference: [Functions and directives](https://tailwindcss.com/docs/functions-and-directives)

### 2.5 Class Attribute Formatting & Order

**Impact (MEDIUM):** Sorting is not what settles a conflict — the stylesheet is, which is the whole reason `cn()` exists — so order itself is never worth a review comment once the formatter runs. What lifts this above cosmetics is everything around it: a plugin that never sees `cn()` leaves every composed string unsorted, contradictory utilities left inside one string resolve by stylesheet order instead of by intent, and a formatter let loose on generated folders fills diffs with noise that hides the real edits.

**Guidelines:**

1.  **The formatter owns the order:**
    - `prettier-plugin-tailwindcss` is the single authority; never sort by hand and never raise ordering as a review comment when it is configured
2.  **Configure it for composed strings:**
    - Set `tailwindStylesheet` to the main CSS entry point (v4 replaced the `tailwindConfig` option)
    - List helpers in `tailwindFunctions` (`cn`, `cva`) and custom attributes in `tailwindAttributes`, otherwise those strings go unsorted
    - Load it last in `plugins`: it rewrites what the plugins before it produced, and anything registered after it leaves the classes unsorted
    - `core/lib/shadcn/` stays in `.prettierignore`, so the formatter never rewrites generated code and any diff there is a deliberate edit (see the view-structure rule)
3.  **The plugin's distribution is the distribution:**
    - Never regroup a sorted string by hand into blocks of layout, spacing and colour — the plugin sorts inside each string literal and never across two, so splitting one literal into several is how a hand-made order survives review disguised as readability
    - What earns its own argument is meaning, not appearance: base classes in the first, conditionals after them
    - Where the call wraps is decided by the print width, which makes line breaks a formatting outcome and never a review topic
4.  **What review should still flag:**
    - Dead or contradictory utilities (`flex flex-col block`, `p-4 p-6`) — the formatter sorts, it does not deduplicate
    - Utilities that no longer apply after a refactor, left behind in the string

**Incorrect (unconfigured plugin, hand-grouped literals, contradictory utilities):**

```js
// ./prettier.config.js
// Bad: no stylesheet reference and no helper functions — cn() strings never get sorted
export default { plugins: ['prettier-plugin-tailwindcss'] };
```

```tsx
// Bad: hand-grouped into blocks the plugin can no longer sort against each other,
// with contradictory utilities and a leftover from a previous layout
<div
  className={cn(
    'block flex flex-col md:flex-row',
    'p-6 p-4',
    'text-sm',
    isActive && 'bg-accent',
  )}
>
  ...
</div>
```

**Correct (configured plugin, one base literal in the plugin's order, no dead utilities):**

```js
// ./prettier.config.js
export default {
  plugins: ['prettier-plugin-tailwindcss'],
  tailwindStylesheet: './app/styles/app.css',
  tailwindFunctions: ['cn', 'cva'],
  tailwindAttributes: ['containerClassName'],
};
```

```tsx
<div
  className={cn(
    // Good: one literal for the base, left in whatever order the plugin produced
    'flex flex-col gap-4 p-4 text-sm text-muted-foreground md:flex-row',
    isActive && 'bg-accent',
  )}
>
  ...
</div>
```

Reference: [prettier-plugin-tailwindcss](https://github.com/tailwindlabs/prettier-plugin-tailwindcss)

---

## 3. View Structure

### 3.1 View Structure & Generated Code

**Impact (HIGH):** The layer boundary itself — `core/`, `shared/`, and the direction imports flow — belongs to `react-core-best-practices`, because none of it changes with the renderer. What is left here is what only the web has: a view layer with a design-system folder inside it, and a generator that writes files into the project on its own terms. Both decay the same way, and the second decays faster — a structure the generator does not know about is undone the first time someone runs `shadcn add`.

**Guidelines:**

1.  **The view layer splits by responsibility:**
    - `components/` holds reusable presentation, with the design-system primitives under `components/ui/`
    - `components/ui/` is the generator's target and nothing else lands there; a component the project wrote sits beside it, not inside it
    - That route modules compose and never fetch is the core skill's rule; this one only fixes where the components they arrange live
2.  **The tooling has to agree with the structure:**
    - `tsconfig` resolves `~/*` to the source root, and every generator reads the alias from there
    - `components.json` decides where the next generated file lands, so its aliases are part of the structure and not a detail
    - Its `tailwind` block is part of the same contract: `cssVariables: true` is what makes generated components read the semantic tokens instead of arriving with the palette baked in, and `baseColor` seeds those variables at generation time (see the theme-tokens rule)
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

---

## 4. Performance & Robustness

### 4.1 Layout Stability & Overflow

**Impact (HIGH):** Layout shift and horizontal overflow are the two defects utility CSS makes easiest to ship. An `img` with no reserved box pushes the page down when it loads; `w-screen` scrolls sideways as soon as a scrollbar exists; a flex child with long content stretches past its container instead of truncating. All three are one utility away from being fixed, and all three are visible in review.

**Guidelines:**

1.  **Reserve the box before load:**
    - Every `img` declares `width` and `height` attributes, or sits in an `aspect-*` container with `object-cover`
    - Attributes plus `h-auto w-full` gives a responsive image that still reserves its ratio
2.  **Loading strategy:**
    - `loading="lazy"` below the fold; the LCP image stays eager and may be preloaded from the route
3.  **Viewport units:**
    - `w-screen` is `100vw`, which ignores the scrollbar and overflows — use `w-full`
    - `h-screen` fights the mobile dynamic toolbar — prefer `h-dvh` (or `min-h-dvh`)
    - Full-bleed inside a constrained container is a deliberate pattern, not a `w-screen` accident
4.  **Fixed heights on text:**
    - `h-[72px]` on a text container clips at other font sizes and languages — use `min-h-*` or let the content size the box
    - `line-clamp-2` bounds the text instead of bounding the box
5.  **Overflow needs a decision:**
    - A flex or grid child that can receive long content needs `min-w-0` — flex items default to `min-width: auto` and refuse to shrink below their content
    - Then choose the behavior: `truncate`, `line-clamp-*`, or `overflow-auto`
6.  **Async content reserves the same box:**
    - A skeleton or pending fallback must occupy the resolved content's box, otherwise the shift only moves from load time to resolve time

**Incorrect (unsized image, w-screen, fixed text height, unshrinkable flex child):**

```tsx
type Props = { file: Attachment };

export function AttachmentRow({ file }: Props) {
  return (
    <>
      {/* Bad: no dimensions — the page jumps when this loads */}
      <img src={file.previewUrl} className="w-full rounded-lg" />
      {/* Bad: 100vw ignores the scrollbar and scrolls the page sideways */}
      <section className="w-screen bg-muted py-12">
        <div className="mx-auto flex max-w-3xl items-center gap-3">
          {/* Bad: no min-w-0, so a long filename blows out the row instead of truncating */}
          <div className="flex-1">
            <p className="h-[24px] truncate">{file.name}</p>
          </div>
          <button type="button">Download</button>
        </div>
      </section>
    </>
  );
}
```

**Correct (reserved ratio, w-full, content-sized text, min-w-0 on the flex child):**

```tsx
type Props = { file: Attachment };

export function AttachmentRow({ file }: Props) {
  return (
    <>
      <img
        src={file.previewUrl}
        width={1200}
        height={630}
        loading="lazy"
        className="h-auto w-full rounded-lg"
      />
      <section className="w-full bg-muted py-12">
        <div className="mx-auto flex max-w-3xl items-center gap-3">
          <div className="min-w-0 flex-1">
            <p className="truncate">{file.name}</p>
          </div>
          <button type="button">Download</button>
        </div>
      </section>
      {/* Unknown intrinsic size: reserve the ratio instead */}
      <figure>
        <div className="mb-2 aspect-video overflow-hidden rounded-lg">
          <img src={file.previewUrl} className="size-full object-cover" />
        </div>
        <figcaption className="text-sm text-muted-foreground">
          Attachment preview
        </figcaption>
      </figure>
    </>
  );
}
```

Reference: [Cumulative Layout Shift](https://web.dev/articles/cls)

### 4.2 Source Detection & CSS Footprint

**Impact (MEDIUM):** _TailwindCSS_ only generates the classes it finds in the sources it scans. Two failure modes follow: a template the scanner never sees ships unstyled in production while looking fine locally, and a defensive safelist added to "fix" it inflates the stylesheet with thousands of unused rules. v4 detects sources automatically, so the correct fix is a targeted declaration, not a wider net.

**Guidelines:**

1.  **Automatic detection is the default:**
    - v4 has no `content` array to maintain; it scans the project, respects `.gitignore`, and skips binaries
    - Do not port a v3 `content` config forward out of habit
2.  **Register sources the scanner cannot reach:**
    - Anything outside the source root, or in a path `.gitignore` excludes — `node_modules` being the common one — needs `@source "…"`
    - This is why a component library installed from npm can ship with its classes missing
3.  **Narrow the scan when it is noisy:**
    - `@source not "…"` excludes vendor or generated directories rather than accepting the scan cost
4.  **Classes that live in data:**
    - When a class name comes from outside the codebase — a CMS field, an API response — declare exactly those with `@source inline("…")`
    - Prefer a static map from data value to a complete class string; inline declaration is the fallback when the value genuinely cannot be mapped

**Incorrect (v3 config ported forward, broad safelist to paper over a missing source):**

```js
// ./tailwind.config.js
// Bad: v4 does not need this, and the safelist ships ~1,500 unused rules
export default {
  content: ['./app/**/*.{ts,tsx}'],
  safelist: [
    { pattern: /(bg|text|border)-(red|green|amber|sky)-(100|500|800)/ },
  ],
};
```

```tsx
// Bad: the class comes from data and is built by interpolation
<span className={`bg-${status.color}-100 text-${status.color}-800`}>
  {status.label}
</span>
```

**Correct (automatic detection, explicit source registration, static map with a scoped inline fallback):**

```css
/* ./app/styles/app.css */
@import 'tailwindcss';

/* Good: a template the scanner cannot reach on its own */
@source "../../node_modules/@acme/ui/dist";

/* Good: exclude a generated directory instead of widening the net */
@source not "../../public/vendor";

/* Good: only these classes come from CMS data */
@source inline("bg-{success,warning,info} text-{success,warning,info}-foreground");
```

```tsx
const STATUS_STYLES = {
  error: 'bg-destructive text-destructive-foreground',
  ok: 'bg-success text-success-foreground',
  warn: 'bg-warning text-warning-foreground',
} as const;

// Good: complete static strings, nothing for the scanner to miss
<span className={STATUS_STYLES[status.kind]}>{status.label}</span>;
```

Reference: [Detecting classes in source files](https://tailwindcss.com/docs/detecting-classes-in-source-files)
