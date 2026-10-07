# Client estimates

The original client shows the player several projections that are not
part of the year's outcome: fleet travel times, fuel use and range,
production completion years, research completion, next year's population
growth, planet value and mining rate. Elegy's client needs the same
numbers. This file says how each is computed and displayed.

Every estimate is computed by the client from the player's own file (the
`.M` file, or the host file for the same player), with the turn rules in
`KERNEL.md`. Nothing here changes the game state.

## Status

| Estimate | Where it appears | Status |
|---|---|---|
| Travel time | Fleet Waypoints tile, fleet report ETA column | CONFIRMED (ES-001, stargate legs ES-002) |
| Est. fuel usage | Fleet Waypoints tile, fleet report colours | CONFIRMED (ES-001) |
| Est. range | Fleet Composition tile | CONFIRMED (ES-001, every engine) |
| Leg distance | Fleet Waypoints tile | CONFIRMED (ES-001, `x.0y` display ES-002: LEGACY BUG) |
| Production completion | Production tile and dialog, queue colours | CONFIRMED (ES-001, "Skipped" ES-002) |
| Research estimates | Research dialog | CONFIRMED (ES-001, Generalized Research and "Maxed Out" ES-002); slower-tech doubling BINARY-ONLY |
| Population growth | population popup | CONFIRMED (ES-001) |
| Value and optimal value | planet report, planet summary | CONFIRMED (ES-001) |
| Mining rate | planet report | CONFIRMED (ES-001) |

ES-001 (one Combat Lab year, `experiments/es001`) compared 149 readings
of the original client with the rules below and all 149 matched
(`PARITY.md` "Client estimates"). ES-002 (`experiments/es002`) then
exercised the five items ES-001 left out: 81 of 83 predictions matched,
and the two misses (one fleet, one cause) corrected the stargate rule
below. BINARY-ONLY items were read from the original program and not yet
exercised.

## Fleets

`D` is the straight-line distance of a leg (floating point), `w` the warp
ordered for it (the warp stored on the leg's destination waypoint) and
`v = w²`. Leg `j` runs from waypoint `j` to waypoint `j + 1`; waypoint 0
is the fleet's position.

### Travel time (CONFIRMED, ES-001)

1. Years for one leg: 1 if `trunc(D) ≤ v`, otherwise `ceil(trunc(D) / v)`.
   A zero-length leg counts 1 year.
2. Travel time to waypoint `i` is the sum over legs `0 … i−1`.
3. Any leg at warp 0 makes it "Never" (the tile's warp box then reads
   "Stopped!").
4. Warp above 10 (a stargate leg, CONFIRMED ES-002 except where marked):
   the client checks the leg in this order.
   - No planet at the leg's destination: "Never".
   - Destination planet not the viewer's: "Uncertain", except an unowned
     planet that is in the viewer's reports this year, which is "Never"
     (that exception is BINARY-ONLY; ES-002 saw "Uncertain" for another
     player's planet and for an unowned planet absent from this year's
     reports).
   - Viewer's destination planet without a stargate: "Never".
   - Source not the viewer's planet with a stargate: "Never".
   - Otherwise each design in the fleet is checked against both gates
     with the jump rules in `OBJECTS.md` (range of the source gate, mass
     limits of both gates). A design that cannot jump at all makes it
     "Never". If any design would take losses: "Danger". Else, if the
     fleet carries any cargo and its race is not Inter-Stellar Traveler:
     "Unload". Else the leg takes 1 year.
   A usable leg (1 year, "Danger" or "Unload") counts 1 year towards the
   cumulative time of later waypoints; the gate texts themselves replace
   the time only for the gate leg's own waypoint.

The trunc matters: a 25.495 ly leg at warp 5 is 1 year (ES-001 F07). It
agrees with the movement rule in `KERNEL.md` ("Distance and arrival"):
the fleet arrives when `D < w² + 0.99999`.

Display:

- Fleet Waypoints tile, "Travel Time": cumulative time to the selected
  waypoint, "1 year" / "N years". With waypoint 0 selected the tile shows
  the next waypoint (waypoint 1) and labels the row "Next Way Pt".
- Fleet report, "ETA" column: waypoint 1 only, short form "Ny"; "--" for a
  fleet with no orders. "Never" and the ETA of a fleet that lacks the fuel
  for that leg (next section) are drawn in red. Gate texts appear here as
  in the tile ("Danger", "Unload", "Uncertain", "Never", "1y").
- Gate legs (ES-002): the tile's warp box reads "Use Stargate" in yellow,
  "Est Fuel Usage" is 0mg for the leg, and "Never" is red while
  "Uncertain", "Danger" and "Unload" are olive.

Vectors (ES-001, CONFIRMED):

| Fleet | Legs (D @ warp) | Travel time per waypoint |
|---|---|---|
| F00, 3 freighters | 28.28 @5, 50.0 @6, 42.43 @4 | 2, 4, 7 years |
| F01 | 30.0 @0, 20.0 @6 | Never, Never |
| F02 | 3.61 @1, 0.0 @5, 57.0 @7 | 3, 4, 6 years |
| F07 | 25.50 @5, 25.0 @5 | 1, 2 years |
| F08 | 50.0 @3, 90.0 @6 | 6, 9 years |

Stargate vectors (ES-002, CONFIRMED; gates 100/250 unless noted):

| Fleet | Leg | Shown |
|---|---|---|
| Scout | own gate → own gate 84.86, then 27.0 @5 | 1 year; 3 years |
| Scout | own gate (Space Station) → own gate 25.32 → own gate 84.86 | 1 year; 2 years |
| Freighter with cargo | own gate → own gate 84.86 | Unload |
| Scout | own gate → own gate 319.1 (beyond 250) | Danger |
| 120 kT freighter | own 150/600 gate → own 100/250 gate, 200.0 | Danger |
| Scout | own gate → own planet without gate | Never |
| Scout | own planet without gate → own gate | Never |
| Scout | own gate → deep space | Never |
| Scout | own gate → another player's planet | Uncertain |
| Scout | own gate → unowned planet not in this year's reports | Uncertain |

### Est. fuel usage (CONFIRMED, ES-001)

Per leg, with `cost(L)` the fleet's fuel cost of `L` ly at warp `w`
(`KERNEL.md` "Fuel cost", cargo on the cheapest engine first, rounded up
once per fleet):

1. Warp 0 or above 10: 0 mg.
2. `y = trunc((D + 0.99999)/v + 0.9999)` (years the client allows for the
   leg) and `Li = trunc(D + 0.99999)`.
3. `fuel = cost(trunc(D + 0.9999))`.
4. If `y > 1`, the leg is also priced year by year: `b = cost(v)` (one
   full year), `split = (y−1)·b + cost(Li − (y−1)·v)`, and
   `fuel = max(fuel, split)`. Then the fuel the fleet makes on the way:
   `g = ram-scoop gain of a full year at w` (`KERNEL.md` "Ram scoops and
   free warps", with `L' = v`) `+ 200` per ship whose hull is a Fuel
   Transport or Super-Fuel Xport (their yearly fuel, `KERNEL.md`). If
   `g > 0`: `fuel = b` when `g ≥ b`, otherwise
   `fuel = min(fuel, b + (y−1)·(b − g))`.

`y` can exceed the travel time: the 25.495 ly leg above has `y = 2` and is
priced year by year.

"Est Fuel Usage" to waypoint `i` sums the legs in order and shows the
largest running total. The running total restarts at 0 after a leg that
ends at one of the player's planets whose starbase can build ships
(starbase hull with a dock: refuelling, `KERNEL.md`). Displayed "Nmg",
red when it exceeds the fleet's fuel.

Fleet report: the ETA is red and the fuel figure is drawn in a warning
colour (blue in ES-001) when the fuel estimate of leg 0 alone exceeds the
fleet's fuel.

Vectors (ES-001, CONFIRMED; QJ5 Medium Freighter 64 kT, Sub-Galactic Fuel
Scoop scout 33 kT, Fuel Transport with Long Hump 6 21 kT):

| Fleet | Fuel | Legs | Est Fuel Usage per waypoint |
|---|---:|---|---|
| F00, 3 freighters + 300 kT | 400 | 28.28 @5, 50.0 @6, 42.43 @4 | 72, 294, 401 (red) |
| F03, 2 freighters + scoop scout + 100 kT | 300 | 100 @5, 100 @6 | 45, 265 |
| F04, freighter + Fuel Transport | 500 | 150 @6, 100 @7 | 25, 127 |
| F05, freighter, via its homeworld (Space Station) | 200 | 68.82 @7 to the homeworld, 97.75 @8, 200 @9 | 111, 251 (red), 829 (red) |
| F06, Alpha Drive 8 scout | 30 | 190 @9, 190 @8 | 167 (red), 196 (red) |
| F07, Long Hump 6 scout | 50 | 25.50 @5, 25.0 @5 | 3, 6 |

F03's first leg: `y = 5`, `b = 29`, whole-leg cost 114, year by year
`4·29 + 2 = 118`; the scout's gain at warp 5 is `g = 25`, so
`min(118, 29 + 4·(29 − 25)) = 45`. F05 without the refuelling reset
would show 362 and 940 for its last two waypoints.

### Est. range (CONFIRMED, ES-001)

1. The client picks an "ideal" warp for the fleet. Start at `w = 10`. For
   each design in the fleet (a design without an engine gives warp 0):
   lower `w` to the highest warp not above the current `w` whose fuel
   factor `f(w)` is at most 120. If `f(w) > 0` and the engine is neither
   the Trans-Galactic Mizer Scoop nor the Galaxy Scoop, prefer a nearby
   free warp: `w−1` if `w ≥ 5` and `f(w−1) = 0`, else `w−2` if `w ≥ 6` and
   `f(w−2) = 0`, else `w−3` if `w > 6` and `f(w−3) = 0`. Warp 10 is kept
   only for Interspace-10, Enigma Pulsar, Trans-Star 10 and the two
   scoops above; other engines get 9.
2. `C1000` at that warp exactly as in `KERNEL.md` ("Not enough fuel"):
   the cost of 1000 ly in mg, truncated.
3. "Infinite" when `C1000 = 0`; otherwise `trunc(fuel·1000/C1000)` l.y.,
   or `trunc(fuel / trunc(C1000/1000))` above 100,000.

Ideal warps and ranges (ES-001, one Scout per engine, CONFIRMED):

| Engine | Ideal warp | Fuel | Est. Range |
|---|---:|---:|---|
| Quick Jump 5 | 5 | 23 | 383 l.y. |
| Fuel Mizer | 4 | 24 | Infinite |
| Long Hump 6 | 6 | 25 | 280 l.y. |
| Daddy Long Legs 7 | 7 | 26 | 226 l.y. |
| Alpha Drive 8 | 8 | 27 | 188 l.y. |
| Trans-Galactic Drive | 9 | 28 | 169 l.y. |
| Interspace-10 | 10 | 29 | 175 l.y. |
| Enigma Pulsar | 10 | 30 | 204 l.y. |
| Trans-Star 10 | 10 | 31 | 968 l.y. |
| Settler's Delight | 6 | 32 | Infinite |
| Sub-Galactic Fuel Scoop | 5 | 33 | Infinite |
| Trans-Galactic Mizer Scoop | 10 | 34 | 430 l.y. |
| Galaxy Scoop | 10 | 35 | 729 l.y. |

Mixed fleets (CONFIRMED): 3 QJ5 Medium Freighters with 300 kT and 400 mg →
162 l.y.; 2 freighters, a Sub-Galactic Fuel Scoop scout and 150 kT with
333 mg → 239 l.y. (the scoop ship is free at warp 5 and adds nothing);
freighter and Fuel Transport with 500 mg → 1176 l.y.

### Leg distance

"Distance" in the Fleet Waypoints tile: `c = trunc(D·100 + 0.5)`, printed
as `trunc(c/100)` "." `c mod 100` with no zero padding, then "Light
Years". CONFIRMED for 28.28, 3.61, 25.50, 68.82, 97.75 and whole
distances ("50.0"). LEGACY BUG (display, CONFIRMED ES-002): a hundredths
part below 10 loses its zero, so 319.01 shows "319.1", 20.02 "20.2", 10.05
"10.5", 7.07 "7.7" and 3.0 "3.0", while 3.16 and 5.10 print as expected.
Elegy may print two decimals; if it copies the original, it should do so
behind a named switch.

## Production completion (CONFIRMED, ES-001)

For queue item `t` of a planet the client runs the year's production
(`KERNEL.md` "Production") on a copy of the planet and queue for up to 99
years and notes the first year a unit of the item is finished (`first`)
and the year the last one is (`last`). Each simulated year:

1. Mining as in `KERNEL.md` "Mining", without the random extra kT, with
   concentration depletion and the homeworld floor.
2. The year's resources as in `KERNEL.md`, minus the research share
   unless the planet sends only leftover resources to research.
3. The queue walk, as in the year, from the carried-over item (initially
   none) to the end:
   - Auto Alchemy that is not the last item does nothing itself but lets
     the next item use alchemy (`KERNEL.md` "Auto Alchemy before a
     multi-count item"). As the last item it is built like ordinary
     alchemy without a count limit. If it is item `t` itself, the answer
     is "As Needed".
   - Every other item is built as in the year. Mines and factories built
     are installed in the copy straight away, with no operating cap;
     defenses, terraforming and scanners are not installed.
   - For item `t`: the first year it builds a unit sets `first`. If it is
     an automatic item with nothing to do: "Skipped" when nothing was
     ever built, else `last` = the year before. When it finishes (count
     reaches 0, or an automatic item is done for the year) `last` = this
     year and the estimate ends.
   - An item that leaves resources unspent without finishing stops the
     year's walk, as in the year.
4. The copy keeps its leftover minerals and grows its population
   (`KERNEL.md` "Population growth").

`first` = 100 if nothing was built in 99 years; `last` = 100 if the item
did not finish. The estimate leaves out things the year does: the
Ultimate Recycling bonus, the queue prechecks and clipping, packet and
scanner checks, the cap on installations.

Display, Production tile "Completion:" and Production dialog:

| Result | Text |
|---|---|
| `first` = 100, automatic item (auto mines … auto packets) | Unknown |
| `first` = 100, any other item | Never |
| `last` = 100 | `first` - ??? years |
| `last ≠ first` | `first` - `last` years |
| skipped | Skipped |
| auto alchemy before another item | As Needed |
| otherwise | 1 year / N years |

Queue colours (CONFIRMED): green for "1 year"; blue when the first unit
is finished next year and the last later (including "1 - ??? years");
red for "Never"; grey for "As Needed" and "Skipped"; black otherwise,
including "Unknown" and anything that starts after next year.

Vectors (ES-001, CONFIRMED; queue after the generated year):

| Planet | Queue | Completion |
|---|---|---|
| Liver | Factory ×197 (69%) | 1 - 25 years |
| Fluorine | Factory ×9 (79%), Mine ×30, Defenses ×10 | 1 year; 1 - 2 years; 2 - 4 years |
| Clausewitz (no germanium) | Factory ×5 (24%), Mine ×3 | Never; Never |
| Candy Corn | Factory ×1 (9%), Auto Alchemy last | 1 year; 14 - ??? years |
| Acid (germanium-blocked) | Auto Factories ×20 | Unknown |
| Vivaldi | Mineral Alchemy ×1 (25%), Auto Alchemy, Factory ×8 (99%), Mine ×5 | 2 years; As Needed; 2 - 5 years; 5 - 6 years |
| No Exit | Mine ×6 (59%), Factory ×100 | 1 year; 1 - ??? years |
| New Kalapuya | Mine ×1 (59%), Auto Mines ×50, Auto Defenses ×50, Mine ×5 | 1 year; 1 - 8 years; 8 - 40 years; 40 - 41 years |

ES-002 (CONFIRMED): a queue of Mine ×1 (29%), Auto Defenses ×50 on a
planet already at its defense limit, Auto Factories ×20, Mine ×5 gives
1 year; Skipped (grey); 1 - 6 years; 6 - 7 years. The planet report's
Production column (MEASURED) shows "--- Queue is Empty ---" for a planet
whose only item is a skipped Auto Mines ×50 (500 mines, at its limit); its
Production dialog shows that item as "Skipped" in grey.

The planet report shows the same text's colour for the queue's first
item, and its "Resources" column shows "A / R": `R` the planet's
resources and `A` what is left for production after research.

## Research (CONFIRMED, ES-001)

Research dialog, for the current field:

- "Resources needed to complete": the next level's cost (`KERNEL.md`
  "Level cost") minus the resources already spent in the field, at least
  0. "Maxed Out" at level 26 (CONFIRMED ES-002; the dialog's
  heading then reads "Tech Level 27" and the time to completion is also
  "Maxed Out"). In a slower-tech game, where
  the stored amount is kept at half scale (`KERNEL.md` "Level cost"), the
  client doubles the stored amount before subtracting (BINARY-ONLY).
- "Annual resources from all planets": the sum of the player's planets'
  resources.
- "Total resources spent on research last year": the player's research
  spending recorded by the last generated year.
- "Resources budgeted for research": the research percentage.
- "Next year's projected research budget": for each planet with a
  non-empty queue, the production estimate's first year: resources not
  spent by the queue plus the research share; for a planet with no queue,
  all its resources.
- "Estimated time to completion": 1 year if nothing is needed; "Never"
  with a budget of 0; otherwise `ceil(needed / b)` years, where `b` is the
  projected budget, or `budget − trunc(budget/2)` with Generalized
  Research (CONFIRMED ES-002: 801 needed, projected 261 → 7 years, where
  plain division would give 4).

Vector (ES-001): weapons 4 → 5, cost 910 with 107 spent → 803 needed;
annual resources 578, last year 107, budget 10%, projected 163 →
5 years.

Vector (ES-002, `KERNEL.md` KX-005 rule): a player researching energy at
level 25 with "Same field" next reached 26; the dialog then showed
weapons 3 → 4 as the current field (595 needed, annual 38, last year 35,
15%, projected 38 → 16 years) with "Next field to research" still
`<Same field>`.

## Planets

### Population popup (CONFIRMED, ES-001)

Pressing on the population in the Status tile shows "Your population on
X is N. X will support a population of up to M of your colonists."
(`M` the maximum population, `KERNEL.md`). For the player's own planets
with habitability ≥ 0 and population below the maximum it adds "Your
population on X will grow by G to N+G next year.", with `G` the growth
`KERNEL.md` gives for the next year (with the planet's stored carry),
without applying it. Above the maximum the sentence is left out. On a
hostile planet: "X will kill off approximately a.b% of your colonists
each turn.", with `a.b` = |habitability| / 10.

Vectors: Liver 23,000 of 1,200,000 → grows by 3,400 to 26,400; New
Kalapuya (88%) 79,200 of 1,056,000 → 10,400 to 89,600; Fluorine (1%,
181,200 of 60,000) no growth sentence; Wagner (−10%) → 1.0%.

### Value and optimal value (CONFIRMED, ES-001)

"Value" is the planet's habitability for the player (`KERNEL.md`
"Habitability"), red when negative. The planet report adds the optimal
value in brackets when it is higher: habitability after the terraforming
the player's tech allows. Per axis the race is not immune to, with `t` the
best terraforming amount the player has for that axis (the larger of the
axis part and Total Terraform, which needs its LRT) and `orig` the
original value: the reachable range is `orig − t` to `orig + t` clipped
to 1 … 99; an axis below the race's centre moves up toward the centre as
far as the range allows, an axis above it moves down.

Vectors (tech: gravity ±15, temperature ±7, radiation ±3; centre 50, ±35):
34/50/50 → 88% (100%); 30/50/62 → 68% (88%); 17/17/17 → 1% (16%);
95/50/50 → −10% (53%).

### Mining rate (CONFIRMED, ES-001)

The planet report's "Mining Rate" is the year's mining (`KERNEL.md`
"Mining") without the random extra kT and without depleting anything.
Ten planets matched, including a homeworld below concentration 30 and
germanium concentration 1.

## Implementing

`experiments/es001/estimates.py` is a reference model of every rule
above, and `experiments/es001/predictions.tsv` with `results.tsv` are test
vectors (the state is in `predict.py`'s input, a host-file dump kept
privately; the vectors above give the inputs that matter).
