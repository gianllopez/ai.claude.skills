# Code Review Standards

The code review process, held constant across every technology. This skill decides how a review
runs — its scope, its rubric, what counts as a finding, and how findings are written. It decides
nothing about what good code looks like: that comes from the best-practices skills installed
alongside it, and from the repository's own conventions.

That separation is the whole design. Adding a technology means adding a best-practices skill, not
editing this one.

## Structure

- `SKILL.md` — everything the skill does: the six-step workflow, the finding contract, the report
  format, the closing actions, and the directives
- `README.md` — this overview
- `metadata.json` — version, author, abstract, references

## Usage

An argument is always given — the skill never guesses a scope.

```bash
/review HEAD                # the last commit
/review c265c4a             # a commit by hash
/review c265c4a core/api/   # that commit, narrowed to a path
/review core/api/           # the files at that path, as they stand
/review core/api/ deep      # same scope, read exhaustively
```

Each argument is disambiguated with `git rev-parse --verify --quiet "<arg>^{commit}"`: it resolves
to a commit, or it is a path.

A commit argument makes the subject **a change**: only what that commit touched, with its message
saying what it set out to do. A path argument makes the subject **code as it stands**: no diff, so
every line at that path is in scope. `deep` is a modifier and does not change which of the two you
get. `SKILL.md` _Directive 2_ states both halves.

## What a review costs

| Step      | Questions asked                                                  |
| :-------- | :--------------------------------------------------------------- |
| Scope     | 0, except one when no argument was given at all                  |
| Standards | 0, except one when the scope spans two mutually exclusive stacks |
| Review    | 0                                                                |
| Contract  | 0                                                                |
| Report    | 0                                                                |
| Close     | 1, once, at the end                                              |

## Design decisions

Four choices carry the skill. Each is here because the obvious alternative was measured and cost
more.

### Tier 2, not Tier 3

A _Tier-3_ rule requires _Incorrect_/_Correct_ code examples. A technology-agnostic standard would
have to pick a language to write them in, which contradicts both the agnosticism and the
collection's rule that skills stay self-contained per technology. What this skill holds is a
procedure, so it is shaped like one.

### The rule index, never the compiled document

`AGENTS.md` is a distribution artifact, not a review input. Loading `react-core-best-practices`'s
alone costs ~114 KB before a single line of the scope is read, and a mixed scope loads more than
one.

The skill reads each matched skill's `SKILL.md` instead — its _Quick Reference_ is a complete index
of rule IDs at about 3 KB — selects the rules the scope plausibly touches, and reads only those at
about 6 KB each. Typical cost lands near 30 KB, and it scales with the size of the scope rather than
the size of the catalog.

### The finding contract

Every finding carries an anchor (`file:line` in the scope), a ground, and a fix (a minimal patch).
Two out of three is not a finding. The ground is normally a rule ID from a loaded standard; a
concrete failure scenario is accepted as a safety valve, for a real defect noticed while applying
the rules rather than hunted for.

It is a test anything can be put through, and it is what keeps the report short without a severity
threshold hiding anything — the explicit noise floor in `SKILL.md` catches whatever survives it. An
observation with no anchor is a remark, one with no ground is an opinion, one with no fix is a
complaint.

### Impact is inherited

Rules in this collection declare `impact: CRITICAL | HIGH | MEDIUM | LOW` in their frontmatter. A
finding copies that value verbatim rather than scoring the instance, so two reviews of the same
defect always agree and the rule's author keeps the judgment they already made. Only findings
grounded in a failure scenario are scored, by a fixed ladder in `SKILL.md`.

## Maintenance

- **A new technology** — write its best-practices skill. This skill discovers it by reading the
  `description` of every installed `SKILL.md`, so nothing here needs editing
- **A new closing action** — add it to _Step 6_ and its mechanics to _Closing Actions_
- **Everything lives in `SKILL.md`.** The skill is deliberately three files — the Tier 2 minimum. Do
  not split content back out into `references/`

## Related skills

| Skill              | Relationship                                                                                                       |
| :----------------- | :----------------------------------------------------------------------------------------------------------------- |
| `*-best-practices` | Supply the rules. This skill supplies the process                                                                  |
| `audit`            | Owns the review queue and the guard on `done` files; this skill only decides to exclude them from a review's scope |
| `commit`           | Where a review hands off once its fixes are applied                                                                |

## Acknowledgments

Originally created by [@gianllopez](https://github.com/gianllopez).
