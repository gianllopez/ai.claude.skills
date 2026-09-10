---
name: deployment-workflow
description: Standardized, security-first workflow for deploying a project's services to a server over SSH — resolves the target from SSH aliases that already exist, verifies the environment before touching anything, clones private repositories with a per-repo GitHub Deploy Key, brings services up via Docker Compose attached to a shared Caddy reverse-proxy network, and registers the new subdomain with that proxy. Everything — directories, container names, SSH aliases — follows reverse domain naming. Use when asked to deploy, redeploy, or register a new service on a server, to set up a Deploy Key for a repository, to add a new site to the Caddy proxy, or when the user mentions "desplegar", "deploy", "SSH al servidor", "Deploy Key", or "registrar en el proxy".
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - AskUserQuestion
license: MIT
metadata:
  author: gianllopez
  version: 1.0.0
---

# Deployment Workflow

Deploys a project's service to a server the user already administers: resolve the target from
existing _SSH_ configuration, verify the environment is safe to act on, clone the repository with a
_Deploy Key_ scoped to that repository alone, bring the service up under _Docker Compose_ attached to
the server's shared _Caddy_ proxy network, and register its subdomain with that proxy.

This skill owns the _procedure_, not the servers or the proxy repository — it never invents a
server, a network, or a naming pattern of its own. Every identifier it uses either already exists
(an _SSH_ alias, a proxy network, a directory) or is derived from the reverse-domain conventions
below, and every step that cannot be undone stops for the user's explicit approval before it runs.

## When to Apply

- The user asks to _"deploy"_, _"desplegar"_, _"redeploy"_, or _"subir"_ a service to a server
- The user asks to register a new service, subdomain, or site with the _Caddy_ proxy
- The user asks to set up or rotate a _Deploy Key_ for a repository
- The user asks to check whether a server is ready to receive a deployment
- The user references a server by its reverse-domain _SSH_ alias (e.g. _"despliega en
  `com.example.production`"_)

Do not run this workflow speculatively after finishing unrelated code changes — a deployment is
something the user asks for, the same way a commit or `/review` is.

## Naming Conventions (reverse domain, fixed)

Every identifier this skill produces follows the same reverse-domain grammar already used across
the user's projects and `~/.ssh`. Read this table before resolving anything — it is the single
source of truth for how each identifier is shaped:

| What                              | Owned by                                  | Pattern                              | Example                       |
| :-------------------------------- | :---------------------------------------- | :----------------------------------- | :---------------------------- |
| Server _SSH_ alias                | already exists                            | `<reverse-domain>.<environment>`     | `com.example.production`      |
| _Deploy Key_ _SSH_ alias          | this skill creates it, on the server only | `<reverse-domain>.<service>`         | `com.example.api`             |
| Remote project directory          | this skill creates it                     | `~/<reverse-domain>/<service>`       | `~/com.example/api`           |
| Proxy _Docker_ network (external) | already exists                            | `<reverse-domain-with-dashes>-proxy` | `com-example-proxy`           |
| Service container name            | this skill sets it                        | `<reverse-domain>.<service>`         | `com.example.api`             |
| _Caddy_ site file                 | this skill adds it                        | `sites/<subdomain>.<domain>.caddy`   | `sites/api.example.com.caddy` |

A server hosts exactly one project's services — the user does not mix projects on the same host —
so `<service>` alone is enough to disambiguate the _Deploy Key_ alias from the server alias; only the
last segment differs (`<environment>` vs `<service>`).

## Workflow

| Step                        |           Mutates state?            |      Stops on failure       |
| :-------------------------- | :---------------------------------: | :-------------------------: |
| 1 · Resolve the target      |                 no                  |             yes             |
| 2 · Preflight               |                 no                  |             yes             |
| 3 · Deploy Key              |     only if creating a new key      |             yes             |
| 4 · Clone or update         |                 yes                 |             yes             |
| 5 · Secrets                 |                 no                  |             yes             |
| 6 · Compose compliance      | no (unless the user approves a fix) |             yes             |
| 7 · Bring the service up    |                 yes                 |             yes             |
| 8 · Register with the proxy |                 yes                 |    only if step 7 failed    |
| 9 · Post-deploy check       |                 no                  | reports, does not roll back |
| 10 · Report                 |                 no                  |              —              |

### Step 1 · Resolve the target

The user names a project and an environment (e.g. _"despliega `api` de `example` en
producción"_). Derive `<reverse-domain>` and `<environment>`, then search for the server alias:

```bash
grep -rl "Host .*<reverse-domain>\.<environment>" ~/.ssh/config.d/
```

**Never invent, guess, or silently create a server alias.** If none is found, stop and tell the
user which alias was searched for and that it does not exist — ask them to add it before
continuing. This is the one part of the target that is entirely out of this skill's hands: it
belongs to a person's `~/.ssh`, not to a project.

### Step 2 · Preflight (read-only)

Run `scripts/preflight.sh` against the resolved alias — see _Helpers_ below — before any command
that could change state. It checks whether the proxy network exists and reports the target
directory's state (deploy vs. redeploy) and whether a _Deploy Key_ alias is already configured for
this service.

A failed check stops the workflow. Report exactly which check failed and why — never proceed past
a failure "to see what happens," and never retry a failed check silently more than once.

### Step 3 · Deploy Key

Read `~/.ssh/config.d/**/*.conf` on the **server** (not the local machine) for a `Host` matching
`<reverse-domain>.<service>`.

- **If it exists**, use it as the `git clone` remote's host and move on
- **If it does not**, this is a new service. Ask the user, with `AskUserQuestion`, what comment
  (`-C`) to embed in the key — never derive or default it silently — then generate a new, dedicated
  key pair on the server
  (`ssh-keygen -t ed25519 -C "<user-provided comment>" -f ~/.ssh/keys/<reverse-domain>.<service> -N ""`),
  add the matching `Host` block to the server's `~/.ssh/config.d/` (following the pattern above),
  then **stop and hand the public key to the user** so they can register it as a read-only
  [Deploy Key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys)
  on the repository. Registering a key on _GitHub_ is the user's action — this skill never has
  _GitHub_ credentials and never should

Never reuse a personal `~/.ssh` identity, and never grant a _Deploy Key_ write access — read-only is
the only correct scope for a clone-only workflow.

### Step 4 · Clone or update

```bash
# first deploy
ssh <server-alias> "git clone <deploy-key-alias>:<org>/<repo>.git ~/<reverse-domain>/<service>"

# redeploy (directory already exists — Step 2 confirms this)
ssh <server-alias> "cd ~/<reverse-domain>/<service> && git fetch && git checkout <ref> && git pull"
```

Never `rm -rf` an existing directory to force a clean clone — an existing directory means a
redeploy, not a reset. If the directory exists but is not the expected repository, stop and ask
the user how to proceed rather than overwriting it.

### Step 5 · Secrets

Check for the `.env` (or equivalent) file(s) the service's `compose.yml` expects. Never fabricate a
secret value or write a placeholder that looks real — a missing secret stops the workflow, and the
user supplies or transfers it (e.g. over the same authenticated `scp`/`rsync` connection) before
the workflow continues. Never echo a secret's contents into chat, a report, or a shell history-visible
command.

### Step 6 · Compose compliance

Before bringing anything up, read the service's `compose.yml` on the server and confirm:

- It attaches to the proxy network by its exact external name (`<reverse-domain-with-dashes>-proxy`)
- Its `container_name` is pinned to `<reverse-domain>.<service>`
- It does not publish any host ports under `ports:` — the proxy is the only process bound to the
  host in production

If any of these is missing, do not edit the file silently. Show the user the specific fix and get
approval before writing it — this file defines the contract with the proxy repository, and a wrong
edit here is exactly the kind of mistake this skill exists to prevent.

### Step 7 · Bring the service up

```bash
ssh <server-alias> "cd ~/<reverse-domain>/<service> && docker compose up -d --build"
```

Include `--build` only if the `compose.yml` read in Step 6 defines a `build:` key for this service
— a registry `image:` needs no local build. On a redeploy, omitting `--build` for a locally-built
service means `docker compose up -d` reuses the existing image and silently ignores the code Step 4
just pulled; the Step 9 post-deploy check would then pass against stale code.

**This is a production-impacting, hard-to-fully-reverse action on a first deploy.** Confirm with
the user via `AskUserQuestion` before running it, stating the service, the server, and whether this
is a first deploy or a redeploy. A redeploy of an already-approved service on a routine update does
not need to ask again in the same conversation if the user already approved "deploy this service"
as the task — use judgment, but default to asking.

### Step 8 · Register with the proxy (new services only)

Follow the proxy repository's own convention — do not reinvent it. The site file is a
version-controlled change that belongs in the user's local clone of the proxy repository —
this skill never writes it directly on the server, the same way it never holds the _GitHub_
credentials needed for Step 3's _Deploy Key_:

1. Tell the user exactly what to add and where: copy the proxy's example site file to
   `sites/<subdomain>.<domain>.caddy` in their local clone, pointing it at the service's
   `container_name` on the proxy network
2. Confirm the subdomain's `A` record already resolves to the server — _Caddy_'s on-demand _TLS_
   fails the _ACME_ challenge otherwise
3. **Stop and let the user commit and push this change themselves** — registering a new site on
   their proxy repository is their call, not this skill's, exactly like Step 3
4. Once it's pushed, deploy it by pulling the change into the server's clone of the proxy
   repository and reloading without restarting the proxy container:

```bash
ssh <server-alias> "cd ~/<reverse-domain>/proxy && git pull && docker exec <reverse-domain>.proxy caddy reload --config /etc/caddy/Caddyfile"
```

Skip this step entirely on a redeploy of an already-registered service.

### Step 9 · Post-deploy check

```bash
ssh <server-alias> "docker compose logs --tail=50 <service>"
curl -sSI https://<subdomain>.<domain>/ # from wherever this runs, once DNS + TLS are live
```

A failing check here does not trigger an automatic rollback — report it and give the user the
rollback reference from Step 3's preflight (or the previous commit hash) so they decide how to act.

### Step 10 · Report

Summarize: what was deployed (service, commit/ref), where (server alias, directory), what changed
in the proxy (if anything), and the previous state's reference in case a rollback is needed. Stop
here — do not chain into another service's deployment unless asked.

## Helpers

`scripts/preflight.sh` — deterministic, read-only environment checks run against the target server
before Step 4. Invoke it by piping it over the already-resolved alias so nothing but the checks
themselves runs remotely:

```bash
ssh <server-alias> 'bash -s' -- "<reverse-domain>" "<service>" < scripts/preflight.sh
```

It exits non-zero if any check fails, and prints one line per check so the failure is
unambiguous — treat a non-zero exit as a hard stop for the workflow, per Step 2.

---

# 🔧 Security Directives

> These are non-negotiable — the whole reason this skill exists is to remove margin for error from
> a process that touches production infrastructure. Directives 1–3 govern secrets and credentials,
> 4–6 govern when the workflow is allowed to mutate anything, and 7 governs the proxy contract.

## 🔧 Directive 1 — Never invent infrastructure

An _SSH_ alias, a server, a proxy network, or a directory that is not already there is never
created by assumption. The only identifiers this skill is allowed to create are the ones _Naming
Conventions_ explicitly assigns to it (a _Deploy Key_ alias, a remote project directory, a container
name, a _Caddy_ site file) — everything else (the server itself, the proxy network, the server's
_SSH_ alias) must already exist, or the workflow stops and asks.

## 🔧 Directive 2 — Never expose key material

`IdentityFile` paths are referenced, never read, printed, `cat`'d, or embedded in a report. A
_Deploy Key_'s private half never leaves the server it was generated on — only the public half is
ever shown to the user, and only so they can paste it into _GitHub_'s _Deploy Key_ form.

## 🔧 Directive 3 — Deploy Keys are read-only and single-repository

One key per repository, generated on the server that will use it, registered on _GitHub_ as
read-only. Never reuse a key across repositories, never reuse a personal identity for an
automated clone, and never request or accept write access for a _Deploy Key_ used by this workflow.
Its `-C` comment is always asked of the user (Step 3) — never inferred or defaulted, since it is the
one piece of the key a person reads when auditing which keys exist on a repository or a server.

## 🔧 Directive 4 — Preflight before every mutation

No command that changes state on the server (Steps 4, 7, 8) runs before Step 2's preflight has
passed for that server in the current run. A check that fails stops the workflow — it is never
downgraded to a warning so the deploy can proceed anyway.

## 🔧 Directive 5 — Irreversible steps are confirmed, not assumed

A first `docker compose up` on a server, a `caddy reload`, generating a new _Deploy Key_, or writing
to an existing directory always gets an explicit `AskUserQuestion` before it runs, naming exactly
what is about to happen. The user asking for "the deployment" is not the same as approving every
individual irreversible action inside it — state each one and let them confirm.

## 🔧 Directive 6 — Idempotent, never destructive, by default

An existing remote directory means update, not recreate — `git fetch` + `pull`, never `rm -rf` +
`clone`. An existing container means `docker compose up -d` recreates it in place, never a manual
`stop` + `rm` unless the user asks for that specifically. Step 10 always records the previous
state's reference so a mistake is recoverable.

## 🔧 Directive 7 — The proxy contract is read, never reinvented

The proxy repository already defines how a service registers itself (external network name, site
file location and extension, reload command). This skill follows that contract exactly, as read
from the proxy repository at hand, and never proposes a different reverse-proxy pattern unless the
user explicitly asks for one to be evaluated.
