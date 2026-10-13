# T15: the yearly design check against the owner's tech (DC-1 to DC-6)

The question came from the review of lane A's T-37 work. Elegy's
ASSUMPTION T15 says that the year's design check uses the owner's tech
from before the year's research, and that a design received with a
fleet transfer is checked against the recipient's tech. The coordinator
also asked for a part gated by energy alone. `TAKEOVER.md` "Design parts
dropped when the year is generated" and PARITY "Design parts dropped" and
T-37 already showed parts being removed, but only parts gated by
weapons, electronics or construction, and never with a level-up in the
gating field or a design received by transfer.

Pre-run records, never edited after the runs:

| Starts | Record | Pushed (activity API) | Runs started |
|---|---|---|---|
| `t15-ctl`, `t15-pre`, `t15-up` (DC-1 to DC-3) | `PREDICTION.md`, 28ef34c | 08:29:06Z | 08:29:22Z |
| `t15-p1own`, `t15-recv0` (DC-4, DC-5) | `PREDICTION-DC4.md`, 5363e44 | 08:34:54Z | 08:35:10Z |
| `t15-load` (DC-6) | `PREDICTION-DC6.md`, 4bb648f | 08:40:24Z | 08:40:36Z |

`gen.py` writes the specs. Later versions add DC-4 and DC-5 (5363e44)
and then DC-6 (4bb648f), and leave the earlier specs unchanged. Combat Lab, two JOAT players,
neutral to each other. Each start ran at cycles 20000, 30000 and 14000
with `tools/fleetlab/years` (step 1000). DC-1 to DC-3 and DC-5 ran two
chained years, and DC-4 and DC-6 ran one. The check involves no random draw, and
the three streams agreed everywhere. Raw evidence is in the private
apparatus, `evidence/t15`. Results are read from the host file after
each year. For DC-2, player 1's own file showed the same designs.

## Results

| Case | Setup | Observed | Result |
|---|---|---|---|
| DC-1 | Player 0 at energy 9; Bear Scout carries a Bear Neutrino Barrier (energy 10). Three starts: no level-up (`ctl`, energy stays 9), a level-up at the first level-up check from stored research (`pre`, 5160 stored), and a level-up from the year's research (`up`, 5159 stored). | Energy ended at 9, 10 and 10. The barrier was removed in year 1 in all 9 runs (3 starts × 3 streams): the slot was written back empty, and the mass fell from 13 to 12. | H-before CONFIRMED by prediction (9 of 9): the check uses the tech from before any of the year's research. H-mid and H-after fail. |
| DC-3 | The same player 0. Gorilla Delagator (energy 14) and Wolverine Diffuse Shield (energy 6). | Gorilla removed in year 1, and Wolverine kept, in 9 of 9. | CONFIRMED by prediction: a part gated only by energy is checked like the others. |
| DC-2 | Player 0 (electronics 26) transfers a fleet of Possum Scouts (Possum Scanner, electronics 5) and one of Rhino Scouts (electronics 1) to player 1 (electronics 3) in year 1. | Player 1 received both fleets, with copies of the designs in its slots 6 and 7. The Possum copy still had its scanner after year 1 and after year 2, in 9 of 9 runs. Player 1's electronics stayed 3. Player 0's own Possum design was unchanged. | Prediction failed. The prediction was that the copy would be removed after year 2. What happened is the pre-run's H-never reading, MEASURED for two years. |
| DC-4 | Player 1 (electronics 3) owns its own Possum Scout, written into its slot 6. | Scanner removed in year 1 (3 of 3). | CONFIRMED by prediction: player 1's own designs are checked. So DC-2 is not a player-1 effect. |
| DC-5 | Player 1 (electronics 26) transfers a Possum Scout to player 0 (electronics 3) in year 1. Player 0's own Possum Scout is the control. | The control lost its scanner in year 1. Player 0's received copy (slot 1) kept its scanner after years 1 and 2 (3 of 3). | CONFIRMED by prediction (H-recv): a design received with a fleet transfer was not checked in the two years that followed, whichever player received it. |
| DC-6 | Player 0 at construction 8. Fleet 0/0 is a Pod Scout (Super Cargo Pod: construction 9, 100 kT; a bare Scout carries nothing) at its homeworld, with a waypoint-0 task to load all ironium. Fleet 0/1 is a Small Pod Scout (Cargo Pod: construction 3, 50 kT) with the same task, as the control. | The control loaded 50. The Pod Scout lost its pod and loaded 0, 3 of 3. | CONFIRMED by prediction: the check runs before the waypoint-0 load tasks. It says nothing about client order replay. |
| DC-6b | A Pod Scout in deep space already holding 80 kT of ironium | The pod was removed, and the fleet still held 80 kT with no cargo space, 3 of 3. | CONFIRMED by prediction: cargo above the new capacity is kept. |

In DC-6 the spec gave the two homeworld fleets the wrong coordinates
(1240,1299) together with the homeworld as their orbit. After the year
they were at the homeworld's position (1306,1060). The control's load
shows that the fleets were in orbit when the load tasks ran.

Also seen (MEASURED, not predicted): after the transfer, the giver
still had its own design in its slot (player 1's slot 6 in DC-5, player
0's slot 3 in DC-2).

## Scope

- DC-1 is one field (energy, 9 to 10) and one owner.
- DC-2 and DC-5 followed a received copy for two years after the
  transfer. Later years are NOT RUN.
- Why the copy escapes the check is not known from these runs.
- The order of the check against client orders (order replay: a split
  or another capacity-dependent order in the same year) is NOT RUN. It
  needs an order file, which waits on the serial decision. DC-6 places
  the check only against the waypoint-0 load tasks.
- Starbase designs were not part of these runs.
