# FO: fleet operations corpus (FO-01 to FO-05)

Oracle round on the "Fleet operations" rules of `docs/ORDERS.md`
(stars-elegy #40, all BINARY-ONLY; private derivation and predictions
OR-14..19 in stars-decomp #12). Only what waypoint tasks written into the
host file can set up is tested here; nothing uses a crafted order (.X) file.

## Setup

- Combat Lab (CB, game id 82222, two JOAT players), one pinned generation
  per run (`tools/fleetlab/pinned-turn`, cycles 20000). Player 0 tech 26,
  research 0% for both. Specs and predictions: `gen.py`; checker:
  `check.py`.
- Freighter = Medium Freighter + Long Hump 6 (cargo 210 kT, fuel 450 mg),
  player 0 design 11. Colonizer = Colony Ship + Long Hump 6 + Colonization
  Module (cargo 25, fuel 200), design 12. Player 1's freighter is its CB
  design 3 (Medium Freighter, Long Hump 6, Rhino Scanner, Crobmnium).
- Fleets in deep space sit at spots more than 30 ly from every planet.
  Own planets have no starbase, no mines and no factories, so their surface
  minerals change only by the case.
- New CombatLab spec syntax: `target fleet OWNER ID` makes waypoint 0
  target a fleet (id `number | owner << 9`, type 0x12); `to X Y fleet OWNER
  ID warp W` adds a fleet-targeted waypoint; tasks `merge` (4) and
  `transfer K` (9, recipient as the K-th other player).
- A tooling smoke run before the predictions showed the encodings work: a
  merge into a fleet-targeted waypoint 0, a fleet-to-fleet "load all" of
  Ir and fuel, and a transfer to player 1 (which received a fleet of a
  copied design in a free slot) all applied.

## Not tested here (waiting on the serial decision)

These need an order file the registered host accepts:

- split and split-all (ORDERS "Split"; OR-18);
- the direct "transfer to fleet" order between own fleets, its owner check
  and the capacity-proportional sharing (ORDERS "Transfer between the
  player's own fleets"; OR-19);
- direct merges (order 0x25) and their co-location check;
- order-time placement of direct loads, unloads and transfers (ORDERS
  "Turn placement", replay step).

Also not tested: steal mode (a robber-baron scanner loading from another
player's fleet), the "fleet may carry colonists" condition on a fleet
that fails it, and transfers to an AI player.

## Predictions (written before the runs)

Sources: "ORDERS" is the public rule in #40; "decomp §..." is the
stars-decomp reading (orders-misc §3, fleet-gates-merge §3-4) where ORDERS
says nothing about the detail. Cargo in kT, colonists in kT (100s),
populations in 100s; growth 15% (`grow`).

### FO01: transport loads from an own planet: clamps, kinds in order, actions 3/5/6/8/9, fuel

| Case | Source | Setup | Predicted |
|---|---|---|---|
| A | ORDERS clamp | own planet 0 surface 500/500/500; empty Freighter in orbit loads all Ir: capped by the free hold | fleet 0/0: fe 210, bo 0, ge 0; planet 0: surface 290/500/500 |
| B | decomp §3.1 order | planet 1 surface 150/150/0; load all Ir and all Bo: Ir first (150), Bo gets the rest (60) | fleet 0/1: fe 150, bo 60; planet 1: surface 0/90/0 |
| C | ORDERS clamp | planet 2 surface 0/0/500; Freighter holding 50 Ir loads exactly 300 Ge: gets 160 | fleet 0/2: fe 50, ge 160; planet 2: surface 0/0/340 |
| D | ORDERS colonists | planet 3 P=87; Freighter loads exactly 30 colonists before growth: fleet 30, planet grows from 57 | fleet 0/3: col 30; planet 3: pop 65 |
| E | decomp §3.1 fuel | planet 4 (no starbase) surface 100/0/0; Freighter fuel 200 loads all fuel and all Ir: no fuel from a planet, Ir 100 | fleet 0/4: fe 100, fuel 200 |
| F | decomp §3.1 a=5 | planet 5 surface 500/0/0; fill to 50% Ir: 105 (half of 210) | fleet 0/5: fe 105 |
| G | decomp §3.1 a=8 | planet 6 surface 500/0/0; set amount Ir to 80: loads 80 | fleet 0/6: fe 80 |
| H | decomp §3.1 a=9 | planet 7 surface 300/0/0; set waypoint Ir to 100: loads 200, planet keeps 100 | fleet 0/7: fe 200; planet 7: surface 100/0/0 |
| I | decomp §3.1 a=6 | planet 9 surface 100/0/0, wait for 100% Ir, second waypoint planet 14: loads 100 and stays at planet 9 | fleet 0/8: fe 100, x 1208, y 1297 |
| J | decomp §3.1 a=5 / turn placement | control for I: planet 11 surface 100/0/0, fill to 100% Ir, second waypoint planet 12 (35 ly): loads 100 before movement and arrives at planet 12 with it | fleet 0/9: fe 100, x 1245, y 1158 |
| K | turn placement | Freighter 20 ly from own planet 13 (surface 300/0/0) arrives with load all Ir: loads after movement, 210 | fleet 0/10: fe 210, x 1249, y 1354; planet 13: surface 90/0/0 |

### FO02: transport between two of player 0's fleets (waypoint 0 targets the other fleet)

| Case | Source | Setup | Predicted |
|---|---|---|---|
| L | ORDERS clamp | X (0/0/100 Ge, free 110) loads all Ir and all Bo from Y (150/60): X gets 110 Ir, 0 Bo | fleet 0/1: fe 110, bo 0, ge 100; fleet 0/0: fe 40, bo 60 |
| M | ORDERS clamp (hold and tank separate) | X full hold (210 Ir), fuel 200, loads all Ir and all fuel from Y (50 Ir, fuel 450): no Ir, fuel capped by the free tank (250) | fleet 0/3: fe 210, fuel 450; fleet 0/2: fe 50, fuel 200 |
| N | ORDERS clamp (shortfall stays) | X (200 Ir) unloads all Ir to Y (100 Ir, free 110): Y 210, X keeps 90 | fleet 0/5: fe 90; fleet 0/4: fe 210 |
| O | ORDERS clamp (fuel) | X fuel 400 unloads exactly 300 fuel to Y (fuel 300, free 150): Y 450, X 250 | fleet 0/7: fuel 250; fleet 0/6: fuel 450 |
| P | decomp §3.1 (own fleet) | X (50 colonists) unloads all colonists to Y: Y 50, X 0 | fleet 0/9: col 0; fleet 0/8: col 50 |
| Q | decomp §3.1 a=7 | X (fuel 200, one waypoint) "load optimal" fuel: unloads all its fuel to Y (fuel 100): Y 300, X 0 | fleet 0/11: fuel 0; fleet 0/10: fuel 300 |
| R | turn placement / follow | X loads all Ir from Y (100 Ir); Y leaves for a point 30 ly away: X loads before movement, then follows Y (one fleet-targeted waypoint) to Y's destination | fleet 0/13: fe 100, x 1010, y 1310; fleet 0/12: fe 0, x 1010, y 1310 |
| S | turn placement | X arrives (30 ly) at stationary Y, its second waypoint targeting Y, and unloads all Ir (100) to Y after movement | fleet 0/15: fe 0, x 1010, y 1325; fleet 0/14: fe 100 |
| U | turn placement | X arrives (30 ly) at stationary Y, its second waypoint targeting Y, and loads all Ir (100) from Y after movement | fleet 0/17: fe 100, x 1010, y 1370; fleet 0/16: fe 0 |

### FO03: Merge with Fleet waypoint task (deep space, stationary unless stated)

| Case | Source | Setup | Predicted |
|---|---|---|---|
| A | ORDERS merge | X (2 Freighters, 100 Ir, fuel 300) merges into Y (3 Freighters, 50 Bo, fuel 400): Y keeps its id, 5 ships, 100/50, fuel 700; X removed | fleet 0/0: ships 11:5, fe 100, bo 50, fuel 700; fleet 0/1 gone |
| B | ORDERS merge (per design) | X (1 Colonizer, 20 colonists, fuel 150) merges into Y (1 Freighter, fuel 100): Y has both designs, 20 colonists, fuel 250 | fleet 0/2: ships 11:1,12:1, col 20, fuel 250; fleet 0/3 gone |
| C | ORDERS merge (damage) | X 10 Freighters 100 units on 50%, Y 10 Freighters 200 units on 20%: D = 5 + 2, units (500+400)/7 = 128 on ceil(700/20) = 35%, then repair 10 -> 118/35 | fleet 0/4: ships 11:20, dmg 11: 118/35% |
| D | ORDERS merge (damage) | X 10 Freighters 100 units on 50% into undamaged Y 10 Freighters: 100 units on 25%, then repair -> 90/25 (if an undamaged stack counts as one damaged ship: 83 on 30% -> 73/30) | fleet 0/6: ships 11:20, dmg 11: 90/25% |
| E | ORDERS merge (cap) | X 1000 Freighters into Y 32000 Freighters: 32766 (per-design cap) | fleet 0/8: ships 11:32766; fleet 0/9 gone |
| F | decomp §3.5 (no distance check) | X (1 Freighter, 30 Ir) at (1205, 1235) targets Y (1 Freighter) at least 100 ly away with merge: merged anyway (the task has no position test) | fleet 0/10: ships 11:2, fe 30, x 1010, y 1235; fleet 0/11 gone |
| G | turn placement | X merges into Y before movement; Y then leaves for a point 30 ly away: Y arrives with 2 ships | fleet 0/12: ships 11:2, fe 40, x 1010, y 1310; fleet 0/13 gone |
| H | turn placement | X arrives (30 ly) at stationary Y, its second waypoint targeting Y with merge: merged after movement | fleet 0/14: ships 11:2, fe 40, x 1010, y 1325; fleet 0/15 gone |

### FO04: cargo, merge and fleet transfer toward player 1; player 1 is neutral toward player 0, player 0 an enemy toward player 1

| Case | Source | Setup | Predicted |
|---|---|---|---|
| A | decomp §3.1 relation | X (50 Ir) unloads all Ir to player 1's freighter Z: Z gets 50 | fleet 0/0: fe 0; fleet 1/0: fe 50 |
| B | decomp §3.1 (0x155) | X (30 colonists) unloads all colonists to player 1's freighter Z: refused, X keeps 30 | fleet 0/1: col 30; fleet 1/1: col 0 |
| C | decomp §3.1 (no steal) | X (no scanner) loads all Ir from player 1's freighter Z (100 Ir): nothing moves | fleet 0/2: fe 0; fleet 1/2: fe 100 |
| D | ORDERS merge (owner) | X merges into player 1's freighter Z: refused, both unchanged | fleet 0/3: ships 11:2, fe 20; fleet 1/3: ships 3:1 |
| E | decomp §3.3 | X (2 Freighters, 100 Ir, fuel 300) transfers to player 1: X removed; player 1 gets a fleet there with 2 ships of a copied Freighter design, 100 Ir, fuel 300 | fleet 0/4 gone; player 1 fleet at 1010,1190: n 2, fe 100, fuel 300, hull Medium Freighter |
| F | decomp §3.3 | X (1 Freighter, 10 colonists) transfers to player 1: refused (carries colonists) | fleet 0/5: ships 11:1, col 10; no player 1 fleet at 1010,1235 |

### FO05: cargo, merge and fleet transfer toward player 1; player 1 is an enemy toward player 0, player 0 neutral toward player 1

| Case | Source | Setup | Predicted |
|---|---|---|---|
| A | decomp §3.1 relation | X (50 Ir) unloads all Ir to player 1's freighter Z: nothing moves (relation 2 toward the giver) | fleet 0/0: fe 50; fleet 1/0: fe 0 |
| B | decomp §3.1 (0x155) | X (30 colonists) unloads all colonists to player 1's freighter Z: refused, X keeps 30 | fleet 0/1: col 30; fleet 1/1: col 0 |
| C | decomp §3.1 (no steal) | X (no scanner) loads all Ir from player 1's freighter Z (100 Ir): nothing moves | fleet 0/2: fe 0; fleet 1/2: fe 100 |
| D | ORDERS merge (owner) | X merges into player 1's freighter Z: refused, both unchanged | fleet 0/3: ships 11:2, fe 20; fleet 1/3: ships 3:1 |
| E | decomp §3.3 | X (2 Freighters, 100 Ir, fuel 300) transfers to player 1: refused, X unchanged | fleet 0/4: ships 11:2, fe 100; no player 1 fleet at 1010,1190 |
| F | decomp §3.3 | X (1 Freighter, 10 colonists) transfers to player 1: refused (carries colonists) | fleet 0/5: ships 11:1, col 10; no player 1 fleet at 1010,1235 |

