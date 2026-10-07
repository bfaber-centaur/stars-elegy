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
