# File Formats

Exact formats and checklists for every file a skill may contain. Copy the matching template from `templates/`, then validate against the checklist here.

---

## Prose conventions

Apply these across every markdown file in a skill:

- Write in _English_
- Italicize proper nouns / product names in prose (`_Django_`, `_Docker_`); leave them plain in headings, code, link text, and frontmatter
- Do not end enumeration items (bullet, numbered, or checklist) with a period; keep periods only inside running-prose paragraphs
- Keep generated artifacts (`AGENTS.md`) out of manual edits

---

## `SKILL.md` (all tiers — required)

The only file the official spec requires. _YAML_ frontmatter + a markdown body.

```markdown
---
name: <skill-name>
description: <what it does AND when to use it; trigger words>
license: MIT # optional (Tier 2/3 convention)
metadata: # optional (Tier 2/3 convention)
  author: <handle>
  version: <x.y.z>
---

# <Title>

<Body: instructions, when-to-apply, quick reference>
```

**Frontmatter rules (enforced by the platform):**

- `name`: chosen by the user (never generated) · lowercase letters, numbers, hyphens only · ≤ 64 chars · no _XML_ tags · must not contain `anthropic` or `claude`
- `description`: non-empty · ≤ 1024 chars · no _XML_ tags · must say what the skill does and when _Claude_ should use it (this is the text _Claude_ matches against)

**Checklist:**

- [ ] `name` matches the folder name
- [ ] `description` includes both capability and trigger conditions
- [ ] Body keeps heavy detail in `references/` (Tier 2/3), not inline
- [ ] Written in _English_ (collection convention)

---

## `metadata.json` (Tier 2/3)

Human/tooling metadata. Not read by the platform; it is the single source for the compiled `AGENTS.md` header in _Tier 3_.

```json
{
  "version": "1.0.0",
  "author": "<Name>",
  "date": "<Month Year>",
  "abstract": "<1–3 sentence summary of scope and intent>",
  "references": ["<url>", "..."]
}
```

**Checklist:**

- [ ] `version` matches `SKILL.md` frontmatter `metadata.version`
- [ ] `date` is absolute (`Month Year`), not relative
- [ ] `abstract` describes scope and intent, not implementation trivia

---

## `README.md` (Tier 2/3)

Human-facing overview. Describes the skill's purpose, its file structure, and how to use/maintain it. For _Tier 3_ it also documents the authoring workflow (creating a rule, recompiling).

**Checklist:**

- [ ] Lists the file structure with one-line descriptions
- [ ] States how to use the skill
- [ ] Tier 3: documents "create a rule" and "recompile `AGENTS.md`" steps and marks `AGENTS.md` as generated

---

## `rules/` (Tier 3)

### `rules/_sections.md`

Index of all rules, grouped by section, linking each rule file. Keep it in sync with the actual rule set and with the section order used to compile `AGENTS.md`.

### `rules/_template.md`

A blank rule scaffold authors copy. Establishes the strict rule shape.

### `rules/<prefix>-<name>.md`

One rule per file. Filenames start with a category prefix (`arch-`, `conf-`, …) so related rules sort together.

```markdown
---
title: <Title>
impact: <CRITICAL | HIGH | MEDIUM | LOW>
description: <one-line summary>
tags: <comma, separated>
---

## <Title>

**Impact (<LEVEL>):** <why it matters>

**Guidelines:** <optional numbered list>

**Incorrect (<what's wrong>):**

​`<lang>
<bad example>
​`

**Correct (<what's right>):**

​`<lang>
<good example>
​`

Reference: [<label>](url)
```

**Checklist per rule:**

- [ ] Filename `<prefix>-<name>.md`; first heading is `## <Title>`
- [ ] Frontmatter has `title`, `impact`, `description`, `tags`
- [ ] Has clear _Incorrect_ and _Correct_ examples
- [ ] Registered in `rules/_sections.md`
- [ ] Proper nouns / product names italicized in prose (`_Django_`, `_Docker_`, …); left plain in headings, code, link text, and frontmatter

---

## `AGENTS.md` (Tier 3 — generated)

The full compiled document: _Vercel_-style header (title, version, Note, Abstract), a derived table of contents, and every rule expanded inline under numbered sections. Never hand-edit. See `compilation.md` for the exact format and how it is produced.
