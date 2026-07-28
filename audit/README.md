# Audit State Guard

An executable skill that lets _Claude Code_ read and update the review state maintained by the
user's _Neovim_ `audit` plugin (`~/.config/nvim/lua/custom/audit`): it refuses to modify files
already marked `done`, and can move files between `pending` and `done` when explicitly asked.

Like the other procedural skills in this repository, this is a small, linear skill read in full and applied as a policy — its structure is intentionally flat. It differs from the best-practices catalogs (`django-...`, `react-native-...`) that split rules into a `rules/` directory.

## Structure

- `SKILL.md` — The skill definition: trigger conditions, status semantics, the read/write procedures,
  and the guard directives that govern behavior
- `scripts/audit.py` — A reader and writer for the plugin's per-project database
- `metadata.json` — Document metadata (version, author, date, abstract, references)

## What it does

1. **Resolves the database** — walks up from the working directory to the nearest `.git` and reads
   the plugin's per-project database, `<git-root>/.git/audit.json`. No hashing is involved: the
   plugin stores the data at this fixed path
2. **Reports status** — for any file: `done` (✅), `pending` (⏳), or `unaudited` (·, absent from the
   database)
3. **Guards edits** — before changing or proposing a diff for a file, _Claude_ checks its status and
   refuses to touch anything marked `done` unless the user explicitly overrides
4. **Sets status** — on an explicit request, moves files between `pending` and `done`, appending to
   each file's history exactly as the plugin does

## The plugin's storage contract (shared with `scripts/audit.py`)

The plugin stores each project's database in a single file, `<git-root>/.git/audit.json`, which this
skill reads and writes directly.

| Aspect         | Value                                                                     |
| :------------- | :------------------------------------------------------------------------ |
| Database       | `<git-root>/.git/audit.json`                                              |
| `project_root` | nearest ancestor directory containing `.git`                              |
| Keys           | _POSIX_ paths relative to the root (matching `git ls-files`)              |
| Entry          | `{ "status": "pending" \| "done", "history": [{ "status", "at" }, ...] }` |
| Timestamps     | `at` is UTC, `%Y-%m-%dT%H:%M:%SZ`, appended on every status change        |
| Encoding       | compact _JSON_, no spaces (what `vim.json.encode` emits)                  |
| Statuses       | `pending` ⏳ · `done` ✅ · _absent_ = unaudited                           |

## Usage

```bash
# Status of specific files (exit code 1 if any target is `done`)
python3 ~/.claude/skills/audit/scripts/audit.py status src/auth.py src/models.py

# Every audited file in the current project
python3 ~/.claude/skills/audit/scripts/audit.py list

# Only the files awaiting review
python3 ~/.claude/skills/audit/scripts/audit.py list --status pending

# Change a status (`pending` or `done`); files already at that status are left alone
python3 ~/.claude/skills/audit/scripts/audit.py set done src/auth.py

# Bulk selections come from Git, mirroring the plugin's `bulk_set_*` commands
python3 ~/.claude/skills/audit/scripts/audit.py set pending $(git diff-tree --no-commit-id -r --name-only HEAD)
```

## Why it writes the database directly

The plugin's own writers (`utils.save`, `bulk_set`) resolve their target from the _current buffer_
(`vim.fn.expand("%:p")`), so reusing them would mean booting `nvim --headless` with each file loaded
— along with `nui.nvim` and `fzf-lua` — and `M.open()`/`M.filter()` are interactive UI that cannot
run headless at all. Writing `audit.json` is the cheaper and more robust path: the schema is small
and fixed, and the plugin re-reads it from disk on every operation with no in-memory cache, so
neither side can clobber the other. `scripts/audit.py` mirrors `utils.save` exactly — same key
format, same UTC timestamp, same history append, same skip when the status is unchanged — and
replaces the file atomically (`os.replace`).

## Notes

- **Single source of truth.** The skill does not re-implement any of the plugin's discovery or
  status logic; it reads and writes the same `<root>/.git/audit.json`, so the two can't drift
- **Writes are opt-in.** `set` runs only when the user explicitly asks for a status change. In
  particular, the skill must never demote a `done` file to `pending` to get around its own guard
- **No path back to `unaudited`.** Removing an entry also destroys its history, so that stays with
  the plugin (`clear_file_history`, `clean_orphans`)
- A skill only guards while it is loaded. For a hard, unconditional block on every edit, pair this
  with a `PreToolUse` hook in `settings.json` that runs `audit.py status --... && exit 2` on `done`
  targets. This skill deliberately ships without that hook
