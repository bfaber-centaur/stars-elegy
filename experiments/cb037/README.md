# CB-037: the observer LEGACY BUG for players other than 0

Round 5 (COMBAT.md "Tech from battle": player `i` qualifies for the
observer attempt when `i AND observers ≠ 0`; the owner of a planet without
a starbase is in the observer set even when it is a participant;
BINARY-ONLY except for player 0, CB-031-obs). CB16P game. Observers have
weapons 3 and 0% research; player 6's Phaser Frigates (weapons 10) are
destroyed. Pinned at the twelve cycle counts 5000 … 50000.

- `cb037`: deep space. Player 5 (6 Phaser DDs) and player 6 (2 Phaser
  Frigates) are enemies. Players 1, 2 and 3 each have a Hauler there
  (observers, mask 0b1110); player 4 (weapons 3) has nothing there.
- `cb037-owner`: at planet 19, owned by player 1 with no starbase.
  Players 1 (6 Phaser DDs) and 6 (2 Phaser Frigates) fight; player 3 has
  a Hauler there (observers {1, 3} = 0b1010 with the owner's bit).
- `cb037-deep`: the same three fleets in deep space (observers {3} =
  0b1000).

## Predictions (committed before the run)

- `cb037`: player 1 stays at weapons 3 in every stream (1 AND 14 = 0).
  Players 2 and 3 qualify (2 AND 14, 3 AND 14 ≠ 0) and reach weapons 4 in
  some streams (about a third each). Player 4 stays at 3 (no fleet).
- `cb037-owner`: player 3 qualifies (3 AND 10 = 2) and reaches weapons 4
  in some streams.
- `cb037-deep`: player 3 does not qualify (3 AND 8 = 0) and stays at 3 in
  every stream.
