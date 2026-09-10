# Deployment Workflow

Deploys a project's service to a server over _SSH_, the same way every time: resolve the target
from _SSH_ configuration that already exists, verify the environment before touching it, clone with
a repository-scoped _Deploy Key_, bring the service up under _Docker Compose_ attached to the
server's shared _Caddy_ proxy network, and register its subdomain with that proxy. Built around one
constraint: no margin for error on infrastructure that is already in production.

## Structure

- `SKILL.md` — the full ten-step workflow, the reverse-domain naming table, and the security
  directives that govern every mutating action
- `README.md` — this overview
- `metadata.json` — version, author, abstract, references
- `scripts/preflight.sh` — read-only environment checks run on the target server before any
  mutating step (proxy network, target directory state, _Deploy Key_ alias)

## Usage

Ask to deploy a service by project and environment, e.g. _"despliega `api` de
`example` en producción"_. The skill resolves `<reverse-domain>` and `<environment>`,
searches `~/.ssh/config.d/` for the matching server alias, and refuses to proceed — asking instead
— if that alias does not already exist. It never invents a server, a network, or a _Deploy Key_ alias
that `SKILL.md`'s naming table does not assign to it.

Run the preflight check on its own, without deploying, by invoking it directly:

```bash
ssh <server-alias> 'bash -s' -- "<reverse-domain>" "<service>" < scripts/preflight.sh
```

## Design decisions

### Tier 2, not Tier 3

This skill holds one coherent procedure — a deployment either runs start to finish or stops at the
step that failed. It is not a catalog of independent rules, so it stays a single `SKILL.md` rather
than a compiled `rules/` catalog.

### The proxy pattern is documented, not replaced

The reverse-proxy model this skill deploys into (one _Caddy_ container, an external _Docker_
network, one `.caddy` file per site) already exists as its own repository per project and is sound
for this scale — explicit, file-based, no label-based magic to debug. This skill's Step 8 follows
that contract as written in the project's own proxy repository rather than re-implementing or
replacing it, and treats the new site file the same way Step 3 treats a _Deploy Key_: a
version-controlled change the user makes and pushes from their own local clone, not something this
skill writes directly on the server. The skill's own mutation is limited to pulling that already-
committed change into the server's clone and reloading _Caddy_.

### Preflight is a script, not prose

`SKILL.md` (_Skill Factory_ convention) prefers a bundled script over a described procedure exactly
when an operation must be deterministic. Whether the proxy network exists is not something to judge
from a shell transcript — it is a fixed check with a pass/fail answer, so it is a script the
workflow runs and reads an exit code from, not a step it reasons about freely.

## Maintenance

- **A new mandatory precondition** — add a check to `scripts/preflight.sh`, keep it read-only, and
  make it print one `PASS`/`FAIL`/`INFO` line so a failure is unambiguous in the transcript
- **A new naming pattern** (e.g. a second proxy technology, a non-_GitHub_ remote) — extend the
  _Naming Conventions_ table in `SKILL.md`; do not introduce a pattern outside that table
- **Everything else lives in `SKILL.md`.** The whole procedure stays in one file — a Tier 2 skill
  never splits its instructions across side documents

## Acknowledgments

Originally created by [@gianllopez](https://github.com/gianllopez).
