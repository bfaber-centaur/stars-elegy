# E-8: salvage from several battles when salvage already lies at a point

Question: CB-058 measured two deep-space battles in one year, each leaving
its own salvage object. E-8 tests three more things: what happens when
salvage already lies at a battle's point; how the new objects are
numbered when the owner's pool has a gap; and how much the lying salvage
decays.

The prediction was pushed before the runs: private apparatus 38ba2fdb,
committed 2026-10-13T03:48:58Z. The push returned by 03:49:00Z, and the
runs started at 03:49:06Z. Raw evidence: stars-oracle-apparatus
`evidence/e8`.

## Setup

`e8.spec` (`combatlab build` on the 2-player Combat Lab base), tech 26 in
every field for both players:

| Point | Player 0 | Player 1 | Salvage already lying (unmarked) |
|---|---|---|---|
| X (1020,1230) | fleet 1, one Heavy Blaster Battleship | fleet 4, two Laser Destroyers that never fire | player 1's number 1, 250/50/30 |
| Z (1010,1150) | fleet 2, the same | fleet 1, the same | none |
| Y (1000,1400) | fleet 3, the same | fleet 2, the same | player 0's number 0, 60/0/0 |

Battle order by first fleet is X, Z, Y. By ascending y it would be Z, X,
Y, and by the victims' lowest fleet Z, Y, X. There was one pinned year at
each of cycles 20000, 30000, 14000 and 10000.

## Results

Every stream took the stated branch: each battle had two kill events of
one Destroyer each, and player 1's battle ids were 1 X, 2 Z, 3 Y.

| P | Prediction | Observed (4 of 4 streams) | Status |
|---|---|---|---|
| 1 | Lying salvage decays by `⌊m/10⌋`, at least 10 kT: 225/40/20 and 50/0/0, mark clear | 225/40/20 and 50/0/0, mark clear | CONFIRMED |
| 2 | Each battle leaves a new object and never joins lying salvage | X: player 1's number 1 (225/40/20) and a new object. Y: player 0's number 0 (50/0/0) and a new player-1 object | CONFIRMED |
| 3 | Lowest unused number, in battle order: 0 at X, 2 at Z, 3 at Y | 0, 2, 3 | CONFIRMED |
| 4 | 6/4/2 per new object, mark set (CB-058 run B's kill events) | 6/4/2, mark set | CONFIRMED |
| 5 | No other packet-kind object | 5 objects: the 2 lying, the 3 new | CONFIRMED |
