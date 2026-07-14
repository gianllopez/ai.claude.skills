# AGENTS.md Compilation (Tier 3)

`AGENTS.md` is the single distributable document for a _Tier-3_ skill: every rule expanded inline, in a fixed order, behind a header and a derived table of contents. It is a generated artifact — never hand-edited.

There is no build script. You (the agent) produce `AGENTS.md` by reading the skill's `rules/`, `rules/_sections.md`, and `metadata.json`, then following the procedure below. This keeps skills free of bundled commands; the structure is described here and created from analysis of the rules themselves.

## Sources of truth

- **`rules/_sections.md`** — section grouping and order, and which rules belong to each section
- **`rules/<slug>.md`** — each rule's title (its `## ` heading), `impact` (frontmatter), and body
- **`metadata.json`** — `version`, `author`, `date`, `abstract` for the header
- **`SKILL.md`** — the skill's human title (its top `# ` heading)

## Output format (Vercel-aligned)

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

## Procedure

### 1 · Header

Build it from `metadata.json` and `SKILL.md`; do not keep a separate header file:

- `# <Skill Title>` — the skill's human title (the `# ` heading in `SKILL.md`)
- `**Version <version>**` — end the line with two spaces (hard break)
- `_<author>_` — italicized, two-space hard break
- `_<date>_` — italicized
- The note blockquote verbatim from the format above, with `<domain>` replaced by the technology the skill governs (e.g. "Django and Django REST Framework")
- `---`, then `## Abstract`, then the `abstract` from `metadata.json` (proper nouns may be italicized), then `---`

### 2 · Table of Contents (derived)

- Number the sections in `rules/_sections.md` order (`N`), and the rules within each section (`N.M`)
- Section line: `N. [<Section>](#<anchor>) — ` + the strongest impact among its rules in backticks (rank `CRITICAL > HIGH > MEDIUM > LOW`)
- Rule line (indented three spaces): `- N.M [<Rule Title>](#<anchor>)`
- Anchor = the heading's visible text (including its number) lowercased, with every character that is not a letter, digit, space, or hyphen removed, then spaces turned into hyphens. Examples: `## 2. Configuration & DevOps` → `#2-configuration--devops`; `### 2.2 Deployment Topology` → `#22-deployment-topology`

### 3 · Body (expanded rules)

- For each section, in order: `## N. <Section>`
- For each rule, in order: `### N.M <Rule Title>`, followed by the rule's body — everything after its frontmatter and after its own `## ` title line — with any inner `### ` heading demoted to `#### ` so it nests under the numbered rule
- Separate sections (and the header from the TOC) with a `---` rule

## Invariants to verify after generating

- **Idempotent:** regenerating without content changes reproduces the same file
- **Anchors resolve:** every TOC link matches a heading slug
- **No leaks:** no rule frontmatter and no un-numbered rule titles appear in the output
- **Spacing:** exactly one blank line after each heading

## Adding a rule (recap)

- Create `rules/<prefix>-<name>.md` from `rules/_template.md`
- Register it in `rules/_sections.md` (section + order)
- Regenerate `AGENTS.md` by following this procedure
