# CB-052: does a beam's leftover damage carry past a starbase? (round 9)

Prediction from private stars-decomp `docs/combat-predictions.md` "Round 9
prediction" (#28, d202d44), committed before the runs and restated here.

Two players, enemies, tech 26, at player 1's homeworld (planet 8).
Player 1 has an unarmed Orbital Fort (100 armor, no shields) and 5
one-Laser destroyers on "Starbase only" (tactic 5, primary starbase,
secondary none). Player 0 has none, so that stack never targets anything
and never moves. Player 0: 10 destroyers with one Colloidal Phaser each
(one beam slot, range 3, damage 26), on "Starbase else any" (tactic 3).

The Fort and the guard stack share player 1's start square. In the
decomp's movement model, the phaser stack first fires in round 2 at
distance 3 from both (300 of 300 simulated streams). There it delivers
10 × 26 × 90% = 234 to a starbase with 100 armor left.

## Predictions

- **No carry (COMBAT.md's rule).** Player 0's round-2 fire action has
  exactly **one** hit record: the Fort, destroyed. The guard stack takes
  nothing that round.
- If leftover carried, as it does after a ship stack dies (CB-010,
  CB-042): a second record in the same action, on the guard stack.
  It would be `R' = min(259, 260 × 134/234) = 148`, 133 after dropoff,
  giving 26 per ship of 300 armor, no kills.
- The guard is hit only from round 3 on (by new fire actions), and it
  never moves.

Six pinned cycle settings (5000, 7000, 10000, 14000, 20000, 30000);
streams counted by record hash.
