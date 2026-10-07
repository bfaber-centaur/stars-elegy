# CB-032: a disengaging token that stays on its square

Round 4b (COMBAT.md "Disengaging": every move the token is given counts,
including one where it stays on its square; BINARY-ONLY). Setup from the
Combat decomp pass (stars-elegy #38, stars-decomp #17). Three-player game
(`../cb031/cb3p.def`), deep space at (1060,1080). Spec: `cb032.spec`
(written by `../cb023/gen.py`).

- Players 0 and 2: two Brutes each (Destroyer, Long Hump 6, 2 Laser, 2
  Tritanium), plan "Hunt P1" (tactic 5, attack-who player 1). They are
  neutral to each other.
- Player 1: one Runner (Small Freighter, Long Hump 6, unarmed, so tactic
  0), plan attack-who nobody. Its speed code was 2 in CB-028 (one move a
  round).

Pinned at cycles 8000, 12000, 16000, 20000, 30000 and 50000.

## Predictions (committed before the run)

- The record names all three players (mask 0x7, `n` = 3). Start squares:
  player 0 (4,1), the Runner (8,8), player 2 (1,8).
- The Runner's first move takes it to **(9,9)**. Its moves 2 to 7 keep it
  on (9,9), and **each one writes a move record** to (9,9), with the
  counter going down (6 … 1). It leaves the board on its **8th** move, in
  **round 7**, and the battle ends then.
- No shots are fired: the Brutes (speed code 0 or 1) are still at
  distance ≥ 2 from (9,9) in round 7.
- If moves that keep it on its square did not count, it would still be on
  the board after round 7 (and after round 15, if it never moved again).
