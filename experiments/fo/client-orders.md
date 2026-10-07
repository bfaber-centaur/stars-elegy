# FO client-order round (CO-01..): predictions written before the runs

The `tools/fleetlab/client-orders` tool issues **legal** client fleet orders
through the registered client, so the cases the FO corpus listed as "waiting on
the serial decision" — split and Split All (OR-18), the direct own-fleet
transfer-to-fleet order (OR-19), direct merges (order `0x25`) and the order-time
placement of those — are now reachable **without** a crafted order file. These
are the predictions for that round; the Combat-oracle lane runs them.

Designs and base are the FO corpus's (two-player Combat Lab, player 0 tech 26,
research 0%): **Freighter** = Medium Freighter + Long Hump 6, cargo **210 kT**,
fuel **450 mg** (player 0 design 11). Cargo in kT, fuel in mg. Deep-space,
stationary unless stated. Raw evidence will live in private
`stars-oracle-apparatus` `evidence/fo/` under the CO run ids.

## Rules under test

- **Ship move shares cargo/fuel by capacity, rounded down.** When a split, a
  Split All, or a two-fleet ship exchange moves ships, each cargo kind and the
  fuel move with the ships in proportion to the **capacity moved**, rounded
  **down**; the remainder stays with the source. (The Combat-oracle lane has
  already observed this on a split/exchange: fuel 280 × 500/1450 → **96**.)
  These cases pin the rounding and the remainder placement for Split All.
- **The fleet-to-fleet cargo/fuel transfer *order* (OR-19 / Q2) uses explicit
  amounts, not a capacity rebalance.** This is the discriminating question for
  elegy implementation Q2: a direct "transfer to fleet" order carries an explicit amount
  (load-all / set-amount / fill-to-%), clamped by the destination's free
  capacity, remainder staying aboard the source — the same clamps as the
  FO-02 load/unload actions — and does **not** redistribute by capacity the way
  a ship move does. Elegy's chosen rule is explicit amounts only; the competing
  hypothesis (the order rebalances by capacity like a ship move) is what these
  cases rule out.
- **Direct Merge Fleets (`0x25`).** Damage and ship-count behaviour for the
  direct order, compared with the Merge-with-Fleet *task* measured in FO-03/06/07.

## Predictions

### CO-01 — split one ship off a loaded fleet (OR-18)

Source A: 4 Freighters (cap 840/1800) holding **410 Ir, fuel 1001**. Split 1
ship into new fleet B (cap 210/450).

- B gets `floor(410·210/840)` = **102 Ir**, `floor(1001·450/1800)` = **250 fuel**.
- A keeps 3 ships, **308 Ir, 751 fuel**.

(The non-round inputs discriminate round-down from round-nearest: 102.5→102,
250.25→250.)

### CO-02 — Split All, uneven cargo (OR-18)

Source: 3 Freighters (cap 630/1350) holding **100 Ir, fuel 1000**. Split All →
three one-ship fleets B0,B1,B2 (lowest new id first), source consumed.

- Each fleet's share is `floor(100·210/630)` = **33 Ir**, `floor(1000·450/1350)`
  = **333 fuel**.
- 100 − 3·33 = **1 Ir** and 1000 − 3·333 = **1 fuel** are left over.
- **Prediction:** the rounding remainder accrues to the **first** new fleet
  (lowest id): B0 = 34 Ir / 334 fuel, B1 = B2 = 33 Ir / 333 fuel.
- **Competing hypothesis the run rules out:** the remainder stays with the last
  fleet, or is dropped. This case decides remainder placement.

### CO-03 — two-fleet ship exchange (cargo/fuel follow the ships)

A (2 Freighters, cap 420/900, **200 Ir, fuel 600**) exchanges **1 ship** to B
(1 Freighter, cap 210/450, **0 Ir, fuel 0**).

- The moved ship carries `floor(200·210/420)` = **100 Ir**, `floor(600·450/900)`
  = **300 fuel** to B. A keeps 100 Ir, 300 fuel.
- After: A 1 ship 100/300, B 2 ships 100/300. (Symmetric capacity split, round
  down; here it is exact.)

### CO-04 — direct own-fleet cargo/fuel transfer order (OR-19 / elegy Q2)

This is the open contradiction behind elegy Q2, so **two** predictions are
committed and the run decides between them. `docs/ORDERS.md` "Transfer between
the player's own fleets" currently reads the direct order as a **capacity
rebalance** (BINARY-ONLY, read from the program, not measured): the two fleets'
cargo of each kind and fuel are pooled and shared out in proportion to capacity.
The elegy implementation's proposed rule is **explicit amounts** (load-all /
set-amount / fill-to-%) clamped by free space, like the FO-02 task actions.

Setup: A (1 Freighter, cap 210, **200 Ir**, free 10) and co-located B
(1 Freighter, cap 210, **150 Ir**, free 60), **no ships move**. Order: B loads
**all Ir** from A.

- **Prediction R (capacity rebalance — the committed binary reading):** the 350
  Ir is pooled over two equal-capacity fleets → **A 175, B 175**.
- **Prediction E (explicit amount — the elegy proposal):** B takes what fits its
  free hold (**60**) → **B 210 (full), A 140**.
- `175/175` vs `210/140` is the discriminator. If R holds, the elegy rule is
  INTENTIONALLY DIFFERENT and must be labelled; if E holds, `docs/ORDERS.md`
  "Transfer between the player's own fleets" is corrected. (Contradiction
  preserved: the section reads rebalance, the implementation proposes explicit.)
- Second case to separate the orders: B does "set amount 300 Ir" from A (holds
  200). R shares the pool unchanged (175/175, the "amount" ignored); E gives B
  the 200 it names (B 210 clamped by room, A 0). Different outcomes again.

### CO-05 — direct Merge Fleets damage (O1)

Client Merge Fleets a **damaged** stack X (10 Freighters, 100 units/ship on
50%) into a **damaged** same-design stack Y (10 Freighters, 200 units/ship on
20%), legally co-located — the example `docs/ORDERS.md` "Merge order" works
through, and the two-damaged case is the one that separates the order from the
task.

- **Percent:** both the order and the task give `ceil(100·ΣD/n)` over the full
  post-merge count `n`=20, with `ΣD`=`D_X`+`D_Y`=5+2=7 → **35%**.
- **Units — prediction for the direct order** (`docs/ORDERS.md` "Merge order"):
  averaged over the **damaged** ships only, `Σ(D·units)/ΣD` = (5·100+2·200)/7 =
  **~129 units/ship**.
- **Units — the task** gave a much lower figure for the same inputs
  (**35 units**, FO-03 C observed; the task dilutes over the full slot).
- Discriminator: ~129 (order, over damaged) vs ~35 (task, over the slot). A
  large, unambiguous gap. Confirms the merge-order damage note.

### CO-06 — direct Merge Fleets ship-count boundary (O4)

From an edited start with large legal stacks, client Merge Fleets to cross the
16-bit boundary: **16000 + 16766**, **16000 + 16767**, **16000 + 16768**,
**16000 + 17000** Freighters of one design.

- **Prediction for the direct order** (`docs/ORDERS.md` "Merge order", read from
  the program): **32766 kept; 32767 kept** (the largest the order stores);
  **32768+ clamped to 32766**, the excess ships lost (not spilled, not refused).
- The Merge-with-Fleet **task** behaves differently at the top: it kept 32766
  and 32767 but **emptied the ship slot** at 32768+ (fleet record, cargo and
  fuel retained) — FO-06 E/F/G. So the discriminator is **clamp-to-32766 (order)
  vs empty-the-slot (task)** at 32768+.
- **Elegy's chosen rule** matches the order's clamp (32768+ → 32766), as stated
  in `docs/ORDERS.md` "Merge order".
