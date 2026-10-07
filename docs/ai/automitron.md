# Automitron (IS computer player)

This file covers what the Automitron personality does in its own turn:
the ship designs it keeps, what it builds, and what it orders its fleets
to do. What every personality shares is in `AI.md`. That includes when a
computer player acts and what it sees (§1), the shuffled planet order
(§2), the built-in races (§3), research (§4), starbase designs and the AI
part classes (§5), hubs (§6), planet automation (§7) and scrap orders
(§8). The Turindrone file, `docs/ai/turindrone.md`, has the same shape
and defines the notation used here (T, P, `A`, `G`, `L`, alive and built
counts, "empty" and "replaced").

## Status

- **CONFIRMED** (AP-001, AP-002): ship designs. Both games were predicted
  from the binary, then captured from the original. Every design record
  matched: hull, and every slot's part and count.
- **MEASURED** (AP-003): orders in the AI01 capture, 2400–2402.
- **MEASURED** (AP-004, AP-005): one predicted year each from AP-001's
  year-2401 game, one stream each (apparatus `evidence/ai/ap/`): the
  production threshold, a mine-layer draw, and the fuel scrap of fleet
  rule 1. Marked below.
- **BINARY-ONLY**: everything else here.

## Order of the turn (BINARY-ONLY)

The same as Turindrone's: shared research, turn constants, design upkeep
and creation, the planet pass, the fleet pass, then the shared planet
automation.

## Turn constants (BINARY-ONLY)

These are identical to Turindrone's: armada potency `A`, bomber group `G`
and design age limit `L` (`docs/ai/turindrone.md`, "Turn constants").

## Ship designs

### Upkeep (BINARY-ONLY; shared core)

- **Merging** follows the shared merge rule. From T ≥ 31 it covers the
  destroyer slot (14). From T ≥ 51 it also covers slots 2, 3 and 9–12, and
  the Privateer slot (6).
- **Groups** are (11, 12), (4, 5) freighters, (2, 3) bombers and (9, 10)
  battleships. The ageing rules are the same as Turindrone's.

### Creation (CONFIRMED, AP-001, AP-002)

The method is the same as Turindrone's. The slots are written in this
order:

| Slot | Hull | Needs (current level more than) | When |
|---|---|---|---|
| 4 | Medium Freighter | propulsion 4 | empty |
| 5 | Super Freighter | propulsion 6 | empty |
| 14 | Destroyer | weapons 4, electronics 5, construction 3, propulsion 4 | empty |
| 1 | Medium Freighter (colonizer) | none | replaced |
| 0 | Scout | none | replaced |
| 6 | Privateer | construction 3, propulsion 4, biotechnology 5 | empty |
| 2 | B-17 Bomber | weapons 7, electronics 6, construction 5, propulsion 6 | empty |
| 3 | B-52 Bomber | weapons 10, electronics 11, construction 14, propulsion 8 | empty |
| 9 | Battleship | weapons 4, electronics 5, construction 12, propulsion 6 | empty |

These are the AI part classes (`AI.md` §5) in hull slot order. Every slot
is filled to its maximum count:

| Design | AI part classes |
|---|---|
| Medium Freighter (4) | 8, 16, 10 |
| Super Freighter (5) | 8, 16, 10, 19 |
| Destroyer (14) | 30, 0, 0, 13, 9, 18, 11 |
| Colonizer (1) | 30, 31, 10 |
| Scout (0) | 30, 26, 4 |
| Privateer (6) | 30, 10, 12, 25, 32 |
| B-17 Bomber (2) | 8, 21, 23, 12 |
| B-52 Bomber (3) | 8, 21, 23, 23, 23, 12, 10 |
| Battleship (9), templates a–d | as Turindrone's, with class 10 in place of 37 in the third slot |

- **Battleship.** Up to 5 tries, each drawing a template with `Random(4)`.
- **Destroyer.** Up to 4 tries with one template. As with Turindrone, a
  second template exists, but `Random(1)` never selects it.

Consequences:

- **The colonizer is a Medium Freighter** with a colonization module
  (MEASURED, AP-003 and AP-001/AP-002 year 2401). The starting Colony Ship
  is scrapped at home in 2400, because the colony rule below requires a
  Medium Freighter design in slot 1 (MEASURED, AP-003, AP-001, AP-002).
  From 2401, while no colonizer is alive, slot 1 is deleted and written
  again every year (MEASURED, AP-003: 2401 and 2402).
- The starting Scout stays as design 0 while it is alive.

## Planet pass (BINARY-ONLY)

### Bookkeeping

As Turindrone's, except that no mining score is kept. The personality
counts the unowned, known planets of positive value (colony targets),
marks other players' planets of positive value (invasion targets), and
marks its own negative-value planets.

### Production

Production runs at an own planet with a starbase and population
≥ 150,000 whose queue holds no ship-design item. With the starting
population this means no ship production for several years: AP-003 queued
only the shared factories and mines in 2400–2402, and AP-005 none at
25,800 colonists. MEASURED (AP-004): at 160,000 colonists with an empty
queue the homeworld queued three of design 6 (step 3's draw succeeded)
and nothing else from the personality; the shared automation then
appended defenses. Q means "append one".
The steps run in order.

1. **Freighters.** This uses Turindrone's step 2 with group (4, 5): N, the
   propulsion > 4 condition, and the 1/4 chance below `10N/7`.
2. **Colonizer.** When a colony target exists, no colonizer is alive and
   T > 10: Q design 1 once.
3. **Mine layers.** When slot 6 holds a design, the odds are those of
   Turindrone's step 4, using the fleet's slot-6 count: 3 of design 6.
4. **Bombers.** When group (2, 3) has a design, take the first own fleet at
   this planet that counts as an Automitron war fleet:
   `slots 11 + 12 + 2 × (slots 9 + 10) ≥ A`. If its bombers (slots 2 and
   3) number at least G, queue 4 of the bomber design and end production
   here.
5. **Fill items**, under the same rules as Turindrone's step 6:
   - group (11, 12): cap `P/12 + 8`. Automitron never designs these slots;
   - battleships (9, 10): cap `P/24 + 4`.

The personality's own pass never queues scouts or destroyers.

## Fleet pass (BINARY-ONLY)

### Classification

The shared **attack** rule (`AI.md`) puts fleets on the attack list. The
shared **transport** rule picks out freighter-type fleets: freighter
hulls, Privateer, Rogue and Galleon. Then each colonizer's target is
checked again, under the same rules as Turindrone's, including the
invasion of a non-AR planet without a starbase by a fleet carrying
colonists.

### Orders by contents

The first rule that matches the fleet applies.

1. **Fleets with two or more waypoints.** If the Scout design's engine is
   not a ramscoop (it comes before Radiating Hydro-Ram Scoop in the engine
   list) and the fleet has less than 2 mg of fuel, the fleet is scrapped.
   This applies to every fleet, not only scouts. Otherwise the fleet is
   left as it is (MEASURED, AP-004: the two-waypoint Scout fleet at 0 mg
   got a scrap task; AP-005: with fuel it kept its route. Its second
   waypoint's warp was re-picked 6 → 5 in both runs by the shared core's
   whole-year arrival slowdown after this pass, not by this rule; `AI.md`,
   AI-11).
2. **Privateers** (slot 6), with one waypoint and no task, get the
   lay-mines task with both parameters 5.
3. **Colonizers** (slot 1):
   - if slot 1 is not a Medium Freighter design, the fleet is scrapped;
   - not carrying colonists and not over an own planet with population
     ≥ 20,000: if the design's engine is better than Quick Jump 5, it goes
     to the nearest own starbase; otherwise, or if there is none, it is
     scrapped;
   - otherwise, over an own planet, it loads 150 kT of colonists, then
     colonizes the nearest colonizable planet if there is one.

   There is no wormhole or closest-planet fallback.
4. **Bombers** (slots 2, 3). Over an own planet with a starbase, a group
   waits while it has fewer than 2 of each bomber design, or fewer than 3
   of each battleship design (slots 9 and 10). Then it picks a target as
   Turindrone's bombers do.
5. **Scouts** (slot 0). If the engine is not a ramscoop and the fleet has
   less than 2 mg of fuel, the scout is scrapped. Otherwise the shared
   scout targeting applies. In AP-003 the starting Scout went to a planet
   at warp 6 in 2400, and to another in 2401.
6. **Transports** act as freighters for their hub (`AI.md` §6), or the
   first own planet with a starbase. If the player has no planet with a
   starbase, the fleet pass stops there, and later fleets get no orders
   this year. Turindrone's Rogue and Galleon rule has the same stop.

## Elegy

Elegy reproduces this personality (`AI.md`). The fuel scrap in fleet rule
1, which reaches every multi-waypoint fleet through the Scout design's
engine, looks unintended. Following the project's default, Elegy
reproduces it behind a named legacy switch.

## Open experiments

1. Long captures for production and fleet rules. These include the first
   colonizer after T = 10, the freighter counts and the Privateer odds.
2. The fuel scrap of fleet rule 1. It needs a non-scout fleet with two
   waypoints and under 2 mg of fuel.
3. Levels other than expert, as for Turindrone.
4. The shared helpers this file names need their rules in `AI.md`, as for
   Turindrone.
