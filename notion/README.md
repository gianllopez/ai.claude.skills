# Notion Task Management

An executable skill that creates and manages tasks in the _Notion_ database
`💻 Control`, following the workspace's default template, property schema,
and task conventions.

Unlike the best-practices skills in this repository (which are reference catalogs split into a
`rules/` directory), this is a procedural skill: a single, linear workflow that is read in
full and executed in order. Its structure is intentionally flat.

## Structure

- `SKILL.md` - The skill definition. Contains the execution protocol, the property schema, the
  page-content template, and the user directives that govern behavior.
- `metadata.json` - Document metadata (version, author, date, abstract, references).

## What it does

Given a request to create a task, the skill:

1. **Re-validates the schema** - reads the live data source to get current options for the
   dynamic catalog properties.
2. **Gathers the task data** - infers what it can, applies defaults, and always confirms the
   mandatory fields with the user.
3. **Checks for duplicates** - warns if a very similar active task already exists.
4. **Previews and gets approval** - shows the full task (properties + body) and waits for an
   explicit "go" before writing.
5. **Creates the task** - under the correct data source, with the `📝` icon and the default
   template body.
6. **Confirms** - returns the created task's address.

## Behavior configuration

The skill's behavior is defined by the user directives section of `SKILL.md`:

1. **Default values** - what to assume when the user does not specify a value.
2. **Fields that must always be confirmed** - `Proyecto`, `Sprint`, `Módulo`, `Tipo`, `Prioridad`.
3. **Task name convention** - uppercase, infinitive verb, no trailing period.
4. **Content tone and style** - _Spanish_, one-paragraph objective, 3–5 action items, and _italics_
   for technical terms, acronyms, and proper nouns.
5. **"Registros" section behavior** - opening line plus an empty placeholder block that shows
   collaborators how to log progress.

To change how the skill behaves, edit these directives — not the execution protocol.

## Scope

This skill currently covers task creation. If it grows to cover multiple operations
(updating status, closing tasks, logging progress, reporting), the recommended next step is to
split it by operation, not into a `rules/` catalog.

## Acknowledgments

Originally created by [@gianllopez](https://github.com/gianllopez).
