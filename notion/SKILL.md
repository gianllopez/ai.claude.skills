---
name: notion
description: Creates and manages tasks, respecting the default task template and the workspace property schema.
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
  version: 1.0.0
---

# Notion Task Management

Creates tasks in the user's _Notion_ database following the default template and the property
schema defined in the workspace.

## When to Apply

- The user types `/notion`
- The user asks to _"create a task"_, _"add a task to Notion"_, _"register a task"_, etc
- The user describes a piece of work or a to-do that should be recorded in the task database

## Fixed workspace references (do not change between runs)

These identifiers were confirmed and can be used directly:

| Resource                  | Identifier                                          |
| :------------------------ | :-------------------------------------------------- |
| Database                  | `💻 Control` — `bbd62c06e9d783bb9a0201136005d2a3`   |
| Data source (parent)      | `collection://93c62c06-e9d7-826d-bd33-875c237b46f6` |
| Default template          | `39162c06e9d78061a6fdcb399d848fb5`                  |
| Primary user (Gian López) | `a3c06894-0016-457e-8d4a-5ebce86eb8c0`              |

> When creating the page, the `parent` must be
> `{ "type": "data_source_id", "data_source_id": "93c62c06-e9d7-826d-bd33-875c237b46f6" }`.

## Execution Protocol

### 1. Re-validate the schema (mandatory for dynamic properties)

Several select properties are dynamic catalogs whose options grow or change depending on what
is registered at the moment — `Sprint`, `Módulo`, `Proyecto`, and `Tipo`.
Before assigning any of these, run `notion-fetch` on
`collection://93c62c06-e9d7-826d-bd33-875c237b46f6` to read the current options, then:

1. Infer the best match from the existing options based on the user's request.
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
| `Fecha de Inicio`       | date         | 🔒 Not set on creation — filled when work starts. Do not assign.            |
| `Fecha de Finalización` | date         | 🔒 Not set on creation — filled when the task is completed. Do not assign.  |
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
	**Estado: **<span color="gray">**`[Estado]`**</span>
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
> (`<mention-date/>`) and the person (`<mention-user/>`), plus a status line formatted as
> ``**Estado: **<span color="COLOR">**`ESTADO`**</span>``. Status colors:
> `BLOQUEADO`→`red`, `PENDIENTE`→`gray`, `EN PROGRESO`→`blue`, `TERMINADO`→`green`.

> If you need more advanced block syntax, first read the MCP resource
> `notion://docs/enhanced-markdown-spec` before generating the content.

---

# 🔧 User Directives

> These blocks define the skill's _behavior_. Follow them on every task creation.

## 🔧 Directive 1 — Default values

When the user does not specify a value:

- **Estado:** always `PENDIENTE` — a new task is created in this state, no exception.
- **Responsable:** default to _Gian López_ (`a3c06894-0016-457e-8d4a-5ebce86eb8c0`) unless another
  person is explicitly named.
- **Prioridad:** never assume — always ask (see Directive 2).
- **Dificultad:** infer from the described scope (e.g. several technical steps → `4 — COMPLEJO`).
  Do not ask.
- **Sprint:** never assume — always ask, offering the live options (see Directive 2).
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

- **Language:** _Spanish_.
- **Objetivo:** a single paragraph giving the context, need, or problem to solve.
- **Plan de acción:** 3–5 actionable checkbox items.
- **Emphasis:** technical terms, acronyms, and proper nouns (brands, products, services,
  people, places) in _italics_ (e.g. _API_, _SQL_, _Google_).

## 🔧 Directive 5 — "Registros" section behavior

On creation, generate:

1. The opening line — date via the `@now` equivalent + the _Gian López_ mention, followed by
   `Se inicia la tarea con el objetivo de …`.
2. An empty placeholder `<details>` block (with bracketed placeholders for date, person,
   description, and status) so collaborators know how to log their progress updates.

Keep the placeholder block with its bracketed placeholders — do not fill it with a real
update and do not remove it.
