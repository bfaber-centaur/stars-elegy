# CB-025: dump cargo at battle setup

Round 4 (COMBAT.md "Setup steps", BINARY-ONLY). Player 1 Small Freighters
carry 20/10/5 kT (Ir/Bo/Ge). Plan 1 has "dump cargo", plan 2 does not.
Player 0's Watchers are armed aggressors whose plan (primary "starbase",
no secondary) never lets them fire, so nothing is destroyed. Planets 5
and 22 are player 1's (no starbase), surface 100/100/100 at the start.
Pinned at cycles 20000 and 30000.

| case | where | plan | battle |
|---|---|---|---|
| D1 | deep space (1020,1230) | dump | yes |
| D2 | planet 5 | dump | yes |
| C1 | deep space (1100,1230) | dump | no |
| C2 | planet 22 | dump | no |
| C3 | deep space (1180,1230) | no dump | yes |

## Predictions (committed before the run)

- D1: the Freighter ends with 0/0/0 minerals (fuel unchanged by the dump),
  and a salvage object at (1020,1230) holds exactly 20/10/5 (no quarter
  lost; it exists although nothing was destroyed).
- D2: planet 5's surface gains the full 20/10/5 relative to planet 22
  (C2), not × 5/10.
- C1, C2, C3: cargo kept, no salvage object.
- Speed code in the battle record: D1/D2 Freighter 0 (1 for its empty mass,
  −1 for dumping), C3 Freighter 1 (loaded mass 64).
