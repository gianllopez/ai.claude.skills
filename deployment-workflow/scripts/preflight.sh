#!/usr/bin/env bash
# Read-only environment checks run on the target server before deployment-workflow
# mutates anything (SKILL.md, Step 2). Never runs a command that changes state.
#
# Usage (from the local machine, over the already-resolved server alias):
#   ssh <server-alias> 'bash -s' -- "<reverse-domain>" "<service>" < scripts/preflight.sh
#
# Exit code: 0 if every check passed, 1 if any check failed.

set -uo pipefail

REVERSE_DOMAIN="$1"
SERVICE_NAME="$2"
PROJECT_DIR="$HOME/$REVERSE_DOMAIN/$SERVICE_NAME"
PROXY_NETWORK="$(echo "$REVERSE_DOMAIN" | tr '.' '-')-proxy"

failures=0

check() {
  local description="$1"
  local status="$2"
  local detail="${3:-}"

  if [ "$status" -eq 0 ]; then
    printf 'PASS  %s\n' "$description"
  else
    printf 'FAIL  %s%s\n' "$description" "${detail:+ — $detail}"
    failures=$((failures + 1))
  fi
}

# Proxy network exists
if docker network inspect "$PROXY_NETWORK" >/dev/null 2>&1; then
  check "proxy network '$PROXY_NETWORK' exists" 0
else
  check "proxy network '$PROXY_NETWORK' exists" 1 "bring the proxy repository up first"
fi

# Target directory state — report, do not fail on either state; the workflow
# branches on this (clone vs. update) rather than treating it as an error
if [ -d "$PROJECT_DIR" ]; then
  if [ -d "$PROJECT_DIR/.git" ]; then
    printf 'INFO  %s exists and is a git repository (redeploy)\n' "$PROJECT_DIR"
  else
    check "'$PROJECT_DIR' is empty or a git repository" 1 "exists but is not a git repository — do not overwrite"
  fi
else
  printf 'INFO  %s does not exist yet (first deploy)\n' "$PROJECT_DIR"
fi

# Deploy Key SSH alias for this service
deploy_alias="$REVERSE_DOMAIN.$SERVICE_NAME"

if grep -rlq "Host[[:space:]]\+$deploy_alias\b" "$HOME/.ssh/config.d/" 2>/dev/null; then
  printf 'INFO  Deploy Key alias "%s" already configured\n' "$deploy_alias"
else
  printf 'INFO  Deploy Key alias "%s" not found yet — Step 3 will create one\n' "$deploy_alias"
fi

echo "-------"

if [ "$failures" -eq 0 ]; then
  echo "preflight: all checks passed"
  exit 0
else
  echo "preflight: $failures check(s) failed — stop and resolve before deploying"
  exit 1
fi
