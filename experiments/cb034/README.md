# CB-034: a disengaging token that stays on its square (second setup)

Round 4c. CB-032's setup did not produce a stay: out of reach, a Laser
stack's damage estimate floors at its count at every distance of 2 or
more, so the Runner's scores were flat (Combat decomp pass, stars-elegy
#38). This setup, also from the decomp pass, makes the estimate fall with
distance. Three-player game (`../cb031/cb3p.def`), deep space at
(1060,1080). Spec: `cb034.spec` (written by `../cb023/gen.py`).

- Players 0 and 2: 12 Delta DDs each (Destroyer, Long Hump 6, 2 Delta
  Torpedo, 2 Tritanium), plan "Armed P1": tactic 5, attack-who player 1,
  primary target armed ships, secondary starbases. Player 1 has neither,
  so they start the battle and count in the Runner's estimates but have
  nothing to attack.
- Player 1: one Runner (Small Freighter, Long Hump 6, unarmed, so tactic
  0; speed code 2, one move a round), plan attack-who nobody.

Pinned at cycles 8000, 12000, 16000, 20000, 30000 and 50000.

## Predictions (committed before the run)

- The record names all three players (mask 0x7). Start squares: player 0
  (4,1), the Runner (8,8), player 2 (1,8).
- The Delta DD stacks never move and never fire.
- The Runner's move 1 goes to **(9,9)**. Moves 2 to 7 **stay on (9,9)**:
  each writes a move record to (9,9), with the counter going 6 … 1. It
  leaves the board on its **8th** move, in **round 7**, and the battle
  ends then.
- If a move that keeps the token on its square did not count, the Runner
  would still be on the board after round 7.

## Result

Six cycle counts gave six distinct records (they differ only in token
order); every prediction held in every stream. CONFIRMED.

- Three players (mask 0x7); start squares as predicted.
- The Delta DD stacks made no move and no fire action.
- The Runner's move records, rounds 0 to 7: (9,9) with counter 7, then
  (9,9) six more times with counter 6 … 1, then off the board with
  counter 0. The battle had 8 actions and ended in round 7.
- So a move that keeps a disengaging token on its square writes a move
  record and counts toward its 8 moves.
