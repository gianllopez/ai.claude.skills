---
title: Correct Interactive Elements
impact: CRITICAL
description: Requires native button, a, and input elements for interactive behavior instead of click handlers attached to div or span.
tags: semantics, interaction, jsx
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
