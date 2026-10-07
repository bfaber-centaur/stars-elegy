# Universe objects specification: minefields, packets, stargates, wormholes, Mystery Trader

Behavioral specification of the J-RC3 rules for the objects in space that
are neither planets nor fleets, and for the travel that bypasses normal
flight: minefields, mass-driver packets, stargates, wormholes and the
Mystery Trader, with where each step sits in the year. It is written for an
implementer working only from this public repository. It describes what
happens in the game, not how any file encodes it.

`PARITY.md`, section "Universe objects" (and "Scanning", object
visibility), holds the experiment records (OB-001 to OB-018). This file
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
   (OB-002-F) and before a hit's loss is counted (OB-010-S).
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
  25 ly away stayed and laid its full amount).
- Space Demolition (SD) only: a fleet travelling toward a waypoint whose
  task is "lay mines" also lays, at its end-of-year position, **half** the
  amount (CONFIRMED, OB-014-C: 80 from a layer rated 160). The halving uses
  the moving test, so an SD fleet that moved for any reason lays half
  (BINARY-ONLY beyond that case).
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
  - Super Mine Layer doubling: BINARY-ONLY.
- A fleet with no dispenser of any kind lays nothing and gets a message.
- **Merging.** Among the owner's fields of the same kind that contain the
  fleet, the one whose centre is nearest takes the new mines, unless it
  already holds more than 999,999. Its count adds, and its centre moves to
  the count-weighted mean, each coordinate
  `⌊(x_field·N_field + x_fleet·laid) / (N_field + laid)⌋`, using the
  field's count after this year's decay. Otherwise a new field is created
  at the fleet. CONFIRMED (OB-002-G): a 390 field 10 ly west of the layer,
  plus 160, became 550 centred 2 ly east of the old centre.
- **Duration.** The task carries a duration: "this year only" lays once and
  ends the task (CONFIRMED, OB-002-N); "indefinitely" never ends; 2 to 5
  years count down one per year and end after the last (BINARY-ONLY). The
  fleet's later waypoints stay queued meanwhile (MEASURED, OB-014-D after
  file; see Open experiments).

### Decay (CONFIRMED, OB-002, OB-014-A, OB-015, OB-016)

Each year, every field loses `p` percent, where `n` is the number of
planets inside it (any owner, including none):

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

### Hits on moving fleets (CONFIRMED in part, OB-010; rest BINARY-ONLY)

Applies to a fleet moving at warp 1–10 (not through a stargate) across a
field whose owner is not the fleet owner and does not treat the fleet
owner as a friend. Stationary fleets are never hit.

- **Effective warp** `e` comes from the distance `D` actually travelled
  this year, not the ordered warp: the smallest of 3..10 with
  `e² ≥ D − 1`. CONFIRMED: five warp-9 fleets moving 30 ly inside a heavy
  field (safe 6, `e` = 6) were never hit in 30 fleet-years (OB-010 H0–H4).
- **Safe warp** by kind: standard 4, heavy 6, speed bump 5; +1 if the
  fleet owner is Super Stealth, +2 if Space Demolition. No check when `e`
  is at or below the safe warp, or when the fleet was already at its
  waypoint.
- The path from the fleet's position toward its next waypoint is cut by
  each field into an entry and exit distance (whole ly, entry not below 0,
  exit not beyond this year's travel; a tangent path does not count).
  Overlapping stretches of one kind merge. Stretches are visited in order
  of entry across all kinds. For each whole ly of a stretch, one draw:
  `rand(1000) < (e − safe)·h` is a hit, with `h` = 3 (standard), 10
  (heavy), 35 (speed bump) per mille.
- **On a hit** the fleet stops there (distance from its start = entry + the
  ly index); no further checks this year; no ram-scoop fuel this year; the
  fuel for the full planned leg is already spent. CONFIRMED: stop points
  55 and 64 ly into a field (OB-010-S).
- **Damage** (standard and heavy; speed bumps only stop): per ship per
  engine, standard 100 and heavy 500, or 125 and 600 when any design in
  the fleet has an engine that burns no fuel at warp 4. Fleets of fewer
  than 5 ships get at least 500 (standard) or 2000 (heavy) in total, 600
  and 2500 with such an engine, the shortfall added to the first design.
  Per design: `D = (ships·per + shortfall)·engines`; shields absorb at most
  `D/2`; the result is added to existing damage and spread evenly. A design
  whose average exceeds its armor is destroyed. CONFIRMED: five Laser
  Destroyers each took half their armor (OB-010-S, OB-002-M).
- Destroyed ships' share of cargo is lost; their minerals become salvage
  at the stop point (none at a planet's exact position). A fleet with no
  minerals that loses ships drops `rand(10)` kT of each mineral as salvage
  (BINARY-ONLY; LEGACY BUG candidate).
- **Mines lost to the hit:** the field of that kind, not owned by a friend,
  whose edge is nearest the stop point, loses `max(10, ⌊N/20⌋)`, or
  `max(50, ⌊N/100⌋)` when `⌊N/20⌋ > 50`. CONFIRMED for one size: 3000 →
  2950 before decay (OB-010-S). The victim learns the field. If the field
  owner is SD, it learns the victim's damaged designs (all of its designs
  present if none was damaged).

### Detonation (MEASURED, OB-002-M)

A field set to detonate (an SD standard-field order, BINARY-ONLY) goes off
each year before decay: every fleet inside it, of any owner including the
field's owner, takes hit damage as above, except the owner's own Mini Mine
Layer and Super Mine Layer hulls. No stop, no salvage, at most one
detonation per fleet per year. The field then decays with the extra 25%.
OB-002-M: the owner's five Laser Destroyers took half their armor, the
enemy's five Medium Freighters 100 each, the layer nothing; the field went
1000 → 730.

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

### Launch (BINARY-ONLY)

- Needs a mass driver on the planet's starbase and a packet destination;
  otherwise the item is not built and the player gets a message.
- Driver warp `Dw`: the best driver's rating; `t` = 1 when two different
  orbital slots each hold that best driver (only starbase hulls with two
  orbital slots can), else 0.
- Each item launches 100 kT of one mineral (Packet Physics: 70), or for a
  mixed item 40 kT of each (PP: 25), times the item count, at most 32,760
  per mineral.
- Packet warp `W`: the planet's packet-speed setting; if below 5 or above
  `Dw + 3`, it becomes `Dw + t`.
- Decay class `k = max(0, W − Dw − t)`, +1 for an Interstellar Traveler
  launcher, at most 3.
- A packet launched from the same planet in the same year with the same
  warp, destination and class merges into the first while it is under
  16,300 kT.

### Flight and decay (CONFIRMED in part, OB-003; rest BINARY-ONLY)

- On its launch year a packet moves `⌊W²/2⌋` ly; after that `W²` ly per
  year (CONFIRMED for later years, OB-003 J, K), straight toward the
  destination planet. It arrives when the truncated distance is at most
  the year's move; otherwise each coordinate moves by the rounded share.
- Decay per year by class: 0 none; 1, 2, 3: 10, 25, 50% of each mineral
  (CONFIRMED for classes 2 and 3, OB-003 J, K). A PP owner's packets decay
  at half those rates, 5, 12 and 25% (BINARY-ONLY). Each non-empty mineral
  loses at least 10 kT (PP: 5). On the launch year a packet that does not
  arrive decays half a year. On arrival it decays for the share of the
  year it flew, but the minimum still applies (CONFIRMED, OB-003-C: a
  class-1 100 kT packet arriving with 5% of a year left lost 10).

### Impact (CONFIRMED, OB-003, OB-009; marked parts BINARY-ONLY)

Target planet with catcher warp `C` (the planet's own `Dw + t`; 0 if
unowned or no starbase). Let `w² = W²`, `c² = C²`,
halved when the target's owner is Interstellar Traveler (BINARY-ONLY).

1. Caught share, per mille: `q = 1000` if `w² ≤ c²`; `⌊c²·1000/w²⌋` if
   `C > 0`; else 0.
2. **Minerals added to the surface**, per mineral after arrival decay:
   `⌊m·(q + ⌊(1000 − q)/9⌋)/1000⌋`. The uncaught share arrives as one ninth;
   the rest is lost. Vectors: 1000 kT uncaught: +111; 300/200/100: +33,
   +22, +11; Mass Driver 7 catching warp 10 (q = 490): 1000 kT gives +546;
   a packet no faster than the catcher: +1000 and no damage.
3. Fully caught: done.
4. PP launcher (BINARY-ONLY): the catcher's starbase design becomes known
   to it, and the packet terraforms (below), on owned and unowned planets.
5. Unowned planet: done.
6. **Damage**, in units of 100 colonists:
   `dmg0 = ⌊(w² − c²)·M/160⌋`, `M` = total cargo after arrival decay;
   `dmg = ⌊s·dmg0⌋`, with `s` the planet's share that gets through its
   defenses (the defense coverage against normal bombs, `TAKEOVER.md`).
   Alternate Reality planets take no damage (BINARY-ONLY).
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
With 50 SDI defenses: 418 killed, defenses 50 → 30. Damage at or above the
population: uninhabited.

**PP terraforming (BINARY-ONLY).** For each mineral, the uncaught share
`u = ⌊m·(1000 − q)/1000⌋` works on one axis (ironium gravity, boranium
temperature, germanium radiation; the pairing is inferred). For each
100 kT chunk (the last may be partial) one draw `rand(200) < min(chunk,
100)` is a success; each success draws again and is also permanent with
`rand(10) == 0`. The permanent count moves the planet's original value
toward the PP player's ideal (capped there), or toward the nearer extreme
for an axis the PP player is immune to. Then, if the PP player's
terraforming tech could improve the planet, the current value moves by the
success count toward the PP player's ideal, within the PP player's
terraform range around the original value (immune axis: half the count
toward the nearer extreme).

## Stargates (BINARY-ONLY)

A fleet uses gates when its next waypoint's warp is the gate setting.

- **Source:** the gate on the starbase of the planet the fleet is at, owned
  by the fleet owner or a friend. Without one, every ship in the fleet
  must carry a Jump Gate, and the destination gate's limits then stand for
  both ends.
- **Destination:** a planet at the waypoint with a gate owned by the fleet
  owner or a friend. A Jump Gate does not replace a missing destination
  gate.
- **Cargo:** unless the fleet owner is Interstellar Traveler or uses a
  Jump Gate, all ironium, boranium, germanium and colonists are unloaded
  onto the source planet before the jump is checked, so a jump refused for
  range or mass still empties the hold (LEGACY BUG). Carrying colonists
  from a planet the fleet owner does not own blocks the jump.
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
  damaged ships still count in that average: LEGACY BUG candidate). A
  design with `pct = 100` is lost entirely; if every design is lost, the
  fleet is gone.
- Gate travel uses no fuel and crosses no minefields. Landing on a
  wormhole transits it.

## Wormholes

### Creation (MEASURED, OB-006)

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
  `rand(100) < pct` jumps (BINARY-ONLY odds). So class 0, 1, 2 cannot jump
  before 15, 10, 5 years.
- **Jump:** years reset to 0; nobody knows the wormhole any more; a new
  position from up to 100 uniform tries over the whole galaxy. MEASURED
  (OB-005-B): a class-2 end at 30 years jumped (−59, −25; years 0) in one
  of four streams, while its partner jiggled.
- **Jiggle:** years +1; up to 100 tries of `(x + rand(25) − 12, y + rand(25)
  − 12)` (CONFIRMED: at most 12 per axis). A try equal to the old position
  is rejected. The class never changes.

### Placement badness (BINARY-ONLY)

A try is rejected outright when outside the galaxy or exactly on another
object, planet or fleet. Otherwise its badness combines: within 10 ly of
an edge; near its partner (`d²` < 25, 100, 900, 4900, worst first); near
another wormhole (< 16, 64, 225, 900); near a planet (< 25, 100, 400, 784).
The first try with no badness wins, else the least bad. In effect ends
settle ≥ 70 ly from their partner, ≥ 30 ly from other wormholes and
≥ 28 ly from planets when they can.

### Travel (CONFIRMED, OB-005 C, D)

A fleet whose next waypoint is a wormhole and that reaches it this year is
placed on the partner end, at the partner's position from before this
year's wormhole movement. Both ends become known to its owner; other
players' fleets that were following it lose it. Fuel, mass and stability
play no part and there is no damage. A fleet that falls short stays in
normal space. A waypoint on a wormhole its owner no longer knows (after a
jump) becomes a plain position (BINARY-ONLY).

## Mystery Trader

### Spawn and movement (BINARY-ONLY)

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
  ship with 1/6, else research. Otherwise one of 13 parts, rerolled once
  for four of them, and three of those turn into research with 1/2 before
  year index 120, 150 or 180.
- It moves before fleets, `warp²` ly per year like a packet. Below warp 13,
  each year with 1/25 its warp rises by 1, and then with 1/3 it picks a new
  destination. On arrival it leaves the galaxy if another Trader exists or
  with 1/2; otherwise it stays at the edge, takes warp `max(6, warp − 2) +
  1` and a new destination, and does not move further that year.

### Encounters (CONFIRMED, OB-004; reward details BINARY-ONLY)

After battles, each Trader meets every fleet at exactly its position, of
any owner, whether the fleet targeted it or just ended there. It works
with random events off (an inserted Trader traded).

- Ironium + boranium + germanium below 5,000 kT (colonists and fuel do not
  count): nothing happens (the fleet's owner gets a message if the fleet
  moved). 4,999 kT kept the fleet; 5,000 kT traded.
- Each player gets one reward per Trader: a second fleet of the same
  player at the same Trader in the same year was kept.
- Trading **removes the whole fleet**, ships and cargo.
- Reward:
  - a part the player lacks: that part;
  - research (or an offered part already owned): if every tech field is at
    26 (10 for computer players, inferred), with 4/5 a random part not yet
    owned (else a ship) and with 1/5 nothing; otherwise
    `L = min(10, 6 + ⌊(cargo − 5000)/1200⌋)` levels, reduced by the sum of
    tech levels `T`: `T ≥ 108` → 1, 96–107 → 2, 84–95 → `L − 3`, 72–83 →
    `L − 2`, 60–71 → `L − 1`. Each level goes with 3/4 to a random field
    (the lowest if that one is at 26) and with 1/4 to the lowest field.
    CONFIRMED: a tech-3 player trading 5,000 kT gained 6 levels;
  - a ship: computer players get nothing. One of three Trader designs, 1
    ship (2/3) or 2 (1/3), more after year index 100, at most 5; the new
    fleet has full fuel and the design joins the player's designs (if a
    design slot and a fleet number are free).

## Visibility

Which of these objects each player sees, and what seeing them discloses
(including the Packet Physics, Interstellar Traveler and Space Demolition
rules), is specified in `SCANNING.md`, which owns all visibility rules.
The oracle records are OB-011..OB-014, OB-017 and OB-018 in `PARITY.md`.

## Open experiments

1. A lay-mines task on the current waypoint with "indefinitely": the fleet
   stays and lays again the next year (field 160 → 310 → 460), and its next
   waypoint stays queued. The OB-014-D summary reported that waypoint
   removed; the preserved after-turn file still lists it.
2. A known wormhole between a quarter of normal range and full normal
   range (no penetration) is seen; an unknown one at the same distance is
   not (`SCANNING.md`).
3. Packet launch: warp, class, amounts, same-year merge, the launch-year
   half move; PP decay rates and terraforming; IT and AR targets.
4. Wormhole jump odds over many streams; what a jump does to fleets heading
   for the wormhole.
5. Mystery Trader spawn, path, part and ship rewards.
6. Minefield hit odds per ly and mines lost for other field sizes; heavy
   and speed-bump detonation; the Super Mine Layer doubling.
7. Stargates: every rule above.

Random outcomes must be compared with the full outcome set. Repeated oracle
runs at one generator setting are not independent samples.

## Sources

- Oracle: OB-001..OB-018 (`PARITY.md`, "Universe objects" and "Scanning",
  `experiments/ob/`); raw evidence in private `stars-oracle-apparatus`.
- White-box readings: private `stars-decomp` (objects, minefield hits and
  stargates in fleet movement, scanning notes).
