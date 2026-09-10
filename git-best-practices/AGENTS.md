# Git Best Practices

**Version 1.0.0**  
_Gian López_  
_September 2026_

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring version-controlled codebases. Humans  
> may also find it useful, but guidance here is optimized for automation  
> and consistency by AI-assisted workflows.

---

## Abstract

Version-control conventions for projects, covering both what a commit message looks like and what a branch is called before a single line of it is written. Commit messages follow _Conventional Commits_: a typed, scoped header, a single plain-prose paragraph, backticked references to code members and libraries, and a mandatory attribution footer. Branch names follow the _Conventional Branch_ specification: a purpose-built type vocabulary (`feature`/`feat`, `bugfix`/`fix`, `hotfix`, `release`, `chore`) distinct from the commit type set, a hyphen-and-dot character grammar, and an agent-source prefix family (`claude/`, `ai/`, `codex/`, `copilot/`, `cursor/`) for branches an AI agent creates. The `/commit` command is the actionable entry point: it analyzes staged changes and executes a commit that already satisfies the message rule. The rule catalog is deliberately built to grow — merge strategy, tagging, and pull-request conventions are the next precedents to add here rather than in a separate skill.

---

## Table of Contents

1. [Commit Messages](#1-commit-messages) — `HIGH`
   - [1.1 Conventional Commit Messages](#11-conventional-commit-messages)
2. [Branching](#2-branching) — `MEDIUM`
   - [2.1 Branch Naming Convention](#21-branch-naming-convention)

---

## 1. Commit Messages

### 1.1 Conventional Commit Messages

**Impact (HIGH):** A commit message is read far more often than it is written — by a reviewer scanning history, by `git blame`, by a changelog generator, by the next person bisecting a regression. An untyped, unscoped, free-form message forces every one of those readers to open the diff to learn what a commit even is. A consistent type + scope + description lets history be scanned, filtered (`git log --grep '^feat'`), and mechanically turned into a changelog. The cost of getting it wrong compounds silently: nothing breaks the build, but the history becomes unsearchable over time.

**Guidelines:**

1. **Header:** `<type>(`<scope>`): <summary>` — the scope, in backticks, is the module/package/file the change centers on; the summary is imperative mood, lowercase, no trailing period
2. **Types (only these):** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
3. **Description:** one plain-prose paragraph after a blank line — no bullet points, no numbered lists, no line breaks inside the paragraph itself. Summarize the most significant change only; discard minor details
4. **Backticks (critical):** every reference to a code member (variable, function, class, filename) or third-party library (`react-query`, `axios`) is wrapped in backticks, in both the header and the description
5. **Footer (mandatory):** one blank line after the description, then the attribution line exactly as the project's active attribution instructions specify for the current session — never fabricated or reused from a prior session
6. **Language:** the message is written in _English_ only, regardless of the language used to discuss the change

**Incorrect (untyped, unscoped, no backticks, prose lost in a list):**

```
fixed bug in useSession

- token was expiring
- added a refresh check
- tested manually
```

**Correct (typed, scoped, backticked, single prose paragraph, footer):**

```
fix(`auth`): resolve token expiration handling in `useSession` hook

Updated the `useSession` hook to properly check token expiration before making API requests. This prevents unnecessary 401 errors and improves user experience by proactively refreshing tokens when needed. The fix integrates with the existing `react-query` cache invalidation strategy.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
```

Reference: [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#specification)

---

## 2. Branching

### 2.1 Branch Naming Convention

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
   - When Claude Code creates a branch on this repository's behalf, prefer `claude/<description>` over a purpose type
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
