---
title: Theme Tokens Over Arbitrary Values
impact: CRITICAL
description: Requires design decisions to live in the @theme block so utilities resolve to system tokens instead of one-off arbitrary values.
tags: tailwind, theme, tokens
---

## Theme Tokens Over Arbitrary Values

**Impact (CRITICAL):** Every arbitrary value is a design decision made outside the design system. Once `bg-[#1d4ed8]` appears in three files, the brand color has no single definition, a theme change becomes a find-and-replace, and dark mode has nothing to swap. In v4 the theme is the stylesheet: tokens declared in `@theme` generate utilities _and_ expose CSS variables, so there is no reason to hardcode.

**Guidelines:**

1.  **Declare once, in `@theme`:**
    - Colors, radii, fonts, breakpoints, and shadows live in the `@theme` block of the main stylesheet
    - A token generates its utilities automatically: `--color-primary` yields `bg-primary`, `text-primary`, `border-primary`
    - The spacing scale is the exception and is never redeclared: `--spacing` is _Tailwind_'s and the design works in its steps, so a diff that redefines it is changing every margin, gap and size in the project at once
2.  **Two token layers, and they do not compete:**
    - `shadcn init` writes the semantic layer and every generated component reads it, so it is not optional decoration: `--background` / `--foreground` for the page, `--card` and `--popover` for raised surfaces, `--primary` and `--secondary` for actions, `--muted` and `--muted-foreground` for de-emphasised fills and text, `--accent` for hover and selection, `--destructive` for danger, and `--border` / `--input` / `--ring` for edges
    - Each pair travels together: a `--*-foreground` is the contrast partner of its surface, so painting `bg-muted` and then picking the text colour by hand breaks the pair the generator maintains
    - The brand colour is declared there and nowhere else: our own components paint with `bg-primary` too, which is the only thing that keeps them in step with every generated one
    - A parallel brand scale is a second source of truth for one decision — the day `--primary` changes, everything painted with the other name quietly stops matching
    - A plain `@theme` sits beside it for what the generator does not decide: the font, type steps, radii of our own
    - Roles the generator has no token for — success, warning, info — are declared the same way it declares its own, as a surface and its foreground, so they behave under `.dark` like everything else. Reaching for `bg-green-100` instead leaves a status colour that no theme can reach
3.  **Turn on the switch that makes all of this real:**
    - `components.json` decides what the generator writes: with `cssVariables: false` every component it installs arrives with the palette baked in — `bg-neutral-900` instead of `bg-primary` — and the semantic layer stops existing
    - `baseColor` picks the neutral ramp those variables are seeded from, and it is read at generation time, so changing it later rewrites nothing that already exists
    - Both belong to the structure, not to the setup ceremony (see the folder-structure rule)
4.  **Reach for the token that names the role:**
    - Muted text is `text-muted-foreground`; a hover or selected row is `bg-accent`; an error message is `text-destructive`. A step off the neutral ramp standing in for any of them is the finding
    - The palette is not arbitrary — every ramp step is a real theme token — which is exactly why this slips through: it looks tokenised and still hardcodes a decision the semantic layer already owns
    - The test is whether the value survives a theme change. A role token does; a ramp step does not
5.  **Arbitrary values are a review flag:**
    - `bg-[#1d4ed8]`, `p-[13px]`, `text-[15px]` mean one of two things: the token exists and was not used, or the token is missing and must be added
    - Legitimate use is genuinely one-off geometry with no reuse — `grid-cols-[auto_1fr]`, `mask-[url(...)]`, a third-party magic offset
    - A color is almost never one-off, and a spacing value never is: `p-[13px]` means the markup drifted off the scale, and the fix is the nearest step — not a token of its own
6.  **A token outlives the diff that stops using it:**
    - The diff that removes a token's last consumer removes the token too — leaving it behind is how a stylesheet accumulates values nobody can tell apart from the live ones
    - Declaring ahead of use is not the same defect and is not a finding: a design system defines its scale before every step has a consumer, and a token waiting for its first caller is design, not debt
    - The generator's tokens are never pruned on either count — `--chart-*` and `--sidebar-*` sit unused until the component that needs them is installed, and removing them breaks the next `shadcn add`
    - The reverse direction is a finding: a value repeated across files and declared nowhere is a token that was never written down
7.  **Do not bypass the utility layer:**
    - `style={{ color: 'var(--color-primary)' }}` skips variants, merge resolution, and the sort order
    - The `style` prop is reserved for values computed at runtime (an animated transform, a measured offset)
8.  **v4 configuration:**
    - There is no `tailwind.config.js` by default; the theme is CSS
    - A JS config is reintroduced only through `@config` when a legacy plugin requires it
    - `@theme inline` is what makes the semantic layer work: it compiles `bg-background` down to `var(--background)` instead of copying the value, so the utility still follows the variable when `.dark` redefines it — a plain `@theme` freezes whatever the variable held at build time

**Incorrect (hardcoded values scattered across components, inline CSS variable):**

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

**Correct (tokens declared in the theme, utilities resolve to them):**

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

  /* Ours: the status roles the generator ships no token for */
  --success: oklch(0.55 0.14 150);
  --success-foreground: oklch(0.985 0 0);
  --warning: oklch(0.68 0.15 75);
  --warning-foreground: oklch(0.145 0 0);
  --info: oklch(0.58 0.15 240);
  --info-foreground: oklch(0.985 0 0);
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
  --warning: oklch(0.75 0.15 75);
  --warning-foreground: oklch(0.145 0 0);
  --info: oklch(0.65 0.15 240);
  --info-foreground: oklch(0.145 0 0);
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
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
  --color-info: var(--info);
  --color-info-foreground: var(--info-foreground);
}

/* Ours: the decisions the generator does not make. No --spacing here — the
   scale is Tailwind's and the design works in its steps */
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
        'rounded-badge border border-primary bg-primary px-3 py-1 text-badge text-primary-foreground',
        className,
      )}
      {...props}
    />
  );
}
```

Reference: [Theme variables](https://tailwindcss.com/docs/theme)
