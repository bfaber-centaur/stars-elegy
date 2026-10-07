# Cybertron (PP computer player)

Cybertron is the computer player of definition-file type 5, with the PP
race of `../AI.md` §3. This file specifies its own turn. The shared
rules it calls (what it sees, state leaking between computer players,
research, starbase designs, planet automation, scrap orders, the design
builder, ageing, splitting, merging and the shared fleet rules) are in
`../AI.md` and are named here by section.

Status (cases in `../PARITY.md`, "Computer players"):
- Ship designs are CONFIRMED (AI-13): the predicted design orders matched
  the AIX corpus in every year, 2400–2460.
- Starbase queueing is MEASURED (AI-14) and the fleet pass is MEASURED
  (AI-15): every own fleet's orders matched in every AIX year.
- Everything else is BINARY-ONLY unless marked.

Notation: `y` = year index; `lvl` = AI level 0..3 (easy, standard,
harder, expert); slot `k` = own ship design slot; `n(k)` = ships of
design `k` alive; `age(k)` = `y` − creation year of design `k`. "Holds a
design" means the slot is not empty. Every rule below that reads a
slot's age first checks that the slot holds a design, so Cybertron is
not affected by leaking design slots (`../AI.md` §1). It is affected by
the leaking armada parameters (§1 step 3).

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
     BUG, MEASURED by the PP-B2 oracle run: with those values zeroed,
     every idle armada left home in 11 of 11 armada-years where AIX's
     stayed);
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

## 2. Ship designs (CONFIRMED, AI-13)

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
population estimate/250 + 1)`, plus 1 if it has a starbase (the estimate
as the player's report holds it). Each own planet with a starbase notes
which minerals are low: below 10 kT under an Orbital Fort, else below
1,000 kT (used by §6).

The fleet pass (§5) also makes per-planet notes (inbound colonists, no
colonizable target here, no drop-off, guard present and weak). Those
notes are lost: production and the freighter drop-off choice never see
them, and a note about planet 0 lands on the last planet instead (LEGACY
BUG, MEASURED, AI-15: with the notes kept, 64 freighter-years in AIX
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

### 4.3 Starbases (MEASURED, AI-14)

Every own planet in planet-id order (not shuffled) with no starbase,
value above 14 and at least 50,000 colonists gets, unless its queue
already holds a starbase item, ×1 of the newest Space Station family
design when every mineral concentration is above 15, else of the newest
Orbital Fort family design (`../AI.md` §5). The population counted is
after this turn's fleet pass: colonists Cybertron's own freighters
unloaded or loaded there this turn already count. Starbase upgrades
(`../AI.md` §7) start at year index 40.

## 5. Fleets (MEASURED, AI-15)

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
  go on the attack list and count as Destroyer fleets or group fleets.
  Which of the two depends on the warship-group ageing earlier in the
  turn, not on the fleet's designs: while only group 6–9 was aged out
  this turn, every armed fleet counts as a Destroyer fleet (LEGACY BUG,
  BINARY-ONLY). A group fleet marks the planet it heads to (or orbits),
  when another player owns it, as targeted.

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

## 6. Packets (BINARY-ONLY; warps MEASURED in AIX)

Own planets with a starbase, in the shuffled order, each try at most one
of these. Items go to the front of the queue. `w` = the planet's mass
driver rating + 3.

- **Supply** (the starbase is an Orbital Fort, the planet has over 700
  kT of a mineral and at least 70 resources): up to 7 packets of that
  mineral to the nearest own starbase planet that is low on it (§4.1),
  within `3.5·k²` ly, `k` = the lower driver rating of the two (+1 for a
  planet with two drivers of its best warp). *Not exercised.*
- **Attack** (expert and harder always; standard when `Random(3) == 0`;
  easy never): with `M` = the planet's available minerals less queued
  costs, less 210, over 150: the nearest other player's planet (not AR)
  with a known non-zero population, whose starbase is fully known or
  absent, within `2.5·w²` ly, that the budget can kill. Kill mass `=
  16000·min(1000, 4(pop + 25)) / ((w² − c²)(95 − d))`, `c` = the
  target's catch warp, `d` = its defense coverage, scaled by
  `q^(distance/w²)` (`q` = 0.875 with two drivers of the best warp, else
  0.75). Packets of 70 kT, each of the mineral with the most left, at
  warp `w` (MEASURED: AIX warps and packet counts, 16 of 16).
- **Scanner shot**: a random edge direction (`Random(7)`), a random slide
  along the edge and a random inset; the nearest planet to that point
  that is not Cybertron's and lies beyond `w²` ly gets one packet of the
  most plentiful mineral when at least 170 kT of it is available, at
  warp `w` (MEASURED: 118 of 118 warps; destinations inside the predicted
  band).

## Open experiments

- Branches not exercised in AIX: obsolete fleets, slot-0 minelayers,
  freighter invasions, armada departures and retreats, splitting, the
  supply packets, easy and standard levels.
- The packet rules' remembered cooldowns between years never act, since
  the memory is empty each turn (`../AI.md` §1); the attack-budget and
  kill-mass formulas need a check with known minerals.
- List 35's position in the list table was read but never built.
