---
title: One Component, One Block Name
impact: HIGH
description: Each component is named by its BEM block in one lowercase word, and its folder, its file and its root class share that name
tags: naming, components, bem, folders
---

## One Component, One Block Name

**Impact (HIGH):** When the folder says `logo` but the classes say `logo-usage`, people cannot find the CSS from the docs or the docs from the CSS.

**Guidelines:**

1. Folder `components/<block>/`, root class `.<block>`, documentation title `# <block>`, except the platform's `Cover` folder (see `name-bem-english`)
2. One word, no hyphens, in English (`businesscard`, `titleslide`, `letterhead`), because the artifact type requires component folders to be _JavaScript_ identifiers
3. Shared blocks are allowed only when documented in the overview (for example `quote` and `invoice` sharing `document`); each component keeps its own folder and title, and both use the shared root class (`components/quote/` → `.document`)
4. Rename every class of the block when the block name changes, and treat it as a major version

**Incorrect (folder and block disagree):**

```text
components/logo/preview.html   → <div class="logo-usage"> … </div>
```

**Correct (folder, file and block agree):**

```text
components/logo/README.md      → # logo
components/logo/preview.html   → <div class="logo"> <div class="logo__row"> …
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
