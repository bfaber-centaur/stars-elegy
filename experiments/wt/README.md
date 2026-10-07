# WT: wormholes and Mystery Trader corpus

Oracle tooling for the wormhole and Mystery Trader rules in
`docs/OBJECTS.md` (open experiments 2 and 3: jump odds, what a jump does to
fleets heading for a wormhole, Trader spawn, path and rewards). Predictions
come from the objects decomp lane and are committed here before any WT run
they describe. WT-000 is a tooling smoke run with no predictions.

## Tools

| Tool | What it does |
|---|---|
| `wt.py` | Spec helpers on top of Combat Lab: `pair` (two wormhole ends with chosen positions, class 0–3, years since the last jump and the two player masks), `enter` (a fleet whose waypoint 1 is a wormhole), `trader` (a Trader at a point heading for a destination at a warp), `meet` (a cargo fleet staged to fly onto the Trader's end point), `axis_move` (the OB-004 axis-aligned Trader step, for staging only). |
| `smoke.py` | Writes `wt000.spec` (WT-000). |
| `tools/fleetlab/years` | Generates N pinned years in a row from one start: `years START BASE OUT N [CYCLES] [STEP]`, one `OUT/yK` per year. |
| `trace.py` | Reads a `years` output (or pinned-turn outputs in order) and prints each year: player tech and Trader item mask; every wormhole end with its move since the year before; every Trader with its move, destination, warp and raw words; every fleet with position, ships, damage, cargo and fuel. `--json` gives the same as data. |
| `combatlab` `thing` lines | Wormholes and Traders gain `w14`/`w16` and `w10`/`w16` tokens (hex) for setting their raw words. A Trader's `w10` token replaces the whole word, warp included. |

```sh
python3 experiments/wt/smoke.py OUT
tools/fleetlab/combatlab build BASE/CB.HST OUT/wt000.spec OUT/wt000.HST
tools/fleetlab/years OUT/wt000.HST BASE OUT/wt000 3 20000 1000
python3 experiments/wt/trace.py OUT/wt000
```

## Random streams across years

Every pinned year starts a fresh DOSBox, and the stream depends on the
cycles value. With the same cycles every year (`STEP 0`), each year replays
the same draws. In WT-000 both class-0 ends moved by the same vector three
years running, (+2,−5) and (−8,+9). `trace.py` flags such a year
`SAME STREAM?`.

Different cycles values do not always give different streams. Year 1 of
WT-000, fingerprinted by wormhole 0's first move, fell into a few classes:

| Stream (wormhole 0, wormhole 3 first moves) | Cycles values |
|---|---|
| (+2,−5), (−3,−9) | 20000, 21500, 22000, 24000, 25000, 27000, 28000, 29000, 33000 |
| (+2,−2), (−7,+7) | 20100, 20200, 20300, 20500, 20700, 23000; 21000 (from year 2 of `wt000s`) |
| (−3,−7), (−7,+2) | 26000, 31000, 35000, 45000 |

That is 3 streams from 21 values between 20000 and 45000. It fits the
KX-004 cycles-to-tick map (stars-elegy #44, ORACLE.md): the startup tick
is about trunc(k·54.925) ms with k ≈ 70000/cycles. So sampling jump odds
needs a sweep down to low cycles, as in `experiments/kx004/sweep.sh`,
rather than nearby values.

For a multi-year chain, pass a CYCLES list whose consecutive values fall in
different classes, for example `20000,21000,26000`.

## WT-000 smoke run (observed, no predictions)

Raw evidence: stars-oracle-apparatus `evidence/wt/wt000`, `wt000s` (cycles
20000, 21000, 22000) and `fp*` (year 1 fingerprints).

- The wormhole helpers placed the pairs as written. Both ends of each pair
  became known to player 0 (seen and seen2 `0001`) when its fleet transited.
- The scout 30 ly from wormhole 0 at warp 6 ended year 1 on wormhole 1's
  start position (1290,1240), as in OB-005-C.
- Two Laser DDs with damage 100/50% transited a class-3 end at 200 years.
  They ended on the partner's start position (1360,1040), damage 95, then
  85 and 75. That is consistent with repair after transit and no transit
  damage.
- The class-3, 200-year ends did not jump in 3 years. The streams were
  20000 ×3, and 20000/21000/22000.
- Trader 0, heading east at warp 8 from (1010,1210), moved +64 ly a year.
  Its `w10` went from 0008 to 0018 after the first move, and its `w16`
  counted 0, 1, 2 in the files after years 1–3.
- Trader 1, heading for (1005,1390) from (1395,1010) at warp 9, moved
  (−58,+57), (−58,+56), (−58,+57).
- Player 1's 24 freighters with 5000 kT flew 20 ly onto Trader 0's end
  point. The fleet was removed, the Trader's met mask became `0002`, and
  player 1's tech went from 3 everywhere to 5,6,3,3,4,3 (+6 levels in
  total, as in OB-004-D).
