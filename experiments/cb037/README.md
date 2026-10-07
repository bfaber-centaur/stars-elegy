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

## Results

Weapons level after the turn, twelve cycle counts (5000 … 50000), which
gave **8 distinct random streams** per setup (by battle record; 20000 =
25000 and 30000 = 35000 = 40000 = 45000). Player 6's Frigates were
destroyed in every run; all hits replayed (0 mismatches). Counts below
are per distinct stream.

| setup | p1 | p2 | p3 | p4 |
|---|---|---|---|---|
| `cb037` (observers 1, 2, 3) | 3 in 8 of 8 | **4 in 2 of 8** | **4 in 3 of 8** | 3 in 8 of 8 |
| `cb037-owner` (observers {1, 3}) | (fighter, 26) | — | **4 in 3 of 8** | — |
| `cb037-deep` (observer {3}) | (fighter, 26) | — | 3 in 8 of 8 | — |

- **CONFIRMED:** player 1, an observer, never gained (1 AND 0b1110 = 0;
  at a 1/3 chance per attempt, 0 of 8 has probability about 4%); players
  2 and 3 gained in some streams; player 4 with no fleet never gained.
  Player 3 gained at a planet whose owner has no starbase (the owner's
  bit makes 3 AND 0b1010 ≠ 0) and never in the same streams in deep space
  (3 AND 0b1000 = 0; the `-owner` and `-deep` runs share their streams
  and player 3 gained in three of them only at the planet).
