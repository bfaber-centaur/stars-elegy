# GT: stargates left open by OB-021/OB-022

Predictions written before the run; they restate the BINARY-ONLY rules in
`docs/OBJECTS.md` "Stargates" (stars-decomp O-54..O-67).

Base game: `tools/fleetlab/new-game experiments/gt/gt.def OUT 20000 gtc.r1
gtj.r1`, a medium universe (x, y in 1000..2200, 288 planets, positions in
`planets.txt`), no random events, two human players: player 0 is PG000's
race with PRT JOAT and Cheap Engines (`racelab edit … prt=9 lrt=0x100`),
player 1 the same with no LRT. Player 0's homeworld is planet 142, player
1's planet 70. Player 1 lists player 0 as a friend; player 0 lists player 1
as an enemy.

```sh
python3 experiments/gt/gen.py OUTDIR
tools/fleetlab/combatlab build GT.HST OUTDIR/gt001.spec start.HST
tools/fleetlab/pinned-turn start.HST BASEDIR OUT 20000 GT
python3 experiments/gt/check.py OUTDIR/cases.json OUT
```

## Cases

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| GT-001-A | O-54 | 2 Jump Gate freighters, 100 kT ironium, deep space 200 ly from own 100/250 planet 0 | at planet 0 with 100 kT, fuel 100, undamaged | refused (no source gate); cargo dropped |
| GT-001-A2 | O-54 | 5 Jump Gate freighters, deep space 300 ly from own 100/250 planet 193: danger 5% (the destination range stands for both ends) | at planet 193; each lost with 1%; survivors 20/100% | undamaged (no range limit for a Jump Gate) |
| GT-001-A3 | O-54 | one Jump Gate freighter and one plain freighter in deep space, gate warp to own planet 98 | stays (message 0xde) | jumps |
| GT-001-B | O-55 | Jump Gate freighter with 60 kT at own 100/250 planet 3, 299 ly to own any/any planet 39: danger 4% | planet 3 surface +60; at planet 39 empty (or lost with 1%), damage 20/100% | cargo kept and no damage (Jump Gate used instead of the planet gate) |
| GT-001-C | O-56 | Jump Gate freighter 100 ly from own planet 196 whose starbase has no gate | stays with its 50 kT (message 0xe2) | jumps |
| GT-001-C2 | O-56 | Jump Gate freighter 100 ly from own planet 101 with no starbase | stays (message 0xe2) | jumps |
| GT-001-D | O-57 | player 0 Laser DD at player 1's gate planet 6 (player 1 lists 0 as friend; 0 lists 1 as enemy) to own gate planet 27 | at planet 27 | stays (fleet owner's view, or mutual friendship) |
| GT-001-D2 | O-57 | player 1 Laser DD at player 0's gate planet 104 (0 lists 1 as enemy) to own gate planet 95 | stays (message 0xe6) | jumps (player 1 lists 0 as friend) |
| GT-001-E | O-58 | player 0 Laser DD from own gate 9 to player 1's gate planet 8 | at planet 8; player 1 gets no message naming it | stays |
| GT-001-E2 | O-58 | player 1 Laser DD from own gate 202 to player 0's gate planet 241 | stays (message 0xe5) | jumps |
| GT-001-F | O-59 | player 0 freighter with 70 kT ironium at player 1's gate planet 107 to own gate 128 | planet 107 (player 1's) surface +70; both players get message 0xec; freighter at 128 empty | cargo carried; or dumped without telling player 1 |
| GT-001-F2 | O-59 | player 0 freighter with 50 kT ironium and 10 kT colonists at player 1's gate planet 12 | stays full (message 0x15e); planet 12 surface +0 | minerals dumped first; or jumps |
| GT-001-F3 | O-59 | as F2, destination own planet 178 without a gate | stays full (message 0xe2, checked before 0x15e) | message 0x15e |
| GT-001-G | O-60 | freighter with 50 kT from own 100/250 planet 110 to own any/any planet 283, 1301 ly (> 1250) | stays, undamaged, empty (message 0xe3); planet 110 surface +50 | jumps with losses |
| GT-001-G2 | O-60 | 3 Jump Gate DDs in deep space exactly 1250 ly (truncated) from own 100/250 planet 1 | fleet gone (message 0xe7) | refused at 1250; or jumps at 1251 |
| GT-001-G3 | O-60 | 3 Jump Gate DDs in deep space exactly 1249 ly (truncated) from own 100/250 planet 2 | at planet 2; each lost with 33%; survivors 495/100% | refused at 1250; or jumps at 1251 |
| GT-001-G4 | O-60 | 3 Jump Gate DDs in deep space exactly 1251 ly (truncated) from own 100/250 planet 4 | stays, 3 ships, undamaged (message 0xe3) | refused at 1250; or jumps at 1251 |
| GT-001-H | O-61 | a 500 kT design (5 x 100) at own 100/250 planet 15 to own any/any 14 | fleet gone (message 0xe7) | refused (0xe4) as at 502 kT |
| GT-001-H2 | O-61 | the 500 kT design and a Laser DD in one fleet, same jump (208 to 185) | at planet 185 with only the Laser DD, undamaged | whole fleet gone or refused |
| GT-001-I | O-62 | 2 Laser DDs at 50% damage, safe jump 113 -> 136 (100/250 both) | at planet 136, damage still 250/100% | repaired |
| GT-001-I2 | O-62 | control: the same stack parked at own gate planet 18 | repaired (below 250) |  |
| GT-001-I3 | O-62 | the same stack refused at own gate 211 (destination 192 has no gate) | stays; repaired exactly as the control I2 | not repaired (counted as moved or as a jump) |
| GT-001-K | O-63 | player 0 Laser DD gating 116 -> 67, seen by player 1 | in player 1's file at planet 67 with warp 0 | warp shown |
| GT-001-K2 | O-64 | player 1 scout chasing that DD (warp 2) | waypoint left at planet 116's position (departure) | waypoint at planet 67 (tracked) |
| GT-001-K3 | O-64 | player 0's own DD chasing it (warp 2) | waypoint at planet 67 (tracked) | frozen at 116 |
| GT-001-K4 | O-63 | control: player 0 Laser DD moving 36 ly at warp 6 in deep space | player 1 sees warp 6 and a heading |  |
| GT-001-K5 | O-64 | control: player 1 scout chasing that normally moving DD | waypoint at the DD's new position |  |
| GT-001-L | O-65 | 20 single Laser DDs (Cheap Engines owner) gating 21 -> 17 (danger 0) | all 20 at planet 17; no message 0xf2 | about 2 fail (10%% each) |
| GT-001-L2 | O-65 | control: 20 single Laser DDs at warp 9 in deep space | some stay with message 0xf2 (about 2) |  |
| GT-001-M | O-66 | Laser DD at own gate 214, warp 11 to a deep-space point | stays (message 0x147) | moves |
| GT-001-N1 | O-67 | 3 x Laser DD (41 kT) through Stargate any/300, 402 ly to any/any: danger 8% | at planet 42; each lost with 2%; survivors 40/100% |  |
| GT-001-N2 | O-67 | 3 x Laser DD (41 kT) through Stargate 150/600, 699 ly to any/any: danger 4% | at planet 111; each lost with 1%; survivors 20/100% |  |
| GT-001-N3 | O-67 | 1 x Heavy 500 (500 kT) through Stargate 300/500, 297 ly to any/any: danger 16% | at planet 181; each lost with 5%; survivors 80/100% |  |
| GT-001-N4 | O-67 | 3 x Super Freighter (202 kT) through Stargate 100/any, 300 ly to any/any: danger 25% | at planet 149; each lost with 8%; survivors 125/100% |  |
| GT-001-N5 | O-67 | 3 x Laser DD (41 kT) through Stargate any/800, 905 ly to any/any: danger 3% | at planet 257; each lost with 1%; survivors 15/100% |  |
| GT-001-N6 | O-67 | 3 x Super Freighter (202 kT) through Stargate any/any, 901 ly to any/any: danger 0% | at planet 243, undamaged |  |
