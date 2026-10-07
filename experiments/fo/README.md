# FO: fleet orders given through the original client

These are fleet orders written by the original client (`tools/fleetlab/client-orders`), followed by one pinned host year (`tools/fleetlab/pinned-turn`, cycles 20000). This is a tooling check: each order is given in the client, and the host's result is read back. Raw files are in the private apparatus, `evidence/fo/`. Those are the client's order files, screenshots and game files.

## Setup

`fo1.spec` on the Combat Lab base. Player 0 has two designs, Hauler (Medium Freighter) and Looker (Scout). Fleet 0 is one Hauler at its homeworld (planet 17). Fleets 1 to 4 sit at the deep-space point (1100, 1230), so no fleet refuels there:

| Fleet | Ships | Fuel | Cargo |
|---|---|---|---|
| 1 | 3 Hauler, 2 Looker | 300 | none |
| 2 | 2 Hauler | 400 | 40/30/20 |
| 3 | 1 Hauler | 100 | none |
| 4 | 1 Looker | 20 | none |

One pinned year gives the `CB.M1` that is opened in the client.

## FO-1 (`fo1.cmds`), 2026-10-07

These are the orders the client wrote, in order (`combatlab dump`):

1. Rename fleet 4 "Picket".
2. Cargo between fleet 1 and fleet 3: 50 mg of fuel to fleet 3.
3. Cargo between fleet 1 and fleet 2: 10 kT of ironium and 30 mg of fuel to fleet 1.
4. Split fleet 1: one Hauler and one Looker go to the new fleet 5.
5. Merge fleet 4 into fleet 1.
6. Move one Hauler from fleet 2 to fleet 1.

The host year after it:

| Fleet | Ships | Fuel | Cargo |
|---|---|---|---|
| 1 | 3 Hauler, 2 Looker | 389 | 22/15/10 |
| 2 | 1 Hauler | 185 | 15/15/10 |
| 3 | 1 Hauler | 150 | none |
| 5 | 1 Hauler, 1 Looker | 96 | 3/0/0 |

Fleet 4 is gone.

Every order was applied. The split and the exchange shared fuel and cargo by capacity, rounding down:

- Fleet 1 had 280 mg of fuel and fuel capacity 1450. The split took ships with capacity 500, so it took 280 × 500/1450 = 96 mg, leaving 184.
- Fleet 1 had 10 kT of ironium and cargo capacity 630. The split took one Hauler (cargo 210), so it took 10 × 210/630 = 3 kT.
- The merge added fleet 4's 20 mg.
- The exchange took half of fleet 2's fuel (370) and cargo (30/30/20) with the one Hauler that moved.

## Exploration (same day, at the homeworld)

These orders were given at the homeworld, then the host year was run:

- split one Hauler and one Looker off a mixed fleet;
- move a fleet's only ship into another fleet with the two-fleet Merge, which emptied it;
- Merge Fleets with one other fleet;
- 1 kT of fleet-to-fleet cargo;
- a rename;
- Split All.

The host applied all of them, and the name was stored in the host file. Within the turn, Split All's new fleets took numbers 2 and 3. Those were freed earlier in the turn by the emptied fleet and the merge, and the host gave the same numbers. Fuel can't be checked at the homeworld, because its starbase refuels every fleet.
