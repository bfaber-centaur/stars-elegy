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

## Result

Six cycle counts gave six distinct records; no shots in any.

- Record and start squares as predicted: three players (mask 0x7),
  player 0 (4,1), the Runner (8,8), player 2 (1,8). Speed codes: Runner 2,
  Brutes 0.
- **CONTRADICTED:** the Runner never stayed on its square. In every stream
  each of its 8 moves (one per round, rounds 0 to 7) went to a different
  square from the one before, with the counter going 7 … 0. It reached
  (9,9) only in 8000 (first move) and moved on; in several streams it
  moved towards the Brutes (12000 ended at (6,6) with Brutes at (4,5) and
  (5,8)). Its squares, by move:

  | cycles | squares |
  |---|---|
  | 8000 | (9,9) (8,8) (9,8) (8,9) (9,8) (8,8) (7,9) |
  | 12000 | (7,9) (7,8) (6,8) (7,8) (6,7) (5,6) (6,6) |
  | 16000 | (7,9) (6,8) (5,7) (6,6) (7,7) (6,7) (7,6) |
  | 20000 | (7,7) (8,6) (7,6) (6,7) (7,6) (8,6) (7,7) |
  | 30000 | (7,8) (7,9) (8,9) (9,8) (8,7) (7,8) (6,7) |
  | 50000 | (8,7) (9,7) (8,7) (9,7) (8,6) (7,6) (7,7) |

- It left the board on its 8th move, in round 7, as in CB-028. Whether a
  move that keeps it on its square counts is still not tested.
