# CB-051: falling back from the primary to the secondary target type (round 8)

Spec from `experiments/cb042/gen.py`; predictions from private stars-decomp
`docs/combat-predictions.md` "Round 8 predictions" (#28, 55483ce),
restated here before the runs.

Two players, enemies, tech 26, deep space (1020, 1230); player 0 starts at
(1,4), player 1 at (8,5). Player 0: 3 Laser destroyers on "Starbase else
armed" (tactic 3, primary starbase, secondary armed) and 2 on "Freighters
else any" (tactic 5, primary freighters, secondary any). Player 1: 3 Laser
destroyers on "Careful" (tactic 2, armed) and one unarmed Medium
Freighter on plan 0.

## Predictions

- The "Starbase else armed" stack has no starbase to target, so it scores
  against armed ships (its secondary) and leaves (1,4) on its first move,
  in every stream. Without the fallback it would stay on (1,4) until fired
  on.
- The "Freighters else any" stack targets the freighter while it is on
  the board, then falls back to "any" after the freighter leaves (tactic
  0, 8th move) or dies.
- The full replay (battlesim) must match after fire too, which tests
  whether the fallback is rechecked on every move.

Six pinned cycle settings (5000, 7000, 10000, 14000, 20000, 30000);
streams counted by record hash.

## Results

Pending.
