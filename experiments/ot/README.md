# OT: turn-order runs

Each run separates two neighbouring steps of `docs/KERNEL.md` "Turn order"
whose order was read from the program (BINARY-ONLY) but not yet measured.
One pinned year per case from the CB base (2400, two players, random events
off), at cycles 20000 and 3700. `run-ot.sh` builds the starts from the
specs here and runs them. Raw output goes to the private apparatus
repository.

## Predictions

Committed before any OT run. "Binary order" is the order in KERNEL.md;
"other order" is what the run would show if the two steps were swapped.

| Case | Steps | Setup | Binary order predicts | Other order would show |
|---|---|---|---|---|
| OT-1 | 6b Trader encounter before 6c unload | 24 freighters with exactly 5000 kT ironium arrive at their own planet 15 with "unload all ironium"; the Trader moves onto planet 15 (1217 → 1281, warp 8) | The fleet is consumed by the Trader and player 0 gets a reward; planet 15's surface ironium stays 0 | The fleet unloads 5000 kT onto planet 15 and is kept |
| OT-2 | 6 battles before 6b encounter | The same freighters (stationary, 5000 kT) and three enemy Destroyers at the Trader's end point (1084,1210) | A battle at 1084,1210 with the freighters. If the battle destroys any freighter, the cargo falls below 5000 kT with it and nothing is traded; if none is lost, the fleet trades after the battle | No battle: the freighters are consumed first |
| OT-3 | 5 launch-year packet flight before 6a bombing | Planet 21 (Mass Driver 7) launches 10 × 100 kT ironium at warp 7 at planet 19, 17 ly away (half-year move 24 ly). Damage 49·1000/160 = 306 units against about 170 units after growth, no defenses. Four Lady Finger bombers orbit planet 19 | Planet 19 is uninhabited by the packet before bombing: no bombing messages to either player; packet messages only | Bombing messages for planet 19, then the packet empties it |
| OT-4 | 7.3 Claim Adjuster year-end terraforming before 7.4 Orbital Adjusters | CA planet 15 at 50/50/60 (original 50/50/60), both players at tech 26 (reach 15); player 0's one-adjuster fleet in orbit, enemies, no starbase | The CA step moves radiation to 50; the adjuster then worsens radiation by one click (score 141 against 74 for gravity and temperature): final 50/50/51 | Adjuster first (50/50/61), then the CA step back to 50/50/50 |
| OT-5 | 3b breeding in transit before 4 production and growth | Player 0 is IS (growth 15%). Fleet A, 10 freighters with a full hold of 2100 kT colonists, orbits planet 15 (1000 units). Controls with the same environment: planet 19 at 1157 units, planet 21 at 1000 | Breeding gives `⌊2100·15/200⌋` = 157 units; none fits the hold, so all 157 go to planet 15 with message 0x158 and no 0x0fb. Planet 15 then ends the year equal to planet 19 | Planet 15 ends at planet 21's value + 157 |

OT-5 also checks two breeding rules:

- Fleet B (200 kT, deep space) breeds `⌊200·15/200⌋` = 15. Ten fit, with message 0x0fb for 10, and five are lost.
- Fleet C (full, orbiting player 1's planet 4) breeds 15. None fits, and none goes to the planet. There is no message.

The race check (step 2a) and other BINARY-ONLY items need no run (`KERNEL.md`).
