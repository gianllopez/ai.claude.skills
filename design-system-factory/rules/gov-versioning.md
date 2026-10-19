---
title: Version Every Change and Record It in the Changelog
impact: HIGH
description: Renaming or removing a token, class or file is major, adding is minor and fixing is patch, and each version is published with a dated Spanish changelog entry that names every touched class, file and asset
tags: governance, versioning, semver, changelog, documentation
---

## Version Every Change and Record It in the Changelog

**Impact (HIGH):** Derived designs depend on names: an unannounced rename breaks them silently, and a vague changelog cannot tell them what to update.

**Guidelines:**

1. Major: rename or remove a token, class, component or file (including deleting an unused icon or a duplicate logo)
2. Minor: add a token, class, component, asset or rule
3. Patch: fix a value, a wording, a position or a bug without changing names
4. Group the changes of one request in one version; adjustments stay in the same version only while it is unpublished; once published, every adjustment is a new version
5. Each version gets one Spanish entry in `changelog.md`, newest first, headed `## <version> · <day> de <month> de <year>`; a major adds one line saying what breaks
6. One bullet per change naming the classes, files and assets involved as inline code; removals name their replacement ("Sale `folder__icon` y entra `folder__bullet`")
7. Update the index `lastChange` (author, date, note with the version)
8. Never rewrite past entries: a change reverted before it is published leaves no version and no entry; reverting a published change is a new version with its own entry, classified like any other change

**Incorrect (removed classes published as a patch, with a vague entry):**

```md
## 7.1.1

- Mejoras en la carpeta.
```

**Correct (a major with a precise entry):**

```md
## 8.0.0 · 15 de octubre de 2026

Cambio mayor: se eliminan clases de `folder` y tres archivos del grupo `icons`.

- `folder`, bolsillo: misma distribución, sin íconos; cada dato lleva como viñeta un cuadrado `primary-500` de 1.6 mm. Sale `folder__icon` y entra `folder__bullet`.
- Íconos: salen `icon__call--outline.svg`, `icon__sms--outline.svg` e `icon__global--outline.svg`; el grupo vuelve a 25.
```

Reference: [Semantic Versioning](https://semver.org/) · [Keep a Changelog](https://keepachangelog.com/)
