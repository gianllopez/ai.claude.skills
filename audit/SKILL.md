---
name: audit
description: Reads the Neovim `audit` plugin's per-project review database to know each file's status (`pending`, `done`, or unaudited) and refuses to modify or propose changes to files already marked `done`. Use whenever editing, refactoring, or reviewing source files in a project tracked by the audit plugin, or when the user asks about file review states.
allowed-tools:
  - Bash
  - Read
license: MIT
metadata:
  author: gianllopez
  version: 1.0.0
---

# Audit State Guard

Consults the review state maintained by the user's _Neovim_ `audit` plugin and enforces one rule
above all: never modify or propose changes to a file that is marked `done`. The plugin stores,
per project and file by file, a review `status` with full history; this skill reads that database
(read-only) so _Claude Code_ respects the user's review progress.

## When to Apply

- Before editing, creating, deleting, or proposing changes to any file in a project that the
  audit plugin tracks — always check the target's status first
- The user types `/audit`
- The user asks about review state: _"what's the status of X?"_, _"which files are done?"_,
  _"what's left to review?"_, _"is this file audited?"_, etc
- Before a broad/multi-file refactor, to filter out files that are already `done`

## Status Semantics

| Status      | Icon | Meaning                         | Claude's behavior                         |
| :---------- | :--- | :------------------------------ | :---------------------------------------- |
| `done`      | ✅   | Reviewed and locked by the user | Do not change. Guard applies (see below). |
| `pending`   | ⏳   | Awaiting review                 | Edit freely                               |
| `unaudited` | ·    | Not present in the database     | Edit freely                               |

The database is read-only from this skill: setting a status is the exclusive job of the _Neovim_
plugin. Never write to the database files.

## How to Read the Status

The plugin stores each project's database in a single, fixed file: `<git-root>/.git/audit.json`.
Always use the bundled reader rather than parsing that file by hand:

```bash
python3 ~/.claude/skills/audit/scripts/audit.py status <path> [<path>...]
python3 ~/.claude/skills/audit/scripts/audit.py list [--status pending|done|unaudited]
```

- `status <path…>` — prints `<icon> <status> <path>` for each file. Exit code is `1` if any target
  is `done`, `0` otherwise, so it doubles as a guard check.
- `list` — prints every audited file in the current project; `--status` filters

Run the script from the project's working directory: it resolves the project root by walking up to
the nearest `.git` and reads `<root>/.git/audit.json`. If that file is absent, the project simply
has no audit data yet — the plugin writes it on the next status change.

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

- Always check a file's audit status before modifying or proposing changes to it in a tracked project
- Never edit, overwrite, or propose a diff for a file whose status is `done` without an explicit
  user override for that specific change
- Never write to, edit, or delete the plugin's database at `<root>/.git/audit.json`; this skill is
  strictly read-only
- When you skip a `done` file during a broader task, always surface it to the user rather than
  silently omitting the change
- If the reader reports a file as `unaudited`, treat it as editable — absence from the database is
  not the same as `done`
