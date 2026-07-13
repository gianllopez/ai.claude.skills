"""Read-only reader for the Neovim `audit` plugin database"""

from __future__ import annotations

import argparse
import json
import os
import sys

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


def relative(path: str, root: str) -> str:
    """`path` as a POSIX database key relative to `root`"""
    return os.path.relpath(os.path.abspath(path), root).replace(os.sep, "/")


def emit(status: str, key: str) -> None:
    """Print one `<icon> <status> <key>` row"""
    print(f"{ICONS.get(status, '?')} {status:<9} {key}")


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


def build_parser() -> argparse.ArgumentParser:
    """Build the `status` / `list` CLI"""
    parser = argparse.ArgumentParser(
        prog="audit.py",
        description="Read the Neovim audit plugin database",
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

    return parser


def main() -> int:
    """Parse arguments and dispatch to the chosen command"""
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
