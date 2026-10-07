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
