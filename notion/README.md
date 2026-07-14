# Notion Task Management

An executable skill that creates and manages tasks in the _Notion_ database
`💻 Control`, following the workspace's default template, property schema,
and task conventions.

Unlike the best-practices skills in this repository (which are reference catalogs split into a
`rules/` directory), this is a procedural skill: a small set of linear operations that are read
in full and executed in order. Its structure is intentionally flat.

## Structure

- `SKILL.md` - The skill definition. Contains the execution protocol, the property schema, the
  page-content template, and the user directives that govern behavior.
- `metadata.json` - Document metadata (version, author, date, abstract, references)

## What it does

The skill exposes two operations.

**Operation A — Create a Task**

1. **Re-validates the schema** - reads the live data source to get current options for the
   dynamic catalog properties.
2. **Gathers the task data** - infers what it can, applies defaults, and always confirms the
   mandatory fields with the user.
3. **Checks for duplicates** - warns if a very similar active task already exists
4. **Previews and gets approval** - shows the full task (properties + body) and waits for an
   explicit "go" before writing.
5. **Creates the task** - under the correct data source, with the `📝` icon and the default
   template body.
6. **Confirms** - returns the created task's address

**Operation B — Calculate & Set Task Dates**

Given a task (by link or mention), it maps the task's `Dificultad` to estimated hours — read live
from the `⚙️ Sistema` page, the single source of truth for that mapping — sets `Fecha de Inicio`
to the next full hour, and spreads the estimated hours over the company's working blocks (skipping
lunch, weekends, and _Colombian_ holidays) to compute `Fecha de Finalización`. After approval, it
writes both dates to the task.

## Behavior configuration

The skill's behavior is defined by the user directives section of `SKILL.md`:

1. **Default values** - what to assume when the user does not specify a value
2. **Fields that must always be confirmed** - `Proyecto`, `Sprint`, `Módulo`, `Tipo`, `Prioridad`
3. **Task name convention** - uppercase, infinitive verb, no trailing period
4. **Content tone and style** - _Spanish_, one-paragraph objective, 3–5 action items, and _italics_
   for technical terms, acronyms, and proper nouns.
5. **"Registros" section behavior** - opening line plus an empty placeholder block that shows
   collaborators how to log progress.
6. **Working schedule** - business hours, effective daily hours, and the holiday rule used by
   _Operation B_ to compute dates.

To change how the skill behaves, edit these directives — not the execution protocol.

## Scope

This skill currently covers task creation (_Operation A_) and date calculation (_Operation B_). If it
grows further (updating status, closing tasks, logging progress, reporting), keep splitting it
**by operation**, not into a `rules/` catalog.

## Acknowledgments

Originally created by [@gianllopez](https://github.com/gianllopez).
