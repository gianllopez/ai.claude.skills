---
name: audit
description: Reads and updates the Neovim `audit` plugin's per-project review database, which tracks each file's status (`pending`, `done`, or unaudited). Refuses to modify or propose changes to files already marked `done`, and marks files `pending` or `done` when the user explicitly asks. Use whenever editing, refactoring, or reviewing source files in a project tracked by the audit plugin, or when the user asks about — or asks to change — file review states.
allowed-tools:
  - Bash
  - Read
license: MIT
metadata:
  author: gianllopez
  version: 1.1.0
---

# Audit State Guard

Consults the review state maintained by the user's _Neovim_ `audit` plugin and enforces one rule
above all: never modify or propose changes to a file that is marked `done`. The plugin stores,
per project and file by file, a review `status` with full history; this skill reads that database
so _Claude Code_ respects the user's review progress, and writes to it — only on an explicit
request — so statuses can be changed without leaving the terminal.

## When to Apply

- Before editing, creating, deleting, or proposing changes to any file in a project that the
  audit plugin tracks — always check the target's status first
- The user types `/audit`
- The user asks about review state: _"what's the status of X?"_, _"which files are done?"_,
  _"what's left to review?"_, _"is this file audited?"_, etc
- The user asks to change a review state: _"mark X as done"_, _"set these files back to pending"_,
  _"mark everything from the last commit as pending"_, etc
- Before a broad/multi-file refactor, to filter out files that are already `done`

## Status Semantics

| Status      | Icon | Meaning                         | Claude's behavior                         |
| :---------- | :--- | :------------------------------ | :---------------------------------------- |
| `done`      | ✅   | Reviewed and locked by the user | Do not change. Guard applies (see below). |
| `pending`   | ⏳   | Awaiting review                 | Edit freely                               |
| `unaudited` | ·    | Not present in the database     | Edit freely                               |

## How to Read the Status

The plugin stores each project's database in a single, fixed file: `<git-root>/.git/audit.json`.
Always use the bundled script rather than parsing or editing that file by hand:

```bash
python3 ~/.claude/skills/audit/scripts/audit.py status <path> [<path>...]
python3 ~/.claude/skills/audit/scripts/audit.py list [--status pending|done|unaudited]
```

- `status <path…>` — prints `<icon> <status> <path>` for each file. Exit code is `1` if any target
  is `done`, `0` otherwise, so it doubles as a guard check.
- `list` — prints every audited file in the current project; `--status` filters

Run the script from the project's working directory: it resolves the project root by walking up to
the nearest `.git` and reads `<root>/.git/audit.json`. If that file is absent, the project simply
has no audit data yet — the database is created on the first status change.

## How to Change a Status

Only when the user explicitly asks for it (see the directives below):

```bash
python3 ~/.claude/skills/audit/scripts/audit.py set pending|done <path> [<path>...]
```

- Writes the same `<root>/.git/audit.json` the plugin writes, with the same schema and the same
  rules: a change appends `{ "status", "at" }` to the file's `history` (UTC, `%Y-%m-%dT%H:%M:%SZ`),
  and a file already at the requested status is left untouched and reported as `(unchanged)`
- All paths are validated first; if any is not a file in the project, nothing is written
- The plugin re-reads the database from disk on every operation, so changes show up immediately in
  the statusline and in `M.filter()` — no need to restart _Neovim_

There is no `unaudited` target: dropping a file's entry also destroys its history, which stays the
plugin's job (`clear_file_history`, `clean_orphans`). Bulk selections come from _Git_, not from a
dedicated flag:

```bash
# Every file in the last commit
python3 ~/.claude/skills/audit/scripts/audit.py set pending $(git diff-tree --no-commit-id -r --name-only HEAD)
```

## The Guard (core rule)

Before any edit, run `status` on the target file(s). Then:

1. **`done` (✅)** — Do not edit, create, delete, or propose a diff for that file. Stop and tell
   the user the file is marked `done`, e.g. _"`src/auth.py` is marked ✅ done in the audit database,
   so I won't change it. Do you want to override this for this edit?"_ Only proceed if the user
   gives an explicit override
2. **`pending` / `unaudited`** — Proceed normally
3. **Multi-file work** — Run `status` on all candidates first, silently skip the `done` ones, apply
   changes to the rest, and then report which files were skipped because they were `done`

## Directives

### Reading and guarding

- Always check a file's audit status before modifying or proposing changes to it in a tracked project
- Never edit, overwrite, or propose a diff for a file whose status is `done` without an explicit
  user override for that specific change
- When you skip a `done` file during a broader task, always surface it to the user rather than
  silently omitting the change
- If the reader reports a file as `unaudited`, treat it as editable — absence from the database is
  not the same as `done`

### Writing

- **Never change a status to unblock yourself.** Demoting a `done` file to `pending` so an edit
  becomes allowed defeats the whole guard. When the guard blocks you, ask for an override — do not
  touch the database
- Only run `set` when the user explicitly asks for that status change, in the same turn. A request
  to _write code_ is never a request to re-audit files
- Never mark a file `done` on your own initiative: `done` means _the user reviewed it_, and only
  they can assert that. Marking work you just produced as `done` claims a review that never happened
- Before a bulk `set` (more than a handful of files, or a _Git_-derived list), state which files it
  will touch and get confirmation — status changes carry history and are not undone by the plugin
- Always go through `scripts/audit.py`; never hand-edit, reformat, or delete `<root>/.git/audit.json`.
  Editing it directly risks clobbering the plugin's schema and losing history
- Report what changed after a `set`, including files reported `(unchanged)`
