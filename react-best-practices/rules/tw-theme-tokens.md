---
title: Theme Tokens Over Arbitrary Values
impact: CRITICAL
description: Requires design decisions to live in the @theme block, and sizes the token layer to the project — one plain theme by default, the variable-backed semantic layer only where something reads it.
tags: tailwind, theme, tokens
---

## Theme Tokens Over Arbitrary Values

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
