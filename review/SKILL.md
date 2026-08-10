---
name: review
description: Runs a code review against the standards a project already declares. Takes a commit, a path, or a commit narrowed to a path; detects the stack, loads the matching best-practices skills, and reports findings ranked by impact — each with its rule, one sentence of rationale, and a minimal patch. Technology-agnostic: it owns the review process, never the language rules. Use when the user asks to review a commit, the last commit, a file, or a directory, or types /review.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Edit
  - AskUserQuestion
license: MIT
metadata:
  author: gianllopez
  version: 1.0.0
---

# Code Review Standards

Runs the same review every time, whatever the stack. This skill owns the _process_: what gets
reviewed, which standards apply to it, what earns the name _finding_, and how a finding is written.

It owns no language rules of its own. Those come from the best-practices skills already installed
and from the repository's own conventions — which is what makes the skill technology-agnostic
without being vague. It never says _"use `select_related`"_; it says _"a finding cites a rule or a
failure scenario, and inherits that rule's impact"_.

**The constraint that shapes every decision below:** a review must be fast enough to run on every
change. Four things make reviews slow — reviewing more than the change, reporting more than the
findings, writing more than the reader needs, and asking before starting. Each step below closes one
of them.

## When to Apply

- The user types `/review <commit>`, `/review <path>`, or `/review <commit> <path>`
- The user asks to _"review the last commit"_, _"revisa este archivo"_, _"review c265c4a"_, etc
- The user wants a commit checked before it is pushed, or a module read against the standards
- A task finishes with a commit and the user asks whether it is sound

Do not run it to answer a question about code, to explain an implementation, or as an unrequested
follow-up to work just written — a review is something the user asks for.

## Workflow

| Step          | Resolved by                                     | Costs the user |
| :------------ | :---------------------------------------------- | :------------- |
| 1 · Scope     | the argument, disambiguated against _Git_       | nothing¹       |
| 2 · Standards | the scope's paths + the installed skills        | nothing²       |
| 3 · Review    | the rubric, at the requested depth              | nothing        |
| 4 · Contract  | every candidate finding passes it or is dropped | nothing        |
| 5 · Report    | one block per finding, ranked                   | reading time   |
| 6 · Close     | one question, once                              | one answer     |

¹ Only when no argument was given — see _Step 1_.  
² Only when the scope spans two mutually exclusive stacks — see _Step 2_.

### Step 1 · Resolve the scope

An argument is always given — the skill never guesses a scope. Three forms:

| Invocation                   | Scope                                       | Subject    |
| :--------------------------- | :------------------------------------------ | :--------- |
| `/review <commit>`           | Everything that commit changed              | a change   |
| `/review <commit> <path>...` | What that commit changed inside those paths | a change   |
| `/review <path>...`          | The files at those paths, as they stand     | code as-is |

`<commit>` is `HEAD` for the last one, or any hash or ref; `deep` combines with all three.

Disambiguate every argument instead of guessing from its shape — a short hash and a filename can
look alike:

```bash
git rev-parse --verify --quiet "<arg>^{commit}"   # exit 0 → a commit · non-zero → a path
```

At most one argument resolves to a commit; the rest are paths. If none does, the subject is code
as-is. A branch name resolves to its tip commit, which is a harmless superset. If no argument was
given at all, ask which commit or path — never default to `HEAD`, and never fall back to reviewing
the working tree.

**Read the scope:**

```bash
git show --stat <commit>          # what it touched
git show <commit>                 # the change itself
git show <commit> -- <path>...    # the change, narrowed to paths
git log -1 --format=%B <commit>   # its stated purpose
```

A path scope does not involve _Git_ at all: list the files under the path and read them.

**Read the commit message.** It states what the change set out to do, which is what tells a
deliberate behavior change apart from an accidental one — the noise floor in _Step 4_ excludes the
first and not the second. A path scope has no message and no stated purpose, so that exclusion
simply has nothing to apply to.

**Exclusions.** Lock files, generated artifacts, vendored directories, and `AGENTS.md` files
compiled from rules are not reviewed — report them as excluded in one clause rather than reading
them.

**The audit queue.** In a repository the `audit` skill tracks, check the scope's files against it
and drop the ones marked `done`: the user already read them line by line, so reviewing them again
spends time re-deriving a conclusion they reached. Name the count in the report header
(`2 files skipped (audit: done)`) — never drop them silently, because _"no findings"_ over a
filtered scope is a false result.

That exclusion is this skill's alone. The `audit` guard governs _writing_, so nothing stops a `done`
file from being read: if the user asks for one to be reviewed anyway, review it. Everything else —
how to read a status, when a status may change, and the guard on editing a `done` file — belongs to
the `audit` skill and is not restated here.

### Step 2 · Load the standards

When the user names the standards, detection does not run. _"review HEAD against react-core
only"_, _"revísalo solo contra las reglas de DRF"_ — load exactly what was named, state it in the
header, and skip the rest of this step.

The companion rule below is not applied silently over an explicit request. If the user names a skill
whose description declares a companion they did not name, load exactly what they asked for and say
in one clause which companion's rules went unapplied — never add it behind their back, and never
refuse the request.

#### Discover what is installed

Never assume a fixed catalog — the user authors new skills, and a hardcoded map goes stale:

```bash
grep -H '^description:' ~/.claude/skills/*/SKILL.md .claude/skills/*/SKILL.md 2>/dev/null
```

The path gives each skill's name, the description says what it governs and when it applies. Match
the files in scope against those descriptions.

#### Match the stack

Detect from the scope's paths and extensions first, then confirm with the manifests actually
present (`package.json`, `pyproject.toml`, `requirements.txt`, `app.json`, `app.config.*`, `go.mod`).
As a worked example of the shape of the mapping — not as its source of truth. Every row is a
complete answer, never an increment, and no row lists half of a pair the descriptions declare
together:

| Signal in the scope                                                                 | Standards to load                                                       |
| :---------------------------------------------------------------------------------- | :---------------------------------------------------------------------- |
| _React_ files, plus `expo` in `package.json`, `app.json`, or `react-native` imports | `react-core-best-practices` and `react-native-with-expo-best-practices` |
| _React_ files, plus `react-dom`, a router, `.html`, or _Tailwind_ theme files       | `react-core-best-practices` and `react-best-practices`                  |
| _React_ files with no platform signal either way                                    | `react-core-best-practices` alone                                       |
| `.py` importing `django` or `rest_framework`                                        | `django-rest-framework-best-practices`                                  |
| any scope at all                                                                    | the repository's `CLAUDE.md` / `AGENTS.md`, in addition                 |

_React_ files means `.tsx` / `.jsx`, or `.ts` importing `react`.

The repository's own conventions outrank every generic standard. When they conflict, the repository
wins and the finding cites the repository.

#### Close the set over declared companions

A skill's `description` may state that another has to be loaded with it. Where it does, that
statement is binding: match one and you have matched both. The wording to look for reads like
_"…lives in X, which a … project loads alongside this one"_.

After matching, re-read the description of every matched skill, add any companion it names, and
repeat until the set stops growing. Do this even when the mapping above already produced the pair —
the mapping is an example, the descriptions are the source of truth.

Why it is a rule and not a nicety: a skill that declares a companion is telling you it is partial.
It governs its own slice and says where the rest lives. Load it alone and the review runs against a
fraction of the standards that apply, then reports how little it found — which is indistinguishable
from a clean review.

**A declared companion missing from the resolved set is a bug in this step, not a valid outcome.**
The report header names the set; read it back before writing findings.

**The one question.** If the scope spans two stacks whose standards are mutually exclusive — a
monorepo holding both a web app and an _Expo_ app — ask once with `AskUserQuestion`, offering the
detected sets and recommending the one matching the bulk of the scope. Ambiguity is the only reason
to ask, and a set completed by the companion rule is not ambiguous. A scope matching nothing is not
ambiguous either: there is no standard to apply, so the review falls to the repository's own
conventions alone — and if it has none, the report says the review had nothing to enforce rather
than inventing something.

#### Load the index, then only the rules the scope needs

**Never read a skill's `AGENTS.md`.** It is the compiled distribution artifact, not the review input.

Load in three steps instead:

1. **Index** — read the matched skill's `SKILL.md`. Its _Quick Reference_ lists every rule ID with a
   one-line summary, for about 3 KB
2. **Select** — from the scope, pick the rule IDs whose summary plausibly touches what it holds
3. **Read** — read only those `rules/<id>.md`, about 6 KB each

### Step 3 · Review

Two passes:

1. **Standards** — the rules loaded in _Step 2_
2. **Project conventions** — the repository's `CLAUDE.md` / `AGENTS.md`, which outrank the standards
   wherever the two disagree

This skill hunts for nothing else, and carries no defect taxonomy of its own. What counts as wrong
is what a loaded rule says is wrong, plus what the repository wrote down. A defect no rule claims is
reported only if it is noticed while applying them — see _Step 4_ — and never searched for.

#### Depth

| Mode              | Reads                                                                                                                                                                              |
| :---------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `quick` (default) | on a commit, the diff plus enough surrounding lines to judge each hunk; on a path, the files themselves; both add the selected rules and the repository's conventions              |
| `deep`            | all of the above, plus each modified file in full, the call sites of every changed signature, the adjacent tests, and `git log -L` / `git blame` on hunks that rewrite recent work |

`deep` is for changes that earn it — a refactor across modules, a migration, anything touching
authorization. Do not promote a review to `deep` on your own; run what was asked, and if the change
clearly warranted more, say so in one clause at the end of the report.

### Step 4 · The finding contract

This is the filter that keeps a review short, and it applies to every candidate without exception.
A finding carries three things:

1. **Anchor** — a `file:line` inside the scope under review
2. **Ground** — a rule ID from a loaded standard, or a concrete failure scenario: an input or
   state, and the wrong output or crash it produces
3. **Fix** — the minimal patch that resolves it

Missing any of the three, it is not a finding. An observation with no anchor is a remark, one with
no ground is an opinion, and one with no fix is a complaint. None of them go in the report.

The second ground is a safety valve, not an invitation. _Step 3_ is explicit that this skill
does not hunt for defects no rule claims. But a reviewer who trips over a real one while applying
the rules reports it instead of stepping around it — a secret in the diff, an inverted condition, an
error path that leaves the system half-changed. It earns the same anchor and the same minimal patch
as any other finding, and the ladder below scores it because no rule declared its impact.

#### Impact

Reported flat: all four levels appear in the report, in detail, ordered strongest first.

| Level    | Grounded in a rule           | Grounded in a failure scenario                                                             |
| :------- | :--------------------------- | :----------------------------------------------------------------------------------------- |
| CRITICAL | the impact the rule declares | wrong output, data loss, or an exploitable hole on a path the change makes reachable       |
| HIGH     | the impact the rule declares | fails on a realistic input, or an ownership/strategy choice that is costly to unwind later |
| MEDIUM   | the impact the rule declares | degrades performance, resource use, or robustness under load                               |
| LOW      | the impact the rule declares | a named, concrete cost to clarity or consistency — never a preference                      |

A rule's declared `impact` is copied verbatim. Never re-score it because the instance felt milder:
the rule already made that judgment, and re-scoring makes two reviews of the same defect disagree.

#### Never reported

The noise floor. Each of these is a real thing someone could say about the code, and none of them
belong in a review the user reads before committing:

- Anything a formatter, linter, typechecker, or compiler already catches — those run separately
- On a commit scope, pre-existing issues on lines the commit did not touch, unless the commit
  makes them wrong. A path scope has no such exclusion — every line in it is the subject
- Style that no loaded rule and no repository convention states
- Missing tests as a blanket complaint. A specific branch the change makes reachable and leaves
  untested is a finding; _"add tests"_ is not
- An alternative approach with no named defect in the current one — _"you could also do X"_
- Behavior changes that are the stated point of the change
- A rule the code explicitly silences with a documented suppression

### Step 5 · Report

The report is the whole answer. It opens the turn — no preamble — and nothing follows it but the
closing question.

#### Header

```markdown
**Reviewing** 3 files · +214/−38 · commit `c265c4a`
**Standards** react-core-best-practices · react-native-with-expo-best-practices · CLAUDE.md
**Findings** 6 — 1 CRITICAL · 2 HIGH · 2 MEDIUM · 1 LOW
```

The first line names the scope in the shape it was resolved:

```text
… · commit `c265c4a`                    a whole commit
… · commit `c265c4a` ∩ `core/api/`      a commit narrowed to paths
4 files · 612 lines · `core/api/`       a path, where there is no diff to count
```

State excluded and skipped files here in one clause when there were any: `2 files skipped (audit:
done)`, `lock files excluded`.

#### One block per finding

Ordered by impact, then by file. Numbered continuously across the whole report.

````text
#### 1 · CRITICAL · `core/api/invoices/use-invoices.ts:22`

The effect fetches data — `state-effect-discipline`
It re-fires on every render and never cancels on unmount, so a slow response overwrites a newer one.

```diff
- useEffect(() => { fetch(url).then(setData) }, [])
+ const { data } = useInvoices()
```
````

The four parts, in order, every time:

- **Heading** — `#### <n> · <IMPACT> · ` then the anchor as inline code. Nothing else
- **Defect** — one clause naming what is wrong, then a spaced em dash and the rule ID in backticks. Omit the
  rule when the ground is a failure scenario
- **Rationale** — exactly one sentence, and it states the consequence. _"It re-fires on every render
  and never cancels on unmount"_ is a consequence; _"effects should not fetch"_ is a restatement of
  the rule, and the reader already read the rule ID
- **Patch** — a `diff` fence with the minimum change. No unchanged context beyond what places the
  edit. If the fix cannot be shown in a few lines, show the shape of it and say what the rest
  entails in the same sentence — never expand the block

#### No findings

One line, naming what was actually checked so the result is falsifiable:

```markdown
No findings. Reviewed 7 files against react-core-best-practices, react-native-with-expo-best-practices, and CLAUDE.md.
```

#### Language

The report follows the language the user is writing in. The skill's own files stay in _English_;
what the user reads does not have to.

### Step 6 · Close

The review is not finished when the findings are written — it is finished when the user has been
asked what to do with them. In the same turn as the report, call `AskUserQuestion` once, with
`multiSelect`, offering only the actions that apply:

- **Apply the fixes** — all of them, or a subset the user picks
- **Mark the files with findings as `pending`** — offered only when the repository has an audit
  database
- **Continue to `/commit`** — offered only after fixes were applied, since that is what puts
  changes in the working tree

On no findings, the question narrows to whatever remains useful, and disappears entirely when
nothing does. The mechanics of all three are in _Closing Actions_ below.

## Closing Actions

The mechanics behind the three actions offered in _Step 6_. The audit filter that runs _before_ a
review is in _Step 1_.

### Marking files `pending`

Scope it to the files that carried findings, not to everything reviewed — a clean file has nothing
new for the user to look at. The `audit` skill owns the rest: how the status is written, and the
rule that it is written only when the user asks in the same turn.

### Applying the fixes

Fixes land in the working tree, never in history. Reviewing commit `c265c4a` and applying a fix
produces new uncommitted changes on top of it; it does not amend, rebase, or rewrite that commit.
Never do so unless the user asks for it in those words.

**Apply exactly what the report showed.** The user approved the patch they read. A fix that grew
between the report and the edit is a different fix, and it was never approved. If the better
solution only became clear while editing, stop, say what changed, and ask.

Order strongest impact first, so a run that has to stop partway has resolved the worst of it.

**When a patch no longer applies** — the file moved on, another change landed, the anchor drifted —
skip it, name it, and do not improvise a replacement. A finding that cannot be applied as written
goes back to the user, not into a fix they have not seen.

**Change nothing that was not a finding.** Being inside the file is not a reason to fix something
adjacent; that edit has no finding, no rationale, and no approval, and it lands in a diff the user is
about to commit.

Close by reporting what was applied and what was not — and stop. Do not re-review the result. The
review already ran, the patches came from it, and a second pass over the same change is the loop that
makes reviews expensive. If the user wants the applied state reviewed, they will ask.

### Continuing to `/commit`

Offered only when fixes were applied in this run — that is the only thing that puts changes in the
working tree, and without changes there is nothing to commit. A clean review of an existing commit
ends without this option.

Hand off to the `commit` skill and let it do its own work: it analyzes the staged changes and writes
the _Conventional Commit_. Do not compose the message here, and do not stage or commit anything
because the review went well. The user picking the action is the approval to hand off, not the
approval to commit.

If findings remain unapplied, the option is not offered. Committing over a known finding is a
decision the user can make deliberately by asking — never one this skill suggests.

---

# 🔧 User Directives

> These blocks define the skill's _behavior_. Directives 1–2 govern how a review starts, 3–6 what
> becomes a finding, 7 how it is written, and 8 how it ends.

## 🔧 Directive 1 — Resolve, do not ask

A review starts with zero questions. Scope comes from the argument, standards come from the scope's
paths and the installed skills, and both are stated in the report header so the user can see what
was assumed and correct it in one word.

Two questions are allowed, and only these: _Step 1_'s, when no argument was given at all, and
_Step 2_'s, when the scope spans two mutually exclusive stacks. Nothing else earns a question before
the report — not the depth, not whether to include a file. Pick the documented default, state it,
and review.

## 🔧 Directive 2 — Review the scope, not the repository

The subject is whatever the argument named, and it never grows.

On a commit scope the subject is the change. Code the commit did not touch is out of scope even
when it is worse than the code that changed, with one exception: the commit makes it wrong. A
renamed field whose old consumers now break is a finding on the commit, not on the consumers.

On a path scope the subject is the files at that path, in full — there is no diff, so every line
in them is fair game. What stays outside is everything else: a call site in another module is
context to read, never a place to look for findings.

This is what keeps a review's cost proportional to what was asked for, which is the only reason it
can run on every commit.

## 🔧 Directive 3 — The contract is not negotiable

Anchor, ground, and fix. All three, on every finding, or it does not go in the report. When a
candidate has only two, the choice is to do the work that produces the third or to drop it — never
to publish it partial and let the user finish it.

## 🔧 Directive 4 — Never invent a standard

If no loaded rule covers it and no repository convention states it, it is not a finding — the one
exception being a real defect noticed in passing, which _Step 4_'s second ground admits. A
preference that has never been written down does not become a standard by appearing in a review.

When something genuinely worth standardizing turns up, say so in one clause after the findings and
offer to add a rule to the relevant skill. That is a proposal, not a finding, and it never gets a
numbered block.

## 🔧 Directive 5 — Impact is inherited, never invented

A rule declares its `impact`. Copy it verbatim into the finding. Only findings grounded in a failure
scenario are scored here, and only by the ladder in _Step 4_.

Re-scoring a rule's impact because this instance felt minor is how two reviews of the same defect
end up disagreeing, and it quietly overrides a judgment the rule's author already made deliberately.

## 🔧 Directive 6 — Confidence is part of the contract, not a disclaimer

A finding that cannot be verified from what was read is not hedged into the report with _"this may
be"_ or _"consider whether"_. Either read enough to confirm it — the call site, the type, the
migration — or drop it.

The one legitimate hedge is a finding that depends on runtime information no amount of reading
supplies. Write it as a question with its anchor and the answer that would make it a defect, and
place it after the findings, unnumbered.

## 🔧 Directive 7 — The report is the whole answer

The turn opens with the report header and ends with the closing question. Between them there is
nothing but findings.

No preamble (_"I've reviewed your changes and found a few things"_), no verdict paragraph (_"overall
the code is well structured"_), no summary restating the findings after listing them, and no
encouragement. The header already carries the count and the shape; a reader who wants the summary
reads the header. Every line that is not a finding is a line between the user and the work.

## 🔧 Directive 8 — The closing question closes the turn

The turn that reports findings ends with the `AskUserQuestion` call, in that same turn. Not with
a sentence offering help, not deferred to the next turn, and not skipped because the findings looked
self-explanatory or the user seemed to be in a hurry.

The findings exist to be acted on, and the gap between reading them and acting on them is exactly
where a review stops paying for itself. When nothing actionable remains — no findings, no audit
database, nothing to commit — there is no question to ask, and the report ends the turn on its own.
