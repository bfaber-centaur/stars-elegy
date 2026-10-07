#!/usr/bin/env bash
# KX-004 stream sweep: generate one year from START once per cycles value,
# each into OUT/c<cycles>, with one retry. Each cycles value reaches one
# startup tick (docs/ORACLE.md, "Which stream a cycles value reaches").
#   experiments/kx004/sweep.sh START.HST BASEDIR OUT CYCLES...
# OUT holds registered-copy output: keep it out of this repository.
set -uo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"
start="$(realpath "$1")" base="$(realpath "$2")" out="$(realpath -m "$3")"; shift 3
cd "$root"
for c in "$@"; do
  d="$out/c$c"
  for try in 1 2; do
    [[ -f "$d/raw/after/CB.HST" ]] && break
    rm -rf "$d"
    tools/fleetlab/pinned-turn "$start" "$base" "$d" "$c" >/dev/null 2>&1 || echo "cycles $c try $try failed"
  done
  [[ -f "$d/raw/after/CB.HST" ]] && echo "cycles $c done" || echo "cycles $c FAILED"
done
