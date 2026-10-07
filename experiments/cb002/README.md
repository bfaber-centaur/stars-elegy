# CB-002: weapon types, who fights, starbases

Questions (stars-decomp combat predictions P-4..P-6, P-8, P-12..P-15,
P-18..P-20, P-29; experiments E-3, E-4, E-9): gatling and long-range beam
damage, sappers, capacitors and deflectors, missiles against unshielded
ships, which plans start a battle, the energy dampener, and the starbase
plan-0 "attack everyone" case.

Setup as CB-001 (Combat Lab 2400, tech 26 everywhere, mutual enemies),
spec `cb002.spec`, one host turn 2400 → 2401. Plans: player 0 plan 0
attack everyone, plan 1 attack enemies, plan 2 attack nobody; player 1
plan 0 attack enemies, plan 1 attack enemies, plan 2 attack nobody; all
"maximize damage", primary target any. Player 1's homeworld starbase is
replaced by a Space Station with 2 Gatling Guns and 16 Mole-skin Shields.

| Battle | Where | Player 0 | Player 1 |
|---|---|---|---|
| C1 | (1020,1230) | 1 Gatling Destroyer (plan 1) | 3 Small Freighters, 3 Shield Frigates (2 fleets, plan 2) |
| C2 | (1060,1230) | 1 Destroyer with Phaser Bazooka + Colloidal Phaser (plan 1) | 3 Deflector Destroyers (plan 2) |
| C3 | (1100,1230) | 5 Destroyers with 2 Pulsed Sappers (plan 1) | 3 Small Freighters, 3 Shield Frigates (plan 2) |
| C4 | (1140,1230) | 3 Destroyers, 2 Lasers + Flux + Energy Capacitor (plan 1) | 3 Deflector Destroyers (plan 2) |
| C5 | (1180,1230) | 101 Cruisers with 2 Jihad Missiles (plan 1) | 2 Hulks in one fleet (plan 2) |
| C6 | (1220,1230) | 5 Laser Frigates (plan 1) | 5 Laser Frigates (plan 2, attack nobody) |
| C7 | (1260,1230) | 5 Laser Frigates (plan 2) | 5 Laser Frigates (plan 2) |
| C8 | (1300,1230) | 5 Laser Frigates + 1 Energy Dampener frigate, one fleet (plan 1) | 3 Shield Frigates (plan 2) |
| C9 | planet 17, player 0 homeworld | armed default Space Station, plan 0 = attack everyone | 3 Small Freighters in orbit (plan 2) |
| C10 | planet 8, player 1 homeworld | 3 Small Freighters + 3 Shield Frigates in orbit (2 fleets, plan 2) | Gatling Station, plan 0 = attack enemies |

## Predictions (committed before the run)

From stars-decomp `tools/combat.py` / `docs/combat-predictions.md`
(branch `claude/project-thread-9j7tt8` at 8cad60f):

- C1, C10 (P-13): a gatling shot hits every enemy stack in range, each
  with the full ships × count × 31 damage (×deflector), no range dropoff,
  in token order, and no leftover carries. Starbase weapon range is +1
  (Gatling 2 → 3), starbase initiative 14, gatling initiative 26.
- C2 (P-12, P-14): Phaser Bazooka (26, range 2) does 26/24/23 at distance
  0/1/2 before the deflector; Colloidal Phaser (26, range 3) 26/25/24/23
  at 0/1/2/3 (integer d·10/range). Against a Beam Deflector (90%) the
  deflector applies first: 26·90/100 = 23, then the dropoff.
- C3 (P-15): sappers produce no hit record against the unshielded
  freighters and are never aimed at them while a shielded stack exists;
  hits on the Shield Frigates only reduce shields.
- C4 (P-14): capacitor product 1.2 × 1.1 → 132%: 3 ships × 2 × 10 = 60
  raw → 79 at distance 0, then × 90% deflector → 71, then dropoff 90% at
  distance 1 → 63.
- C5 (P-18, P-20): 202 Jihads (20%) hit floor(202·20/100) = 40 times;
  missiles do double damage (170) to a stack with no shields. 40 × 170 =
  6800 < 7300 stack armor, so all 202 are used, no ship dies, and the
  damage word is 3400 per ship → ceil(3400·500/3650) = 466/500 (undoubled
  would be 233).
- C6 (P-6): player 1, attacking nobody, still fires back once attacked.
- C7 (P-5): no battle record at (1260,1230).
- C8 (P-8): with a dampener present every ship token's speed code is 4
  lower (Laser Frigate and Shield Frigate 2 → 0, i.e. ½ square per round).
- C9 (P-29, legacy-bug candidate): the station's owner plan 0 is "attack
  everyone"; the binary reading predicts that this path may fail to set
  the station's attack mask, so a battle may not happen (or happen
  inconsistently). C10 (plan 0 "attack enemies") should fight.
- Every recorded hit replays through the decomp damage model
  (`combat.py check`).

## Result

7 battles (C1–C8 except C7); 48 hit records replay, 0 mismatches.
Gatling, phaser dropoff with deflector, capacitor, sapper (shields only,
never aimed at the freighters), Jihad doubling (40 hits × 170) and
retaliation as predicted; no battle at C7; dampener sets speed codes to 0.
C5: one Hulk was destroyed (my hand calculation above forgot that 6800
≥ 3650 kills one ship first; the model's replay matched).
**No battle at C9 or C10**: the C10 case contradicts the binary reading.
