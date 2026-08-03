---
title: State-Driven Styling With Data Attributes
impact: HIGH
description: Styles component state from data-* attributes with variants instead of toggling ad-hoc class strings in JavaScript.
tags: tailwind, state, jsx
---

## State-Driven Styling With Data Attributes

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
    - `not-*` inverts without a second branch; `group` and `peer` are relationship variants and live in the responsive-and-variants rule
4.  **Never mutate classes imperatively:**
    - `element.classList.add(...)` or assigning `className` in an effect puts design state outside the render output
5.  **Boolean data attributes must be absent, not `"false"`:**
    - `data-active="false"` still matches the `data-active:` variant — the variant tests for presence
    - Render `data-active={isActive || undefined}` so the attribute disappears when false

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
