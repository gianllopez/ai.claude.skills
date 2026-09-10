---
name: git-best-practices
description: Version-control conventions for a project — Conventional Commits message format and Conventional Branch naming (including an agent-authored prefix), with `/commit` as the actionable command that analyzes staged changes and executes a compliant commit. Use when writing a commit message, running `/commit`, naming or creating a branch, or when the user mentions "conventional commits", "git commit", "commit convention", "branch naming", "conventional branch", or "git workflow". The rule catalog is meant to grow with future version-control precedents (merge strategy, tags, pull requests).
license: MIT
metadata:
  author: gianllopez
  version: 1.0.0
---

# Git Best Practices

Conventions for how a project uses _Git_, starting from the two decisions every contributor makes before a change is even reviewable: what the branch is called, and what the commit says. Each follows its own typed vocabulary — commits use the _Conventional Commits_ types (`feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`), branches use the smaller, purpose-built _Conventional Branch_ set (`feature`/`feat`, `bugfix`/`fix`, `hotfix`, `release`, `chore`) plus an agent-source prefix (`claude/`, `ai/`, …) for branches an AI agent creates — so a name always signals what kind of work it is, without pretending the two vocabularies are the same thing.

This skill is both a reference and an executor: it hosts the rule catalog (`rules/`, compiled into `AGENTS.md`) that future Git conventions get added to, and it owns the `/commit` command, which is the one convention here that also has to run as an action rather than only be checked against.

## When to Apply

Reference these guidelines when:

- Writing or reviewing a commit message
- Running `/commit`, or being asked to _"commit changes"_, _"save changes"_, _"create commit"_
- Naming a new branch, or reviewing an existing branch name
- Setting up version-control conventions for a new project

## Rule Categories by Priority

| Priority | Category        | Impact | Prefix    |
| -------- | --------------- | ------ | --------- |
| 1        | Commit Messages | HIGH   | `msg-`    |
| 2        | Branching       | MEDIUM | `branch-` |

## Quick Reference

### 1. Commit Messages (HIGH)

- `msg-conventional-commits` - typed, scoped header (`feat(`scope`):`), one prose paragraph, backticked code/library references, mandatory attribution footer

### 2. Branching (MEDIUM)

- `branch-naming-convention` - `<type>/<description>` per the Conventional Branch spec (`feature`, `bugfix`, `hotfix`, `release`, `chore`), or `claude/<description>` when Claude Code creates the branch

## Executing `/commit`

This is the one rule in this skill that is also a command: when triggered, actually run the commit rather than only describing the convention.

1. **Check status** — run `git status` to confirm what is staged
2. **Analyze diff** — run `git diff --staged` to understand the exact changes
3. **User input** — treat any arguments passed to `/commit` (e.g. `/commit fixing auth bug`) as additional context for the commit intent
4. **Generate** the message following `rules/msg-conventional-commits.md` in full
5. **Construct** the command using single quotes: `git commit -m '<message>'` — single quotes prevent bash from interpreting backticks as subcommands, so the message is stored literally; do not escape backticks inside the message string
6. **Execute** the command immediately
7. **Confirm** the commit succeeded

Do not ask for confirmation unless the diff is empty or confusing. Only commit when the user has asked for it in this conversation, or `/commit` was invoked directly — never commit proactively.

## How to Use

Read individual rule files for detailed explanations and examples:

```plaintext
rules/*.md
```

Each rule contains a brief rationale, an Incorrect example, a Correct example, and a reference.

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md` (generated — see `README.md`).
