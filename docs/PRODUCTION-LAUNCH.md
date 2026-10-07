# Ships and starbases leaving production

What happens when a production queue completes a ship or a starbase: the
new fleet, its number, fuel and first orders, routing to the planet's
route destination, the 512-fleet limit, and what replacing a starbase
does. It extends `KERNEL.md` "Production" (which covers spending and
queue order) and stops where the new fleet starts its first waypoint.

## Status of each rule

Tags as in `KERNEL.md`. The rules were read from the original program and
predicted as SL-01..SL-12 before the oracle ran them. The SL batch
(`experiments/sl`, stars-elegy #61; two streams, cycles 20000 and 30000,
identical results) held for every prediction it could test, so the rules
it covers are **CONFIRMED**, citing the SL item. Rules it did not reach
stay **BINARY-ONLY** and are marked so.

## Conventions

- `d` is the distance between the two planets' centres, truncated to
  whole light-years.
- `f(w)` is an engine's fuel factor at warp `w` (`COMPONENTS.md`,
  `fuel_table`), without the Improved Fuel Efficiency reduction unless
  stated.
- Fleet numbers are given as the client shows them (#1 is the first).
  Stored numbers are one less.
- Ship damage is the per-design pair (`pct`, `units`) of `COMBAT.md`:
  `pct` percent of the ships are damaged, each by `units` five-hundredths
  of the design's armor.

## When it happens

During production (`KERNEL.md` "Turn order", step 4), in queue order, as
each item completes. Each queue item that completes one or more ships in a
year makes **one** build event for that year, holding all the ships it
completed. Two items of the same design make two build events.

A new fleet exists for the rest of the year: it is refuelled with the
other fleets (step 5; it is already full), takes part in battles (step 6)
and is seen like any fleet. It does not move until next year.

## Ships

### Can the planet build it

- The planet must have a starbase. Without one, the item builds nothing
  (BINARY-ONLY).
- The owner must have the technology for the hull and every part of the
  design. If not, the item builds nothing and the owner is told the plans
  were lost (BINARY-ONLY).
- **The host does not check the starbase's dock** (LEGACY BUG). The
  original client offers ships only at a starbase with a dock, and only up
  to the dock's hull mass (200 kT for a Space Dock), but the host builds
  any ship in the queue at any starbase, including an Orbital Fort, and
  any mass at a Space Dock (CONFIRMED, SL-12: an Orbital Fort built a
  Scout, and a Space Dock built a 574 kT Mini-Miner). A hand-built order or file can
  therefore queue ships the client would refuse. **Chosen rule for an
  independent implementation:** reject at order validation any ship item
  the client could not queue (no dock, or hull mass above the dock's
  limit), as `ORDERS.md` does for other client-only checks.

In each case where nothing is built, the resources are already spent and
the item is removed from the queue (as `KERNEL.md` "Production" removes a
finished non-auto item). CONFIRMED for minerals at the fleet limit
(SL-09: the planet ended 12/6/13 kT of Fe/Bo/Ge below its control); the
resource share could not be tested there (both players at tech 26, so no
research accumulates), and is BINARY-ONLY.

### The new fleet

One new fleet per build event (CONFIRMED, SL-01: a queue of 2 Scouts,
1 Scout and 1 Colony Ship made three fleets of 2, 1 and 1 ships):

- **Number:** the owner's lowest unused fleet number (CONFIRMED, SL-02).
  With fleets #1, #2 and #4, the next is #3, then #5.
- **Fleet order.** Fleets are processed in order of owner, then number. A
  new fleet takes its place in that order by its number, so a fleet that
  fills a gap is processed before older fleets with higher numbers
  (BINARY-ONLY).
- **Ships:** the item's ships, undamaged.
- **Fuel:** tanks full (CONFIRMED, SL-01: 100, 50 and 200 mg). **Cargo:**
  none.
- **Orders:** one waypoint, at the planet, with no task and warp 0. Repeat
  off. Battle plan: the player's first plan (the default plan). No name.
  CONFIRMED (SL-01).
- **Default task** (AR only): an Alternate Reality player's new fleet that
  can mine gets the task "remote mining" on its first waypoint, at its own
  planet. No other race gets a default task at build. CONFIRMED (SL-11:
  an AR Mini-Miner got remote mining and battle plan 0; a JOAT one got no
  task).
- **Mining at its own AR planet** (a `KERNEL.md` mining rule, recorded
  here because SL-11 measured it). An AR planet mines with
  `trunc(sqrt(P))` mines (`KERNEL.md` "Production"). A same-owner fleet
  orbiting it with the remote-mining task that did not move this year
  adds its mining-robot rate to those mines, and the planet mines once
  with the total (BINARY-ONLY). The SL-11 measurement is consistent with
  it (two streams, one setup): planet with `P` 1150 (33 mines) and
  concentrations 62/10/87, Mini-Miner with two Robo-Mini-Miners (rate 8):
  41 mines predict +25/+4/+35 or 36 kT and the planet gained +25/+4/+36,
  against +20/+3/+29 in the control. Mining the fleet separately would
  also fit these values within the random +1. The planet's own gain also matches
  `KERNEL.md`: `P` 1000 → 31 mines → +19/+3/+27. In its build year the
  miner adds nothing (it moved, below).
- **"Moved this year."** The game marks, during movement, every fleet that
  did not move. A fleet built in production was not there to be marked,
  so for the rest of its first year it counts as a fleet that moved
  (CONFIRMED, SL-03: new fleets lacked the flag in their build year, and
  had it in year 2 once they had stayed put).
  Effects inside that year: it does not remote-mine (`KERNEL.md` "Remote
  mining" requires a fleet that did not move), it gets the moved-this-turn
  repair rate (`COMBAT.md` "Repair"), and it is not a stationary remote
  miner for `SCANNING.md` "Remote miners".
- Two fleets lack the flag after a year at the planet (MEASURED, SL-03 and
  SL-11, two streams; explanation BINARY-ONLY):
  - A fleet routed to its own planet has a second waypoint there at warp
    2. Movement treats it as moving (a leg of 0 ly), so it is not marked.
    On arriving, the route task routes it to the same planet again, so this
    repeats every year.
  - An AR fleet whose remote mining is added to its own planet's mining
    (above) has the flag cleared when that mining is applied, after
    movement. It did mine.
- If the planet has a route destination: see Routing.
- The owner is told the planet built the ships, and where they are routed.

### Fleet names (client)

A fleet has no stored name unless the player renames it. The client shows
the name of the design with the most ships (the first in design order on
a tie; a Fuel Transport or Super-Fuel Xport design loses ties), cut to 28
characters, with `+` added when the fleet holds more than one design, then
` #` and the number. Another player's fleet is prefixed with that player's
name. A new fleet of Scouts numbered #12 shows as "Scout #12". Seen in the
tooling check: the game wrote no name for new fleets.

## Routing

A planet can have a **route destination**: another planet. When it does,
each new fleet gets a second waypoint at that planet with the task
"route", at a warp chosen as below. The route setting itself is unchanged.
CONFIRMED (SL-04..SL-07: 28 of 28 warps, every route word unchanged).

### Ideal warp of the fleet

Start from warp 10 and take, for each design in the fleet in design
order (carrying the result from one design to the next; a new fleet has
one design):

1. The design's engine. A design with no engine gives 0.
2. Go down from the current warp until `f(w) < 121`.
3. If `f(w) > 0` and the engine is not the Trans-Galactic Mizer Scoop or
   the Galaxy Scoop, drop to a fuel-free warp just below: to `w − 1` if
   `w ≥ 5` and `f(w − 1) = 0`; else to `w − 2` if `w ≥ 6` and
   `f(w − 2) = 0`; else to `w − 3` if `w ≥ 7` and `f(w − 3) = 0`.
4. Warp 10 becomes 9 unless the engine is Interspace-10, Enigma Pulsar,
   Trans-Star 10, Trans-Galactic Mizer Scoop or Galaxy Scoop.

Results for one design: Settler's Delight 6, Quick Jump 5 5, Fuel Mizer 4,
Long Hump 6 6, Daddy Long Legs 7 7, Alpha Drive 8 8, Trans-Galactic Drive
9, Interspace-10 10, Enigma Pulsar 10, Trans-Star 10 10, Radiating
Hydro-Ram Scoop 6, Sub-Galactic Fuel Scoop 5, Trans-Galactic Fuel Scoop 6,
Trans-Galactic Super Scoop 7, Trans-Galactic Mizer Scoop 10, Galaxy Scoop
10.

### Route warp

`w` = the ideal warp. Then:

1. **Own destination with starbases.** Only if the destination belongs to
   the fleet's owner and both planets have a starbase:
   - **Gates.** If both starbases have stargates, the fleet carries no
     minerals or colonists, and a jump of the heaviest design over `d`
     would be allowed with no damage (`OBJECTS.md` "Stargates": `d ≤ R`
     and no mass over a limit), `w` = the gate setting.
   - **Dock.** Otherwise, if `w < 9` and the destination's starbase has a
     dock (any starbase but an Orbital Fort): `w` = the highest warp from 9
     down to 1 whose range on the fuel aboard (`KERNEL.md` "Not enough
     fuel", `R`) is at least `d`, or 0 if none. This can be faster than the
     ideal warp: the fleet will refuel at the destination.
2. **Step down.** If `w` is 1..10: with `m = ⌊⌊d/w⌋/w⌋`, lower `w` by one
   while `w ≥ 3` and `⌊⌊d/(w − 1)⌋/(w − 1)⌋ ≤ m`. Then lower it by one
   while the whole leg at `w` costs more fuel than the fleet carries
   (`KERNEL.md` "Fuel cost", with `L = d`). Warp 1 costs nothing, so this
   never reaches 0.
3. `w` is the waypoint's warp. Warp 0 happens only for an engine-less
   design; the owner is then told the fleet will not be routed for lack of
   fuel, and the waypoint stays at warp 0.

Vectors, CONFIRMED (SL-04..SL-07, both streams). Scout: Scout hull with
Long Hump 6, Rhino Scanner and X-Ray Laser, 23 kT, 50 mg. QJ5 Scout: Quick
Jump 5 and Bat Scanner, 14 kT, 50 mg. Stations are Space Stations; gates
are Stargate 100/250.

| Destination | `d` | Scout | QJ5 Scout |
|---|---|---|---|
| unowned | 12 | 4 | 4 |
| unowned | 17 | 5 | 5 |
| unowned | 25 | 6 | 4 |
| unowned | 41 | 5 | 5 |
| unowned | 86 | 6 | 5 |
| unowned | 299 | 6 | 5 |
| own Station | 72 | 7 | 9 |
| own Station | 84 | 7 | 7 |
| own Station with a gate (source without one) | 94 | 7 | 7 |
| own Orbital Fort (no dock) | 77 | 6 | 5 |
| the other player's Station | 77 | 6 | 5 |
| own Station, gates at both ends, `d` within range | 49 | 11 | 11 |
| own Station, gates at both ends, `d` beyond the 250 ly range | 309 | 6 | 6 |
| the building planet itself (a Station) | 0 | 2 | 2 |

Without the dock rule the three own-Station rows would give 5/5, 6/5 and
6/5, and with it the Fort and other-player rows would give 7/9. Two more
from the SL tooling check (MEASURED once): one Scout to an unowned planet
at 41 ly, warp 5; two Scouts with a Fuel Tank instead of the laser (25 kT,
600 mg) to an unowned planet at 133 ly, warp 6.

How a routed fleet behaves when it arrives (it is routed on again from
that planet's route, or given the default orders) is the route task, in
the waypoint tasks spec, not here.

## The 512-fleet limit

A player can own at most 512 fleets. The 512th fleet is made normally.
When the owner already has 512 fleets, a build event makes no new fleet:

- **Joins a fleet.** The ships join the first of the owner's fleets, in
  fleet order, that is at the planet and whose stack of that design would
  stay at or below 32,765 ships. The owner is told they were merged into
  that fleet. So with 511 fleets and two items, the first item makes the
  512th fleet and the second joins it (CONFIRMED, SL-08). A stack at
  32,765 is passed over for the next fleet at the planet (CONFIRMED,
  SL-10 variant).
- **Damage of the receiving stack.** If the stack had no ships or no
  damage, it has no damage after. Otherwise, with `n` ships before, `b`
  built, armor `A`:
  - `D = max(1, ⌊pct·n/100⌋)` damaged ships;
  - total damage `T = ⌊⌊units·A/10⌋·D/50⌋`;
  - `pct' = ⌊D·100/(n + b)⌋`, at least 1;
  - `D' = max(1, ⌊pct'·(n + b)/100⌋)`;
  - `units' = ⌊⌊5T/D'⌋·100/A⌋`.

  The total is kept and spread over `D'` ships, and truncating `D'` can
  concentrate it. CONFIRMED (SL-10, two setups): 10 Scouts (armor 20) at
  50% / 100 units, plus 1 built → 45% / 125 units; at 50% / 300 units →
  45% / 375. This is not the merge rule of `ORDERS.md` ("Damage
  dilution"), which would give 46%. Starbase repair later in the same year
  then acts on the merged stack as usual: 125 ended at 25 and 375 at 275,
  each 100 units less, the same repair the controls without a build
  showed (300 → 200, and 100 → undamaged).
- **Lost.** If no fleet qualifies, the ships are lost, the owner is told
  that only 512 fleets can be tracked, the item is removed and its
  resources stay spent (CONFIRMED, SL-09: no ship, no fleet changed, both
  ship items removed, the Factory item after them built; minerals spent,
  the resource share untested as above).

## Starbases

Building a starbase design at a planet:

- The owner must have the technology for its hull and parts; otherwise
  nothing is built and the item is removed, with no message (BINARY-ONLY).
- The new starbase replaces the old one, if any. The owner is told, with
  the dock limit when the new hull has one ("up to N kT", or "any size").
- **Queued ships.** If the new starbase's hull comes **earlier** in the
  hull list than the old one's (Orbital Fort, Space Dock, Space Station,
  Ultra Station, Death Star), every ship item is removed from the planet's
  queue, and every starbase item left in the queue loses its progress
  (percent complete back to 0). This follows hull order, not dock size:
  Space Station → Space Dock and Death Star → Ultra Station both remove
  queued ships; Space Dock → Space Station and a same-hull replacement do
  not (CONFIRMED, SL-12). Items earlier in the queue than the starbase were already
  built that year (MEASURED once: two Scouts queued before an Orbital Fort
  that replaced a Station were built).
- **Damage is kept.** The planet's starbase damage stays as it was, as
  `units` (five-hundredths of armor), so it now applies to the new
  starbase's armor, and is repaired from there as usual (CONFIRMED,
  SL-12: a Station at 200 units replaced by another Station design read
  150 after the year, as the unreplaced control did).
- **Mass driver.** If the planet had no mass driver before and the new
  starbase has one, the planet's packet speed is set to the new driver's
  speed. If it still has none, the planet's packet destination and speed
  are cleared and its queued packet items (not automatic packets) are
  removed (BINARY-ONLY).

### Cost of a replacement

Building a starbase design at a planet that already has a starbase costs
less than the design. Per component (Fe, Bo, Ge, resources), with `c` the
new design's owner cost and `o` the old design's (`COMPONENTS.md`
"Starbases", step 1–3: before the ISB/AR reduction and the halving):

- **Different hull:** `max(⌊c/2⌋, c − ⌊o/2⌋)`.
- **Same hull** (BINARY-ONLY): `c` less the hull's cost, then for each slot
  position filled in both designs, with `N` the new slot's cost (count ×
  part cost) and `O` the old slot's: the slot is charged
  `max(0, N − O)` if it holds the same part; `max(N − ⌊8·O/10⌋, ⌊2·N/10⌋)`
  if a different part of the same category; `max(N − ⌊7·O/10⌋,
  ⌊3·N/10⌋)` otherwise. The cost falls by `N` less the charge, but not
  below 0. So replacing a design by one with the same hull and the same
  parts costs nothing.

Then, as for any starbase design, ISB or AR takes `c − ⌊c/5⌋` and the
result is halved rounding up.

MEASURED for a different hull (SL-12, two streams): a JOAT + ISB Space
Dock replaced by a Space Station design of 92/72/157/364 costs
35/29/61 kT and 136 resources (a fresh design would cost 37/29/63 and
149). The item, short of resources, reached 88% and had spent
30/25/53 kT, which those costs give and the fresh costs do not
(32/25/55). The planet had 120 resources for it (below), and 88% of 120
resources means a resource cost of 135 or 136, so the fresh 149 is ruled
out too. With three times the resources the Station and both queued
Scouts were built.

Note on the SL races: both SL races were over their advantage-point
budget (JOAT + ISB −42, AR + ISB −94), so the host degraded them before
production (`KERNEL.md` "Item costs": colonists per resource 1,000 →
2,400 for player 0 and 2,500 for player 1). That changes resources only:
`trunc(1000/24) + 100 = 141`, less the 15% research share of 21, gives
the 120 above. No other SL result here depends on resources or colonists
per resource: fleet numbers, fuel, orders, warps, the fleet limit,
damage and repair do not, and the AR mining figures depend on population
and concentrations only. Where a planet built everything it queued
(every case but this one), the item counts were not resource-limited.

## Not covered here

- How resources are spent on ship and starbase items, and their costs
  (`KERNEL.md` "Production").
- What happens to queued ships when a starbase is destroyed in battle
  (`COMBAT.md`).
- The route task on arrival, and waypoint upkeep (waypoint tasks spec).
- Messages beyond what the owner is told above (messages spec).

## Elegy

Elegy's production queue does not model ship or starbase items yet
(elegy `engine/production.go`, main at b463f19). When it does:

- the dock check is added at order validation (above), instead of the
  host's missing check;
- the other rules are implemented as written, with regression tests from
  the SL vectors above. None of them is a crash or
  data corruption, so no chosen rule replaces them.
