# Scanning specification: what each player learns each year

Behavioral specification of the J-RC3 rules that decide what each player
knows at the end of a year: scanner ranges, penetration, cloaking,
tachyon detectors, starbases, planet scanners, race-specific disclosure,
allies, and how much detail each kind of sighting reveals. It is written
for an implementer working only from this public repository. It describes
what a player is told, not how any file encodes it.

`PARITY.md`, section "Scanning", holds the experiment records (SC-001 to
SC-023). This file restates them as rules and adds rules that so far come
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
of WM, CA or JOAT+NAS against JOAT, stationary fleets, one year each.

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
fleets, starbases or minefields, or receives a message from them.

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
- **Built-in scanners (BINARY-ONLY).** Three non-scanner parts also scan,
  combining like scanner parts: Mega Poly Shell, Multi Contained Munition
  and Langston Shell (components table).
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
- **Tachyon detectors (CONFIRMED for 0, 1 and 2 on a one-design fleet;
  BINARY-ONLY beyond).** The number of Tachyon Detectors on a design
  (summed over its slots, not multiplied by ship count) selects a factor
  `T` from this table (index = count, capped at 17):

  `100, 95, 93, 91, 90, 89, 88, 87, 86, 86, 85, 84, 84, 83, 83, 82, 82, 81`

  Against this fleet a target's cloak `c` becomes `⌊c·T/100⌋`. Vector: a
  75% cloak is 71% against one detector and 69% against two (SC-010).
  BINARY-ONLY: a fleet uses the smallest factor among its designs, so
  detectors on different designs or ships do not add up.

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

**Fleets at your planets (BINARY-ONLY).** Every enemy fleet in orbit around
one of the viewer's planets is seen, whatever its cloak and whether or not
the planet has a scanner.

## Cloaking

### Fleet cloak (CONFIRMED, SC-001, SC-010)

1. Each ship design has **cloak points**: the sum over its parts of
   each part's cloak points times the stack count (components table).
   Cloaking devices carry points, and so do some other parts
   (BINARY-ONLY for the non-device parts: Depleted Neutronium, Mega Poly
   Shell, Enigma Pulsar, Chameleon Scanner, Shadow Shield, Langston Shell,
   Multi Contained Munition, Alien Miner, Orbital Adjuster, Multi Cargo
   Pod). Super Stealth (SS) players add 300 points to every design
   (BINARY-ONLY).
2. The fleet's points are mass-weighted:
   `u = trunc(Σ (points × stack mass) / (Σ stack mass + cargo))`, where a
   stack's mass is ship mass times ship count and cargo is the fleet's
   ironium, boranium, germanium and colonists. Fuel is never counted. For
   an SS fleet cargo is left out (BINARY-ONLY).
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
  Improved Starbases player on any starbase hull and 300 for SS
  (BINARY-ONLY). A point total above 25,000 counts as 0 (BINARY-ONLY).
- The planet itself is still reported; only the starbase is hidden.

## Seeing planets

- **Only penetrating range reveals planets (CONFIRMED, SC-003..SC-008).** A
  planet is reported when `d² ≤ P²` from a viewer's fleet or planet.
  Normal range alone never reports a planet, at any distance.
- **Orbiting (CONFIRMED, SC-002, SC-014).** A planet orbited by one of the
  viewer's fleets is reported: position only if that fleet has no scanner,
  a normal report if it has any scanner (Bat Scanner included), a detailed
  report with a Robber Baron Scanner.
- **Remote miners (BINARY-ONLY).** A stationary fleet remote-mining an
  unowned planet that yields minerals gets a detailed report of it.
- **Interstellar Traveler through gates, IT (BINARY-ONLY).** An IT player's planets
  with stargates report every planet with a stargate within the gate's
  range (unlimited range gates reach every such planet), subject to the
  starbase cloak rule.
- **Battles and bombing (BINARY-ONLY, unclear).** A fleet that bombed,
  fought or hit a minefield at a planet this year gives a normal report of
  that planet.
- **Lost planets (BINARY-ONLY).** A planet the viewer lost this year, or one
  named in certain loss and invasion messages, gets a normal report.

### What a planet report contains

| Report | Contents |
|---|---|
| Own planet | everything |
| Position only | position and name |
| Normal | owner, environment (current and original), mineral concentrations, whether it is a homeworld, has a starbase (and its design, see Disclosure) or an artifact, was terraformed; for an owned planet, estimated population and defense coverage |
| Detailed | normal, plus surface minerals |

(BINARY-ONLY for the field list; CONFIRMED for which planets get which
report in SC-001..SC-023.)

**Population estimate (BINARY-ONLY; a private check found all 131
estimates in the preserved single-player games inside this range).** Once a year, after growth, each owned planet gets one estimate,
shared by every viewer that year:

`estimate = 400 × max(1, min(4090, trunc((u + rand(trunc(u/4)) − trunc(u/8)) / 4)))`

where `u` is the population in units of 100 colonists. That is the true
population within about −12.5%..+12.5%, rounded down to a multiple of 400.
An uninhabited planet shows none. AR planets report an estimate of 0. A coarse
defense coverage estimate (16 steps) accompanies it.

**Old reports (BINARY-ONLY; a client feature).** A player's client keeps
the best report of each planet it has ever received, with the year of the
report. A newer report replaces the fields it contains and leaves the rest
(for example old surface minerals) as they were. The host does not use
this history.

## Space objects (BINARY-ONLY)

- **Minefields.** A player's own minefields are always known. An enemy
  minefield is seen from a fleet or planet when `d² ≤ P²`, or
  `d² ≤ ⌊R²/16⌋` (a quarter of normal range), or, for a fleet only, when
  the fleet is inside the field. A minefield the player has seen before is
  seen again within the full normal range. A minefield's owner becomes a
  known player.
- **Wormholes.** An unknown wormhole is seen within `P` or a quarter of `R`. A persistent known-bit is kept after discovery; the binary-derived model predicts that a known wormhole is seen again within full normal range. This persistence/range rule is BINARY-ONLY.
- **Mineral packets.** Seen within `R`. A Packet Physics (PP) player knows
  every packet in the universe.
- **Mystery Trader.** Known to every player while it exists, at any
  distance.
- **PP packet scanners.** A PP player's own moving packets scan as
  penetrating scanners with range warp² ly (warp 10 → 100), seeing fleets
  (with the cloak rule), space objects and planets.
- **Space Demolition minefields.** An SD player's minefields detect any
  non-orbiting enemy fleet inside them: an uncloaked fleet always, a
  cloaked one when `rand(100) ≥ c`.

## Disclosure: what each sighting reveals

### Fleets

| Sighting | Revealed |
|---|---|
| Normal | owner, position, ship designs and counts, direction of travel and warp (not the destination), total mass |
| With cargo (Pick Pocket or Robber Baron at the same position) | normal, plus ironium, boranium and germanium carried |
| Own | everything |

- Pick Pocket and Robber Baron viewers see the cargo of an enemy fleet at
  their exact position. 30 ly away, or with a Rhino at the same position,
  the fleet arrives without cargo (CONFIRMED, SC-002, SC-014).
- The mass shown is ship mass plus ironium, boranium, germanium and
  colonists, without fuel (BINARY-ONLY here; a private check matched every
  partial fleet in the CB combat corpus, not yet recorded in `PARITY.md`).
- BINARY-ONLY: colonists and fuel are never shown to another player.

### Designs

- A seen ship or starbase reveals its design **partially**: hull and mass
  (CONFIRMED, SC-001..SC-023).
- A **War Monger** viewer gets every seen design in full (CONFIRMED,
  SC-015, SC-015L).
- BINARY-ONLY: a design is also disclosed in full to every player whose
  forces fought it in a battle, to the owner of an SD minefield it struck,
  and (starbases) to a PP player whose packet that starbase caught.
- A planet report without its starbase (starbase cloak) reveals no
  starbase design.

### Players

- Another known player is identified by name only (CONFIRMED, SC corpus).
- A **Claim Adjuster** viewer also receives each known player's
  habitability ranges, with every tech level shown as zero. With no contact
  it receives nothing about the other player (CONFIRMED, SC-016, SC-016N).
- BINARY-ONLY: scores of other players are shown when public scores are
  enabled and more than 20 years have passed.

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

1. Minefields, wormholes, packets and the Mystery Trader: the quarter-range
   rule, the inside-the-field rule, persistent knowledge, PP sees all
   packets, MT seen by everyone (needs a universe with these objects).
2. PP packet scanners and the IT gate scan.
3. Space Demolition minefield detection and the population estimate (random;
   inject the generator in tests; repeated oracle runs are not
   independent).
4. Alternate Reality planet scanners.
5. Chase retargeting and patrol target choice.
6. Planet reports after battle, bombing or minefield hits, and after a
   planet is lost.
7. Built-in scanners in Mega Poly Shell, Multi Contained Munition and
   Langston Shell; cloak points of non-device parts; SS cloak; Improved Starbases (ISB) starbase
   cloak bonus.
8. More than two tachyon detectors; tachyon detectors spread over several
   designs.
9. Design disclosure after battle, SD mine hits and PP packet catches.
10. Three or more players, and scanners on moving fleets mid-year (all SC
    runs were stationary).

## Sources

- Oracle: SC-001..SC-023 (`PARITY.md`, "Scanning"; `experiments/sc/`;
  `ORACLE.md`, "Scanning experiments"). Raw evidence: private
  `stars-oracle-apparatus`, `evidence/sc/`.
- Partial-fleet mass and population estimates were also checked privately
  against the CB combat corpus and the preserved single-player games; these
  checks are not yet public records.
- White-box reading: private `stars-decomp` (scanning notes and the
  per-player view checker that reproduces every SC and CB view).
