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

Six cycle settings gave six distinct record hashes. Each battle had 7
tokens and 20 to 37 actions.
- The unarmed freighter token is recorded with tactic 0, although its
  fleet's plan has tactic 3.
- The stars-decomp `combat.py check` (fixed version, stars-decomp #28)
  replayed every hit in five streams: 17, 25, 15, 16 and 22 hits.
- In cycles 7000 it matched 17 hits and missed 1. That miss is in round
  4: a 4-ship Mixed DD token (Colloidal Phaser, Laser, Delta Torpedo,
  Energy Capacitor) hitting the 4-ship Shield DD token (Wolverine shield,
  Beam Deflector), recorded as shield 12, damage 3300.

The movement replay is the decomp's to run. `battlesim.py` handles only
tactics 0, 1, 2 and 5 with uniform designs. These records are the
evidence for COMBAT.md's BINARY-ONLY movement parts. Raw runs are in
stars-oracle-apparatus `evidence/cb7/cb049`.
