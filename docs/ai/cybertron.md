# Cybertron (PP computer player)

Cybertron is the computer player of definition-file type 5, with the PP
race of `../AI.md` §3. This file specifies its own turn. The shared
rules it calls (what it sees, state leaking between computer players,
research, starbase designs, planet automation, scrap orders, the design
builder, ageing, splitting, merging and the shared fleet rules) are in
`../AI.md` and are named here by section.

Status (cases in `../PARITY.md`, "Computer players"):
- Ship designs are CONFIRMED (AI-19): the predicted design orders matched
  the AIX corpus in every year, 2400–2460.
- Starbase queueing is MEASURED (AI-20) and the fleet pass is MEASURED
  (AI-21): every own fleet's orders matched in every AIX year.
- Packets (§6): warps, attack packet counts and scanner-shot
  destinations (as a band) are MEASURED (AI-24); the draw bounds are
  MEASURED for the oracle's arithmetic only.
- Everything else is BINARY-ONLY unless marked.

Notation: `y` = year index; `lvl` = AI level 0..3 (easy, standard,
harder, expert); slot `k` = own ship design slot; `n(k)` = ships of
design `k` alive; `age(k)` = `y` − creation year of design `k`. "Holds a
design" means the slot is not empty. Every rule below that reads a
slot's age first checks that the slot holds a design, so Cybertron is
not affected by leaking design slots (`../AI.md` §1). It is affected by
the leaking armada parameters (§1 step 4).

## 1. Turn order

1. Research (`../AI.md` §4, Cybertron plan, 17%) and starbase designs
   (§5). Cybertron keeps no hubs.
2. Ship designs (§2).
3. Merge (`../AI.md` §10) the ships of slot 0, of slots 4–5, of slots
   14–15, of slots 6–9 and of slots 10–13, in that order, each as its own
   merge. Slots 1, 2 and 3 are never merged.
4. Parameters:
   - strength unit `s` = 1; when `y > 50`, `(y − 50)/10 + 1`; when
     `y > 100`, plus `((y − 100)/10)·(y/100)` (integer division
     throughout);
   - armada parameters: Cybertron computes potency 3 (when `y > 130`,
     `(y − 120)/20 + 3`, at most 50) and size 6 (when `y > 115`,
     `(y − 100)/22 + 6`, at most 12), but never uses them. Its armada rule
     reads the shared values another computer player left
     (`../AI.md` §1, "State leaking between computer players", LEGACY
     BUG, MEASURED, AI-18: with those values zeroed, every idle armada
     left home in 11 of 11 armada-years where AIX's stayed). Elegy's
     default clean per-player state gives Cybertron the values 0; the
     original's values come only with the legacy-compatibility switch
     (`../AI.md` §1);
   - design age limit `L` = 50 while `y < 120`, 70 while `y < 200`, 100
     while `y < 400`, else 300.
5. Design ageing (§3).
6. `y > 80`: split obsolete ships out (`../AI.md` §10), then split out the
   ships of slot 0, of slot 1, and of slots 2–3, each as its own split.
7. Planet notes (§4.1), fleets (§5), production (§4.2) visiting own
   planets in the shuffled order of `../AI.md` §2.
8. Planet automation (`../AI.md` §7) with Cybertron's starbase rule
   (§4.3), packets (§6), then the production queue fill.

Cybertron's memory between years is empty: every turn starts with no
remembered planet state (`../AI.md` §1, AI-10). The per-planet notes
below are made and used within one turn.

## 2. Ship designs (CONFIRMED, AI-19)

Each step builds its design with the builder of `../AI.md` §10, from one
of Cybertron's class lists below. A *range* `a..b` tries lists in random
order without repeats: with `m` = lists left, it draws `Random(m)` and
tries that list, stopping at the first success. So any list in the range
that can be built may result; none buildable means no design. The steps
run in this order every year:

| Step | Slot | When | Hull and lists |
|---|---|---|---|
| 1 | 0 | slot 0 holds a design whose hull is not Frigate, `lvl` ≥ harder, `n(0) = 0` and `y > 5`: delete it. Then, if slot 0 is empty | Frigate list 12 |
| 2 | 4 | empty and `y > 30` | Destroyer list 0 when `y ≤ 75`; if that fails, or when `y > 75`, range 0..4 |
| 3 | 5 | empty, slot 4 holds a design and `age(4) > 20` | Destroyer list 5 when `y ≤ 75`; if that fails, or when `y > 75`, range 5..9 |
| 4 | 2 | empty and `y > 20` | Privateer list 10 |
| 5 | 3 | empty, slot 2 holds a design and `age(2) > 20` | Privateer list 11 |
| 6 | 6–9, then 10–13 | the group's first slot is empty, and either (group 6–9 and `y > 40`) or (slot 6 holds a design and `age(6) > 30`; group 10–13 also reads slot 6) | see below |
| 7 | 14 | empty and `y > 30` | Battleship range 26..32; if none, Cruiser range 17..25; if none, Destroyer range 0..9 |
| 8 | 15 | empty, slot 14 holds a design and `age(14) > 20` | as step 7 |

Step 6, for a group starting at slot `g`: the target slot starts at
`g + 2`. Nubian range 33..35 into the target slot (on success the target
moves down one), then Battleship range 29..32 the same way, then
Battleship range 26..28 the same way. Then Cruisers fill the target slot
and every slot below it down to `g`: the first gets the range of the last
`3·(g − t + 3)` Cruiser lists ending at list 25 (`t` = the target slot),
each later one range 20..22, and slot `g` itself range 17..19. Finally
slot `g + 3` gets the first of Nubian list 16, Battleship list 15, B-52
Bomber list 14 and B-52 Bomber list 13 that can be built.

Slot 1 (the starting colony ship) is never designed.

In AIX (expert): the Scout design in slot 0 was deleted in 2406 and no
Frigate could be built (list 12 needs a Mine Dispenser 130). Privateers
came in 2421 (slot 2) and 2442 (slot 3), Destroyers in 2431 (slots 4 and
14) and 2452 (slot 5), Cruisers in 2448 (slots 6 and 7, where no list for
slots 8 and 9 could be built) and 2452 (slot 15).

### Cybertron class lists

One AI part class (`../AI.md` §5 "AI part classes") per hull slot, in
hull slot order.

| List | Hull | Classes |
|---|---|---|
| 0 | Destroyer | 8, 4, 4, 18, 17, 18, 20 |
| 1 | Destroyer | 8, 4, 4, 5, 17, 18, 20 |
| 2 | Destroyer | 8, 4, 4, 4, 17, 18, 19 |
| 3 | Destroyer | 8, 3, 3, 14, 17, 18, 19 |
| 4 | Destroyer | 8, 4, 3, 2, 17, 18, 20 |
| 5 | Destroyer | 8, 0, 0, 18, 17, 18, 19 |
| 6 | Destroyer | 8, 0, 0, 10, 17, 18, 19 |
| 7 | Destroyer | 8, 0, 0, 11, 17, 18, 19 |
| 8 | Destroyer | 8, 1, 1, 11, 17, 18, 19 |
| 9 | Destroyer | 8, 1, 1, 11, 17, 18, 11 |
| 10 | Privateer | 44, 10, 15, 4, 4 |
| 11 | Privateer | 44, 17, 11, 0, 0 |
| 12 | Frigate | 24, 26, 25, 10 |
| 13 | B-52 Bomber | 8, 21, 23, 23, 23, 12, 10 |
| 14 | B-52 Bomber | 8, 21, 22, 22, 22, 12, 10 |
| 15 | Battleship | 8, 14, 10, 33, 33, 33, 33, 33, 17, 20, 19 |
| 16 | Nubian | 8, 18, 20, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33 |
| 17 | Cruiser | 8, 20, 19, 4, 4, 13, 17 |
| 18 | Cruiser | 8, 20, 19, 4, 3, 3, 17 |
| 19 | Cruiser | 8, 20, 19, 3, 2, 10, 17 |
| 20 | Cruiser | 8, 19, 11, 0, 0, 0, 17 |
| 21 | Cruiser | 8, 19, 11, 0, 0, 18, 17 |
| 22 | Cruiser | 8, 19, 11, 0, 0, 10, 17 |
| 23 | Cruiser | 8, 19, 11, 1, 1, 11, 17 |
| 24 | Cruiser | 8, 19, 11, 1, 1, 0, 17 |
| 25 | Cruiser | 8, 19, 11, 1, 1, 10, 17 |
| 26 | Battleship | 8, 18, 10, 2, 2, 3, 3, 2, 17, 20, 20 |
| 27 | Battleship | 8, 20, 10, 2, 2, 3, 3, 2, 17, 20, 20 |
| 28 | Battleship | 8, 18, 10, 0, 0, 3, 3, 2, 17, 20, 11 |
| 29 | Battleship | 8, 18, 10, 1, 1, 0, 0, 1, 17, 11, 11 |
| 30 | Battleship | 8, 11, 10, 1, 1, 0, 0, 1, 17, 11, 11 |
| 31 | Battleship | 8, 20, 10, 1, 1, 2, 2, 1, 17, 11, 11 |
| 32 | Battleship | 8, 11, 10, 1, 1, 1, 1, 1, 17, 11, 11 |
| 33 | Nubian | 8, 11, 11, 1, 1, 1, 20, 20, 2, 3, 3, 15, 19 |
| 34 | Nubian | 8, 11, 11, 1, 1, 1, 1, 1, 1, 19, 19, 15, 19 |
| 35 | Nubian | 8, 20, 20, 2, 2, 2, 3, 3, 3, 19, 19, 15, 19 |

## 3. Design ageing

Ageing (`../AI.md` §10) with limit `L` (§1), for slots 4–5 (newest =
`DD`, the current Destroyer), 14–15 (newest = `GG`, the current guard
design) and 2–3 (newest = `FR`, the current freighter; the reported ship
count is `nFr`). After each check the newest design of that group is
unmarked, except that after the 14–15 check it is `DD` that is unmarked
again, so `GG` can stay obsolete (LEGACY BUG).

Warship groups (first slot `g` = 6, then 10): if slot `g` holds a design
with `age(g) > L`, walk slots `g + 3` down to `g`. A design with no ships
is deleted, except that slot `g` is kept (and marked) when any higher slot
of the group was kept. A design with ships is marked obsolete. No newest
design is exempted. `GR` = the group whose first slot holds the newer
design (none if neither does).

## 4. Production

### 4.1 Planet notes

Every planet owned by another player gets the AI threat mark `min(6,
e/250 + 1)`, plus 1 if it has a starbase, where `e` is the population
estimate as Cybertron's report holds it, in units of 400 colonists (the
estimate in colonists ÷ 400, `SCANNING.md` "What a planet report
contains"). So the mark is 1 below 100,000 colonists, 2 from 100,000,
and so on up to 6 from 500,000; a planet with no estimate counts as 0
colonists. (BINARY-ONLY: the threat mark only affects armada targets,
and no AIX armada ever picked one.) Each own planet with a starbase
notes which minerals are low: below 10 kT under an Orbital Fort, else
below 1,000 kT (used by §6).

The fleet pass (§5) also makes per-planet notes (inbound colonists, no
colonizable target here, no drop-off, guard present and weak). Those
notes are lost: production and the freighter drop-off choice never see
them, and a note about planet 0 lands on the last planet instead (LEGACY
BUG, MEASURED, AI-21: with the notes kept, 64 freighter-years in AIX
would differ). So, for example, a planet whose idle colony ships found
no target still builds colony ships.

### 4.2 Each own planet

In the shuffled order of `../AI.md` §2. A planet is skipped when any of
its four available amounts (`../AI.md` §7) is below its queue's cost.
`v` = the planet's value for the race, `o` = its value after the
terraforming the race can reach (`ESTIMATES.md` "Value and optimal value"), `g` =
growth rate × population in hundreds, `R` = available resources less the
queue's cost. Items are appended.

1. `v < 10`: Terraform ×`R/70 + 1`. Otherwise, `v < o` and `R > 70`:
   Terraform ×1.
2. Only at a planet whose starbase is not an Orbital Fort:
   1. **Colony ship** (slot 1) ×1 when fewer than 40 slot-1 ships exist
      and the colonizer test passes: always while `y < 60`; later by the
      distance to the nearest colonizable planet: over 353 ly no, over 300
      ly `Random(2)`, over 250 ly `Random(2)`, else yes. A second ×1 when
      `g > 15,000` and `y < 100`.
   2. **Freighter** (`FR`) ×1 when the population is over 200,000, slot
      2 holds a design, `nFr < 50`, and an own planet within 400 ly could
      take colonists (population + 21,000 × inbound count < 100,000).
   3. **Frigates** (only when slot 0 holds a Frigate): when `Random(4) ==
      0` and fewer than 10,000 slot-0 ships exist, with `c` = slot-0 ships
      in the first own fleet orbiting here: `c < 10` → slot 0 ×4 when
      `Random(2c + 1) == 0`; `c < 17` → the same after `Random(10) == 0`.
   4. **Attack fleet.** Guard candidate: `GG` when fewer than 40 guard
      fleets exist, with `Random(100) < 50` when another player's planet
      lies within 300 ly, else `Random(100) < 10`. Over 120 Destroyer
      fleets drop `DD`; over 250 group fleets drop `GR`. Then `r1 =
      Random(100)` and `r2 = Random(100)`; when `r2 ≥ 90` (mine or factory
      room under 100) or `≥ 60` (otherwise):
      - `GR` and `r1 > 50`: the group's first slot ×2 and second ×2 (each
        if it holds a design), third ×1 when `Random(100) < 75`, fourth ×1
        when `Random(100) < 50`;
      - else the guard candidate and `r1 > 25`: ×1;
      - else `DD` ×1.

### 4.3 Starbases (MEASURED, AI-20)

Every own planet in planet-id order (not shuffled) with no starbase,
value above 14 and at least 50,000 colonists gets, unless its queue
already holds a starbase item, ×1 of the newest Space Station family
design when every mineral concentration is above 15, else of the newest
Orbital Fort family design (`../AI.md` §5). The population counted is
after this turn's fleet pass: colonists Cybertron's own freighters
unloaded or loaded there this turn already count. Starbase upgrades
(`../AI.md` §7) start at year index 40.

## 5. Fleets (MEASURED, AI-21)

In AIX every own Cybertron fleet's resulting orders matched these rules
in all 61 years: 2,064 fleet-years, with waypoints, cargo, scrap, battle
plan and merges compared, and warps from `../AI.md` §11 "Warp choice".
Rules with draws were checked as sets of allowed outcomes (4
fleet-years needed that). Branches marked *not exercised* never fired in
AIX and stay BINARY-ONLY.

Cybertron's view of planets is `../AI.md` §1 (its file plus the planet
history). Cargo moves change the planet and fleet at once, so later
fleets in the pass see them.

**Pass A**, every fleet in fleet order, counts:
- other players' fleets go on the enemy list;
- own fleets holding slot 14–15 ships count as guard fleets;
- other own fleets: those with slot-0 ships count as scout fleets
  (with their slot-0 ships totalled); armed ones (ships of slots 4–13)
  go on the attack list and count as Destroyer fleets or group fleets,
  by a test that does not look at the fleet's designs (LEGACY BUG,
  BINARY-ONLY):
  - when the last warship group aged out this turn (§3) is group 6–9
    (group 6–9 aged out and group 10–13 did not), every armed fleet
    counts as a Destroyer fleet;
  - otherwise (no group aged out, or group 10–13 did), a fleet with two
    or more waypoints whose waypoint 1 is a planet, or a fleet orbiting a
    planet, counts as a group fleet; any other armed fleet (idle or bound
    for deep space or a fleet, and not in orbit) counts as a Destroyer
    fleet.

  A group fleet marks its planet (waypoint 1's planet when that is a
  planet, else the orbited planet), when another player owns it, as
  targeted. In AIX no warship group ever aged out, so only the second
  case occurred. These counts feed §4.2's "over 120 Destroyer fleets" and
  "over 250 group fleets" tests, and each attack-fleet item §4.2 queues
  adds one to the count of its kind (group, guard or Destroyer).

**Pass B**, every own fleet, first rule that applies (idle = one
waypoint):
1. **Obsolete** (every design in it marked obsolete; slots 0 and 1 never
   are; *not exercised*): moving with two or more waypoints, nothing.
   Orbiting an own planet with a starbase: scrapped. Orbiting an own
   planet without one: scrapped when `Random(5) == 0`. Otherwise it moves
   to the nearest own starbase (`../AI.md` §11); if there is none, it
   falls through to the rules below.
2. **Guard fleet orbiting a planet**: no order.
3. **Armada** (armed, no slot-4 ships; slot-5 Destroyers count): armada
   targeting (below). Then, if still idle, when `Random(100) < 75` it
   joins a buddy (`../AI.md` §11) over slots 6–9 (its first armed slot ≤
   9) or 10–13, radii 100 and 200 ly. A slot-5 fleet that joins a group
   fleet never merges with it, because those slots merge separately (§1
   step 3).
4. **Destroyers** (slot-4 ships): when `s ≤ 2 × slot-4 ships` or it has
   two or more waypoints, it takes an attack target (`../AI.md` §11).
   Then, if idle, when `Random(100) < 75` it joins a buddy over slots
   4–5, radii 100 and 200 ly.
5. Unarmed fleets with two or more waypoints: no order. Unarmed idle
   fleets:
   - **Scouts early**: `y < 6` and slot-0 ships: scrapped.
   - **Colony ships** (slot 1): the nearest colonizable planet
     (`../AI.md` §11; a planet never seen counts as not colonizable, and
     the value includes the race's terraforming reach). None: no order.
     Otherwise, at an own planet it first loads colonists up to 250 kT,
     clamped to its hold, then gets the colonize order, and the target
     counts as taken for later colony ships this turn.
   - **Slot-0 fleets** (`y > 40`, one waypoint, no freighters; *not
     exercised*): with more than 55 scout fleets, or more than 40 and
     `Random(3) != 0`, it joins a buddy over slot 0, radii 72 and 108 ly.
     If not, with more than 6 slot-0 ships and `Random(5) == 0`, it moves
     to a random nearby planet within 105 ly, avoiding starbases
     (`../AI.md` §11), with the task *lay mines* at warp 4. Otherwise,
     unless waypoint 0 already has that task, it lays mines where it is.
   - **Freighters** (slots 2–3): battle plan 4 (an order only when it was
     not already), then the freighter rule below.

**Armada targeting.** `W` = ships of slots 6, 7, 10 and 11, plus twice
those of slots 8 and 12; `B` = ships of slots 9 and 13 (bombers). `P`,
`A` = the shared armada potency and size, `P'` = `P/2`, `A'` = `min(A/2 −
1, 3)`. "Hard" = harder or expert.
1. A fleet keeps its target when it has two or more waypoints and
   waypoint 1 is a fleet within 250 ly, another player's planet, an own
   planet with a starbase, or a planet not seen this year.
2. In deep space: it moves to the nearest other player's planet within
   450 ly, else the nearest planet.
3. At an own planet: when `W < P` or `B < A`, a fleet that is not hard
   stays, and a hard one stays when `W ≤ 2P` and `W < 60`; otherwise up
   to three `Random(10)` draws, with tests on `W > 3P` and `W < 121`,
   decide whether it stays (*not exercised*: every AIX armada stayed by
   the first tests). A fleet that does not stay picks a target.
4. At another planet: when `W < P'` or `B < A'` it clears its task and,
   unless hard draws send it on (`W ≤ 2P` or `Random(10) > 4`, then `W ≤
   4P` or `Random(10) > 6`, then `W < 121` or `Random(10) > 6`, all three
   needed to retreat), retreats to the nearest own planet with a
   starbase. Not weak at an owned planet: it stays. At an unowned planet:
   pick a target.
5. Target: the planet with the best score, threat mark plus a distance
   bonus (under 50 ly +7, 100 +5, 150 +4, 200 +3, 300 +2, 500 +1). A
   planet already targeted counts only when its own `Random(4) == 0`
   (one draw per such planet, in planet-id order). The best score above
   1 wins; ties go to the closer planet (*not exercised*). It moves there at warp 4 and the
   planet is marked targeted. With no planet, it targets the nearest other
   player's fleet, if any.

In AIX the inherited `P` = 3 and `A` = 6 kept every armada at home (W ≤
4, no bombers), while buddy joins gathered new ships to it.

**Freighter rule.** In deep space: move to the nearest planet. At an own
planet: with up to 200,000 colonists there, unload all colonists and
look for a pickup; otherwise load up to 1,000 kT of colonists (clamped to
the hold) and look for a drop-off. At an unowned or AR planet, or one
with a starbase: carrying colonists, look for a drop-off, else a pickup.
At any other player's planet: unload colonists there as an invasion,
move toward the nearest own starbase, and look for a pickup (*not
exercised*). Pickup: the nearest own planet with a starbase and over
220,000 colonists (it can be the planet itself). Drop-off: the nearest
own planet within 400 ly with fewer than 20,000 colonists, else one
within 400 ly where population + 21,000 × inbound count is under 100,000.
No drop-off at an own planet: it unloads what it just loaded and stays.
It moves with no task.

Shared rules apply too: minefields are seen enlarged for the whole turn,
and the warp re-pick keeps the starbase exception only for a planet
exactly at waypoint 1 (`../AI.md` §11).

## 6. Packets (BINARY-ONLY unless marked; AI-24)

Own planets with a starbase at the start of the step, in the shuffled
order of `../AI.md` §2; a planet without one is skipped and draws nothing.
Each planet tries supply, then attack, then the scanner shot, and does at
most one of them. Items go to the front of the queue. `r` = the warp
rating of the best mass driver on the planet's starbase, `w = r + 3`
(the pair bonus below never applies to `w`).

**Packet marks.** A planet can carry a packet mark. All marks are clear
at the start of the step: the memory that would carry them, and the
original's skip-a-year and keep-shooting flags, is empty every turn
(`../AI.md` §1, AI-10), so marks act only within the turn. A marked planet
is not a supply or attack target. A successful attack marks its target.
A scanner shot tests and sets the mark of the planet whose id is one
higher than its destination (LEGACY BUG, MEASURED, AI-24); for the
highest-numbered planet that mark belongs to no planet.

- **Supply** (the starbase is an Orbital Fort, the planet has over 700
  kT of a mineral and at least 70 resources): up to 7 packets of that
  mineral to the nearest own unmarked starbase planet that is low on it
  (§4.1), within `3.5·k²` ly, `k` = the lower driver rating of the two
  (+1 for a planet with two drivers of its best warp). No draws, and it
  marks nothing. *Not exercised.*
- **Attack** (expert and harder always; standard when `Random(3) == 0`;
  easy never): with `M` = the planet's available minerals less queued
  costs, less 210, over 150: the nearest other player's unmarked planet
  (not AR) with a known non-zero population, whose starbase is fully known
  or absent, within `2.5·w²` ly, that the budget can kill. Kill mass
  `need = 16000·min(1000, 4(pop + 25)) / ((w² − c²)(95 − d))`
  (truncated), where `pop` is the population estimate as the report holds
  it, in units of 400 colonists (the estimate ÷ 400, `SCANNING.md`), `c`
  = the target's catch warp and `d` = its defense coverage estimate as the
  report holds it. With `f = q^(D/w²)`, `D` = the distance in ly and `q`
  = 0.875 with two drivers of the best warp, else 0.75 (so `f ≤ 1`, the
  share of the mass that arrives):
  - the budget is `C = min(M, 70·((R/2 − 5)/5))`, `R` = the planet's
    available resources (integer division), and a target qualifies when
    `need ≤ trunc(C·f)` (BINARY-ONLY);
  - the mass sent is `A = trunc(min(need, M) / f)`, divided by `f`, so
    more than the kill mass leaves the planet to cover the loss in
    flight, as `⌈A/70⌉` packets (MEASURED, AI-24: dividing gives AIX's
    packet count in 16 of 16 attacks, assuming `M` is at least the kill
    mass (`M` not reconstructed); e.g. need 284 at `f` = 0.75^0.807 gives 358 kT, 6 packets, as
    observed, where multiplying would give 225 kT, 4 packets).

  Packets of 70 kT, each of the mineral with the most left, at
  warp `w`, aimed at the target, which is then marked (MEASURED: AIX
  warps and packet counts, 16 of 16). The level test's `Random(3)` is the
  attack's only draw. No target, or `M` too small: the scanner shot.
- **Scanner shot**, below.

### Scanner shot (AI-24)

`W` = the galaxy width (`UNIVERSE.md`). Positions here are relative to
the map's corner (1000, 1000), so both coordinates run from 0 to `W`;
`(x, y)` is the shooting planet's position. Integer arithmetic.

1. **Direction.** `r7 = Random(7)`; `dir = r7`, except `dir = 1` when
   `r7 = 0`. (The original avoids repeating last year's direction, and with
   the empty memory that reads as 0.) So `dir` is 1..6, and 1 is twice as
   likely as the others.
2. **Edge point.** From `(x, y)` straight to the map edge:

   | `dir` | Heading | Edge point |
   |---|---|---|
   | 1 | +x, −y | `(x + y, 0)` when `W − x > y`, else `(W, y − (W − x))` |
   | 2 | −y | `(x, 0)` |
   | 3 | −x, −y | `(x − y, 0)` when `y < x`, else `(0, y − x)` |
   | 4 | −x | `(0, y)` |
   | 5 | −x, +y | `(0, y + x)` when `W − x > y`, else `(x − (W − y), W)` |
   | 6 | +y | `(x, W)` |

   (The original also has `dir` 0, `(W, y)`, and 7, the +x +y diagonal;
   neither can occur with the empty memory.)
3. **Slide.** `j = Random(3W/10) − 3W/20` (draw bounds: see below). On an
   edge `x = 0` or `x = W` (tested first, so a corner counts here): `y +=
   j`; if `y > W` the excess `e = y − W` and `y = W`; if `y < 0`, `e = −y`
   and `y = 0`; else `e = 0`; then `x` moves `e` inward (`x = e` on the
   `x = 0` edge, `x = W − e` on the `x = W` edge). Otherwise (on `y = 0`
   or `y = W`) the same with `x` and `y` exchanged. So a slide past a
   corner continues along the next edge.
4. **Inset.** `k = Random(w²)`. The first of these that holds: `y = 0` →
   `y = k`; `y = W` → `y = W − k`; `x = 0` → `x = k`; `x = W` → `x = W −
   k`.
5. **Destination.** The planet nearest that point, over every planet in
   the galaxy, by `dx² + dy²` (ties to the lower id). No shot, and no
   change at all, when Cybertron owns it in its own view, or when it is
   nearer the shooting planet than `w²` ly (`d² < w⁴`; exactly `w²` ly
   passes). For `w` 14 or more (driver rating 11 or more) the distance
   test passes every planet, because the original's `w⁴` overflows (LEGACY
   BUG, BINARY-ONLY; AIX's ratings were 5 and 7).
6. **Shot.** The shooting planet's packet destination becomes that planet,
   at warp `w`, whether or not a packet is built. Then, when the planet
   whose id is one higher has no packet mark and the mineral with the
   most left after the queue's costs (`../AI.md` §7 available amounts;
   ties go to ironium, then boranium) has at least 170 kT left, one
   packet of that mineral goes to the front of the queue and the
   higher-id planet is marked.

The three draws (`Random(7)`, `Random(3W/10)`, `Random(w²)`) are all made
whenever a planet reaches the scanner shot, including when step 5 then
finds no target. So a planet draws nothing (supply), `Random(3)` only
(a standard-level attack), or, in order, `Random(3)` at standard level
only, then `Random(7)`, `Random(3W/10)` and `Random(w²)` (scanner shot).

**Draw bounds.** The original computes `3W/10` and `3W/20` as truncated
floating-point products, `0.3·W` and `0.15·W`. In the oracle's DOSBox
these are exactly `3W/10` and `3W/20` for every galaxy size (120 and 60
up to 600 and 300; MEASURED, AI-24, by running the same floating-point
instructions in that DOSBox, not a game run). On a real x87 FPU at its
default 64-bit precision, each product would truncate to one less (239
and 119 for `W` = 800); which precision the original ran at on real
hardware is UNRESOLVED. Elegy follows the oracle.

MEASURED (AI-24), AIX, 2400–2460: 118 of 118 scanner warps were `w`; 118
of 118 destinations were reachable from the recorded direction by some
slide and inset (the band covers about 6 of 128 planets on average;
neighbouring directions reach the observed planet in only 12 and 19
cases); no destination was Cybertron's own planet; directions were only
1..6, with many 1s; 85 of 85 scanner packets marked the planet one id
higher, and every mark was explained by such a packet or an attack target
(105 of 105). The individual draws were not reproduced (the random stream
offset at this step is unknown), so the slide and inset values are
BINARY-ONLY within that band.

## Open experiments

- Branches not exercised in AIX: obsolete fleets, slot-0 minelayers,
  freighter invasions, armada departures and retreats, splitting, the
  supply packets, easy and standard levels.
- The packet rules' remembered cooldowns between years never act, since
  the memory is empty each turn (`../AI.md` §1); the attack-budget and
  kill-mass formulas need a check with known minerals.
- The scanner shot's individual draws: replaying them needs the random
  stream's position at the packet step (all earlier computer players'
  turns and Cybertron's own earlier draws). The slide and inset rules are
  checked only as a band (AI-24); the `w ≥ 14` overflow and the draw
  bounds on real hardware are untested.
- List 35's position in the list table was read but never built.

## What a faithful planner still depends on

The rules above are enough to write the planner. To check one against
the AIX captures, the turn engine also has to carry out every kind of
order Cybertron gives:
- ship design create and delete;
- merges and splits by design slot;
- scrapping;
- the colonize, lay-mines and transport (load and unload, including
  unloading at another player's planet as an invasion) tasks;
- ship, starbase and mineral-packet production items placed at the
  front of the queue;
- planet automation (`../AI.md` §7).

Two inputs come from shared state and need a decision before a check:
- **Armada parameters.** Under clean per-player state they read as 0
  (§1 step 4), so AIX's 2452–2460 armada orders match only with the
  legacy switch on.
- **Random draws.** All computer players draw from one stream in player
  order. A Cybertron check needs the earlier computer players' turns to
  run as well, or the AIX random-dependent lines will not line up (AI-18).
