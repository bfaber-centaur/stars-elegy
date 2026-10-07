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

## Round 2: OT-6 (KERNEL gaps K1 and K3)

Committed after OT-1..5 ran and before OT-6 ran. Player 0 is Alternate
Reality, player 1 is War Monger, and both are at tech 26. The run uses
the same two cycles values.

| Case | Setup | Predicted (binary reading) | Rules out |
|---|---|---|---|
| OT-6-1 | AR freighter, 22 kT colonists, moves 20 ly | 22 kT kept: the loss `⌊33·3/100⌋` is 0, and there is no message 0x0c1 | loss of at least 1, or a message for a zero loss |
| OT-6-2 | 23 kT, moves 20 ly | 22 kT, message 0x0c1 for 1 kT | |
| OT-6-3 | 100 kT, waypoint 1 on its own position at warp 5 | 97 kT with 0x0c1: no distance test before the loss | "not moving" when the destination is the fleet's own position |
| OT-6-4 | 100 kT, no fuel, waypoint 1 50 ly away at warp 5 | 97 kT with 0x0c1, and the fleet does not move | loss only when the fleet actually covers distance |
| OT-6-5 | 100 kT, chasing fleet 6 | 97 kT, lost once (pass 0, before the chase is deferred) | no loss for chasers, or a loss per pass |
| OT-6-7 | 100 kT, waypoint 1 at warp 0 | 100 kT, no message | |
| OT-6-P | Each player owns one "BMC" (7 Big Mutha Cannons: beam 1785, speed code 5 without War Monger) and one "DIS" (9 Disruptors: beam 1899, speed code 5) | Power: BMC `1785 + ⌊1785·1/10⌋` = 1963 (escort) for both players, because the speed code has no War Monger bonus; DIS 2088 (capital). Score records: player 1 has U/E/C = 1/1/1; player 0 has U/E/C = 8/1/1 | War Monger +2 in the score's speed code (player 1 BMC = 2320, capital: E/C 0/2); no speed term (DIS 1899, escort: E/C 2/0) |

## Results

Every case matched its prediction at both cycles values (20000 and 3700).
Raw files, hashes and the per-run dumps are in the private apparatus
repository under `evidence/ot/`.

| Case | Observed (both streams) | Result |
|---|---|---|
| OT-1 | The fleet is gone; player 0 got the Trader's research reward (message 0x109); planet 15's surface ironium is 0 | encounter before unload: CONFIRMED |
| OT-2 | A battle at 1084,1210 (0x9a messages and a battle record); no freighter was lost, and the fleet then traded (0x109) | battle before encounter: CONFIRMED |
| OT-3 | Planet 19 uninhabited by the packet (0xda to player 1); no bombing message to either player; launch message 0xd3 to player 0 | launch-year flight before bombing: CONFIRMED |
| OT-4 | Final environment 50/50/51 (0x15b, 0x156). At 3700 the CA's original also drifted (to 50/50/59, 0x15c) and the result was still 50/50/51 | CA terraforming before Orbital Adjusters: CONFIRMED |
| OT-5 | Planets 15 and 19 both end at 1330, planet 21 at 1150; 0x158 for 157 to planet 15; fleet B 200 → 210 with 0x0fb for 10; fleet C unchanged, no message | breeding before growth, and the breeding rules: CONFIRMED |
| OT-6-1..7 | Colonists: 22 → 22 (no 0x0c1), 23 → 22, 100 → 97 (own position), 100 → 97 (no fuel; the fleet stayed put), 100 → 97 (chaser, once), 100 → 100 (warp 0, no message). 0x0c1 went to fleets 2, 3, 4 and 5 only | as predicted |
| OT-6-P | Score records: player 0 U/E/C 8/1/1, player 1 1/1/1; starbases 0; tech sum 156 | speed code without the War Monger bonus: CONFIRMED |
