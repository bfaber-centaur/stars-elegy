# FC: fleet orders given through the original client

These are fleet orders written by the original client (`tools/fleetlab/client-orders`), followed by one pinned host year (`tools/fleetlab/pinned-turn`, cycles 20000). This is a tooling check: each order is given in the client, and the host's result is read back. Raw files are in the private apparatus, `evidence/fc/`. Those are the client's order files, screenshots and game files.

## Setup

`fc1.spec` on the Combat Lab base. Player 0 has two designs, Hauler (Medium Freighter) and Looker (Scout). Fleet 0 is one Hauler at its homeworld (planet 17). Fleets 1 to 4 sit at the deep-space point (1100, 1230), so no fleet refuels there:

| Fleet | Ships | Fuel | Cargo |
|---|---|---|---|
| 1 | 3 Hauler, 2 Looker | 300 | none |
| 2 | 2 Hauler | 400 | 40/30/20 |
| 3 | 1 Hauler | 100 | none |
| 4 | 1 Looker | 20 | none |

One pinned year gives the `CB.M1` that is opened in the client.

## FC-1 (`fc1.cmds`), 2026-10-07

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

## CO-01..06: Turn orders' client-order cases (2026-10-07)

Turn orders committed the predictions before the runs, on its own branch (`experiments/fo/client-orders.md`). Its revision of CO-04/05/06 (20:30Z) also came before those runs; the verdicts below use the revised text, and CO-05's revised setup ran as CO-05c. This lane's added cases are in `co/PREDICTIONS.md`. The setups and commands are in `co/`, and each case has its own start file. Each run is one pinned base year, then the client's orders, then one pinned host year (cycles 20000). The design is a Freighter: a Medium Freighter with a Long Hump 6, cargo 210, fuel 450. Fleets 1 and 2 sit in deep space at (1100, 1230). Raw files are in the private apparatus, `evidence/fo/co*`.

| Case | Orders the client wrote | Host result | Verdict |
|---|---|---|---|
| CO-01 | split; move 1 ship, fleet 1 → new fleet 2 | 2: 102 Ir, 250 fuel; 1: 3 ships, 308 Ir, 751 fuel | CONFIRMED |
| CO-02 | Split All of 3: two split and move pairs; the source keeps one ship | 1: 34 Ir, 334 fuel; 2 and 3: 33 Ir, 333 fuel | prediction MISSED in form, rule held (below) |
| CO-03 | move 1 ship, fleet 1 → fleet 2 | 1: 100 Ir, 300 fuel; 2: 2 ships, 100 Ir, 300 fuel | CONFIRMED |
| CO-04a | cargo, fleet 2 loads 60 Ir from fleet 1 (the client capped the 300 asked) | 1: 140; 2: 210 | E (explicit amount) CONFIRMED; R (capacity rebalance, 175/175) refuted |
| CO-04b | cargo, fleet 2 loads 200 Ir (300 asked; fleet 2 empty, not the revised text's 150 Ir B) | 1: 0; 2: 200 | E CONFIRMED; R refuted |
| CO-05 (first text) | Merge Fleets, fleet 1 (10 at 100 units on 50%) into fleet 2 (10 healthy) | 20 ships, 90 units on 25% after repair | 25% as first predicted; units do not discriminate |
| CO-05c (revised CO-05) | Merge Fleets, 10 at 100 units on 50% into 10 at 200 on 20% | 20 ships, **118 units on 35%** after repair (128 before) | CONFIRMED: 35%, (500 + 400) / 7 = 128.6 → 128 (task: 35) |
| CO-05b | Merge Fleets, 2 at 101 units on 50% into 2 at 100 on 50% | 4 ships, **90 units on 50%** after repair | Turn orders' direct-order rule CONFIRMED; task rule (41) refuted |
| CO-06 | see below | see below | merge order not reachable; the exchange path keeps at most 32765 |

Notes:

- **The client checks orders before writing them.** For a fleet-to-fleet transfer, the client caps the amount by the other fleet's free hold and by what is aboard, then writes that number. The host applied the written amount as it was (CO-04a, CO-04b; FC-1).
- **CO-02, Split All.** The client keeps the source fleet with one ship and writes one split and one move per new fleet, so the source is not consumed. Each move takes floor(share) of what is left, so the remainder stays with the source, which is the lowest-numbered fleet:
  - Ir: 100 → 33 moved, then 67 → 33 moved, leaving 34;
  - fuel: 1000 → 333 moved, then 667 → 333 moved, leaving 334.
  The predicted numbers (34/334 on the lowest id) held. The predicted form (three new fleets) did not.
- **CO-05 and CO-05b, direct merge damage.** With one damaged stack, both candidate rules give 100 units at merge (CO-05). With both stacks damaged (CO-05b), units = (101 + 100) / 2 = 100.5 → 100 before repair. That divides by the damaged count and rounds down. The Merge-with-Fleet task gave ceil(201 / 4) = 51 (FO-07 A), so the direct order and the task differ. The percent is the damaged share of all ships in both cases.
- **CO-06, ship-count boundary.**
  - The fleet panel's Merge (Merge Fleets) was disabled for the 16000-ship fleets, so the client wrote nothing (first tries). It was enabled with 10 + 10 and 2 + 2. Its exact limit was not measured.
  - The re-run moved fleet 1's ships into fleet 2 with the two-fleet exchange (a move-ships record). The client's Ship Transfer stops the destination at **32766**, so it moved 16000, 15999, 15998 and 15766 for N = 16766, 16767, 16768 and 17000.
  - The host then stored **32765** in fleet 2 each time, one ship fewer than the client showed. Controls kept 32765 (16000 + 16765) and 32000 (16000 + 16000).
  - So the host clamps the move-ships destination at 32765 and the extra ship is lost. Cargo and fuel moved by the share of ships moved (16767: 99 of 100 Ir, 999 of 1000 fuel). A source left with ships kept the rest.
  - Neither the 32768 slot-emptying of the task path nor its 32766/32767 kept counts were reachable through legal client orders.

## CO-07, CO-07b, CO-08: deleting and editing designs in use (2026-10-07)

The predictions are Turn orders' (CO-07, CO-08). This lane's pre-run notes are in `co/PREDICTIONS.md`. The setup (`co07.spec`) has three designs:
- Freighter (slot 6), used by fleet 1 (2 Freighters and a Looker), by fleet 2 (2 Freighters) and by the homeworld's queue (2 Freighters, the first 66% done);
- Looker (slot 7);
- Queued (slot 8), used only by the queue (1).

The homeworld's starbase uses starbase design 0.

- **In the client:** Edit Selected Design is disabled for a design that ships use, and for the starbase design in use. It is enabled for a design used only in a queue. Delete is enabled in every case. Its alert, in substance: "you have 4 Freighters and 2 in production with some work done; deleting destroys the ships and/or removes them from the queues". For the starbase design: "you have 1 Starbase; deleting destroys it".
- **CO-07, deleting the Freighter: CONFIRMED except renumbering.**
  - Fleet 1 lost its two Freighters and kept the Looker. Its fuel went from 500 to 27 (the Looker holds 50; 27 is observed, not explained).
  - Fleet 2 was removed.
  - The queue's Freighter entry was dropped (no Freighter was built). The Queued design was built that year and took the freed fleet number 2.
  - The slot was cleared, and the Looker and Queued kept slots 7 and 8. **No renumbering** (predicted: later designs renumber).
- **CO-07b, deleting the starbase design in use** (a ship design can't be a starbase, so this stands in for CO-07's starbase): the homeworld's **starbase was removed**. The planet kept its other state.
- **CO-08, editing:**
  - A design that ships or a starbase use can't be edited in the client, so prediction A holds there.
  - For the queued-only design, the client wrote a full design record for slot 8 (Bat Scanner added), and the host **overwrote the slot in place**. The queue entry still pointed at slot 8 and now builds the edited design. This is prediction B's "overwrite", for a slot that only a queue uses.
