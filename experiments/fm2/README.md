# FM round 2: movement and fuel sweep (FM-101 to FM-104)

Oracle round on the `docs/KERNEL.md` "Fleet movement" rules that
FM-001..004 did not reach: the BINARY-ONLY "Other movement rules", the
"not exercised" ram-scoop cases, rule 6 for chasers, the equal-factor
cargo order, keeping warp, and waypoint chains across years.

## Setup

- Combat Lab (CB, two JOAT players), one pinned generation per year
  (`tools/fleetlab/pinned-turn`, cycles 20000); FM-104 runs two years.
  Both players tech 26, research 0%. FM-101's player 0 has Improved Fuel
  Efficiency plus NRSE, CE, OBRM, LSP and BET (`lrt 0x1b81`; checked legal
  before the run: no message 0x117), so it also has Cheap Engines.
- Player 0's designs (masses and tanks from COMPONENTS.md, matching the
  host's design dump): QJ5 scout (Scout, Quick Jump 5, Fuel Tank: 15 kT,
  300 mg), LH6 scout 20 kT, Trans-Star 10 scout 16 kT, RHRS scout 21 kT,
  Fuel Mizer scout 17 kT, AMG scout (Long Hump 6 + Anti-matter Generator:
  27 kT, 250 mg), Super-Fuel Xport with 2 Long Hump 6 (129 kT, 2250 mg),
  Large Freighter with 2 RHRS (145 kT), Large Freighter with 1 of 2 Long
  Hump 6 (134 kT), Medium Freighter + RHRS (70 kT), Small Freighters with
  QJ5 (29 kT) and LH6 (34 kT), a minelayer scout, Medium Freighter + LH6.
  Starbase designs are restated (combatlab replaces them): unarmed Space
  Stations at the homeworlds, player 1's Space Dock and Orbital Fort,
  player 0's Orbital Fort.
- Moving fleets travel along their own row in deep space.
- `model.py` is KERNEL.md's movement and fuel rules as code; `gen.py`
  writes the specs and takes most predictions from it; `check.py`
  compares them with the runs.

## Predictions (written before the runs)

Sources: "KERNEL" is the public rule (stars-elegy main 004b4dc); "decomp"
is the stars-decomp reading (fleet-movement.md, fleet-fuel.md) where
KERNEL.md is silent or vague. "warp None" means the fleet has no waypoint
left. Random cases predict a range.

### FM101: Improved Fuel Efficiency and Cheap Engines (player 0 IFE + NRSE CE OBRM LSP BET)

1 year(s).

| Case | Source | Setup | Predicted |
|---|---|---|---|
| A | KERNEL IFE | QJ5 scout, warp 6, +100 x, 300 mg: factor 180 - 27 = 153 | fleet 0/0: x 1041, y 1005, fuel 295, warp 6 |
| B | KERNEL IFE | LH6 scout, warp 5, +25 x, 300 mg: factor 100 - 15 = 85; arrives | fleet 0/1: x 1030, y 1011, fuel 297, warp None |
| C | KERNEL IFE | three QJ5 scouts, warp 4, +16 x: factor 100 - 15 = 85 | fleet 0/2: x 1021, y 1017, fuel 297, warp None |
| D | KERNEL IFE / running dry | QJ5 scout, warp 6, +100 x, 2 mg: range with the IFE factor, ends 0, warp 1 | fleet 0/3: x 1022, y 1023, fuel 0, warp 1 |
| E | KERNEL IFE / ram scoop | RHRS scout, warp 4, +100 x, 100 mg: free warp, gain 6 x 16 = 96 (IFE does not touch a zero factor) | fleet 0/4: x 1021, y 1029, fuel 196, warp 4 |
| F | KERNEL CE | 40 QJ5 scouts, one per fleet, warp 7, +49 x from one point: each fleet has a 1 in 10 chance of not moving (then 300 mg kept, waypoint kept); expect about 4 (0-9 covers 99%) | 40 fleets: between 0 and 9 stay at (1005, 1035) with 300 mg; the rest at (1054, 1035) |
| G | KERNEL CE | control: 20 QJ5 scouts, warp 6, +36 x: every fleet moves (warp 6 is exempt) | 20 fleets: between 0 and 0 stay at (1005, 1041) with 300 mg; the rest at (1041, 1041) |

### FM102: warp 10, two-engine ram scoops, an under-engined design, fuel generators, starbases, task gates, keeping warp, equal factors, chasers, rounding, RHRS colonists

1 year(s).

| Case | Source | Setup | Predicted |
|---|---|---|---|
| A | KERNEL warp 10 | 100 LH6 scouts in one fleet, warp 10, +100 x, 30000 mg: each ship lost with chance 1/10 (expect about 10; 2-20 covers 99.6%); the survivors' fuel = 30000 - trunc(30000 x lost/100) - cost | fleet 0: 100 - k ships with 2 <= k <= 20, at (1105, 1005) |
| B | KERNEL warp 10 | 50 Trans-Star 10 scouts (rated), warp 10, +100 x: none lost | fleet 0/1: ships 2:50, x 1105, y 1011 |
| C | KERNEL warp 10 | one fleet of 50 LH6 and 50 Trans-Star 10 scouts, warp 10: only LH6 scouts are lost | fleet 2: design 2 keeps 50; design 1 loses 0-13 |
| D | KERNEL ram scoop (e = 2) | Large Freighter with 2 RHRS, warp 4, +100 x, 1000 mg: 2 x 6 x 16 = 192 | fleet 0/3: x 1021, y 1023, fuel 1192 |
| E | KERNEL ram scoop (e = 2) | the same at warp 2 (free 3, 4, 5): 2 x 10 x 4 = 80 | fleet 0/4: x 1009, y 1029, fuel 1080 |
| F | decomp (engine slot not full) | Large Freighter with 1 of 2 LH6, warp 5, +100 x, 2600 mg: factor 99999, so it moves only its tiny range and ends with 0 (warp unchanged: no warp is free) | fleet 0/5: x 1008, y 1035, fuel 0 |
| G | KERNEL generators | AMG scout stationary in deep space, 100 of 250 mg: +50 | fleet 0/6: x 1005, y 1041, fuel 150 |
| H | KERNEL generators | AMG scout, warp 5, +25 x, 100 mg: pays the move, then +50 | fleet 0/7: x 1030, y 1047, fuel 146 |
| I | KERNEL generators | AMG scout stationary, 230 of 250 mg: capped at 250 | fleet 0/8: x 1005, y 1053, fuel 250 |
| J | KERNEL generators | 2 Super-Fuel Xports stationary, 1000 of 4500 mg: +200 each | fleet 0/9: x 1005, y 1059, fuel 1400 |
| K | KERNEL generators | Super-Fuel Xport, warp 6, +36 x, 1000 mg: pays, then +200 | fleet 0/10: x 1041, y 1065, fuel 1175 |
| L | decomp _FuelFleets | QJ5 scout (50 mg) orbiting player 1's planet 5 with a Space Dock; player 1 is an enemy toward player 0: not refuelled | fleet 0/11: fuel 50 |
| M | KERNEL (dock needed) | QJ5 scout (50 mg) orbiting player 0's planet 0 with an Orbital Fort: not refuelled | fleet 0/12: fuel 50 |
| N | KERNEL (fuel onto a planet) | MF LH6 at own planet 1 (no starbase), 300 mg, transport "unload all" fuel: the fleet ends with 0 (fuel unloaded onto a planet is lost) | fleet 0/13: fuel 0 |
| O | KERNEL task gate | minelayer scout with "lay mines" at waypoint 0 and a second waypoint 30 ly away, warp 5: does not move | fleet 0/14: x 1005, y 1071 |
| P | decomp task gate | MF LH6 at own planet 2 with 50 Ir, transport "unload all" Ir at waypoint 0, second waypoint 30 ly away, warp 5: unloads before movement, the task ends, it moves (KERNEL's "transport does not move" holds only while the task is open) | fleet 0/15: x 1115, y 1295, fe 0 |
| Q | KERNEL (BINARY-ONLY, no corpus case) | QJ5 scout, warp 6, +100 x, 10 mg: cannot afford the leg (14 mg) but keeps fuel after this year's 36 ly: keeps warp 6 | fleet 0/16: x 1041, y 1077, fuel 5, warp 6 |
| R | KERNEL (equal factors, BINARY-ONLY) | SF QJ5 (design 10) + SF LH6 (design 11), 50 kT, warp 5, +25 x: cargo on design 10 first: 140 tenths, 14 mg (design 11 first would give 141, 15 mg) | fleet 0/17: x 1030, y 1083, fuel 116, warp None |
| S | KERNEL (equal factors, BINARY-ONLY) | SF LH6 (design 14) + SF QJ5 (design 15), 50 kT, warp 5, +25 x: cargo on design 14 first: 141 tenths, 15 mg | fleet 0/18: x 1030, y 1089, fuel 115, warp None |
| T | KERNEL chaser rule 6 | QJ5 scout (2 mg), warp 6, chasing a stationary scout 100 ly away: fuel-limited like an ordinary leg, ends with 0, warp 1 | fleet 0/20: x 1019, y 1095, fuel 0, warp 1 |
| U | KERNEL chaser rule 6 | FM scout (100 mg), warp 4, chasing a stationary scout 100 ly away: ram scoop +16 | fleet 0/22: x 1021, y 1101, fuel 116, warp 4 |
| V | KERNEL chaser rule 6 | QJ5 scout (102 mg), warp 9, chasing a stationary scout 126 ly away: topped up to 37 | fleet 0/24: x 1086, y 1107, fuel 47, warp 9 |
| W | KERNEL rounding (negative) | QJ5 scout, warp 5, from (1395, 1395) toward (1345, 1366): rounds half away from zero on both axes | fleet 0/25: x 1373, y 1382, fuel 298, warp 5 |
| X | KERNEL rounding (negative) | QJ5 scout, warp 6, from (1395, 1380) toward (1300, 1349) | fleet 0/26: x 1361, y 1369, fuel 295, warp 6 |
| Y | KERNEL rounding (mixed) | QJ5 scout, warp 7, from (1390, 1010) toward (1290, 1067) | fleet 0/27: x 1347, y 1034, fuel 281, warp 7 |
| Z1 | KERNEL RHRS colonists | MF RHRS with 100 kT colonists, warp 4, +100 x: loses 18 | fleet 0/28: col 82 |
| Z2 | KERNEL RHRS colonists | MF RHRS with 3 kT colonists, warp 4, +100 x: loses 1 | fleet 0/29: col 2 |
| Z3 | KERNEL RHRS colonists | MF RHRS with 100 kT colonists, stationary: loses 0 | fleet 0/30: col 100 |
| ZO | KERNEL order (owner before number) | player 0 QJ5 scout (fleet number high) and player 1 LH6 scout (fleet 0) chase each other at warp 4, 20 ly apart: player 0 moves first (12 ly), player 1 meets it (8) | fleet 0/31: x 1017, y 1131; fleet 1/0: x 1017, y 1131 |

### FM103: refuelling at a friend's starbases (player 1 friend toward player 0; player 0 enemy toward 1)

1 year(s).

| Case | Source | Setup | Predicted |
|---|---|---|---|
| A | decomp _FuelFleets | QJ5 scout (50 mg) orbiting player 1's planet 5 with a Space Dock: refuelled to 300 | fleet 0/0: fuel 300 |
| B | decomp _FuelFleets | QJ5 scout (50 mg) orbiting player 1's homeworld 8 (Space Station): refuelled to 300 | fleet 0/1: fuel 300 |
| C | decomp _FuelFleets | QJ5 scout (50 mg) orbiting player 1's planet 3 with an Orbital Fort: not refuelled | fleet 0/2: fuel 50 |
| D | decomp _FuelFleets (direction) | player 1 LH6 scout (50 mg) orbiting player 0's homeworld 17 (Space Station); player 0 is an enemy toward player 1: not refuelled | fleet 1/0: fuel 50 |

### FM104: waypoint chains across two years

2 year(s).

| Case | Source | Setup | Predicted |
|---|---|---|---|
| A | KERNEL arrival 5 / chains | QJ5 scout: waypoint 20 ly away (warp 5), then 60 ly further (warp 6): year 1 stops at the first (no carry-over), year 2 moves 36 toward the second | fleet 0/0: x 1025, y 1005, fuel 298; fleet 0/0: x 1061, y 1005, fuel 293 (year 2) |
| B | KERNEL arrival 5 | QJ5 scout: first waypoint at its own position (warp 5), then 25 ly: year 1 no move, year 2 arrives | fleet 0/1: x 1005, y 1011, fuel 300; fleet 0/1: x 1030, y 1011, fuel 298 (year 2) |
| C | KERNEL chains | QJ5 scout: three waypoints 10 ly apart (warp 5): one per year | fleet 0/2: x 1015, y 1017, fuel 299; fleet 0/2: x 1025, y 1017, fuel 298 (year 2) |
| D | KERNEL running dry, next year | QJ5 scout, warp 6, +100 x, 2 mg: year 1 runs dry (warp 1); year 2 moves 1 ly at warp 1 and its ram scoop gives 1 mg | fleet 0/3: x 1019, y 1023, fuel 0; fleet 0/3: x 1020, y 1023, fuel 1 (year 2) |
| E | KERNEL per-year rounding | QJ5 scout, warp 5, +100 x: 25 ly a year, rounded up each year | fleet 0/4: x 1030, y 1029, fuel 298; fleet 0/4: x 1055, y 1029, fuel 296 (year 2) |
| F | KERNEL chains (fuel-limited leg then next) | QJ5 scout, 4 mg: waypoint 10 ly away at warp 9, then 50 ly further at warp 6 | fleet 0/5: x 1010, y 1035, fuel 0; fleet 0/5: x 1011, y 1035, fuel 1 (year 2) |

