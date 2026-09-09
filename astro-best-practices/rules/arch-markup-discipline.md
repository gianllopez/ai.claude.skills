---
title: Markup Discipline Under the v7 Compiler
impact: HIGH
description: Requires well-formed, semantically valid markup now that the v7 Rust compiler treats unclosed tags as build errors, stops auto-correcting invalid nesting, and compresses whitespace with JSX rules.
tags: markup, html, compiler, v7, build
---

## Markup Discipline Under the v7 Compiler

**Impact (HIGH):** For most of _Astro_'s history the compiler was forgiving: an unclosed `<div>` was accepted, invalid nesting was silently restructured into something valid, and the page rendered close enough to what the author meant that nobody investigated. In v7 the _Rust_ compiler is the default and the only option, and it is strict — **unclosed tags are errors** and semantically invalid _HTML_ is **no longer auto-corrected**. So markup that a codebase has carried for years, rendering fine, can fail the build on an upgrade with no change to the file that contains it. The whitespace default moved at the same time: `compressHTML` is now `'jsx'`, which strips space using _JSX_ rules, so the space between two inline elements that used to survive can disappear and run two words together. Both are cheap to satisfy deliberately and confusing to diagnose after the fact.

**Guidelines:**

1.  **Close every tag:**
    - Including the ones _HTML_ historically allowed to be left open — `<li>`, `<p>`, `<td>`, `<tr>`, `<option>` — because the compiler no longer infers where they end
    - Void elements are self-closed or written as single tags consistently: `<br />`, `<img ... />`, `<meta ... />`
    - Component tags follow the same rule, and an unclosed component is the version of this that is hardest to spot in a long template
2.  **Respect nesting rules instead of relying on repair:**
    - A `<div>` inside a `<p>`, a `<p>` inside a `<p>`, block content inside inline elements, a `<td>` outside a `<tr>` — previously restructured, now left as written or rejected
    - Interactive elements do not nest: a `<button>` inside an `<a>`, an `<a>` inside an `<a>`
    - Table structure is explicit — `<thead>`, `<tbody>`, `<tr>`, `<td>` — rather than assumed
3.  **Be explicit about significant whitespace:**
    - Under `compressHTML: 'jsx'`, the space between `</a>` and the next inline element on a separate line is removed, so `<a>Read</a> <span>more</span>` split across lines can render as "Readmore"
    - Where a space is meaningful, write it: `{' '}` between the elements, or keep them on one line
    - The failure is visual and easy to miss in review, so it shows up on pages with inline links inside paragraphs first
4.  **Reserved filenames are part of the routing surface:**
    - `src/fetch.ts` (and `src/fetch.js`) is reserved in v7 for advanced routing; a project using that path for its own helper must rename it or set `fetchFile`
    - This is the kind of collision that produces a confusing error rather than an obvious one, so it is worth knowing before the upgrade
5.  **Let the build be the check:**
    - This rule needs no separate linter — the compiler now enforces most of it, which is the change
    - The practical consequence is upgrade sequencing: run the build early against real templates rather than discovering the strictness at deploy time

**Incorrect (markup the old compiler repaired, and a space the new default removes):**

```astro
---
// src/components/ArticleList.astro
---

<ul>
  <!-- Bad: unclosed <li> — previously inferred, now a build error -->
  <li><a href="/blog/one">One</a>
  <li><a href="/blog/two">Two</a>
</ul>

<!-- Bad: a div cannot live inside a p. Previously restructured, now left
     invalid -->
<p>
  Introduction text.
  <div class="callout">A note about the above.</div>
</p>

<!-- Bad: interactive elements nested -->
<a href="/pricing"><button>See pricing</button></a>

<p>
  Read the
  <a href="/guide">migration guide</a>
  <em>before</em> starting.
</p>
<!-- Under compressHTML: 'jsx' the newline between the inline elements is not a
     space, so this renders as "…migration guidebefore starting." -->
```

**Correct (well-formed, correctly nested, whitespace stated):**

```astro
---
// src/components/ArticleList.astro
---

<ul>
  <li><a href="/blog/one">One</a></li>
  <li><a href="/blog/two">Two</a></li>
</ul>

<p>Introduction text.</p>
<aside class="callout">A note about the above.</aside>

<a href="/pricing" class="button">See pricing</a>

<p>
  Read the <a href="/guide">migration guide</a>{' '}
  <em>before</em> starting.
</p>
```

Reference: [Upgrade to Astro v7](https://docs.astro.build/en/guides/upgrade-to/v7/)
