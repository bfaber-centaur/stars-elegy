# OB: universe objects corpus

Tests the stars-decomp universe-objects reading (private `docs/objects.md`,
`docs/objects-predictions.md` O-1..O-40, `tools/objects.py`; stars-decomp
PR #10) and the scanning predictions S-17..S-19 that needed these objects.
Predictions below were committed **before** the OB runs they describe.

## Setup

Combat Lab (`docs/ORACLE.md`), one generation per run with the random
stream pinned (`tools/fleetlab/pinned-turn`, cycles fixed 20000 unless
stated). Specs: `obNNN.spec`, written by `gen.py`; `check.py` compares a
run's `after.dump` with the predictions.

- Combat Lab has no minefields, packets, wormholes or Mystery Trader, so
  they are inserted into the start file as object records (`thing` lines,
  ORACLE.md "Universe objects"). Probe OB-000 showed the game loads,
  updates and rewrites all four kinds. That probe (written before
  this table) already showed two results: a Mini Mine Layer with two Mine
  Dispenser 40 laid 160 mines, and an uncaught 1000 kT warp-10 packet
  added 111 kT to an unowned planet. OB-002-F and OB-003-A repeat them.
- Player 0 is at tech 26 in every field (no design part is stripped);
  player 1 is at its 2400 tech (3 everywhere). Research is 0% for both.
  Mutual enemies unless stated.
- Each minefield case sits alone: `gen.py` asserts that every field
  contains exactly the planets its case names, and cases are far apart.
- Minefields decay before sweeping and laying in the same year (O-7), so a
  1000-mine enemy field with no planet inside is 980 when it is swept.
- Population is in the file's units of 100 colonists.

## Predictions (stars-decomp reading)

`python3 experiments/ob/gen.py --list` prints the same table.


### OB-001: minefield sweeping by fleets and starbases (mutual enemies)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-001-A | O-8 | Gatling DD (rating 992) 20 ly from the centre of a 1000 field | field 399 | field removed (0) |
| OB-001-B | O-9 | Laser DD (2 lasers, rating 20) at the centre | field 960 |  |
| OB-001-C | O-9 | Mini Gun DD (gatling, swept as range 4: 13*16 = 208) | field 772 | 928 if the Mini Gun swept at its range 2 |
| OB-001-D | O-9 | Sapper DD (2 Pulsed Sappers) at the centre | field 980 (sappers do not sweep) | field reduced |
| OB-001-E | O-10 | Laser DD with plan "attack nobody" at the centre | field 980 | field 960 |
| OB-001-F | O-11 | two separate Laser DD fleets at the centre | field 940 | 960 if they shared |
| OB-001-G | O-9 | one fleet of 3 Laser DDs at the centre | field 920 | 960 |
| OB-001-H | O-9 | speed-bump field 1000 (decays 2% to 980), Laser DD at the centre | field 974 (a third of 20) | 960 |
| OB-001-I | O-9 | Gatling DD at the centre of a 2000 field (decays to 1960) | field 968 (2*31*16 = 992) | 1712 if gatlings swept at range 2 |
| OB-001-J | O-9 | player 0 planet 5 with a Laser Fort (2 lasers) inside a 1000 field (d^2 = 656) | field 900 (starbase range +1: 2*10*4 = 80) | 960 without the +1 |

### OB-002: minefield decay, laying and detonation (mutual enemies)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-002-A | O-5 | player 1 field 1000, no planets | field 980 |  |
| OB-002-B | O-5 | player 1 field 100 | field 90 (minimum decay 10) | 98 |
| OB-002-C | O-5 | player 1 speed-bump field 100 | field 98 (no minimum 10) | 90 |
| OB-002-D | O-5 | player 1 field 1000 containing unowned planets 11 and 12 | field 900 (10%) | 980 |
| OB-002-E | O-5 | player 1 field 2000 containing its own homeworld 8 and unowned 4, 5 | field 1720 (14%: owners do not matter) | 1880 if only unowned planets counted |
| OB-002-F | O-1/O-7 | Mini Mine Layer (2 Mine Dispenser 40), lay indefinitely, empty space | new player 0 field 160 at the fleet (laid after decay) | 150 if decayed the same turn |
| OB-002-G | O-3 | layer 10 ly east of the centre of its own 400 field (decays to 390) | one field 550 centred at x+2 (1282,1240) | a second field at the fleet |
| OB-002-H | O-1 | fleet of 3 Mini Mine Layers | field 480 |  |
| OB-002-I | O-1 | Mini Mine Layer with 2 Mine Dispenser 40 + 2 Heavy Dispenser 50 | standard field 160 and heavy field 200 at the fleet | one mixed field |
| OB-002-J | O-1 | Frigate with 3 Speed Trap 20 (no layer hull) | speed-bump field 60 | 120 if doubled |
| OB-002-K | O-1 | Frigate with 2 Mine Dispenser 40 | standard field 80 | 160 |
| OB-002-L | O-1 | Frigate with 1 Multi Contained Munition | standard field 40 (if the part survives) | no field |
| OB-002-M | O-13 | player 0 detonating field 1000 with 5 own Laser DDs, own Mini Mine Layer, 5 enemy Medium Freighters inside | DDs 50% armor damage, layer undamaged, freighters 80% (100 per ship); field 730 (27%) | own warships exempt; field also shrunk by hits |
| OB-002-N | O-4 | layer with years word 0 | field 160 and waypoint task cleared | task kept |

### OB-003: mass-driver packets in flight and on impact (player 0 packets, mutual enemies)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-003-A | O-21 | 1000 kT ironium, warp 10, 25 ly from unowned planet 0 | planet 0 surface +111 Ir | +1000 |
| OB-003-B | O-21 | 300/200/100 kT, warp 10, into unowned planet 6 | surface +33/+22/+11 | +300/200/100 |
| OB-003-C | O-20 | class-1 packet (10%/yr) of 100 kT arriving with a 5% share (5 ly at warp 10) into unowned planet 13 | loses the 10 kT minimum: 90 arrive, surface +9 | +11 with no minimum |
| OB-003-D | O-21/O-22 | warp 10 packet 1000 kT into own planet 9 with a Mass Driver 7 fort (catch 49%) | surface +546; damage 318: pop 1000 -> 682 (units of 100) | surface +1000, no damage |
| OB-003-E | O-21 | warp 7 packet into own planet 14 with a Mass Driver 7 fort (fully caught) | surface +1000, pop 1000 unchanged |  |
| OB-003-F | O-22 | warp 10, 1000 kT into enemy planet 20 (no starbase, no defenses, pop 1000) | pop 375 (kill 625 units), surface +111 |  |
| OB-003-G | O-23 | the same packet into enemy planet 22 with pop 500 | planet uninhabited (owner none) | pop > 0 |
| OB-003-H | O-24 | player 0 packet into its own planet 10 (no starbase, pop 1000) | pop 375 | no damage to own planets |
| OB-003-I | O-22 | warp 10, 1000 kT into enemy planet 18 with 50 SDI defenses, pop 1000 | damage 625 scaled by defenses to 418: pop 582, defenses 30 | defenses ignored: pop 375 |
| OB-003-J | O-19/O-20 | class-2 packet (25%/yr) in flight, 250 ly from planet 23, moved bit clear | moves 100 ly to (1228,1261) (within 1 ly); 750 kT left | half speed or no move |
| OB-003-K | O-19/O-20 | class-3 packet (50%/yr), 250 ly+ from planet 23, moved bit set | moves 100 ly; 500 kT left (bit meaning measured) |  |

### OB-004: Mystery Trader encounters (player 1 at tech 3, sum 18)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-004-A | O-34 | stationary player 0 fleet with 4999 kT minerals and 100 colonists at the MT | fleet kept, no message (stationary) |  |
| OB-004-B | O-34 | player 0 fleet with 4999 kT that moves 20 ly onto the MT | fleet kept, message 0x108 |  |
| OB-004-C | O-34 | stationary player 0 fleet with exactly 5000 kT (tech 26: reward is a part or nothing) | fleet removed | fleet kept |
| OB-004-D | O-34/O-36 | player 1 fleet of 24 Medium Freighters with 5000 kT; MT item research | fleet removed; player 1 gains 6 tech levels in total | fleet kept |
| OB-004-E | O-35 | second player 1 fleet with 5000 kT at the same MT, same turn | fleet kept, message 0x118 | removed |

### OB-005: wormhole jiggle and transit (multi-year; mutual enemies)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-005-A | O-28/O-29 | class-0 pair, years 0 | no jump; each end moves at most 12 ly per axis, years 1 |  |
| OB-005-B | O-28 | class-2 pair, years 30 (6%/yr) | jiggle (94%) or jump; recorded per stream |  |
| OB-005-C | O-31/O-40 | scout 30 ly from wormhole 0 targeting it at warp 6 | ends on wormhole 1's pre-move position (1290,1240) | stops at wormhole 0 |
| OB-005-D | O-31 | scout 30 ly from wormhole 2 at warp 4 (16 ly) | moves 16 ly, no transit |  |

## Round 2 predictions

Committed after OB-001..005 ran and before OB-006..016 and the OB-004 rerun.
OB-004 is rerun because fleet B had too little fuel to reach the trader in
run 1 (it moved 1 ly), so B did not test the moving case.


### OB-006: new games from a definition file (O-27)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-006-T11 | O-27 | size 0, seed 11, random events on | 0..2 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-T22 | O-27 | size 0, seed 22, random events on | 0..2 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-T33 | O-27 | size 0, seed 33, random events on | 0..2 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-S11 | O-27 | size 1, seed 11, random events on | 1..3 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-S22 | O-27 | size 1, seed 22, random events on | 1..3 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-S33 | O-27 | size 1, seed 33, random events on | 1..3 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-M11 | O-27 | size 2, seed 11, random events on | 1..5 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-M22 | O-27 | size 2, seed 22, random events on | 1..5 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-M33 | O-27 | size 2, seed 33, random events on | 1..5 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-L11 | O-27 | size 3, seed 11, random events on | 3..6 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-L22 | O-27 | size 3, seed 22, random events on | 3..6 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-L33 | O-27 | size 3, seed 33, random events on | 3..6 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-H11 | O-27 | size 4, seed 11, random events on | 4..8 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-H22 | O-27 | size 4, seed 22, random events on | 4..8 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-H33 | O-27 | size 4, seed 33, random events on | 4..8 wormhole pairs, each end class 0, 1 or 2 with years 0 |  |
| OB-006-T11N | O-27 | size 0, seed 11, random events off | no wormholes (random events off) |  |
| OB-006-T22N | O-27 | size 0, seed 22, random events off | no wormholes (random events off) |  |
| OB-006-T33N | O-27 | size 0, seed 33, random events off | no wormholes (random events off) |  |
| OB-006-H11N | O-27 | size 4, seed 11, random events off | no wormholes (random events off) |  |
| OB-006-H22N | O-27 | size 4, seed 22, random events off | no wormholes (random events off) |  |
| OB-006-H33N | O-27 | size 4, seed 33, random events off | no wormholes (random events off) |  |

### OB-007: sweeping and relations: both players neutral; player 1 plan 0 attacks enemies only

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-007-A | O-10 | Laser DD with plan "enemies" in a neutral player's field | field 980 (no sweep) | 960 |
| OB-007-B | O-10 | Laser DD with plan "neutral and enemies" in a neutral player's field | field 960 | 980 |
| OB-007-C | O-10 | player 0 Laser Fort (planet 5) inside a neutral player's 1000 field (1 planet: 6% decay) | field 860 (940 - 80: starbases sweep any non-friend field) | 940 |
| OB-007-D | O-12 | player 0 layer lays 160 at player 1's homeworld (Space Station, 32 lasers: rating 1280) | no player 0 field left (laid, then swept the same turn) | field 160 |
| OB-007-E | O-10 | Laser DD with plan "everyone" in a neutral player's field | field 960 | 980 |

### OB-008: sweeping and relations: player 0 counts player 1 as a friend

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-008-A | O-10 | player 0 Laser Fort inside a friend's 1000 field (6% decay) | field 940 (no sweep) | 860 |
| OB-008-B | O-10 | Laser DD with plan "everyone" in a friend's field | measured (does "everyone" include friends?) |  |
| OB-008-C | O-10 | Laser DD with plan "neutral and enemies" in a friend's field | field 980 | 960 |
| OB-008-D | O-10 | Laser DD with plan "player 1 only" in a friend's field | measured |  |

### OB-009: packet impacts with population growth controlled (player 0 packets, mutual enemies)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-009-A | control | player 0 planet 16, pop 1000, no packet | pop 1150 |  |
| OB-009-B | control | player 1 planet 21, pop 1000, no packet | pop 1150 |  |
| OB-009-C | O-21/O-22 | warp 10, 1000 kT into own planet 9 with a Mass Driver 7 fort (catch 49%) | surface +546; 318 units killed: pop 682 -> 784 | no damage: 1150 |
| OB-009-D | O-21 | warp 7 packet 30 ly from own planet 14 with a Mass Driver 7 fort (fully caught) | surface +1000, pop 1150 (no damage) |  |
| OB-009-E | O-24 | own packet into own planet 10 (no starbase, pop 1000) | pop 375 -> 431 | no damage |
| OB-009-F | O-22 | warp 10, 1000 kT into enemy planet 20 (no defenses, pop 1000) | pop 375 -> 431 |  |
| OB-009-G | O-23 | the same into enemy planet 22, pop 500 | uninhabited |  |
| OB-009-H | O-22 | warp 10, 1000 kT into enemy planet 18 with 50 SDI (tech 3) | damage 418: pop 582 -> 669, defenses 30 | defenses ignored: 431 |

### OB-010: minefield hits while moving (player 1 fields, player 0 fleets of 5 Laser DDs, warp 9)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-010-H0 | O-14 | warp-9 fleet moving only 30 ly inside a heavy field (checked at warp 6 = safe) | never hit: ends at (1065,1030), undamaged | 1-0.97^30 = 60%% hit chance if warp 9 counted |
| OB-010-H1 | O-14 | warp-9 fleet moving only 30 ly inside a heavy field (checked at warp 6 = safe) | never hit: ends at (1065,1180), undamaged | 1-0.97^30 = 60%% hit chance if warp 9 counted |
| OB-010-H2 | O-14 | warp-9 fleet moving only 30 ly inside a heavy field (checked at warp 6 = safe) | never hit: ends at (1095,1360), undamaged | 1-0.97^30 = 60%% hit chance if warp 9 counted |
| OB-010-H3 | O-14 | warp-9 fleet moving only 30 ly inside a heavy field (checked at warp 6 = safe) | never hit: ends at (1375,1040), undamaged | 1-0.97^30 = 60%% hit chance if warp 9 counted |
| OB-010-H4 | O-14 | warp-9 fleet moving only 30 ly inside a heavy field (checked at warp 6 = safe) | never hit: ends at (1385,1220), undamaged | 1-0.97^30 = 60%% hit chance if warp 9 counted |
| OB-010-S | O-14/O-15 | warp-9 fleet crossing 76 ly of a standard 3000 field (15 per mille per ly) | no hit (32%): at (1241,1230), field 2940; or a stop inside the field, 50% damage on each DD and field 2891 (hit -50, then 2% decay) | 2890 if decay came first |

### OB-015: decay cap: a 40000 field over 22 planets

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-015-A | O-6 | player 1 field 40000 containing 22 planets | field 20000 (50% cap) |  |

### OB-016: SD owner decay: the same 40000 field owned by a Space Demolition player 1

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-016-A | O-5/O-6 | SD player 1 field 40000 with 22 planets | field 30400 (1 per planet + 2 = 24%) | 20000 |

### OB-011: scanning of objects by a JOAT viewer with Rhino scouts (R 50, no penetrating range)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-011-A | S-17 | field 100 at d=12 from a scout (not inside) | seen (d <= R/4) |  |
| OB-011-B | S-17 | field 100 at d=13 | not seen |  |
| OB-011-C | S-17 | field 1000 at d=30 (scout inside) | seen |  |
| OB-011-D | S-17 | field 800 at d=30 (scout outside after decay to 784) | not seen |  |
| OB-011-E | S-17 | field 100 already known to player 1, d=40 | seen (full R) |  |
| OB-011-F | S-17 | field 100 already known, d=51 | not seen |  |
| OB-011-G | S-17 | wormhole 6 ly from a scout before its jiggle; partner far from every scanner | each end seen iff d <= R/4 after the jiggle |  |
| OB-011-H | S-17 | wormhole already known to player 1, far from scanners; its partner unknown and far | known end seen, partner not |  |
| OB-011-I | S-17 | packet near the (1300,1150) scout after its move | seen iff d <= R |  |
| OB-011-J | S-18 | Mystery Trader ending the move at (1084,1100), 69+ ly from every scanner | seen anyway |  |

### OB-012: Packet Physics viewer: every packet, and its own packet as a scanner (S-19)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-012-A | S-19 | player 0 scouts 20 and 30 ly from player 1's moving warp-5 packet | the first seen (penetrating range 25), the second not |  |
| OB-012-B | S-19 | player 0 fields 20 and 30 ly from the packet | first seen, second not |  |
| OB-012-C | S-19 | player 0 packet far from every player 1 scanner | seen (PP sees every packet) |  |

### OB-013: Interstellar Traveler viewer: planets with stargates within its gate range

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-013-A | IT gate | player 0 planet 11 with a gate fort, 75 ly from player 1's gate (range 250) | player 1 sees planet 11 at level 3 or more |  |
| OB-013-B | IT gate | player 0 planet 23 with a gate fort, 259 ly away | below level 3 |  |
| OB-013-C | IT gate | player 0 planet 15 with a starbase but no gate, 138 ly away | below level 3 |  |

### OB-014: Space Demolition player 1: minefield detection, decay and laying while moving

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| OB-014-A | O-5 | SD player 1 field 1000 containing planets 11 and 12 | field 960 (1 per planet + 2 = 4%) | 900 |
| OB-014-B | S-17/SD | player 0 scouts: deep space inside the SD field, orbiting planet 11 inside it, and far away | only the deep-space one appears in player 1's file |  |
| OB-014-C | O-2 | SD layer moving 25 ly (warp 5) toward a lay-mines waypoint | new field 80 at (1050,1205) | nothing while moving |
| OB-014-D | O-2 | non-SD (player 0) layer with lay on waypoint 0 that moves 25 ly | no field | 160 or 80 |

Scanning runs (OB-011..014) are checked object by object: `check.py`
applies the S-17..S-19 rules to the generated host file (positions after
the year's jiggles and moves) and compares the expected set with the objects
in the viewer's `.M` file.
