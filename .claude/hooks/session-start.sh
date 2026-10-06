#!/bin/bash
# Rebuild the Stars! oracle in cloud sessions (scripts/oracle/bootstrap).
# Never fails the session: missing inputs or errors only print one line.
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
	exit 0
fi

repo="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
home="${ORACLE_HOME:-$HOME/.stars-oracle}"
mkdir -p "$home"
log="$home/bootstrap.log"

if "$repo/scripts/oracle/bootstrap" >"$log" 2>&1; then
	echo "Stars! oracle ready: run copy reset to the registered snapshot (see docs/ORACLE.md)."
else
	echo "Stars! oracle not bootstrapped: $(grep 'oracle: ' "$log" | tail -n 1 | sed 's/^oracle: //') (log: $log)"
fi
exit 0
