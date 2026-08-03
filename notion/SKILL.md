---
name: notion
description: Creates tasks in the Notion "Control" database, computes their start/finish dates from the company's working hours, and appends progress records to a task's "Registros" log, respecting the default template and property schema.
allowed-tools:
  - mcp__claude_ai_Notion__notion-fetch
  - mcp__claude_ai_Notion__notion-create-pages
  - mcp__claude_ai_Notion__notion-get-users
  - mcp__claude_ai_Notion__notion-query-data-sources
  - mcp__claude_ai_Notion__notion-update-page
  - AskUserQuestion
license: MIT
metadata:
  author: gianllopez
  version: 1.1.0
---

# Notion Task Management

Manages tasks in the user's _Notion_ database. It provides three operations: A — Create a Task
(following the default template and property schema), B — Calculate & Set Task Dates
(computing `Fecha de Inicio` and `Fecha de Finalización` from the company's working hours), and
C — Add a Progress Record (appending an entry to a task's _Registros_ log).

## When to Apply

- The user types `/notion`
- The user asks to _"create a task"_, _"add a task to Notion"_, _"register a task"_, etc (_Operation A_)
- The user describes a piece of work or a to-do that should be recorded in the task database (_Operation A_)
- The user asks to _"calculate the dates"_, _"set the start/finish dates"_, or _"schedule"_ a task (_Operation B_)
- The user asks to _"add a record"_, _"log progress"_, _"registrar un avance"_, or to note a blocker
  or an update on an existing task (_Operation C_).

## Fixed workspace references (do not change between runs)

These identifiers were confirmed and can be used directly:

| Resource                  | Identifier                                          |
| :------------------------ | :-------------------------------------------------- |
| Database                  | `💻 Control` — `bbd62c06e9d783bb9a0201136005d2a3`   |
| Data source (parent)      | `collection://93c62c06-e9d7-826d-bd33-875c237b46f6` |
| Default template          | `39162c06e9d78061a6fdcb399d848fb5`                  |
| Primary user (Gian López) | `a3c06894-0016-457e-8d4a-5ebce86eb8c0`              |
| Effort estimation source  | `⚙️ Sistema` — `f8b62c06e9d78242b6e6816333c7f6e9`   |

> When creating the page, the `parent` must be
> `{ "type": "data_source_id", "data_source_id": "93c62c06-e9d7-826d-bd33-875c237b46f6" }`.

## Operation A — Create a Task

### 1. Re-validate the schema (mandatory for dynamic properties)

Several select properties are dynamic catalogs whose options grow or change depending on what
is registered at the moment — `Sprint`, `Módulo`, `Proyecto`, and `Tipo`.
Before assigning any of these, run `notion-fetch` on
`collection://93c62c06-e9d7-826d-bd33-875c237b46f6` to read the current options, then:

1. Infer the best match from the existing options based on the user's request
2. If no existing option fits with reasonable confidence, ask the user with `AskUserQuestion`,
   offering the live options as choices — do not invent new option values on your own.

For these properties the live schema is the only source of truth — the table below does not list
their values. Fixed-scale properties (`Estado`, `Prioridad`, `Dificultad`) are stable and can be
used as documented without re-validation.

### 2. Gather the task data

From the user's request, infer as much as possible, then apply Directives 1 and 2: fill defaults,
infer what can be inferred, and always confirm the mandatory fields (`Proyecto`, `Sprint`,
`Módulo`, `Tipo`, `Prioridad`). Use `AskUserQuestion` to present closed-choice options.

### 3. Check for duplicates

Before creating, query the data source for an existing task whose name is very similar (use
`notion-query-data-sources` or `notion-search` scoped to the data source). If a likely duplicate
is found, warn the user and ask whether to proceed.

### 4. Preview and get approval

Show the user a summary of the task (all resolved `properties` plus the rendered body) and wait
for explicit approval. Do not write to _Notion_ until the user approves.

### 5. Create the task

Use `notion-create-pages` with the data source `parent`, the `properties` mapped to the schema,
the `content` in _Notion-flavored Markdown_ following the template, and `icon: "📝"`.

### 6. Confirm

Return the address of the created task and a summary of the assigned properties.

### 7. Offer to calculate the dates

Right after confirming, always ask the user with `AskUserQuestion` whether the dates should be
computed now (Directive 7). If they accept, continue straight into _Operation B_ using the task
just created — do not ask again for the task link. If they decline, stop here.

## Property schema (valid values)

Map each property exactly to these names and options. Fields marked 🔒 are never assigned on
creation: formula fields are read-only, and `Fecha de Inicio`, `Fecha de Finalización`, and
`Horas (Reales)` are filled in later as the task progresses — omit them from `properties`.

| Property                | Type         | Options / Format                                                            |
| :---------------------- | :----------- | :-------------------------------------------------------------------------- |
| `Tarea`                 | title (text) | Task name                                                                   |
| `Estado`                | select       | `PENDIENTE`, `EN PROGRESO`, `BLOQUEADO`, `POR APROBAR`, `TERMINADO`         |
| `Proyecto`              | select       | dynamic — read live options before assigning                                |
| `Tipo`                  | select       | dynamic — read live options before assigning                                |
| `Prioridad`             | select       | `ALTA`, `MEDIA`, `BAJA`                                                     |
| `Dificultad`            | select       | `1 — TRIVIAL`, `2 — FÁCIL`, `3 — MEDIO`, `4 — COMPLEJO`, `5 — MUY COMPLEJO` |
| `Módulo`                | select       | dynamic — read live options before assigning                                |
| `Sprint`                | select       | dynamic — read live options before assigning                                |
| `Responsable`           | person       | _JSON_ array of user IDs                                                    |
| `Notas`                 | text         | Free text                                                                   |
| `Fecha de Inicio`       | date         | 🔒 Not set at creation — assigned by _Operation B_ (or manually).           |
| `Fecha de Finalización` | date         | 🔒 Not set at creation — assigned by _Operation B_ (or manually).           |
| `Horas (Reales)`        | number       | 🔒 Not set on creation — filled when the task is completed. Do not assign.  |
| `Horas (Estimadas)`     | formula      | 🔒 Read-only — do not assign                                                |
| `Varianza (Horas)`      | formula      | 🔒 Read-only — do not assign                                                |

### Some `properties` example

```json
{
  "Tarea": "DESARROLLAR MÓDULO DE FACTURACIÓN",
  "Estado": "PENDIENTE",
  "Proyecto": "<live `Proyecto` option>",
  "Tipo": "<live `Tipo` option>",
  "Prioridad": "MEDIA",
  "Dificultad": "4 — COMPLEJO",
  "Módulo": "<live `Módulo` option>",
  "Sprint": "<live `Sprint` option>",
  "Responsable": "[\"a3c06894-0016-457e-8d4a-5ebce86eb8c0\"]"
}
```

## Page content structure (default template)

The page body must replicate this template in _Notion-flavored Markdown_. Do not include the title
inside `content` (it goes in `properties.Tarea`). The body copy stays in _Spanish_.

```markdown
## Objetivo 🎯

[Descripción breve del problema, necesidad o situación que se busca resolver]

## Plan de acción ✅

- [ ] [Primera actividad o paso]
- [ ] [Siguiente actividad, entregable o validación]
- [ ] [Actividad adicional necesaria]

## Registros 📋

**<mention-date start="<YYYY-MM-DD>" startTime="<HH:mm>" timeZone="America/Bogota"/> — <mention-user url="user://a3c06894-0016-457e-8d4a-5ebce86eb8c0"/>**
Se inicia la tarea con el objetivo de [contexto o punto de partida]

<details>
<summary>**[Día de la tarea (DD de MM)] — [[Mención de la persona]]**</summary>
	[Describe qué se realizó, avance obtenido o bloqueo identificado]
	**Estado: **<span color="gray_bg">**`[Estado]`**</span>
</details>
```

> **Opening record line:**
>
> - **Date:** in the _Notion UI_ this is typed with the `@now` shortcut (current
>   date and time). Since that shortcut does not exist in the _API_ format, insert a
>   `<mention-date>` set to the creation moment — current date in `start`, current time in
>   `startTime`, and `timeZone="America/Bogota"`.
> - **User:** always mention the task creator, _Gian López_
>   (`<mention-user url="user://a3c06894-0016-457e-8d4a-5ebce86eb8c0"/>`).

> Each later update is appended inside a `<details>` block whose `<summary>` holds the date
> (`<mention-date/>`) and the person (`<mention-user/>`), plus the status line described in
> _Status line_ below. Appending those updates is _Operation C_.

> If you need more advanced block syntax, first read the MCP resource
> `notion://docs/enhanced-markdown-spec` before generating the content.

## Status line (last line of every record)

Every record in _Registros_ ends with a status line. It is never omitted, and its color is a
**background** color (`*_bg`), so the status reads as a highlighted chip matching the color _Notion_
gives that option in the `Estado` select:

```markdown
**Estado: **<span color="red_bg">**`BLOQUEADO`**</span>
```

| `Estado`      | Select color | Span color  |
| :------------ | :----------- | :---------- |
| `PENDIENTE`   | gray         | `gray_bg`   |
| `EN PROGRESO` | blue         | `blue_bg`   |
| `BLOQUEADO`   | red          | `red_bg`    |
| `POR APROBAR` | yellow       | `yellow_bg` |
| `TERMINADO`   | green        | `green_bg`  |

> Text colors (`red`) and background colors (`red_bg`) are different values in
> _Notion-flavored Markdown_ — always use the `_bg` variant here. Never invent a color outside this
> table; if a status has no row, read the live option colors from the data source before rendering.

## Operation B — Calculate & Set Task Dates

Computes a task's `Fecha de Inicio` and `Fecha de Finalización` from its estimated effort and the
company's working schedule (Directive 6), then writes them to the task.

### 1. Identify the target task

The user provides the task by link or mention (a _Notion_ URL or page ID). Run `notion-fetch`
on it to read its properties — in particular `Dificultad`.

### 2. Resolve the estimated effort

The task's `Horas (Estimadas)` is a formula whose value is returned opaquely by the API
(`formulaResult://…`) and cannot be read or queried directly, so the effort must be derived from
`Dificultad`.

**Single source of truth:** the level → hours mapping lives only in _Notion_, on the `⚙️ Sistema`
page, section _Esquema de Control de Horas → Capa 1: Estimación_
(`f8b62c06e9d78242b6e6816333c7f6e9`). Run `notion-fetch` on that page and read the current mapping
from that table. Do not hardcode the values in this skill — always read them from that page so
the estimate is maintained in one place.

### 3. Compute `Fecha de Inicio`

Get the current time in _America/Bogota_ (e.g. `TZ="America/Bogota" date`). Round it up to the
next full hour (10:15 → 11:00). If that instant falls outside a working block (lunch, after
17:00, weekend, or holiday), move it forward to the next working instant.

This operation is meant to run during working hours. If it is run outside working hours, the
user will provide the start date instead — use the value they give.

### 4. Compute `Fecha de Finalización`

Starting at `Fecha de Inicio`, consume the estimated hours only within working blocks, rolling
over lunch, end of day, weekends, and _Colombian_ public holidays, until the hours are exhausted.
The instant the last hour is consumed is `Fecha de Finalización`. See Directive 6 for the exact
schedule and holiday rule.

### 5. Preview and get approval

Show the computed `Fecha de Inicio` and `Fecha de Finalización` (with the effort hours used) and
wait for explicit approval. Do not write to _Notion_ until the user approves.

### 6. Write the dates

Update the task with `notion-update-page` (`command: "update_properties"`), setting both dates as
date-times:

- `date:Fecha de Inicio:start` = ISO-8601 datetime, `date:Fecha de Inicio:is_datetime` = 1
- `date:Fecha de Finalización:start` = ISO-8601 datetime, `date:Fecha de Finalización:is_datetime` = 1

### 7. Confirm

Return the task address and the dates written.

## Operation C — Add a Progress Record

Appends one entry to an existing task's _Registros_ section: what happened, who logged it, when,
and the status the task is left in.

### 1. Identify the target task

The user provides the task by link or mention (a _Notion_ URL or page ID). Run `notion-fetch` on it
to read its current `Estado` and its existing _Registros_ entries.

### 2. Gather the record data

- **Date:** the current date and time in _America/Bogota_, as a `<mention-date>` (same format as the
  opening record line).
- **Person:** _Gian López_ (`a3c06894-0016-457e-8d4a-5ebce86eb8c0`) unless the user names someone
  else — resolve other people with `notion-get-users`.
- **Description:** one short paragraph in _Spanish_ describing what was done, the progress made, or
  the blocker found (Directive 4).

### 3. Resolve and present the status

The record's status is never silently inferred. Always ask the user with `AskUserQuestion`,
offering the five `Estado` options and marking the task's current one, then render it with its
background color from the _Status line_ table (Directive 8).

### 4. Render the record

```markdown
<details>
<summary>**<mention-date start="<YYYY-MM-DD>" startTime="<HH:mm>" timeZone="America/Bogota"/> — <mention-user url="user://<user-id>"/>**</summary>
	[Descripción del avance, resultado o bloqueo]
	**Estado: **<span color="<estado>_bg">**`<ESTADO>`**</span>
</details>
```

### 5. Preview and get approval

Show the rendered record — including the resolved status and the color it will use — and wait for
explicit approval. Do not write to _Notion_ until the user approves.

### 6. Append the record

Use `notion-update-page` with `command: "insert_content"` and `position: { "type": "end" }` so the
entry lands at the bottom of _Registros_. If the placeholder `<details>` block from the template is
still the last block, keep it: insert the real record and leave the placeholder in place
(Directive 5).

### 7. Sync the `Estado` property

If the record's status differs from the task's current `Estado`, ask the user whether to update the
property too. On a yes, run `notion-update-page` with `command: "update_properties"` setting
`Estado`.

### 8. Confirm

Return the task address and a summary of the appended record.

---

# 🔧 User Directives

> These blocks define the skill's _behavior_. Directives 1–5 govern _Operation A_ (task creation);
> Directive 6 governs _Operation B_ (date calculation); Directive 7 chains _A_ into _B_; Directive 8
> governs _Operation C_ (progress records). Directive 4 applies to every operation that writes page
> content.

## 🔧 Directive 1 — Default values

When the user does not specify a value:

- **Estado:** always `PENDIENTE` — a new task is created in this state, no exception
- **Responsable:** default to _Gian López_ (`a3c06894-0016-457e-8d4a-5ebce86eb8c0`) unless another
  person is explicitly named.
- **Prioridad:** never assume — always ask (see Directive 2)
- **Dificultad:** infer from the described scope (e.g. several technical steps → `4 — COMPLEJO`)
  Do not ask.
- **Sprint:** never assume — always ask, offering the live options (see Directive 2)
- **Módulo / Tipo:** dynamic catalogs — infer a candidate from the live options, but always
  confirm (see Directive 2).

## 🔧 Directive 2 — Fields that must always be confirmed

Always confirm these with the user before creating, even when a value can be inferred. Present the
live options with `AskUserQuestion`:

- `Proyecto`
- `Sprint`
- `Módulo`
- `Tipo`
- `Prioridad`

## 🔧 Directive 3 — Task name convention

The `Tarea` title must be written in uppercase and begin with a verb in the infinitive
(e.g. `DESARROLLAR MÓDULO DE FACTURACIÓN`). No trailing period.

## 🔧 Directive 4 — Content tone and style

- **Language:** _Spanish_
- **Objetivo:** a single paragraph giving the context, need, or problem to solve
- **Plan de acción:** 3–5 actionable checkbox items
- **Lists:** no enumeration item ever ends with a period — checkboxes, bulleted lists, and numbered
  lists alike, anywhere in the page body. Periods belong only to running-prose paragraphs
  (_Objetivo_, record descriptions). Other trailing punctuation (`?`, `:`) is fine when the item
  genuinely calls for it.
- **Emphasis:** technical terms, acronyms, and proper nouns (brands, products, services,
  people, places) in _italics_ (e.g. _API_, _SQL_, _Google_).

## 🔧 Directive 5 — "Registros" section behavior

On creation, generate:

1. The opening line — date via the `@now` equivalent + the _Gian López_ mention, followed by
   `Se inicia la tarea con el objetivo de …`.
2. An empty placeholder `<details>` block (with bracketed placeholders for date, person,
   description, and status) so collaborators know how to log their progress updates.

Keep the placeholder block with its bracketed placeholders — do not fill it with a real
update and do not remove it. Real updates are appended below it by _Operation C_.

## 🔧 Directive 6 — Working schedule (for _Operation B_)

Used to compute task dates in _Operation B_:

- **Working days:** Monday to Friday
- **Working blocks:** 08:30–12:00 and 13:30–17:00 → 7 effective hours per day (the 12:00–13:30
  lunch break does not count).
- **Holidays:** skip _Colombia_'s official public holidays — they are not working days. Determine
  them from the official _Colombian_ calendar for the year(s) the calculation spans.
- **Time zone:** _America/Bogota_
- **Effort mapping:** `Dificultad` → hours is defined only in _Notion_ (single source of truth):
  the `⚙️ Sistema` page, section _Esquema de Control de Horas → Capa 1: Estimación_. Read it live
  with `notion-fetch` (_Operation B_, step 2); never hardcode the values in this skill.

## 🔧 Directive 7 — Always offer the date calculation after creating a task

A newly created task has no dates. So immediately after _Operation A_ confirms the creation, always
ask — with `AskUserQuestion`, never as a passing remark — whether to calculate them now:

- **Yes** → run _Operation B_ on the task just created, reusing its page ID
- **No** → close the interaction; the dates stay empty until the user asks for them

Ask every time, even when the user did not mention dates, and never compute them without asking.

## 🔧 Directive 8 — Status in a progress record

Every record appended to _Registros_ (_Operation C_) ends with the status line, with no exceptions:

- **Always present:** a record without its `Estado` line is incomplete — never omit it
- **Always presented to the user:** show the resolved status in the preview before writing, so the
  user sees which state the task is being left in and can correct it.
- **Never inferred silently:** ask with `AskUserQuestion`, offering the five `Estado` options with
  the task's current one marked.
- **Color from the mapping:** use the `_bg` background color of the _Status line_ table, so
  `BLOQUEADO` renders on light red, `TERMINADO` on light green, and so on.
