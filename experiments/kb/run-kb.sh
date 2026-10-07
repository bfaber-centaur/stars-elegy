#!/usr/bin/env bash
# KB: KERNEL.md BINARY-ONLY sweep. Builds the starts from the CB base and
# generates one year per case. W is scratch for registered-copy output
# (keep it out of this repository).
#   experiments/kb/run-kb.sh CB_BASE_DIR W
set -uo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"; B="$(realpath "$1")"; W="$(realpath -m "$2")"
cd "$root"; E=experiments/kb; mkdir -p "$W/base" "$W/events" "$W/slow"
cp "$B/CB.HST" "$B/CB.M1" "$B/CB.M2" "$B/CB.XY" "$W/base/"
cp "$B/CB.HST" "$B/CB.M1" "$B/CB.M2" "$W/events/"
scripts/oracle/hst-edit xy "$B/CB.XY" "$W/events/CB.XY" 10:40
cp "$B/CB.HST" "$B/CB.M1" "$B/CB.M2" "$W/slow/"
scripts/oracle/hst-edit xy "$B/CB.XY" "$W/slow/CB.XY" 10:82
ed=scripts/oracle/hst-edit
sw=experiments/kx004/sweep.sh
for s in ${KB_CASES:-kb1a kb1b kb1c}; do
  tools/fleetlab/combatlab build "$B/CB.HST" $E/$s.spec "$W/$s.HST"
  case $s in   # research fields that the spec cannot set
    kb2a) $ed edit "$W/$s.HST" "$W/$s.t.HST" planet=17 field=0,6 accum=85080,0,0,0,0,0 && mv "$W/$s.t.HST" "$W/$s.HST" ;;
    kb2b) $ed edit "$W/$s.HST" "$W/$s.t.HST" planet=17 field=1,6 && mv "$W/$s.t.HST" "$W/$s.HST" ;;
  esac
  case $s in
    kb1c) $sw "$W/$s.HST" "$W/events" "$W/${s^^}" 20000 35000 11500 10500 6000 5200 3700 2190 1985 1750 1490 ;;
    kb2b) $sw "$W/$s.HST" "$W/slow" "$W/${s^^}" 20000 3700 ;;
    *)    $sw "$W/$s.HST" "$W/base" "$W/${s^^}" 20000 3700 ;;
  esac
done
echo KBDONE
