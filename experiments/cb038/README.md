# CB-038: cargo and War Monger in the speed code

Round 5 (COMBAT.md "Speed code": `w − 4 + … − (mass/70)/engines`, `+2` for
War Monger; mass = design mass + the stack's share of the fleet's cargo by
cargo capacity; the cargo and WM terms are BINARY-ONLY). Two-player Combat
Lab base. Player 0's Laser Destroyer attacks player 1's unarmed fleets in
deep space. Medium Freighter + Long Hump 6 has mass 69 (code 2 empty, as
for the Small Freighter in CB-028: `w` = 6); the bare Frigate has mass 17.
`cb038-wm` is the same with player 1 a War Monger (`prt 1 2`, `lrt 1
0x1b80`, legal per ORACLE.md). Pinned at cycles 20000 and 30000.

## Predictions (committed before the run)

Speed codes in the battle record (`cb038` / `cb038-wm`):

| fleet | stack | mass | code | WM |
|---|---|---|---|---|
| 0: empty | Medium Freighter | 69 | 2 | 4 |
| 1: 1 kT | Medium Freighter | 70 | 1 | 3 |
| 2: 71 kT | Medium Freighter | 140 | 0 | 2 |
| 3: two freighters, 1 kT | Medium Freighter ×2 | 69 + 1 | 1 | 3 |
| 4: freighter + frigate, 1 kT | Medium Freighter | 70 | 1 | 3 |
| 4 | Frigate (no cargo capacity) | 17 | 2 | 4 |

Fleet 3 reads "the stack's share" as added once to the design mass; if it
were shared per ship (0 each), its code would be 2 (WM 4).
