# CB-021: tech from battle at six pinned streams

R-9 (stars-decomp 134256d). Player 0 (weapons 3, every other field 26,
research 0%) has a Laser Station at its homeworld (planet 17), plan 0
"enemies". Three player-1 Phaser Frigates (2 Colloidal Phasers, tactic 5,
primary "any", attack enemies) attack it. A lone player-0 hauler sits far
away. Generated with `tools/fleetlab/pinned-turn` at cycles 8000, 12000,
16000, 20000, 30000 and 50000. CB-018's control showed weapons research
does not move without a battle at research 0%.

## Predictions (committed before the run)

Frigates start at (8,5), the station at (1,4). The frigates step one square
per round toward the station and all three are destroyed in round 4.

| cycles | frigate squares r0..r4 | player 0 gains weapons research |
|---|---|---|
| 8000 | (7,5) (6,5) (5,4) (4,3) (3,3) | no |
| 12000 | (7,5) (6,4) (5,3) (4,3) (3,2) | yes |
| 16000 | (7,4) (6,5) (5,5) (4,4) (3,3) | yes |
| 20000 | (7,4) (6,4) (5,3) (4,2) (3,3) | yes |
| 30000 | (7,5) (6,4) (5,5) (4,4) (3,4) | no |
| 50000 | (7,4) (6,3) (5,3) (4,4) (3,5) | no |

"Yes" means weapons reaches level 4 in the same generation. Player 1 is at
a planet it does not own and makes no attempt.

## Result

Frigate squares r0..r4 matched the table in all six streams, and all three
frigates died in round 4. Weapons went from 3 to 4 in the 2401 file at
12000, 16000 and 20000 and stayed 3 at 8000, 30000 and 50000, exactly as
predicted; every research accumulator was 0. Six distinct records; all 24
hits replayed with 0 mismatches. R-9 CONFIRMED.
