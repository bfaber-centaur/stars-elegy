#!/usr/bin/env bash
# KX-004 driver: build a start, then generate YEARS years in a row with
# tools/fleetlab/pinned-turn, one process per year, cycles 15000 + 37·year.
#   experiments/kx004/run-kx4.sh SPEC OPTION_BYTE YEARS OUT [CB_BASE]
# OPTION_BYTE is the game record's option byte (hex): 40 = random events on,
# public scores on; 80 = random events off, public scores off.
# Owned planets other than the homeworlds get the queue
# Auto Factories x5, Factory x1, design 0 x1. OUT holds registered-copy
# output: keep it out of this repository.
set -euo pipefail
spec="$1" opt="$2" years="$3" out="$4" B="${5:-}"
root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$root"; B="${B:-$root/../stars-oracle-apparatus/evidence/cb/base2400}"
mkdir -p "$out/base"
cp "$B/CB.HST" "$B/CB.M1" "$B/CB.M2" "$out/base/"
scripts/oracle/hst-edit xy "$B/CB.XY" "$out/base/CB.XY" "10:$opt"
tools/fleetlab/combatlab build "$B/CB.HST" "$spec" "$out/start.HST"
cur="$out/start.HST"
for n in 0 1 2 3 4 5 6 7 9 10 11 12 13 14 15 16; do
  scripts/oracle/hst-edit edit "$cur" "$out/tmp.HST" planet=$n queue=1:5:0:1,7:1:0:1,0:1:0:2 >/dev/null
  mv "$out/tmp.HST" "$out/start-q.HST"; cur="$out/start-q.HST"
done
for ((y = 1; y <= years; y++)); do
  d="$out/$(printf 'y%03d' "$y")"
  # one retry: an oracle start occasionally fails to generate (E1 2422)
  for try in 1 2; do
    [[ -f "$d/raw/after/CB.HST" ]] && break
    rm -rf "$d"
    tools/fleetlab/pinned-turn "$cur" "$out/base" "$d" $((15000 + 37 * y)) >/dev/null 2>&1 || echo "year $y try $try failed"
  done
  cur="$d/raw/after/CB.HST"
  echo "year $y done"
done
