# CB-024: repair rates, Inner Strength and starbases

Round 4 (COMBAT.md "Repair"). No battle. Player 0 is Inner Strength
(`prt 0 4`), player 1 JOAT. Each player has unarmed fleets of one Small
Freighter with damage 400/500 at 100%, at the same kinds of places, plus a
Fuel Transport + Freighter fleet; starbases have preset damage
(`planetset N sbdmg=U`, new in CombatLab). Pinned at cycles 20000.

## Predictions (committed before the run)

Damage units after the turn (before → after), `r` doubled for IS, `f` not:

| fleet | situation | player 0 (IS) | player 1 |
|---|---|---|---|
| 0 | stationary, deep space | 400 → 380 | 400 → 390 |
| 1 | moving (waypoint, warp 5) | 400 → 390 | 400 → 395 |
| 2 | orbiting the other player's homeworld | 400 → 370 | 400 → 385 |
| 3 | own homeworld, Space Station (dock) | 400 → 200 | 400 → 300 |
| 4 | own planet, no starbase | 400 → 350 | 400 → 375 |
| 5 | own planet, Orbital Fort | 400 → 320 | 400 → 360 |
| 6 | deep space, Fuel Transport in the fleet (both stacks) | 400 → 355 | 400 → 365 |

Starbases (none fought): homeworld stations 200 → **125** (IS, −75) and
200 → **150** (−50); Orbital Forts 100 → 25 and 100 → 50.
The damaged-ship percentage stays 100.
