# GAP-001: coverage gaps left open by RG-002

Rules RG-002 never exercised:
- hostile Orbital Adjusters (W);
- scrapping at a starbase planet (S);
- the Interstellar Traveler packet costs and the packet items' resource
  cost (P);
- automatic, mixed and driverless packets (A);
- the Genesis Device (G);
- fleet gifts (T).

Planet gifts are not covered: no order kind gives a planet away
(`ORDERS.md` "Scope and vocabulary").

The predictions were pushed before any run:
- elegy 0aa44f5849ca2e90f1473cdde05bb765db46d97a (W, P, A;
  `docs/TERRAFORM-STATUS.md` and `docs/OBJECTS-STATUS.md` "GAP-001
  predictions"; elegy #183);
- elegy d2df970dd257acef2a9850cde769c435234d0dd6 (C, S, T, G;
  `docs/KERNEL-STATUS.md` "GAP-001 predictions"; elegy #182).

**Order.** All times are the recording machine's UTC clock.
- 18:23:58Z: both prediction commits were fetched from the elegy remote, as
  the heads of #182 and #183 (the time of the fetch record).
- 18:24:17Z: run 1 began.
- 18:26:38Z: run 2 began. Its output was written at 18:26:51Z and
  18:27:03Z.

The raw evidence is in the private apparatus, under `evidence/gap001`.

**Starts (sha256).**
- Run 1, `gap001.spec`: the start validated before the predictions,
  fb3fde3435b87d373a12ddfacb23cc69c8ca7eb356b3c642bc82cd62938273a2.
- Run 2, `gap001b.spec`:
  5c8a62d8f8000abc754ada79f99ace501875f66cd145ec0b44102f96f0aa4902. It
  differs from run 1 only in the populations of planets 2–7, 9–11 and 13,
  which are divided by 100, and in the added planets 14 and 16 (G3, G4).

**Setup.** The Combat Lab base, year 2400. Player 0 is an Interstellar
Traveler with NRSE, CE, OBRM, LSP and BET, at tech 26, and owns the
Genesis Device. Player 1 is a Claim Adjuster at propulsion 10 and
biotechnology 6. Player 1 treats player 0 as neutral, and player 0
treats player 1 as a friend. Every action is in the start state, as
waypoint-0 tasks and production queues, so there are no order files. One
pinned host year was run at cycles 20000 and 30000.

**Run 1 and run 2.** `gap001.spec` (run 1) gave the resource-probe
planets populations 100 times too large: the `pop` value is in units of
100 colonists. Every packet item was therefore built whole, and run 1 says
nothing about resource costs. `gap001b.spec` (run 2) divides those
populations by 100. That is the setup the predictions describe (20, 37
and 60 resources), and it adds two Genesis cost probes, G3 and G4. Every
row below is scored on run 2 alone. No resource-dependent row uses run 1.
The rows that do not depend on resources (W, S, T, A3–A5, the P1
minerals, G1) came out the same in run 1. Neither run had a battle, and neither sent a
race-degrade message.

## Results (run 2; both streams agree unless noted)

| Row | Prediction | Observed | Status |
|---|---|---|---|
| W1 | 63/60/60, original 60/60/60; messages for fleet 1/1 to both players (72% → 70%), none for fleet 1/4 | 63/60/60, original unchanged; fleet 1/1's messages as predicted; fleet 1/4 got "cannot degrade any further" (70%) | environment CONFIRMED; the fleet 1/4 message REFUTED |
| W2 | no change, no message (starbase) | as predicted | CONFIRMED |
| P1 | 40/40/40 launched, warp 7 class 1, 48 kT each, queue emptied | as predicted (30/30/30 after the launch-year decay) | CONFIRMED |
| P2 | 3 units, one 300 kT packet, ×17 at 79%, 454 kT spent | as predicted | CONFIRMED |
| P3 | 120/120/120, ×17 at 79%, 181 kT each spent | as predicted | CONFIRMED |
| A1 | 2 units (80/80/80), hidden Mixed ×1 at 9% ahead of Auto ×3, no "completed" message | as predicted | CONFIRMED |
| A2 | 120/120/120, hidden Mixed ×1 at 79% ahead of Auto ×20, no "completed" message | as predicted | CONFIRMED |
| A3 | a cancel message per item, then "completed"; minerals unchanged | as predicted | CONFIRMED |
| A4 | nothing built, Auto ×5 kept, "completed" sent | as predicted | CONFIRMED |
| A5 | as A4 | as predicted | CONFIRMED |
| C | Hauler 4/0/5 kT (and 6 resources) | the scrap sums fit 4/0/5; resources not observable here | minerals CONFIRMED |
| S1 | 56/20/18; scrap message; no tech | as predicted | CONFIRMED |
| S2 | 52/20/13; scrap message; no tech attempt | as predicted | CONFIRMED |
| T1 | player 1's fleet 3, same place, 200 mg, given/received messages | as predicted | CONFIRMED |
| T2 | refused; stays player 0's fleet 21 | as predicted, with "couldn't give" and "finished its orders" | CONFIRMED |
| T3 | given with its cargo, fleet 5 | as predicted | CONFIRMED |
| G1 | completes from 99% with 60 resources; reborn message to every player | as predicted | CONFIRMED |
| G2 | 0% (1% would need 50 of a 5,000 cost) | 1% from 37 resources | REFUTED |
| G3, G4 (no prediction) | | 28% from 999 and 14% from 500 resources | MEASURED bounds with G2: the cost is 3,445–3,567 resources, consistent with 3,500 but not pinned |
| G1 rebirth (not predicted) | | 20000: environment 49/6/38, concentrations 61/61/34; 30000: 31/42/51, 58/88/69. Not marked terraformed afterwards; surface minerals unchanged | MEASURED; the values are random-driven (draws from the year's stream) |

**Random-driven rebirth.** For each stream, the Genesis rebirth gave the same values
in run 1 and run 2, although their populations differed a hundredfold.
