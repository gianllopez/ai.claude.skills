---
title: Correct Interactive Elements
impact: CRITICAL
description: Requires native button, a, and input elements for interactive behavior instead of click handlers attached to div or span.
tags: semantics, interaction, html
---

## Correct Interactive Elements

**Impact (CRITICAL):** An interactive `div` throws away behavior the browser provides for free — keyboard activation, form submission, link context menus, middle-click and modifier-click navigation, framework prefetching, and `:disabled` state. Rebuilding any of it costs more code than using the right element, and the reimplementation drifts the moment someone edits it.

**Guidelines:**

1.  **Element by intent:**
    - Navigation that changes the URL is an anchor, and it carries a real `href`
    - An action that stays on the page is a `button`
    - An anchor without `href` is not a link — if there is no destination, it is a `button`
2.  **Button type is mandatory:**
    - Every `button` inside a `form` declares `type`; the default is `submit`, so an unmarked action button silently submits the form
    - Wrapping it in a component changes nothing: a button component with no `type` forwarded is still a submit button
3.  **No click handlers on inert elements:**
    - A click/tap handler on `div`, `span`, or `li` as the only interaction path is a defect, not a style choice
    - Utilities like `cursor-pointer` make a `div` look interactive without making it interactive
4.  **Disabled is an attribute:**
    - Use the `disabled` attribute so the control stops firing; `opacity-50 pointer-events-none` only hides the affordance and leaves the handler reachable by other means (a parent listener, a keyboard shortcut)
    - Style the real state with the `disabled:` variant

**Incorrect (clickable div, untyped form button, fake disabled state):**

```html
<form>
  <!-- Bad: a div is not a control -->
  <div
    class="cursor-pointer rounded-md bg-primary px-4 py-2"
    onclick="handleSave()"
  >
    Save
  </div>
  <!-- Bad: no type — a button inside a form still defaults to submit -->
  <button onclick="openHelp()">Help</button>
  <!-- Bad: disabled is only painted, the handler still runs -->
  <button onclick="publish()" class="pointer-events-none opacity-50">
    Publish
  </button>
</form>
```

**Correct (native controls, explicit type, real disabled attribute):**

```html
<form>
  <button type="submit">Save</button>
  <button type="button" onclick="openHelp()">Help</button>
  <!-- Good: the attribute stops the handler, and disabled: carries the styling -->
  <button
    type="button"
    onclick="publish()"
    disabled
    class="disabled:pointer-events-none disabled:opacity-50"
  >
    Publish
  </button>
</form>
```

Reference: [The button element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button)
