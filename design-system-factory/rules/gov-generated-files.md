---
title: Regenerate Generated Files Before Every Publish
impact: MEDIUM
description: Files generated from the sources (tokens stylesheet, manifest, API pages, the generated tail of the overview) are rebuilt on every publish, and the index is published last
tags: governance, publishing, generated files, artifacts
---

## Regenerate Generated Files Before Every Publish

**Impact (MEDIUM):** Generated files update only when the system is saved from its page; publishing sources without them leaves the manifest and API pages out of date.

**Guidelines:**

1. The system lives in a claude.ai artifact of the Design System type; publishing means updating that artifact, with the index (`design-system.json`) as its main file
2. Edit only sources: the overview body (`README.md`), component files, `tokens.json`, `components/bundle.css`, `components/bundle.js`, asset group files, `changelog.md`, `code/tailwind__theme.css` and the index
3. Regenerate from the sources before publishing: `tokens.css` (compiled from `tokens.json`), `manifest.json`, `api/**` and the generated tail of the overview
4. Publish changed sources plus regenerated files in one call, with the index as the main file (sent last)
5. Read the published index back to confirm records, then clean up replaced blobs

**Incorrect (hand-edited manifest):**

```text
edit manifest.json by hand → publish only bundle.css → api/components/*.md describe the old classes
```

**Correct (regenerate then publish):**

```text
regenerate tokens.css (from tokens.json), manifest.json, api/** and the README tail with a regeneration script
publish: changed sources + regenerated files, index (design-system.json) last
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
