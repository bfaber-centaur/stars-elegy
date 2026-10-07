# CB-036: start squares for n = 4 and 6, and a starbase owner past row n

Round 5 (COMBAT.md "Start squares": entry `n(n−1)/2 + rank` of the
flattened table; BINARY-ONLY for `n` other than 1 and 2). CB16P game
(`../cb035/cb16p.def`). Players 1..6 are mutual enemies, each with one
Laser Frigate (plan "enemies") per location; player 0 is neutral to all.
Pinned at cycles 20000 and 30000.

- (1060,1080): players 1..4.
- (1100,1080): players 1..6.
- Player 0's homeworld (planet 16) with an unarmed station: players 1 and
  2. Player 0 is in the player list (starbase owner) but not involved.

## Predictions (committed before the run)

- `n` = 4: player 1 (1,1), 2 (8,8), 3 (1,8), 4 (8,1).
- `n` = 6: player 1 (1,4), 2 (8,5), 3 (2,8), 4 (7,1), 5 (6,8), 6 (3,1).
- Planet 16: players {0, 1, 2} in the record, `n` = 2. Ranks 0, 1, 2 take
  entries 1, 2, 3: the station (1,4), player 1 (8,5), player 2 (4,1).

## Results

Both streams, all hits replayed by the stars-decomp checker (32 + 32, 0
mismatches). **CONFIRMED, every square as predicted.**

| location | record players | squares |
|---|---|---|
| (1060,1080), `n` = 4 | 0x1e | p1 (1,1), p2 (8,8), p3 (1,8), p4 (8,1) |
| (1100,1080), `n` = 6 | 0x7e | p1 (1,4), p2 (8,5), p3 (2,8), p4 (7,1), p5 (6,8), p6 (3,1) |
| planet 16 | 0x7 | station p0 (1,4), p1 (8,5), p2 (4,1) |

The uninvolved starbase owner takes the first entry of row `n` = 2, and
player 2, at rank 2, takes the next table entry (the first entry of row
3), as the flattened-table rule says.
