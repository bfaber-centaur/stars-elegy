# CB-049: battle movement beyond the replayed cases (round 7)

`experiments/cb042/gen.py` writes the spec. Two mutually hostile players
fight in deep space, with seven fleets that all move.

Player 0:
- 4 Mixed DD (Colloidal Phaser range 3, Laser range 1, Delta Torpedo
  range 4, Energy Capacitor) on tactic 3, primary any;
- 3 Sapper DD (two Pulsed Sappers, Wolverine shield, Beam Deflector) on
  tactic 2, primary armed ships;
- 2 Mixed DD on tactic 4, primary unarmed ships, which mismatches
  everything except player 1's freighters.

Player 1:
- 4 Shield DD (Colloidal Phaser, Rho Torpedo, Wolverine shield, Beam
  Deflector, Flux Capacitor) on tactic 1, primary any;
- 3 Torpedo Frigates (3 Delta Torpedoes, 2 Wolverine shields) on
  tactic 4, primary bombers and freighters (a mismatch);
- 2 shielded unarmed Medium Freighters on tactic 3;
- 2 Shield DD on tactic 2, primary armed ships.

## Prediction (committed before the runs)

COMBAT.md's movement rules (stars-elegy #59, "Choosing a square" and
"Square score") predict every move in each pinned stream, including the
cases the earlier replays did not cover:
- tactics 1 to 4 with several movers;
- target-type mismatches;
- weapons of different ranges;
- capacitors, deflectors and sappers in the damage estimate;
- the torpedo estimate's shield term;
- the tactic 3/4 score row.

The decomp's `battlesim.py` replay is the test. It should place every
move on the recorded square, in order, with the tie draws in place. The
stars-decomp `combat.py check` replays every hit. Six cycle settings
are run, and streams are counted by record hash.

## Results

(pending)
