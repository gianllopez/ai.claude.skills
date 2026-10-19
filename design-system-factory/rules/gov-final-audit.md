---
title: Run a Final Audit Before Closing the System
impact: HIGH
description: Before declaring the system finished, sweep files, classes, assets and conventions, fix every finding and publish the result as one version
tags: governance, audit, cleanup, conventions
---

## Run a Final Audit Before Closing the System

**Impact (HIGH):** Small inconsistencies (an unused class, a lone modifier, a gray border on a tint, a slogan with a period) are invisible one by one and obvious together.

**Guidelines:**

1. Files: compare the published list with the local tree; every file is expected (platform files, sources, generated files)
2. Assets: every index record is used, except the logo variant set of `brand-logo-variants`, and documented; blob count equals record count
3. Classes: every class in the bundle appears in a preview, the script or a component file; every documented class exists; no lone modifiers; every component uses its own block
4. Conventions: _BEM_ English names; Spanish docs; italic proper nouns; values as inline code; one form of address; no shadows; tinted borders at 200; neutral control borders; logo and print minimums; icons from the library or registered as custom; slogan form; templates only; 4px grid (whole spacing steps, no `radius-md`, print sizes in multiples of 3pt); measured contrast for every text and icon pair
5. Claims: every sentence in the overview that says "cada", "todos" or a count is checked against the files
6. Fix, render the affected previews, publish one version and report findings, fixes and documented exceptions

**Incorrect (closing without a sweep):**

```text
User: "¿Ya todo está listo?"
Agent: "Sí." (an unused class, a 14px symbol and a period after the slogan remain)
```

**Correct (sweep, fix, report):**

```text
Audit 9.0.0: 47 assets = 47 blobs · chart__delta now used with its modifiers · logo-usage → logo ·
checkbox tick from the icon library · borders added to card__icon, empty__icon, tabs__count,
newsletter footer and tooltip · report__symbol 12pt → 15pt · slogan without period ·
exceptions documented (Cover folder, shared document block, folder--outside/--inside hooks)
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
