# React Core Best Practices

A structured repository of _React_ rules that hold on any platform, optimized for agents, LLMs, and human developers. Built for writing and reviewing: each rule names a defect concrete enough to point at in a diff, and shows the correct shape beside it.

What belongs to a renderer is deliberately absent. Semantic _HTML_, _TailwindCSS_ v4 and `shadcn/ui` live in `react-best-practices`; _NativeWind_ and _Expo_ configuration in `react-native-with-expo-best-practices`. A project loads this skill plus the one for its platform.

## Structure

- `rules/` - Individual rule files (one per rule)
  - `_sections.md` - Section metadata (index of all rules)
  - `_template.md` - Template for creating new rules
  - `category-rule-name.md` - Individual rule definitions
- `metadata.json` - Document metadata (version, author, abstract, references)
- `AGENTS.md` - **Generated** compiled output (all rules expanded); never hand-edit
- `SKILL.md` - Skill definition and trigger mapping for AI agents

## Conventions

Decisions that hold across every rule in this package, so no rule has to restate them and no two rules can disagree.

### `~/` is the import alias

Every example imports through `~/`, resolved to the source root. It is a convention rather than a platform constraint — each stack configures its own resolver, and _Expo_ scaffolds `@/` by default — but the projects this skill governs standardize on `~/`, and the examples say so with one voice.

What must not vary is everything after the prefix: `~/core/api/invoices/use-invoices` reads the same in a web project and in an _Expo_ one. The alias is the only part a platform gets to choose, and `arch-folder-structure` is the rule that owns it once it lands.

### Names

Components keep the entity singular — `InvoiceList`, `InvoiceRow` — because the suffix already carries the plurality. Domain folders are the opposite and stay plural: `core/api/invoices/`, `core/types/products/`. Files are kebab-case whatever they export, and never repeat the folder that contains them.

## Dual examples: the three levels

This is what distinguishes this skill from its two siblings, and the decision that keeps it readable. A rule lives here **once**. Where its correct shape is written differently on web and on _React Native_, it shows both — but only where they genuinely differ.

Pick the **lowest** level that works.

### Level 1 · No platform surface

The rule is demonstrated in `.ts` with no _JSX_, or with components the project owns. There is nothing to duplicate, and a second block would repeat the same code.

One `Incorrect`, one `Correct`, no platform labels.

_Examples:_ `data-query-layer`, `arch-typing-system`, `arch-core-utilities`, `state-derived-values`, `perf-render-stability`.

### Level 2 · The fix differs, the defect does not

The defect reads the same on both platforms; only the correct shape changes idiom. Write the `Incorrect` once, in whichever platform shows it most clearly, then two labelled `Correct` blocks.

```markdown
**Incorrect (…):**

**Correct (React DOM):**

**Correct (React Native):**
```

This is the default.

_Examples:_ `state-effect-discipline`, `state-identity-and-keys`, `data-async-states`, `arch-typing-conventions`, `arch-syntax-conventions`, `arch-class-composition`.

### Level 3 · The defect differs too

A single `Incorrect` would be unintelligible to one of the two audiences, so both halves are written per platform. The most expensive level — reach for it only when Level 2 genuinely fails.

_Examples:_ `state-colocation`, `arch-components-structure`, `arch-composition-patterns`.

### Why the levels matter

A duplicated block that shows no real difference is noise, and it teaches the reader to skip examples — which is exactly how the one that mattered gets missed. A rule that sits at Level 3 without needing it is a review finding against this repository, not against anyone's code.

## Workflow

1. **Define rules:** create or edit markdown files in the `rules/` directory
2. **Regenerate:** rebuild `AGENTS.md` from the rules (see below). It is a generated artifact — edit the rules, not `AGENTS.md`
3. **Deploy:** distribute `AGENTS.md` to your AI context or development team

## Creating a New Rule

1. Copy `rules/_template.md` to `rules/category-name.md`
2. Choose the appropriate category prefix:
   - `state-` for state and effects: effect discipline, derivation, ownership, identity
   - `arch-` for architecture: folder structure, component files, composition, extraction, typing, syntax, class composition
   - `data-` for data flow: the query layer, mutations, async branches
   - `perf-` for performance and robustness: render stability
3. Fill in the frontmatter (`title`, `impact`, `description`, `tags`)
4. Pick the example level from the section above, and justify Level 3 if you reach for it
5. Register the rule in `rules/_sections.md` (section + order)
6. Regenerate `AGENTS.md` (see below)

## Regenerating `AGENTS.md`

There is no build script. `AGENTS.md` is regenerated by following the described procedure in `skill-factory/SKILL.md` (_AGENTS.md Compilation_) — reading `rules/`, `rules/_sections.md`, and `metadata.json`, then producing the compiled document. The sources of truth are the rules and `metadata.json`.

## File Naming Convention

- Files starting with `_` are special (metadata or templates)
- Rule files: `prefix-description.md` (e.g., `state-effect-discipline.md`)
- Rules are categorized by their filename prefix

## Impact Levels

- **CRITICAL** - Breaks behavior or ships broken output (misplaced effects, interpolated class names)
- **HIGH** - Wrong ownership or strategy, or standardization that prevents technical debt; costly to unwind later
- **MEDIUM** - Optimizations for build output or runtime behavior
- **LOW** - Stylistic preferences, usually enforced by tooling

## Acknowledgments

Originally created by [@gianllopez](https://github.com/gianllopez).
