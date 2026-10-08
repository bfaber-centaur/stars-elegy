# Universe objects specification: minefields, packets, stargates, wormholes, Mystery Trader

Behavioral specification of the J-RC3 rules for the objects in space that
are neither planets nor fleets, and for the travel that bypasses normal
flight: minefields, mass-driver packets, stargates, wormholes and the
Mystery Trader, with where each step sits in the year. It is written for an
implementer working only from this public repository. It describes what
happens in the game, not how any file encodes it.

`PARITY.md`, section "Universe objects" (and "Scanning", object
visibility), holds the experiment records (OB-001 to OB-020). This file
restates them as rules and adds rules that so far come only from white-box
analysis of the original program (private `stars-decomp`, promoted here as
behavior only). Part statistics (dispenser ratings, driver warps, gate
limits) belong in the public components table. Parts are named here, and
numbers appear only where a rule needs them.

Rules this file relies on but does not restate: normal movement, fuel and
chasing (`KERNEL.md`), battles and battle plans (`COMBAT.md`), scanner
ranges and what a sighting reveals (`SCANNING.md`), and a planet's defense
coverage against bombs (`TAKEOVER.md`).

## Status of each rule

- **CONFIRMED**: a white-box reading agrees with original-game oracle
  observations (OB case ids given). Vectors given for it are ground truth.
- **MEASURED**: observed in the oracle, but in one case only or without a
  full model check. Implement as stated; the cases are listed.
- **BINARY-ONLY**: read from the original program, with no oracle
  observation yet. Vectors are worked from the rule. Treat these as
  predictions; they are listed under Open experiments.
- **LEGACY BUG**: behavior that looks like an accident of the original
  implementation rather than a design intent. Implement it for parity,
  isolated so it can be switched off, unless the project decides otherwise.

"Confirmed" covers the measured scope only: two players (JOAT, plus SD, PP
or IT where stated), Combat Lab universe, one year per run, objects written
into the start file.

## Conventions

- Positions are integer light-year coordinates. `d²` is `dx² + dy²`, an
  integer.
- Divisions truncate. `⌊x⌋` is used where the order of truncations matters.
- `rand(n)` is a uniform draw in `0..n−1` from the game's generator.
- **Draw order.** Space objects are kept in one list ordered by kind
  (minefields, then packets and salvage, then wormholes, then the Mystery
  Trader), then by owner, then by number. Every per-object loop, and so
  every random draw in it, runs in that order (BINARY-ONLY).
- A minefield's **size** is its mine count `N`. Its radius is `√N`: a point
  is inside when `d² ≤ N` (CONFIRMED, OB-002, OB-018-C).
- "Year index" is the game year minus 2400.

## Turn placement (BINARY-ONLY except where noted)

These steps slot into `KERNEL.md`'s turn order.

1. Orders, then waypoint tasks that act before movement.
2. Every minefield forgets which players saw it this year (see Visibility).
3. The Mystery Trader moves. Every packet already in flight moves and, if
   it arrives, hits its target.
4. Fleets move: minefield hits on the way, stargate jumps, wormhole
   transit on arrival.
5. Salvage and packets decay; detonating minefields go off; then every
   minefield decays. CONFIRMED: decay comes before this year's laying
   (OB-002-F). A stop's mine loss is taken during step 4 from the field's
   count at that moment, and decay then counts the planets inside the field
   as the stops left it (CONFIRMED, MF-4: every MF run's final count fit
   exactly; OB-010-S fits it too: no-hit settings 3000 → 2940 → 2840 after
   sweeping, hit settings −50 during movement, then decay and sweep, 2791).
6. Production: packets are launched. At the end, random events may spawn a
   Mystery Trader.
7. Packets launched this year fly half a year (and may hit). Wormholes
   jiggle or jump.
8. Fleets refuel. Battles and bombing; then Mystery Trader encounters; then
   waypoint tasks after movement, including **laying mines**.
9. Mine sweeping (CONFIRMED after laying: OB-007-D), then repair.
10. Files are written (Visibility).

CONFIRMED: packet impacts come before population growth (OB-009). A
transiting fleet lands on the exit's position from before step 7
(OB-005-C).

## Minefields

Three kinds: standard, heavy and speed bump. A player may own several
fields of each kind.

### Laying (CONFIRMED except where marked)

- A fleet lays when its current waypoint task is "lay mines" and it did not
  move this year. **A fleet whose current task is "lay mines" never moves**,
  whatever its later waypoints, so in practice it lays in place every year
  until the task ends (CONFIRMED, OB-014-D: a fleet with a second waypoint
  25 ly away stayed and laid its full amount; OB-019: it stayed three
  years, the field growing 160 → 310 → 460).
- Space Demolition (SD) only: a fleet travelling toward a waypoint whose
  task is "lay mines" also lays, at its end-of-year position, **half** the
  amount (CONFIRMED, OB-014-C: 80 from a layer rated 160). The halving uses
  the moving test, so an SD fleet that moved for any reason lays half
  (BINARY-ONLY beyond that case). Each kind's amount is halved on its own.
  Every amount is a multiple of 10 (the rule below), so the half is exact
  and needs no rounding (BINARY-ONLY).
- Amount per year, per kind: for each ship, the sum of its dispensers of
  that kind (count × rating), doubled on the Mini Mine Layer and Super Mine
  Layer hulls; summed over ships. Each Multi Contained Munition adds 40
  standard mines per ship. Vectors (CONFIRMED, OB-002):
  - Mini Mine Layer with two Mine Dispenser 40: 160; three such ships: 480.
  - Frigate with two Mine Dispenser 40: 80; with one Multi Contained
    Munition: 40.
  - Frigate with three Speed Trap 20: a 60-mine speed-bump field.
  - Two Mine Dispenser 40 and two Heavy Dispenser 50 on a Mini Mine Layer:
    a standard 160 and a heavy 200, as two fields.
  - Super Mine Layer with two Mine Dispenser 40: 160 (OB-024).
- A fleet with no dispenser of any kind lays nothing and gets a message.
- **Merging.** Among the owner's fields of the same kind that contain the
  fleet, the one whose centre is nearest takes the new mines, unless it
  already holds more than 999,999. Its count adds, and its centre moves to
  the count-weighted mean, each coordinate
  `⌊(x_field·N_field + x_fleet·laid) / (N_field + laid)⌋`, using the
  field's count after this year's decay. Otherwise a new field is created
  at the fleet. CONFIRMED (OB-002-G): a 390 field 10 ly west of the layer,
  plus 160, became 550 centred 2 ly east of the old centre. The 999,999
  cap is CONFIRMED (MF-10): a field holding 1,050,000 after decay made the
  layer start a new 160 field; one holding 999,500 merged. "Contains"
  means `d² ≤ N`. When two of the owner's fields of that kind are equally
  near, the first in object order takes the mines, which is the lower field
  number (BINARY-ONLY).
- **Duration.** The task carries a duration: "this year only" lays once and
  ends the task (CONFIRMED, OB-002-N); "indefinitely" never ends
  (CONFIRMED, OB-019); a duration of `k` years lays `k` times, one per
  year, and then ends the task (CONFIRMED for 2 and 3 years, OB-019 and
  OB-025, and still laying after three years with 4; BINARY-ONLY for 5).
  The fleet's later waypoints stay queued meanwhile (CONFIRMED, OB-019:
  both waypoints kept for three years).
- **Order (CONFIRMED, MF-12).** Fleets lay one at a time in fleet order (owner,
  then fleet number). Each fleet lays standard, then heavy, then speed-bump
  mines, and each kind is merged (rule above) before the next fleet lays.
  So two layers inside one field in the same year merge one after the
  other, and the centre depends on their order. Vector: a 390 field at
  (0, 0) after decay, with layers at (10, 0) and then (0, 10) laying 160
  each, ends at (1, 2) with 710. In the other order it ends at (2, 1). One
  simultaneous weighted mean would give (2, 2). MF-12 measured both orders:
  each ended at 710 with the centre the sequential merge gives.
- **Limits.** A player owns at most 512 minefields, all kinds together,
  numbered 0..511 (MEASURED, MF-11: with 511 fields a layer in open space
  made field 511; with 512 it made none, the owner got a message and the
  mines were lost; a layer inside an existing field merged normally). The
  last number, 511, is given only when no other space object sorts after
  that player's minefields (objects sort by kind, minefields first, then
  by owner and number), so a higher-numbered player's minefield or any
  packet, salvage, wormhole or Mystery Trader holds the player to 511
  (MEASURED, MF-13: a player-1 field elsewhere, or a salvage object, gave
  no field and the message; player 1's 511 fields with a player-0 field
  sorting before them made field 511). LEGACY BUG. **Chosen rule for
  Elegy:** a plain limit of 512; the 511 case is reproduced only behind a
  switch. The universe holds at most 4050
  space objects of all kinds (BINARY-ONLY). A lay that needs a new field
  when there is no room creates nothing: the owner gets a message and
  those mines are lost. A lay that merges needs no room. A new field takes
  the lowest number not in use among the owner's minefields of all three
  kinds (BINARY-ONLY; MF-11 and MF-13 measured only the last number).

### Decay (CONFIRMED, OB-002, OB-014-A, OB-015, OB-016, MF-4)

Each year, every field loses `p` percent, where `n` is the number of
planets inside it (any owner, including none), counted after this year's
stops have shrunk it (MF-4: a field that lost two of its five planets to
the stops decayed 14%, not 22%):

```
p = min(50, 4·n + 2)        owner not SD
p = min(50, n + 2)          owner SD
p = p + 25                  if the field is detonating this year
loss = max(p, ⌊N·p/100⌋)
loss = max(loss, 10)        standard and heavy only
```

The field disappears when `loss ≥ N`. Vectors: no planets 1000 → 980,
100 → 90, speed bump 100 → 98; two planets 1000 → 900; SD with two
planets 1000 → 960; 22 planets 40000 → 20000, SD 40000 → 30400;
detonating with no planets 1000 → 730.

### Hits on moving fleets (CONFIRMED, OB-010, OB-024, MF-1..MF-9; marked parts BINARY-ONLY)

Applies to a fleet moving at warp 1–10 (not through a stargate) across a
field whose owner is not the fleet owner and does not treat the fleet
owner as a friend. Stationary fleets are never hit. The field owner's
relation decides, not the victim's (CONFIRMED, MF-5: with the owner
treating the victim as a friend and the victim treating the owner as an
enemy, 24 fleets crossed with no stop; reversed, they were stopped at the
usual rate). The owner's own fleets are never stopped (MF-6).

- **Effective warp** `e` comes from the distance `D` actually travelled
  in the movement step being checked, not the ordered warp: the smallest of 3..10 with
  `e² ≥ D − 1`. CONFIRMED: five warp-9 fleets moving 30 ly inside a heavy
  field (safe 6, `e` = 6) were never hit in 30 fleet-years (OB-010 H0–H4);
  warp-9 fleets whose waypoint was 17 ly ahead in a standard field or 36 ly
  ahead in a heavy field were never stopped, and a 26-ly leg in a standard
  field (`e` = 5) stopped 1 fleet of 12 (MF-3).
- **Chasers (CONFIRMED, MF-2; one LEGACY BUG).** A chaser moving in
  rounds (`KERNEL.md`, "Chasing another fleet") is checked once per round,
  with `D` that round's step. A chaser whose target has already finished
  moving takes its whole remaining distance in one round and is checked
  like any other fleet. A chaser whose target has not finished moves in
  fifths: at warp 9 its steps are 17 ly, so `e` = 4 and no field can hit
  it. Which case applies depends on fleet order (owner, then number):
  - Two fleets chasing each other: 24 fleet-years in a heavy field with no
    stop, in 17-ly steps (MF-02b).
  - A chain C ← B ← A (B follows C, A follows B), numbered C < B < A: B and
    A each moved their whole remainder in one step after their target
    finished, and A was stopped in 2 of 6 chains.
  - The same chain numbered A < B < C: A moved first and reached B's start
    in its first 17-ly step. **B then never moved at all**: a chaser that
    lands on a target that has not moved yet ends that target's movement
    for the year (MEASURED, MF-02, 6 of 6; LEGACY BUG). It is a movement
    rule rather than a minefield rule: `KERNEL.md` "Chain freeze" gives the
    mechanism (one "finished moving" mark shared by "has moved" and "a
    chaser landed on it") and Elegy's switch.
- **Cloak** plays no part in hits (CONFIRMED, MF-1: cloaked fleets were
  stopped at 29.1 per mille, uncloaked ones at 36.1) or in detonation,
  laying or sweeping (BINARY-ONLY). It matters for minefields only through what a Space
  Demolition field sees (`SCANNING.md`).
- **Safe warp** by kind: standard 4, heavy 6, speed bump 5; +1 if the
  fleet owner is Super Stealth, +2 if Space Demolition. No check when `e`
  is at or below the safe warp, or when the fleet was already at its
  waypoint.
- The path from the fleet's position toward its next waypoint is cut by
  each field into an entry and exit distance in whole ly. Entry is not
  below 0, exit is not beyond this year's travel, and a tangent path does
  not count. The exact arithmetic, including a LEGACY BUG on due-north and
  due-south legs, is under "Arithmetic details" below. Overlapping
  stretches of one kind merge. Stretches are visited in order of entry
  across all kinds. For each whole ly of a stretch, one draw:
  `rand(1000) < (e − safe)·h` is a hit, with `h` = 3 (standard), 10
  (heavy), 35 (speed bump) per mille. CONFIRMED as rates (MF-1): heavy at
  warp 9 gave 32.3 per mille over 2137 draws (predicted 30), standard 15.9
  over 2709 (predicted 15). A stop on the first draw leaves the fleet where
  it entered the field.
- **On a hit** the fleet stops there (distance from its start = entry + the
  ly index); no further checks this year; no ram-scoop fuel this year; the
  fuel for the full planned leg is already spent. CONFIRMED: stop points
  55 and 64 ly into a field (OB-010-S).
- **Damage** (CONFIRMED, MF-9, for every engine, shield and fleet-size
  case; standard and heavy; speed bumps only stop, OB-024: the stopped
  fleet was undamaged): per ship per
  engine, standard 100 and heavy 500, or 125 and 600 when any design in
  the fleet has an engine that burns no fuel at warp 4 (the Fuel Mizer
  as well as the ram scoops, MF-9). Fleets of fewer
  than 5 ships get at least 500 (standard) or 2000 (heavy) in total, 600
  and 2500 with such an engine, the shortfall added to the first design.
  Per design: `D = (ships·per + shortfall)·engines`; shields absorb at most
  `D/2`; the result is added to existing damage and spread evenly. A design
  whose average exceeds its armor is destroyed. CONFIRMED: five Laser
  Destroyers each took half their armor (OB-010-S, OB-002-M).
- **Cargo when ships are destroyed (MEASURED, MF-14; LEGACY BUG
  candidate).** The destroyed ships take their share of cargo and fuel,
  shared as a ship move between fleets (`ORDERS.md` "Split": by capacity,
  rounded down), and that share is lost. Then every mineral still in the
  fleet, the survivors' included, is dropped as salvage at the stop point;
  colonists and fuel stay aboard. MF-14: four 70-kT freighters and a
  250-kT Privateer carrying 100/100/100 kT and 50 kT of colonists lost
  53/53/52/26 with the freighters and dropped the other 47/47/48 as
  salvage, leaving the Privateer with 24 kT of colonists. When the whole
  fleet is destroyed, all its minerals become salvage (BINARY-ONLY; MF-14
  saw only partial losses). No salvage is made
  at a planet's exact position; the minerals then stay aboard
  (BINARY-ONLY). A fleet with no minerals left drops `rand(10)` kT of each
  mineral as salvage (MEASURED, OB-024: 0–9 kT of each in five fleets;
  LEGACY BUG candidate). **Implementing:** while this stays a LEGACY BUG
  candidate, Elegy reproduces the measured survivors' salvage behind a
  named legacy switch.
- **Mines lost to the hit:** one field of the kind that stopped the fleet
  pays. It loses `max(10, ⌊N/20⌋)`, or `max(50, ⌊N/100⌋)` when
  `⌊N/20⌋ > 50`. CONFIRMED for 400 (−20), 3000 (−50) and 6000 (−60) before
  decay, and for a 400 speed bump (−20) (OB-010-S, OB-024).
- **Which field pays (CONFIRMED, MF-4).** Among the fields of that kind whose
  owner is not the victim and does not treat the victim as a friend, the
  one with the smallest `d² − N` at the stop point, where `d` is the
  distance from the field's centre. On a tie, the first in object order
  pays. This is not the field with the nearest edge or the nearest centre.
  Vector: a stop point 90 ly from the centre of a 10,000 field (value
  8,100 − 10,000 = −1,900) and at the centre of a 100 field (value −100):
  the 10,000 field pays. MF-4: a 400 field wholly inside a 10,000 field
  only decayed while the big field paid all 11 stops, 10 of them inside
  the small one.
- The victim learns the paying field. If its owner is SD, that owner
  learns the victim's damaged designs, or all of the victim's designs
  present if none was damaged. This applies to hits and to detonations
  (CONFIRMED for detonations, MF-7: an SD owner got the full designs of
  both enemy designs its detonating field damaged).

### Detonation (CONFIRMED, OB-002-M, MF-7, MF-8)

A field set to detonate goes off each year before decay: every fleet inside it, of any owner including the
field's owner, takes hit damage as above, except the owner's own Mini Mine
Layer and Super Mine Layer hulls. No stop, no salvage, at most one
detonation per fleet per year. A destroyed ship's share of cargo and fuel
is lost as for a hit, and the survivors keep the rest (BINARY-ONLY). The field then decays with the extra 25%.
OB-002-M: the owner's five Laser Destroyers took half their armor, the
enemy's five Medium Freighters 100 each, the layer nothing; the field went
1000 → 730.

- **Kinds (CONFIRMED, MF-7, MF-8).** A detonating heavy field deals heavy
  hit damage the same way: an enemy Tank, the owner's own Tank and a
  friend's Tank each took 2000, the owner's Mini Mine Layer nothing, and
  nobody moved. A detonating speed-bump field damages and stops nobody.
  Every kind decays with the extra 25% (1000 → 730, with no minimum of 10
  for a speed bump). Damage adds to existing damage: an enemy fleet of 5
  Tanks at 250/500 went to 265/500, and the owner's Laser Destroyer at
  250/500 was destroyed.
- **The detonate setting (BINARY-ONLY; LEGACY BUG).** The original client
  offers the setting only to a Space Demolition player, and only on that
  player's own standard fields. The host checks only that the order names
  a minefield. It does not check the field's owner, its kind or the
  submitter's race. So a hand-built order can turn detonation on or off
  for any player's field of any kind. This is the same kind of gap as the
  orders that are not re-checked under `ORDERS.md` "Ownership". **Chosen
  rule for an independent implementation:** accept the setting only from
  the field's owner, only when that owner is SD, and only for a standard
  field. That is exactly what an unmodified client can produce. The rule
  follows the client's offer, not what can detonate: every kind detonates
  once set (MF-7, MF-8, above).

### Arithmetic details (BINARY-ONLY except where marked)

Read from the original program for the Elegy implementation. Where these
differ from an exact-geometry reading, the original is stated.

**Path cut.** For each field that can hit the fleet: `(sx, sy)` is the
fleet's position, `(dx, dy)` the vector to waypoint 1, `(cx, cy)` the
field's centre, `N` its count, and `L` the whole ly the fleet travels in
this movement step. All divisions truncate toward zero.

1. The foot of the perpendicular from the centre onto the leg, in whole
   ly: `fx = (cx·dx² + sx·dy² + (cy − sy)·dx·dy) / (dx² + dy²)`, then
   `fy = sy + (fx − sx)·dy / dx`. When `dx = 0`, `fy = sy` (LEGACY BUG,
   below). When `|dx·dy|`, `dx²` or `dy²` is 500,001 or more, `fx` is
   computed in floating point and then truncated.
2. `p² = (fx − cx)² + (fy − cy)²`. There is no cut when `p² ≥ N`.
3. `h` = the distance from the start to the foot, truncated, and negative
   when the foot lies behind the start. "Behind" is compared along x, or
   along y on a leg with `dx = 0`. `w = trunc(√(N − p²))`.
4. Entry `= max(0, h − w)`, exit `= min(L, h + w)`. The field counts only
   when exit > 0 and entry < L.

On an east-west leg the foot is exact, so entry is the exact entry rounded
up and exit the exact exit rounded down. The MF corpora are east legs
(MF-1, MF-3: CONFIRMED as rates). On other legs the truncated foot can
move entry and exit by more than 1 ly. That is BINARY-ONLY, apart from
due north and south.

**Due-north and due-south legs (LEGACY BUG, MEASURED, MF-15).** With
`dx = 0`, the foot is the fleet's start. So a fleet that starts outside a
field and flies straight north or south into it is never checked. A fleet
that starts inside is checked from the start for `trunc(√(N − d²))` ly,
where `d` is its distance from the centre, in whichever direction it
flies. MF-15, heavy field of 10,000: none of 8 Tanks flying north into
the field from 3 ly outside was stopped. 8 Tanks starting 90 ly from the
centre and flying south out of the field (outside after 10–13 ly) were
stopped at 2, 9, 10, 18, 19 and 31 ly, inside the 43 ly the rule gives.
**Implementing:** Elegy reproduces this behind a named legacy switch, like
the other deterministic legacy bugs. With the switch off, the exact foot
is Elegy's choice, not the original's.

**Stretches.** Per kind, up to 8 stretches are kept, sorted by entry, and
a ninth disjoint one is dropped. A new stretch merges with an existing one
when they overlap or touch, and also when it ends exactly 1 ly before the
existing one starts. Stretches are visited by smallest entry across the
three kinds; on equal entry, standard comes first, then heavy, then speed
bump. A stretch of a kind whose safe warp is not below the effective warp
is passed with no draws. A stretch from entry `a` to exit `b` makes the
draws `k = 0 .. b − a − 1`, and a hit at draw `k` stops the fleet `a + k`
ly from its start (stop offsets MEASURED: OB-010-S, MF-15).

**Stop point.** Each coordinate is the start plus that coordinate's
offset to waypoint 1, times `a + k`, divided by the leg length to
waypoint 1 rounded to the nearest ly. The product is rounded to the
nearest ly. On east legs this is exact (MF corpora). The salvage and the
paying field use this point.

**Damage on top of existing damage.** A design's damage is stored as the
percentage of its ships damaged and the damage per damaged ship, in units
of 1/500 of its armor. With `n` ships, armor `A`, and the hit damage `D`
from the hit rules:
- existing damage `X = ⌊⌊pct·n/100⌋ · A · units / 500⌋` (the count of
  damaged ships rounds down);
- `total = X + D − min(⌊D/2⌋, shield · n)`, where `shield` is the design's
  shield value per ship;
- `avg = ⌊total / n⌋`.

The design is destroyed when `avg > A`. Otherwise every ship counts as
damaged (100%), with `⌊avg·500/A⌋` units and at least 1 unit. CONFIRMED
for prior damage on all ships: MF-8, 5 Tanks at 250/500 went to 265/500.

**Several detonating fields.** Fields detonate one at a time in object
order, each just before its own decay, and "inside" uses that field's
count before its decay. The first detonating field whose area contains a
fleet marks it, and later detonating fields skip it that year. This holds
even when the first field did it no damage: for example, a fleet of the
first field owner's own minelayer hulls, or a speed-bump field. So an
enemy's later detonation misses that fleet.

### Sweeping (CONFIRMED, OB-001, OB-007, OB-008, OB-010-S)

After laying, every fleet and then every starbase sweeps.

- **Sweep rating** of a ship design: Σ over its beam weapons of
  `count × damage × range²`, with range 4 for gatling-type beams (Mini
  Gun, Gatling Gun, Gatling Neutrino Cannon, Big Mutha Cannon) and range+1
  on a starbase hull. Sappers, torpedoes, missiles and bombs sweep nothing.
  A fleet's rating is the sum over its ships; a starbase's is its design's.
- **Who.** A fleet sweeps every other player's field that contains it and
  whose owner its battle plan would attack: "nobody" sweeps nothing,
  "enemies" only enemies, "neutrals and enemies" neutrals and enemies,
  "everyone" and "player N only" ignore relations, so they sweep a
  friend's field too (OB-008, one case each). A starbase sweeps every
  field containing its planet whose owner is not the planet owner's
  friend, whatever the battle plan.
- **How much.** `a = S` (`⌊S/3⌋` for speed bumps), at least 2. The field
  only shrinks until the sweeper is just outside it: if `N − a < d² − 1`
  then `a = N − d² + 1`,
  with `d` the sweeper's distance from the centre (a sweeper at the exact
  centre can clear it). The field loses `a`, and disappears at 0. The
  sweeper's owner learns the field.
- Every sweeper sweeps each field it is inside with its full rating; two
  fleets do twice what one does.
- Vectors: Destroyer with 2 Lasers, field 1000 with no planets: 980 after
  decay, 960 after sweeping. Mini Gun Destroyer: 980 → 772. Gatling
  Destroyer in a 2000 field: 1960 → 968. A fleet rated 992 sitting 20 ly
  from a 1000 field's centre leaves 399. Laser Fort (2 Lasers) starbase:
  sweeps 80.

## Mass-driver packets

### Launch (CONFIRMED, OB-028, OB-029; marked parts BINARY-ONLY)

- Needs a mass driver on the planet's starbase and a packet destination;
  otherwise the item is not built and the player gets a message (OB-028-F:
  no packet, minerals unchanged, two messages).
- Driver warp `Dw`: the best driver's rating; `t` = 1 when two different
  orbital slots each hold that best driver (only starbase hulls with two
  orbital slots can), else 0 (OB-028-C: two Mass Driver 7s give warp 8;
  OB-028-D: Mass Driver 7 with Mass Driver 5 gives 7).
- Each item launches 100 kT of one mineral (Packet Physics: 70), or for a
  mixed item 40 kT of each (PP: 25), times the item count, at most 32,760
  per mineral (the cap BINARY-ONLY). Measured spend from the surface: 110 kT
  per 100 kT item (Interstellar Traveler 120, PP 70) and 44 kT of each per
  mixed item (PP 25) (MEASURED, OB-028, OB-029). An Interstellar Traveler
  mixed item launches 40 kT of each and spends 48 kT of each (BINARY-ONLY:
  the item's cost; not measured).
- **The settings (BINARY-ONLY).** The planet's packet destination and
  speed are stored as the owner sends them; the host only checks that the
  planet is the sender's (`LIMITS.md`). The speed is stored as given in its
  field (warps 4..19) and resolved at launch by the rule below. A
  destination is a planet number, or none; nothing checks that the planet
  exists, and launching toward a number past the last planet reads past
  the planet table (no measured behaviour; Elegy needs a chosen rule, such
  as treating it as no destination).
- Packet warp `W`: the planet's packet-speed setting; if below 5 or above
  `Dw + 3`, it becomes `Dw + t` (OB-028-B: 11 with a Mass Driver 7 → 7;
  unset → `Dw + t`, OB-028-C, D).
- Decay class `k = max(0, W − Dw − t)`, +1 for an Interstellar Traveler
  launcher, at most 3 (OB-028-A: warp 9 from a Mass Driver 7 is class 2;
  IT: warp 7 class 1, warp 10 class 3, OB-028-H, I).
- A packet launched from the same planet in the same year with the same
  warp, destination and class merges into the first while it is under
  16,300 kT (OB-028-B, E: two items, one 200 kT packet; the 16,300 kT limit
  BINARY-ONLY).
- **Merge details (BINARY-ONLY).** The new minerals join any packet of the
  same owner lying exactly at the launching planet with the same warp,
  destination and class; the minerals it carries do not matter, so a mixed
  item merges into an ironium packet and the packet then carries all three.
  The limit is tested on the existing packet before the new minerals are
  added: it takes them while the sum over its three minerals of
  `⌈m/10⌉` is below 1,630 (so 16,290 kT of one mineral still takes more,
  16,291 does not). A merged mineral that would pass 32,767 kT becomes
  32,760. Otherwise a new packet is made.
- **Numbering (BINARY-ONLY).** A new packet takes its owner's lowest
  unused packet number, from 0. Packets use the same numbering rule as
  minefields ("Limits" above, MEASURED there by MF-11 and MF-13): numbers
  0..510, and 511 only when no other space object sorts after the owner's
  packets; the universe holds at most 4050 objects. Packets and salvage
  are one kind of object, so a player's packets and its own salvage share
  one pool of numbers: its salvage does not sort after its packets, it
  uses up numbers in the same pool. What sorts after them is any packet
  or salvage of a higher-numbered player, every wormhole and the Mystery
  Trader. Minefields of any owner and lower-numbered players' packets and
  salvage sort before and never withhold 511. With no number or no
  room, the item still counts as built (its minerals are spent and the
  launch message is sent) but no packet appears.

### Flight and decay (CONFIRMED, OB-003, OB-028; marked parts BINARY-ONLY)

- On its launch year a packet moves `⌊W²/2⌋` ly (OB-028 A–I); after that
  `W²` ly per year (OB-003 J, K), straight toward the
  destination planet. It arrives when the truncated distance is at most
  the year's move; otherwise each coordinate moves by the rounded share.
- Decay per year by class: 0 none; 1, 2, 3: 10, 25, 50% of each mineral
  (CONFIRMED for classes 2 and 3, OB-003 J, K). A PP owner's packets decay
  at half those rates, 5, 12 and 25% (CONFIRMED, OB-023: 1000 kT → 950,
  880, 750). Each non-empty mineral loses at least 10 kT (PP: 5)
  (CONFIRMED, OB-023: 50 kT of a mineral → 40, PP → 45). On the launch
  year a packet that does not arrive decays half a year (OB-028: class 2
  100 kT → 88, class 3 → 75, IT class 1 → 90). A packet that arrives in
  its launch year decays for half of the share of the year it flew
  (OB-028-G: 500 kT class 3 arriving after 70% of a year → 413, +45 on an
  unowned planet). On a later arrival it decays for the share of the
  year it flew, but the minimum still applies (CONFIRMED, OB-003-C: a
  class-1 100 kT packet arriving with 5% of a year left lost 10).
- **Rounding (BINARY-ONLY; fits OB-003, OB-023, OB-028).** All in
  integers. The year's share is a whole percent `p`: 100 for a full year,
  50 for a launch year without arrival, and on arrival
  `p = round(trunc(d)·100/m)` (halves rounded up), with `d` the distance
  to the destination at the start of the move and `m` the year's move,
  clamped to 0..100 and then halved (rounding down) in the launch year.
  The rate `r` is 10, 25 or 50 (PP: 5, 12, 25). Each non-empty mineral
  `m` loses `min(m, max(minimum, ⌊m·r·p/10000⌋))` with minimum 10 (PP 5).
  A packet with nothing left is removed. So a share is not a real-valued
  fraction: OB-028-G's 70% launch-year arrival is `p = 35`, and 500 kT
  at class 3 loses `⌊500·50·35/10000⌋ = 87`.

### Impact (CONFIRMED, OB-003, OB-009; marked parts BINARY-ONLY)

Target planet with catcher warp `C` (the planet's own `Dw + t`; 0 if
unowned or no starbase). Let `w² = W²` and `c² = C²`. When the target's
owner is Interstellar Traveler, `c² = ⌊C²/2⌋`; `w²` is never halved
(CONFIRMED, OB-022-D, E). An IT catcher works at half its speed squared in
every step below, damage included.

1. Caught share, per mille: `q = 1000` if `w² ≤ c²`; `⌊c²·1000/w²⌋` if
   `C > 0`; else 0.
2. **Minerals added to the surface**, per mineral after arrival decay:
   `⌊m·(q + ⌊(1000 − q)/9⌋)/1000⌋`. The uncaught share arrives as one ninth;
   the rest is lost. Vectors: 1000 kT uncaught: +111; 300/200/100: +33,
   +22, +11; Mass Driver 7 catching warp 10 (q = 490): 1000 kT gives +546;
   a packet no faster than the catcher: +1000 and no damage.
3. Fully caught: done.
4. PP launcher: the packet terraforms (below), on owned and unowned
   planets (CONFIRMED, OB-029-T1..T3), and the catcher's starbase design
   becomes known to the PP player (BINARY-ONLY: OB-029-D2 found no foreign
   design in the PP player's file, but no control shows that such a design
   would be written there).
5. Unowned planet: done.
6. **Damage**, in units of 100 colonists:
   `dmg0 = ⌊(w² − c²)·M/160⌋`, `M` = total cargo after arrival decay;
   `dmg = ⌊s·dmg0⌋`, with `s` the planet's share that gets through its
   defenses (the defense coverage against normal bombs, `TAKEOVER.md`).
   Alternate Reality planets take no damage (CONFIRMED, OB-030-A: 1000 kT
   at warp 10, population equal to the control, surface +111).
7. With population `P` (units of 100): `kill = max(⌊P·dmg/1000⌋, dmg)`.
   `kill ≥ P` leaves the planet uninhabited. Otherwise population drops by
   `kill` and defenses drop by `Dk = ⌊def·dmg/1000⌋`; when that is 0 and
   the planet has defenses, `Dk = 1` if `rand(20) < dmg`; then
   `Dk = min(def, max(Dk, ⌊dmg/20⌋))`.
8. The packet's owner is not checked: an owner's own packet damages its own
   planet the same way (CONFIRMED, OB-009-E). Packets do not interact with
   fleets, minefields or other packets.

Vectors (OB-009, growth controlled): 1000 kT at warp 10 into 1000 units, no
driver, no defenses: 625 killed. Against a Mass Driver 7 catcher: 318.
IT target (OB-022): no starbase, 625 killed as for any owner; a Mass
Driver 7 catcher gives `c² = 24`, caught 240‰, surface +324, 475 killed.
With 50 SDI defenses: 418 killed, defenses 50 → 30. Damage at or above the
population: uninhabited.

**PP terraforming (CONFIRMED in part, OB-029; the draws BINARY-ONLY).**
For each mineral, the uncaught share `u = ⌊m·(1000 − q)/1000⌋` works on
one axis: ironium gravity, boranium temperature, germanium radiation
(CONFIRMED, OB-029-T1..T3: 1000 kT of one mineral moved only its axis,
by 3, 6 and 2, toward the PP player's ideal; the original values did not
change). The rest of this paragraph is BINARY-ONLY. The axes are handled
one after another, ironium's first, then boranium's, then germanium's,
and each axis finishes before the next axis's draws: all of its draws, then
its permanent move, then its current-value move (the moves draw nothing).

- **Draws.** For each 100 kT chunk of the axis's mineral (the last may be
  partial) one draw `rand(200) < min(chunk, 100)` is a success; each
  success draws again and is also permanent with `rand(10) == 0`.
- **Permanent move.** The permanent count `k` moves the planet's original
  value toward the PP player's ideal by at most `k`, never past the ideal;
  an original value already at the ideal stays. For an axis the PP player
  is immune to, the extremes are 1 and 99: an original value below 50 moves
  `k` toward 1, one of 50 or more moves `k` toward 99 (so 50 counts as
  nearer to 99), stopping at the extreme.
- **Current move, ordinary axis.** With `n` successes (none: nothing
  happens), the PP player's terraforming reach on the axis (its
  terraforming tech, as for its own terraforming) is measured around the
  original value as it stands after the permanent move, and only in the
  improving direction: the limit is `original ± reach`, kept within 1..99
  and never past the PP player's ideal, and it exists only when it lies
  beyond the current value toward the ideal. The current value then moves
  toward that limit by at most `n`, stopping at it; with no limit on this
  axis it does not move. This test is effectively per axis.
- **Current move, immune axis.** The move is `⌊n/2⌋` toward the extreme
  chosen as above (from the original value after the permanent move: below
  50 toward 1, else toward 99), stopping at the extreme. It is gated by the
  whole planet: it happens only if, at that moment, some axis the PP player
  is not immune to still has a limit as described above (an immune axis
  never has one itself). With no such axis the immune axis does not move,
  however many successes it drew.

## Salvage (BINARY-ONLY except where marked)

Salvage is a packet-kind object with no warp and no destination. An
object of that kind is salvage when its packet-warp field is 0 (the field
stores warp − 4, so a record written with "warp 4" is salvage); the
destination field is ignored (BINARY-ONLY). How
much each event leaves, and where, is in `COMBAT.md` "Salvage" (battles
and cargo dumped by a battle plan), "Hits on moving fleets" above (mine
hits) and `TAKEOVER.md` (scrapping in deep space). None is ever placed
exactly on a planet's position, and one object holds at most 30,000 kT,
the overflow going into a new object at the same spot (CONFIRMED,
CB-040).

- **Owner.** A new salvage object belongs to the player whose ships or
  cargo it came from: the owner of the destroyed ships (or of the fleet
  dumping cargo) in a battle, the owner of the fleet hit by mines, the
  owner of the scrapped fleet. Minerals added to an existing object do not
  change its owner, whoever they came from; an overflow object belongs to
  the owner of the addition that overflowed. The owner decides only the
  object's place in the object list and its number (it shares the owner's
  packet numbers, "Launch" above) and which player a viewer learns of
  (below); it gives no rights over the salvage.
- **Joining existing salvage.** A battle starts a fresh salvage object:
  every loss and dump in that battle goes into it, whoever's ships they
  were, and it never joins salvage already lying at that spot, from an
  earlier year or not (CONFIRMED in part: one object per battle location,
  CB-001 B1). A mine hit's minerals join the first salvage object (in
  object order) lying exactly at the stop point, of any owner and age, or
  make a new one. Scrapping in deep space always makes a new object. In
  every case where minerals are added, the object's whole contents are
  taken out and added back with the new ones under the 30,000 kT limit.
- **Decay.** Once a year, with packets (step 5 of "Turn placement"), each
  non-empty mineral loses `⌊m/10⌋`, at least 10 kT, and not below 0. An
  object with nothing left is removed. An object skips the first decay
  after it is made or added to: making or adding marks it, and the next
  decay only clears the mark. So salvage from a mine hit or a deep-space
  scrap keeps its full amount through the year it was made (fits T-34:
  60/20/70 at the end of the scrap year), battle salvage through the next
  year's decay, and a mine hit that adds to old salvage spares it one
  decay. An overflow object made by the 30,000 kT limit is not marked
  and decays the next time.
- **Loading.** A fleet at the salvage's position may load its minerals
  with a load task or a manual load, whoever owns the salvage and the
  fleet; colonists and fuel cannot be loaded from it. The amount is the
  usual load amount (`TAKEOVER.md` "Unload and load amounts"), capped by
  what the salvage holds. Manual loads by several players during order
  replay are taken in turn, and a player who finds it emptied first gets
  the "another player emptied it" messages (`MESSAGES.md` 0x0db, 0x0dc).
  An emptied object stays until the next decay removes it. Unloading
  into salvage is accepted but only up to the object's stored size (kept
  in 10 kT steps and refreshed only when it is made, added to or
  decays): a few kT of rounding room plus whatever has been loaded out
  since.
- **Visibility.** Salvage is seen as a packet is (`SCANNING.md`, "Mineral
  packets"): within a viewer's normal scanning range, with no exception
  for its owner's own salvage, and a Packet Physics player sees every
  salvage object in the universe. Seeing it makes its owner a known
  player, as for packets. Salvage does not scan.

## Stargates (CONFIRMED, OB-021, OB-022, GT-001, GT-002, except where marked)

A fleet uses gates when its next waypoint's warp is the gate setting
(waypoint warp 11). Routing that picks gates on its own uses the same
rules: a new ship's route (`PRODUCTION-LAUNCH.md`, "Routing") and the
route task (`ORDERS.md`, "Waypoint upkeep") choose warp 11 only when both ends are gated and the jump is safe.

Gate types (stats in `COMPONENTS.md`, `safe_mass`/`safe_range` of the
seven orbital stargates; "any" is `null` there):

| Gate | Mass limit | Range | Refused beyond (`5×`) |
|---|---|---|---|
| Stargate 100/250 | 100 kT | 250 ly | 500 kT, 1250 ly |
| Stargate any/300 | any | 300 ly | 1500 ly |
| Stargate 150/600 | 150 kT | 600 ly | 750 kT, 3000 ly |
| Stargate 300/500 | 300 kT | 500 ly | 1500 kT, 2500 ly |
| Stargate 100/any | 100 kT | any | 500 kT |
| Stargate any/800 | any | 800 ly | 4000 ly |
| Stargate any/any | any | any | never |

"Any" range counts as 8000 ly in the danger formula, so it never refuses
and never adds danger on a real map. Between 1× and 5× a limit the jump
goes ahead with losses (Danger, below); exactly 5× means `pct = 100`, so
everything of that design is lost (CONFIRMED, GT-001: 1250 ly and 500 kT
through 100/250 lost the fleet; 1251 ly was refused). The damage of each
gate type matched in GT-001 N1–N6 (one stream).

- **What makes a gate** (CONFIRMED, GT-004): a planet has a gate when it
  has a starbase whose design holds a stargate in any orbital slot. That
  design is the planet's own starbase design, so redefining the design
  changes every planet that uses it; nothing else on the planet records
  the gate. A Space Station with the gate in either of its two orbital
  slots worked, and a player whose tech is below the gate's requirement
  could still use it. A gate jump is asked for with waypoint warp 11.
- **Source:** the gate on the starbase of the planet the fleet is at, owned
  by the fleet owner or a friend. "Friend" is the gate owner's relation
  toward the fleet owner; the fleet owner's own view of the gate owner does
  not matter, so a one-sided friendship lets only the befriended player
  through (CONFIRMED, GT-001 D/E: a player listed as an enemy used the
  gates of a player who listed it as a friend, and not the other way
  round). Without one, every ship in the fleet must carry a Jump Gate, and
  the destination gate's limits then stand for both ends (CONFIRMED,
  GT-001 A). A fleet at a gated planet uses that planet's gate even when
  it carries Jump Gates, unloading its cargo there (GT-001 B).
- **Destination:** a planet at the waypoint with a gate owned by the fleet
  owner or a friend (same direction as the source). A Jump Gate does not
  replace a missing destination gate (CONFIRMED, GT-001 C). A waypoint in
  deep space, or on anything not at a planet's exact position, is refused
  (CONFIRMED for deep space, GT-001 M).
- **Refusal order** (CONFIRMED, GT-001 F3, GT-003 R1–R6; the destination
  planet check BINARY-ONLY in its place): source gate (or Jump Gate on every
  ship), then destination planet, destination gate, destination owner,
  colonists from a planet not the fleet owner's, the cargo unload, then
  range and mass design by design. Only the first failure is reported to
  the fleet owner. A refused fleet stays where it is with its waypoints.
  GT-003, each fleet with two reasons to be refused, got one message each:
  source gate before destination gate (R1, and before deep space, R6);
  destination owner before range (R2) and before mass (R3); foreign
  colonists before mass, with the minerals kept aboard (R4); range before
  mass, after the unload (R5: the hold emptied onto the source planet,
  with an unload message).
- **Cargo:** unless the fleet owner is Interstellar Traveler or uses a
  Jump Gate, all ironium, boranium, germanium and colonists are unloaded
  onto the source planet before the jump is checked, so a jump refused for
  range or mass still empties the hold (LEGACY BUG, MEASURED in OB-021: a
  refused freighter's 100 kT still unloaded; IT kept its cargo in OB-022).
  Carrying colonists from a planet the fleet owner does not own (a
  friend's gate) blocks the jump before anything is unloaded; minerals
  alone are unloaded onto the friend's planet, and both players are told
  (CONFIRMED, GT-001 F, F2).
- **Limits:** range `R` from the source gate only ("any" counts as 8000);
  mass limits `Ms`, `Md` from both gates, compared with each ship's design
  mass. Distance `d` = truncated distance. Refused, with no losses: `d >
  5R`, or a ship heavier than 5× either mass limit.
- **Danger:** starting from `f = 10000`; if `d > R`, `f = ⌊(5R − d)·2500/R⌋`;
  for each mass limit `M` with `0 < M < mass`,
  `f = ⌊⌊(5M − mass)·2500/M⌋·f/10000⌋`; any factor ≤ 0 means `pct = 100`.
  Else `pct = ⌊(10000 − f)/100⌋`. Per design.
- **Losses** for `0 < pct < 100` (IT: no ships destroyed): each ship is
  destroyed with `rand(100) < ⌊pct/3⌋`; survivors take `max(1,
  ⌊pct·armor/100⌋)` damage each, averaged with old damage (destroyed
  damaged ships still count in that average: LEGACY BUG candidate). When
  one of three identical ships was lost, the fleet's fuel went 100 → 67
  (MEASURED, OB-021). A design with `pct = 100` is lost entirely; if
  every design is lost, the fleet is gone.
- **Order of designs and draws (BINARY-ONLY).** Every design's `pct` is
  worked out first, in design-number order (the owner's design slots),
  before any draw; a refusal stops there and nothing is drawn. Then the
  designs are taken in design-number order again, whatever order their
  ships joined the fleet in. A design with `pct = 0` is skipped: no draws
  and no damage. A design with `pct = 100` is removed with no draws. For
  `0 < pct < 100` with `k = ⌊pct/3⌋ > 0` (never for IT), each ship of the
  design in turn draws `rand(100)`, and `rand(100) < k` destroys it. When a
  ship is destroyed while the design still counts damaged ships (`D > 0`,
  below), `rand(500) < u` follows, and if it holds `D` drops by one. No
  other draws are made.
- **Damage (BINARY-ONLY; fits OB-021, GT-001).** For a design with `n`
  ships before the jump, armor `A` and old stack damage `(p₀, u)`
  (`COMBAT.md` conventions): damaged ships `D = max(1, ⌊p₀·n/100⌋)`, old
  damage per damaged ship `Dm = max(1, ⌊u·A/500⌋)` (both 0 when the stack
  was undamaged), and new damage `Nw = max(1, ⌊pct·A/100⌋)`. With `s`
  ships left after the draws: if `D > 0` and `Nw + Dm ≥ A`, `D` more ships
  are destroyed (`s − D` left). If ships are left, `avg = ⌊(Nw·s + Dm·D)/s⌋`
  and the stack becomes `p = 100` with `u = max(1, ⌊avg·500/A⌋)`. `D` is
  not lowered by that extra destruction, so destroyed damaged ships still
  add their old damage to the average (the LEGACY BUG candidate above).
  So the old damage counted is that of the `D` damaged ships, not of every
  ship of the design. When `D` is larger than `s`, the ship count goes
  negative and the fleet record is corrupt (BINARY-ONLY; no case reaches
  it, so Elegy needs a chosen rule there).
- **Fuel and cargo after losses (BINARY-ONLY; fits OB-021).** When any
  ship is lost, including a design lost entirely, the lost ships take
  `⌊fuel·L/T⌋` of the fleet's fuel, with `L` the fuel capacity (hull plus
  tanks) of the lost ships and `T` that of every ship before the jump. The
  fleet keeps the rest, so its fuel in effect rounds up: OB-021's 100 with
  one of three lost keeps `100 − 33 = 67`, and two of three lost would
  keep `100 − 66 = 34`. Cargo still aboard (IT, Jump Gate) is lost the same
  way by cargo capacity: `⌊C·Lc/Tc⌋` in total, split as `⌊c·lost/C⌋` per
  item, then any remainder 1 kT at a time over ironium, boranium,
  germanium and colonists in that order, in one pass over the items still
  holding cargo. It is the same proportional rule as for ships lost in
  battle. With no ship lost, fuel and cargo are unchanged.
- **Mixed fleets (LEGACY BUG, MEASURED GT-001 H2, GT-002):** each design
  lost entirely (`pct = 100`) counts twice against the fleet's number of
  designs, and a design wiped out by the loss rolls (`pct < 100`) counts
  once (CONFIRMED, GT-003 W0–W5: in W2 and W3 the roll destroyed the 491 kT
  freighter and the fleet kept its Laser DD). When the
  count comes to exactly 0, the whole fleet is deleted with the "fleet
  lost" message, survivors included: a 500 kT ship with a safe Laser DD
  through a 100 kT gate lost both, and so did two lost designs with two
  safe ones. Three designs with one lost, or three with two lost (count
  −1), kept their survivors. Elegy reproduces this behind a named
  legacy switch, like the other deterministic legacy bugs.
- Vectors (OB-021): 5 Laser
  Destroyers at 13% took 65/500 each; a refused ship over 5× a mass limit
  did not move and took no damage.
- Gate travel uses no fuel and crosses no minefields.
- **The rest of the year** (CONFIRMED, GT-001 I, K, L): a fleet that jumped (even with
  `pct = 0`) is not repaired that year. It counts as having moved; a
  refused fleet counts as stationary. Cheap Engines' engine failure never
  applies to a gate order. Other players' fleets chasing it stop at its
  departure point; the owner's own chasers follow it (as for wormholes).
- **What others see** (CONFIRMED, GT-001 E, F, K): only the fleet owner (and, for an
  unload, the source planet's owner) gets messages. The destination gate's
  owner is not told. Another player scanning the fleet after the jump
  sees it at the destination with warp 0 and no heading, since only
  ordinary movement records heading and warp.
- A gate jump never reaches a wormhole: the destination is always a
  planet and wormholes are never placed exactly on one (Placement;
  BINARY-ONLY, from absence).

## Wormholes

### Creation (CONFIRMED, OB-006, UG01–UG21)

The UG new games (`UNIVERSE.md`) matched a white-box prediction of every
wormhole's position and class exactly, at every size.


Only in games with random events on; with them off there are none (tiny
and huge, three seeds each). Pairs by universe size: `rand(v) + m` with
`(v, m)` = tiny (3, 0), small (3, 1), medium (5, 1), large (4, 3), huge
(5, 4), so 0–2, 1–3, 1–5, 3–6, 4–8 pairs. Every observed count (21 games)
fell in its range. Each end gets its own stability class `rand(3)` (0, 1
or 2; class 3 never appeared) and 0 years. Position: up to 100 uniform
tries over the galaxy, keeping the first with no badness, else the least
bad (Placement).

### Yearly movement (CONFIRMED in part, OB-005, OB-017)

Each end separately, in list order:

- Jump chance `pct = clamp(⌊years/5⌋ + class − 2, 0, 6)` percent;
  `rand(100) < pct` jumps (MEASURED, OB-025: 5 jumps in 60 end-years at
  6%). So class 0, 1, 2 cannot jump before 15, 10, 5 years (CONFIRMED for
  class 1, OB-025: no jump in its first three years).
- **Jump:** years reset to 0; nobody knows the wormhole any more; a new
  position from up to 100 uniform tries over the whole galaxy. MEASURED
  (OB-005-B): a class-2 end at 30 years jumped (−59, −25; years 0) in one
  of four streams, while its partner jiggled. CONFIRMED (OB-025): every
  jump reset the years and kept the class.
- **Jiggle:** years +1; up to 100 tries of `(x + rand(25) − 12, y + rand(25)
  − 12)` (CONFIRMED: at most 12 per axis). A try equal to the old position
  is skipped: it uses up a try but is not scored. The class never changes.
- Both kinds of move choose among their tries with the creation badness
  (Placement, "During movement" below).

### Stability (BINARY-ONLY)

The stability a player sees in the wormhole report is the end's current
yearly jump chance `pct` (above), by name: 0 Rock Solid, 1 Stable, 2 Mostly
Stable, 3 Average, 4 Slightly Volatile, 5 Volatile, 6 Extremely Volatile.
So it is not fixed: an end grows more volatile as its years rise, and a
jump (years back to 0) makes it stable again. A class-2 end at 0 years
reads Rock Solid, like class 0.

### Placement badness (CONFIRMED at creation, UG01–UG21)

A try is rejected outright when outside the galaxy or exactly on another
object, planet or fleet. Outside the galaxy means `x` or `y` below `1000` or
above `1000 + W`, where `W = 400 × (size + 1)` is the galaxy width (tiny
400 to huge 2000); a coordinate equal to `1000 + W` is inside (BINARY-ONLY:
no run placed an end on that line). Otherwise its badness combines: within 10 ly of
an edge; near its partner (`d²` < 25, 100, 900, 4900, worst first); near
another wormhole (< 16, 64, 225, 900); near a planet (< 25, 100, 400, 784).
The first try with no badness wins, else the least bad. In effect ends
settle ≥ 70 ly from their partner, ≥ 30 ly from other wormholes and
≥ 28 ly from planets when they can.

**How the terms combine.** Badness is a set of four flags, not a sum. Each
distance band sets one flag: the closest band sets 8, the next 4, then 2,
then 1. Being within 10 ly of an edge (`x` or `y` below `1010` or above
`1000 + W − 10`) sets 4. Every term is checked against every other
wormhole end and every planet, and the flags are OR-ed: two planets in the
same band still set only that band's flag. Tries are compared by the
resulting number (0–15), lower is better, and the first try with the
lowest value wins. So one closest-band hit (8) is worse than every other
combination (at most 7). A rejected try counts as 15: it can only be kept
when every one of the 100 tries was rejected. The partner's bands apply
only to the partner; when the first end of a pair is placed it has no
partner yet. A try is never outside the galaxy, since positions are drawn
as `1000 + rand(W)` on each axis.

**What counts as an object.** The exact-position rejection checks every
object in the object list (such as minefield centres, packets, Mystery Traders and
other wormhole ends; the end being placed is skipped), every planet and
every fleet. The distance bands look only at wormhole ends and planets:
fleets, minefields, packets and Traders add no badness short of sitting
exactly on the try (BINARY-ONLY for fleets, minefields, packets and
Traders; the wormhole and planet terms are CONFIRMED at creation).

**During movement (BINARY-ONLY except where tagged).** A jump and a
jiggle use the same badness as creation, with the same partner, wormhole
and planet bands and the same objects. Each try draws `x` first, then `y`:
a jump draws `1000 + rand(W)` twice, a jiggle `rand(25)` twice (the ±12
bound is CONFIRMED, the draw order is not). The end is moved to each try
before it is scored, and a try equal to the old position is skipped
without a score but still uses up one of the 100. The first try with
badness 0 ends the search. Otherwise the end takes the first try with the
lowest badness, and a rejected try (15) beats no try at all: if every
scored try was rejected, the end moves to the first of them, even outside
the galaxy or onto another object. It does not stay where it was. A
jiggle can only be rejected for being outside the galaxy or on an exact
object, so every try failing would in practice need an end in a corner with
all of its inside cells occupied; no run has come close (UNRESOLVED whether the
original then shows the end outside the galaxy; LEGACY BUG candidate).

### Travel (CONFIRMED, OB-005 C, D)

A fleet whose next waypoint is a wormhole and that reaches it this year is
placed on the partner end, at the partner's position from before this
year's wormhole movement. Both ends become known to its owner; other
players' fleets that were following it lose it. Fuel, mass and stability
play no part and there is no damage. A fleet that falls short stays in
normal space.

**What transits (CONFIRMED, WT-001 B–E; stargate landings BINARY-ONLY).** Only fleets, and only when the waypoint
they reach targets the wormhole itself. A waypoint that is a plain position
on the same coordinates does not transit, and a fleet that passes over a
wormhole in mid-move does not. A stargate jump that lands on a wormhole
target transits (Stargates). Packets and the Mystery Trader never transit
or interact with wormholes (a packet and a Trader that ended their moves
exactly on an end stayed there). Arrival and the exit position both use the
positions from the start of the year: wormholes move after fleets.

**Destination knowledge (CONFIRMED, WT-001 A, G; WT-004: 18 jumps; the
report and map display BINARY-ONLY).** Besides knowing where an end is
(scanning, `SCANNING.md`), each end records which players know where it
leads. That record is set only by transit, for the fleet's owner, on both
the entry and the exit end; the exit end also becomes known. Seeing both
ends, however long, never reveals that they are a pair. The record is
never cleared, even by a jump: after its partner jumps, a player who once
transited still sees the destination, at the partner's new position, but
only while the partner end itself is seen that year. The wormhole report
shows the destination's coordinates when both hold, and "Unknown"
otherwise; the map draws the link line under the same condition.

**Waypoints on a wormhole (CONFIRMED, OB-025-F, OB-027).** A waypoint aimed
at a wormhole follows it only while the owner knows the wormhole at the
start of the year. Otherwise, after the wormhole's first move, the
waypoint becomes a plain position at the wormhole's old position, even if
the owner sees the wormhole later that year. A jump clears everyone's
knowledge, so after a jump it always becomes a plain position.

## Mystery Trader

### Appearance (CONFIRMED, KX-004 S6–S10; marked details BINARY-ONLY)

When and where a Trader appears, its warp, start, destination, item and
announcement are specified in `KERNEL.md` "Mystery Trader appearance" and
were CONFIRMED by KX-004 S6–S10 (`PARITY.md` KX-004 addendum: 24 one-year
runs, 15 Traders and 9 empty years, each as replayed). The summary below is
for reference; `KERNEL.md` is authoritative. The part reroll and the
late-year conversion to research stay BINARY-ONLY: no run drew them.

- From year index 40, with random events on, at the end of production:
  chance 1/2 when `year index mod 100 = 71`, 1/3 when `= 33`, 1/4 when
  `year index mod 128 = 49`, otherwise 1/7 in even and none in odd years.
  A second Trader can appear while one exists.
- Warp `8 + rand(5)`. It enters on one edge and heads for a point on the
  opposite edge (axis `rand(2)`, direction `rand(2)`, the free coordinate
  uniform along the edge for start and destination separately). Every
  player is told.
- Item offered: research or a ship with probability `r/10`, `r` = 5 before
  year index 100, 3 before 250, 2 after, +1 below warp 10, −1 above; then
  ship with 1/6, else research. Otherwise one of 13 bits, uniformly: the
  twelve parts of the bit table in "Encounters" below, or bit 12, a ship gift.
  - **Reroll.** A first draw of bit 6 (Anti Matter Torpedo), 7 (Multi
    Contained Munition), 10 (Genesis Device) or 11 (Jump Gate) is replaced
    by a second `1 << rand(13)`. The second draw stands even if it is one of
    those four again; there is no third.
  - **Conversion.** Only a second draw can convert. If it is bit 7 before
    year index 120, bit 10 before 150, or bit 11 before 180, a `rand(2)` is
    drawn and 1 turns the item into research (so 1/2). Bit 6 is rerolled
    but never converted. No `rand(2)` is drawn in any other case.
  - BINARY-ONLY: no KX-004 run drew one of the four bits.

### Movement (BINARY-ONLY except where noted; not part of KX-004)

- It moves before fleets, `warp²` ly per year like a packet. Below warp 13,
  each year with 1/25 its warp rises by 1, and then with 1/3 it picks a new
  destination. On arrival it leaves the galaxy if another Trader exists or
  with 1/2; otherwise it stays at the edge, takes warp `max(6, warp − 2) +
  1` and a new destination, and does not move further that year.
- **Draws in a year (BINARY-ONLY).** Only at warp 12 or below: `rand(25)`;
  0 raises the warp (every player is told), and only then `rand(3)`, where
  0 draws a new destination. So a new destination in flight comes only in
  a year whose warp rose. The Trader then moves at the new warp. On
  arrival: with another Trader present it is removed with no draw;
  otherwise `rand(2)`, where 0 removes it and 1 keeps it and draws the new
  destination. Traders move one at a time in object-list order, and a
  removed Trader leaves the list at once. So "another Trader" means one
  still in the galaxy at that moment, anywhere, including one that has
  not moved yet this year; a Trader removed earlier in the same year does
  not count. When two arrive in one year, the first is removed with no
  draw and the second, now alone, draws.
- **New destination (CONFIRMED in part).** Drawn the same way after a
  warp rise and after arrival: `rand(2)` picks the side (0 the high edge
  `1380 + 400·size`, 1 the low edge `1020`); then the free coordinate
  `1020 + rand(361 + 400·size)`; then `rand(2)` picks the axis (0: the
  destination's `x` is the edge value and `y` the free one; 1: the
  reverse, note the opposite sense to the appearance draw in `KERNEL.md`).
  So it can be any of the four edges, wherever the Trader is and wherever
  it was heading. CONFIRMED that it is not tied to the old axis: OB-023's
  Trader arrived on the `x = 1380` edge at (1380, 1300) and got (1098,
  1380), on a `y` edge. The draw order is BINARY-ONLY.
- **Each year's step (BINARY-ONLY in detail; shared with packets).** With
  `d` the exact distance to the destination and `m` the year's move: if
  `trunc(d) ≤ m` it arrives. Otherwise, when `d > 0.0001`, each axis moves
  by `trunc(Δ·m/d + h)`, with `Δ` the destination's coordinate minus the
  current one, `h = +0.5` when `Δ > 0`, else `−0.5`: rounding half away
  from zero, `m/d` computed once for both axes. If that step lands exactly
  on the destination, it counts as an arrival that year. The packet flights
  of OB-003 and OB-028 and the Trader's 81 ly at warp 9 (OB-023) agree
  with it.
  CONFIRMED (OB-023, OB-026, OB-031): a warp-9 Trader moved 81 ly; one
  arriving while another existed was removed; the only Trader stayed, warp
  8 → 7, with a new destination on an edge; a lone warp-6 Trader stayed
  with warp 7 (`max(6, 4) + 1`) in three streams (OB-031). The 1/2 chance
  of leaving is still unobserved: all four lone arrivals measured so far
  stayed (OB-023, OB-031 ×3). MEASURED (WT): 4 warp rises 8 → 9 in
  about 80 Trader-years, each before that year's move and announced to
  every player, one with a new destination on an edge.

### Targeting the Trader (CONFIRMED, WT-001 F1, WT-005)

The Trader moves before fleets, and waypoints on it are then moved to its
new position before any fleet moves. So a fleet aimed at the Trader flies
toward where the Trader is after this year's move: a fleet that reaches
that point meets it, and a slower one ends the year on the line toward
it. (WT-005: a fleet 50 ly east of the Trader's start reached its end
point 31 ly away and traded; a warp-6 fleet 30 ly west flew its full 36 ly
east, past the start point.) The same refresh runs whenever a Trader or a
packet moved that year; it is the waypoint check described under "Waypoints
on a wormhole", so wormhole targets are checked again at that point too
(wormholes themselves move only after fleets). A Trader that appears this year (end of production, before meetings) meets
fleets already sitting on its entry point the same year. When a Trader is
gone, waypoints on it become plain positions at its last known position,
and the owner is told.

### Encounters (CONFIRMED, OB-004, OB-023, OB-026; marked details BINARY-ONLY)

After battles, each Trader meets every fleet at exactly its position, of
any owner, whether the fleet targeted it or just ended there. It works
with random events off (an inserted Trader traded).

- Ironium + boranium + germanium below 5,000 kT (colonists and fuel do not
  count): nothing happens (the fleet's owner gets a message if the fleet
  moved). 4,999 kT kept the fleet; 5,000 kT traded.
- Each player gets one reward per Trader: a second fleet of the same
  player at the same Trader in the same year was kept.
- Trading **removes the whole fleet**, ships and cargo.
- Order of checks for each fleet (CONFIRMED with two Traders, OB-030-T:
  Trader 0 took one fleet of each player and refused the second fleet of
  player 0, which Trader 1 then took): cargo below 5,000 kT →
  refused; else owner already served by this Trader → refused ("still
  recovering from the last transaction"), fleet kept; else the owner is
  marked served, the fleet is consumed, and the reward follows. A fleet
  consumed by one Trader is not offered to another in the same year.
- Reward:
  - a part the player lacks: that part (CONFIRMED, OB-026: the player's
    Trader part word gained the part's bit; tech unchanged). The part
    word's bits and messages (CONFIRMED, WT-003 A, all twelve):

    | Bit | Item | Message |
    |---|---|---|
    | 0 | Multi Cargo Pod | unique part |
    | 1 | Multi Function Pod | unique part |
    | 2 | Langston Shell | unique part |
    | 3 | Mega Poly Shell | unique part |
    | 4 | Alien Miner | unique part |
    | 5 | Hush-a-Boom | unique part |
    | 6 | Anti Matter Torpedo | unique part |
    | 7 | Multi Contained Munition | unique part |
    | 8 | Mini Morph hull | new ship hull |
    | 9 | Enigma Pulsar | unique part |
    | 10 | Genesis Device | powerful planetary device |
    | 11 | Jump Gate | unique part |
    | 12 | (a ship gift, below) | |

    The same twelve parts can also come from a battle, a capture or
    scrapping at a starbase: that tech attempt (`COMBAT.md` "Tech from
    battle", `TAKEOVER.md`) makes up to 13 `rand(13)` item draws, with a
    `rand(100)` only for an item that has a chance there and that the
    player lacks. A capture gives no item a chance, so it always makes its
    13 draws and gives nothing.

  - research (or an offered part already owned):
    - If every tech field is at 26: with 1/5 nothing ("unable to teach you
      anything new"); with 4/5 a random part. The part is drawn as `bit =
      rand(13)`, redrawn while the player already owns it, up to 25
      redraws. Bit 12 means a ship. If the 25 redraws run out, the player
      gets a ship, and so does a player whose 25th redraw found an unowned
      part (LEGACY BUG, BINARY-ONLY: too rare to sample). A player who owns
      all twelve parts therefore always gets a ship on the 4/5 branch
      (CONFIRMED, WT-004 C: nothing in 3 of 15 meetings, a ship in 12). (A player whose
      research is capped at 10 uses 10 here; Elegy has no such players.)
    - Otherwise (CONFIRMED, WT-002 A, B; the field odds MEASURED in two
      streams only): `L = min(10, 6 + ⌊(cargo − 5000)/1200⌋)`
      levels, adjusted by the sum of tech levels `T`: `T ≥ 108` → 1,
      96–107 → 2, 84–95 → `L − 3`, 72–83 → `L − 2`, 60–71 → `L − 1`. The
      message gives `L`. Each level, in turn: with 3/4 a uniformly random
      field (the lowest field instead if that one is at 26), with 1/4 the
      lowest field (first in field order on ties); the loop stops early
      once the lowest field is at 26. Draws per level: `rand(4)`; 0–2 then
      `rand(6)` for the field (fields in the order energy, weapons,
      propulsion, construction, electronics, biotech), 3 no further draw
      (BINARY-ONLY; the field odds are MEASURED as above). Each step raises that field by
      exactly one level and leaves its accumulated research unchanged.
      CONFIRMED: a tech-3 player trading 5,000 kT gained 6 levels.
  - a ship (CONFIRMED, WT-003 B, WT-004 B, C: 27 gifts, Lifeboat 5,
    Scout 11, Probe 11, at most 4 ships; the count rules after year index
    100 and for computer players BINARY-ONLY):
    - Computer players get nothing, and their fleet is still consumed.
    - Design: with 1/4 (1/3 after year index 100) "M.T. Lifeboat", a
      Nubian; otherwise "M.T. Scout" or "M.T. Probe" with equal odds, both
      Mini Morphs. Loadouts:
      - Lifeboat: Enigma Pulsar ×3; Mega Poly Shell ×3 in two slots; Anti
        Matter Torpedo ×3 in two slots; Langston Shell ×3 in two slots;
        Multi Function Pod ×3 in two slots; Multi Cargo Pod ×3; Multi
        Contained Munition ×3 in three slots.
      - Scout: Enigma Pulsar ×2, Langston Shell ×3, Multi Function Pod,
        Multi Cargo Pod, Jump Gate, Anti Matter Torpedo ×2 in two slots.
      - Probe: as the Scout, with Mega Poly Shell ×3 in place of the
        Langston Shells.
    - **Slot layout (MEASURED, WT-004: 27 gift designs).** The loadouts
      above are in the hull's slot order (`data/components.json`), one
      entry per slot, and "in two slots" or "in three slots" means
      consecutive slots. Every slot of the hull is filled to its maximum,
      the engines in the first slot. The gift copies a fixed design, so
      the layout never varies (BINARY-ONLY).
    - Count: 2 with 1/3, else 1. After year index 100, unless the game has
      a single human player, add `rand(⌊year index/100⌋ + 1)`. Cap at 5.
      For the Scout and the Probe, then add `rand(count + 1)`. So 1–10
      ships.
    - A design the player already has that matches is reused; otherwise
      the design goes into the player's first empty design slot, in slot
      order 1 to 16 (CONFIRMED, WT-004). It keeps its Trader parts although
      the player's part word does not gain them. The new fleet appears at
      the trade point with full fuel.
    - **Matching (BINARY-ONLY).** Only a design that came from an earlier
      Trader gift and is still in use can match: the gift marks the
      designs it creates, and a player's own design with the same parts
      never matches. It matches when the hull, the number of slots and
      every slot's count are equal, and every non-empty slot holds the same
      part. The name is not compared. A reused design is not rewritten.
    - **Draw order (BINARY-ONLY).** Computer players draw nothing. Then the
      design `rand(4)` (`rand(3)` after year index 100), then for a
      non-zero result `rand(2)` (0 Scout, 1 Probe). The count draws come
      only when a slot is found and the player has fewer than 512 fleets:
      `rand(3)`, then `rand(⌊year index/100⌋ + 1)` when that applies, then
      `rand(count + 1)` for a Scout or Probe.
    - **The new fleet (BINARY-ONLY).** It takes the player's lowest unused
      fleet number, battle plan 0 (the player's first plan), one waypoint
      at the trade point, and is marked as not having moved this year.
      Consumed fleets, the traded fleet and any consumed earlier that
      year included, still hold their numbers then: they stay in the
      fleet list until all the meetings are over. So the gift fleet never
      takes the number of a fleet consumed that year. It
      orbits whatever planet the traded fleet orbited, if any. If it lands
      later in the fleet list it is offered to the Trader like any fleet,
      but it carries no minerals, so it never trades and, not having
      moved, gets no message.
    - With no free design slot, or 512 fleets already, there is no ship
      (the player is told the design records could not be stored) and the
      fleet is still consumed.
    - CONFIRMED (OB-026): one Nubian at the trade point, added as a new
      design.

### Computer players' planets (CONFIRMED in part, TP-001, TP-002; marked parts BINARY-ONLY)

After the fleets, each Trader also trades with computer players' planets.
Only Harder and Expert computer players take part, and only a planet with
a starbase, within 100 ly of the Trader, whose owner this Trader has not
served. The planet needs Ir + Bo + Ge on its surface of at least 5,000 kT
(3,500 for Harder). (TP measured Expert Turindrone and Automitron
homeworlds within 100 ly. O-53 CONFIRMED the Harder rule: a Harder
planet with 3,600 kT traded and paid 3,500 kT. A Standard planet and an
Expert planet with 3,600 kT did not trade, which fits but does not
separate "Standard never trades" from "Standard needs 5,000 kT"; the
exclusion of Standard and Easy players is BINARY-ONLY. The exact edge at
3,500 kT is NOT RUN, and the 100 ly edge is BINARY-ONLY.)

- **Part item.** If the owner lacks the part, it gains it. If it owns it,
  a random part it lacks is drawn, with up to 50 redraws; bit 12 counts as
  a part here and gives nothing but the bit. The price is all the
  planet's surface minerals (CONFIRMED, TP-001-A: the bit, surface to 0;
  TP-002-A: the part owned, a new bit drawn instead).
- **Research item, or no part found.** If the owner's tech levels sum to
  150 or more, nothing happens and the Trader stays available to it
  (CONFIRMED, TP-002-B). Otherwise the lowest field gains a level, six
  times, at no research cost (CONFIRMED, TP-001-B: 10,10,10,13,10,10 →
  12,11,11,13,11,11). The price is 5,000 kT (3,500 for Harder; CONFIRMED,
  O-53).
- The price is taken from germanium first, then boranium, then ironium
  (CONFIRMED, TP-001-B). The owner is marked served. No message is sent.
- **Order and range (BINARY-ONLY).** For each Trader, its fleets come
  first, then the planets in planet-number order (numbered in `x` order at
  creation, `UNIVERSE.md`). The scan stops at the first planet more than 100 ly east of
  the Trader in `x`. A planet trades when `d² ≤ 10,000`, so exactly 100 ly
  is in range.
- **A ship item (BINARY-ONLY).** For planets a ship offer is not
  research: it is handled as part bit 12. An owner that lacks the bit gains
  it, and the price is all the surface minerals; an owner that has it
  rerolls as for a part it owns. Only item 0, or no unowned bit found in
  50 rerolls, leads to the research branch.

Human players' planets never trade (CONFIRMED, TP-001-C, TP-002-C).

## Visibility (see SCANNING.md; CONFIRMED there)

Which of these objects each player sees, and what seeing them discloses
(including the Packet Physics, Interstellar Traveler and Space Demolition
rules), is specified in `SCANNING.md`, which owns all visibility rules.
The oracle records are OB-011..OB-014, OB-017, OB-018 and OB-020 in
`PARITY.md` (OB-020: a known wormhole is seen anywhere within normal range
and nowhere beyond it).

## Open experiments

1. Packets: the 32,760 kT and 16,300 kT limits; the PP terraforming
   draws and permanent changes as rates; whether a PP packet discloses the
   catcher's starbase design (needs a control, OB-029-D2).
2. Wormhole jump odds as a measured rate (one stream so far).
3. Mystery Trader: leaving with 1/2 at an edge (0 of 4 lone arrivals
   left); ship counts after year index 100; the 25th-redraw LEGACY BUG;
   the part reroll and late-year conversion at appearance; the trade's
   exact 3,500 kT edge for Harder players, its 100 ly edge, and whether
   Standard and Easy players' planets never trade.
4. Minefields (MF-1..MF-15 done; see PARITY "Minefield lane"): the
   4050-object limit; SS and SD safe-warp bonuses; steep (not due-north)
   legs and diagonal stop points;
   fleets jumping through a gate inside a field; the detonate-order gap
   (needs crafted orders).
5. Stargates: gate losses in more streams.
6. Wormholes: stability names in the report (O-45, UI).

Random outcomes must be compared with the full outcome set. Repeated oracle
runs at one generator setting are not independent samples.

## Sources

- Oracle: OB-001..OB-031, GT-001..GT-003, TP-001/002, WT (`PARITY.md`,
  "Universe objects", "Stargates" and "Scanning", `experiments/ob/`,
  `experiments/gt/`, `experiments/tp/`); raw evidence in private
  `stars-oracle-apparatus`.
- White-box readings: private `stars-decomp` (objects, minefield hits and
  stargates in fleet movement, scanning notes).
