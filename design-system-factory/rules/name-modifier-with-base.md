---
title: Never Use a Modifier Without Its Base
impact: MEDIUM
description: A modifier class always accompanies its block or element class, and a base class defined in CSS must be used
tags: naming, bem, modifiers, css
---

## Never Use a Modifier Without Its Base

**Impact (MEDIUM):** A lone modifier hides which element it modifies and leaves the base rule unused, which the final audit then reports as dead code.

**Guidelines:**

1. Write `class="chart__delta chart__delta--negative"`, never only the modifier
2. If the base class carries no styles, still keep it in markup when the modifier is defined on it
3. Modifiers with no CSS of their own are allowed only as documented hooks, listed under **Clases** in the component file (for example `folder--outside` marking a face)
4. States the markup already expresses (`disabled`, `aria-selected`, `aria-expanded`, `aria-current`) are styled from the attribute, not with a modifier

**Incorrect (modifier alone):**

```html
<text class="chart__value chart__delta--negative">−8 %</text>
```

**Correct (base plus modifier):**

```html
<text class="chart__value chart__delta chart__delta--negative">−8 %</text>
```

Reference: [BEM naming](https://getbem.com/naming/)
