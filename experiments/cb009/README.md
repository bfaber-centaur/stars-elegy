# CB-009: deterministic deep-space cases (round 2)

Round 2 tests the sharpened stars-decomp predictions Q-1..Q-14
(`docs/combat-predictions.md` at 4a8c82b, branch
`claude/project-thread-9j7tt8`). From CB-009 on, turns are generated with
the random number generator pinned (`docs/ORACLE.md`, "Pinned battle
RNG"): Stars! is launched by DOSBox with `cycles=fixed 20000` and
`stars.exe -g cb.hst`, which generates the year and exits with no UI
input. Reruns of the same file then produced byte-identical battle
records (CB-001, CB-002, CB-008 starts, two runs each).

Combat Lab, tech 26, mutual enemies, one generation 2400 → 2401
(`cb009.spec`). Player 0 plan 1 = maximize damage, any, enemies; player 1
plan 2 = attack nobody (armed stacks still fire back, P-6).

| | x | Player 0 | Player 1 |
|---|---|---|---|
| K1 | 1020 | 101 Jihad Cruisers (202 Jihads) | 1000 Small Freighters |
| K2 | 1060 | 10 Laser Frigates | 4 fleets × 3 Small Freighters with a Beam Deflector |
| K3 | 1100 | 10 Laser Frigates | 4 fleets × 3 Frigates (1 Laser, 1 Beam Deflector) |
| K4 | 1140 | 3 Laser Destroyers | Laser Frigates: a fleet of 3 and a fleet of 5 |
| K5 | 1180 | 3 Laser Destroyers | two fleets of 3 Laser Frigates |
| K6 | 1220 | 3 Laser Destroyers | 3 Laser Frigates, 3 Laser Frigates with a Fuel Tank |
| K7 | 1260 | 3 Laser Destroyers | two fleets of 3 Laser Frigates, one damaged 100/500 |
| K8 | 1300 | 10 Beta Cruisers (20 torpedoes) | 3 Shield Frigates (2 Mole-skin) |

## Predictions (committed before the run)

From the stars-decomp reading at 4a8c82b:

- K1 (Q-8): 202 > 200 Jihads at 20% hit 40 times, each 170 (double
  damage, no shields): 6800 armor damage, enough for 272 Freighters, but
  one missile kills at most one ship: the hit records total **202 kills**
  (not 272) and the survivors are undamaged (damage word 0).
- K2, K3 (Q-7): a laser action that destroys a stack carries the leftover
  to the next stack rescaled, R' = min(R − 1, R·L/dp) (then deflector and
  dropoff again), not as the raw leftover. Visible when one action
  records hits on 2 or more stacks; `combat.py check` (4a8c82b) replays
  every hit with the rescaled carry.
- K4–K7 (Q-6): the first player-0 beam action that has a choice between
  in-range stacks picks: K4 the 5-ship stack; K5 the stack listed first
  (lower token index); K6 the Fuel Tank frigates (same armor, higher
  cost); K7 the damaged stack. Only stacks within range compete.
- K8 (Q-14, ≤ 200 torpedoes, so hit/miss rolls are random but pinned): a
  torpedo that misses a shielded target produces a miss record (flag
  0x80) before the hit record and does dmg/8 to shields only (Beta 12 →
  1 per miss).
- Every recorded hit replays through `combat.py check` (4a8c82b).

## Result

Run twice (run1 `fixed 20000`, run2 `fixed 30000`, different streams);
101 and 104 hits replay, 0 mismatches.

- K1: four salvos of 202 kills each, then 192; survivors' damage word 0.
  CONFIRMED.
- K2/K3: carries happened (K3) but at distance 0, where the two carry
  rules agree; see CB-010.
- K4–K7: the predicted stack was chosen in all four battles in both runs
  (K4 5-ship stack, K5 lower index, K6 Fuel Tank frigates, K7 damaged
  stack). In run1 the K4 and K6 picks also had the lower index; in run2
  they had the higher one. CONFIRMED.
- K8: miss records (flags 0xc4) precede each hit record; miss shield
  damage 21 for 14 misses (floor(14 × 12 / 8)). CONFIRMED.
