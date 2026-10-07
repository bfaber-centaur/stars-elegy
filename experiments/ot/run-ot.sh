#!/usr/bin/env bash
# OT: turn-order runs. Builds the starts from the CB base and generates one
# year per case at two cycles values. W is scratch for registered-copy
# output (keep it out of this repository).
#   experiments/ot/run-ot.sh CB_BASE_DIR W
set -uo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"; B="$(realpath "$1")"; W="$(realpath -m "$2")"
cd "$root"; E=experiments/ot; mkdir -p "$W/base"
cp "$B/CB.HST" "$B/CB.M1" "$B/CB.M2" "$B/CB.XY" "$W/base/"
for s in 1 2 3 4 5; do
  tools/fleetlab/combatlab build "$B/CB.HST" $E/ot$s.spec "$W/ot$s.HST"
  experiments/kx004/sweep.sh "$W/ot$s.HST" "$W/base" "$W/OT$s" 20000 3700
done
echo OTDONE
