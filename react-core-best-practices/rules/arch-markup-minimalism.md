---
title: Minimal Markup Depth
impact: HIGH
description: Removes wrapper elements that exist only to carry utility classes and collapses nesting that modern layout utilities make unnecessary.
tags: architecture, markup, structure
---

## Minimal Markup Depth

**Impact (HIGH):** Utility classes make it cheap to add a wrapper, so wrappers accumulate. Each one is another node to render, another indentation level to read, and another place where a future style can be attached at the wrong depth. Most of them are removable: their classes belong on the element they wrap.

The element changes with the renderer and the defect does not. A chain of `div`s that each add one class is the same chain of `View`s, costs the same extra nodes, and is removed the same way.

**Guidelines:**

1.  **A wrapper needs a job:**
    - Justified when it creates a layout context (a `flex` parent), a positioning context (`relative`), an overflow clip, or a stacking context
    - Not justified when its classes could sit on the child
2.  **Fragments over structural noise:**
    - Use `<>` when a wrapper exists only to satisfy a single-root requirement
3.  **Spacing comes from the parent:**
    - `gap-4` on the container, not a wrapper per child carrying `mb-4`. On the web `space-y-4` is the other spelling of the same idea
    - Margins per child leak into every context where the child is reused: the child decides its own spacing, so a second call site inherits a decision it never made
4.  **Margins flow in one direction:**
    - When a margin is unavoidable, it goes on the element **above** as `mb-*`, never on the element below as `mt-*`
    - One direction is what stops two elements from both claiming the same gap — `mb-4` above and `mt-4` below is eight units of space nobody asked for
    - The web has a second reason on top of that: adjacent vertical margins collapse, and which of the two survives is a rule nobody recalls under pressure. Under _React Native_ they simply add, which makes the defect more predictable and no less wrong
    - The exception is markup whose preceding sibling you do not control, which in practice only happens on the web — rich text from a _CMS_, where a heading has to reserve its own space above
5.  **Centering is one element:**
    - `items-center justify-center` on a single flex parent, or `mx-auto` on the child — not three nested containers, each contributing one axis
6.  **Passthrough wrappers are removable:**
    - A wrapper whose only class is `w-full` around a block element, or whose only class is `flex-1`, almost always belongs on the child instead

**Incorrect (five levels of wrappers, per-child margins, nested centering):**

```tsx
export function EmptyState() {
  return (
    // Bad: wrapper chain, each level adding one class
    <div className="w-full">
      <div className="flex">
        <div className="mx-auto">
          <div className="flex flex-col items-center">
            <div className="mb-2">
              <h2 className="text-lg font-semibold">No reports yet</h2>
            </div>
            <div className="mb-4">
              <p className="text-sm text-muted-foreground">
                Create one to get started.
              </p>
            </div>
            <div>
              <Button>New report</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

**Correct (React DOM) — one layout container, gap for spacing, classes on the elements themselves:**

```tsx
export function EmptyState() {
  return (
    <div className="flex flex-col items-center gap-2">
      <h2 className="text-lg font-semibold">No reports yet</h2>
      {/* Good: the extra space before the button belongs to the element above it */}
      <p className="mb-2 text-sm text-muted-foreground">
        Create one to get started.
      </p>
      <Button>New report</Button>
    </div>
  );
}
```

**Correct (React Native) — the same single container, the same one-directional margin:**

```tsx
export function EmptyState() {
  return (
    <View className="items-center gap-2">
      <Text className="text-lg font-semibold">No reports yet</Text>
      {/* Good: same convention, and here the two margins would have added up
          rather than collapsed — the wrong version is simply eight units */}
      <Text className="mb-2 text-sm text-muted-foreground">
        Create one to get started.
      </Text>
      <Button>New report</Button>
    </View>
  );
}
```

Reference: [Styling with utility classes](https://tailwindcss.com/docs/styling-with-utilities)
