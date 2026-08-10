---
name: skill-factory
description: Guide and templates for authoring new Agent Skills in this collection. Use when creating a new skill, scaffolding a skill's folder structure, deciding a skill's complexity tier, standardizing an existing skill, or setting up the rules/AGENTS.md compilation procedure. Triggers on "create a skill", "new skill", "scaffold a skill", "skill structure", "skill tier".
license: MIT
metadata:
  author: gianllopez
  version: 2.0.0
---

# Skill Factory

Authoring standard for the skills in this collection. It defines three complexity tiers, the exact file formats each tier uses, and the compilation procedure for rule-based skills — so every skill is organized, scalable, and consistent.

## When to Apply

- Creating a brand-new skill from scratch
- Choosing the right folder structure for a skill's complexity
- Standardizing or upgrading an existing skill (e.g. promoting a growing procedural skill to a compiled one)
- Setting up or regenerating a rule-based skill's `AGENTS.md`

## What is actually required

Per the official [Agent Skills spec](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview), a skill needs only a `SKILL.md` with _YAML_ frontmatter (`name` + `description`). Everything else (`metadata.json`, `README.md`, `rules/`, `AGENTS.md`) is a convention this collection adopts — adapted from [Vercel Labs' agent-skills](https://github.com/vercel-labs/agent-skills) — to keep larger skills maintainable. The tiers below layer that convention on top of the spec by complexity.

## Choose a Tier

| Tier           | Use when…                                                                                      | Files                                                                       | Examples                                                                        |
| -------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| 1 · Minimal    | One stable instruction/procedure, no assets, no versioning                                     | `SKILL.md`                                                                  | `commit`                                                                        |
| 2 · Procedural | A workflow or tool integration; may bundle helper scripts; benefits from versioning + a README | `SKILL.md`, `metadata.json`, `README.md`, optional `scripts/`, `templates/` | `notion`, `audit`, `review`, `skill-factory`                                    |
| 3 · Compiled   | A large, evolving catalog of many independent rules distributed as one compiled document       | Tier 2 **+** `rules/` **+** `AGENTS.md` (generated)                         | `django-rest-framework-best-practices`, `react-native-with-expo-best-practices` |

**Heuristic:** one instruction → _Tier 1_ · one workflow/tool → _Tier 2_ · many rules needing a single distributable artifact → _Tier 3_.

```
Is it one stable instruction with no assets?            → Tier 1
Is it one workflow/tool (maybe with a script)?          → Tier 2
Is it many independent rules → one compiled document?   → Tier 3
```

A skill's folder structure should match its complexity — no more, no less. Adding `rules/` and a compiled `AGENTS.md` to a one-line procedure is overhead; cramming a large rule catalog into a single `SKILL.md` is unmaintainable. Pick the smallest tier that fits, and when in doubt start one tier lower — promoting later is a copy-and-split, not a rewrite.

### Tier 1 · Minimal

Use when the skill is a single, stable instruction or procedure with no supporting assets, no executable helpers, and no need for versioning or a changelog. The whole thing fits comfortably in `SKILL.md` (keep the body under ~5k tokens).

```
<skill-name>/
└── SKILL.md
```

**Example:** `commit` — one procedure (analyze staged changes, write a _Conventional Commit_).

**Promote to Tier 2 when** you start wanting a helper script, bundled assets, or version metadata.

### Tier 2 · Procedural

Use when the skill encodes a workflow or a tool/_API_ integration. It may bundle helper scripts (Level-3 executable code), and it benefits from version metadata and a human-facing `README.md`.

```
<skill-name>/
├── SKILL.md          # the whole procedure + when-to-use
├── metadata.json     # version, author, abstract, reference links
├── README.md         # human-facing overview
├── scripts/          # optional: executable helpers (run via bash)
│   └── <tool>.py
└── templates/        # optional: copy-ready assets the skill hands out
```

**Examples:** `notion` (workflow over an _API_), `audit` (`scripts/audit.py` helper), `review` (three files, nothing else), and `skill-factory` itself (bundles `templates/`).

**Everything lives in `SKILL.md`.** A _Tier-2_ skill never splits its instructions across side documents — the complete procedure stays in `SKILL.md` so a single read gives the whole picture. Several hundred lines is normal; `notion` and `review` both sit there. Prefer a `scripts/` helper over prose when an operation must be deterministic.

**Promote to Tier 3 when** the body stops being one coherent procedure and becomes a large catalog of many independent guidelines that you want to distribute as one compiled document. Outgrowing `SKILL.md` is a signal to promote, never to split the file.

### Tier 3 · Compiled (best-practices)

Use when the skill is a large, evolving set of many independent rules that (a) benefit from one-rule-per-file modularity and (b) are consumed as a single compiled artifact (`AGENTS.md`).

```
<skill-name>/
├── SKILL.md               # overview, when-to-apply, quick reference
├── metadata.json          # version, author, abstract, reference links
├── README.md              # human-facing overview + authoring workflow
├── rules/
│   ├── _sections.md       # index of all rules, grouped by section
│   ├── _template.md       # blank rule scaffold
│   └── <prefix>-<name>.md # one rule per file
└── AGENTS.md              # GENERATED: all rules compiled into one document
```

- Rule filenames use a category prefix (e.g. `arch-`, `conf-`) so they sort and group by concern
- `AGENTS.md` is a generated artifact — never hand-edited. It is regenerated by following the procedure in _AGENTS.md Compilation_ below (reading the rules and `metadata.json`), not by any bundled script

**Examples:** `django-rest-framework-best-practices`, `react-native-with-expo-best-practices`.

## Authoring Workflow

1. **Pick a tier** using the table above
2. **Use the name the user chose** — never invent or pick one; if it is missing, ask. Then validate it: lowercase letters, numbers, and hyphens only; ≤ 64 chars; must not contain `anthropic` or `claude`
3. **Copy the matching template** from `templates/tier-<n>/` into `~/.claude/skills/<skill-name>/`
4. **Fill every placeholder** (`<skill-name>`, `<Title>`, `<description>`, …). The `description` must state what the skill does and when to use it — it is what _Claude_ matches against
5. **Tier 3 only:** author one rule per file under `rules/`, register each in `rules/_sections.md`, then compile `AGENTS.md` following _AGENTS.md Compilation_ below
6. **Verify** against the checklists in _File Formats_ below

## File Formats

Exact formats and checklists for every file a skill may contain. Copy the matching template from `templates/`, then validate against the checklist here.

### Prose conventions

Apply these across every markdown file in a skill:

- Write in _English_
- Italicize proper nouns / product names in prose (`_Django_`, `_Docker_`); leave them plain in headings, code, link text, and frontmatter
- Do not end enumeration items (bullet, numbered, or checklist) with a period; keep periods only inside running-prose paragraphs
- Keep generated artifacts (`AGENTS.md`) out of manual edits

### `SKILL.md` (all tiers — required)

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
- [ ] Body is self-contained — the whole procedure lives here, never split across side documents
- [ ] Written in _English_ (collection convention)

### `metadata.json` (Tier 2/3)

Human/tooling metadata. Not read by the platform; it is the single source for the compiled `AGENTS.md` header in _Tier 3_. Its `references` field is a list of external _URLs_ — source material the skill is based on.

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

### `README.md` (Tier 2/3)

Human-facing overview. Describes the skill's purpose, its file structure, and how to use/maintain it. For _Tier 3_ it also documents the authoring workflow (creating a rule, recompiling).

**Checklist:**

- [ ] Lists the file structure with one-line descriptions
- [ ] States how to use the skill
- [ ] Tier 3: documents "create a rule" and "recompile `AGENTS.md`" steps and marks `AGENTS.md` as generated

### `rules/` (Tier 3)

#### `rules/_sections.md`

Index of all rules, grouped by section, linking each rule file. Keep it in sync with the actual rule set and with the section order used to compile `AGENTS.md`.

#### `rules/_template.md`

A blank rule scaffold authors copy. Establishes the strict rule shape.

#### `rules/<prefix>-<name>.md`

One rule per file. Filenames start with a category prefix (`arch-`, `conf-`, …) so related rules sort together.

````markdown
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

```<lang>
<bad example>
```

**Correct (<what's right>):**

```<lang>
<good example>
```

Reference: [<label>](url)
````

**Checklist per rule:**

- [ ] Filename `<prefix>-<name>.md`; first heading is `## <Title>`
- [ ] Frontmatter has `title`, `impact`, `description`, `tags`
- [ ] Has clear _Incorrect_ and _Correct_ examples
- [ ] Registered in `rules/_sections.md`
- [ ] Proper nouns / product names italicized in prose (`_Django_`, `_Docker_`, …); left plain in headings, code, link text, and frontmatter

### `AGENTS.md` (Tier 3 — generated)

The full compiled document: _Vercel_-style header (title, version, Note, Abstract), a derived table of contents, and every rule expanded inline under numbered sections. Never hand-edit. The exact format and how it is produced follow below.

## AGENTS.md Compilation (Tier 3)

`AGENTS.md` is the single distributable document for a _Tier-3_ skill: every rule expanded inline, in a fixed order, behind a header and a derived table of contents. It is a generated artifact — never hand-edited.

There is no build script and no bundled command. You (the agent) produce `AGENTS.md` by reading the skill's `rules/`, `rules/_sections.md`, and `metadata.json`, then following the procedure below — the structure is described here, and the artifact is created from analysis of the rules themselves.

### Sources of truth

- **`rules/_sections.md`** — section grouping and order, and which rules belong to each section
- **`rules/<slug>.md`** — each rule's title (its `## ` heading), `impact` (frontmatter), and body
- **`metadata.json`** — `version`, `author`, `date`, `abstract` for the header
- **`SKILL.md`** — the skill's human title (its top `# ` heading)

### Output format (Vercel-aligned)

```
# <Skill Title>

**Version <version>**            ← two trailing spaces = hard line break
_<Author>_
_<Date>_

> **Note:**
> This document is mainly for agents and LLMs to follow when maintaining,
> generating, or refactoring <domain> codebases. Humans
> may also find it useful, but guidance here is optimized for automation
> and consistency by AI-assisted workflows.

---

## Abstract

<abstract from metadata.json>

---

## Table of Contents

1. [<Section>](#1-section) — `<IMPACT>`
   - 1.1 [<Rule Title>](#11-rule-title)
   ...

---

## 1. <Section>

### 1.1 <Rule Title>

<rule body: Impact, Guidelines, Incorrect/Correct, Reference>
...
```

### Procedure

#### 1 · Header

Build it from `metadata.json` and `SKILL.md`; do not keep a separate header file:

- `# <Skill Title>` — the skill's human title (the `# ` heading in `SKILL.md`)
- `**Version <version>**` — end the line with two spaces (hard break)
- `_<author>_` — italicized, two-space hard break
- `_<date>_` — italicized
- The note blockquote verbatim from the format above, with `<domain>` replaced by the technology the skill governs (e.g. "Django and Django REST Framework")
- `---`, then `## Abstract`, then the `abstract` from `metadata.json` (proper nouns may be italicized), then `---`

#### 2 · Table of Contents (derived)

- Number the sections in `rules/_sections.md` order (`N`), and the rules within each section (`N.M`)
- Section line: `N. [<Section>](#<anchor>) — ` + the strongest impact among its rules in backticks (rank `CRITICAL > HIGH > MEDIUM > LOW`)
- Rule line (indented three spaces): `- N.M [<Rule Title>](#<anchor>)`
- Anchor = the heading's visible text (including its number) lowercased, with every character that is not a letter, digit, space, or hyphen removed, then spaces turned into hyphens. Examples: `## 2. Configuration & DevOps` → `#2-configuration--devops`; `### 2.2 Deployment Topology` → `#22-deployment-topology`

#### 3 · Body (expanded rules)

- For each section, in order: `## N. <Section>`
- For each rule, in order: `### N.M <Rule Title>`, followed by the rule's body — everything after its frontmatter and after its own `## ` title line — with any inner `### ` heading demoted to `#### ` so it nests under the numbered rule
- Separate sections (and the header from the TOC) with a `---` rule

### Invariants to verify after generating

- **Idempotent:** regenerating without content changes reproduces the same file
- **Anchors resolve:** every TOC link matches a heading slug
- **No leaks:** no rule frontmatter and no un-numbered rule titles appear in the output
- **Spacing:** exactly one blank line after each heading

### Adding a rule (recap)

- Create `rules/<prefix>-<name>.md` from `rules/_template.md`
- Register it in `rules/_sections.md` (section + order)
- Regenerate `AGENTS.md` by following this procedure
