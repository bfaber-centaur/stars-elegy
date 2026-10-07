# MF: minefield corpus

Tests the stars-decomp minefield reading MF-1..MF-12 (private
`docs/minefield-predictions.md`, `docs/objects.md` §2, `tools/objects.py`;
stars-decomp #23, branch `claude/project-thread-q0iccj` at d136fab; public
summary in `docs/OBJECTS.md` "Minefields", stars-elegy #50). Predictions
below were committed **before** the MF runs.

## Setup

Combat Lab, one pinned generation per run (`tools/fleetlab/pinned-turn`,
cycles 20000), as in `experiments/ob`. `gen.py` writes the specs and the
table below; `check.py` compares a run with them.

- Both players are at tech 26 everywhere (no part is stripped); research 0%.
  Mutual enemies unless the run says otherwise.
- Fields are host-file object records (`thing minefield ... [kind] [det]`).
  The 50,000-mine fields at (1200,1200) hold all 24 planets, so they decay
  50% (to 25,000, radius 158) whether decay runs before or after movement;
  every leg stays within 90 ly of the centre.
- Movers are unarmed "Tanks" (Destroyer, Trans-Galactic Drive, two
  Superlatanium: 3200 armor), so a heavy-field hit (2000) leaves them
  alive at the stop point. Damage is read as `dmgN=units/pct` (units of
  500 of armor). Variants swap the engine (Trans-Galactic Fuel Scoop; Fuel
  Mizer, which is not a ram scoop but burns no fuel at warp 4), add a
  Complete Phase Shield (500) or a Super-Stealth Cloak.
- Stops are read from the fleet position (legs run due east, so the stop
  offset is x − start) and from the hit messages, now decoded by `combatlab
  dump` (`msg id=0xc6 ...`, docs/ORACLE.md "Turn messages").
- Rate cases are scored by the decomp's `minerate` convention: a stopped
  fleet made (offset + 1) draws, a clear one 81 (or its leg length).
- MF-4 is built for power rather than copied: a heavy F2 of 400 mines 50 ly
  inside a heavy F1 of 10,000, with the legs starting inside F2, so many
  stops fall inside both fields. The rule tested is the same (smallest
  d² − count pays).
- MF-10 uses counts that stay on the intended side of 999,999 after the
  50% decay (decay runs before laying, OB-002-F).
- MF-11 uses fields of 100 mines (they survive decay as 90) so the 511
  slots stay taken when the layers lay.
- Left out: the detonate-setting validation gap (needs crafted orders).

## Predictions (stars-decomp reading)

`python3 experiments/mf/gen.py --list` prints the same table.

### MF-01: hit rate per ly in a heavy field, cloak, own fleets (mutual enemies)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-01-A | MF-1 | 24 player-1 single Tanks (12 with a Super-Stealth Cloak), warp 9, 81-ly legs inside a player-0 heavy field (e 9, 30 per mille per ly) | per-ly stop rate: 95% interval contains 30 per mille; cloaked and uncloaked alike; about 22 of 24 stopped | one roll per year; 3 or 300 per mille; cloak lowering the odds |
| MF-01-B | MF-9 | each stopped Tank (1 ship, 1 ordinary engine, 3200 armor) | damage 2000: dmg 312/100% (cloak no effect), stopped at its message position |  |
| MF-01-C | MF-6 | 6 player-0 Tanks crossing their own heavy field | all reach x=1241, no damage |  |

### MF-05a: relation direction: field owner treats the victim as friend

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-05a-A | MF-5 | MF-01 layout; player 0 (field owner) friend to player 1, player 1 enemy to player 0 | no player-1 fleet stopped | the victim's relation decides (hits) |

### MF-05b: relation direction: field owner treats the victim as enemy

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-05b-A | MF-5 | MF-01 layout; player 0 enemy to player 1, player 1 friend to player 0 | stops at the MF-1 rate (interval contains 30 per mille) | the victim's relation decides (no hits) |

### MF-02: follower chains crossing a heavy field (mutual enemies)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-02-A | MF-2 | 12 chains on one line: C flies 81 ly east at warp 9, B (10 ly behind) follows C, A (10 ly behind B) follows B; 6 chains numbered A<B<C, 6 numbered C<B<A | C and B stopped at about the MF-1 rate; A never stopped (it moves in warp-4 steps) | A stopped like B (effective warp per year for followers) |

### MF-03s: effective warp of a short final leg, standard field (mutual enemies)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-03s-A | MF-3 | 12 Tanks, warp 9, waypoint 17 ly ahead inside a standard field (e 4 = safe) | none stopped | waypoint warp 9 used (15 per mille per ly: 23% per fleet) |
| MF-03s-B | MF-3 | 12 Tanks, warp 9, waypoint 26 ly ahead (e 5: 3 per mille per ly, 7.5% per fleet) | rare stops (expected 0.9 of 12) | waypoint warp (32% per fleet) |
| MF-03s-C | MF-3 | 12 Tanks, warp 9, 81-ly legs (e 9: 15 per mille per ly) | rate interval contains 15 |  |

### MF-03h: effective warp of a short final leg, heavy field (mutual enemies)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-03h-A | MF-3 | 12 Tanks, warp 9, waypoint 36 ly ahead inside a heavy field (e 6 = safe) | none stopped | waypoint warp (30 per mille per ly: 66% per fleet) |
| MF-03h-B | MF-3 | 12 Tanks, warp 9, waypoint 50 ly ahead (e 7: 10 per mille per ly, 39% per fleet) | rate interval contains 10 | waypoint warp (78% per fleet) |

### MF-04: which field loses mines: a small field deep inside a big one (mutual enemies)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-04-A | MF-4 | player-0 heavy fields F1 10000 at (1160,1200) and F2 400 at (1210,1200); 12 Tanks start at x=1190 (inside both) and fly 81 ly east at warp 9 | every stop is paid by F1 (smallest d^2 - count): F1 -100 per stop; F2 only decays (400 -> 390) | nearest centre or nearest edge: F2 pays (-20) for stops inside F2 |

### MF-07: detonation of heavy, speed-bump and standard fields; laying order (mutual enemies)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-07-A | MF-7 | player-0 heavy field 1000 set to detonate (non-SD owner): enemy Tank, own Tank, own Mini Mine Layer inside | both Tanks dmg 312/100% (2000), layer undamaged, nobody moves; field 730 | only SD or standard fields detonate; own warships exempt |
| MF-07-B | MF-7 | player-0 speed-bump field 1000 set to detonate: enemy Tank and own Tank inside | no damage; field 730 (27%, no minimum 10) | damage or a stop |
| MF-07-C | MF-8 | player-0 standard field 1000 set to detonate: own Laser DD at 50% (dmg 250/500) and enemy fleet of 5 Tanks at 50%, enemy single Tank | Laser DD destroyed (100 + 500 > 200 armor); 5 Tanks dmg 265/100% (1600 + 100 each); single Tank dmg 78/100% (500); field 730 | damage replaces the old damage |
| MF-07-D | MF-12 | own standard field 400 (390 after decay) at (1300,1250); layers (160 each) at +10 east (lower fleet number) then +10 north | one field 710 at (1301,1252) | simultaneous merge (1302,1252) |
| MF-07-E | MF-12 | the same at (1380,1050) with the north layer numbered first | one field 710 at (1382,1051) | simultaneous merge (1382,1052) |

### MF-07f: detonation hits friends: field owner treats the victim as friend

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-07f-A | MF-7 | player-0 detonating heavy field 1000; player 0 friend to player 1; player-1 Tank inside | Tank dmg 312/100%; field 730 | friends exempt |

### MF-07sd: SD owner learns the designs its detonation damages

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-07sd-A | MF-7 | SD player 0 detonating standard field 1000 with player-1 Scoop Tank and Shield Tank inside | Scoop Tank dmg 93/100% (600), Shield Tank 39/100% (250); player 0's .M carries full designs of both; field 1000 -> 730 (SD: 1*0+2+25 = 27%) | no design learning on detonation |

### MF-09s: damage by engine, shield and fleet size, std field (mutual enemies)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-09s-A | MF-9 | 30 single- and two-ship fleets, warp 9, 81-ly legs through a player-0 std field | per stopped fleet, dmg units/500 at 100%: Tank: 78; Scoop Tank (TG Fuel Scoop): 93; Mizer Tank (Fuel Mizer, not a ram scoop): 93; Shield Tank (500 shields): 39; Tank + Cloak Tank (2 ships): 62/15 | Mizer like the Tank (ram scoops only); shields absorbing all; shortfall split |

### MF-09h: damage by engine, shield and fleet size, heavy field (mutual enemies)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-09h-A | MF-9 | 30 single- and two-ship fleets, warp 9, 81-ly legs through a player-0 heavy field | per stopped fleet, dmg units/500 at 100%: Tank: 312; Scoop Tank (TG Fuel Scoop): 390; Mizer Tank (Fuel Mizer, not a ram scoop): 390; Shield Tank (500 shields): 234; Tank + Cloak Tank (2 ships): 234/78 | Mizer like the Tank (ram scoops only); shields absorbing all; shortfall split |

### MF-10a: merge cap: own field of 2100000 mines containing a layer

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-10a-A | MF-10 | own standard field 2100000 (decays to 1050000, > 999,999) containing a Mini Mine Layer | a new 160 field at (1100,1300); the big field only decays (and is swept) | merge |

### MF-10b: merge cap: own field of 1999000 mines containing a layer

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-10b-A | MF-10 | own standard field 1999000 (decays to 999500) containing a Mini Mine Layer | merge: no field at the layer; the big field gains 160 | a new field |

### MF-11a: per-player minefield limit: 511 tiny own fields already exist

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-11a-A | MF-11 | 511 own standard fields of 100 (numbers 0..510) and a layer in open space | no new field; "failed to lay" message (0x17e) for that layer | a new field (no limit) |
| MF-11a-B | MF-11 | a layer at (1010,1010) inside the tiny fields | merges (a tiny field there gains 160) |  |

### MF-11b: per-player minefield limit: 510 tiny own fields already exist

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-11b-A | MF-11 | 510 own standard fields of 100 and a layer in open space | a new 160 field at (1100,1300) |  |
| MF-11b-B | MF-11 | a layer at (1010,1010) inside the tiny fields | merges (a tiny field there gains 160) |  |

## Follow-up runs (committed before they ran)

- Runs at the same cycles share one random stream: MF-01, MF-05b, the
  C fleets of MF-02 and the first fleets of MF-09h drew the same numbers and
  stopped at the same offsets. They are not independent rate samples. MF-01
  is repeated at cycles 15000, 25000, 30000, 35000 and 40000 and MF-09s at
  25000 and 30000; the MF-1 prediction is unchanged (pooled 95% interval
  contains 30 per mille for heavy, 15 for standard at e 9).
- MF-02 again: the first run's follow orders named fleet numbers without
  the owner (player 1's followers aimed at player 0 fleets that did not
  exist, and flew to the waypoint coordinates). `combatlab build` now writes
  `owner << 9 | number`. Same prediction, run at cycles 20000 and 25000.
- MF-11c: MF-11a created a 512th field (number 511). With 512 fields
  (numbers 0..511) the layer in open space is predicted to make no field.

### MF-11c: per-player minefield limit: 512 tiny own fields already exist

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-11c-A | MF-11 | 512 own standard fields of 100 (numbers 0..511) and a layer in open space | no new field; the layer's mines are lost (refusal message) | a new field |
| MF-11c-B | MF-11 | a layer at (1010,1010) inside the tiny fields | merges (a tiny field there gains 160) |  |

### MF-04 follow-up (committed before these runs)

MF-04 left F2 at 390 (decay only) as predicted, but F1 lost only 126 mines to
its 11 stops (10000 → 9874 before decay; one stop would be −100, eleven
−1045). Counts in every single-field run fit "each stop takes max(50,
count/100) (or max(10, count/20)) in turn, then decay, then sweeping"
exactly (MF-01, MF-02, MF-03s/h, MF-05b, MF-09s/h). Each field alone, the
same fleets, cycles 20000; and MF-04 again at cycles 25000:

### MF-04b: MF-04 with F1 only

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-04b-A | MF-4 | F1 alone (heavy 10000, 5 planets), the MF-04 fleets | F1 = 10000 less max(50, count/100) per stop in turn, then 22% decay, then the starbase sweep (1280) |  |

### MF-04d: MF-04 with F2 only

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-04d-A | MF-4 | F2 alone (heavy 400, no planets), the MF-04 fleets (40 ly inside F2) | F2 = 400 less 20 per stop, then 2% decay (min 10) |  |


### MF-02 follow-up (committed before this run)

MF-02 with owner-qualified follow orders: in chains numbered A<B<C, A
reached B's start in its first step (10 ly) and B never moved; in chains
numbered C<B<A, B and A each got their whole remainder in one step and A was
stopped twice in 6. So the 10-ly spacing did not test the fifth-of-warp²
steps. Mutual chases keep both fleets deferred:

### MF-02b: mutual chases inside a heavy field (mutual enemies)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-02b-A | MF-2 | 12 pairs 80 ly apart on one line, each Tank following the other at warp 9 | no stops: each moves in steps of about 17 ly (effective warp 4, below heavy safe 6) until they meet | per-year effective warp (9: 30 per mille per ly over about 40 ly each, 70% per fleet) |


### MF-13 and OB-010-S re-check (committed before these runs)

MF-13 (stars-decomp minefields branch c9aa82c, `objects.md` §2.6, MF-13):
with numbers 0..510 taken, a player's field number 511 is given only when
no object sorts after that player's minefields (LEGACY BUG candidate).
Objects sort by type (minefields, then packets/salvage, wormholes, Trader),
then owner, then number. MF-11a (field 511 made) had nothing after the run.
One pinned year at cycles 20000, as MF-11.

#### MF-13a: player 0 has 511 fields; one player-1 field far away sorts after them

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-13a-A | MF-13 | 511 player-0 fields of 100 (numbers 0..510), a player-1 field, and a layer in open space | no new field; "failed to lay" message (0x17e) for that layer | field 511 made (as in MF-11a) |

#### MF-13b: player 0 has 511 fields; one salvage object (type 1) sorts after them

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-13b-A | MF-13 | 511 player-0 fields of 100 (numbers 0..510), a salvage object, and a layer in open space | no new field; "failed to lay" message (0x17e) for that layer | field 511 made (as in MF-11a) |

#### MF-13c: player 1 has 511 fields; one player-0 field far away sorts before them

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MF-13c-A | MF-13 | 511 player-1 fields of 100 (numbers 0..510), a player-0 field (sorts before), and a player-1 layer in open space | a new 160 field (number 511) at (1100,1300) | refusal |

OB-010-S re-check (existing apparatus evidence `evidence/ob/ob010*`, six
cycles settings, no new run). Under the order measured in MF-4 (stops take
their loss during movement; decay then counts planets inside the field as
the stops left it; sweeping after decay), the 3000-mine standard field at
(1220,1230) has no planet inside at 3000 or 2950. Predicted final counts:
no stop → 3000 → 2940 (decay 2%) → 2840 if the five Laser DDs end inside
the field and sweep 100; one stop → 2950 → 2891 → 2791. A fleet that ends
outside the field does not sweep it (2940).
Decay before the stop's loss would give 2890 before sweeping.

## Results

Evidence: stars-oracle-apparatus `evidence/mf/` (54335b2), one directory
per run with `check.txt`. Summary in `docs/PARITY.md` "Minefield lane".

| Case | Result | Observed |
|---|---|---|
| MF-01-A | HELD | heavy e 9: 24 stops in 526 draws (45.6 per mille, 30.0–65.7); pooled over streams 20000, 15000, 30000: 69 in 2137, 32.3 (25.4–40.3); cloaked 29.1, uncloaked 36.1 |
| MF-01-B | HELD | every stopped Tank 312/500 (2000) |
| MF-01-C | HELD | 6 own Tanks at their waypoints, undamaged |
| MF-05a-A | HELD | owner friend to victim: 0 stops in 1944 draws |
| MF-05b-A | HELD | owner enemy to victim (victim friend to owner): as MF-01 (same stream) |
| MF-02-A | CONTRADICTED | numbered A<B<C: A never stopped, but it landed on B in its first step and B never moved; numbered C<B<A: A stopped in 2 of 6 (whole remainder in one step) |
| MF-02b-A | HELD | mutual chases: 0 of 24 stopped (streams 20000 and 15000); moved 46 and 34 ly in 17-ly steps |
| MF-03s-A | HELD | 17-ly legs (e 4): 0 stops in 204 draws |
| MF-03s-B | OBSERVED | 26-ly legs (e 5): 1 of 12 stopped |
| MF-03s-C | HELD | 81-ly legs: 16.6 (8.0–29.8); pooled with MF-09s (2 streams) 15.9 (11.6–21.0) |
| MF-03h-A | HELD | 36-ly legs (e 6): 0 stops in 432 draws |
| MF-03h-B | HELD | 50-ly legs (e 7): 17.0 (7.4–32.7) |
| MF-04-A | HELD | 11 stops, 10 inside F2; F2 400 → 390 (decay only); F1 paid all |
| MF-04b-A | HELD | F1 alone: same count 6422 (after correcting the prediction: decay counts the planets inside the field after the stops, 3 not 5) |
| MF-04d-A | HELD | F2 alone: 9 stops, 400 → 244 |
| MF-07-A | HELD | heavy detonation: enemy and own Tank 312/500, layer untouched, field 730 |
| MF-07-B | HELD | speed-bump detonation: no damage, field 730; "stopped" messages to both fleets |
| MF-07-C | HELD | Laser DD destroyed; 5 Tanks 265/500; single Tank 78/500; field 730 |
| MF-07-D, E | HELD | (1301,1252) 710 and (1382,1051) 710 |
| MF-07f-A | HELD | friend's Tank 312/500 |
| MF-07sd-A | HELD | SD owner got full designs of both damaged designs; Scoop Tank 93/500, Shield Tank 39/500; field 730 |
| MF-09s-A, MF-09h-A | HELD | every stopped fleet matched (table in PARITY.md); Fuel Mizer takes the no-fuel-at-warp-4 figures |
| MF-10a-A | HELD | 1,050,000 after decay: new 160 field at the layer |
| MF-10b-A | HELD | 999,500 after decay: merged, centre (1199,1200) |
| MF-11a-A | CONTRADICTED | with 511 fields a 512th (number 511) was made |
| MF-11b-A | HELD | with 510 fields, field number 510 made |
| MF-11c-A | HELD | with 512 fields: no field, message 0x17e, mines lost |
| MF-11a/b/c-B | HELD | the layer inside a tiny field merged (90 + 160 = 250) |

Field counts in every run fit: stops shrink the field during movement,
then decay (planets counted in the shrunken field), then sweeping.
