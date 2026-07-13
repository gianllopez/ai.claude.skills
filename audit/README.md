# Audit State Guard

An executable skill that lets _Claude Code_ read the review state maintained by the user's _Neovim_
`audit` plugin (`~/.config/nvim/lua/custom/audit`) and refuse to modify files already marked
`done`.

Like the other procedural skills in this repository, this is a small, linear skill read in full and applied as a policy — its structure is intentionally flat. It differs from the best-practices catalogs (`django-...`, `react-native-...`) that split rules into a `rules/` directory.

## Structure

- `SKILL.md` — The skill definition: trigger conditions, status semantics, the read procedure, and
  the guard directives that govern behavior
- `scripts/audit.py` — A read-only reader for the plugin's per-project database
- `metadata.json` — Document metadata (version, author, date, abstract, references)

## What it does

1. **Resolves the database** — walks up from the working directory to the nearest `.git` and reads
   the plugin's per-project database, `<git-root>/.git/audit.json`. No hashing is involved: the
   plugin stores the data at this fixed path
2. **Reports status** — for any file: `done` (✅), `pending` (⏳), or `unaudited` (·, absent from the
   database)
3. **Guards edits** — before changing or proposing a diff for a file, _Claude_ checks its status and
   refuses to touch anything marked `done` unless the user explicitly overrides

## The plugin's storage contract (read by `scripts/audit.py`)

The plugin stores each project's database in a single file, `<git-root>/.git/audit.json`, which this
skill reads directly.

| Aspect         | Value                                                        |
| :------------- | :----------------------------------------------------------- | ----------------------------------------------- |
| Database       | `<git-root>/.git/audit.json`                                 |
| `project_root` | nearest ancestor directory containing `.git`                 |
| Keys           | _POSIX_ paths relative to the root (matching `git ls-files`) |
| Entry          | `{ "status": "pending"                                       | "done", "history": [{ "status", "at" }, ...] }` |
| Statuses       | `pending` ⏳ · `done` ✅ · _absent_ = unaudited              |

## Usage

```bash
# Status of specific files (exit code 1 if any target is `done`)
python3 ~/.claude/skills/audit/scripts/audit.py status src/auth.py src/models.py

# Every audited file in the current project
python3 ~/.claude/skills/audit/scripts/audit.py list

# Only the files awaiting review
python3 ~/.claude/skills/audit/scripts/audit.py list --status pending
```

## Notes

- **Read-only by design.** Setting a status is the exclusive job of the _Neovim_ plugin; this skill
  never writes to the database, avoiding clobbering the plugin's copy (and its history)
- **Single source of truth.** The skill does not re-implement any of the plugin's storage logic; it
  reads the same `<root>/.git/audit.json` the plugin writes, so the two can't drift
- A skill only guards while it is loaded. For a hard, unconditional block on every edit, pair this
  with a `PreToolUse` hook in `settings.json` that runs `audit.py status --... && exit 2` on `done`
  targets. This skill deliberately ships without that hook
