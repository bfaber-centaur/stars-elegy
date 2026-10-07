#!/usr/bin/env bash
# KX-005: build the starts and run every case. W is scratch for
# registered-copy output (keep it out of this repository).
#   experiments/kx005/run-kx5.sh CB_BASE_DIR W
set -uo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"; B="$(realpath "$1")"; W="$(realpath -m "$2")"
cd "$root"; E=experiments/kx005; mkdir -p "$W/base" "$W/slow"
cp "$B/CB.HST" "$B/CB.M1" "$B/CB.M2" "$B/CB.XY" "$W/base/"
cp "$B/CB.HST" "$B/CB.M1" "$B/CB.M2" "$W/slow/"
scripts/oracle/hst-edit xy "$B/CB.XY" "$W/slow/CB.XY" 10:82
for s in r l t0 t1 t2; do tools/fleetlab/combatlab build "$B/CB.HST" $E/kx5$s.spec "$W/$s.HST"; done
scripts/oracle/hst-edit edit "$W/r.HST" "$W/re.HST" planet=17 field=0,7 stat=12:0/13:0
scripts/oracle/hst-edit edit "$W/l.HST" "$W/le.HST" planet=17 field=0,6 accum=85080,0,0,0,0,0
sw=experiments/kx004/sweep.sh
$sw "$W/re.HST" "$W/base" "$W/R1" 20000
$sw "$W/re.HST" "$W/slow" "$W/R2" 20000
$sw "$W/le.HST" "$W/base" "$W/R3" 20000
$sw "$W/t1.HST" "$W/base" "$W/T1" 3700
$sw "$W/t2.HST" "$W/base" "$W/T2" 1165
$sw "$W/t0.HST" "$W/base" "$W/T0" 35000 11500 10500 6000 5200 3700 2190 1985 1490 1210 1190 1165 1135 930 880
echo KX5DONE
