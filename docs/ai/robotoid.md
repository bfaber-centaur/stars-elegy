# Robotoid (HE computer player)

Robotoid is the computer player of definition-file type 1, with the HE
race of `../AI.md` §3. This file specifies its own turn. The shared
rules it calls (research, starbase designs, hubs, planet automation,
scrap orders, the design builder, ageing, splitting, merging and the
fleet rules) are in `../AI.md` and are named here by section.

Status: ship designs are CONFIRMED (case AI-8 in `../PARITY.md`). Their
predicted design orders matched the AIX corpus in every year, 2400–2460.
Everything else is BINARY-ONLY unless marked.

Notation: `y` = year index; `lvl` = AI level 0..3 (easy, standard,
harder, expert); slot `k` = own ship design slot; `n(k)` = ships of
design `k` alive; `age(k)` = `y` − creation year of design `k`, where a
slot that never held a design counts creation year 0. A slot that held a
design and was deleted keeps its old creation year. Tech fields are
energy, weapons, propulsion, construction, electronics and biotech.

## 1. Turn order

1. Research (`../AI.md` §4, Robotoid plan), starbase designs (§5) and
   hubs (§6).
2. `y > 50`: merge (`../AI.md` §10) the slots 2–7 and 9–10, then slot 0,
   then slots 14–15.
3. Armada parameters, used by the armada rules of `../AI.md` §11:
   - potency `P` = 4; when `y > 130`, `(y − 120)/20 + 4` (integer), at
     most 50;
   - armada size `A` = 6; when `y > 115`, `(y − 100)/22 + 6`, at most 12.
4. Design ageing (`../AI.md` §10) with limit `T` = 50 while `y < 120`,
   70 while `y < 200`, else 100, in this order: slots 14–15 (`T`), 11–13
   (`T`), 9–10 (`T`), 2–5 (`T`), 6–7 (`3T/2`). Each group's newest design
   is that group's current design below (`D1415`, `D1113`, `D910`,
   `D25`, `D67`; none if the group is empty). After the 14–15 check, a
   Nubian design in slot 14 or 15 is never marked obsolete.
5. `y > 80`: split obsolete ships out (`../AI.md` §10), then split out
   the ships of slot 0, of slot 1, and of slots 11–13, each as its own
   split.
6. Ship designs (§2).
7. Production (§3), visiting own planets in the shuffled order of
   `../AI.md` §2.
8. Fleets (§4).
9. Planet automation (`../AI.md` §7) and the production queue fill.

Before production it also counts the own fleets holding slot 14 or 15
ships, and sets the AI threat mark on every planet owned by another
player: `min(6, defense estimate/250 + 1)`, plus 1 if the planet has a
starbase. The armada launch target of `../AI.md` §11 uses this mark.

## 2. Ship designs (CONFIRMED, AI-8)

Every step needs its target slot to be empty and the tech levels listed.
Each step builds its design with the builder of `../AI.md` §10. A
"random list" step makes up to 5 tries: each try draws `Random(k)`,
builds with list `base + r`, and stops at the first success. A failed
try costs only that draw. The steps run in this order every year:

| Step | Slots | Tech needed | Previous slot | Hull and lists |
|---|---|---|---|---|
| 1 | 11, 12, 13, in turn | propulsion ≥ 2, construction ≥ 3·slot − 29 (4, 7, 10) | 12 and 13 need `age(slot − 1) ≥ 15`, without checking that the previous slot holds a design | construction < 10: Privateer, list 14 (slot 11) or 15 (slots 12, 13), one try; construction ≥ 10: Meta Morph, random list 8 + `Random(6)` |
| 2 | 14 | weapons ≥ 5, electronics ≥ 6, construction ≥ 6, propulsion ≥ 6, energy ≥ 2 | — | 5 rounds: Nubian list 37; if it fails, Destroyer list 16 + `Random(4)`, ending the rounds on success |
| 3 | 15 | electronics ≥ 10, construction ≥ 8, propulsion ≥ 9, weapons ≥ 14 | — | Nubian list 37, one try; if it fails, Destroyer random list 20 + `Random(4)` |
| 4 | 2, 3, 4, 5, in turn | weapons ≥ 10, construction ≥ 10, propulsion ≥ 9, energy ≥ 6 | 3–5 need the previous slot to hold a design and `age ≥ 13` | Meta Morph, random list `Random(4)` (slots 2, 4) or 4 + `Random(4)` (slots 3, 5) |
| 5 | 6, 7 | biotech ≥ 4, electronics ≥ 10, construction ≥ 12, propulsion ≥ 12, energy ≥ 6, weapons ≥ 15 | 7 needs slot 6 to hold a design and `age(6) ≥ 21` | Battleship, random list 27 + `Random(4)` (slot 6) or 31 + `Random(4)` (slot 7) |
| 6 | 9, 10 | weapons ≥ 14 | 10 needs slot 9 to hold a design and `age(9) ≥ 16` | Battleship list 36, one try; if it fails, B-52 Bomber list 24 (slot 9) or 25 (slot 10) |
| 7 | 0 | biotech ≥ 4, electronics ≥ 5, construction ≥ 6, propulsion ≥ 6, energy ≥ 6; level harder or expert | slot 0's hull is not Frigate and `n(0) = 0` (slot 0 need not hold a design) | delete slot 0, then Frigate list 26 |

Slots 1 and 8 are never designed. Slot 1 keeps the starting colony ship.

LEGACY BUGs (reproduced):
- **Step 2, five Nubians.** A successful Nubian does not end the rounds,
  so slot 14 is written five times in one turn: four times as a delete
  plus a new Nubian, with a picture and name drawn each time. Nubian
  needs construction 26, so before that slot 14 is a Destroyer.
- **Step 7, repeated deletes.** A deleted slot 0 keeps its old hull, so
  while the Frigate cannot be built (no part available for a class of
  list 26), slot 0 gets a delete order every year.
- **Step 1, unchecked previous slot.** Slots 12 and 13 test the previous
  slot's age even when it is empty.

Step 1's slot 13 always needs construction 10, so it is always a Meta
Morph. In AIX the observed design orders were: slot 11 Privateer (2415),
the slot-0 delete and Frigate (2435), slot 12 Privateer (2436), slot 14
Destroyer (2442), slot 2 Meta Morph (2450) and slot 13 Meta Morph (2451).

### Robotoid class lists

One AI part class (`../AI.md` §5 "AI part classes") per hull slot, in
hull slot order.

| List | Used for | Classes |
|---|---|---|
| 0 | Meta Morph, slots 2 and 4 | 8, 4, 10, 10, 13, 9, 9 |
| 1 | Meta Morph, slots 2 and 4 | 8, 10, 5, 4, 13, 12, 15 |
| 2 | Meta Morph, slots 2 and 4 | 8, 10, 4, 7, 13, 12, 14 |
| 3 | Meta Morph, slots 2 and 4 | 8, 10, 3, 3, 13, 12, 14 |
| 4 | Meta Morph, slots 3 and 5 | 8, 9, 1, 1, 11, 11, 12 |
| 5 | Meta Morph, slots 3 and 5 | 8, 0, 9, 10, 13, 11, 12 |
| 6 | Meta Morph, slots 3 and 5 | 8, 9, 0, 0, 10, 11, 12 |
| 7 | Meta Morph, slots 3 and 5 | 8, 1, 9, 12, 12, 11, 11 |
| 8 | Meta Morph, slots 11–13 | 8, 10, 16, 16, 3, 12, 2 |
| 9 | Meta Morph, slots 11–13 | 8, 16, 4, 3, 14, 12, 13 |
| 10 | Meta Morph, slots 11–13 | 8, 3, 16, 10, 16, 12, 14 |
| 11 | Meta Morph, slots 11–13 | 8, 16, 1, 11, 12, 10, 10 |
| 12 | Meta Morph, slots 11–13 | 8, 16, 11, 12, 16, 1, 0 |
| 13 | Meta Morph, slots 11–13 | 8, 10, 16, 16, 11, 0, 0 |
| 14 | Privateer, slot 11 | 8, 10, 15, 4, 4 |
| 15 | Privateer, slots 12 and 13 | 8, 9, 11, 0, 0 |
| 16 | Destroyer, slot 14 | 8, 4, 4, 4, 17, 18, 19 |
| 17 | Destroyer, slot 14 | 8, 3, 3, 14, 17, 18, 19 |
| 18 | Destroyer, slot 14 | 8, 4, 3, 2, 17, 18, 20 |
| 19 | Destroyer, slot 14 | 8, 4, 4, 5, 17, 18, 20 |
| 20 | Destroyer, slot 15 | 8, 0, 0, 10, 17, 18, 19 |
| 21 | Destroyer, slot 15 | 8, 0, 0, 11, 17, 18, 19 |
| 22 | Destroyer, slot 15 | 8, 1, 1, 11, 17, 18, 19 |
| 23 | Destroyer, slot 15 | 8, 1, 1, 11, 17, 18, 11 |
| 24 | B-52 Bomber, slot 9 | 24, 21, 23, 23, 23, 12, 10 |
| 25 | B-52 Bomber, slot 10 | 24, 21, 22, 22, 22, 12, 10 |
| 26 | Frigate, slot 0 | 24, 26, 25, 10 |
| 27 | Battleship, slot 6 | 8, 11, 10, 1, 1, 1, 1, 2, 9, 11, 19 |
| 28 | Battleship, slot 6 | 8, 13, 10, 1, 1, 0, 0, 0, 9, 11, 19 |
| 29 | Battleship, slot 6 | 8, 13, 10, 0, 0, 1, 1, 0, 9, 11, 19 |
| 30 | Battleship, slot 6 | 8, 13, 10, 0, 0, 0, 0, 3, 9, 11, 19 |
| 31 | Battleship, slot 7 | 8, 13, 10, 4, 4, 4, 4, 4, 9, 20, 19 |
| 32 | Battleship, slot 7 | 8, 13, 10, 4, 3, 3, 7, 2, 9, 20, 19 |
| 33 | Battleship, slot 7 | 8, 13, 10, 2, 3, 7, 7, 3, 9, 20, 19 |
| 34 | Battleship, slot 7 | 8, 13, 10, 4, 4, 3, 3, 5, 9, 20, 19 |
| 36 | Battleship, slots 9 and 10 | 8, 13, 10, 33, 33, 33, 33, 33, 17, 20, 19 |
| 37 | Nubian, slots 14 and 15 | 8, 10, 10, 7, 5, 20, 20, 4, 4, 19, 4, 2, 3 |

List 35 is never used. Class 33 (Multi Contained Munition) has no
fallback part, so list 36 fails until that weapon is available, and
step 6 makes B-52 Bombers before that.

## 3. Production (BINARY-ONLY)

Robotoid considers each own planet that has a starbase and at least
20,000 colonists. A planet already holding a ship item of any design
slot 0–15 in its queue is skipped. Items are added through the shared
queueing rule (`../AI.md` §10).

1. **Freighters** (if `D1113` exists): with `F = max(planets/8, 4 ×
   hubs)` and `N` = ships alive in slots 11–13, queue 1 of `D1113` when
   `N < 0.8F`, or when `N < F` and `Random(3) == 0`.
2. **Colonizers**: when the colonizer test below says yes, or else when
   its fleet count `c < 26` and `Random(8 × hubs) == 0`. In both cases also
   `y > 4`. Queue slot 1 ×1 (×2 while `y < 21`). Add one more when
   population × max growth % > 2,300, the planet's resources > 35 and the
   level is standard or above. Add another when those exceed 3,600 and 50
   and the level is harder or above.

   *Colonizer test* (once per turn, before production). Colony designs
   are own non-empty designs with a Mini-Colony Ship or Colony Ship hull;
   `c` = own fleets holding ships of them (0 when the test stops at its
   first two rules). In order: easy level in an odd year index → no;
   `y < 30` → yes; no colony design → no; `c > 20 × universe size + 10`
   (size 0..4, tiny to huge) → no; with `e` = the planets owned by all
   players the AI knows, `e + c > 4/5 × planets` → no; with `b` = ships
   ever built of the colony designs, `0 ≤ b − (e + c) ≤ 25` → yes; `c < 5`
   → yes when `Random(2) == 0`; otherwise no.
3. **Frigates**: only when slot 0's hull is Frigate, with `Random(4) ==
   0`. Let `s` be the slot-0 ships in the first own fleet orbiting here.
   When `s < 10`, queue 4 of slot 0 if `Random(2s + 1) == 0`. When `10 ≤
   s ≤ 16`, first require `Random(10) == 0`, then apply the same draw.
4. `rich` = ironium ≥ 5,000 and boranium ≥ 5,000 and germanium < 5,000 on
   the planet. This is the literal reading of the original's test. It is
   a LEGACY BUG candidate, since all three ≥ 5,000 was probably meant.
5. **Armada** (if `D910` exists): take the first own fleet orbiting here
   that is not too weak by the war-fleet strength rule (`../AI.md` §11).
   If it holds fewer than `A` ships of slots 9–10, queue `rich ? 6 : 4`
   of `D910`, and the planet is done.
6. **Warships** (if `D25` exists): if `n(D25)` ≥ planets/7 + 6, skip to
   step 7 when `Random(2) == 0`. The design is `D25`, or `D67` when that
   exists and `Random(2) == 0`. If the planet's available minerals or
   resources minus what its queue already costs is negative in any
   part, the planet is done. If that remainder minus 3/5 of the design's
   cost is negative, skip to step 7. Otherwise queue `rich ? 5 : 1`.
7. **Slot 14/15** (if `D1415` exists and `n(D1415) < planets/12 + 8`): up
   to 5 times, while available minus queue minus the accumulated cost
   stays non-negative, queue 1 of `D1415`.

## 4. Fleets (BINARY-ONLY)

**Pass A**, every fleet in fleet order:
- Any fleet whose waypoint 1 is a route order more than 200 ly away
  loses that waypoint.
- Own fleets are handled as follows, except a scout fleet (slot-0 ships)
  with `y ≥ 41` and only one waypoint, which is covered below:
  - A *transport fleet* (`../AI.md` §11) bound for a planet, idle there
    or with waypoint 1 at it, drops waypoint 1 and its AI task when the
    planet is not its own and it carries nothing.
  - An *attack fleet* joins the attack list. If it holds ships of slots
    2–7 and heads to or orbits a planet, that planet is marked as
    targeted.
  - When `y > 20` or the fleet has no slot-0 ships: an idle fleet with
    colonizers (slot 1), once `y > 4` or with player positions "close",
    goes to the nearest colonizable planet (`../AI.md` §11, with the
    wormhole preference and the colonize order). If there is none, it is
    scrapped where it orbits (`../AI.md` §8). Before a fleet orbiting a
    planet leaves, it loads up to 10 kT of colonists from that planet.
  - While `y ≤ 20`, a fleet with slot-0 ships is scrapped (`../AI.md`
    §8, case AI-3).
  - Scouts with `y ≥ 41` and one waypoint: with more than 6 scouts, 1 in
    5 (`Random(5)`) moves to a random nearby planet (`../AI.md` §11,
    radius 105) other than its current one.
- Other players' fleets join the enemy list.

**Pass B, freighters** (if the player owns any planet with a starbase):
every idle own transport fleet works for its hub (`../AI.md` §6), or for
the first own planet with a starbase when it has no hub, by the hub
freighter rule (`../AI.md` §11).

**Pass C**, every own fleet:
- *Obsolete fleets* (every design in the fleet marked obsolete by
  ageing): orbiting an own planet with a starbase, it is scrapped;
  orbiting an own planet without one, it is scrapped when `Random(5) ==
  0`. Otherwise, unless it already heads to a planet, it moves to the
  nearest own starbase (`../AI.md` §11). If none is reachable, it is
  targeted as below.
- *Targeting*: a fleet with ships of slots 2–10 is an armada (`../AI.md`
  §11). Any other attack fleet not already chasing a fleet first tries
  to join up. Let `c` = own fleets holding slot 14/15 ships. It joins
  when `c > 70` (50 from `y ≥ 121`), or when `c > 60` (40) and
  `Random(3) == 0`. A fleet with ≥ 20 ships of `D1415` skips the join
  unless `Random(20) == 0`. The join uses the buddy rule (`../AI.md` §11)
  over slots 14–15 with radii 36 and 72 ly. If it does not join, it takes an attack
  target (`../AI.md` §11).

## Open experiments

- A level-harder-or-above colonizer idle at another player's planet,
  carrying cargo, gets a transport-style order there and then a move. Its
  exact target is not yet read.
- Idle scouts at `y ≥ 41` get a waypoint-0 marker task with two
  parameters (5, 5). Its effect is not yet observed.
- The production rules (§3) and the fleet passes (§4) need a corpus check
  against AIX's queue and move orders.
