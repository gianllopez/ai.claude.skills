---
title: State-Driven Styling With Data Attributes
impact: HIGH
description: Styles component state from data-* attributes with variants instead of toggling ad-hoc class strings in JavaScript.
tags: tailwind, state, css
---

## State-Driven Styling With Data Attributes

**Impact (HIGH):** When state lives in a `data-*` attribute, the whole variant matrix is visible on one line of markup and the browser applies it. When state is expressed by swapping class strings imperatively, presentation scatters across event handlers and effects, a merge helper cannot resolve conflicts it never sees, and the rendered class list becomes impossible to predict while reading a diff.

**Guidelines:**

1.  **Expose state as data:**
    - Render `data-state="open"` or a boolean `data-active` and style with `data-[state=open]:` / `data-active:` variants
    - This is the convention headless UI libraries already emit — many write `data-state`, `data-disabled`, `data-side` and `data-orientation` on their own primitives, so styling one means writing the variant, never adding a parallel boolean of the project's own to track what the component already announces
2.  **Descendants read the parent:**
    - Mark the container `group` and let children use `group-data-[state=open]:rotate-180`
    - Do not thread a boolean through the tree whose only purpose is styling a descendant
3.  **Structural conditions:**
    - `has-*` styles a parent from its children (`has-[:checked]:border-primary`), removing wrappers that existed only to receive a class
    - `not-*` inverts without a second branch; `group` and `peer` are relationship variants and live in the variants-and-responsive rule
4.  **Never mutate classes imperatively:**
    - `element.classList.add(...)` or reassigning a class attribute from a script or effect puts design state outside the markup that is supposed to describe it
5.  **Boolean data attributes must be absent, not `"false"`:**
    - `data-active="false"` still matches the `data-active:` variant — the variant tests for presence
    - Render the attribute only when true, so it disappears entirely when false
6.  **An arbitrary variant is a selector living in a class attribute:**
    - `[&>*:nth-child(3)]:mt-0` styles by position, so it breaks the moment an element is inserted, and nothing in the markup says why the third child is special
    - The legitimate case is a slot this component does not render — `[&_svg]:size-4` on a button that accepts any icon
    - A cluster of them on one element is a structural finding: the child needs a component or a prop, not a longer selector
    - This is the same defect as styling from a script, one level down: the rule lives in the class attribute instead of in the markup, so nothing at the call site says why it applies

**Incorrect (class toggling from a script, a boolean threaded down only to pick a class, data-active="false"):**

```html
<ol>
  <li>
    <!-- Bad: "false" still matches data-active: -->
    <button type="button" data-active="false" class="data-active:bg-accent">
      Step one
    </button>
  </li>
</ol>
<div id="progress-bar"></div>

<script>
  // Bad: presentation applied outside the markup, from an imperative call
  document
    .querySelector('#progress-bar')
    .classList.toggle('hidden', currentIndex === 0);
</script>
```

**Correct (state on the element, variants do the styling, attribute omitted when false):**

```html
<ol>
  <!-- Good: not-* dims every step that is not the current one, with no
       second branch and no extra attribute to carry the negation -->
  <li
    data-state="current"
    class="group flex items-center gap-3 not-data-[state=current]:opacity-60"
  >
    <button
      type="button"
      data-active
      class="flex w-full items-center justify-between data-active:bg-accent"
    >
      Step one
      <!-- Good: the child reads the group's state -->
      <svg class="opacity-0 group-data-[state=complete]:opacity-100">
        <!-- check -->
      </svg>
    </button>
  </li>
  <li
    data-state="upcoming"
    class="group flex items-center gap-3 not-data-[state=current]:opacity-60"
  >
    <!-- Good: attribute is absent when inactive, instead of data-active="false" -->
    <button
      type="button"
      class="flex w-full items-center justify-between data-active:bg-accent"
    >
      Step two
    </button>
  </li>
</ol>
```

```html
<!-- Good: a headless accordion primitive already announces its own state, so
   there is nothing to mirror — the variant reads what the library writes,
   and has-* styles the container from its own child instead of a wrapper
   that existed to carry a class -->
<div class="group border-b" data-value="billing">
  <button data-state="open" class="data-[state=open]:text-primary">
    Billing
    <svg class="transition-transform group-data-[state=open]:rotate-180">
      <!-- chevron -->
    </svg>
  </button>
  <div>Billing content</div>
</div>

<label class="rounded-md border p-3 has-[:checked]:border-primary">
  <input type="checkbox" />
  <span>Enable notifications</span>
</label>
```

Reference: [Styling based on data attributes](https://tailwindcss.com/docs/hover-focus-and-other-states#data-attributes)
