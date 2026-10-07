# CB-050, CB-050-ctl: the torpedo estimate's shield term (round 8)

Specs from `experiments/cb042/gen.py`; predictions from private stars-decomp
`docs/combat-predictions.md` "Round 8 predictions" (#28, 55483ce),
restated here before the runs.

Three-player Combat Lab game CB3P, deep space (1060, 1080), tech 26.
Players 0 and 2 are friends; both are enemies of 1. Player 0: 2 Upsilon
Torpedo destroyers; player 2: 4 Jihad Missile destroyers; both on
"Starbases only" (primary starbase, secondary none), so they never move
or fire. Player 1: 2 runners on tactic 0 (disengage), shielded (Wolverine)
in CB-050, unshielded in CB-050-ctl. Start squares for n = 3: (4,1),
(8,8), (1,8).

## Predictions

- **CB-050:** the runner moves (8,8) → (9,9), has 7 move records there
  (counter 7 … 1) and then leaves the board, in every stream, with no tie
  draws for its square. Without the shield term it would alternate
  between (9,9) and (8,9).
- **CB-050-ctl:** the runner alternates between (9,9) and (8,9) and leaves
  on its 8th move; the first square is (9,9) or (8,9), about half of the
  streams each.

Six pinned cycle settings each (5000, 7000, 10000, 14000, 20000, 30000);
streams counted by record hash.

## Results

Six runs each, 6 distinct streams (ticks 823, 549, 384, 274, 164, 109).
The decomp's battlesim replay (stars-decomp 55483ce) matched every move
in all 12 runs. Players 0 and 2 never moved or fired.

- **CB-050: CONFIRMED, 6 of 6.** The shielded runner moved to (9,9) on
  its first move and stayed there for 7 move records with counter
  7 … 1, then left the board on the 8th.
- **CB-050-ctl: CONFIRMED, 6 of 6.** The unshielded runner alternated
  between (9,9) and (8,9) for 7 moves and left on the 8th. It started
  on (9,9) in 4 streams and on (8,9) in 2.

The shield term in the torpedo estimate is what keeps the shielded runner
on (9,9).
