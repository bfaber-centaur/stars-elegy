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

## GT-002 (after GT-001-H2 missed; predictions written before GT-002)

`python3 experiments/gt/gen.py --two OUTDIR` writes gt002.spec and cases2.json.

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| GT-002-H3 | O-61 | 500 kT + Laser DD + Small Freighter in one fleet, 100/250 gate 0 to any/any 8 (100 ly) | at planet 8 with only the Laser DD, Small Freighter (count 3 - 2 x 1 = 1) | deleted only when every design is lost |
| GT-002-H4 | O-61 | 500 kT + 500 kT + Laser DD + Small Freighter in one fleet, 100/250 gate 193 to any/any 222 (100 ly) | fleet gone (message 0xe7): count 4 - 2 x 2 = 0 | deleted only when every design is lost |
| GT-002-H5 | O-61 | 500 kT + 500 kT + Laser DD in one fleet, 100/250 gate 98 to any/any 91 (100 ly) | at planet 91 with only the Laser DD (count 3 - 2 x 2 = -1) | deleted only when every design is lost |
| GT-002-H6 | O-61 | 500 kT + 500 kT in one fleet, 100/250 gate 3 to any/any 27 (100 ly) | fleet gone (message 0xe7): every design lost |  |
| GT-002-H7 | O-61 | 500 kT + Laser DD in one fleet, 100/250 gate 196 to any/any 190 (100 ly) | fleet gone (message 0xe7): count 2 - 2 x 1 = 0 | deleted only when every design is lost |

## Results (2026-10-07, cycles 20000)

`check.py` output for both runs is in stars-oracle-apparatus
`evidence/gt/gt00N/check.txt`. GT-001: 34 held, H2 missed, L2 is a
control (1 of 20 warp-9 Cheap Engines fleets failed). GT-002: 5 of 5
held. Write-up: `docs/PARITY.md` "Stargates, round 2"; rules in
`docs/OBJECTS.md` "Stargates".

- H2 missed: the 500 kT ship and the safe Laser DD were both deleted
  (message 0xe7). The reconciled reading (a design lost entirely counts
  twice against the fleet's design count; deletion at exactly 0) was
  written into GT-002 before it ran, and held in all five mixes.

## GT-003: refusal order and loss-roll wipe-outs (BINARY-ONLY sweep)

Written before the run (`python3 experiments/gt/gen.py --three OUTDIR`, then the same build, pinned
turn and `check.py OUTDIR/cases3.json OUT`). R1-R6 each give a fleet two reasons to be refused and
predict the single refusal message the first check produces. W0-W5 send a 491 kT freighter (danger
97%, lost with 32%) with a Laser DD through a 100/250 gate: a design wiped out by the loss rolls should
count once against the design count, so the Laser DD survives.

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| GT-003-R1 | refusal order | player 1 Laser DD at player 0's gate 0 (source refused) to own planet 16 without a gate | stays; the only refusal message is 0xe6 (source gate) | 0xe2 (destination gate) first |
| GT-003-R2 | refusal order | player 1 Laser DD from own 100/250 gate 9 to player 0's gate 250, 1343 ly (over 5 x 250) | stays; only 0xe5 (destination owner) | 0xe3 (range) first |
| GT-003-R3 | refusal order | player 1 502 kT freighter from own 100/250 gate 193 to player 0's gate 173 | stays; only 0xe5 (destination owner) | 0xe4 (mass) first |
| GT-003-R4 | refusal order | player 0 502 kT freighter with 50 kT ironium and 10 kT colonists at player 1's gate 98 (friend) to own gate 122 | stays full; only 0x15e (colonists); planet 98 surface +0 | 0xe4 (mass) after the minerals were unloaded |
| GT-003-R5 | refusal order | player 0 502 kT freighter with 50 kT ironium, own 100/250 gate 276 to own any/any 4, 1350 ly (over range and over mass) | stays empty; only 0xe3 (range before mass); planet 276 surface +50 | 0xe4 (mass) first |
| GT-003-R6 | refusal order | player 0 freighter (no Jump Gate) at own planet 3 without a gate, warp 11 to deep space | stays; only 0xde (no source gate) | 0x147 (destination not a planet) first |
| GT-003-W0 | O-61 roll | Heavy 491 (danger 97%, lost with 32%) and a Laser DD, gate 196 to 190 | at planet 190 with the Laser DD, with or without the Heavy (a design wiped out by the roll counts once: 2 - 1 = 1) | fleet gone (0xe7) whenever the Heavy is destroyed |
| GT-003-W1 | O-61 roll | Heavy 491 (danger 97%, lost with 32%) and a Laser DD, gate 101 to 121 | at planet 121 with the Laser DD, with or without the Heavy (a design wiped out by the roll counts once: 2 - 1 = 1) | fleet gone (0xe7) whenever the Heavy is destroyed |
| GT-003-W2 | O-61 roll | Heavy 491 (danger 97%, lost with 32%) and a Laser DD, gate 6 to 13 | at planet 13 with the Laser DD, with or without the Heavy (a design wiped out by the roll counts once: 2 - 1 = 1) | fleet gone (0xe7) whenever the Heavy is destroyed |
| GT-003-W3 | O-61 roll | Heavy 491 (danger 97%, lost with 32%) and a Laser DD, gate 104 to 76 | at planet 76 with the Laser DD, with or without the Heavy (a design wiped out by the roll counts once: 2 - 1 = 1) | fleet gone (0xe7) whenever the Heavy is destroyed |
| GT-003-W4 | O-61 roll | Heavy 491 (danger 97%, lost with 32%) and a Laser DD, gate 202 to 183 | at planet 183 with the Laser DD, with or without the Heavy (a design wiped out by the roll counts once: 2 - 1 = 1) | fleet gone (0xe7) whenever the Heavy is destroyed |
| GT-003-W5 | O-61 roll | Heavy 491 (danger 97%, lost with 32%) and a Laser DD, gate 107 to 84 | at planet 84 with the Laser DD, with or without the Heavy (a design wiped out by the roll counts once: 2 - 1 = 1) | fleet gone (0xe7) whenever the Heavy is destroyed |

## GT-004: how a planet's gate and a gate waypoint are encoded (before the run)

For Turn orders' route-stargate upkeep case. Reading (private decomp, behavior only): a planet has a
gate when it has a starbase and that starbase's design (the planet's starbase design number, in the
owner's starbase designs) holds a stargate in any orbital slot with a count above 0. Nothing else on
the planet records the gate. A waypoint asks for the gate with warp 11 (the waypoint's warp value
11). Owner tech is not checked when a gate is used. Written with `python3 experiments/gt/gen.py --four
OUTDIR`, built on `base/raw/GT.HST`, one pinned year, checked with `check.py OUTDIR/cases4.json OUT`.

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| GT-004-G1 | gate encoding | player 0 (tech 26) Laser DD at planet 0, starbase design 0 = Space Station with Stargate any/any in its first orbital slot, waypoint warp 11 to planet 56 with the same design, 297 ly | at planet 56, fuel 100 (no fuel used), no refusal message | stays at 0; fuel used |
| GT-004-G2 | gate encoding | player 1 (base tech 3, below the gate's requirement) Laser DD, the same setup, planets 193 to 158 | at planet 158, fuel 100: gate use does not check the owner's tech | refused (0xe6 or 0xe2) |
| GT-004-G3 | gate encoding | player 0 Laser DD at planet 98 whose Space Station has the gate in its second orbital slot (slot 10), to planet 27 | at planet 27, fuel 100 (any orbital slot counts) | refused 0xe6 (only the first slot read) |
| GT-004-G4 | gate encoding | player 0 Laser DD at gated planet 3, warp 11 to planet 39 whose starbase has no gate | stays at 3, fuel 100, only 0xe2 (destination gate) | moves at normal warp; fuel used |

GT-004 result: G1, G2 and G3 jumped (0x4e, at the destination planet) and G4 stayed with only 0xe2,
as predicted. `check.py` reports MISSED for all four on the fuel field alone: the cases wrote "fuel
100" for "no fuel used", but these fleets ended the year over Space Stations, which refilled them to
280 mg. Evidence: apparatus `evidence/gt/gt004`.
