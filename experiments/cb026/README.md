# CB-026: a range-0 beam on a starbase

Round 4 (COMBAT.md "Beams", BINARY-ONLY). Player 0's station at planet 18
has one slot of 2 Blackjacks (damage 90, range 0); on a starbase its reach
is 1. Five player-1 Destroyers (armor 300 each, no shields, speed code 1)
approach it. Pinned at cycles 20000 and 30000.

## Predictions (committed before the run)

- The station first fires when the Destroyers are within distance 1.
- Every station hit delivers 180 (2 × 90), at distance 1 as at distance 0:
  no dropoff. With 5 undamaged ships of 300 armor, a first hit records
  `wDmg` 60/100% (36 per ship); a 90% hit (162) would record 54/100%.
- Every hit replays with the stars-decomp checker.

## Result

Both seeds (20000, 30000). The station first fired in round 7, when the
Destroyers had reached a square at distance 1. That first hit recorded
`wDmg` **60/100%** (180 delivered), as did every later hit (cumulative
120, 180, 240 …). No dropoff at distance 1. CONFIRMED. All 17 hits in each
record replayed with the stars-decomp checker, no mismatches.
