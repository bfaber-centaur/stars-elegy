# Kernel specification: peaceful economy and fleet movement

Behavioral specification of the J-RC3 rules an independent implementation
needs for a peaceful single-player turn and for ordinary fleet movement:
habitability, population, resources, installation caps, mining, research,
production, movement and fuel. It is written for an implementer working
only from this public repository.

`PARITY.md` holds the experiment records these rules come from. This file
restates them as rules with test vectors and adds rules that so far come
only from white-box analysis of the original program (private
`stars-decomp`, promoted here as behavior only).

## Status of each rule

Every rule carries one status:

- **CONFIRMED**: a white-box reading agrees with original-game oracle
  observations. The test vectors given for it are ground truth.
- **ORACLE**: measured in the original game but not yet matched to a
  white-box reading.
- **BINARY-ONLY**: read from the original program's arithmetic, with no
  oracle observation yet. Vectors are worked from the rule, not observed.
  Expect most of these to hold, but treat them as predictions: they are
  listed for oracle testing.

"Confirmed" covers the measured scope only (race, habitability, cases).
Each rule says what that scope was.

## Conventions

- Integers. Every division truncates toward zero (`trunc`). Where the
  operands can be negative this is said explicitly; it differs from floor.
- Population is held in **units of 100 colonists** ("units"). 1,000,000
  colonists = 10,000 units.
- Percentages are integers (hab 100 = 100%).
- `rand(n)` is a uniform draw in `0..n−1` from the game's random generator.
  The oracle restarts the game for each generated year, which makes random
  draws nearly identical from year to year (`ORACLE.md`). Random outcomes in
  the oracle corpus are therefore correlated, not independent samples.
  Tests of random rules should inject the generator.

## Turn order

This is the authoritative, ordered list of everything the host does when it
generates one year. The list comes from reading the original's generation
routine from start to end (private `stars-decomp`, `turn.md`). Each step
names the specification that owns its rules, or says **uncovered** if no
public specification owns it yet.

Two tags appear on each step. The step's own rules carry their usual tags
in the owning specification. The **Order** tag says how well the step's
**place in the sequence** is known:

- **CONFIRMED** means an oracle run separated this step from its
  neighbour and matched this order (the run is named).
- **BINARY-ONLY** means the order was read from the program and no run has
  yet distinguished it.

Top-level step numbers 1–8 and the letter sub-steps are the phase labels
`MESSAGES.md` uses (P1, P1a, …). Numbered items inside a step run in the
order shown. "Fleet order" means by owner, then by fleet number
(`TAKEOVER.md`, "Order inside a phase").

### 1. Orders

1. The game is loaded. The random generator is reseeded only in tutorial
   mode, so generation otherwise continues the stream it was started with.
2. **Player order.** The players are shuffled. For each position `i` from
   the first to the last, the host draws `Random(n − i)` (`n` players) and
   swaps position `i` with position `i +` the draw. That is one draw per
   player, the last of them always 0, and they are the first draws of the
   year. CONFIRMED as two draws before mining for two players (KX-004,
   KB-1C, KB-3A: every replay matched only with these two draws first).
   The permutation itself is BINARY-ONLY. With orders a client can save,
   it has no observable effect: each player's orders edit only that
   player's own objects, and every effect on another player's object
   (cargo gifts, drops, fleet transfers) is queued to a fixed later step.
   Only crafted order files that act on another player's object could
   show it (`ORDERS.md`, "Conflicts between players").
3. Each player's order file, in that order, is accepted or skipped,
   validated and applied: direct cargo moves, transfers, merges, splits,
   waypoint and production changes, research settings. Owner: `ORDERS.md`
   (file acceptance, per-order validation, conflicts, fleet operations).
   Order CONFIRMED (FO-01..07): direct cargo, transfer, merge and split
   orders take effect before any movement.

**1a. Checks after the orders** (Order BINARY-ONLY)

1. **Registration check.** Players with an invalid or duplicated serial
   are flagged, and the penalty notices are sent. Owner: `ORDERS.md`
   "Registered-copy gate", this file's "Duplicate-serial penalty",
   `MESSAGES.md` 0x100–0x103. Elegy has no registration scheme, so this
   step does nothing in Elegy.
2. Ship-design housekeeping: starbase designs are marked as starbases.
   Uncovered. No observable effect is known.
3. **Following fleets.** A fleet whose only waypoint (waypoint 0) is
   aimed at another fleet follows it. If the leader has a next waypoint,
   or is itself a follower, the follower gets a copy of the leader's
   waypoint 1, carrying its own waypoint-0 task onto it. Up to 8 passes
   resolve chains of followers. A follower whose leader no longer exists
   gets message 0x138 (`MESSAGES.md`, CONFIRMED fo/fo04) and stops
   following. The copying rule is BINARY-ONLY. This is separate from
   chasing, where waypoint 1 is aimed at a fleet (this file's "Chasing
   another fleet"). Then the **waypoint check**
   runs: coordinates are clamped to the galaxy and waypoints aimed at a
   fleet or object are moved to its current position (`ORDERS.md`
   "Waypoint upkeep"). Every fleet's "fought this year, no repair" mark is
   cleared before this (`COMBAT.md` "Repair").

### 2. Waypoint tasks before movement

Owner: `TAKEOVER.md` "Where each task happens in the year"; route and
transfer-fleet tasks in `ORDERS.md` "Waypoint upkeep and the remaining
tasks"; cross-owner cargo in `ORDERS.md`.

1. Every planet records whether it is owned (`TAKEOVER.md`, "At the start
   of this phase").
2. Unload tasks: each fleet in fleet order runs its waypoint-0 task:
   unload (including colonist drops on other players' planets), scrap,
   colonize or route.
3. All queued colonist drops are resolved (ground combat, new colonies).
4. Research level-up check (see Research). The year has three such
   checks: here, in step 4b and in step 6c.
5. Load tasks: each fleet in fleet order runs load, merge or route.
6. Cargo given to other players moves.

Order CONFIRMED (TK-001..003): these tasks act before movement and before
growth. A transport already in orbit invades, and a colony ship already in
orbit colonizes, before the year's growth (T-5, T-1).

**2a. Race check.** Each player's race is clamped and checked for
legality, with the penalty for a human race. Owner: `RACES.md` "In a
running game". Order BINARY-ONLY: in the program this runs **after** step
2 and before any movement, so the degraded race already applies to
that year's production. MEASURED (SL-12 and OT-6, whose test races were
not legal): colonists per resource had been raised before the year's
resources were computed. `MESSAGES.md` labels messages 0x117/0x182 for
this step.

### 3. Movement

1. Every minefield forgets which players saw it this year (`OBJECTS.md`
   "Visibility").
2. **Objects move.** The Mystery Trader moves, and every packet already in
   flight moves and, if it arrives, hits its target (`OBJECTS.md`). If any
   object moved, the **waypoint check** runs again, so waypoints aimed at
   the Trader or a wormhole move to its new position before any fleet
   moves. Order CONFIRMED: Trader before fleets with the waypoint refresh
   (WT-001 F1, WT-005); packet impacts before growth (OB-009).
3. **Fleets move**, in fleet order, ordinary fleets first: the movement
   gates (a waypoint-0 transport or lay-mines task holds the fleet; the
   registration penalty; engine failure), stargate jumps, travel with
   minefield hits on the way, and wormhole transit on arrival. Owners: this
   file's "Fleet movement"; `OBJECTS.md` (minefield hits, stargates,
   wormholes).
4. **Chasing fleets** move after every ordinary fleet, over passes 1–10.
   Owner: this file's "Chasing another fleet". Order CONFIRMED (FM-003,
   MF-02, the chain freeze).
5. Reached waypoints are consumed or rotated (`ORDERS.md` "Reaching a
   waypoint").
6. Every planet's homeworld mark is cleared, then set on each player's
   homeworld. This mark feeds the homeworld floor in Mining. Which
   planet keeps the mark after its owner changes is covered in
   `TAKEOVER.md`.

Order CONFIRMED (MF-4): a minefield stop's mine loss is taken during this
step from the field's count at that moment, before step 3a's decay.

**3a. Decay and detonation** (`OBJECTS.md` "Turn placement" step 5).
Salvage decays, packets decay, detonating minefields go off, and then
every minefield decays. Order CONFIRMED: decay comes before this year's
laying (OB-002-F); a detonating field decays with the extra 25% in the same
year (OB-002-M, MF-7, MF-8).

**3b. Colonists breeding in transit** (Inner Strength; this file's
"Inner Strength colonists breed in transit"). Order CONFIRMED (OT-5): the
overflow lands on the planet before production and growth, and the planet
grows on it the same year.

### 4. Production

Owner: this file's "Mining", "Resources and installation caps",
"Research" and "Production".

1. Mining on every planet.
2. Per planet, in planet order: resources (including resources from ships
   scrapped there this year, and the duplicate-serial ×4/5), the research
   tax, then the production queue. Ships completed here become new fleets
   (`PRODUCTION-LAUNCH.md`). Packets launched here start their flight
   (`OBJECTS.md` "Launch"). Terraforming items follow this file's
   "Terraforming".

Order CONFIRMED (PG-001..003, PQ-001): mining and resources use the
population **before** this year's growth. Installation caps for automatic
items use population **after** growth (see Production). Production uses
the tech levels from **before** this year's research (KX-005).

**4a. Population growth** on every planet (this file's "Population
growth"). Order CONFIRMED (TK-001..003, OB-009, PG): growth comes after
the pre-movement tasks, packet impacts and mining.

**4b. Research level-ups** (this file's "Research": the check that
spends this year's research). Order CONFIRMED
(KX-005): production used the old tech levels, and the terraforming in
step 7 used the new ones.

**4c. Random events**, when the option is on: comet strike, climate
change, new minerals, then the Mystery Trader's appearance (this file's
"Random events"; `OBJECTS.md` "Spawn and movement"). Order CONFIRMED
(KX-004): the events run after growth (protection and comet losses use
the after-growth population) and in this internal order.

### 5. Objects move again; fleets refuel

1. Packets launched this year fly half a year and may hit. Wormholes
   jiggle or jump. The Trader does not move. If any object moved, the
   waypoint check runs again (`OBJECTS.md`). Order CONFIRMED: wormholes
   move after fleets, so a fleet transits to the exit's position from
   before this step (OB-005-C). A packet launched this year can hit
   before battles and bombing: CONFIRMED (OT-3, a packet emptied the
   planet and the bombers orbiting it sent no bombing message).
2. Fleets refuel at starbases (this file's "Refuelling at a starbase").
   A fleet built in step 4 is already full (`PRODUCTION-LAUNCH.md`).

### 6. Battles, bombing and tasks after movement

1. Every planet records whether it is owned, before anything else in the
   phase (`TAKEOVER.md`, "Order inside a phase").
2. Battles at every location (`COMBAT.md`).

**6a. Bombing**, after every battle at every location (`TAKEOVER.md`
"Orbital bombing"). Order CONFIRMED: a starbase destroyed in this year's
battle no longer protects the planet (T-2); bombing uses the after-growth
population and tech researched this year (T-8).

**6b. Mystery Trader encounters** (`OBJECTS.md` "Encounters"). Order
CONFIRMED: after battles (OT-2: the battle was fought, then the surviving
freighters traded) and before the unload tasks (OT-1: a fleet ordered to
unload exactly 5,000 kT at the Trader's arrival planet was consumed and
nothing was unloaded). Its place against bombing is BINARY-ONLY and has
no visible effect: bombing never changes a fleet's cargo.

**6c. Waypoint tasks after movement** (`TAKEOVER.md`; mine laying in
`OBJECTS.md` "Laying"; remote mining in `TAKEOVER.md` "Other waypoint
tasks").

1. Every planet's report age is cleared. This is a file detail: it is the
   value the player's client shows as how many years old its information
   about a planet is. It has no effect on play.
2. Unload tasks: each fleet in fleet order runs unload (including invasions
   by arriving transports), colonize, remote mining, mine laying or route.
3. All queued colonist drops are resolved.
4. **Research level-up check** (the one `TAKEOVER.md` calls the second
   check). Order CONFIRMED
   (CB-018, CB-021): research gained from a battle becomes a level the
   same year, after step 4b has run.
5. Load tasks: each fleet in fleet order runs load, merge or transfer
   fleet.

Order CONFIRMED: an arriving colony ship colonizes after growth (T-1);
mines are laid before sweeping (OB-007-D). That laying comes after battles
is BINARY-ONLY.

### 7. Sweeping, repair and terraforming

1. Mine sweeping, by every fleet and then every starbase (`OBJECTS.md`
   "Sweeping"). Order CONFIRMED: after laying (OB-007-D).
2. Repair (`COMBAT.md` "Repair"). Order CONFIRMED (CB-017): it comes after
   battles, and a fleet that fought gets none.
3. Automatic terraforming: Claim Adjuster drift and the CA's free
   terraforming (this file's "Terraforming").
4. Remote terraforming by Orbital Adjusters (this file's "Terraforming").
   Order CONFIRMED (KX-005): both use this year's researched tech, and a
   fleet that arrived this year terraforms. 3 comes before 4: CONFIRMED
   (OT-4, a CA planet and a hostile adjuster ended where the CA step
   followed by the adjuster predicts, in two streams).

**7a. End-of-year checks.**

1. Registration penalties (`MESSAGES.md` 0x104–0x107). This step does
   nothing in Elegy.
2. The waypoint check (`ORDERS.md` "Waypoint upkeep").
3. Each player's estimates of other players' planets (population and
   defenses, with a random error) are refreshed. Owner: `SCANNING.md`.

### 8. Year end, scores and files

Order BINARY-ONLY: no state that play can observe depends on the order of
these items. Their rules carry their own tags.

1. The previous host file is backed up, and the year advances.
2. Scores, the yearly score record and the victory conditions (this file's
   "Scores and victory conditions").
3. Per-design caches written to the files: each design's scanner range,
   a "can no longer be built" mark, and the cloak percentage of other
   players' designs (`SCANNING.md`; uncovered as a file detail).
4. Three per-year random bits in the game options are redrawn
   (`Random(8)`). This affects the file contents only. Uncovered.

**8a. Files are written**: the host file, then each player's file, with
that player's knowledge (`SCANNING.md` "When knowledge is computed") and
the checks on later waypoints that `MESSAGES.md` places at P8a.

### Random draws

Any step that draws from the generator moves every later draw, so an
implementation that wants the original's streams must draw in this order.
Each item is tagged with how its place in the sequence is known.

1. **Player shuffle** (step 1): one draw per player, `Random(n − i)`.
   CONFIRMED (KX-004, KB-1C, KB-3A).
2. **Before movement** (step 2), in the order the tasks run:
   - A scrap at a planet with a starbase makes a tech attempt for the
     planet's owner, as in `COMBAT.md` "Tech from battle": `rand(100)`,
     and nothing more below 50. Otherwise up to 13 `rand(13)` Trader tries,
     each with a second `rand(100)` only when that item has a chance and
     the player lacks it. Then up to 6 `rand(6)` field tries. A player who
     has already gained a tech this year makes no draws. CONFIRMED (KB-3A:
     before mining).
   - Colonist drops are resolved by planet, in the order of each planet's
     first queued drop (`TAKEOVER.md`). A capture makes one tech attempt,
     against the old owner's levels. A planet with an ancient artifact
     adds `rand(6)` then `rand(301)`. Colonization draws nothing except
     those artifact draws. BINARY-ONLY.
3. **Movement** (steps 3–3b): the movement gates, minefield hits, the
   Trader's and wormholes' movement, salvage and packet decay with
   detonations, and breeding in transit. BINARY-ONLY as a place in the
   sequence; their rules carry their own tags.
4. **Production** (step 4). Mining makes one `Random(100)` per mineral
   whose output has a non-zero remainder, planets in id order, ironium,
   boranium, then germanium. CONFIRMED (KB-1C, KB-3A).
5. **Random events** (step 4c): comet strike, climate change, new
   minerals, then the Mystery Trader's appearance (this file's "Random
   events"). CONFIRMED after mining (KB-1C, KB-3A) and before bombing
   (KB-3A).
6. **After movement** (step 6):
   - battles (`COMBAT.md`);
   - bombing passes, in fleet order. Each pass draws, in order:
     factories `rand(T)`, defenses `rand(T)`, population `rand(1000)`,
     each only when its remainder is non-zero. Retro bombs draw nothing.
     CONFIRMED after the events (KB-3A);
   - Trader rewards (step 6b);
   - colonist drops after movement, as in item 2, with the same tech
     attempt and artifact draws.
   Battles, rewards and drops are BINARY-ONLY as places in the sequence.
7. **Year end**: Claim Adjuster drift (step 7), the estimates of other
   players' planets (7a) and the option bits (8). BINARY-ONLY, except
   that with events off the drift began right after mining (KX-005,
   below).

MEASURED (KX-004, KX-005): in quiet states with no fleets in motion,
battles or drops, the random events (KX-004) and the Claim Adjuster drift
with events off (KX-005) both began at draw 4 of the year's stream. Those
four draws are the two-player shuffle (2) and the two homeworlds'
germanium mining (2). CONFIRMED (KB-1C): with 17 mining draws, the events
began at draw 19. CONFIRMED (KB-3A, `PARITY.md` "KB batch 3"): a scrap
tech attempt, five mining draws, the events and one bombing pass in one
year matched the replay in all 11 streams whose start is known. The 12
other streams each matched at some start, and two of them showed a
climate change exactly where this order puts it. With mining before the
scrap attempt, all 11 streams of known start would differ; with bombing
before the events, 3 of them and both climate streams would.

### Orders still unpinned

The OT runs (`PARITY.md`, "OT — turn order, breeding in transit, AR loss gate, score speed code") measured the five orders an
implementation could get visibly wrong: 3b before 4, 5 before 6a, 6 before
6b, 6b before 6c and 7.3 before 7.4. All matched the program.

What stays BINARY-ONLY:

- **The race check after the pre-movement tasks (2a after 2).** Only a
  hand-edited race file could tell the two orders apart.
- **The Trader encounter against bombing (6a against 6b).** Bombing does
  not touch fleets, so no run can separate them.
- **Mine laying after battles (6c after 6).**
- **Registration steps, design housekeeping, the report-age reset, and the
  file-only caches and bits (8.3, 8.4).** None of them changes game state
  an implementation can observe.

## Habitability

Race: for each axis (gravity, temperature, radiation) a center `c`, a low
`lo` and a high `hi` on the 0–100 internal scale, or "immune" on that axis.
Planet: current environment `v` per axis on the same scale.

Rule (CONFIRMED at the seven points the vector table marks so: KX-002
H1–H6 cover one and two axes off centre, all three off, the range edge
and two hostile planets, read through growth and resources):

1. If any axis is outside `lo..hi`, the planet is hostile:
   `hab = −Σ min(15, distance beyond the nearer edge)` over the axes outside
   their range (−1 to −45).
2. Otherwise, start with `S = 0`, `M = 10000`. Per axis:
   - immune: `S += 10000`;
   - else `d = |v − c|`, `w = c − lo` if `v < c` else `hi − c`,
     `e = 100 − trunc(100·d / w)`, `S += e²`; and if `2d − w > 0`
     (more than halfway to the edge), `M = trunc(M·(2w − (2d − w)) / (2w))`.
3. `x = trunc(sqrt(S/3) + 0.9)` (floating point), `hab = trunc(x·M / 10000)`.

Vectors (race center 50, low 15, high 85 on every axis):

| Planet (g, t, r) | hab | Status |
|---|---:|---|
| 50, 50, 50 | 100 | CONFIRMED (PG001) |
| 60, 50, 50 | 92 | CONFIRMED (KX-002 H1) |
| 70, 50, 50 | 79 | CONFIRMED (KB-1A, through the maximum population) |
| 85, 50, 50 | 41 | CONFIRMED (KX-002 H4) |
| 70, 70, 50 | 58 | CONFIRMED (KX-002 H2) |
| 80, 80, 80 | 3 | CONFIRMED (KX-002 H3) |
| 90, 50, 50 | −5 | CONFIRMED (KX-002 H5) |
| 10, 95, 50 | −15 | CONFIRMED (KX-002 H6) |

The cap of 15 per hostile axis is CONFIRMED (KB-1A: a race with range
40–60 on a planet at 90/50/50 lost 15 of 1,000 units, hab −15, not −30;
at 90/90/50 it lost 30, hab −30, not −60).

## Maximum population

In units. Rule:

- ordinary race: `max = 100·hab` for `hab ≥ 5`; `max = 500` for `hab < 5`
  (hostile included). CONFIRMED for hab 100 (10,000 units), 92, 58, 41
  and 3 (500), and 500 on hostile planets (KX-002 H1–H6, through growth
  and effective population).
- Hyper-Expansion: `max −= trunc(max/2)`. Jack of all Trades:
  `max += trunc(max/5)`. Then Only Basic Remote Mining:
  `max += trunc(max/10)`. CONFIRMED one at a time at hab 100 (KX-002 P1:
  HE 5,000; P2: JOAT 12,000; P3: OBRM 11,000), and JOAT with OBRM
  combined (KB-1A: hab 79 gives 10,428, not the 10,270 of adding both
  bonuses to the base). That case does not tell the order of the
  truncations apart, and HE with OBRM is BINARY-ONLY.
- Alternate Reality: 0 unless the planet has the owner's starbase; then by
  starbase hull, in hull order: 2,500, 5,000, 10,000, 20,000, 30,000 units,
  regardless of habitability. CONFIRMED for all five hulls (KB-1B:
  Orbital Fort, Space Dock, Space Station, Ultra Station and Death Star
  planets each held at the maximum plus 5, and the Space Dock at hab 3).
  OBRM's +10% on top is BINARY-ONLY.
- Alternate Reality with maximum 0 (population on a planet without the
  owner's starbase): the original cannot generate the year. If the planet's
  habitability is ≥ 0, population growth divides by the maximum and the
  program stops with an integer divide-by-zero error; no file is written.
  CONFIRMED (KX-001 Z1, from both the player screen and Host Mode).
  LEGACY BUG: there is no original behavior to reproduce, so an
  implementation must choose one and say so. A hostile planet (`hab < 0`)
  takes the hostile death rule, which does not use the maximum, and
  generates normally (CONFIRMED, KX-001 Z3). AR colonization gives the
  planet a starbase; the route to this state in play is deleting the
  starbase's design, which removes the starbase and keeps the population
  (BINARY-ONLY).

Vectors: HE at hab 100 → 5,000; JOAT at hab 100 → 12,000; OBRM at hab
100 → 11,000; hab 3 → 500 (all CONFIRMED, KX-002); JOAT+OBRM at hab 79 →
10,428 (CONFIRMED, KB-1A).

## Population growth

State per planet: population `P` (units) and a growth **carry** `k`
(hundredths of a unit, 0–99). The carry is persistent: it is the byte
StarsAPI calls `excessPop`. Race growth rate `G` (percent; doubled for
Hyper-Expansion, CONFIRMED, KX-002 P1).

### Positive habitability (`hab ≥ 0`)

1. `g = G·hab` (growth in hundredths of a percent).
2. Crowding, with `max` from above:
   - `P < trunc(max/4)`: no change to `g`;
   - otherwise, if `P < max`: `c = trunc(1000·P / max)` (permille), and
     `g = trunc(g·(1000 − c)² / 562500)` if `g < 1000`, else
     `g = 10·trunc(trunc(g/10)·(1000 − c)² / 562500)`;
   - if `max ≤ P ≤ max + 10`: no change at all this year (P and k kept);
   - if `P > max + 10` (overcrowded): `g = 4·max(−300, trunc(c/−10) + 99)`
     with `c` as above (negative: deaths, at most 12% a year).
3. `t = trunc(g·P / 100)` (hundredths of a unit). (For very large products
   the game computes `trunc(g/100)·P`; it uses that value whenever it is at
   least 10,000,000.)
4. `q = trunc(t/100)`, `r = t − 100q` (both truncate toward zero, so negative
   when `t` is). If `q = 0` and `r = 0`, set `r = 1`.
5. `k += r`; if `k ≥ 100`: `q += 1`, `k −= 100`; if `k < 0`: `q −= 1`,
   `k += 100`. `P += q`.

Status: CONFIRMED for an ordinary race (growth 10%, hab 100,
max 10,000) over 36 consecutive years 2400–2436, 11 of them crowded
(27% to 54% of capacity), population **and** carry every year. That race
has `g = G·hab = 1000` exactly, so its crowded years exercise the
quantized branch, and the boundary is inclusive: the unquantized formula
would give 2425 → 2426 growth of 256 units, not the observed 254. KX-002
confirms the `g < 1000` branch (H3 `g = 30`, H4 `g = 410`), HE's
`g = 2000` (P1), the "within 10 units of max" freeze (G2), the zero-growth
carry (G3) and overcrowding (G1). Overcrowding was published before
KX-002 as `2·max(−300, …)`. The oracle gave twice those deaths (G1:
12,000 → 11,899 carry 20, not 11,949 carry 60). Re-reading the binary
shows that this branch's result also goes through the final doubling of
the quantized crowded branch, so the factor is 4. The 16/9·(1−x)² curve in `PARITY.md` (H1) is
this rule; its 0–4 unit misses come from the permille truncation, the
quantization of `g` to a multiple of 10, and the carry.

Vectors, CONFIRMED (PG-001..003, `G = 10`, hab 100, max 10,000, start
P 250, k 0 in 2400):

| Year | P | k | | Year | P | k | | Year | P | k |
|---:|---:|---:|---|---:|---:|---:|---|---:|---:|---:|
| 2400 | 250 | 0 | | 2413 | 861 | 90 | | 2426 | 2958 | 17 |
| 2401 | 275 | 0 | | 2414 | 948 | 0 | | 2427 | 3218 | 47 |
| 2402 | 302 | 50 | | 2415 | 1042 | 80 | | 2428 | 3479 | 12 |
| 2403 | 332 | 70 | | 2416 | 1147 | 0 | | 2429 | 3740 | 4 |
| 2404 | 365 | 90 | | 2417 | 1261 | 70 | | 2430 | 3998 | 10 |
| 2405 | 402 | 40 | | 2418 | 1387 | 80 | | 2431 | 4253 | 97 |
| 2406 | 442 | 60 | | 2419 | 1526 | 50 | | 2432 | 4500 | 64 |
| 2407 | 486 | 80 | | 2420 | 1679 | 10 | | 2433 | 4739 | 14 |
| 2408 | 535 | 40 | | 2421 | 1847 | 0 | | 2434 | 4971 | 35 |
| 2409 | 588 | 90 | | 2422 | 2031 | 70 | | 2435 | 5190 | 7 |
| 2410 | 647 | 70 | | 2423 | 2234 | 80 | | 2436 | 5402 | 86 |
| 2411 | 712 | 40 | | 2424 | 2458 | 20 | | | | |
| 2412 | 783 | 60 | | 2425 | 2704 | 0 | | | | |

Worked crowded step (2425 → 2426): `g = G·hab = 10·100 = 1000`, which is
not below 1000, so the quantized branch applies. `c = trunc(1000·2704/10000) = 270`,
`(1000 − c)² = 532900`, `g = 10·trunc(100·532900/562500) = 940`;
`t = trunc(940·2704/100) = 25417`; `q = 254`, `r = 17`; P 2958, k 17.

Vectors (start `(P, k)`, max, G, hab → result; CONFIRMED where a KX-002
case is named, otherwise BINARY-ONLY):

| Start | max | G | hab | Result | Case |
|---|---:|---:|---:|---|---|
| 1000, 0 | 7900 | 15 | 79 | 1118, 50 | uncrowded |
| 5000, 30 | 10000 | 15 | 100 | 5330, 30 | crowded, `g ≥ 1000` quantization |
| 3000, 0 | 8600 | 10 | 86 | 3194, 70 | crowded, `g < 1000` |
| 300, 0 | 500 | 10 | 3 | 300, 24 | crowded, `g < 1000` (KX-002 H3) |
| 3000, 0 | 4100 | 10 | 41 | 3015, 60 | crowded, `g < 1000` (KX-002 H4) |
| 3000, 0 | 5000 | 20 | 100 | 3168, 0 | HE, crowded, `g ≥ 1000` (KX-002 P1) |
| 10005, 0 | 12000 | 10 | 100 | 10045, 2 | JOAT, crowded (KX-002 P2) |
| 10005, 0 | 11000 | 10 | 100 | 10015, 0 | OBRM, crowded (KX-002 P3) |
| 9995, 0 | 10000 | 10 | 100 | 9995, 1 | zero growth adds 1 to the carry (KX-002 G3) |
| 10005, 0 | 10000 | 10 | 100 | 10005, 0 | within 10 units of max: frozen (KX-002 G2) |
| 12000, 0 | 10000 | 10 | 100 | 11899, 20 | overcrowded deaths, `g = −84` (KX-002 G1) |

### Hostile planets (`hab < 0`) (CONFIRMED, KX-002 H5, H6)

`t = max(1, trunc(|hab|·P / 10))` hundredths of a unit die:
`q = trunc(t/100)`, `r = t − 100q`; `k −= r`, and if `k < 0`, `k += 100`
and `q += 1`; `P −= q`. (Matches the documented `|hab|/10` percent per
year.) Growth and deaths are computed only for owned planets with a
non-zero population, so the `max(1, …)` never acts on an empty planet
(BINARY-ONLY). Vectors (CONFIRMED): `P 1000, k 0, hab −5` → `995, 0`;
`P 1234, k 10, hab −15` → `1215, 59`.

### Duplicate-serial penalty (BINARY-ONLY)

A player flagged for a duplicate or invalid serial has `g` halved
(`trunc(g/2)`, applied before crowding) during turn generation, and its
planets' production resources (with a queue) multiplied by 4/5 (truncating).
Not part of normal play; listed because `PARITY.md` records the earlier
halved-growth observation.

## Resources and installation caps

Race settings used: colonists per resource `R0` (in units: the race
wizard's value / 100), factory output `F` (resources per 10 factories),
factories operated `Fo` and mines operated `Mo` (per 10,000 colonists, i.e.
per 100 units).

### Resources per planet

1. Effective population `E = P` if `P ≤ max`, else
   `min(2·max, max + trunc((P − max)/2))`. Above max: CONFIRMED (KX-002 G1,
`P` 12,000 at max 10,000 → `E` 11,000; H5, H6, hostile planets above
their 500); the `2·max` limit is CONFIRMED (KB-1A: 45,000 units at
maximum 13,200 gave 2,650 resources, from `E = 26,400`, not 2,920).
2. Non-AR: `resources = trunc(E / R0) + trunc((F·n + 9) / 10)`, where
   `n = min(installed factories, operable factories)`.
3. Alternate Reality: `trunc(sqrt((E / R0)·max(1, energy tech))·
   max(25, hab)·0.1 + 0.999)`, all in floating point, including `E / R0`.
   The `max(25, hab)` floor is CONFIRMED (KB-1B: with an AR planet at hab
   3, the player's yearly resources were 8,054, not 7,803).
   CONFIRMED at one point (KX-001 Z2: `E = 486`, `R0 = 10`, energy 2,
   hab 100 → `trunc(9.859·100·0.1 + 0.999) = 99`; truncating `E / R0`
   first would give 98).
4. A result of 0 becomes 1 (unless `P = 0`, which gives 0).

AR with maximum 0 has `E = 0`, so 1 resource (CONFIRMED, KX-001 Z3).

CONFIRMED (PG-001..003, `R0 = 10`, `F = 10`, 10 factories): this year's
research resources are `trunc(P/10) + 10` from last year's population, for
every year 2408–2436. Vectors: P 486 → 58, 1042 → 114, 2704 → 280,
5190 → 529. PQ-001 confirms `resources = trunc(P/10)` with no factories.

### Caps (units for `P`, `max`)

| Quantity | Rule | Status |
|---|---|---|
| maximum mines | `max(10, trunc(max·Mo/100))` (AR: 0) | CONFIRMED at hab 41: 410 (KX-002 C3); AR 0 (KB-1B); the floor of 10 cannot be reached (below) |
| maximum factories | `max(10, trunc(max·Fo/100))` (AR: 0) | CONFIRMED at hab 58: 580 (KX-002 C1); AR 0 (KB-1B); the floor of 10 cannot be reached |
| maximum defenses | `min(100, max(10, 4·hab))` (AR: 0) | CONFIRMED at hab 3: 12 (KX-002 C2); the cap of 100 (KB-1A: 95 + 5 built at hab 100), the floor of 10 (KB-1A: hab −15, 5 + 5) and AR 0 (KB-1B) |
| operable mines | `max(1, min(max mines, trunc(P'·Mo/100)))` | CONFIRMED for auto mines (PQ C04, C09, C14) |
| operable factories | `max(1, min(max factories, trunc(P'·Fo/100)))` | CONFIRMED for auto factories (PQ C09) |
| operable defenses | `min(max defenses, 1000, ceil(P'/25))` | CONFIRMED (PQ C13) |
| mines working this year | `min(installed, operable with P' = P)`; AR: `trunc(sqrt(P))` | CONFIRMED (PG mining; AR: KX-001 Z2, Z3, P 486 → 22) |

`P'` is `P` for the year's mining and resources, and `P` plus this year's
growth when production caps are computed. Production caps differ by order
kind:

- **Auto Mines, Auto Factories, Auto Defenses** build at most
  `operable − installed` this year (and at most their count). CONFIRMED
  (PQ C04, C09, C13, C14). Auto Alchemy is not an installation; its count
  is ignored (PQ C05).
- **Plain Mine, Factory and Defenses orders** larger than
  `max(maximum, operable) − installed` are cut to it when the queue
  reaches them, with a message; the order is edited permanently, and
  removed if that is 0 or less. CONFIRMED (PQ C10).

The floor of 10 on maximum mines and factories never acts in a legal
game: the smallest maximum population is 250 units (Hyper-Expansion below
hab 5), and the race wizard's lowest mines and factories operated is 5
per 10,000 colonists, which gives 12.

Vectors (PG race, `Mo = Fo = 10`, 100% planet, so maximum mines and
factories are 1000 and maximum defenses 100):

- C09: 48 mines, population 550 after growth → operable 55; Auto Mines ×100
  builds 7 (`max(maximum, operable) − installed` would allow 952).
- C13: 40 defenses, population 1111 after growth → operable
  `ceil(1111/25) = 45`; Auto Defenses ×100 builds 5 (not 60).
- C10: 995 factories, Factory ×10 → cut to `max(1000, operable) − 995 = 5`;
  factories end at 1000.

## Mining

Per planet with an owner and population, per mineral (ironium, boranium,
germanium), with concentration `conc` (stored byte), a per-mineral
depletion fraction `f` (stored byte, 1/256ths of the current concentration
point remaining, 0 meaning a full 256) and `m` working mines:

1. Homeworld floor: on a homeworld, `conc` below 30 counts as 30 for output
   and for depletion (the stored value is not raised, and keeps falling).
   CONFIRMED (KX-002 N2: stored ironium 20 → 19 over three years, output
   300 kT a year from 1000 mines).
2. `prod = conc_used·m`; output `amt = trunc(prod·eff/10)` with
   `eff` = race mine output (AR: 10).
3. Surface minerals gain `trunc(amt/100)`, plus 1 with probability
   `(amt mod 100)/100` (one `rand(100) < amt mod 100` draw per mineral with a
   non-zero remainder). Draw order: every planet is mined before any
   planet's production, planets in id order, and within a planet ironium,
   boranium, germanium. CONFIRMED (KB-1C): 17 mining draws on 7 planets in
   11 random streams, 77 planet results, all as replaying each stream with
   this rule gives (mining starting at draw 2, right after the shuffle;
   starting at draw 4 would have changed 68 of them), and the year's
   random events then followed at draw 19.
4. Depletion uses `p = trunc(prod/100)` (before `eff` and before the random
   +1) and the stored `conc` clamped for this purpose to
   `cc = 100` if above 100, `25` if below 25 (`10` if below 5):
   repeat while `p > 0` and stored `conc > 1`:
   - `cc` from the current stored `conc`, re-evaluated on every repetition
     (CONFIRMED, KX-002 N2: germanium 84 → 79 in one year, fraction 34;
     the `cc = 25` clamp, ironium at 20 and 19; the `cc = 10` clamp below
     5 is CONFIRMED by KB-1A: concentration 4 with 500 mines ended with
     fraction 251, where the clamp 25 gives 245);
   - `s = f` (or 256 if `f = 0`); `need = trunc(trunc(s·12500/256) / cc)`;
   - if `need ≤ p`: `p −= need`, `conc −= 1`, `f = 0`, and continue;
   - else `f' = trunc((need − p)·256 / trunc(12500/cc))`, raised to 1 if
     smaller and lowered to `s − 1` if not below `s`; set `f = f'` (and if
     that is 0, `conc −= 1`) and stop.

   So one concentration point costs about `12500/cc` units of `p`.
   CONFIRMED: concentration and fraction bytes after every one of 48 PG
   years (homeworld, 10 mines, race mine output 10, concentrations 30, 113,
   84 at 2407), and three years with 1000 mines, several points a year
   (KX-002 N2, vectors below).

Vectors (CONFIRMED, PG002 run, 10 working mines, `eff = 10`; fraction shown
as stored, 0 = 256):

| Year | conc I/B/G | frac I/B/G | surface I/B/G | Next year surface delta |
|---:|---|---|---|---|
| 2407 | 30/113/84 | 242/86/157 | 550/713/545 | +3/+11/+8 |
| 2408 | 30/113/84 | 240/61/143 | 553/724/553 | +3/+11/+9 |
| 2409 | 30/113/84 | 238/36/129 | 556/735/562 | +3/+12/+8 |
| 2410 | 30/113/84 | 236/12/114 | 559/747/570 | +3/+11/+9 |
| 2411 | 30/112/84 | 234/243/100 | 562/758/579 | |

Worked: boranium 2407 → 2408: `prod = 1130`, `amt = 1130`, gain 11 (+1 with
probability 30%; this year 0). `p = 11`, `cc = 100`, `s = 86`:
`need = trunc(4199/100) = 41 > 11`, so `f = trunc(30·256/125) = 61`.
Boranium 2410 → 2411: `s = 12`, `need = trunc(585/100) = 5 ≤ 11`: conc
113 → 112, `p = 6`; then `s = 256`, `need = 125 > 6`,
`f = trunc(119·256/125) = 243`.

Vectors (CONFIRMED, KX-002 N2: homeworld, 1000 working mines, `eff = 10`,
population frozen at max; 2407 as PG with ironium concentration set to
20):

| Year | conc I/B/G | frac I/B/G | Surface gain I/B/G that year |
|---:|---|---|---|
| 2407 | 20/113/84 | 242/86/157 | |
| 2408 | 20/104/79 | 88/73/34 | +300/+1130/+840 |
| 2409 | 19/96/74 | 189/11/77 | +300/+1040/+790 |
| 2410 | 19/88/70 | 35/241/11 | +300/+960/+740 |

### Remote mining

A fleet with a remote-mining task that did not move this year mines the
planet it orbits after production (turn order step 6c), with `m` = the
sum over its ships of each mining robot's rate, capped at 4,000 per
fleet: Robo-Midget 5, Robo-Mini 4, Robo 12, Robo-Maxi 18, Robo-Super 27,
Robo-Ultra 25, Alien 10. Output `amt = prod = conc·m` (the race's mine
output is ignored), with the same random +1 and depletion as planetary
mining, and no homeworld floor.

- **Unowned planets** (CONFIRMED, T-35: 24 robot points at 100/50/25 mined
  24/12/6 kT a year; CS-003-B: 10 robot points at 100 mined 10 kT; KB-1A:
  4,320 robot points at 68/78/76 mined 2,720/3,120/3,040 kT, the 4,000
  cap, with concentrations and fractions exactly as the depletion rule
  gives). A fleet that arrived this year mines nothing until the next
  year (T-35).
- **Owned planets.** Miners at a planet owned by a race other than
  Alternate Reality mine nothing, whether the planet is their owner's or
  another player's (CONFIRMED, T-35). At an Alternate Reality planet, the
  planet owner's own miners do mine it (CONFIRMED, KB-1B). Their output
  is a separate mining step, not extra mines added to the planet's own:
  each step truncates and depletes on its own. KB-1B: an AR Space Station
  planet at 15/82/45 with 100 own mines and an 8-point miner ended with
  boranium fraction 106, which two separate steps give; one step with 108
  mines gives 107. The order of the two steps is BINARY-ONLY (both give
  the same result here). Another player's miners at an AR planet are
  BINARY-ONLY.

## Research

Six fields (energy, weapons, propulsion, construction, electronics,
biotech), each with a level (0–26) and accumulated research toward the next
level.

### Level cost

`cost(level L) = base[L] + 10·(sum of the player's six current levels)`,
then by the field's research-cost setting: "costs 75% more" →
`2c − trunc(c/4)`; "normal" → `c`; "costs 50% less" → `trunc(c/2)`; then
doubled when the game's slower-tech option is set.

`base[L]` for L = 1..26: 50, 80, 130, 210, 340, 550, 890, 1440, 2330, 3770,
6100, 9870, 13850, 18040, 22440, 27050, 31870, 36900, 42140, 47590, 53250,
59120, 65200, 71490, 77990, 84700.

CONFIRMED for the normal setting, levels 3–9 of one field (PG), and for
"costs 75% more" (KX-002 R1: `c = 210` → 368, rounding up) and "costs 50%
less" (KX-002 R2: 100, 145, 215, 325).

Slower tech (CONFIRMED, KX-003 S2): the stored accumulation `S` is kept at
half scale. Each year `L = 2S + research`; levels are taken while
`L ≥ 2·cost`; what is left is stored as `ceil(L/2)`. Vectors (JOAT, every
field at 3, energy): research 435 → level 3, stored 218 (a normal game
levels with 45 left); next year 485 → `436 + 485 − 780` → level 4, stored
71. Research 937 → level 4, stored 79; next year 954 → `158 + 954 − 1060`
→ level 5, stored 26. Under Generalized Research the current field's
half is treated like normal research (stored as half, rounded up), and
each other field's 15% share `o` is added to its stored value as
`trunc(o/2)` (CONFIRMED, KX-005 R2: research 1,995, energy current →
stored 499, every other field 150 (`o` = 300); weapons at level 0 did not
level). Stolen research (Super Stealth) is halved rounding up: the
message shows the full `s`, and `ceil(s/2)` is stored (CONFIRMED, KB-2B:
stolen 23 and 88 stored as 12 and 44).

### Allocation

- Planets without a production queue send all their resources to research,
  whatever the research budget setting, 0% included (CONFIRMED, PG; TK-001). Planets with a queue send the research tax first
  (`trunc(resources·budget%/100)`, skipped with the leftover-only option)
  and whatever is left after the queue (CONFIRMED, PQ-001).
- All research goes to the current field. Level-ups: while
  `accumulated ≥ cost(level+1)`, subtract the cost and raise the level;
  the excess carries over (CONFIRMED, PG). Several levels per year are
  possible (CONFIRMED, KX-002 G1 and R2: three and four levels).
- When a level is gained in the current field and the "next field" choice
  is not "same field", the leftover moves to the new field and the current
  field's accumulation becomes 0; "lowest field" picks the lowest level
  (counting the level just gained), first in field order on ties. The new
  field is checked for level-ups the same year with that leftover, and can
  switch again. An explicit next-field choice is used once and then resets
  to "same field"; "lowest field" stays set. CONFIRMED (KX-002 R3: energy
  → weapons → propulsion in one year, "lowest" kept; R4: leftover 100 to
  biotech, choice reset). Only a level-up in the current field switches
  fields: under Generalized Research a field fed by its 15% share levels
  up in place and research stays in the current field (CONFIRMED, KX-005
  R1: weapons 0 → 1 from a 300 share, carry 30; energy stayed current with
  next "lowest" set).
- Generalized Research: the current field gets `trunc((res+1)/2)`; each
  other field gets `trunc((3·res + 19)/20)` (15% rounded up)
  (CONFIRMED, KX-002 R5: 211 → 106 and 32 each).
- Research into a field at level 26 is lost (CONFIRMED, KX-002 R6);
  level 10 for a capped player: BINARY-ONLY.
- When the current field reaches 26 and the next-field choice is "same
  field", research moves that year, with the leftover, to the lowest
  field (first in field order on ties), and the stored choice stays "same
  field" (CONFIRMED, KX-005 R3: energy 25 → 26 with 15 left over; weapons
  became current with 15 stored, choice still "same"). For the rest of
  that year the switch logic acts as if "lowest field" were chosen
  (CONFIRMED, KB-2A: energy 25 → 26 with 1,115 left; weapons 0 → 1, then
  propulsion 0 → 1, then back to weapons with 185 stored; the stored
  choice stayed "same").
- **Messages.** Each level gained sends the player one message naming the
  field, the new level and the field research continues in (Generalized
  Research players get a variant). It is followed by one message per part
  that the level makes available: a part the race may use (race-restricted
  parts and Mystery Trader parts the player does not own are skipped)
  whose requirement in that field equals the new level **and** whose other
  five requirements are already met. CONFIRMED (KX-005 R1: energy 9 → 10
  announced Bear Neutrino Barrier, Laser Battery and Temp Terraform ±11,
  not Battle Nexus, which also needs electronics 19; a GR weapons 0 → 1
  announced Radiation Terraform ±3). So a part is normally announced
  when its last missing requirement is reached (follows from the rule).
- Super Stealth: after every player's research, an SS player gains, per
  field, `s = trunc(trunc(spent/players)/2)` when `s > 1`, where `spent` is
  every player's research in that field this year, its own included, and
  `players` the players still in the game; one message per field
  (CONFIRMED, KX-003 S3L: the other player spent 355 on weapons and the SS
  player 95 on energy; it ended with weapons 88 and energy 95 + 23 = 118).

Vectors, CONFIRMED (PG003: one player, energy current, next "same field",
other levels 0, 0, 0, 5 (electronics), 0; research = all resources):

| Year | Research added | Energy level | Energy accumulated |
|---:|---:|---:|---:|
| 2407 | | 2 | 65 |
| 2408 | 58 | 2 | 123 |
| 2409 | 63 | 2 | 186 |
| 2410 | 68 | 3 | 54 |
| 2413 | 88 | 4 | 7 |
| 2417 | 124 | 5 | 15 |
| 2421 | 177 | 5 | 638 |
| 2422 | 194 | 6 | 182 |
| 2426 | 280 | 7 | 163 |
| 2431 | 409 | 8 | 389 |
| 2435 | 507 | 8 | 2274 |
| 2436 | 529 | 9 | 343 |

Worked 2435 → 2436: `2274 + 529 = 2803 ≥ cost(9) = 2330 + 10·(8+5) = 2460`;
level 9, carry 343.

## Production

The PQ-001 model in `PARITY.md` ("Production Queues") is CONFIRMED in all
15 cases and is the production specification: research tax first, partial
percentage per component, stopping vs skipping, auto items and their hidden
partial items, Auto Alchemy, installation-order clipping, leftover to
research. Its predictions table doubles as the test vectors.

Partial percentage of one component with `a` available (including what is
already spent on the unit) and cost `c`:
`p = max(trunc((a + 1)·100/c) − 1, trunc(a·100/c))` (100 if `a ≥ c`). Use
this formula as written. It is usually, but not always, the largest
percentage whose truncated cost fits in `a`: for `c = 9`, `a = 4` it gives
54, although 55 would also cost only 4 (CONFIRMED, KX-001 M4: Inner
Strength defense, 4 resources left, 54%).

Which component limits a unit (CONFIRMED where cases are cited,
BINARY-ONLY otherwise): the components are compared in the order Fe, Bo,
Ge, resources, and one replaces the current lowest only if its percentage
is strictly lower. So the first of tied minerals wins, and a mineral wins
a tie with resources (BINARY-ONLY). Two facts are recorded: whether **any**
mineral is short, and whether resources were **strictly** the lowest.

- An auto item with any mineral short is mineral-blocked: without an
  alchemy prefix it is skipped with nothing spent, even when resources
  give the lower percentage (CONFIRMED, KX-001 A7).
- Otherwise the unit is charged up to the lowest percentage (all
  components), and the queue stops there unless an alchemy prefix applies
  (next section).

### Item costs

Per unit, as resources and Fe/Bo/Ge kT, from the owner's race:

| Item | Cost | Status |
|---|---|---|
| Factory (and Auto Factories) | race factory cost; Ge 4, or 3 with "factories cost 1 kT less germanium" | CONFIRMED (PQ-001 cost 10; KX-001 M3 cost 7, M3b cost 15; Ge 3 in M3, M3b) |
| Mine (and Auto Mines) | race mine cost | CONFIRMED (PQ-001 cost 5; KX-001 M3b cost 8) |
| Defenses (and Auto Defenses) | 15 + 5/5/5; Inner Strength `trunc(c·3/5)` of each component (9 + 3/3/3) | CONFIRMED (PQ-001; KX-001 M4) |
| Mineral Alchemy, Auto Alchemy | 100 resources per unit (1 kT of each mineral); 25 with the Mineral Alchemy LRT | CONFIRMED (PQ-001; KX-001 M1, M2) |
| Terraform | 100 resources per step; 70 with Total Terraforming; halved for Claim Adjuster | CONFIRMED (KX-002 T1, T2; Claim Adjuster KX-005) |

Race settings outside the race wizard's advantage-point budget do not
survive: at the start of turn generation the game sends the player a
message and degrades the race before production (MEASURED once, KX-001
M3: colonists per resource went from 1,000 to 2,400). The binary reading
says the trigger is a negative advantage-point total; the points formula
is not specified here. Test races must be legal.

### Auto Alchemy before a multi-count item (CONFIRMED, KX-001)

An Auto Alchemy that is not the last item does nothing itself; it lets the
next item buy minerals. For a ×n item the purchase is made **one unit at a
time** inside the item's normal unit loop:

1. If the unit's remaining cost is available, it completes; go to the next
   unit.
2. Otherwise the unit takes its partial percentage as usual (every
   component charged up to it). Unless resources were strictly the lowest
   component, alchemy then buys `k = min(trunc(resources / rate), s)`
   units, where `s` is the lowest component's shortfall for this unit
   (`cost − available − already spent`, taken before the partial charge)
   and `rate` the alchemy cost; each unit adds 1 kT of all three minerals.
   An auto item with any mineral short skips the partial charge and goes
   straight to alchemy, even when resources were the lowest; `s` is then
   the resource shortfall (CONFIRMED, KX-001 A6: 1 resource, no germanium,
   Auto Factories → nothing bought, Mineral Alchemy ×1 @1% at the front,
   not a 19% factory).
3. If `k = s`, retry the unit (it now completes). Otherwise the unit keeps
   the percentage from step 2, unchanged by the minerals just bought; if
   resources `r` remain, they become a Mineral Alchemy ×1 item at
   `pct = max(trunc((r + 1)·100/rate) − 1, trunc(r·100/rate))` (the same
   partial-percentage formula as any item; it is not always the largest
   percentage that fits), charging `trunc(rate·pct/100)`, inserted at the
   queue front; the queue stops. The prefix and the item (with its reduced
   count) stay.
4. If every unit of a non-auto item completes, the item and its prefix
   are removed and the walk continues. An auto item stays in the queue
   when it has built its year's count, and so does its prefix, which
   applies again next year (CONFIRMED, KX-001 A5: Auto Alchemy, Auto
   Factories ×2, Mine ×2 with 900 resources and no germanium → 2
   factories, 2 mines, queue Auto Alchemy, Auto Factories ×2, research
   70).

Vectors (PG race: factory 10 + 4 kT Ge, mine 5, alchemy 100; no tax;
minerals 100/100/g before the year):

| Case | Resources | g | Queue | Result |
|---|---:|---:|---|---|
| A1 | 900 | 0 | Auto Alchemy, Factory ×5, Mine ×2 | 2 factories; 108/108/0; Mineral Alchemy ×1 @78%, Auto Alchemy, Factory ×3 @24%, Mine ×2; research 0 |
| A2 | 900 | 6 | same | 3 factories; 108/108/2; Mineral Alchemy ×1 @68%, Auto Alchemy, Factory ×2 @24%, Mine ×2 |
| A3 | 900 | 0 | Auto Alchemy, Auto Factories ×5, Mine ×2 | 2 factories; 108/108/0; Mineral Alchemy ×1 @80%, Auto Alchemy, Auto Factories ×5, Mine ×2 |
| A4 | 820 | 0 | Auto Alchemy, Factory ×2, Mine ×2 | 2 factories; 108/108/0; Mine ×2 @19% (0 resources left) |
| M2 (alchemy 25) | 300 | 0 | Auto Alchemy, Factory ×5, Mine ×2 | 2 factories; 111/111/3; Mineral Alchemy ×1 @15%, Auto Alchemy, Factory ×3 @24%, Mine ×2 |

Worked A1: unit 1 has no germanium, so it takes 24% (`max(1·100/4 − 1, 0)`),
spending 2 resources and 0 kT; alchemy buys the 4 kT short (400); the unit
completes with the remaining 8 resources (410 in all). Unit 2 the same:
80 resources left. Unit 3 takes 24% (2 resources), alchemy can buy none,
and the remaining 78 become Mineral Alchemy @78%. Minerals: +8 kT each,
8 kT of germanium used.

Additional rules (CONFIRMED by KB-2A unless marked):

- A planet with a production queue of zero items contributes nothing to
  research that year, not even the research tax, and gets no production
  message; the empty queue stays. (A queue emptied during the year is
  removed, so the next year takes the no-queue path and sends everything
  to research.) A zero-item queue does not arise in play; KB-2A wrote one
  directly.
- Resources from ships scrapped at a planet this year with Ultimate
  Recycling (`x`, the ships' resource cost for their owner) raise that
  planet's production resources `r` to `r + trunc(x·r/(x + r))`, also on
  a planet without a queue. The scrap message shows the added amount
  (KB-2A: `x` 2,410, `r` 500 → 914, message 414).
- A planetary scanner order on a planet that already has one is removed
  with a message; a mass-driver packet order without a driver or
  destination is removed with a message. Either way, a queue left empty
  is freed with the "completed its orders" message and the planet's
  resources go to research. A terraform order above the remaining
  terraform capacity is clipped, or removed at 0 (KX-002 T1, T3; KB-2C;
  see "Terraforming").
- A planet with 0 resources builds nothing and sends no messages
  (BINARY-ONLY; an owned planet with population has at least 1 resource,
  so only the duplicate-serial ×4/5 cut of a 1-resource planet reaches it).

### Terraforming

A Terraform Environment unit (planetary item 12) moves one environment
axis of the planet one click (CONFIRMED, KX-002 T1–T3; parts below
BINARY-ONLY where marked):

- **Reach per axis.** `t` = the largest value among the owner's
  available terraform parts for that axis (`COMPONENTS.md`, category
  `terraform`; a Total Terraform part, which needs the TT LRT, counts for
  every axis). The axis can be moved within `orig ± t`, clipped to 1–99,
  where `orig` is the planet's original (never-terraformed) value, and
  only toward the race's centre, stopping at it. CONFIRMED: Gravity
  Terraform ±3 from 60 reaches 57 (T1), and from a current 58 with
  original 60 only 57 remains (T3); TT ±3 applies to gravity and
  temperature (T2). An immune axis is not terraformed and adds nothing to
  the capacity (CONFIRMED, KB-2C: a gravity-immune race at 20/47/50 had
  Terraform ×5 cut to ×3 and reached 20/50/50; at 10/50/50 ×2 was
  removed with nothing built).
- **Capacity.** The clicks still available are the sum over axes of the
  distance from the current value to its limit. An order (or the part of
  it left) above that is cut to it when the queue reaches it, with a
  message, and removed if it is 0 (CONFIRMED, T1: ×5 → ×3; T3: ×5 → ×1;
  T2: 6 clicks, ×5 kept).
- **Axis choice.** For each unit, each axis with room gets
  `score = trunc(|hab(limit) − hab(now)|·100 / |limit − now|) + 1`, where
  `hab(limit)` is the planet's habitability with that axis alone set to its
  limit: the average change per click over the whole remaining range, not
  the next click. The highest score wins, the first axis (gravity,
  temperature, radiation) on ties. CONFIRMED at one point (T2: from
  60/45/50 with ±3, temperature 101 against gravity 67, and both units went
  to temperature). Ties go to the first axis (CONFIRMED, KX-005: 50/60/60
  with gravity at the centre, temperature and radiation tied, one unit →
  50/59/60).
- **Cost.** 100 resources per unit, 70 with TT (CONFIRMED, T1, T2), half
  for Claim Adjuster (CONFIRMED, KX-005: a CA planet with 120 resources
  and Terraform ×3 built two and left ×1 at 41%); no minerals.
- **Tech used.** Production uses the owner's tech before this year's
  research; the Claim Adjuster year-end step and Orbital Adjusters run
  after research and use the levels just reached (CONFIRMED, KX-005: both
  players went from energy 3 to 5 during the year; production still
  reached ±3 in temperature, the CA planets and the adjusters ±7).
- **Auto Max Terraform** builds units up to the capacity, whatever the
  population (CONFIRMED, KX-005: ×9 with capacity 6 built 6; 50/60/58 →
  50/57/55). **Auto Min Terraform** builds up to the capacity only when
  the planet's population change this year is negative or its
  habitability for the owner is 0 or less; otherwise nothing (CONFIRMED,
  KX-005: a growing planet built none; a planet at −1% habitability built
  its one unit; an overcrowded planet at 83% built 6). The count of an
  auto item is a per-year limit and the item stays in the queue.
- **Orbital Adjusters** (CONFIRMED, KX-005 T0–T2). After movement, every
  fleet orbiting an owned planet with Orbital Adjusters makes one click
  per adjuster (whatever the part's value) on that planet, with the
  **fleet owner's** reach (its terraform parts, at its levels after this
  year's research) and the **planet owner's** habitat. A fleet that
  arrived this year counts.
  - Fleet owner = planet owner, or the fleet owner treats the planet owner
    as a friend: each click improves the planet as a production unit
    would, from `orig ± reach`, starbase or not (planet 60/60/60, reach
    gravity 11, temperature 7, radiation 3: two clicks → 60/58/60, also on
    a planet with a starbase).
  - Otherwise (neutral or enemy): nothing if the planet has a starbase.
    Else each click worsens the planet: per axis the target is whichever
    of `orig − reach` and `orig + reach` (clipped to 1–99) is farther from
    the owner's centre, provided it is farther than the current value
    (the lower end on a tie), and the axis is chosen by the same score
    (60/60/60 → 62/60/60: gravity toward 71 scores 137 against 67).
  - The fleet owner gets a message per planet changed, the planet owner
    one too when its habitability changed.
- **Claim Adjuster.** At the end of the year (after production and growth)
  every axis of each CA planet moves in one step to the full reachable
  value, as far as the reach rule above allows, with no items built and no
  resources spent (CONFIRMED, KX-003 S3/S3L at reach 3: 60/42/56 →
  57/45/53, and 58/50/50 with original 60/50/50 → 57/50/50; growth that
  year used the old environment; TK-108 and TK-118..121 at reach 15 and
  30 after a capture). After a capture the reach is measured from the
  original value the capture restored (`TAKEOVER.md`), so a CA capturing a
  CA planet ends the year at original ± reach toward its own centre:
  55/47/52 → 50/50/50, 80/20/80 → 65/35/65 (±15) or 50/50/50 (TT ±30). The CA owner's terraform parts follow the normal tech and LRT
  rules (Total Terraform still needs TT). The original value of an axis
  can also drift one click toward the centre, before the year-end step
  (so the reach is measured from the new original): for each CA planet in
  planet order, `rand(3)` picks an axis; if that axis's original value
  differs from the centre (and the axis is not immune), `rand(10)` must
  be 0, then the drift happens if the population (after growth) is 1000
  units or more, else if `rand(1000) <` the population. Message to the
  owner. CONFIRMED (KX-005: 17 runs from 15 random streams, 13 drifts on
  8 CA planets, every one reproduced by replaying these draws, and none
  where the replay gave none).

## Fleet movement

Coordinates are integers (light-years). `D` = straight-line distance from
the fleet to its current destination (waypoint 1), floating point. `w` =
the warp ordered for that leg (1–10). Engine fuel table `f(w)` per engine
(J-RC3 values in StarsAPI / the game's part data; e.g. Quick Jump 5:
0, 25, 100, 100, 100, 180, 500, 800, 900, 1080 for warps 1–10).

### Distance and arrival (CONFIRMED, FM-001..003)

1. Allowed distance `A = min(trunc(D + 0.9999), w²)`.
2. The fleet arrives exactly on the destination if
   `trunc(D − 0.99999) < A` (equivalently `D < w² + 0.99999` when not fuel
   limited), or if `trunc(D − 0.99999) ≤ 0`.
3. Otherwise it moves `A` along the line: each coordinate becomes
   `x0 + trunc(dx·A/D ± 0.5)`, `+0.5` when the destination coordinate is
   greater than the start, `−0.5` otherwise (round half away from zero; an
   exact half cannot occur between integer points at integer distance).
4. A fleet is in orbit of a planet exactly when its coordinates equal the
   planet's, including a deep-space waypoint that lies exactly on a planet
   (FM-004 OR).
5. Reaching waypoint 1 ends the fleet's movement for the year; leftover
   movement is not carried to the next waypoint. A first waypoint at the
   fleet's own position also uses up the year.

Vectors (FM-001/002, one Quick Jump 5 scout at warp 5, w² = 25, fuel 300;
every one ends with 297 mg):

| Corpus fleet | Start | Destination | D | End | Arrived |
|---|---|---|---:|---|---|
| FM-001 12 | (1250, 1020) | (1275, 1020) | 25.000 | (1275, 1020) | yes |
| FM-001 13 | (1310, 1020) | (1336, 1020) | 26.000 | (1335, 1020) | no |
| FM-001 17 | (1310, 1065) | (1334, 1073) | 25.298 | (1334, 1073) | yes |
| FM-002 18 | (1270, 1015) | (1295, 1020) | 25.495 | (1295, 1020) | yes |
| FM-002 19 | (1305, 1010) | (1331, 1011) | 26.019 | (1330, 1011) | no |
| FM-002 20 | (1200, 1050) | (1207, 1075) | 25.962 | (1207, 1075) | yes |
| FM-001 23 | (1110, 1190) | (1200, 1227) | 97.308 | (1133, 1200) | no |

Worked (FM-001 23): `A = 25`, `25/97.308 = 0.2569`;
`x = 1110 + trunc(90·0.2569 + 0.5) = 1133`,
`y = 1190 + trunc(37·0.2569 + 0.5) = 1200`.
The full per-fleet tables are `experiments/fm00N/{predictions,results}.tsv`
in the movement corpus.

### Fuel cost (CONFIRMED, FM-001..004)

For a move of `L` light-years at warp `w`:

1. Group the fleet's ships by design. Each design has a mass per ship `m`,
   a ship count `n`, a cargo capacity per ship and an engine factor
   `f(w)`.
2. Assign the fleet's cargo (minerals and colonists in kT; fuel has no
   mass) to designs in order of increasing `f(w)`, each up to `n ×` its cargo
   capacity. Designs with equal `f(w)` keep the fleet's own design order
   (CONFIRMED, KB-4A Q: a Small Freighter and a Medium Freighter, both
   Quick Jump 5, 111 kT: 57 mg with the Small Freighter filled first; the
   other order gives 56).
3. Cost in tenths of a mg per design: `trunc(f(w)·L·(n·m + cargo assigned)
   / 2000)`; designs with `f(w) = 0` cost nothing.
4. Fleet cost in mg: `trunc((Σ tenths + 9) / 10)` (rounded up once per
   fleet).

`L` is `A` from the distance rule: `w²` for a partial move,
`min(trunc(D + 0.9999), w²)` on arrival.

Vectors (CONFIRMED):

- One QJ5 scout (18 kT), 25 ly at warp 5: `trunc(100·25·18/2000) = 22`
  tenths → 3 mg (FM-001 0).
- Seven QJ5 scouts, 36 ly at warp 6: `trunc(180·36·126/2000) = 408` tenths
  → 41 mg, not 7 × 6 (FM-001 42).
- Three QJ5 scouts and one AD8 scout (31 kT), 49 ly at warp 7:
  `trunc(500·49·54/2000) + trunc(100·49·31/2000) = 661 + 75` tenths →
  74 mg (FM-002 32).
- A QJ5 freighter carrying 70 kT with an AD8 scout: the cargo is charged
  at the freighter's engine (FM-002 34).
- Per-design truncation (FM-004 MS): a QJ5 scout and an LH6 scout (23 kT),
  4 ly at warp 2: `trunc(25·4·18/2000) + trunc(20·4·23/2000) = 0 + 0` →
  0 mg (one truncation of the sum would give 1). A QJ5 scout and a Fuel
  Mizer scout (20 kT), 25 ly at warp 5: `22 + trunc(35·25·20/2000) = 22 +
  8 = 30` tenths → 3 mg (not 4).
- Cargo on the cheapest engine first (FM-004 CA): a QJ5 freighter (31 kT)
  and an LH6 freighter (36 kT, 70 kT hold), 36 ly at warp 6 (factors 180
  and 105). With 70 kT: all on the LH6 freighter,
  `trunc(105·36·106/2000) + trunc(180·36·31/2000) = 200 + 100` → 30 mg.
  With 100 kT: 70 on the LH6, 30 on the QJ5,
  `200 + trunc(180·36·61/2000) = 200 + 197` → 40 mg.
- A warp-9 scout chasing a fleet that ends 55 ly away:
  `trunc(900·55·18/2000) = 445` tenths → 45 mg (FM-001 67).

### Not enough fuel (CONFIRMED, FM-001..004)

- Range on the current fuel: `R = trunc(fuel·1000 / C1000)` where `C1000 =
  trunc(Σ_designs trunc(f(w)·1000·(n·m + cargo)/2000) / 10)` (the cost of
  1000 ly in mg, truncated, not rounded up; above 100,000 the game uses
  `trunc(fuel / trunc(C1000/1000))`; `C1000 = 0` means unlimited). A fleet with enough fuel for
  the whole leg uses `max(R, w²)` instead.
- If the allowed distance exceeds `R`, the fleet moves exactly `R` (placed
  by rule 3 above) and its fuel becomes 0. Otherwise it pays the cost of
  the distance it moves, never going below 0.
- **Running dry.** After paying, the fleet has run dry when all of these
  hold: its fuel is 0; it was limited by `R` or paid a non-zero cost; it
  could not afford the whole leg at the start of the year; and it does not
  reach its destination this year (`A + 0.99999 ≤ D`), or `R = 0`. Paying
  the full cost of this year's move does not prevent it (FM-002 24 below).
  A fleet that has run dry gets the out-of-fuel message, gains no ram-scoop
  fuel this year, and the warp of its leg is lowered
  to the fastest warp at which the whole leg would cost no fuel (the
  lowest warp with a non-zero cost, minus one). CONFIRMED for QJ5, where
  this is warp 1; Fuel Mizer → 4, Settler's Delight → 6, Radiating
  Hydro-Ram Scoop → 6 (FM-004 WD). "Cost" is the rounded fleet cost of
  the whole remaining leg, so a short leg can give a higher warp: a Fuel
  Mizer scout with 0 mg and a 2 ly leg gets warp 5, because 2 ly at warp 5
  costs `trunc((trunc(35·2·20/2000) + 9)/10) = 0` mg. BINARY-ONLY: no
  free warp at all → the warp is left unchanged (a different message);
  every J-RC3 engine is free at warp 1, so this should not arise.
- A fleet with `R = 0` does not move.
- With exactly enough fuel for this year's move it moves the full
  distance, and it has still run dry if that leaves 0 and the destination
  is further away. A fleet that arrives with exactly enough fuel has not.
- A fleet that cannot afford the whole leg but keeps some fuel after this
  year's move has not run dry: it keeps its warp (CONFIRMED, KB-4A K:
  20 mg for a 39 mg leg, 15 left after the year, warp 6 kept, no
  message).
- Top-up (CONFIRMED, FM-004 TU): a fleet that had enough fuel for the whole
  leg at the start of the year ends the year with at least the fuel the
  rest of the leg needs (capped at its tank; the cap was not exercised), so
  per-year rounding never strands it.

Vectors (CONFIRMED, FM-001, QJ5 scout at warp 6 heading +160 x; fuel →
distance moved, end fuel 0, warp set to 1): fuel 1 → 6 ly, 3 → 18, 5 → 30,
fuel 0 → no move. At warp 9, fuel 10 → 12 ly.

Running dry while paying in full (CONFIRMED, FM-002, QJ5 scout, 18 kT,
warp 6, `C1000 = 162`):

| Fleet | Leg | Fuel | `R` | Moves | Pays | End fuel | Warp after | Event |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 24 | +100 x | 6 | 37 | 36 | 6 | 0 | 1 | out of fuel |
| 29 | +5 x | 1 | 6 | 5 (arrives) | 1 | 0 | 6 | completed orders only |

Fleet 24 is not limited by `R` (37 ≥ 36) and pays exactly its fuel
(`trunc(180·36·18/2000) = 58` tenths → 6 mg), but it needed 17 mg for the
100 ly leg and stops 64 ly short, so it has run dry.

Vectors (CONFIRMED, FM-004 LR, each heading +100 x, ends with 0 mg; these
are the cases where `R` and `trunc(fuel·20000/M)` differ by 1 ly):

| Fleet | Warp | Fuel | `C1000` | Moves | Warp after |
|---|---:|---:|---:|---:|---:|
| LH6 scout (23 kT) | 6 | 3 | 120 | 25 | 1 |
| DLL7 scout (27 kT) | 7 | 4 | 148 | 27 | 1 |
| LH6 scout | 8 | 25 | 862 | 29 | 1 |
| 3 AD8 scouts (93 kT) | 8 | 31 | 534 | 58 | 1 |
| LH6 freighter (36 kT) + 10 kT | 6 | 7 | 241 | 29 | 1 |
| Settler's Delight scout (16 kT) | 10 | 23 | 460 | 50 | 6 |

Worked (first row): `C1000 = trunc(trunc(105·1000·23/2000)/10) =
trunc(1207/10) = 120`; `R = trunc(3·1000/120) = 25` (the corpus formula
gives `trunc(3·20000/2415) = 24`).

Top-up vectors (CONFIRMED, FM-004 TU, QJ5 scout, warp 9, leg 126 ly):
fuel 102 → moves 81, pays 66, has 36, topped up to 37 (the remaining 45 ly
cost 37); fuel 101 → cannot afford the whole leg (103), no top-up, ends
with 35.

### Ram scoops and free warps

A moving fleet that did not run dry and was not stopped by a minefield
gains fuel when its engines are free at the ordered warp:
`gain = Σ_designs n·k·L'`, where `L'` = `min(trunc(D − 0.99999), A)` and,
for a design whose engine (first slot) has `f(w) = 0`, `k` = engines per
ship `e` × (1, or 3 if also free at `w+1`, 6 if free at `w+1` and `w+2`, 10
if free through `w+3`); capped at the tank's free space.
CONFIRMED (FM-002..004): warp 1 on every engine, Fuel Mizer at warps 1–4,
Settler's Delight at 1–6, Radiating Hydro-Ram Scoop at 4 and 6, several
ships of one design, a mixed fleet (only the free design gains), the tank
cap, and arrival years. Not exercised: designs with more than one engine
(`e > 1`), an engine outside the first slot, minefield stops.

Note that `L'` is `trunc(D − 0.99999)`, not `D`, on arrival: a Settler's
Delight scout arriving 10 ly away at warp 4 gains `6·9 = 54`; at
(+7, +7) (`D = 9.90`) it gains `6·8 = 48`.

Vectors (CONFIRMED, FM-004 RS, one scout, 100 mg, heading +100 x, gain):

| Engine | w1 | w2 | w3 | w4 | w5 | w6 | w7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fuel Mizer (free to 4) | 10 | 24 | 27 | 16 | 0 | | |
| Settler's Delight (free to 6) | 10 | 40 | 90 | 96 | 75 | 36 | 0 |
| Radiating Hydro-Ram (free to 6) | | | | 96 | | 36 | |

Three Fuel Mizer scouts at warp 2 gain 72; a QJ5 scout with a Fuel Mizer
scout at warp 2 gains 24. A Settler's Delight scout with 250 mg of 300 at
warp 3 gains 50 (raw 90, capped).

### Chasing another fleet (CONFIRMED, FM-001..003)

1. Fleets move in id order. Fleets whose destination is another fleet are
   deferred until every ordinary fleet has moved.
2. Deferred fleets then move in rounds (at most 10), in id order. A chaser
   has `rem = w²` and `moved = 0` at the start of the year. In a round, its
   step is `rem` if its target has already finished moving, else
   `min(rem, trunc((rem + moved + 4)/5))` (a fifth of `w²`, rounded up). It
   heads for the target's current position, using the distance, arrival
   and rounding rules above with `A = min(trunc(D + 0.9999), step)`.
3. A chaser that arrives on its target has finished, and the target is
   marked as having finished moving. If that target is itself a chaser
   that has not finished, it therefore stops for the year (its waypoint is
   then settled by rule 8 below), and any other chaser of it now takes
   its whole remainder in one step (rule 2). LEGACY BUG (CONFIRMED; see
   "Chain freeze" below).
4. Otherwise `moved += step`, `rem −= step`, and it stays deferred while
   `rem > 0`.
5. Fuel is charged on the year's total distance (`moved + step`), refunding
   the previous round's charge, so rounds add no extra rounding.
6. CONFIRMED for a chaser whose target has finished moving (KB-4A C: 5 mg,
   `R` 7, moved 7 ly toward the target's end position, 0 mg, warp lowered
   to 1, out-of-fuel message); BINARY-ONLY for the per-round steps
   (FM-001..003 chasers all had full tanks): each round applies
   the ordinary fuel rules to the step, with `R` reduced by `moved` and
   "the whole leg" meaning the distance to the target's current position.
   A chaser limited by `R` moves only that far and ends with 0; a chaser
   that runs dry has its warp lowered as above and stops for the year; a
   chaser that could afford the whole leg is topped up after each round;
   ram-scoop fuel is gained per round on that round's step.

After every fleet has moved, waypoints are settled (CONFIRMED, FM-001..003):

7. Every waypoint whose destination is a fleet takes that fleet's position
   at the end of movement. Exception: when the target went through a
   stargate or a wormhole this year, other players' waypoints aimed at it
   stop at its departure point and lose it, while its owner's own follow
   it (`OBJECTS.md` "Stargates" and "Travel").
8. Every fleet whose position equals its next waypoint exactly completes
   that waypoint ("completed orders" when it was the last one). This
   applies to a fleet that has used its movement or never moved.

So when a chaser lands on a fleet that is chasing it, both complete their
waypoints. A fleet that is caught while heading somewhere else keeps its
orders, and a chaser that did not reach its target keeps chasing, its
waypoint now at the target's end-of-year position.

Vectors (CONFIRMED): two fleets 20 ly apart chasing each other at warp 4:
the lower id moves 12, the higher 8. A at 1200 chasing B at 1215 (warp 9),
B chasing Z at 1225 (warp 9), Z moving +60 at warp 5: with ids in order
A < B < Z, A reaches 1215 and B does not move; with B < A < Z, all three
end at 1250.

Waypoint vectors (CONFIRMED; ids in order, start → end, waypoints left
after the year):

| Case | Lower id | Higher id | Result |
|---|---|---|---|
| FM-001 71/72, mutual chase, warp 4 | 1200 → 1212 | 1220 → 1212 | both complete |
| FM-002 39/40, mutual chase, warps 4 and 3 | 1150 → 1164 | 1170 → 1164 | both complete |
| FM-003 29/30, mutual chase, warps 4 and 1 | 1150 → 1159 | 1160 → 1159 | both complete |
| FM-003 21/22, mutual chase, warp 1, gap 6 | 1150 → 1151 | 1156 → 1155 | neither; waypoints now 1155 and 1151 |
| FM-003 0–2, A chases B, B chases Z, Z +60 | A 1200 → 1215 | B stays 1215 | A completes; B keeps chasing Z, waypoint 1250 |
| FM-002 41/42, C3 chases T3 head-on | T3 1080 → 1055 | C3 1040 → 1055 | C3 completes; T3 keeps its own waypoint |

#### Chain freeze (LEGACY BUG, CONFIRMED)

The original uses one "finished moving" mark both for "this fleet has used
its movement" and for "a chaser landed on this fleet". So whether a
chaser in a chain moves at all depends on fleet numbers, not on geometry:

- With A chasing B and B chasing C, numbered **A < B < C**: C (ordinary
  or chasing) and B are both deferred. A moves first in each round; if
  its first step reaches B's start, B is marked finished and never
  moves that year. A ends on B's start.
- Numbered **C < B < A** (or any order where B's turn comes before A
  reaches it): B moves toward C in its rounds (the whole remainder in one
  step once C has finished), then A follows B; each covers the full
  distance its speed allows.

Measured: FM-003 (A 1200 chasing B 1215, B chasing Z, Z moving +60; ids
A < B < Z: B did not move; B < A < Z: all ended at 1250). MF-02 (stars-elegy
#47, PARITY "Minefield lane", "Followers"): C flies 81 ly, B 10 ly behind
follows C, A 10 ly behind B follows B; numbered A < B < C, A reached B's
start in its first 17-ly step and B never moved, 6 of 6 chains. Numbered
C < B < A, B and A each moved their whole remainder in one step after
their target finished. In a minefield the numbering also changes the stop
odds, since the check uses each step's length: a frozen fleet does not
move, and a fleet moving its whole remainder in one step crosses at a
higher effective warp (A was stopped in 2 of 6 C < B < A chains;
`OBJECTS.md`, minefields).

Binary (stars-decomp `fleet-movement.md`, "Following a fleet"): landing
on the target sets the target's processed bit, which is the bit a
deferred chaser checks to know it is done.

**Implementing:** Elegy reproduces the freeze behind a named switch
(project default for deterministic LEGACY BUGs), with the processed mark
shared exactly as above. With the switch off, a chaser landing on a
waiting chaser would leave the target to move in its own rounds; that
alternative is Elegy's choice, not the original's.

### Refuelling at a starbase (CONFIRMED, FM-004 DK)

After production, a fleet orbiting a planet with a starbase that has a
dock (not an Orbital Fort), owned by the fleet's owner or by a player who
treats the fleet's owner as a friend (KB-4A), is set to its tank capacity, including a fleet that arrived
there this year. Fuel above capacity is reduced to capacity there, but not
in deep space (a scout holding 400 mg of 300 keeps 400 away from a
starbase). A fleet that leaves the planet this year is not refuelled, nor
is one at a planet without a starbase.

### Alternate Reality colonists in flight (CONFIRMED, TK-117)

An Alternate Reality fleet carrying more than 10 kT of colonists loses
`trunc((C + 11)·3/100)` kT (C the colonists in kT) in each year it moves,
before the move, with a message to the owner. A fleet that does not move
loses nothing. Vectors (TK-117, deep space): 10 → 10, 11 → 11, 40 → 39,
200 → 194 moving; 200 stationary → 200. TK-107 matches too (25 → 24,
100 → 97).

What counts as moving (CONFIRMED, OT-6): the loss is taken when the fleet
starts its move, before the fuel limit and before a chaser is put off to
the chase passes. A fleet loses if it has a waypoint 1 with a warp above 0,
even when:

- waypoint 1 is the fleet's own position (100 → 97);
- the fleet has no fuel and does not move (100 → 97);
- the fleet is chasing another fleet (100 → 97, once a year, not once per
  pass).

A fleet loses nothing when it has no waypoint 1 or when waypoint 1's
warp is 0 (CONFIRMED, OT-6 and TK-117: 100 → 100). From the program
(BINARY-ONLY), the fleets that the other movement gates stop also lose
nothing: a waypoint-0 transport or mine-laying task, the registration
penalty, engine failure, and a stargate jump.

The message (`MESSAGES.md` 0x0c1) is sent only when the loss is at least
1 kT. A fleet with 11–22 kT loses 0 and gets no message (CONFIRMED,
OT-6: 22 → 22 with no message, 23 → 22 with one).

### Inner Strength colonists breed in transit (CONFIRMED, OT-5)

Each year, after movement and before production (turn order step 3b), every
Inner Strength fleet carrying C kT of colonists breeds
`g = trunc(C·growth/200)` kT, `growth` being the race's growth rate in
percent. If `g` is 0, a draw `Random(3)` of 0 makes it 1 (BINARY-ONLY).

1. As much of `g` as fits in the fleet's free cargo space is added to its
   colonists, with message 0x0fb for the amount, if any.
2. The rest goes to the planet the fleet orbits if the fleet's owner owns
   it, as population, with message 0x158. Otherwise the rest is lost and
   there is no message.

Vectors (OT-5, growth 15%): a full 2100 kT fleet over its own planet
breeds 157, all of it landing on the planet, which then grows on it that
year; 200 kT in a 210 kT hold in deep space takes 10 and loses 5; a full
fleet over an enemy planet gains nothing and the planet gets nothing.

### Fuel cannot be unloaded onto a planet (CONFIRMED, FM-101..105)

A waypoint unload of fuel at a planet moves nothing: the fleet keeps all
its fuel and the unload order is cleared as usual (FM round 2, `PARITY.md`
"Fleet Movement": "unload all" at the owner's own planet without a starbase, 300 mg kept). A planet
neither takes nor supplies fuel, and deep space behaves the same way
(`TAKEOVER.md`). Fuel moves only between fleets. A direct cargo transfer
of fuel to a planet was not run.

### Designs without a full set of engines (LEGACY BUG, CONFIRMED FM-105)

A design whose engine slot is empty or not filled to the hull's maximum
uses engine factor `f = 99999` at every warp (it can still move).

Each stack's fuel term `trunc(f·L·M/2000)` (`L` light-years, `M` its mass
plus cargo, Fuel cost above) is computed with 32-bit integers when
`M < 200`, or when `f·L < 500000` and `M < 4000`, or when
`f·L < 100000` and `M < 20000`; otherwise in floating point. In the
integer form the product `f·L·M` keeps only its low 32 bits (unsigned) and
is then divided as a signed 32-bit number. With J-RC3 engines this never
wraps. With `f = 99999` it does for the range estimate (`L = 1000`):

- A Large Freighter with one of its two Long Hump 6 engines, 134 kT, warp
  5: `99999·1000·134 = 13,399,866,000` keeps `514,964,112`, so `C1000 =
  trunc(trunc(514964112/2000)/10) = 25748` and `R = trunc(fuel·1000/25748)`.
  Moving `R` costs far more than the tank (25 ly: `trunc(99999·25·134/2000)
  = 167498` tenths), so the fleet moves `R` and ends with 0 mg.
- Vectors (CONFIRMED, FM-105): fuel 200, 50, 500 mg → 7, 1, 19 ly, 0 mg
  left.

This is a deterministic arithmetic overflow, not memory corruption: the
result depends only on the factor, distance and mass. Elegy reproduces it
in one isolated function (32-bit wrap of the integer-form product) so it
can be switched off. FM-105 used an edited design; whether the original's
ship designer lets a player save one is not established.

### Other movement rules

- A fleet whose current task is "transport" or "lay mines" does not move.
  A transport task stays current until a load phase finds every load
  satisfied, so an unmet "wait for" holds the fleet, while a satisfied
  transport (an unload, for instance) is cleared before movement and the
  fleet moves. CONFIRMED for mine laying (OB-014-D, OB-019: `OBJECTS.md`
  "Laying") and for transport (KB-4A T1: "wait for 50% ironium" at a
  planet with none held the fleet; T2: "unload all" unloaded and moved).
- Warp 10 with an engine not rated for warp 10 (rated: Interspace-10,
  Enigma Pulsar, Trans-Star 10, Trans-Galactic Mizer Scoop, Galaxy Scoop):
  each ship is destroyed with probability 1/10 each year it moves
  (MEASURED, FM round 2: 11 of 100 and 5 of 50 ships lost; fuel left with
  the lost ships in proportion; CS-003-W: 58 of 660, none of 300 with
  rated engines).
- Cheap Engines: at warp 7 or more, a 1 in 10 chance each year that the
  fleet does not move (MEASURED, FM round 2: 2 of 40 fleets stopped at
  warp 7, 0 of 20 at warp 6).
- Improved Fuel Efficiency: engine factor `f − trunc(15f/100)`
  (CONFIRMED, KB-4A E: warp 6, 36 ly, 295 mg left, 294 without IFE; C at
  warp 9).
- Radiating Hydro-Ram Scoop engines kill
  `max(1, trunc(colonists·trunc((86 − mid)/2)/100))` kT of carried
  colonists (at most all of them) per year moved, where `mid` =
  `trunc((radiation low + radiation high)/2)`; not for radiation-immune
  races or when low + high ≥ 170. CONFIRMED for `mid` 50 (KB-4A H: 70 →
  58 moving, message 0x74; 70 kept when stationary); the immune and
  ≥ 170 exemptions are BINARY-ONLY.
- Fuel transports add 200 mg each per year to a stationary fleet
  (CONFIRMED, CS-003-W: 200 with one, 600 with three, 200 with a
  Super-Fuel Xport). Fuel generators (anti-matter) add 50 mg each. Both
  are capped at the tank (CONFIRMED, KB-4A G, X: 100 → 150 and 230 → 250
  with a 250 tank; 1,000 → 1,200 and 2,150 → 2,250 with a 2,250 tank).
- Refuelling at a starbase (above) also happens at another player's
  planet whose owner treats the fleet's owner as a friend, and not at a
  starbase without a dock (an Orbital Fort). CONFIRMED (KB-4A F1–F5: a
  friend's Space Station filled 10 → 300 and lowered 400 → 300; a neutral
  owner's did not; the own Orbital Fort did not; the own Space Station
  did).

## Scores and victory conditions

Computed once a year for every player, after all of the year's other
phases (turn order step 8), and written to each player's `.M` file. The
vectors are KX-003 S1 (`PARITY.md`); S2 and S3L (four more player-years)
also matched.

### Score (CONFIRMED, KX-003)

The sum of five terms:

| Term | Rule | KX-003 S1 player 0 | player 1 |
|---|---|---|---|
| Planets | per owned planet `min(6, ceil(P/1000))`, P the population in units of 100 after this year's growth | 287, 1001, 1000, 5739, 7412 → 1+2+1+6+6 = 16 | 287, 1148, 1, 3450 → 8 |
| Starbases | 3 per owned starbase whose hull has a dock (an Orbital Fort scores 0) | Space Station ×2 (+ a Fort) → 6 | Fort → 0 |
| Resources | `trunc(R/30)`, R = the year's resources over owned planets computed from population **after** growth (not the pre-growth figure research uses) | 1552 → 51 | 498 → 16 |
| Tech | per field at level L: L (L ≤ 3), `2L − 3` (4–6), `3(L − 3)` (7–9), `4L − 18` (10+) | 6 × 86 = 516 | 3, 4, 6, 7, 9, 10 → 69 |
| Ships | below | 34 | 8 |
| **Score** | | **623** | **101** |

Ships: every ship in the player's fleets (starbases excluded) is
**unarmed** (power 0), an **escort** (power 1–1999) or a **capital ship**
(power 2000 or more). With N owned planets and U, E, C ships of each
class: `trunc(min(N, U)/2) + 2·min(N, E) + trunc(8·N·C/(N + C))` (last term
0 when C = 0). S1 player 0: N = 5, U = 7, E = 3, C = 10 → 2 + 6 + 26;
player 1: N = 4, U = 1, E = 5, C = 0 → 0 + 8 + 0.

Power of a design (summed over its slots):

- Beams: `(range + 3)·damage·count/4`, divided by 3 for shield sappers.
  The beam total is then scaled by capacitors: a factor starts at 1000
  and each capacitor multiplies it by `(100 + pct)/100`; if it changed,
  `beam = beam·min(255, trunc(factor/10))/100`. Finally
  `beam = beam + beam·(speed − 4)/10`, `speed` being the design's battle
  speed code (`COMBAT.md`).
- Torpedoes and missiles: `(range − 2)·damage·count/2`.
- Bombs: `(kill rate in tenths of a percent + installations killed)·count·2`.

CONFIRMED for the class boundaries KX-003 reached: 4 Omega Torpedoes
(1896, escort), 5 (2370, capital), 2 Cherry Bombs (140, escort), an X-Ray
Laser scout (escort), unarmed scouts.

Details:

- **Truncation** (BINARY-ONLY). Each slot's term is truncated before the
  slot terms are summed: a beam slot to `trunc((range + 3)·damage·count/4)`,
  then `trunc(…/3)` for sappers; a torpedo slot to
  `trunc((range − 2)·damage·count/2)`. Each capacitor's step of the factor
  is truncated too. No legal design was found where per-slot truncation
  moves a ship across the 2000 boundary, so no run can confirm it.
- **Speed code** (CONFIRMED, OT-6). `speed` is the design's battle speed
  from its own engines and **empty** mass, with no cargo, no War Monger
  bonus and no other race bonus, limited to 0..8. OT-6: a Battle Cruiser
  with 7 Big Mutha Cannons (beam 1785, speed code 5) scored as an escort
  for both a War Monger and a non-War Monger owner (1785 + 178 = 1963). The
  War Monger bonus would have made it 2320, a capital ship. A 9-Disruptor
  design (1899 → 2088) scored as a capital ship for both, so the speed term
  is applied.
- Capacitors and sappers are BINARY-ONLY.

### Yearly score record

Each player's record holds the score, the resources R, the planet count,
the starbase count (only starbases whose hull has a dock, as for the score:
an Orbital Fort is not counted; CONFIRMED, KX-003 S1, where player 0's two
Space Stations and a Fort count 2 and player 1's Fort counts 0), U, E, C, the sum of the six tech levels, the rank and a
flag word. Rank = 1 + the number of players with a strictly higher score
(CONFIRMED, S1, S2, S3L). The flag word is the player number in the low 5
bits, 0x20 always, and one bit per victory condition the player meets
this year **whether or not the condition is enabled** (CONFIRMED for
capital ships, disabled in S1 and flagged): 0x40 planets, 0x80 tech,
0x100 score, 0x200 lead, 0x400 resources, 0x800 capital ships, 0x1000
highest score after N years. S1: player 0 `0x0ae0`, player 1 `0x0021`.

### Victory conditions

The game's settings hold ten values (the new-game dialog's defaults in
brackets): planets owned `(v + 4)·5`% [60], tech level `v + 8` [22] in
`v + 2` fields [4], score `(v + 1)·1000` [11000], lead over second place
`(v + 2)·10`% [100], resources `(v + 1)·10` thousand [100], capital ships
`(v + 1)·10` [100], highest score after `(v + 3)·10` years [100], the
number of conditions needed [1], and the minimum years `(v + 3)·10` [30].
Each of the first seven is on or off. Tests, per player and year:

- Planets: owned planets ≥ `round(total planets·pct/100)` (CONFIRMED,
  S1: 24 planets at 20% need 5; 5 met, 4 did not). The rounding is to the
  nearest whole number with halves rounded up (BINARY-ONLY): 30 planets at
  25% need 8.
- Tech: the number of fields at the level or above ≥ the field count
  (CONFIRMED met and unmet, S1).
- Score ≥ the threshold; resources: `trunc(R/1000)` ≥ the threshold in
  thousands; capital ships: C ≥ the threshold (CONFIRMED for capital
  ships, S1; the others BINARY-ONLY).
- Lead: with scores sorted, `second·(100 + pct)/100 ≤ top` flags the top
  player (CONFIRMED, KX-003 S1: 101·120/100 ≤ 623). When two or more players
  share the top score, `second` is that same score, so the test fails and
  nobody is flagged (BINARY-ONLY).
- Highest score: the year index (years since 2400) ≥ the year count and
  exactly one player has rank 1 (BINARY-ONLY).

Deciding the game (BINARY-ONLY), each year:

1. The "game decided" mark is cleared. It is worked out again from
   scratch every year; nothing carries over from an earlier win.
2. With one player in the game, nothing further happens.
3. A player with no planets and no ships becomes dead (message to the
   others).
4. If all but one player are dead, the game is decided. The survivor
   (the last player in player order with rank 1, if not dead) gets the
   sole-survivor message 0x0bc, and every other player gets 0x0b8.
5. Otherwise, once the year index is at least the minimum years, the
   number needed is the setting's raw value, capped at the number of
   enabled conditions (the seven conditions, not counting the tech field
   count, which is part of the tech condition). If the number needed is 0
   (the raw value is 0, or no condition is enabled), nobody wins. Elegy's
   "treat a value below 1 as 1" is not the original's rule.
6. Every player meeting at least the needed number of enabled conditions
   wins. If anyone wins, the game is decided and: each dead player gets
   0x0b8; each winner gets 0x0b6 if they are the only winner, or 0x0b7 if
   there are several; every other player gets 0x0b5.

Because of step 1, a game is decided again in every year its conditions
still hold, and the messages are sent again each of those years. A year in
which no one wins leaves the game undecided, even if an earlier year
decided it. The program also reads the mark when it decides whether other
players' scores are visible (not measured). `MESSAGES.md` describes the
message slots.

## Random events

When the game's random events option is on, the end of production (after
growth and research, turn order step 4) runs, in this order: a comet
strike, a planetary climate change, a new-minerals discovery and the
Mystery Trader (`OBJECTS.md`). With the option off none of them runs
(CONFIRMED, KX-004 E0: 40 years, no event).

"Protected" below means: the planet is owned, its population (after this
year's growth) is more than 50 units, and the year index (years since
2400, before the year advances) is below 20. Population is in units of
100 colonists.

All three are CONFIRMED by KX-004: 23 events (9 comets, 2 climate
changes, 12 new-mineral finds) from 17 distinct random streams and three
game states, each reproduced exactly (concentrations, environment, surface
minerals, population, queue and every message) by replaying the
original's random generator with the draw order below, plus the
protection and early-year cases (`PARITY.md` KX-004). That the original
environment value moves with the current one is BINARY-ONLY (the dumps
used do not show it). The probabilities are BINARY-ONLY: the oracle
cannot sample them, since each startup tick gives one fixed stream.

### Comet strike

1. With chance 1/20 (`rand(20) = 0`) pick a planet `rand(planets)`, owned
   or not.
2. Stop (no further effect or draw) if the planet is protected, or if the
   year index is below 10 (CONFIRMED, S3: no change at index 5).
3. Size `e = rand(4)`: small, medium, large, huge.
4. Message axis order `A`: start `[0, 1, 2]`; for i = 0, 1, 2 swap `A[i]`
   with `A[rand(3)]`.
5. Base amounts `b[i] = 50 + rand(250)` for minerals i = 0, 1, 2
   (ironium, boranium, germanium).
6. Struck-mineral order `B`: start `[0, 1, 2]`; swap `B[0]` with
   `B[rand(3)]`, then `B[1]` with `B[1 + rand(2)]`.
7. Messages: every player gets one naming the planet. The owner, unless
   its race is Alternate Reality, gets the "colonists killed" form, which
   also names environment axes `A[0..]` (one for small, two for medium,
   three for large and huge); everyone else gets the plain form.
8. Population (owner not AR): `P −= trunc(P·(20e + 25)/100)`, i.e. 25, 45,
   65 or 85% killed, applied to this year's grown population.
   Vectors (CONFIRMED): small 9237 → 6928; medium 9237 → 5081; large
   8110 → 2839; huge 9237 → 1386.
9. For k = 0 .. min(e, 2), mineral `m = B[k]`: `b[m] += 3000 + rand(17000)`;
   then its concentration `+= 50 + rand(50)`, and for a huge comet a further
   `15 + rand(15)`; capped at 200 (CONFIRMED: huge comet, 112 → 200).
10. Surface minerals: every mineral, struck or not, gains `trunc(b[i]/16)`
    kT (3–18 unstruck, 190–1268 struck).
11. Environment: for axis d = 0 .. min(e, 2) **in index order** (gravity,
    then temperature, then radiation): `s = 3 + rand(3)`, a huge comet adds
    `3 + rand(3)`; `rand(2) ≠ 0` makes it negative. The current and the
    original value both move by `s`, each clamped to 1..99.
12. The planet's production queue loses every item except the automatic
    ones (Auto Mines, Auto Factories, Auto Defenses, Auto Alchemy, Auto
    Min/Max Terraform, Auto Mineral Packets), which keep their counts
    (CONFIRMED: Auto Factories ×5 kept, Factory and a ship design dropped).

**LEGACY BUG (CONFIRMED, KX-004 S2):** the axes the owner's message
names come from `A`, while the axes that move are the first `e + 1` in
index order. A small comet on planet 15 moved gravity +4 while the owner's
message named radiation. For large and huge comets both cover all three
axes. It is deterministic and affects only the message text.

Unprotected unowned planets are struck the same way (no population,
messages to every player). An AR owner gets the plain message and loses
no population (BINARY-ONLY: no AR owner was struck).

### Planetary climate change

1. With chance 1/20 pick a planet `rand(planets)`; stop if protected.
   There is no year-index minimum (CONFIRMED, S3: unowned planet 18 at
   index 5).
2. Axis `rand(3)`. The owner (if any) gets a message naming the axis.
3. Magnitude `3 + rand(3)`; if that is 3, it becomes `6 + rand(3)`. So 4 or
   5 (1/3 each), or 6, 7 or 8 (1/9 each). `rand(2) ≠ 0` makes it
   negative.
4. Current and original value move together, each clamped to 1..99.
5. The production queue is cut to the automatic items, as for a comet.

Vectors (CONFIRMED): S3, unowned planet 18 at year index 5, gravity
50 → 44; S5, owned planet 7 at index 30, radiation 50 → 44, owner message
naming radiation, queue cut to Auto Factories ×5.

### New minerals

1. With chance `1/(15 − size)` (`size` 0 tiny .. 4 huge; 1/15 on tiny),
   pick a planet `rand(planets)`.
2. Stop if the year index is below 10 (CONFIRMED, S3). No protection.
3. Mineral `rand(3)`. The owner (if any) gets a message naming the planet
   and mineral, even when nothing changes.
4. If that concentration is below 180, it rises by `5 + rand(15)` (5..19).
   The cap at 180 is BINARY-ONLY.

Vectors (CONFIRMED): +13 ironium, +8 germanium, +16, +10, +19, +5, +14 on
owned and unowned planets; unowned planets get no message.

### Mystery Trader appearance

Runs right after new minerals. This section is the rule for when a
Trader appears and what it carries, with the draw order an exact replay
needs. `OBJECTS.md` "Spawn and movement" covers its flight:

1. Nothing below year index 40. Chance draw: `rand(2)` when the year index
   mod 100 is 71, else `rand(3)` when it is 33, else `rand(4)` when the
   index mod 128 is 49, else no Trader in odd years and `rand(7)` in even
   ones. A Trader appears when the draw is 0.
2. Warp `8 + rand(5)`.
3. Two free coordinates, start then destination, each
   `1020 + rand(361 + 400·size)`.
4. `rand(2)`: 0 puts the start on the low edge (1020) and the destination
   on the high edge (`1380 + 400·size`); 1 the reverse.
5. `rand(2)`: 0 makes the free coordinate x, 1 makes it y.
6. Item: `rand(10) < r` (r as in `OBJECTS.md`) gives a ship when
   `rand(6) = 0`, else research; otherwise a part bit `1 << rand(13)`, with
   the reroll and late-year conversion of `OBJECTS.md`.
7. Every player gets the appearance message.

CONFIRMED by KX-004 S6–S10 (`PARITY.md`): 24 runs at year indexes 49, 71,
72, 73 and 133 gave 15 Traders and 9 empty years, each exactly as
replayed (warp, start, destination, item, messages). Index 133 shows the
mod-100 tests come before the odd-year rule. The part reroll and its
conversion to research were not exercised (BINARY-ONLY).

### Implementing

Elegy draws from its own generator, so only the rules matter, not the
original's stream. The draw order above is given so a parity harness can
replay oracle runs exactly; the comet's draw sequence after the planet is
`e`, three for `A`, three for `b`, two for `B`, then per struck mineral
`rand(17000)`, `rand(50)` (and `rand(15)` if huge), then per moved axis
`rand(3)` (twice if huge) and `rand(2)`.

## Game options during a turn

The game's option flags that matter after creation:

- **Random events**: gates the three events above, the Mystery Trader and
  wormholes (`OBJECTS.md`) and the ancient-artifact research bonus on
  a planet's new owner (`TAKEOVER.md`). CONFIRMED off (E0) and on (KX-004).
- **Public player scores**: a player's file holds another player's score
  record only if (a) the game has been decided, or (b) that player is dead,
  or (c) public scores are on and the year index of the file is at least
  20, i.e. from the 2420 file on (CONFIRMED, KX-004 E1: own record only
  through 2419, both from 2420 to 2548; E0 with the option off: own only
  through 2440). (a) and (b) are BINARY-ONLY. A player always gets its own.
- **Slower tech advances**: research (see Research, "Slower tech"; KX-003).
- **Accelerated BBS play, maximum minerals, galaxy clumping**: used only
  when the universe is created (`UNIVERSE.md`); the turn generator never
  reads them (BINARY-ONLY: no reference in the turn code).
- **Computer players form alliances**: read only by computer-player logic,
  which this specification does not cover.

## Open experiments

The KB sweep (`PARITY.md`, "KB batch 1" to "KB batch 4") tested the
BINARY-ONLY rules that Elegy's turn engine meets every year: economy,
population, production, research, the year's random draw order and
movement fuel. What is still BINARY-ONLY falls into two groups.

**Cannot be oracled, or has no observable effect.** An implementation
follows the reading; no experiment can contradict it in play.

- The duplicate-serial penalty and everything behind the cheater flag:
  halved growth, the ×4/5 resource cut (so a planet with 0 resources),
  the level-10 research cap and the registration movement gate. These
  need a duplicated or invalid serial, which oracle runs cannot use.
  Elegy has no registration scheme.
- The `max(1, …)` in hostile deaths on an empty planet (growth never runs
  there), and the floor of 10 on the maximum mines and factories (no
  planet reaches it).
- A zero-item queue arising in play. KB-2A wrote one directly; no order
  creates one.
- Ties between a mineral and resources as the limiting component of a
  unit, and the order of an Alternate Reality planet's two mining steps.
  Both orders give the same state.
- An Alternate Reality planet with maximum 0 reached by deleting the
  starbase's design. The result is the divide-by-zero crash above
  (LEGACY BUG; Elegy chooses its own rule).
- A fleet with no free warp when it runs dry: every J-RC3 engine is free
  at warp 1.
- The player-order permutation (step 1) with legal orders, and the step
  order where nothing observable differs: the race check against
  the pre-movement tasks (2a), the Trader encounter against bombing (6a,
  6b), the registration steps, design housekeeping, the report-age reset,
  and the file-only caches and option bits (8.3, 8.4).
- Options the turn generator never reads (accelerated BBS play, maximum
  minerals, galaxy clumping).

**Could be oracled, not yet run.** None of these is exercised by an
ordinary year. Each needs a targeted start, and they are queued behind
questions raised by Elegy's implementation:

- Scores and victory: per-slot truncation, capacitors and sappers in the
  power rating; the planets rounding at exact halves; the score and
  resources thresholds; the lead test with tied top scores; the highest
  score condition; deciding the game, and public scores (a) and (b).
- Rare events, by seed replay: an Alternate Reality owner hit by a comet,
  the 180 cap on new minerals, the Trader item reroll and conversion, and
  whether the original environment moves with the current one. The event
  probabilities themselves are confirmed only as draw-and-threshold logic
  in replayed streams, not as sampled rates.
- Movement: chasers taking per-round steps with limited fuel; the copying
  rule for fleets following a fleet; mine laying after battles; the other
  movement gates sparing Alternate Reality colonists; the Radiating
  Hydro-Ram Scoop exemptions (immune radiation, low + high ≥ 170); the
  `Random(3)` when Inner Strength breeding rounds to 0.
- Maximum population: Hyper-Expansion with OBRM, and OBRM on an Alternate
  Reality starbase maximum.
- Drops after movement: the capture tech attempt and artifact draws in
  the year's sequence. These are coordinated with the takeover lane.

## Sources

- Oracle: PG-001..003, PQ-001, KX-001..005, KB-1..4, OT-1..6 and TK-117 (`PARITY.md`); FM-001..004 movement
  corpus (`PARITY.md`, "Fleet Movement", and `experiments/fm00N/`).
- White-box readings: private `stars-decomp` (population, economy,
  research, mining, production, movement and fuel notes, and the turn
  generation routine for "Turn order"; model checks that
  reproduce the PG, PQ and FM observations listed above).
