---
title: Minimal Markup Depth
impact: HIGH
description: Removes wrapper elements that exist only to carry utility classes and collapses nesting that modern layout utilities make unnecessary.
tags: architecture, markup, structure
---

## Minimal Markup Depth

**Impact (HIGH):** Utility classes make it cheap to add a wrapper, so wrappers accumulate. Each one is another node to render, another indentation level to read, and another place where a future style can be attached at the wrong depth. Most of them are removable: their classes belong on the element they wrap.

**Guidelines:**

1.  **A wrapper needs a job:**
    - Justified when it creates a layout context (a `flex`/`grid` parent), a positioning context (`relative`), an overflow clip, or a stacking context
    - Not justified when its classes could sit on the child
2.  **Fragments over structural noise:**
    - Use `<>` when a `div` exists only to satisfy a single-root requirement
3.  **Spacing comes from the parent:**
    - `flex gap-4` or `space-y-4` on the container, not a wrapper per child carrying `mb-4`
    - Margins per child leak into every context where the child is reused
4.  **Margins flow with the document:**
    - When a margin is unavoidable, it goes on the element **above** as `mb-*`, never on the element below as `mt-*`
    - One direction throughout keeps two elements from both claiming the same gap, and keeps adjacent vertical margins from collapsing in ways nobody predicted
    - The exception is markup whose preceding sibling you do not control — rich text from a _CMS_, where a heading has to reserve its own space above
5.  **Centering is one element:**
    - `grid place-items-center`, `flex items-center justify-center`, or `mx-auto` — not three nested containers
6.  **Passthrough wrappers are removable:**
    - `<div className="w-full">` around a block element, or a wrapper whose only class is `flex-1`, almost always belongs on the child

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

**Correct (one layout container, gap for spacing, classes on the elements themselves):**

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

Reference: [Styling with utility classes](https://tailwindcss.com/docs/styling-with-utilities)
