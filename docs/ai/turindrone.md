# Turindrone (SS computer player)

This file covers what the Turindrone personality does in its own turn:
the ship designs it keeps, what it builds, and what it orders its fleets
to do. What every personality shares is in `AI.md`. That includes when a
computer player acts and what it sees (§1), the shuffled planet order
(§2), the built-in races (§3), research (§4), starbase designs and the AI
part classes (§5), hubs (§6), planet automation (§7) and scrap orders
(§8). The Automitron file, `docs/ai/automitron.md`, has the same shape,
and the two personalities share several rules, marked below.

## Status

- **CONFIRMED** (AP-001, AP-002): ship designs. Both games were predicted
  from the binary, then captured from the original as the computer players'
  order files. Every design record matched: hull, and every slot's part and
  count.
- **MEASURED** (AP-003): year-2400 orders in the AI01 capture.
- **BINARY-ONLY**: everything else here. It was read from the original
  and has not yet been tested against its output.

"Year index" T is the year minus 2400. P is the number of planets in the
universe. `Random(n)` is the host's shared generator (`AI.md` §1),
uniform in `0..n−1`. Tech fields are energy, weapons, propulsion,
construction, electronics and biotechnology. A threshold "weapons > 4"
means the current level is at least 5. A design's **alive** count is how
many ships of that design exist now, and its **built** count is how many
were ever built. Design slots are the player's 16 ship-design slots
(0–15).

## Order of the turn (BINARY-ONLY)

After the shared research step (`AI.md` §4):

1. Turn constants (below).
2. Design upkeep, then design creation ("Ship designs").
3. Planet pass: planet bookkeeping, then production at eligible planets.
4. Fleet pass: classification, then orders by fleet contents.
5. The shared planet automation (`AI.md` §7).

## Turn constants (BINARY-ONLY; Automitron identical)

- **Armada potency** `A` is 3, or `3 + (T − 120)/20` when T > 130. It is
  capped at 50. Half of it, `A/2`, is the **escort minimum**.
- **Bomber group** `G` is 6, or `6 + (T − 100)/22` when T > 115. It is
  capped at 12.
- **Design age limit** `L` is 50 years while T < 120, 70 while T < 200,
  and 100 after that.

## Ship designs

### Upkeep (BINARY-ONLY; shared with every personality)

Before it creates designs, the personality:

- merges existing ships into its newest designs: slots 4–7 and 13–15
  when slot 13 holds a design, slot 12 when it does, slots 10–11 when
  slot 10 does, slots 2–3 when slot 2 does;
- checks each of its design groups: (8, 9) freighter-warships, (6, 7),
  (13, 14) bombers, (4, 5) battleships, (12), (15), (2, 3) miners (only
  when construction ≥ 7) and (10, 11) destroyers. The newest design in a
  group is the one the group builds. The group's alive count is the sum
  over its designs, capped at 32000. A design older than `L` years with no
  ship alive is deleted. One with ships alive is marked, and from T > 60
  the marked ones are split out.

The merge, split and age rules are shared core. Their exact rules belong
in `AI.md`.

### Creation (CONFIRMED, AP-001, AP-002)

Every year, in this order, the personality writes a design to each slot
whose condition holds. "Empty" means there is no design in the slot.
"Replaced" means the slot is empty, or no ship of its design is alive. A
replaced slot that still holds a design is first deleted (a
design-delete order), then created again (a design order). A creation
fails, and the slot stays as it is (deleted, if it was just deleted), when
the hull or any slot's part cannot be built now.

| Slot | Hull | Needs (current level more than) | When |
|---|---|---|---|
| 8 | Rogue | propulsion 4, construction 7 | empty |
| 9 | Galleon | propulsion 6, construction 10 | empty |
| 10 | Destroyer | weapons 4, electronics 4, construction 3, propulsion 4 | empty |
| 1 | Colony Ship | none | replaced |
| 0 | Frigate | none | replaced |
| 2 | Miner | construction 6, electronics 3 | replaced |
| 12 | Privateer | construction 3, biotechnology 3 | replaced |
| 13 | Stealth Bomber | weapons 7, electronics 6, construction 5 | empty |
| 14 | Stealth Bomber | weapons 10, electronics 11, construction 14, propulsion 8 | empty |
| 4 | Battleship | weapons 4, electronics 5, construction 12, propulsion 6 | empty |
| 15 | Rogue | weapons 4, electronics 5, construction 12, propulsion 6 | empty |

A ship design is built the way `AI.md` §5 builds a starbase design. Each
hull slot takes the first part of its AI part class that the race can
build now. If any slot has no such part, nothing is created. Every slot is
filled to its maximum count, with no variant reduction. For the hull slots
in hull order (`COMPONENTS.md`), the classes are:

| Design | AI part classes, in hull slot order |
|---|---|
| Rogue (8, 15) | 8, 10, 16, 27, 17, 0, 13, 39, 11 |
| Galleon (9) | 8, 37, 17, 0, 13, 11, 16, 27 |
| Destroyer (10) | 8, 0, 0, 0, 9, 18, 11 |
| Colony Ship (1) | 8, 31 |
| Frigate (0) | 8, 26, 0, 37 |
| Miner (2) | 8, 13, 28, 28, 28, 28 |
| Privateer (12) | 8, 10, 12, 25, 25 |
| Stealth Bomber (13, 14) | 8, 21, 22, 12, 39 |
| Battleship (4), template a | 8, 12, 37, 6, 3, 5, 3, 7, 9, 20, 20 |
| Battleship (4), template b | 8, 12, 37, 0, 0, 0, 0, 0, 9, 19, 11 |
| Battleship (4), template c | 8, 12, 37, 6, 3, 4, 2, 7, 17, 20, 20 |
| Battleship (4), template d | 8, 12, 37, 1, 1, 1, 1, 1, 17, 19, 11 |

- **Battleship.** Up to 5 tries. Each try draws a template with
  `Random(4)`, and the first try whose design can be built wins.
- **Destroyer.** Up to 4 tries, always the same template. The original
  holds a second destroyer template, but it is chosen by `Random(1)`,
  which is always 0, so it is never used.
- **Slots 13 and 14** share one template, as do slots 8 and 15. The later
  slot is the same design re-created once the higher tech is reached.
- Names come from built-in name lists by hull kind, and pictures from the
  hull's pictures. Neither is predicted (Elegy may use its own).

Examples: the full design lists of AP-001 (every field at 10, construction
at 13) and AP-002 (every field at 20) are in `PARITY.md`
"Computer players: Turindrone and Automitron designs".

Consequences (BINARY-ONLY):

- At game start slots 0, 1 and 2 hold the starting Scout, Colony Ship and
  Midget Miner (`UNIVERSE.md` "Starting ships"). They are kept while ships
  of them are alive.
- When no Scout is alive, slot 0 is deleted. Until a Frigate can be built,
  it stays empty, and no scouts are queued.
- When no colony ship is alive, the Colony Ship design is deleted and
  written again every year (Automitron does the same with its colonizer,
  MEASURED there).

## Planet pass (BINARY-ONLY)

### Bookkeeping

For every planet:

- **Unowned and known in detail** (report level above 2): when the
  planet's value to this race (the planet value of `KERNEL.md`) is above
  0, count it as a colony target. Its **mining score** is the sum over the
  three minerals of `concentration/2`, or 75 for a concentration of 67 or
  more, capped at 127.
- **Owned by another player:** when the value is above 0, mark it as an
  **invasion target** and count it.
- **Own planet with negative value:** mark it as unwanted.
- **Own planet with a starbase and population ≥ 20,000** whose queue
  holds no ship-design item: run production (below).

### Production

Q means "append one of this design to the planet's queue". The steps run
in order.

1. **Scouts.** In year 2400 (T = 0), queue design 0 once for each step of
   `n = P; while n > 0: n −= (n ≥ 191 ? 100 : 30)`. That gives P = 128 → 5
   (MEASURED, AP-003). In later years, while slot 0 holds a Frigate design:
   Q design 0 when its alive count is below `min(P/4, 32)` and more than
   `built/10`, that is, while fewer than 90% of the scouts ever built
   have been lost.
2. **Freighter-warships.** Let `N = max(own planets/10, 2 × hubs)` (hubs:
   `AI.md` §6). When propulsion > 4 and group (8, 9) has a design: Q it if
   the group's alive count is below N; otherwise, if the count is below
   `10N/7`, Q it with chance 1/4.
3. **Colonizers.** When a colony target or an invasion target exists and
   fewer than 2 colony ships are alive: Q design 1 four times.
4. **Mine layers.** When slot 12 holds a design, with chance 1/3: let k be
   the Privateer count of the first own fleet at this planet that has
   Privateers (0 if there is none). If `k < 10`, then with chance
   `1/(2k + 1)`; if `10 ≤ k < 17`, with chance 1/8 and then `1/(2k + 1)`;
   if `k ≥ 17`, never. On success, queue 3 of design 12.
5. **Bombers.** When group (13, 14) has a design, take the first own fleet
   at this planet that counts as a war fleet. For this check, a war fleet
   has `slots 2–5 + 2 × slots 6–7 ≥ A` ships. This is Robotoid's war-fleet
   rule applied to the Turindrone's slots: for a Turindrone it counts
   miners and battleships (LEGACY BUG candidate). If that fleet's bombers
   number at least G, queue 4 bombers and end production here.
6. **Fill items**, in this order. Each runs only when its group has a
   design and the group's alive count is below its cap. It appends up to
   5 copies, one at a time, while the planet's resources and minerals left
   after the whole queue's cost still cover the design's hull cost. When
   they run out, production at this planet ends, and later fill items are
   skipped too.
   - Battleships (4, 5): cap `P/24 + 4`.
   - Group (6, 7): cap `P/12 + 8` (Turindrone never designs these slots).
   - Destroyers (10, 11): cap `P/4 + 12`.
   - Slot 15 Rogue: cap `P/12 + 8`, only while slot 15 holds a design.

## Fleet pass (BINARY-ONLY)

### Classification

A fleet with any ship whose hull is between Scout and Dreadnought in the
hull list counts as an **attack** fleet. That includes the Scout and the
Frigate. Every other fleet counts as **support**.

Then, for each fleet, its current target or colonizing planet is checked
again. A target that is gone or now owned by another player clears the
fleet's task. There is one exception. A fleet that carries colonists and
whose target is an invasion target (not an AR planet, and with no
starbase) gets a waypoint to that planet with a transport task, which
lands its colonists as an invasion (`TAKEOVER.md`). The target is marked
and the fleet is sent toward the nearest own starbase.

### Orders by contents

The first rule that matches the fleet applies.

1. **Miners** (slots 2, 3). In year 2400 they are scrapped (MEASURED,
   AP-003: both starting Midget Miners). Later, when the mining score of
   the planet they orbit is below 4, they move to the best remote-mining
   target with the remote-mine task.
2. **Fleets with two or more waypoints** are left as they are.
3. **Colony ships** (slot 1), not carrying colonists and not over an own
   planet with population ≥ 5,000:
   - if the design's engine is better than a Fuel Mizer, go to the nearest
     own starbase;
   - otherwise, or if there is none, the fleet is scrapped.

   Otherwise:
   - over an own planet, it loads 25 kT of colonists (MEASURED, AP-003);
   - it colonizes the nearest colonizable planet if there is one;
   - else it moves toward the closest suitable planet;
   - else, with chance 1/10, it explores a wormhole.

   In AP-003 the starting colony ship loaded 25 kT and then waited at home
   for three years, with no target known.
4. **Rogues and Galleons** (slots 8, 9). In year 2400 they are scrapped.
   Later they act as freighters for their hub (`AI.md` §6): the hub that
   lists this fleet, else the first own planet with a starbase.
5. **Bombers** (slots 13, 14). Over an own planet with a starbase, a group
   waits until it has at least G bombers and at least `A/2` battleships
   (slots 4, 5). Then it moves to the best enemy planet to bomb, chosen by
   the shared target rule. The choice of rule depends on a game option.
6. **Scouts and destroyers** (slots 0, 10, 11). A fleet with ships of
   slot 0, while construction > 5 and slot 0 is still a Scout hull, is
   scrapped. That retires the starting Scout so that a Frigate replaces
   it. Otherwise the shared scout targeting applies: in AP-003 the starting
   Scout got one waypoint to an unexplored planet at warp 6.
7. **A lone Privateer fleet** with one waypoint and no task gets the
   lay-mines task with both task parameters 5.

## Elegy

Elegy reproduces this personality (`AI.md`). The war-fleet count in
production step 5 (Robotoid's rule on Turindrone slots) looks unintended;
following the project's default for deterministic legacy behavior, Elegy
reproduces it behind a named legacy switch. The unused second destroyer
template has no observable effect and needs nothing.

## Open experiments

1. Production and fleet rules as predictions. Most need a long capture,
   about 60 years. Predictable early items: no Frigate design before
   Frigate tech, then no scouts; the delete-and-recreate of slot 1 when no
   colony ship is alive; the Privateer odds.
2. Easy, standard and harder levels. The routine reads no level, so the
   designs should be the same at every level.
3. The shared helpers named above need their rules in `AI.md`: merge,
   split and design ageing, scout targeting, freighter routing, the
   colonize and invasion choices, the bombing target choice, and the
   nearest-starbase move.
