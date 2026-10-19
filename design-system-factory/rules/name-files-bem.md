---
title: Name Asset Files as block__element--modifier
impact: CRITICAL
description: Every asset file follows `block__element--modifier.ext`, with `key_value` modifiers for measures
tags: naming, assets, files, bem
---

## Name Asset Files as block\_\_element--modifier

**Impact (CRITICAL):** Assets are referenced from code, docs, manifests and print shops. A consistent pattern lets anyone predict the file name for a variant without opening a folder.

**Guidelines:**

1. Block = family (`logo`, `icon`, `pattern`, `print`, `image`, `font`)
2. Element = concrete piece (`primary`, `symbol`, `businesscard`, `lexend`)
3. Modifier = version (`gradient`, `flat`, `negative`, `outline`, `400`); a measured value uses `key_value` (`--width_512`); several modifiers go version first, then measured values (`--gradient--width_112`)
4. Print files encode the format, as its standard name (`dl`, `letter`) or width × height in mm (`85x55`, `229x305`): `print__businesscard--85x55.pdf`, `print__envelope--dl.pdf`
5. Icons keep the library name in kebab-case: `icon__chevron-down--outline.svg`

**Incorrect (free-form names):**

```text
Logo Final (2).svg
favicon32.png
tarjeta presentacion.pdf
```

**Correct (_ASKIT_ reference):**

```text
logo__primary--gradient.svg
logo__symbol--gradient--width_112.png
font__lexend--600.woff2
print__folder--229x305.pdf
```

Reference: [BEM naming](https://getbem.com/naming/)
