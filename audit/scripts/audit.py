"""Reader and writer for the Neovim `audit` plugin database"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import tempfile

ICONS = {"pending": "⏳", "done": "✅", "unaudited": "·"}


def resolve_root(start: str) -> str:
    """Absolute path of the Git repository that contains `start`"""
    current = os.path.abspath(start)

    while not os.path.exists(os.path.join(current, ".git")):
        parent = os.path.dirname(current)

        if parent == current:
            raise SystemExit("audit: not inside a Git repository")

        current = parent

    return current


def database_path(root: str) -> str:
    """Project-local database the plugin writes: <root>/.git/audit.json"""
    return os.path.join(root, ".git", "audit.json")


def read_database(root: str) -> dict:
    """Load the database for `root`; empty dict if missing or unreadable"""
    path = database_path(root)

    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, OSError) as error:
        print(f"audit: could not read {path}: {error}", file=sys.stderr)
        return {}

    return data if isinstance(data, dict) else {}


def write_database(root: str, database: dict) -> None:
    """Atomically persist `database`, matching the plugin's compact encoding"""
    path = database_path(root)
    payload = json.dumps(database, separators=(",", ":"), ensure_ascii=False)

    handle, temporary = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")

    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(payload)
        os.replace(temporary, path)
    except OSError as error:
        os.unlink(temporary)
        raise SystemExit(f"audit: could not write {path}: {error}")


def relative(path: str, root: str) -> str:
    """`path` as a POSIX database key relative to `root`"""
    return os.path.relpath(os.path.abspath(path), root).replace(os.sep, "/")


def emit(status: str, key: str, suffix: str = "") -> None:
    """Print one `<icon> <status> <key>` row"""
    print(f"{ICONS.get(status, '?')} {status:<9} {key}{suffix}")


def cmd_status(args: argparse.Namespace) -> int:
    """Print each file's status; exit 1 if any target is `done`"""
    root = args.root or resolve_root(args.paths[0])
    database = read_database(root)

    any_done = False

    for path in args.paths:
        key = relative(path, root)
        status = (database.get(key) or {}).get("status", "unaudited")
        any_done = any_done or status == "done"
        emit(status, key)

    return 1 if any_done else 0


def cmd_list(args: argparse.Namespace) -> int:
    """List audited files for the current project, optionally filtered by status"""
    root = args.root or resolve_root(os.getcwd())
    database = read_database(root)

    rows = sorted(
        (entry.get("status", "unaudited"), key) for key, entry in database.items()
    )

    if args.status:
        rows = [row for row in rows if row[0] == args.status]

    for status, key in rows:
        emit(status, key)

    if not rows:
        target = args.status or "any status"
        print(
            f"audit: no files with {target} in {database_path(root)}", file=sys.stderr
        )

    return 0


def cmd_set(args: argparse.Namespace) -> int:
    """Set the status of one or more files, recording the change in their history"""
    root = args.root or resolve_root(args.paths[0])

    keys = []
    missing = []

    for path in args.paths:
        key = relative(path, root)

        if not os.path.isfile(os.path.join(root, key)):
            missing.append(key)

        keys.append(key)

    if missing:
        for key in missing:
            print(f"audit: not a file in {root}: {key}", file=sys.stderr)

        return 1

    database = read_database(root)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    changed = 0

    for key in keys:
        entry = database.get(key) or {}
        history = entry.get("history")

        if not isinstance(history, list):
            history = []

        if entry.get("status") == args.status:
            emit(args.status, key, " (unchanged)")
            continue

        history.append({"status": args.status, "at": now})

        entry["status"] = args.status
        entry["history"] = history
        database[key] = entry

        emit(args.status, key)

        changed += 1

    if changed:
        write_database(root, database)

    print(f"audit: {changed} file(s) set to `{args.status}`", file=sys.stderr)

    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the `status` / `list` CLI"""
    parser = argparse.ArgumentParser(
        prog="audit.py",
        description="Read and update the Neovim audit plugin database",
    )
    parser.add_argument(
        "--root",
        help="Project root (default: the Git repository containing the target)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="Print the status of one or more files")
    status.add_argument("paths", nargs="+", help="File paths (relative or absolute)")
    status.set_defaults(func=cmd_status)

    listing = sub.add_parser("list", help="List audited files, optionally filtered")
    listing.add_argument(
        "--status",
        choices=["pending", "done", "unaudited"],
        help="Only show files with this status",
    )
    listing.set_defaults(func=cmd_list)

    setter = sub.add_parser("set", help="Set the status of one or more files")
    setter.add_argument("status", choices=["pending", "done"], help="Status to apply")
    setter.add_argument("paths", nargs="+", help="File paths (relative or absolute)")
    setter.set_defaults(func=cmd_set)

    return parser


def main() -> int:
    """Parse arguments and dispatch to the chosen command"""
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
