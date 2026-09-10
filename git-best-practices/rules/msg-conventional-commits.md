---
title: Conventional Commit Messages
impact: HIGH
description: Every commit message follows Conventional Commits — a typed, scoped header, a plain-prose description, and a mandatory attribution footer.
tags: commit, message, format, changelog
---

## Conventional Commit Messages

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
