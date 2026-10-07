# MG: player-message checks

Tests the private message reading (stars-decomp `docs/messages.md` and
`docs/messages-predictions.md` M-1..M-10, stars-decomp #25). The public
catalogue is `docs/MESSAGES.md`. Predictions below were committed
**before** any MG run.

## Setup

Combat Lab (`docs/ORACLE.md`), one pinned generation 2400 → 2401 per run
(`tools/fleetlab/pinned-turn`, cycles 20000 and 30000). `gen.py` writes
the specs and prints the table below (`--list`). Messages are decoded with
`tools/fleetlab/events.py`. Both players are at tech 26 everywhere,
research 0%, and mutual enemies. Owned planets are at environment 50/50/50
(100% for both races) with no installations unless stated.

## Already settled by earlier runs

Checked against the existing message records before this batch was built:

- **M-6** (0x0fa observer test): same rule as the wreckage research
  attempt in `COMBAT.md` (CB-031-obs, CB-037).
- **M-7** (0x180): the capped 2-race battle CB-039 sent no 0x180 to
  either player, although 25 fleets were left out. The capped 3-race
  battle CB-042 sent 0x180 to all three players at the battle location.
  Each one pointed at that player's highest-numbered left-out fleet.
- **M-8, first half** (0x0e2): OB-021-H. The fleet at planet 18 was
  ordered through a gate to planet 20, which had no gate. It got 0x0e2
  with slots (fleet, 20, −1, 20). The departure slot holds the
  destination.
- **M-9** (bombing variants): 0x060/0x06a in 238 bombings (CS, TK),
  including defended planets (TK-001 planet 10: smart bombs against 100
  SDI). 0x065/0x06f were never seen.
- **M-10** (end-of-game messages): CB round 5 holds 0x0b8 and 0x0bc. The
  tie case (all scores 0, survivor with the lower index) needs a scored
  game that Combat Lab cannot make in one year. It is left open.

## Predictions (stars-decomp reading)

MG-003 was added after the MG-002 fuel cases missed, MG-004 after MG-003, and MG-005 (homeworld mark, `TAKEOVER.md` T-41) last. Each was committed before its own run.

### MG-001: PP packet terraforming and impact messages; a gate jump to an enemy gate

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MG-001-A | M-1 | player 0 (PP) packet, 400/400/400 kT at warp 10, into player 1 planet 20 (no starbase, pop 2000, environment 30/70/30; PP centre 50/50/50) | player 0 gets 0x131 and/or 0x133 per changed axis, each followed by its pair 0x132/0x134 (same slots); player 1 gets no 0x131..0x134, only the impact message | player 1 gets 0x132/0x134 |
| MG-001-B | M-1 | the same packet into unowned planet 22 (environment 30/70/30) | player 0 gets 0x131/0x133 for planet 22 with no 0x132/0x134 |  |
| MG-001-C | M-2 | the same packet into player 1 planet 23, owned with population 0 | player 1 gets 0x181 with slots (planet 23, 0 = the packet owner, 0, 0) rather than a damage amount |  |
| MG-001-D | M-8 | player 0 Laser DD at its own gate (planet 12) ordered through the gate to enemy player 1's gate at planet 11 | refused: stays at planet 12; 0x0e5 with slots (fleet 0, 11, 11, 11): all three planet slots hold the destination | departure planet 12 in the second slot |

### MG-002: empty-planet messages, build-count messages and load-optimal fuel (player 0)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MG-002-A | M-3 | player 0 planet 0 (the first planet) owned with population 0 | uninhabited; 0x023 or 0x040 (depends on an uninitialised value; recorded, not predicted) |  |
| MG-002-B | M-3 | planet 2 overcrowded (15000 of 10000: shrinks), planet 3 owned with population 0 | planet 3 uninhabited with **0x023** (the planet before it shrank) | 0x040 |
| MG-002-C | M-3 | planet 5 growing (1000), planet 6 owned with population 0 | planet 6 uninhabited with **0x040** (the planet before it grew) | 0x023 |
| MG-002-D9 | M-4 | planet 9 queue: factories 3,2 | two 0x036: 3, then 2 | one 0x036 with 5 |
| MG-002-D10 | M-4 | planet 10 queue: factories 7,4 | one 0x036 with 5 (a single 0x035 is absorbed) | 0x035 + 0x036 4 |
| MG-002-D13 | M-4 | planet 13 queue: factories 2,7 | 0x036 with 2, then 0x035 | one 0x036 with 3 |
| MG-002-D14 | M-4 | planet 14 queue: factories 7,7 | one 0x036 with 2 | two 0x035 |
| MG-002-E | M-5 | Laser DD, fuel 1, load-optimal fuel at own planet 15 (no starbase), next leg 400 ly at warp 6 | 0x03c (or 0x03d if its tank is too small) with the shortfall; fuel not raised by the order; no 0x02b | 0x02b |
| MG-002-F | M-5 | Scout, fuel 2, load-optimal fuel at own planet 16, next leg about 450 ly at warp 10 | 0x03d (tank smaller than the need) or 0x03c, with capacity and need in the slots; no fuel gained |  |
| MG-002-G | M-5 | Laser DD, fuel 280 (full), load-optimal fuel at own planet 18, next leg 20 ly | the fuel above the need is unloaded: 0x02d (fuel), fleet keeps about the need | no message, fuel kept |
| MG-002-H | M-5 | Laser DD, fuel 280, load-optimal fuel at own planet 19, no further waypoint | all fuel unloaded: 0x02d with 280, fuel 0 | fuel kept |
| MG-002-I | M-5 | Laser DD, fuel 3, arrives at unowned planet 4 with load-optimal fuel, next leg about 350 ly | 0x126 (cannot load fuel there) after arrival | no message |

### MG-003: load-optimal fuel with an own fleet as the target (follow-up to MG-002 E..I)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MG-003-A | M-5 | Laser DD X, fuel 50, load-optimal fuel targeting own empty Laser DD Y (deep space), next leg 340 ly at warp 6 | H1: 0x03c with the shortfall, X keeps 50, Y 0. H2: X gives all 50 to Y (0x02d 50) |  |
| MG-003-B | M-5 | the same with X fuel 280 and a 20-ly next leg | H1: X keeps about the need for 20 ly and Y gets the rest (0x02d). H2: Y gets all 280 |  |
| MG-003-C | M-5 | Scout X, fuel 2, next leg about 330 ly at warp 10, own empty Laser DD Y | H1: 0x03d (capacity 50 below the need) or 0x03c, X keeps 2. H2: Y gets 2 (0x02d) |  |

### MG-004: load-optimal fuel at own planets with a starbase (follow-up to MG-002 and MG-003)

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MG-004-A | M-5 | Laser DD, fuel 1, load-optimal fuel at own planet 15 with an Orbital Fort, next leg 400 ly at warp 6 | if the order runs as with a fleet target: 0x03c and the fleet waits (no load, H1); if planets are skipped as in MG-002: no message and the fleet leaves |  |
| MG-004-B | M-5 | Laser DD, fuel 280, load-optimal fuel at own planet 18 with an Orbital Fort, next leg 20 ly | if the order runs: surplus offered to the planet; else no message, fuel kept |  |

### MG-005: homeworld mark after the homeworld is captured

| Case | Prediction | Setup | Predicted | Rules out |
|---|---|---|---|---|
| MG-005-A | T-41 | player 0 freighter in orbit of player 1's homeworld 8 (pop 10, no starbase) unloads 100 colonists on waypoint 0 (invasion before movement, T-5) | planet 8 owned by player 0 and still marked homeworld; player 1's record still names planet 8; player 0's homeworld 17 still marked | mark cleared, or moved to a planet of player 1 |


## Results

Raw evidence is in apparatus `evidence/mg/` (apparatus #32). MG-001 and
MG-002 ran at cycles 20000 and 30000 and gave the same messages in both,
apart from the random terraform counts. MG-003 and MG-004 ran at 20000.

- **MG-001-A (M-1) CONFIRMED.** Player 0 got 0x133 + 0x134 for each of the
  three axes, and in the 30000 stream also 0x131 + 0x132 (one permanent
  click of temperature). Each pair had the same slots, for example
  (1, 0, 20, 31): raised, gravity, planet 20, new value. Player 1 got only
  the impact message 0x0d8 (planet 20, 1,200 kT, player 0, 1,500
  colonists) and none of 0x131..0x134. Environment 30/70/30 became
  31/68/32 (20000) and 32/68/31 with original 30/69/30 (30000).
- **MG-001-B CONFIRMED.** For the unowned planet 22, player 0 got 0x133 alone
  on each axis, with no 0x134.
- **MG-001-C (M-2) CONFIRMED** in its discriminating part. Player 1 got 0x181
  with slots (23, 0, 0, 0). The amount slot held 0, not the 1,200 kT.
  The packet owner was player 0, so "owner number" and "always player 1"
  cannot be told from a constant here. Then 0x040 followed for planet 23,
  which was left with 0 colonists.
- **MG-001-D (M-8) CONFIRMED.** The gate jump to the enemy gate was
  refused. The fleet stayed at planet 12 and got 0x0e5 with slots
  (0, 11, 11, 11).
- Side effect: a PP race with this habitability fails the race check in a
  running game. Player 0 got 0x117 and player 1 got 0x182 naming player 0
  (as in RD-P12). The packet results above are unaffected.
- **MG-002-A..C (M-3) CONFIRMED.** Both streams:
  - planet 3 (0 colonists) after planet 2 shrank (0x026, 156 lost): 0x023;
  - planet 6 after planet 5 grew: 0x040;
  - planet 0, the first planet: 0x040.
- **MG-002-D (M-4) CONFIRMED,** all four planets:
  - 3 then 2 gave 0x036(3) and 0x036(2);
  - 1 then 4 gave 0x036(5);
  - 2 then 1 gave 0x036(2) then 0x035;
  - 1 then 1 gave 0x036(2).
- **MG-002-E..I (M-5) MISSED.** With a planet as the waypoint-0 target, load-optimal fuel did nothing:
  - no 0x03c, 0x03d, 0x02d or 0x126;
  - fuel unchanged by the order;
  - the fleets left on their next leg (0x08b for the ones that ran dry).
  - H, with no further waypoint, kept its 280 mg and got 0x04e.
- **MG-003 (follow-up) H1 CONFIRMED with a fleet target.**
  - A: 0x03c with slots (−1, target fleet, fleet 0, shortfall 24). X kept 50 and did not move.
  - B: 0x02d gave 275 to Y. X kept 5 for the 20-ly leg and arrived with 0.
  - C: 0x03d with capacity 50 and need 305. X kept 2 and did not move.
- **MG-004 (follow-up).** Own planets with an Orbital Fort behaved like MG-002: no message, and the fleets left. Load-optimal fuel aimed at a planet appears to be skipped. The cause is not yet read from the binary.
- Not run: the 0x0b8/0x0bc tie case (M-10) and 0x126.
