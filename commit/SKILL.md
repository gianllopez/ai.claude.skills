---
name: commit
description: Analyzes staged changes and executes a git commit adhering to Conventional Commits
allowed-tools: [bash]
---

# Git Commit Skill

Automatically analyzes staged git changes and generates _Conventional Commits_ compliant messages with proper formatting and execution.

## When to Apply

This skill activates when:

- User types `/commit`
- User asks to _"commit changes"_, _"save changes"_, _"create commit"_
- User mentions _"conventional commits"_ or _"git commit"_
- Working directory has staged changes

## Context Analysis

Before generating the commit message, you must:

1.  **Check Status**: Run `git status` to confirm what is staged
2.  **Analyze Diff**: Run `git diff --staged` to understand the exact changes
3.  **User Input**: Consider any arguments provided (e.g., `/commit fixing auth bug`) as additional context for the commit intent

## Message Generation Rules (Strict)

You must generate a commit message that follows the _Conventional Commits_ specification, strictly adhering to these constraints:

- **Language**: The message must be written in _English_ only
- **Structure**: The message must consist of a header, a concise description paragraph, and a mandatory footer
- **Backticks Rule (CRITICAL)**:
  - **Scope**: The scope inside the parentheses must be enclosed in backticks (e.g., `feat(api):`)
  - **References**: All references to code members (variables, functions, classes, filenames) and third-party libraries (e.g., `react-query`, `axios`) must be enclosed in backticks in both the title and description
- **Forbidden**: Do not use bullet points or numbered lists. Do not use line breaks _inside_ the description paragraph itself
- **Footer (MANDATORY)**:
  - Leave one empty line after the description
  - Append the signature: `Co-Authored-By: Claude Code (<model>)`
  - Replace `<model>` with the specific name of the model generating this response (e.g., _Claude 3.5 Sonnet_, _Claude 3 Opus_)
- **Focus**: Summarize the most significant change only. Discard minor details
- **Types**: Use only: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

## Commit Type Guidelines

| Type       | When to Use                                         |
| :--------- | :-------------------------------------------------- |
| `feat`     | New features or significant functionality additions |
| `fix`      | Bug fixes                                           |
| `refactor` | Code restructuring without changing behavior        |
| `perf`     | Performance improvements                            |
| `style`    | Code formatting, whitespace, missing semicolons     |
| `docs`     | Documentation changes only                          |
| `test`     | Adding or updating tests                            |
| `chore`    | Maintenance tasks, dependency updates               |
| `build`    | Changes to build system or dependencies             |
| `ci`       | CI/CD configuration changes                         |

## Execution Protocol

1.  **Analyze** staged changes thoroughly
2.  **Generate** commit message following all rules above
3.  **Construct** the final git command using single quotes: `git commit -m '<message>'`. Single quotes prevent bash from interpreting backticks as subcommands, so the message is stored literally — do not escape backticks inside the message string
4.  **Execute** the command immediately using the _bash_ tool
5.  **Confirm** the commit was successful

**Important**: Do not ask for confirmation unless the `diff` is empty or confusing.

## Example Output

```bash
# After analyzing changes to authentication system
git commit -m 'fix(`auth`): resolve token expiration handling in `useSession` hook

Updated the `useSession` hook to properly check token expiration before making API requests. This prevents unnecessary 401 errors and improves user experience by proactively refreshing tokens when needed. The fix integrates with the existing `react-query` cache invalidation strategy.

Co-Authored-By: Claude Code (Claude 3.5 Sonnet)'
```

**Reference:** [Conventional Commits](http://conventionalcommits.org/en/v1.0.0/#specification)
