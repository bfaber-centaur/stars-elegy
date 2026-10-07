# Scanning specification: what each player learns each year

Behavioral specification of the J-RC3 rules that decide what each player
knows at the end of a year: scanner ranges, penetration, cloaking,
tachyon detectors, starbases, planet scanners, race-specific disclosure,
allies, and how much detail each kind of sighting reveals. It is written
for an implementer working only from this public repository. It describes
what a player is told, not how any file encodes it.

`PARITY.md`, section "Scanning", holds the experiment records (SC-001 to
SC-034). This file restates them as rules and adds rules that so far come
only from white-box analysis of the original program (private
`stars-decomp`, promoted here as behavior only). Part statistics (each
scanner's normal and penetrating range, each part's cloak points) belong in
the public components table. Parts are named here, and numbers appear only
where a rule needs a worked example.

## Status of each rule

- **CONFIRMED**: a white-box reading agrees with original-game oracle
  observations (SC case ids given). Vectors given for it are ground truth.
- **BINARY-ONLY**: read from the original program, with no oracle
  observation yet. Vectors are worked from the rule. Treat these as
  predictions; they are listed under Open experiments.
- **LEGACY BUG**: confirmed or read behavior that looks like an accident of
  the original implementation rather than a design intent. Implement it
  for parity unless the project decides otherwise.

"Confirmed" covers the measured scope only: two players, both JOAT or one
of WM, CA, SS or JOAT+NAS against JOAT, one year each, with stationary
viewers (SC-027 measured moving targets' headings).

## Conventions

- Positions are integer light-year coordinates. `d²` is the squared
  distance `dx² + dy²` between two objects, an integer.
- Every range test compares integers: `d² ≤ R²`. A target 50.01 ly from a
  50 ly scanner is not seen (CONFIRMED, SC-001).
- Divisions truncate. `⌊x⌋` is used where the order of truncations
  matters.
- `rand(n)` is a uniform draw in `0..n−1` from the game's generator. Only
  two rules here draw random numbers (population estimates and Space Demolition
  minefield detection); everything else is deterministic.

## When knowledge is computed (BINARY-ONLY)

Each player's knowledge is computed once per year, after every other part
of the year is finished (movement, battles, production, mine sweeping,
repair), from the final positions, current tech levels, current cargo and
current designs. Each player is evaluated on its own; no player's view
depends on another player's view, except through the mine-field and
wormhole knowledge carried between years (below).

A player always knows everything about its own planets, fleets, designs and
race. A player knows another player exists (name, and the race data
described under Disclosure) once it sees any of that player's planets,
fleets, starbases, minefields or packets, or receives a message from them
(CONFIRMED for minefields and packets, OB-011, OB-018).

## Scanner ranges

Every scanner has a **normal** range `R` and a **penetrating** range `P`
(0 for non-penetrating scanners).

### Ship designs

- **Scanner parts (CONFIRMED, SC-001, SC-008).** Each scanner part has a
  normal and a penetrating range (components table). A Bat Scanner has
  range 0; it sees only its own position.
- **Several scanners on one design (CONFIRMED, SC-001).** Ranges combine as
  `⌊⁴√Σ rᵢ⁴⌋` over every scanner on the design, counting each part in a
  stack. Normal and penetrating ranges are combined separately. Vector: two
  Rhino Scanners (50 each) give 59.
- **Built-in scanners.** Three non-scanner parts also scan, combining like
  scanner parts: Mega Poly Shell, Multi Contained Munition and Langston
  Shell (components table). CONFIRMED for Mega Poly Shell (80 / 40) and
  Multi Contained Munition (150 / 75) by designer readouts (CS-003-D);
  BINARY-ONLY for Langston Shell.
- **JOAT hulls (CONFIRMED, SC-020, SC-022, SC-023).** A JOAT player's
  Scout, Frigate and Destroyer have a built-in scanner of `20·E` normal and
  `10·E` penetrating, where `E` is the owner's electronics level. It
  combines with scanner parts like S-2. Vectors at E = 10: no scanner part
  gives 200 / 100; with a Possum Scanner 214 normal. At E = 16 with an
  Elephant Scanner: penetrating 217. BINARY-ONLY: in a tutorial game the
  built-in is fixed at 40 / 20.
- **No scanner (CONFIRMED, SC-002, SC-014).** A design with no scanner part
  and no built-in scanner is blind: it sees only what shares its exact
  position (see Co-location).
- **No Advanced Scanners, NAS (CONFIRMED, SC-017..SC-019).** Ship normal
  ranges double after combining. Ship penetrating ranges are unchanged.

### Fleets

- **Best design (CONFIRMED, SC-001).** A fleet's normal range is the
  largest normal range among its designs, and its penetrating range the
  largest penetrating range. Stacks and different designs do not combine:
  a fleet of two Rhino ships, or of two different Rhino designs, still
  scans 50.
- **Tachyon detectors (CONFIRMED for 0 to 3 on one design, SC-010,
  SC-028, SC-033; BINARY-ONLY beyond 3).** The number of Tachyon Detectors on a design
  (summed over its slots, not multiplied by ship count) selects a factor
  `T` from this table (index = count, capped at 17):

  `100, 95, 93, 91, 90, 89, 88, 87, 86, 86, 85, 84, 84, 83, 83, 82, 82, 81`

  Against this fleet a target's cloak `c` becomes `⌊c·T/100⌋`. Vector: a
  75% cloak is 71% against one detector and 69% against two (SC-010), and
  68% against three (factor 91: seen at d² 27688, not at 27689, SC-033).
  A fleet uses the smallest factor among its designs, so detectors on
  different designs or ships do not add up (CONFIRMED, SC-029): a fleet of
  two one-detector ships, or a one-detector design with another
  one-detector design, is 95; a two-detector design with a one-detector
  design is 93.

### Planets

- **Best scanner by tech (CONFIRMED, SC-011..SC-013).** A planet that has a
  scanner scans with the best planetary scanner its owner's current tech
  allows, whatever scanner was built there. Raising tech upgrades every
  scanner-equipped planet that same year. Vectors: electronics 5 → 150 ly,
  electronics 6 → 220.
- **Penetrating planetary scanners (CONFIRMED, SC-013).** A penetrating
  planetary scanner of range `S` has `R = S` and `P = trunc(S/2)`. Vector:
  320 / 160.
- **No scanner (CONFIRMED by every SC run that removed one).** A planet
  without a planetary scanner does not scan.
- **NAS (CONFIRMED, SC-019).** The best non-penetrating planetary scanner is
  used, and its range doubles. No penetration.
- **Alternate Reality (BINARY-ONLY).** AR planets scan from population
  instead of a planetary scanner: `R = trunc(√(pop/10))` for pop in
  colonists (250,000 → 158), times 1.412 (truncated) under NAS. `P = R/2`
  only when the planet's starbase is an Ultra Station or a Death Star, and
  0 under NAS.
- Tachyon detectors never apply to planet scanners.

## Seeing fleets

A viewer object (a fleet or a planet) with ranges `R`, `P` sees another
player's fleet at squared distance `d²` when all of these hold
(CONFIRMED, SC-001..SC-010):

1. `d² ≤ R²`.
2. If the target is in orbit around a planet: also `d² ≤ P²`. A
   non-penetrating scanner never sees an orbiting fleet except at its own
   position.
3. If the target has cloak `c > 0` (after any tachyon reduction):
   `d² ≤ ⌊⌊(100−c)·R²/100⌋·(100−c)/100⌋`, and for an orbiting target the
   same bound with `P²`.

The viewer sees the fleet if any one of its fleets or planets does.

Vectors (R = 50): cloak 35% → seen to d² 1056 (32.5 ly), 17% → 1722,
10% → 2025. R = 59 (two Rhinos): 26% seen at d² 1905, not 1906. Shrinking the range
first (`⌊R·(100−c)/100⌋`, then squaring) gives different answers and is
ruled out (SC-001 cases at d² 1053, 1721, 505, 153, 53).

**Co-location (CONFIRMED, SC-002, SC-014; LEGACY BUG).** At `d² = 0` every
test passes. A fleet at exactly the same position as an enemy fleet sees
it whatever its own scanner (none included) and whatever the target's
cloak (98% included), and is seen back. One ly away a blind or Bat
Scanner viewer sees nothing. This looks like a consequence of the distance
test rather than a designed rule.

**Fleets at your planets (CONFIRMED, SC-024, SC-026).** Every enemy fleet in
orbit around one of the viewer's planets is seen, whatever its cloak and
whether or not the planet has a scanner, and with no viewer fleet present.
Vectors: a 98% cloaked fleet at the viewer's homeworld and a plain
freighter at a colony without a starbase were seen; the same designs 1 ly
away in deep space were not. A fleet at the planet's exact position that
was not in orbit was also seen (SC-024-E, one case), which is the
co-location rule above.

## Cloaking

### Fleet cloak (CONFIRMED, SC-001, SC-010)

1. Each ship design has **cloak points**: the sum over its parts of
   each part's cloak points times the stack count (components table).
   Cloaking devices carry points, and so do some other parts. CONFIRMED by
   designer readouts (CS-003-D) for Enigma Pulsar (20), Alien Miner (60),
   Mega Poly Shell (40) and Multi Contained Munition (20), and by detection
   edges for Langston Shell (20 per shell, SC-034: one shell on a Small
   Freighter is 10%, five on a Super Freighter 50%); BINARY-ONLY for
   Depleted Neutronium, Chameleon Scanner, Shadow Shield, Orbital Adjuster
   and Multi Cargo Pod. Super Stealth (SS) players add 300
   points to every design (CONFIRMED, SC-030: a plain SS freighter is 75%,
   seen at d² 5625 and not at 5626 by a 100 ly scanner).
2. The fleet's points are mass-weighted:
   `u = trunc(Σ (points × stack mass) / (Σ stack mass + cargo))`, where a
   stack's mass is ship mass times ship count and cargo is the fleet's
   ironium, boranium, germanium and colonists. Fuel is never counted. For
   an SS fleet cargo is left out (CONFIRMED, SC-030: the SS freighter with
   50 kT of cargo was still 75%, where dilution would give 51%).
3. Percent from points:

   | Points `u` | Cloak % |
   |---|---|
   | 0–100 | `trunc(u/2)` |
   | 101–300 | `50 + trunc((u−100)/8)` |
   | 301–612 | `75 + trunc((u−300)/24)` |
   | 613–1124 | `88 + trunc((u−612)/64)` |
   | 1125–1379 | 96 |
   | 1380–1611 | 97 |
   | 1612 and up | 98 |

Vectors: one Stealth Cloak (70 points) on a 31 kT Small Freighter is 35%
empty, 17% with 31 kT of cargo, 10% with 70 kT; 130 mg of fuel leaves it at
35%. A Stealth freighter and an uncloaked one in one fleet are 18%, not
35%.

### Starbase cloak

- A planet inside a viewer's penetrating range is reported **without its
  starbase** (no starbase, no starbase design) when
  `d² > ⌊(100−c)²·P²/10000⌋`, where `c` is the starbase's cloak
  (CONFIRMED, SC-009). Vectors with P = 100: one Stealth Cloak (35%):
  starbase shown at d² 4225, hidden at 4226; two (55%): shown at 2025,
  hidden at 2026.
- A starbase's cloak uses its design's points **without mass weighting**
  (CONFIRMED, SC-009, for cloaking devices), plus 40 points for an
  Improved Starbases player on any starbase hull (BINARY-ONLY) and 300 for
  SS (CONFIRMED, SC-030: an SS player's bare Space Station is 75%, so a
  viewer with P 200 at d² 3600 got the planet without its starbase). A
  point total above 25,000 counts as 0 (BINARY-ONLY).
- The planet itself is still reported; only the starbase is hidden.

## Seeing planets

- **Only penetrating range reveals planets (CONFIRMED, SC-003..SC-008).** A
  planet is reported when `d² ≤ P²` from a viewer's fleet or planet.
  Normal range alone never reports a planet, at any distance.
- **Penetration needs `P > 0` (BINARY-ONLY rule; its consequence is
  CONFIRMED, SC-002 `SC002-blind-orbit`).** A fleet or planet with `P = 0`
  reveals no planets at all, even the planet it orbits at `d² = 0`. The only
  reports a `P = 0` fleet gets of its orbited planet are the orbit report
  and the bombing check below.
- **Orbiting (CONFIRMED, SC-002, SC-014, SC-032).** A planet orbited by one
  of the viewer's fleets is reported: position only if that fleet has no
  scanner, a normal report if it has any scanner (Bat Scanner included), a
  detailed report with a Robber Baron Scanner. A scannerless fleet can
  still get a normal report from the bombing check.
- **Bombing check (CONFIRMED for scannerless fleets without bombs, SC-024,
  SC-031, SC-032; mechanism BINARY-ONLY).** When the viewer would bomb a
  planet by the "Who bombs" test in `TAKEOVER.md` (another player owns it,
  it has no starbase, and one of the viewer's fleets in orbit has a battle
  plan that attacks the owner), the planet gets a normal report, whatever
  the viewer's scanners and whether or not any fleet carries bombs.
  Measured with default plans and relations: a blind freighter got a
  normal report (environment, population and defense estimates, no
  surface minerals) at an enemy colony without a starbase and at an enemy
  homeworld whose starbase was removed, and position only at an enemy
  colony with a starbase and at an unowned planet. So the starbase decides,
  not the homeworld. BINARY-ONLY: a battle plan that would not attack the
  owner (for example "nobody") gives only the orbit report.
  **When it is decided (CONFIRMED, SC-035).** The test is made at the bombing
  step, right after battles, against the state at that moment: the planet
  is owned by another player (not unowned) and has no starbase, and the
  viewer's fleet orbits it with a plan that attacks that owner. The report
  itself is the ordinary end-of-year report, written from the planet as it
  stands at the end of the year, provided the fleet is still in orbit. So
  the two can differ when the planet changes between bombing and the end
  of the year. The case that matters: bombing that kills the last colonists
  leaves the planet unowned, and the viewer still gets a normal report of
  it, where an end-of-year test would give the orbit report only.
  SC-035 (stars-elegy #61, two streams): two scannerless bombers killed
  the 100 colonists of an enemy planet with no starbase. The planet ended
  the year unowned, and the viewer got a normal report of it (environment
  and the unowned state). Bombers orbiting a planet unowned from the start
  got position only. A first setup, on a planet outside the colonists'
  habitat, gave position only at both planets; that fits the rule if, as
  inferred, the colonists died in population growth (`KERNEL.md` "Turn
  order", step 4), before the bombing step.
- **Remote miners (BINARY-ONLY).** A stationary fleet remote-mining an
  unowned planet that yields minerals gets a detailed report of it.
- **Interstellar Traveler through gates, IT (CONFIRMED, OB-013).** From
  each own planet whose starbase has a stargate, an IT player gets a normal
  report of every planet whose starbase has any stargate within that
  gate's range. A gate with unlimited range reaches every such planet. The
  starbase cloak rule still applies (BINARY-ONLY). Vectors from a range-250
  gate: a gated enemy planet at 75 ly was reported, one at 259 ly was not,
  and a starbase without a gate at 138 ly was not.
- **Battles (CONFIRMED, SC-032).** Fighting at a planet gives the same
  report as being there without fighting: a scannerless fleet that fought
  at an unowned planet, and one that fought at an enemy colony with a
  starbase, each got position only. A battle at a planet always gives each
  participant at least a position-only report of it (BINARY-ONLY; it
  matters only for a fleet that did not end the year in orbit).
- **Left out of a battle or hit by mines (BINARY-ONLY).** A fleet in orbit
  that was left out of a battle there because of the battle's size limit,
  or that was hit by a detonating minefield, gives a normal report of the
  planet it orbits.
- **Lost planets (BINARY-ONLY).** A planet the viewer lost this year, or one
  named in certain loss and invasion messages, gets a normal report.

### What a planet report contains

| Report | Contents |
|---|---|
| Own planet | everything |
| Position only | position, name, owner, whether it is a homeworld, whether it has a starbase, and that starbase's design (partial) |
| Normal | owner, environment (current and original), mineral concentrations, whether it is a homeworld, has a starbase (and its design, see Disclosure) or an artifact, was terraformed; for an owned planet, estimated population and defense coverage |
| Detailed | normal, plus surface minerals |

(BINARY-ONLY for the field list; CONFIRMED for which planets get which
report in SC-001..SC-033.)

**Starbases in every report (CONFIRMED, SC-024..SC-026).** The starbase
rule above is the only thing that hides a starbase. Every report of a
planet, including the position-only report from a scannerless fleet in
orbit, says whether it has a starbase and sends that starbase's design
(partially). The orbiting fleet makes the planet's owner a known player:
a blind freighter at an enemy homeworld with a starbase got position only
with the starbase and its partial design, and the owner's player data
arrived although nothing else of that player was seen.

**Population estimate (range CONFIRMED, SC-024..SC-033: all 9 estimates
fell in it, 300 colonists → 400 included; the draw itself is random).** Once a
year each planet with population gets one estimate, shared by every viewer
that year. The estimates are drawn after battles, production, mine
sweeping, repair, terraforming and the duplicate-serial penalty, and before
the year advances and knowledge is computed. So every battle draw of the
year comes before them, and the Space Demolition detection draws come after.
Planets are processed in id order:

`estimate = 400 × max(1, min(4090, trunc((u + rand(trunc(u/4)) − trunc(u/8)) / 4)))`

where `u` is the population in units of 100 colonists. That is the true
population within about −12.5%..+12.5%, rounded down to a multiple of 400.

- `rand(0)` (when `u < 4`) still consumes one draw from the generator and
  yields 0. Every planet with population draws exactly once.
- A planet with no population draws nothing. An AR-owned planet draws
  nothing.
An uninhabited planet shows none. AR planets report an estimate of 0.

**Defense coverage estimate (CONFIRMED, SC-024..SC-033, 9 planets).**
Computed at the same time, with no random draw:

1. A planet with no defenses gets 0 ("none").
2. Otherwise take the best planetary defense the owner's current tech
   allows (its coverage `v` per defense, in tenths of a percent;
   components table) and `n` = the planet's defenses, capped at the number
   the planet can operate (`KERNEL.md`, Caps, "operable defenses", the
   same cap bombing uses).
3. `s = (1 − v/1000)ⁿ`, the share of a bomb's kill that gets through, in
   floating point.
4. `k = trunc(100·s + 0.5)`.
5. `estimate = max(1, min(15, trunc((104 − k)/6)))`.

Vectors with Neutron Shields (`v = 38`): 1, 3, 5 and 10 defenses give 1,
2, 3 and 6; 40 defenses on a planet that can operate 10 give 6; 100
defenses with population 104,400 (42 operable) give 14. Without the cap
the last two would be 13 and 15.

If the owner has no defense type available, `s = 1` and the estimate is 1.
Each step is about 6% of coverage. How the client words a step is
unknown.

**Old reports (BINARY-ONLY; a client feature).** A player's client keeps
the best report of each planet it has ever received, with the year of the
report. A newer report replaces the fields it contains and leaves the rest
(for example old surface minerals) as they were. The host does not use
this history.

## Space objects (CONFIRMED, OB-011..OB-014, OB-017, OB-018)

This file owns these visibility rules. `OBJECTS.md` covers how the objects
behave (laying, decay, hits, jumps, packet flight). Evidence is in
`PARITY.md`, "Scanning", "Universe objects". `R` and `P` are the viewer
fleet's or planet's ranges.

- **Minefields.**
  - A player's own minefields are always known.
  - Another player's minefield is seen when `d² ≤ P²`, or
    `d² ≤ ⌊R²/16⌋` (a quarter of normal range), or the viewing fleet is
    inside the field, whatever its distance to the centre (BINARY-ONLY:
    planets do not get this inside rule). Rhino (R 50): 12 ly seen, 13 not (OB-018); inside
    at 30 ly from the centre seen (OB-018-C).
  - A minefield the player already **knows** is seen within the full normal
    range `d² ≤ R²` (OB-018 E–G: 50 ly seen, 51 not). A player knows a field
    once it has seen it, been hit by it or swept it, and keeps knowing it in
    later years (BINARY-ONLY for hits and sweeps).
  - Whether a field was seen is recomputed every year.
- **Wormholes.** Never seen beyond `R` (`d² > R²`), even when the player
  already knows the wormhole (OB-011-H). Within `R`, one is seen when it is
  already known, or `d² ≤ P²`, or `d² ≤ ⌊R²/16⌋` (OB-018 H, I; OB-017 A, B).
  BINARY-ONLY: the "already known" case covers the band between `R/4` and
  `R` without penetration. A wormhole is known once seen, and every player
  forgets it when it jumps. The penetrating branch is CONFIRMED for ends
  that had just jumped and so were unknown (WT batch, O-44, stars-elegy
  #55): 4 of 18 jumped ends were seen again that year by a newly received
  M.T. ship, at 21, 27, 72 and 107 ly, within its penetrating range (about
  33 ly for an M.T. Scout, 132 ly for a Lifeboat) and beyond `R/4`; an end
  52 ly from an M.T. Scout, beyond both, was not seen. This matches the
  binary reading above, which already includes `d² ≤ P²`.
- **Mineral packets.** Seen within `R` (about 48 ly seen and 53 not with
  R 50; OB-018 J, K). A Packet Physics (PP) player sees every packet in the
  universe (OB-012).
- **Mystery Trader.** In every player's view while it exists, at any
  distance (OB-011-J, 69 ly or more from any scanner).
- **Owners become known.** Seeing another player's minefield or packet makes
  that player known: its player data (Disclosure, Players) is sent even when
  none of its planets or fleets is seen (OB-011, OB-018). Wormholes and the
  Trader have no owner, so seeing only those makes nobody known (OB-017).
- **PP packet scanners.** Each of a PP player's own packets in flight scans
  as a penetrating scanner (`R = P = warp²` ly). It sees fleets (orbiting
  ones too, with the cloak rule), space objects and planets. A warp-5
  packet saw a fleet and a minefield at 20 ly and missed both at 30
  (OB-012).
- **Space Demolition (SD) minefields.** Each of an SD player's own
  minefields sees every enemy fleet inside it that is not orbiting a planet
  (OB-014-B: the deep-space scout inside the field was seen; one orbiting a
  planet inside the field and one far away were not). A cloaked fleet is
  seen only when `rand(100) ≥ c` (BINARY-ONLY; one random draw per cloaked
  fleet considered).

## Disclosure: what each sighting reveals

### Fleets

| Sighting | Revealed |
|---|---|
| Normal | owner, position, ship designs and counts, heading and warp (not the destination), total mass |
| With cargo (Pick Pocket or Robber Baron at the same position) | normal, plus ironium, boranium and germanium carried |
| Own | everything |

- Pick Pocket and Robber Baron viewers see the cargo of an enemy fleet at
  their exact position. 30 ly away, or with a Rhino at the same position,
  the fleet arrives without cargo (CONFIRMED, SC-002, SC-014).
- The mass shown is ship mass plus ironium, boranium, germanium and
  colonists, without fuel (CONFIRMED, SC-027): an empty 29 kT ship shows
  29; with 10/20/30 kT of minerals and 40 kT of colonists, 129; two ships
  with 50 kT of colonists, 108. The cargo itself shows as 0.
- BINARY-ONLY: colonists and fuel are never shown to another player.
- **Heading (CONFIRMED, SC-027, for straight moves; BINARY-ONLY for
  chasers).**
  - A fleet that moved this year shows a heading vector and the warp of
    its next waypoint.
  - The vector is the next waypoint minus the fleet's position just
    before it moved. For a chaser this uses the target's position at that
    step, and the last movement step of the year wins.
  - While either component has magnitude ≥ 128, both are halved,
    truncating toward zero. The result fits in −127..127.
  - It is not reduced by a gcd. Vectors: (300, 100) → (75, 25);
    (50, −120) unchanged; (−128, 3) → (−64, 1); (300, −7) → (75, −1);
    (−1, −395) → (0, −98). Halving toward −∞ would give (75, −2) and
    (−1, −99).
  - A fleet that reached its waypoint this year still shows the vector and
    warp of the move it finished (one case: (10, 0) at warp 5).
  - A fleet that did not move this year shows no heading and no warp
    (heading 0, 0 and warp 0).
  - Fleets travelling by stargate were not read.

### Designs

- A seen ship or starbase reveals its design **partially**: hull and mass
  (CONFIRMED, SC-001..SC-023).
- A **War Monger** viewer gets every seen design in full (CONFIRMED,
  SC-015, SC-015L).
- A design is disclosed in full to every player whose forces fought it in
  a battle, even when every ship of it was destroyed (CONFIRMED, SC-031).
  "Fought it" means took part in the same battle, whatever the sides
  (CONFIRMED for allies, SC-036): each player in a battle gets, in full, the
  design of every ship stack and starbase of every other player in that
  battle's record, a friend on the same side included. Each other player
  in the battle also becomes a known player. SC-036 (stars-elegy #61, two
  streams, three players, 0 and 1 friends, 2 an enemy of both, one
  Destroyer each, no scanners): after the battle each player's file held
  both other players' designs in full and a player block for each.
  BINARY-ONLY: also to the owner of an SD minefield it struck, and
  (starbases) to a PP player whose packet that starbase caught.
- A planet report without its starbase (starbase cloak) reveals no
  starbase design.

### Players

- Another known player is identified by name only (CONFIRMED, SC corpus).
- Taking part in a battle makes every other player in it known, allies
  included (CONFIRMED, SC-036; see Designs).
- A **Claim Adjuster** viewer also receives each known player's
  habitability ranges, with every tech level shown as zero. With no contact
  it receives nothing about the other player (CONFIRMED, SC-016, SC-016N).
- Scores of other players are in a player's file when public scores are
  enabled and the file's year index is at least 20, i.e. from 2420 on
  (CONFIRMED, KX-004; `KERNEL.md` "Game options during a turn").

### Allies (CONFIRMED in one run, SC-001F)

Relations do not affect scanning. Allies (friends) do not share scanner
coverage or reports. Both players' views with mutual friend relations
were identical to the same run with enemy relations.

## Orders that depend on sight (BINARY-ONLY)

While knowledge is computed, a fleet whose waypoint is another fleet it
can no longer see is retargeted: to the planet that fleet entered orbit at,
or else to its last known position. The player gets a message saying the
target was destroyed, entered orbit, or outran the scanners. A waypoint on
a wormhole, minefield or the Mystery Trader that no longer exists is
dropped with a message. A fleet patrolling (single waypoint, patrol task)
picks the nearest visible enemy fleet it can attack within
`(patrol warp + 1) × 50` ly, or at any distance for the "any" setting.

## Open experiments

1. A known wormhole between `R/4` and `R` with no penetration (seen), and
   an unknown one at the same distance (not seen).
2. Minefield knowledge gained from being hit or sweeping.
3. Space Demolition detection of cloaked fleets and the population estimate (random;
   inject the generator in tests; repeated oracle runs are not
   independent).
4. Alternate Reality planet scanners.
5. Chase retargeting and patrol target choice.
6. Planet reports from the bombing check with a fleet that carries bombs,
   or with a battle plan that attacks nobody; after a detonating minefield
   hit or a battle's size limit; and after a planet is lost.
7. The Langston Shell built-in scanner; cloak points of the non-device
   parts not yet confirmed (Depleted Neutronium, Chameleon Scanner, Shadow
   Shield, Orbital Adjuster, Multi Cargo Pod); Improved
   Starbases (ISB) starbase cloak bonus.
8. Four or more tachyon detectors on one design.
9. Design disclosure after SD mine hits and PP packet catches.
10. Three or more players, and scanners on moving fleets mid-year.
11. Headings of chasers and of fleets travelling by stargate.
12. Done: SC-035 (bombing check at the bombing step) and SC-036 (allies
   in a battle) are CONFIRMED (stars-elegy #61).

## Notes for comparing with original-game files

These describe how the original's per-player turn file stores some of the
facts above. They are not rules; they matter only to a tool that compares
an Elegy view with an oracle view (MEASURED, SC-027, SC-031).

- A heading component is stored as one byte holding `value + 127`. A
  fleet that did not move stores 0 for both components and warp 0, and is
  read as "no heading".
- Another player's design records carry no owner field. Their owners
  follow from the order of the records, which are grouped by owner in
  player order.

## Sources

- Oracle: SC-001..SC-034 (`PARITY.md`, "Scanning", including "Round 4"; `experiments/sc/`;
  `ORACLE.md`, "Scanning experiments"). Raw evidence: private
  `stars-oracle-apparatus`, `evidence/sc/`.
- White-box reading: private `stars-decomp` (scanning notes and the
  per-player view checker that reproduces every SC and CB view).
