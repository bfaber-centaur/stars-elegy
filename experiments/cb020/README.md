# CB-020: CB-019 at six pinned streams, tactics 3, 4 and 5

R-8 (stars-decomp 134256d, `docs/combat-predictions.md`). The CB-019 start
(`../cb019/cb019-t3.spec`, `../cb019/cb019-t4.spec`, and `cb020-t5.spec`,
which differs only in tactic 5 "maximize damage") is generated with
`tools/fleetlab/pinned-turn` at cycles 8000, 12000, 16000, 20000, 30000 and
50000. Streams are counted by battle-record hash.

## Predictions (committed before the run)

Final square of the Long DD (record `brc` as (lo, hi)). The decomp's reason:
tactics 3 and 5 close distance using the weapons' minimum range and tactic 4
uses the maximum; ties use the random stream. Under tactic 5 the DD closes
in and is destroyed in round 9.

| cycles | t3 | t4 | t5 (destroyed round 9) |
|---|---|---|---|
| 8000 | (5,5) | (5,6) | (6,5) |
| 12000 | (5,6) | (5,6) | (6,7) |
| 16000 | (5,4) | (5,4) | (6,5) |
| 20000 | (5,5) | (5,6) | (6,4) |
| 30000 | (5,4) | (5,5) | (6,3) |
| 50000 | (5,6) | (5,6) | (6,5) |

The 8000 and 20000 tactic 3/4 cells are CB-019 observations and are rerun
only as controls. Tactic 5 paths: 20000 passes (5,5) in round 6 and (6,4)
in round 8; 8000 reaches (6,5) in round 8.

## Result

All 14 new cells matched, and the tactic 5 Long DD was destroyed in round 9
in all six streams (tactic 5 paths at 20000 and 8000 also as predicted).
The six cycle counts gave six distinct battle records for each tactic.
Every hit replayed with the stars-decomp checker (134256d), 0 mismatches.
R-8 CONFIRMED.
