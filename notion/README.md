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

The skill exposes four operations.

**Operation A — Create a Task**

1. **Re-validates the schema** - reads the live data source to get current options for the
   dynamic catalog properties.
2. **Reads the team's people** - lists the workspace members live, so `Responsable` is picked from
   who actually exists there.
3. **Gathers the task data** - infers what it can, applies defaults, and always confirms the
   mandatory fields with the user — including who is responsible.
4. **Checks for duplicates** - warns if a very similar active task already exists
5. **Previews and gets approval** - shows the full task (properties + body) and waits for an
   explicit "go" before writing.
6. **Creates the task** - under the correct data source, with the `📝` icon and the default
   template body.
7. **Confirms** - returns the created task's address
8. **Offers the date calculation** - always asks whether to run _Operation B_ right away on the
   task just created.

**Operation B — Calculate & Set Task Dates**

Given a task (by link or mention), it maps the task's `Dificultad` to estimated hours — read live
from the `⚙️ Sistema` page, the single source of truth for that mapping — sets `Fecha de Inicio`
to the next full hour, and spreads the estimated hours over the company's working blocks (skipping
lunch, weekends, and _Colombian_ holidays) to compute `Fecha de Finalización`. After approval, it
writes both dates to the task.

**Operation C — Add a Progress Record**

Given a task (by link or mention), it appends an entry to the page's _Registros_ log: date, author,
a short description of the progress or blocker, and a closing field — one key and its value. Both
halves are decided per record, from what the record is actually about; there is no fixed field the
skill always writes. It is always asked for and shown in the preview. When the key happens to be a
property of the task and the value differs from what it holds, the skill offers to update the
property too.

**Operation D — Close a Task**

Given a task (by link or mention), it computes the working hours elapsed between `Fecha de Inicio`
and the moment the task was finished — the same schedule _Operation B_ spends hours across, walked
backwards — and offers that figure as the recommended answer to "how long did it take?". The number
the user confirms is written to `Horas (Reales)` together with the `Estado` transition to
`POR APROBAR`, in one call, because the workspace's own rule is that a task without real hours is
not approved. It closes by offering to append the matching record through _Operation C_.

The elapsed time is an anchor, never the answer: a task can sit open for two days and cost four
hours of work, and only the developer knows the difference. What the skill removes is having to
recall the figure from memory.

## Behavior configuration

The skill's behavior is defined by the user directives section of `SKILL.md`:

1. **Default values** - what to assume when the user does not specify a value
2. **Fields that must always be confirmed** - `Proyecto`, `Sprint`, `Módulo`, `Tipo`, `Prioridad`,
   `Responsable`
3. **Task name convention** - uppercase, infinitive verb, no trailing period
4. **Content tone and style** - _Spanish_, one-paragraph objective, 3–5 action items, no trailing
   period on any list item, and _italics_ for technical terms, acronyms, and proper nouns.
5. **"Registros" section behavior** - opening line plus an empty placeholder block that shows
   collaborators how to log progress.
6. **Working schedule** - business hours, effective daily hours, and the holiday rule used by
   _Operation B_ to compute dates.
7. **Date-calculation prompt** - after creating a task, always ask whether to compute its dates
   now — as a real question that closes the turn, not a remark in the confirmation text.
8. **Every record closes on one field** - a key and its value, decided per record with no default,
   always confirmed, never inferred, and never more than one.
9. **Responsible from the team list** - `Responsable` is always asked, offering the workspace's
   people read live from the connector; _Gian López_ is the recommended option, never a silent
   default.
10. **Real hours are calculated, then confirmed** - the elapsed working time anchors the answer,
    the user confirms it, and the estimate is never copied into it.
11. **The close is atomic** - `Horas (Reales)` and the `POR APROBAR` transition are written
    together, never one without the other.

To change how the skill behaves, edit these directives — not the execution protocol.

## Scope

This skill currently covers task creation (_Operation A_), date calculation (_Operation B_),
progress records (_Operation C_), and closing a task (_Operation D_). Together, B and D implement
the workspace's hour-control scheme: the estimated plan and the real cost, measured on one
calendar. If it grows further (approval, reporting), keep splitting it **by operation**, not into a
`rules/` catalog.

## Acknowledgments

Originally created by [@gianllopez](https://github.com/gianllopez).
