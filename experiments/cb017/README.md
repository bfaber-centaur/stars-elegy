# CB-017: repair between turns (Q-12)

Player-0 fleets of 3 Laser Frigates start with damage 300/500 on every
ship (`dmg 0:300:100`, a new CombatLab fleet option) at ten locations.
All relations neutral, so nothing fights. Two pinned generations,
2400 → 2401 → 2402; damage is read from the host files.

## Predictions (committed before the run)

stars-decomp Q-12 (4a8c82b), repair per turn in 1/500 of armor per
damaged ship; the damaged-ship percentage is unchanged:

| | Location | per turn | 2401 | 2402 |
|---|---|---|---|---|
| R1 | deep space, stationary | 10 | 290 | 280 |
| R2 | deep space, + Fuel Transport | 10 + 25 | 265 | 230 |
| R3 | deep space, + Super-Fuel Xport | 10 + 50 | 240 | 180 |
| R4 | orbiting player 1's planet (no starbase) | 15 | 285 | 270 |
| R5 | orbiting an unowned planet | 15 | 285 | 270 |
| R6 | own planet, no starbase | 25 | 275 | 250 |
| R7 | own planet, Orbital Fort | 40 | 260 | 220 |
| R8 | own planet, Space Dock | 100 | 200 | 100 |
| R9 | own planet, Space Station | 100 | 200 | 100 |
| R10 | own planet, no starbase, + Fuel Transport | 25 + 25 | 250 | 200 |

The "moved" rate (5) is not tested: CombatLab fleets are stationary.

## Result

All 20 values (10 fleets × 2 turns) as predicted. CONFIRMED.
