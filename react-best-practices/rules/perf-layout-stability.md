---
title: Layout Stability & Overflow
impact: HIGH
description: Prevents layout shift and horizontal overflow by sizing media intrinsically and avoiding viewport-width and fixed-height utilities.
tags: performance, layout, media
---

## Layout Stability & Overflow

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
