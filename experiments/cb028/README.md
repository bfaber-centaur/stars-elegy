# CB-028: a disengaging token that stays on its square

Round 4 (COMBAT.md "Disengaging", BINARY-ONLY). A player-1 Small Freighter
(unarmed, so tactic 0; speed code 2: one move every round) meets one
player-0 Watcher whose plan never lets it fire. The Freighter's estimated
damage from the Watcher is the same (1) at every distance of 2 or more, so
staying put scores best. Pinned at cycles 20000 and 30000.

## Predictions (committed before the run)

- The Freighter does not change square (or changes it rarely).
- It leaves the board on its 8th move, i.e. in **round 7**, and the
  battle ends then. If moves that keep it on its square did not count, it
  would still be on the board after round 15.

## Result

Both seeds (20000, 30000). The Runner made one disengage move each round
from round 0 and left the board on its 8th move, in **round 7**; the
battle ended then. CONFIRMED.

The first prediction missed: the Runner changed square on **every** move
(the move records' counter goes 7 … 0), so no move kept it on its square.
The "stay-put moves count" clause is therefore **not tested** by this
setup. The same was true of the four dumping Freighters in CB-025.
