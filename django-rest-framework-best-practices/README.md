# Django Best Practices

A structured repository for creating and maintaining _Django_ & _Django REST Framework_ Best Practices optimized for agents, LLMs, and human developers.

## Structure

- `rules/` - Individual rule files (one per rule)
  - `_sections.md` - Section metadata (index of all rules)
  - `_template.md` - Template for creating new rules
  - `category-rule-name.md` - Individual rule definitions
- `metadata.json` - Document metadata (version, organization, references)
- `AGENTS.md` - Compiled output (the "System Prompt" for Claude/LLMs)

## Workflow

1. **Define Rules:** Create or edit markdown files in the `rules/` directory.
2. **Compile:** Combine rules into the master `AGENTS.md` file.
3. **Deploy:** Upload `AGENTS.md` to your AI context or distribute to the development team.

## Creating a New Rule

1. Copy `rules/_template.md` to `rules/category-name.md`
2. Choose the appropriate category prefix:
   - `arch-` for Architecture & App Structure
   - `conf-` for Configuration & DevOps (Settings, Docker, Env)
3. Fill in the frontmatter (`title`, `impact`, `description`, `tags`)
4. Ensure you have clear **Incorrect** vs **Correct** examples.
5. Update `rules/_sections.md` to include your new rule in the index.

## Rule File Structure

Each rule file should follow this strict frontmatter and structure:

````markdown
| Title    | Impact                       | Description (optional) | Tags (comma-separeted) |
| -------- | ---------------------------- | ---------------------- | ---------------------- |
| \<title> | \<impact: LOW, MEDIUM, HIGH> | \<description>         | \<tags>                |

## \<title>

**Impact (\<impact: LOW, MEDIUM, HIGH>):** \<description>

<Brief explanation of the rule and why it matters. This should be clear and concise, explaining the performance implications>

**Incorrect (description of what's wrong):**

```python
// Bad code example here
const bad = example();
```

**Correct (description of what's right):**

```python
// Good code example here
const good = example();
```

Reference: [Link to documentation or resource](https://example.com)
````

Reference: [Some link example](google.com)

## File Naming Convention

- Files starting with `_` are special (metadata or templates).
- Rule files: `prefix-description.md` (e.g., `orm-model-structure.md`).
- Rules are categorized by their filename prefix.

## Impact Levels

- **CRITICAL** - Security risks or system-breaking patterns (e.g., exposing keys).
- **HIGH** - Major architectural decisions or strict naming conventions.
- **MEDIUM-HIGH** - Standardization that prevents technical debt.
- **MEDIUM** - Optimizations for performance or readability.
- **LOW** - Stylistic preferences.

## Acknowledgments

Originally created by [@gianllopez](https://github.com/gianllopez).
