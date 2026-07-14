---
name: <skill-name>
description: <What this best-practices skill governs AND when to use it. Include trigger words. ≤ 1024 chars, no "claude"/"anthropic">
license: MIT
metadata:
  author: <handle>
  version: 1.0.0
---

# <Title>

<One paragraph: the domain this skill standardizes and the outcomes it optimizes for>

## When to Apply

Reference these guidelines when:

- <situation 1>
- <situation 2>

## Rule Categories by Priority

| Priority | Category   | Impact | Prefix      |
| -------- | ---------- | ------ | ----------- |
| 1        | <Category> | HIGH   | `<prefix>-` |
| 2        | <Category> | MEDIUM | `<prefix>-` |

## Quick Reference

### 1. <Section> (<IMPACT>)

- `<prefix>-<rule>` - <one-line summary>

## How to Use

Read individual rule files for detailed explanations and examples:

```
./rules/*.md
```

Each rule contains a brief rationale, an Incorrect example, a Correct example, and a reference.

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md` (generated — see `README.md`).
