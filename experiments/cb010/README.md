# CB-010: leftover beam damage carried to the next stack (Q-7)

CB-009 K2/K3 recorded laser actions that destroyed one stack and went on
to the next, but at distance 0 with a Beam Deflector the rescaled carry
(Q-7) and carrying the raw leftover give the same numbers, so they did
not discriminate. Integer rounding separates them when range dropoff
applies. CB-010 (`cb010.spec`, pinned RNG, tech 26, mutual enemies) has
six battles M1–M6 on y = 1230: 7, 8, 11, 12, 13 and 14 Phaser Frigates
(2 Colloidal Phasers, range 3) against six stacks of 3 Deflector Gunboats
(Frigate, 1 Laser, 1 Beam Deflector; attack nobody, so they close in and
fire back). For these attacker counts the two carry rules differ at
distances 1–3 (and most at 0) for stacks of 3 with a deflector.

## Predictions (committed before the run)

- stars-decomp (Q-7): within one firing action, after a stack is
  destroyed the next target receives dp from R' = min(R − 1, R·L/dp)
  passed through deflector and range dropoff again. A checker that applies
  only this rule (fresh R at the start of each action) replays every hit.
- The raw-leftover alternative (next target receives L directly)
  mismatches at least one recorded hit, provided some action destroys a
  stack at distance ≥ 1 with damage left over.

## Result

Rescaled-carry-only checker: 59/59 hits. Raw-leftover checker: 51/59
(8 mismatches). CONFIRMED.
