# CB-029: tech attempt of a wiped-out participant (two players)

Round 4 (COMBAT.md "Tech from battle", BINARY-ONLY). Player 0 (weapons 3,
other fields 26, research 0%) has five Laser Destroyers. Player 1 has a
fast "Charger" (Colloidal Phaser + Laser, so tactic 5 closes to range 1)
and four Phaser Destroyers. Player 0 should destroy the Charger (weapons
10) and then be wiped out. Pinned at 12 cycle counts (5000, 6000, 7000,
8000, 9000, 10000, 12000, 14000, 16000, 20000, 30000, 50000); distinct
streams are counted by record hash.

## Predictions (committed before the run)

- In every distinct stream where player 0 is wiped out and some weapons
  ≥ 4 design was destroyed, player 0 ends the turn at weapons **3**: a
  wiped-out participant in a two-player battle makes no attempt.
- If it did attempt, about a third of those streams would reach weapons 4
  (CB-018: 4 of 6; CB-021: 3 of 6).
- Streams where player 0 survives are reported separately (it attempts
  there).

## Result

Twelve cycle counts (5000 … 50000) gave twelve distinct battle records.
In every one, all five player-0 Laser DDs were destroyed, and so was
player 1's Charger (Colloidal Phaser, weapons 10). Player 0 ended at
weapons **3** in **12 of 12** streams. CONFIRMED: a wiped-out participant
in a two-player battle makes no attempt. (A one-in-three attempt would
leave all twelve at 3 about 0.8% of the time.) Every hit replayed with
the checker.
