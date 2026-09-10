---
title: Branch Naming Convention
impact: MEDIUM
description: Branches are named `<type>/<description>` per the Conventional Branch specification — a dedicated branch-purpose vocabulary, plus an `ai/`-family prefix for agent-authored branches, distinct from the Conventional Commits type set.
tags: branch, naming, workflow
---

## Branch Naming Convention

**Impact (MEDIUM):** A branch name is the first thing a teammate, a CI dashboard, or a stale-branch cleanup script sees, long before there is a diff or a PR description to read. `fix-stuff`, `test`, or a personal name tells none of them what the branch is for, whether it is urgent, or whether it is safe to delete. A fixed, small vocabulary of purposes makes a repository's branch list scannable and machine-filterable, and a dedicated prefix for agent-authored branches lets a reviewer tell at a glance which changes started with a human and which started with an AI agent.

**Guidelines:**

1. **Shape:** `<type>/<description>` — one `type`, a single `/`, then a description in hyphen-separated segments. Trunk branches (`main`, `master`, `develop`) carry no prefix and are exempt from this rule
2. **Purpose types (only these) — note this is its own vocabulary, not the _Conventional Commits_ type set:**
   - `feature` or `feat` — a new feature
   - `bugfix` or `fix` — a bug fix
   - `hotfix` — an urgent, out-of-cycle fix
   - `release` — release preparation (its description may hold a version number, e.g. `release/v1.2.0`)
   - `chore` — non-code maintenance
3. **Agent-source prefixes — use when the branch is created by an AI agent, in place of a purpose type:**
   - `claude/` — created by _Claude Code_
   - `ai/` — a generic fallback when no agent-specific prefix applies
   - `codex/`, `copilot/`, `cursor/` — other agents' equivalents, for repositories that work with more than one
   - When _Claude Code_ creates a branch on this repository's behalf, prefer `claude/<description>` over a purpose type
4. **Characters:** lowercase letters (`a-z`), digits (`0-9`), hyphens, and dots — dots appear only inside a `release/` version number, never in a description. No spaces, underscores, or uppercase letters anywhere
5. **No consecutive, leading, or trailing hyphens or dots**, and a hyphen may never sit directly next to a dot
6. **Ticket references are optional and embedded in the description**, not a separate segment: `feature/issue-123-new-login`, not `feature/123/new-login`
7. **One branch, one concern:** if the description needs "and" to describe it, the branch is doing two things and should split in two

**Incorrect (invalid type, uppercase, consecutive/leading hyphens, spaces):**

```
unknown/some-task
Feature/Add-Login
feature/new--login
feature/-new-login
fix/header bug
```

**Correct (valid type or agent prefix, clean hyphenation, optional ticket reference):**

```
feature/add-login-page
fix/header-bug
hotfix/expired-cert
release/v1.2.0
feature/issue-123-new-login
claude/security-patch
```

Reference: [Conventional Branch](https://conventionalbranch.org)
