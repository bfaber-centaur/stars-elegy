# CB-045: how a fleet's cargo enters the speed code

Round 6. CB-038 found that a two-freighter stack carrying 1 kT kept the
empty mass. The Combat decomp pass's rule (stars-decomp #22, COMBAT.md
#38): each ship's mass is its design mass plus `C · c / F`, truncated,
with `C` the fleet's cargo, `c` one ship's cargo capacity and `F` the
fleet's total cargo capacity. Speed code `w − 4 − (mass / 70) / engines`
(`w` = 6 here, one engine).

Two-player Combat Lab base, deep space. Player 0's Laser Destroyer attacks
player 1's unarmed fleets (Medium Freighter + Long Hump 6, mass 69,
capacity 210; Small Freighter + Long Hump 6, mass 34, capacity 70).
Pinned at cycles 20000 and 30000. Record `wt` is the per-ship mass.

## Predictions (committed before the run)

| fleet | cargo | stack | added | `wt` | code |
|---|---|---|---|---|---|
| 0: Medium + Small | 140 | Medium | 140·210/280 = 105 | 174 | 0 |
| 0 | | Small | 140·70/280 = 35 | 69 | 2 |
| 1: three Medium | 210 | Medium ×3 | 210·210/630 = 70 | 139 | 1 |
| 2: three Medium | 212 | Medium ×3 | 70.67 → 70 | 139 | 1 |
| 3: three Medium | 213 | Medium ×3 | 71 | 140 | 0 |

Alternatives: an even split per ship over the fleet would give fleet 0
70 each (`wt` 139 and 104, codes 1 and 1); rounding instead of
truncation would give fleet 2 `wt` 140, code 0.
