# Messages to players

The original game tells each player what happened during the year through a
list of messages. This file catalogues every message kind: when it is
generated, who receives it, what parameters it carries and where in the
year it is made. It describes behavior only. The wording here is ours, not
the original text.

**Project rule (Bobby, 2026-10-07):** Elegy writes its own message text
from the slots catalogued here. The original strings are never used or
published.

Status tags follow `PARITY.md`:

- **CONFIRMED (run)**: the message was seen in oracle turn files with slots
  that fit the stated trigger. The run is named.
- **BINARY-ONLY**: read from the binary, not yet observed.
- **LEGACY BUG?**: what the original does looks unintended. The row says
  what happens; Elegy decides whether to copy it.
- **NEVER SENT**: a message kind exists but no reachable path sends it.

Sources: a private read of every place the original sends a message (387
kinds, ids 0x000–0x182), checked against 22,707 message records decoded from
the oracle turn files of every apparatus corpus (CB, CS, FM, FO, KX, MF, MG,
OB, PG, PQ, RD, SC, SL, TK, UG). Every record decoded cleanly with the slot counts given here.

## How messages work (BINARY-ONLY unless marked)

- **Record.** A message is a kind (an id from 0x000 to 0x182), a **focus**
  (what the player's client opens when the message is clicked: a planet, a
  fleet, a space object, a battle, or a special screen) and up to seven
  **slots**. The number of slots is fixed per kind; the "Slots" column lists
  them in stored order. A slot is a 16-bit value. A long amount (more than
  65,535) takes two slots.
- **Turn file layout** (CONFIRMED, every decoded run). The year's messages for
  a player are one block in that player's `.M` file (block type 12): per
  message a word `kind | wide << 9`, a word for the focus, then the slots,
  each one byte, or two bytes when its bit in `wide` is set. A slot is
  stored wide when its value needs it. `tools/fleetlab/events.py` decodes the
  block.
- **Focus codes.** A planet is its planet number; a fleet is its fleet id
  with bit 15 set. Negative codes select a special screen: −1 none, −2
  research, −3 ship design, −4 scores, −5 registration notice, −6 a space
  object named in the first slot, −7 the battle viewer (the screens are
  inferred from the message contents). A battle message
  uses the battle's id with bit 14 set. A component announcement uses a part
  code with bits 14 and 15 set.
- **Order.** Messages are appended in the order the year generates them
  (the "Phase" column, then the order notes under each table). A few
  end-of-game and viewer messages are put at the front instead. Some steps
  delete a message queued earlier in the year: a fleet's "finished its
  orders" message is replaced when the fleet gets new work or is consumed,
  and a planet's single-unit build message is folded into a later count.
- **Who gets messages.** Each message is addressed to one player. A message
  to "every other player" is one copy per player. A message whose recipient
  would be "no player" (for example the owner of an unowned planet) is
  dropped.
- **Computer players.** For computer players (except one computer-player
  setting) only four kinds are kept: 0x007, 0x023, 0x040 and 0x08f.
  Everything else addressed to them is dropped.
  (A computer player's `.M` file had no message block in the six-player
  race-penalty run, apparatus #27 `rd/rp12`, which fits.)
- **Overflow.** All players' messages for the year share one buffer of
  about 64 KB. Once it is full, further messages that year are dropped
  silently.
- **Viewer-load messages (phase L).** A few messages are not stored in the
  turn file. The client makes them each time a player opens the turn: newly
  seen planets and how good they are, packets that will hit the player's
  planets too fast, starbases whose queue will run out, and the number of
  battles to watch. They come back on every reload.

## Slot types

| Type | Meaning |
|---|---|
| planet | planet number |
| fleet | fleet id (owner and number) |
| player | player number, plus flags for article and plural in the text |
| players | a set of players (bit mask), shown as a list |
| count | a whole number |
| amount | a long whole number (two slots) |
| kT, mg | mineral or fuel quantity |
| colonists | colonists in units of 100 |
| percent | stored ×100, shown with two decimals |
| location | either a planet, or x and y in deep space (two slots) |
| object | a space object: packet, minefield, wormhole, salvage or the Mystery Trader |
| design | a ship or starbase design of a player |
| part | a component (category and item, two slots) |
| mineral | Ironium, Boranium or Germanium |
| field | research field |
| hab | habitability axis and value |

## Phases

| Label | Where in the year (`KERNEL.md` "Turn order") |
|---|---|
| P0 | new game creation |
| P1 | step 1, orders applied |
| P1a | checks after the orders: registration, fleets following fleets |
| P2 | step 2, waypoint tasks before movement |
| P2a | race check in a running game, after the waypoint tasks and before movement |
| P3 | step 3, movement (objects, then fleets) |
| P3a | minefield detonation, after movement |
| P3b | Inner Strength colonists breeding in transit |
| P4 | step 4, production |
| P4a | population growth |
| P4b | research level-ups |
| P4c | random events |
| P5 | step 5, space objects move again |
| P6 | step 6, battles |
| P6a | bombing |
| P6b | encounters with the Mystery Trader |
| P6c | waypoint tasks after movement |
| P7 | step 7, mine sweeping, repair, terraforming |
| P7a | registration penalties and waypoint checks |
| P8 | step 8, scores and end of game |
| P8a | while each player's turn file is written (checks on later waypoints) |
| L | made by the client when the player opens the turn (not stored) |

## Catalogue

Each section lists its message kinds in id order. Rows that share a trigger reference each other. The notes under each table give the order inside the phase, duplicates and open points.

### New game, order checks and registration

| Id | What the player is told | Sent when | To | Slots | Focus | Phase | Status |
|---|---|---|---|---|---|---|---|
| 0x07f | Interface tip (hiding messages) | New game | every player | - | none | P0 | CONFIRMED (all sets) |
| 0x080 | Interface tip (adding waypoints) | New game | every player | - | none | P0 | CONFIRMED (all sets) |
| 0x081 | Interface tip (copying a hull to design ships) | New game | every player | - | none | P0 | CONFIRMED (all sets) |
| 0x082 | Interface tip (pop-up help) | New game | every player | - | none | P0 | CONFIRMED (all sets) |
| 0x0a9 | Welcome message naming the home planet | New game, after the tips | every player | planet | planet | P0 | CONFIRMED (all sets) |
| 0x100 | Penalty notice for an unverified registration | Every turn for a player flagged for an invalid or duplicated registration, when no other flagged player is involved | flagged player | - | special: registration dialog (inferred) | P1a | BINARY-ONLY |
| 0x101 | Penalty notice naming another player with the same registration | As 0x100, when another flagged player shares the registration | flagged player | player | special: registration dialog (inferred) | P1a | BINARY-ONLY |
| 0x102 | A fleet refuses to move until a valid serial is entered. | Fleet of a player flagged for an invalid or shared serial: each year a 1 in 4 chance per moving fleet. From the 11th year on, in one year out of 8 (by player number), its fleets do not move at all and no message is sent. | fleet owner | fleet | special (inferred: serial dialog) | P3 movement | BINARY-ONLY |
| 0x103 | Fleets refused to move this year (registration penalty) | Flagged player, from year index 11, in every 8th year (the year depends on the player number) | flagged player | - | special: registration dialog (inferred) | P1a | BINARY-ONLY |
| 0x104 | A fleet left the player's control (registration penalty) | From year index 10, if any player is flagged: each fleet of a flagged player has a 1/12 chance per turn | fleet owner | fleet | special: registration dialog (inferred) | P7a | BINARY-ONLY |
| 0x105 | A fleet lost part of its mineral cargo (registration penalty) | Same fleet roll, other 11/12: if the fleet carries minerals, each mineral loses trunc(amount × p / 100), at least 1, with p = 10–20% drawn once per fleet | fleet owner | fleet, percent | special: registration dialog (inferred) | P7a | BINARY-ONLY |
| 0x106 | Mines on a planet were destroyed (registration penalty) | Same gate. Each planet of a flagged player that has mines: 1/8 chance to lose trunc(mines × p / 100), at least 1, p = 5–35%. Then no 0x107 roll for that planet that year | planet owner | planet, count | special: registration dialog (inferred) | P7a | BINARY-ONLY |
| 0x107 | Minerals were stolen from a planet (registration penalty) | Same gate, if 0x106 did not fire: 1/15 chance; one random mineral loses trunc(stock × p / 100), p = 5–45%, at most 30000 kT | planet owner | planet, kT, mineral | special: registration dialog (inferred) | P7a | BINARY-ONLY |
| 0x117 | The player's race was found illegal and has been adjusted | New game: a human race with a negative advantage-point total, replaced by the default race. Running game: a human race whose advantage points are below 0 is adjusted step by step until the total is 500 or more (first fewer resources per colonist, then lower growth, then cheaper research costs are removed). Not sent to computer players during a running game | that player | - | none | P0 / P2a | CONFIRMED (apparatus #27, rd/rp12; ob/prt-legality, tk2/smoke, kx003) |
| 0x138 | A fleet told to follow a fleet that did not move is waiting for orders | Before movement: a fleet whose only order is to follow another fleet, when that fleet no longer exists, or has no orders of its own and is not following anyone. A follower of a fleet with orders takes over its next waypoint (no message). Chains of followers are resolved over up to 8 passes. Circular chains get no message | fleet owner | fleet | fleet | P1a | CONFIRMED (fo/fo04) |
| 0x182 | Another player's race was found illegal and adjusted | Same trigger as 0x117. Sent only if the offender is not a computer player | every other player | player | none | P0 / P2a | CONFIRMED (apparatus #27, rd/rp12; ob/prt-legality, tk2/smoke, kx003) |

### Waypoint tasks, cargo and ground combat

| Id | What the player is told | Sent when | To | Slots | Focus | Phase | Status |
|---|---|---|---|---|---|---|---|
| 0x000 | Your landing troops were all killed by the planet's ground forces | Invasion of an owned planet fails (ground combat as in `TAKEOVER.md`) and the planet has no defenses that act on troops | each attacking player | colonists, planet, player (defender) | planet | P2, P6c | CONFIRMED (tk2/tk109) |
| 0x001 | Your landing troops were killed: part by planetary defenses (percentage given), the rest on the ground | Same failure, and the planet has defenses that shot some troops (`TAKEOVER.md`) | each attacking player | colonists, planet, percent (troops lost to defenses), player (defender) | planet | P2, P6c | CONFIRMED (tk/tk003) |
| 0x002 | Colonists you sent down by manual transfer died because the planet was not colonized | A manual colonist transfer onto a planet that was unowned when orders were read, and still is | dropping player | colonists, planet | planet | P2 | BINARY-ONLY |
| 0x003 | Your ground forces beat off an invasion by the named player (no defenses involved) | Counterpart of 0x000; one per attacking player | planet owner | planet, colonists, player (attacker) | planet | P2, P6c | CONFIRMED (tk2/tk109) |
| 0x004 | Your defenses and ground forces beat off an invasion by the named player | Counterpart of 0x001; one per attacking player | planet owner | planet, colonists, player (attacker) | planet | P2, P6c | CONFIRMED (tk/tk003) |
| 0x005 | Your planet was attacked by several players at once and everyone died | An invasion empties an owned planet and two attackers tie for highest strength: nobody lands and the planet becomes unowned | former planet owner | count (attacking players), planet | planet | P2, P6c | CONFIRMED (tk2/tk113) |
| 0x006 | You took part in a multi-player assault where nobody survived | The same tie, on an owned or unowned planet | every attacking player | count, planet | planet | P2, P6c | CONFIRMED (tk2/tk113) |
| 0x007 | The named player invaded and took your planet with this many troops | Planet captured: attackers' total strength ≥ D and one clear winner | former planet owner | player (winner), planet, colonists (winner's landed troops, not survivors) | planet | P2, P6c | CONFIRMED (tk2/tk116) |
| 0x008 | You won a multi-player race for an empty planet | Planet unowned before the landings, ≥ 2 landing players, one clear winner | winner | count, planet | planet | P2, P6c | CONFIRMED (tk/tk002) |
| 0x009 | You lost a multi-player race for an empty planet; the named player holds it | Same case | each losing player | count, planet, player (winner) | planet | P2, P6c | CONFIRMED (tk/tk002) |
| 0x00a | Your colonists now control the planet | Exactly one player landed on an unowned planet (colonization, or landing on a planet emptied this turn) | new owner | planet | planet | P2, P6c | CONFIRMED (cs/cs-003, tk2) |
| 0x00b | Your orbital construction module set up a starter colony | As 0x00a when the new owner is Alternate Reality | new owner | planet | planet | P2, P6c | CONFIRMED (tk2/tk107) |
| 0x00c | You defeated the named player's colonists and now control the planet | Capture (see 0x007); sent before 0x007 | winner | player (former owner), planet | planet | P2, P6c | CONFIRMED (tk2/tk116) |
| 0x00d | Your colonists landed on the planet were wiped out in the fighting | Capture with several attackers, sent to those who did not win | each losing attacker | planet | planet | P2, P6c | BINARY-ONLY |
| 0x02b | Fleet loaded this much cargo from a location | Load task: any amount > 0 taken from an own planet, own or friendly fleet, salvage, or (by a fleet able to steal) a foreign planet; also fuel load-optimal when the net fuel change is a gain | fleet owner | fleet, amount, mineral, location | fleet | P2, P6c | CONFIRMED (fo/fo02) |
| 0x02c | Fleet took colonists aboard from a location | Load task, colonists | fleet owner | fleet, amount, mineral, location | fleet | P2, P6c | CONFIRMED (fo/fo01) |
| 0x02d | Fleet unloaded this much cargo to a location | Unload task, amount accepted > 0 (unloads to an enemy player's fleet move nothing, silently); also fuel load-optimal dumping surplus fuel | fleet owner | fleet, amount, mineral, location | fleet | P2, P6c | CONFIRMED (fo/fo04; fuel form mg/mg003) |
| 0x02e | Fleet beamed colonists down to a location | Unload task, colonists | fleet owner | fleet, amount, mineral, location | fleet | P2, P6c | CONFIRMED (fo/fo02) |
| 0x03c | Not enough fuel here for the next leg; fleet waits; shortfall given | Fuel load-optimal before movement: fuel below the estimated need, but tanks are big enough | fleet owner | location, fleet, mg (shortfall) | fleet | P2 | CONFIRMED (mg/mg003, fleet target) |
| 0x03d | Fleet can never reach its next waypoint: tank capacity vs. fuel needed | Same, tank capacity < estimated need | fleet owner | fleet, mg (capacity), mg (need) | fleet | P2 | CONFIRMED (mg/mg003, fleet target) |
| 0x042 | Your cargo was delivered to the other player's object | Transfer to another player's fleet or planet ordered by hand: destination accepts all of it; minerals or colonists | sending object's owner | object (fleet/planet), amount, mineral, object | fleet or planet (source) | P2 | BINARY-ONLY |
| 0x043 | Same as 0x042, worded for colonists | Same, fuel cargo (see Notes) | sending object's owner | as 0x042 | source | P2 | BINARY-ONLY; LEGACY BUG? |
| 0x044 | Your object received cargo from another player | Counterpart of 0x042 | receiving object's owner | object, amount, mineral, object | destination | P2 | BINARY-ONLY |
| 0x045 | Same as 0x044, worded for colonists | Counterpart of 0x043 (fuel) | receiving object's owner | as 0x044 | destination | P2 | BINARY-ONLY; LEGACY BUG? |
| 0x046 | Only part of the cargo you sent arrived | Destination could take some but not all; the rest is lost; minerals or colonists | sender | object, amount (sent), mineral, object, amount (received) | source | P2 | BINARY-ONLY |
| 0x047 | Same as 0x046, colonist wording | Same, fuel | sender | as 0x046 | source | P2 | BINARY-ONLY; LEGACY BUG? |
| 0x048 | You received only part of what was sent; the rest was lost | Counterpart of 0x046 | receiver | object, amount (received), mineral, object, amount (sent) | destination | P2 | BINARY-ONLY |
| 0x049 | Same as 0x048, colonist wording | Counterpart of 0x047 | receiver | as 0x048 | destination | P2 | BINARY-ONLY; LEGACY BUG? |
| 0x04a | None of the cargo you sent arrived | Destination took nothing | sender | object, amount, mineral, object | source | P2 | BINARY-ONLY |
| 0x04b | Same as 0x04a, colonist wording | Same, fuel | sender | as 0x04a | source | P2 | BINARY-ONLY; LEGACY BUG? |
| 0x04c | Cargo meant for you was all lost | Counterpart of 0x04a | receiver | object, amount, mineral, object | destination | P2 | BINARY-ONLY |
| 0x04d | Same as 0x04c, colonist wording | Counterpart of 0x04b | receiver | as 0x04c | destination | P2 | BINARY-ONLY; LEGACY BUG? |
| 0x04e | A fleet has finished its orders | (a) Waypoint tasks: the fleet is at its last waypoint and its task ends, either completed (a transport fully done, a merge with itself) or cancelled by any refusal message in this table; an earlier copy for the same fleet is removed first. (b) End of movement: the fleet sits exactly on its next waypoint, that becomes its last waypoint, and its task is none, merge, transfer, or route with nothing to route (deep space, a planet that is not the owner's, or no route set); not for transport, colonize, remote mining, scrap, lay mines or patrol | fleet owner | fleet | fleet | P2, P3, P6c | CONFIRMED (tk2/tk113, fo/fo04, cs, fm, ob) |
| 0x051 | Colonize order cancelled: fleet not orbiting a planet | Colonize task in deep space | fleet owner | fleet | fleet | P2, P6c | BINARY-ONLY |
| 0x052 | Colonize order cancelled: planet already inhabited | Colonize task at a planet owned at that moment (including one claimed by another player earlier the same turn) | fleet owner | fleet, planet, planet | fleet | P2, P6c | CONFIRMED (tk2/tk121) |
| 0x053 | Colonize order cancelled: no colonists aboard | Colonize task with no colonists | fleet owner | fleet, planet | fleet | P2, P6c | BINARY-ONLY |
| 0x054 | Colonize order cancelled: no ship has a colony module | No design in the fleet carries a colonization or orbital construction module | fleet owner | fleet, planet, fleet | fleet | P2, P6c | CONFIRMED (cs/cs-003) |
| 0x055 | Colonists can't be beamed onto an uninhabited planet; colonize it instead | Unload colonists onto a planet that is unowned now and was unowned when the phase began; task cancelled | fleet owner | fleet, planet | fleet | P2, P6c | CONFIRMED (tk2/tk114) |
| 0x056 | Your crew refused to beam colonists down (race cannot live on planets) | Alternate Reality fleet unloads colonists onto a planet it does not own; task cancelled | fleet owner | fleet, planet | fleet | P2, P6c | CONFIRMED (tk2/tk107) |
| 0x057 | Your colonists died on landing because your race cannot live on planets | Alternate Reality colonists land anywhere other than an unowned planet with a colonize order (for example a manual or invasion drop) | dropping player | planet | planet | P2, P6c | BINARY-ONLY |
| 0x058 | A starbase shot down the colonists you tried to land | Colonists dropped on an owned planet that has a starbase | dropping player | planet | planet | P2, P6c | BINARY-ONLY |
| 0x059 | Fleet was taken apart; its minerals went to the planet surface | Scrap at a planet without a starbase whose owner lacks Ultimate Recycling (or unowned); also on every successful colonization (the ship-cost share given to the new colony) | fleet owner | fleet, kT, planet | planet | P2 (scrap); P2, P6c (colonize) | CONFIRMED (cs/cs-003, tk2) |
| 0x05a | Fleet was taken apart at the starbase; minerals deposited | Scrap at a planet with a starbase, owner without Ultimate Recycling | fleet owner | fleet, kT, planet | planet | P2 | CONFIRMED (tk2/tk111) |
| 0x05b | Fleet was taken apart in deep space, leaving salvage | Scrap with no planet | fleet owner | object (salvage), fleet | object (salvage) | P2 | CONFIRMED (tk2/tk111) |
| 0x05c | Fleet scrapped at the planet, with recycled resources made available | Scrap at a planet without a starbase whose owner has Ultimate Recycling | fleet owner | fleet, kT, planet, amount (resources) | planet | P2 | CONFIRMED (tk2/tk111) |
| 0x05d | As 0x05c, at a starbase | Same, with starbase | fleet owner | fleet, kT, planet, amount | planet | P2 | CONFIRMED (tk2/tk111) |
| 0x05e | Settlers found an artifact that added research to a field | A planet holding an artifact is owned after the landings resolve and random events are on. Field random (1 of 6); points 100–400, scaled by pop/1000 when pop < 1000 | planet owner after landing | planet, field, value (resources) | special: research (inferred) | P2, P6c | BINARY-ONLY |
| 0x075 | Mining order cancelled: fleet has no remote-mining modules | Remote-mining task after movement, fleet stationary this turn and orbiting | fleet owner | fleet, planet | fleet | P6c | CONFIRMED (cs/cs-003) |
| 0x076 | Mining order cancelled: planet is inhabited | Same, planet owned (an Alternate Reality fleet is skipped silently instead) | fleet owner | fleet, planet | fleet | P6c | CONFIRMED (tk2/tk111) |
| 0x077 | Mining order cancelled: fleet is in deep space | Same, not orbiting | fleet owner | fleet | fleet | P6c | BINARY-ONLY |
| 0x07d | Fleet got ore loaded by your remote miners working the planet | Load ordered at an unowned planet where another own fleet, stationary this turn, is remote mining; ore taken from the planet | fleet owner | fleet, amount, mineral, fleet (miner), planet | fleet | P2, P6c | BINARY-ONLY |
| 0x0bf | Mine-laying order cancelled: no minelaying pods | Lay-mines task after movement, fleet can lay zero mines | fleet owner | fleet | fleet | P6c | BINARY-ONLY |
| 0x0c3 | Fleet laid a new minefield of this many mines | Per mine type laid: no own field of that type covers the fleet (see Notes) | fleet owner | fleet, amount | fleet | P6c | CONFIRMED (ob, cs, fm2) |
| 0x0c4 | Fleet added this many mines to a minefield | Per mine type laid: merged into an own field of that type that covers the fleet | fleet owner | fleet, amount | fleet | P6c | CONFIRMED (ob/ob019-y2) |
| 0x0db | Another player emptied the packet/salvage first; you got only this much | A manual load from a packet or salvage gets less than requested but more than nothing | owner of the loading fleet | fleet, mineral, kT, mineral | fleet | P1 | BINARY-ONLY |
| 0x0dc | Another player emptied the packet/salvage first; you got none | Same, nothing obtained | owner of the loading fleet | fleet, mineral | fleet | P1 | BINARY-ONLY |
| 0x0dd | A manual transfer moved less than requested (shortfall and request given) | A hand-ordered cargo transfer where the giving side lacks the cargo or the receiving side lacks room (not colonists; see Notes) | owner of the source object named in the order | object, value (shortfall), mineral, value (request) | source object | P1 | BINARY-ONLY |
| 0x0f5 | Merge order failed: destination is not a fleet | Merge task with a non-fleet or vanished target | fleet owner | fleet | fleet | P2, P6c | BINARY-ONLY |
| 0x0f6 | Merge order failed: destination fleet belongs to someone else | Merge target owned by another player | fleet owner | fleet | fleet | P2, P6c | CONFIRMED (fo/fo04) |
| 0x0f7 | Fleet merged into the named fleet | Merge task succeeds | fleet owner | fleet (merged, by name), fleet (target) | fleet (target) | P2, P6c | CONFIRMED (fo/fo03) |
| 0x119 | Your fleet stole cargo from another player's fleet | Load from a foreign fleet by a fleet able to steal; the victim is not told | fleet owner (thief) | fleet, amount, mineral, fleet (victim) | fleet | P2, P6c | BINARY-ONLY |
| 0x11e | A fleet was ordered to move cargo with an object that cannot hold cargo | Transport task targets a packet, minefield, wormhole or trader (anything but salvage); task cancelled | fleet owner | fleet, value (object kind) | fleet | P2, P6c | BINARY-ONLY |
| 0x11f | Load from a foreign planet refused; task cancelled | Load after movement from a foreign planet by a fleet that cannot steal; before movement the task just waits | fleet owner | fleet, mineral | fleet | P6c | BINARY-ONLY |
| 0x120 | Load from a foreign fleet refused; task cancelled | Same, foreign fleet | fleet owner | fleet, mineral | fleet | P6c | CONFIRMED (fo/fo04) |
| 0x121 | Fleet can't reach its set cargo amount here and will wait | Set-amount load after movement: target holds less than needed; task kept; what is there is loaded | fleet owner | fleet, mineral, amount (target), location | fleet | P6c | BINARY-ONLY |
| 0x122 | As 0x121, for colonists | Same, colonists | fleet owner | as 0x121 | fleet | P6c | BINARY-ONLY |
| 0x123 | Can't load from deep space | Load after movement with a deep-space target; cancelled | fleet owner | fleet, mineral | fleet | P6c | BINARY-ONLY |
| 0x124 | A fleet failed to take colonists from a foreign target | Coded for taking colonists from a foreign target, but only in a pass of the turn that never runs. In the real turn the task is cancelled silently | fleet owner | (fleet, amount, location) | fleet | — | NEVER SENT |
| 0x125 | A fleet failed to take fuel from a foreign target | As 0x124, fuel | fleet owner | (fleet, amount, location) | fleet | — | NEVER SENT |
| 0x126 | Fleet could not get the fuel it needs here | Fuel load-optimal after movement: fleet has less fuel than the trip to the next waypoint needs, at a target it may not load from | fleet owner | fleet, location | fleet | P6c | BINARY-ONLY |
| 0x127 | Fleet at a planet has been sent on along the planet's route | Route task, last waypoint, at an own planet that has a route destination | fleet owner | fleet, planet, planet (destination) | fleet | P2 | BINARY-ONLY |
| 0x128 | As 0x127, but the fleet lacks fuel for the trip and waits | Same, new leg gets speed 0 | fleet owner | fleet, planet, planet | fleet | P2 | BINARY-ONLY |
| 0x135 | Unload of colonists refused: an enemy starbase guards the planet | Unload colonists onto a foreign planet with a starbase; task cancelled | fleet owner | fleet, planet | fleet | P2, P6c | CONFIRMED (tk/tk002) |
| 0x13c | Scrapping at your starbase revealed a new technology | Starbase scrap (no UR) where the planet owner's tech roll gives a discovery | planet owner | fleet, kT, planet | special (inferred: tech) | P2 | BINARY-ONLY |
| 0x13d | Scrapping at your starbase gave you a research level in a field | Same, roll gives a level | planet owner | fleet, kT, planet, field | special (inferred: research) | P2 | BINARY-ONLY |
| 0x13e | As 0x13c, with recycled resources | Starbase scrap with Ultimate Recycling, plus a tech discovery. Also coded (LEGACY BUG?, probably unreachable) as the result of battle wreckage giving the Mystery Trader's planetary device, where this scrap text would be shown with misread slots | planet owner | fleet, kT, planet, amount | special (inferred) | P2 | BINARY-ONLY |
| 0x13f | As 0x13d, with recycled resources | Starbase scrap with UR, level gained | planet owner | fleet, kT, planet, amount, field | special (inferred) | P2 | BINARY-ONLY |
| 0x140 | A fleet was scrapped at your planet; minerals deposited | Sent with every 0x059 (dropped when the planet is unowned, so colonization never sends it) | planet owner | fleet, kT, planet | planet | P2 | CONFIRMED (tk2/tk111) |
| 0x141 | A fleet was scrapped at your starbase | Sent with 0x05a when no technology was gained | planet owner | fleet, kT, planet | planet | P2 | CONFIRMED (tk2/tk111) |
| 0x142 | As 0x140, with recycled resources | Sent with 0x05c | planet owner | fleet, kT, planet, amount | planet | P2 | CONFIRMED (tk2/tk111) |
| 0x143 | As 0x141, with recycled resources | Sent with 0x05d when no technology was gained | planet owner | fleet, kT, planet, amount | planet | P2 | CONFIRMED (tk2/tk111) |
| 0x148 | Couldn't give the fleet away: recipient is dead | Transfer-fleet task to a dead or invalid player | fleet owner | fleet | fleet | P6c | BINARY-ONLY |
| 0x149 | Couldn't give the fleet away: your colonists are aboard | Transfer-fleet task with colonists aboard | fleet owner | fleet | fleet | P6c | CONFIRMED (fo/fo04) |
| 0x14a | Couldn't give the fleet away: recipient lacks room for its records | Recipient has no free or matching design slot for some design, or already has 512 fleets | giver | fleet, player | fleet | P6c | BINARY-ONLY |
| 0x14b | Fleet gift from another player refused for lack of design slots | Counterpart of 0x14a | recipient | player | none | P6c | BINARY-ONLY |
| 0x14c | The named player refused your gift fleet | Recipient is a computer player or treats the giver as an enemy | giver | player | fleet | P6c | CONFIRMED (fo/fo05) |
| 0x14d | Fleet handed over to the named player | Transfer-fleet succeeds | giver | fleet (by name), player | fleet (new, recipient's) | P6c | CONFIRMED (fo/fo04) |
| 0x14e | The named player gave you a fleet | Same | recipient | player, fleet (by name) | fleet | P6c | CONFIRMED (fo/fo04) |
| 0x155 | Colonists can't be given to another player's fleet | Unload colonists into a fleet owned by another player; task cancelled | fleet owner | fleet | fleet | P2, P6c | CONFIRMED (fo/fo04) |
| 0x165 | Colonists can't be beamed into empty space | Unload colonists with a deep-space target; task cancelled | fleet owner | fleet | fleet | P2, P6c | BINARY-ONLY |
| 0x17e | Fleet failed to lay mines for technical reasons | A new field is needed but the game's object limit is reached (512-field limit); those mines are lost | fleet owner | fleet | fleet | P6c | CONFIRMED (stars-elegy #47, apparatus #27) |

- Within a fleet's task, unload runs before load: before movement (P2) and again after movement (P6c). Colonist landings resolve between the unload and load halves. Hand-ordered cargo gifts to other players (0x042–0x04d) are delivered once, after the pre-movement load half.
- Any refusal message on a waypoint task also cancels that task, and 0x04e follows when it was the last waypoint. Oracle: 0x076 then 0x04e, and 0x052 then 0x04e. Load refusals (0x11f/0x120/0x123, 0x121/0x122, 0x126) are sent only after movement; before movement the same condition just waits. 0x03c/0x03d are sent only before movement.
- Colonizing sends a scrap-style message, 0x059, before 0x00a/0x00b. Oracle: cs/cs-003 and tk2.
- Scrapping at your own planet sends two messages to the same player: one as fleet owner (0x059/0x05a/0x05c/0x05d) and one as planet owner (0x140–0x143 or 0x13c–0x13f). Oracle: tk2/tk111. At a foreign planet the planet owner gets the second message, the recycled resources and the tech roll.
- Invasion results go out in player-number order. The defender gets one 0x003/0x004 per attacking player. In a capture, 0x00c/0x00d go out before 0x007.
- LEGACY BUG? Fuel given by hand to another player gets the colonist-worded variants (0x043/0x045/0x047/0x049/0x04b/0x04d), so a fuel shortfall is reported as colonists lost in space. Colonists given to another player's fleet get the mineral wording.
- LEGACY BUG? When one fleet lays two mine types in one turn, a merge into an existing field for the first type can make the second type's new field be reported as 0x0c4 (added) instead of 0x0c3.
- **Load-optimal fuel (MEASURED, MG-002..004).**
  - It never took on fuel in any case.
  - With an own fleet as the target (MG-003), it behaved as read:
    - fuel short of the next leg's need, tanks big enough: 0x03c with the shortfall, and the fleet stayed put;
    - tanks smaller than the need: 0x03d with capacity and need, and the fleet stayed put;
    - fuel above the need: the surplus went to the target fleet (0x02d), and the fleet kept the need for a 20-ly leg.
  - With a planet as the target, the order did nothing in all 7 cases:
    - own planets with and without a starbase, and an unowned planet on arrival;
    - no message, fuel unchanged, and the fleet left on its next leg.
    - That includes the stationary case, where a fleet target got all the fuel (FO-02 Q).
  - The planet behavior is not explained by the binary reading yet (open).
  - 0x126 and the fuel-gain form of 0x02b were not seen.
- Open: a hand-ordered colonist transfer that cannot be carried out in full looks as if it fails the whole order file, which would stop turn generation. Needs an oracle check.
- 0x0dd, 0x0db and 0x0dc go to the owner of the object the order names as the source, which need not be the player who wrote the order.
- Stealing tells only the thief; the victim gets no message from this step.

### Movement, gates, minefields and sweeping

| Id | What the player is told | Sent when | To | Slots | Focus | Phase | Status |
|---|---|---|---|---|---|---|---|
| 0x027 | A fleet's fuel tanks are empty. | The fleet emptied its tanks short of its waypoint and has no fuel-free warp to slow down to (even warp 1 burns fuel). | fleet owner | fleet | fleet | P3 movement | CONFIRMED (fm2/fm105) |
| 0x074 | Engine radiation killed colonists on board a fleet. | A fleet moved this year using a radiating ram-scoop engine and carries colonists. Its race is not radiation-immune and has radiation low + high < 170. Loss = max(1, C·((86 − (low+high)/2) div 2)/100) kT, capped at C, where C = colonists in kT. Only ordinary movers and the first chase step. | fleet owner | colonists, fleet | fleet | P3 movement | CONFIRMED (fm2/fm102) |
| 0x08b | A fleet ran low on fuel and its speed was cut. | Same as 0x027, but some warp ≥ 1 burns no fuel: the fleet's next waypoint warp is permanently set to the fastest fuel-free warp. That year the fleet gets no ram-scoop fuel. | fleet owner | fleet, value (new warp) | fleet | P3 movement | CONFIRMED (fm004, fm001, fm002, fm2) |
| 0x0be | Someone swept mines from your minefield. | Every time an enemy fleet or starbase sweeps mines from your field (one message per sweeper per field), sent before the field shrinks or vanishes. | field owner | object (minefield), amount (mines), value (field type), location (field centre) | object (the field, which may already be gone) | P7 sweeping, repair, terraforming | CONFIRMED (ob/ob010, cs, mf/mf01: stars-elegy #47, apparatus #27) |
| 0x0c1 | Colonists died from warp acceleration. | AR race, fleet ordered to move at warp 1–10 and carrying more than 10 kT of colonists. Loss = trunc((C+11)·3/100) kT, sent only if > 0. Checked once a year before fuel is considered, so a fleet that then cannot move still loses them. | fleet owner | colonists (amount), fleet | fleet | P3 movement | CONFIRMED (tk2/tk117) |
| 0x0c2 | Your fleet swept mines from a minefield. | A fleet that can sweep mines (beam weapons) sits inside a field of another player whom its battle plan would attack. Swept = its sweep rating (a third for speed bumps), at least 2, but never more than needed to leave the fleet just outside the field (unless it sits exactly at the centre), and never more than the field holds. | sweeping fleet owner | fleet, amount (mines), player (field owner), value (field type), location (field centre) | fleet | P7 sweeping, repair, terraforming | CONFIRMED (ob/ob010, cs) |
| 0x0c5 | A fleet was stopped in a minefield. | A moving fleet is stopped by a speed-bump field (no damage). Also sent when a speed-bump field detonates, to every fleet inside it that is not the owner's, moving or not; the location is then the field centre. | fleet owner | fleet, player (field owner), value (field type), location | fleet | P3 movement; P3a minefield detonation | CONFIRMED (mf/mf07, ob/ob024: stars-elegy #47, apparatus #27) |
| 0x0c6 | A fleet was stopped in a minefield and damaged, no ships lost. | A moving fleet is stopped by an enemy or neutral standard or heavy field, takes damage, and loses no ships. Damage is shown before shields, capped at 32760. | fleet owner | fleet, player (field owner), value (field type), location (stop point), value (damage) | fleet | P3 movement | CONFIRMED (ob/ob010, mf/mf01: stars-elegy #47, apparatus #27) |
| 0x0c7 | A fleet was stopped in a minefield and lost some ships. | As 0x0c6, but some (not all) ships were destroyed. | fleet owner | fleet, player, value (field type), location, value (damage), count (ships lost) | fleet | P3 movement | BINARY-ONLY |
| 0x0c8 | A fleet was destroyed in a minefield. | A moving fleet loses every ship in an enemy field and the wreck leaves salvage, i.e. it was not stopped exactly on a planet. | fleet owner | object (salvage, hidden), fleet (name kept for the dead fleet), player, value (field type), location | object (salvage) | P3 movement | CONFIRMED (ob/ob024) |
| 0x0c9 | Your minefield stopped an enemy fleet. | Field-owner side of 0x0c5: speed-bump stop during movement, or a speed bump detonating on fleets inside it (the owner's own fleets included). | field owner | fleet, value (field type), location | fleet (the victim) | P3 movement; P3a minefield detonation | CONFIRMED (mf/mf07, ob/ob024: stars-elegy #47, apparatus #27) |
| 0x0ca | Your minefield stopped and damaged a fleet, no kills. | Field-owner side of 0x0c6. | field owner | fleet, value (field type), location, value (damage) | fleet (the victim) | P3 movement | CONFIRMED (ob/ob010, mf/mf01: stars-elegy #47, apparatus #27) |
| 0x0cb | Your minefield stopped a fleet and destroyed some ships. | Field-owner side of 0x0c7. | field owner | fleet, value (field type), location, value (damage), count (ships destroyed) | fleet (the victim) | P3 movement | BINARY-ONLY |
| 0x0cc | Your minefield destroyed a fleet. | A fleet of another player is wiped out by your field: during movement, or by detonation. | field owner | object (hidden: salvage if any, otherwise the field), fleet, value (field type), location | object (salvage, or the field) | P3 movement; P3a minefield detonation | CONFIRMED (ob/ob024) |
| 0x0de | A fleet tried to use a stargate where none exists. | Gate order from a place with no stargate (deep space or a gateless planet), and the fleet has no jump gate of its own. | fleet owner | fleet, location (planet or x,y) | fleet | P3 movement | BINARY-ONLY |
| 0x0df | One ship blew up trying to reach warp 10. | Fleet ordered to move at warp 10. Each ship whose engine is not rated for warp 10 has a 1 in 10 chance to explode. Exactly one ship was lost and some survive. Rolled once a year, before fuel matters. | fleet owner | fleet | fleet | P3 movement | CONFIRMED (cs/cs-002) |
| 0x0e0 | Several ships were lost to engine strain at warp 10. | As 0x0df, with two or more ships lost and some surviving. | fleet owner | count (ships lost), fleet | fleet | P3 movement | CONFIRMED (cs/cs-003, fm2) |
| 0x0e1 | A whole fleet was lost to an engine accident. | As 0x0df, but every ship exploded; the fleet is gone. | fleet owner | fleet | fleet | P3 movement | CONFIRMED (ob/ob024) |
| 0x0e2 | Stargate jump failed: no gate at the destination. | Gate order to a planet without a stargate. Applies even if the fleet carries a jump gate. | fleet owner | fleet, planet (shown as the departure gate, but holds the destination; see Notes), location (destination planet) | fleet | P3 movement | CONFIRMED (ob/ob021); LEGACY BUG (the departure slot held the destination) |
| 0x0e3 | Stargate jump failed: destination out of range. | Distance is more than 5× the range of the departure gate. No jump, no losses (cargo already dropped, see 0x0ec). | fleet owner | fleet, planet (where the fleet is), planet (destination) | fleet | P3 movement | BINARY-ONLY |
| 0x0e4 | Stargate jump failed: a ship type is too heavy. | Some ship design in the fleet weighs more than 5× the mass limit of either gate (range is checked first). Names the first such design. No jump. | fleet owner | fleet, planet (departure), planet (destination), design | fleet | P3 movement | CONFIRMED (ob/ob021); LEGACY BUG? (design slot has no owner) |
| 0x0e5 | Stargate jump blocked by the destination owner. | The destination gate belongs to a player who is neither you nor a friend. | fleet owner | fleet, planet, planet, planet (all three hold the destination) | fleet | P3 movement | CONFIRMED (mg/mg001); LEGACY BUG (all three planet slots held the destination) |
| 0x0e6 | Stargate refused at the departure planet. | The departure gate belongs to a player who is neither you nor a friend. | fleet owner | fleet, planet (departure), planet (departure) | fleet | P3 movement | CONFIRMED (ob/ob021) |
| 0x0e7 | A fleet vanished in a stargate jump. | Every ship in the fleet was lost in an overloaded jump (beyond range or mass limits). Either every design was past the point of no survival, or all were killed in the random losses. The fleet is gone. | fleet owner | fleet, planet (departure), planet (destination) | fleet | P3 movement | BINARY-ONLY |
| 0x0e8 | Gate jump made, a few ships lost. | An overloaded jump succeeded with L ships lost (0 < L < 65536) and L < T/4 (T = ships before the jump, integer division). | fleet owner | fleet, planet (departure), planet (destination), count (L) | fleet | P3 movement | BINARY-ONLY |
| 0x0e9 | Gate jump made, a fair number of ships lost. | As 0x0e8 with T/4 ≤ L ≤ T/2. | fleet owner | fleet, planet, planet, count | fleet | P3 movement | CONFIRMED (ob/ob021) |
| 0x0ea | Gate jump made, most ships lost. | As 0x0e8 with L > T/2, survivors remain. | fleet owner | fleet, planet, planet, count | fleet | P3 movement | BINARY-ONLY |
| 0x0eb | Gate jump made with enormous losses. | As 0x0e8 but L ≥ 65536. | fleet owner | fleet, planet, planet, amount (L) | fleet | P3 movement | BINARY-ONLY |
| 0x0ec | Minerals were unloaded before a stargate jump. | Gate order through a departure gate by a non-IT race carrying minerals but no colonists. All minerals go onto the departure planet, even if the jump then fails. If the gate belongs to a friend, the friend gets the same message. | fleet owner; departure planet owner if different | fleet, kT, planet | fleet (owner copy: planet) | P3 movement | CONFIRMED (ob/ob021) |
| 0x0ed | Colonists were unloaded before a stargate jump. | As 0x0ec, with colonists but no minerals. Colonists join the departure planet's population. Only possible at your own planet (see 0x15e). | fleet owner | fleet, colonists, planet | fleet | P3 movement | BINARY-ONLY |
| 0x0ee | Colonists and minerals were unloaded before a stargate jump. | As 0x0ec with both on board. | fleet owner | fleet, colonists, kT, planet | fleet | P3 movement | CONFIRMED (ob/ob021) |
| 0x0f2 | A fleet's engines failed to start this year. | CE race, fleet ordered to move at warp 7 or faster (not by gate): 1 in 10 chance each year that it does not move. | fleet owner | fleet | fleet | P3 movement | CONFIRMED (fm2/fm101) |
| 0x0f3 | Ram scoops made fuel. | A moving fleet that was not stopped by a minefield and was not slowed by 0x08b this year gains ram-scoop fuel > 0 and has tank space. The amount shown is the gain before the tank cap, up to 32500. | fleet owner | fleet, mg | fleet | P3 movement | CONFIRMED (cs/cs-002, fm002, fm003, fm004, fm2) |
| 0x0f4 | Your starbase swept mines. | A starbase that can sweep sits inside a field of a player who is not its owner's friend. The amount follows the same rule as 0x0c2. The starbase's battle plan does not matter, and its rating is not multiplied. | planet owner | planet, amount (mines), player (field owner), value (field type), location (field centre) | planet | P7 sweeping, repair, terraforming | CONFIRMED (ob/ob007, mf/mf01: stars-elegy #47, apparatus #27) |
| 0x0f8 | A fleet's wormhole waypoint was lost from view, so the waypoint now points at empty space where the wormhole was | A second or later waypoint targets a wormhole that still exists but has moved, and the fleet owner no longer knows where it is. Checked at turn start, after objects move, at the end of the turn and again while the player's turn file is written. A wormhole that no longer exists is dropped silently | fleet owner | fleet | fleet | P1a, P5, P7a, P8a | CONFIRMED (ob/ob005) |
| 0x0fb | Colonists bred aboard a fleet. | IS race fleet carrying colonists C. Growth g = C × growth rate/200 kT; if g is 0, a 1 in 3 chance of 1 kT. Sent when any of it fits in the hold. | fleet owner | fleet, colonists | fleet | P3b breeding in transit | BINARY-ONLY |
| 0x137 | A fleet following another fleet has done so and awaits orders. | End of movement, for a fleet that was given a follow-fleet order. Its follow step is dropped whether or not it caught up. | fleet owner | fleet | fleet | P3 movement | CONFIRMED (fo/fo02, fo/fo03) |
| 0x147 | Stargate jump failed: no planet at the destination. | Gate order to a point that is not a planet. | fleet owner | fleet, location (x,y) | fleet | P3 movement | BINARY-ONLY |
| 0x158 | Bred colonists overflowed the hold and were beamed down. | After 0x0fb-type breeding: growth that did not fit goes to the planet the fleet orbits if that planet is yours. Otherwise it is lost silently. | fleet owner | fleet, colonists, planet | fleet | P3b breeding in transit | BINARY-ONLY |
| 0x15e | Stargate refused: colonists on board at a planet you don't own. | Non-IT race using a friend's gate while carrying colonists. Nothing is unloaded and the fleet stays. | fleet owner | fleet, planet | fleet | P3 movement | BINARY-ONLY |
| 0x15f | A fleet was destroyed in a minefield. | Every ship lost and no salvage made: during movement when stopped exactly on a planet, or by another player's detonating field. | fleet owner | fleet (name kept for the dead fleet), player (field owner), value (field type), location | none | P3 movement; P3a minefield detonation | BINARY-ONLY |
| 0x160 | A detonating minefield damaged a fleet, no ships lost. | A field set to detonate damages every fleet inside it, of any owner, except the owner's own mine-layer ships. Each fleet is hit at most once a year. Damage > 0, no ship lost. Location = field centre. | fleet owner (if not the field owner) | fleet, player (field owner), value (field type), location (field centre), value (damage before shields) | fleet | P3a minefield detonation | CONFIRMED (mf/mf07: stars-elegy #47, apparatus #27) |
| 0x161 | A detonating minefield destroyed some of a fleet's ships. | As 0x160 with some (not all) ships destroyed. | fleet owner (if not the field owner) | fleet, player, value (field type), location, value (damage), count (ships destroyed) | fleet | P3a minefield detonation | BINARY-ONLY |
| 0x162 | Your own minefield destroyed one of your fleets. | A detonating field wipes out a fleet of its own owner (a fleet that is not mine-layer ships). | field owner | fleet (name kept), value (field type), location | none | P3a minefield detonation | CONFIRMED (mf/mf07: stars-elegy #47, apparatus #27) |
| 0x163 | Your detonating field damaged a fleet, no kills. | Field-owner side of 0x160, including the owner's own damaged fleets. | field owner | fleet, value (field type), location, value (damage) | fleet | P3a minefield detonation | CONFIRMED (mf/mf07: stars-elegy #47, apparatus #27) |
| 0x164 | Your detonating field destroyed some ships of a fleet. | Field-owner side of 0x161. | field owner | fleet, value (field type), location, value (damage), count (ships destroyed) | fleet | P3a minefield detonation | BINARY-ONLY |

- **Order within movement (per fleet, fleets in number order):** serial refusal (0x102) → engine failure (0x0f2). Then gate path: 0x0e6/0x0de/0x147/0x0e2/0x0e5/0x15e → cargo dump 0x0ec/0x0ed/0x0ee → jump outcome 0x0e3/0x0e4/0x0e7/0x0e8–0x0eb. Or normal path: AR colonist loss 0x0c1 → warp-10 losses 0x0df/0x0e0/0x0e1 → fuel 0x027/0x08b → minefield 0x0c5–0x0cc/0x15f → ram scoop 0x0f3 → radiation 0x074. Once every fleet has moved: 0x04e / 0x137.
- **Minefield message choice:** no damage (speed bump) → stopped; damage with no kills → damaged; some kills → ships destroyed; all ships → annihilated. A destroyed fleet always gets the plain annihilation ids (0x0c8/0x15f/0x0cc/0x162), even in a detonation. The victim is not told when it owns the field; the field owner is always told. Damage is shown before shields and capped at 32760 (CONFIRMED, stars-elegy #47).
- **Detonation:** messages give the field centre, not the fleet's position. A speed bump that detonates sends "stopped" messages (0x0c5/0x0c9) even to fleets that were not moving (CONFIRMED, mf07: stars-elegy #47, apparatus #27). A detonating standard or heavy field that does no damage sends nothing (BINARY-ONLY).
- **Duplicates:** the sweep messages (0x0c2/0x0f4 plus 0x0be) come once per sweeper per field, so several sweepers give the field owner several 0x0be messages in one year. 0x0fb and 0x158 can both go to the same fleet.
- **0x0ec / 0x0ed / 0x0ee:** the cargo dump stands even when the jump then fails (0x0e3, 0x0e4, 0x0e7), so the owner gets both messages. The copy to a friendly gate owner is coded for all three, but for 0x0ed/0x0ee it is NEVER SENT: carrying colonists to a friend's gate is refused first (0x15e).
- **LEGACY BUG 0x0e2 (CONFIRMED, OB-021-H) and 0x0e5 (LEGACY BUG?):** the slot for the departure gate holds the destination, so the message names the destination planet twice (three times in 0x0e5). In OB-021-H a fleet at planet 18 got 0x0e2 with slots (fleet, 20, −1, 20).
- **LEGACY BUG? 0x0e4:** the design slot holds only the design's position in the owner's list, not the owner. For players other than the first, the message may name the wrong player's design. Inferred; not observed.
- **Open:**
  - With a fleet's own jump gate from deep space, the "departure planet" slot of 0x0e3/0x0e4/0x0e7/0x0e8–0x0eb is empty (no planet). How the client shows that is untested.
  - 0x0cc names a fleet that has just been destroyed; whether the client still shows its name is untested.
  - 0x0f3 shows the scoop gain before the tank cap, so it can exceed the fuel actually gained.

### Production, population and random events

| Id | What the player is told | Sent when | To | Slots | Focus | Phase | Status |
|---|---|---|---|---|---|---|---|
| 0x023 | colonists on the planet are all gone; planet lost | an owned planet ends population growth at 0 colonists (it shrank to 0 this year); the planet becomes unowned | planet owner (not AR) | planet | planet | P4a | CONFIRMED (mg/mg002); LEGACY BUG (see Notes) |
| 0x024 | AR variant of 0x023: orbiting colonists gone, starbase and planet lost | as 0x023, owner is Alternate Reality | planet owner (AR) | planet | planet | P4a | BINARY-ONLY |
| 0x025 | population fell from old to new value | owned planet's population shrinks this year but stays above 0, and the planet's hab value for the owner is negative | planet owner | planet, colonists (old), colonists (new) | planet | P4a | CONFIRMED (cb5/cb037-owner, ob/ob007) |
| 0x026 | population fell by an amount because of overcrowding | as 0x025 but hab value ≥ 0 (planet over capacity) | planet owner | planet, colonists (loss) | planet | P4a | CONFIRMED (kx002) |
| 0x02f | starbase built one ship of a design | one ship of a design completes and the planet has no route destination; the new fleet gets the default order | planet owner | planet, design | fleet (new) | P4 | CONFIRMED (cb6/cb047) |
| 0x030 | starbase built several ships of a design | as 0x02f with 2 or more ships in one batch | planet owner | planet, count, design | fleet (new) | P4 | CONFIRMED (cb6/cltool) |
| 0x031 | one new ship built and sent along the planet's route | one ship completes, the planet has a route destination and the new fleet got a moving first leg | planet owner | planet, design, planet (route target) | fleet (new) | P4 | CONFIRMED (sl/sltool) |
| 0x032 | several new ships built and sent along the route | as 0x031 with 2 or more ships | planet owner | planet, count, design, planet (route target) | fleet (new) | P4 | CONFIRMED (sl/sltool) |
| 0x033 | one new ship built but not sent along the route (not enough fuel) | as 0x031 but the route leg got speed 0 | planet owner | planet, design, planet (route target) | fleet (new) | P4 | BINARY-ONLY |
| 0x034 | several new ships built but not routed (fuel) | as 0x033 with 2 or more ships | planet owner | planet, count, design, planet (route target) | fleet (new) | P4 | BINARY-ONLY |
| 0x035 | one factory built | exactly 1 factory installed on the planet this year (summed with earlier single-factory messages of the same year) | planet owner | planet | planet | P4 | CONFIRMED (kx001, pq001, mg/mg002) |
| 0x036 | N factories built | factories installed this year total > 1 by the merge rule in Notes | planet owner | count, planet | planet | P4 | CONFIRMED (kx001, kx002, pq001, mg/mg002); LEGACY BUG (split totals, mg/mg002) |
| 0x037 | one mine built | as 0x035 for mines | planet owner | planet | planet | P4 | BINARY-ONLY |
| 0x038 | N mines built | as 0x036 for mines | planet owner | count, planet | planet | P4 | CONFIRMED (kx001, kx002, pq001); LEGACY BUG? |
| 0x039 | one defense built | as 0x035 for defenses | planet owner | planet | planet | P4 | BINARY-ONLY |
| 0x03a | N defenses built | as 0x036 for defenses | planet owner | count, planet | planet | P4 | CONFIRMED (kx001, kx002, pq001); LEGACY BUG? |
| 0x03e | planet finished its orders; queue now empty | after the planet's queue is processed: the queue became empty, or production reached the end of the queue with no auto item held back by missing minerals. Not sent when production stopped on an unfinished regular item, or when the planet made 0 resources | planet owner | planet | planet | P4 | CONFIRMED (cb6/cltool) |
| 0x03f | planet has no production queue | every year for every owned planet with no queue | planet owner | planet | planet | P4 | CONFIRMED (cb5/cb035-prevbattle, KX-004, many sets) |
| 0x040 | colonists left the planet; planet lost | an owned planet already has 0 colonists when population growth runs; planet becomes unowned. Which of 0x040/0x023 is used depends on the previous planet (see Notes) | planet owner (not AR) | planet | planet | P4a | CONFIRMED (mg/mg002); LEGACY BUG (see Notes) |
| 0x041 | AR variant of 0x040: colonists left the starbase; planet lost | as 0x040, owner is Alternate Reality | planet owner (AR) | planet | planet | P4a | BINARY-ONLY |
| 0x04f | starbase could not build a ship because the design is gone | a ship design order completes at a planet with a starbase but the design was deleted or can no longer be built; resources are spent and the order is dropped | planet owner | planet, count | planet | P4 | BINARY-ONLY; LEGACY BUG? (slots filled wrongly) |
| 0x07b | terraforming moved one hab axis up or down to a new value | each terraform unit completed (regular or auto terraform): one click on the best axis; one message per click. A unit with no useful axis is used up with no message | planet owner | planet, value (1 up / 0 down), hab, hab value | planet | P4 | CONFIRMED (kx002) |
| 0x07c | planet built a planetary scanner of a named type | a scanner order completes; the generic scanner order becomes the best scanner the owner has | planet owner | part | planet | P4 | BINARY-ONLY |
| 0x083 | small comet hit a planet (minerals added, environment changed) | comet strike, severity small (see Notes) | every player except a non-AR owner of the planet; AR owner too | planet | planet | P4c | CONFIRMED (KX-004) |
| 0x084 | medium comet hit a planet | as 0x083, medium | as 0x083 | planet | planet | P4c | CONFIRMED (KX-004) |
| 0x085 | large comet hit a planet | as 0x083, large | as 0x083 | planet | planet | P4c | CONFIRMED (KX-004) |
| 0x086 | huge comet hit a planet | as 0x083, huge | as 0x083 | planet | planet | P4c | CONFIRMED (KX-004) |
| 0x087 | small comet hit your planet: 25% of colonists killed, one hab axis changed | comet strike, small, planet owned by a non-AR player | planet owner | planet, hab | planet | P4c | CONFIRMED (KX-004); LEGACY BUG? (named axis is not the one changed, measured) |
| 0x088 | medium comet hit your planet: 45% killed, two hab axes changed | as 0x087, medium | planet owner | planet, hab, hab | planet | P4c | CONFIRMED (KX-004); LEGACY BUG? (axis names may differ from changed axes) |
| 0x089 | large comet hit your planet: 65% killed, all three axes changed | as 0x087, large | planet owner | planet, hab, hab, hab | planet | P4c | CONFIRMED (KX-004) |
| 0x08a | huge comet hit your planet: 85% killed, all three axes changed | as 0x087, huge | planet owner | planet, hab, hab, hab | planet | P4c | CONFIRMED (KX-004) |
| 0x08c | alchemy made a number of kT of each mineral | one queue item's processing turned resources into minerals (alchemy items completed, plus alchemy bought for the next item when an auto-alchemy item is in front of it) | planet owner | planet, kT | planet | P4 | CONFIRMED (kx001, pq001) |
| 0x0b9 | scanner order cancelled: planet already has a scanner | production reaches a scanner order on a planet that already has a planetary scanner (planet makes > 0 resources); order removed | planet owner | planet | planet | P4 | BINARY-ONLY |
| 0x0ba | ships built but lost because the player is at the fleet limit | player already has 512 fleets and no own fleet at the planet can take the new ships; resources spent, order dropped | planet owner | planet, count, design | planet | P4 | BINARY-ONLY |
| 0x0cd | planet built a starbase that can build no ships | a starbase design order completes and the hull has no ship-building capacity | planet owner | planet, design | planet | P4 | CONFIRMED (sl/sltool) |
| 0x0ce | planet built a starbase; can now build ships up to a hull mass | as 0x0cd, hull with a mass limit | planet owner | planet, design, kT | planet | P4 | BINARY-ONLY |
| 0x0cf | planet built a starbase; can now build ships of any size | as 0x0cd, hull with no mass limit | planet owner | planet, design | planet | P4 | BINARY-ONLY |
| 0x0d1 | packet broke up: no mass driver | coded for a packet completed at a planet without a mass driver | planet owner | planet | planet | P4 | NEVER SENT (inferred: such packet orders are removed or capped to 0 before anything is built) |
| 0x0d2 | packet broke up: mass driver has no destination | coded for a packet completed with no destination | planet owner | planet | planet | P4 | NEVER SENT (inferred, same reason) |
| 0x0d3 | planet produced a packet aimed at a destination | packet order completes and a new packet object is launched | planet owner | planet, planet (destination) | planet | P4 | BINARY-ONLY |
| 0x0d4 | packet produced and merged into another packet going to the destination | packet order completes and joins an own packet still at the planet with the same speed and destination (and not too large) | planet owner | planet, planet (destination) | planet | P4 | BINARY-ONLY |
| 0x0fd | climate change altered one hab axis permanently; production orders cancelled | climate-change event on an owned planet (see Notes); regular build orders removed, auto orders kept | planet owner | planet, hab | planet | P4c | CONFIRMED (KX-004) |
| 0x0fe | new deposit of a mineral found, raising its concentration | mineral-discovery event on an owned planet; sent even when the concentration is already ≥ 180 and does not rise | planet owner | planet, mineral | planet | P4c | CONFIRMED (KX-004) |
| 0x11b | a planet was reborn by a Genesis Device | Genesis Device order completes | every player | planet | planet | P4 | BINARY-ONLY |
| 0x129 | packet order cancelled: no mass driver or no target | production reaches a packet order on a planet without a mass driver or without a destination; order removed. Also used when a packet is completed but the galaxy's object limit is full (packet lost, resources spent) | planet owner | planet | planet | P4 | BINARY-ONLY |
| 0x12a | installation orders over the limit; reduced to the maximum | production reaches a factory, mine or defense order asking for more than the planet can still hold; order cut to what fits, or removed if none fit. Repeats each year it applies | planet owner | planet | planet | P4 | CONFIRMED (kx002, pq001) |
| 0x12c | fleet improved a planet's value from X% to Y% | end-of-turn remote terraforming by a fleet with terraforming hardware orbiting an owned planet, own or allied (friendly), when the value changed; also to a different (allied) planet owner | fleet owner; planet owner if different | fleet, planet, percent (before), percent (after) | fleet (to fleet owner) / planet (to planet owner) | P7 | BINARY-ONLY |
| 0x12d | fleet cannot improve the planet beyond X% | as 0x12c, friendly, value did not change (repeats every turn while parked) | fleet owner | fleet, planet, percent | fleet | P7 | BINARY-ONLY |
| 0x12f | terraform order over the limit; reduced to the maximum | production reaches a terraform order asking for more clicks than remain toward the owner's ideal; cut or removed | planet owner | planet | planet | P4 | CONFIRMED (kx002) |
| 0x139 | ships built but merged into an existing nearby fleet (fleet limit) | player already has 512 fleets; new ships join the first own fleet at the planet that can take them | planet owner | planet, count, design, fleet | fleet (merged) | P4 | BINARY-ONLY |
| 0x156 | Claim Adjuster planet improved automatically; new environment given | end of turn, for each planet of a Claim Adjuster player, when free terraforming can still move the planet: every axis jumps straight to the best target its tech allows | planet owner | planet, percent | planet | P7 | CONFIRMED (tk2/tk108, kx003) |
| 0x15a | fleet degraded a planet's value from X% to Y% | as 0x12c but the fleet is not friendly and the planet has no starbase; value changed; also to the planet owner | fleet owner; planet owner | fleet, planet, percent, percent | fleet / planet | P7 | BINARY-ONLY |
| 0x15b | fleet cannot degrade the planet any further | as 0x15a, value did not change | fleet owner | fleet, planet, percent | fleet | P7 | BINARY-ONLY |
| 0x15c | Claim Adjuster engineers moved a planet's underlying hab by 1 | end of turn, Claim Adjuster planet: pick a random axis; if it is not immune and the original value is not already ideal, with chance 1/10 and (population ≥ 100,000 or a random roll below population/100 out of 1000) the original value moves 1 toward ideal | planet owner | planet, hab | planet | P7 | BINARY-ONLY |

- Order inside production (P4): planets are handled one at a time in planet-number order. For one planet: the no-queue message (0x03f), or for each order in turn its checks (0x0b9, 0x129, 0x12a, 0x12f), alchemy (0x08c) and build messages; then 0x03e. Population messages (P4a) come after all planets, then the random events in this order: comet, climate change, mineral discovery (P4c). Claim Adjuster messages (0x15c before 0x156 for the same planet) and then remote terraforming come at the end of the turn (P7).
- A planet that makes 0 resources this year skips its queue entirely: no limit, cancel or completion messages.
- 0x03e can come in the same year as a cancel message (0x0b9, 0x129, 0x12a, 0x12f) when that cancel empties the queue. Inferred, not yet observed: a queue holding only auto orders that all finish sends 0x03e every year.
- 0x08c is sent once per queue order that produced alchemy, so one planet can get several in a year. Alchemy paid into an unfinished partial unit is not counted.
- Merging of build counts (0x035–0x03a): when a planet builds the same installation twice in one year, earlier *single-unit* messages are removed and added into the new count. Plural messages are not merged. LEGACY BUG (display only), CONFIRMED in MG-002 (two factory items on one planet):
  - 3 then 2 gave two 0x036 messages (3 and 2);
  - 1 then 4 gave one 0x036 with 5;
  - 2 then 1 gave 0x036 with 2, then 0x035;
  - 1 then 1 gave one 0x036 with 2.
- 0x04f looks wrong: the first slot holds the design's slot number plus 1, not the planet. The message probably names an unrelated planet (the one whose number equals that value) and shows type 0. LEGACY BUG? (not observed). A starbase design that is gone fails without any message, and so does a ship order at a planet with no starbase.
- 0x040 vs 0x023 (and 0x041 vs 0x024): a planet that dies out during growth gets 0x023/0x024 and no 0x025/0x026. For a planet that already had 0 colonists, the choice uses a value left over from the previous planet processed: 0x023 if that planet shrank, else 0x040. So the "left" message can show up as "died". LEGACY BUG, CONFIRMED in MG-002 (both streams):
  - planet 3 (0 colonists) after planet 2 shrank from overcrowding: 0x023;
  - planet 6 (0 colonists) after planet 5 grew: 0x040;
  - planet 0, the first planet: 0x040.
  - A packet that hits an owned empty planet also leads to this (MG-001-C: 0x181, then 0x040).
  - Open question: other ways an owned planet can reach this point with 0 colonists.
- Comet strike (P4c): 1 in 20 chance per year. The planet is chosen at random. It is protected while the game is in its first 10 years, and while the planet is owned with more than 5,000 colonists before year 20. Severity is chosen at random: small, medium, large or huge, each 1/4. A non-AR owner loses trunc(pop × (25, 45, 65, 85)% ) colonists. MEASURED in KX-004: 9237 → 6928, 5081, 1386; 8110 → 2839. Every mineral gains a little surface mineral. One, two or three randomly chosen minerals gain a lot more, and their concentration rises by 50–99 (huge: 65–128), capped at 200. Hab axes are changed in fixed order (gravity, then temperature, then radiation): small changes one axis, medium two, large and huge all three. Each changes by ±3–5 (huge ±6–10), applied to both the current and the original value, clamped to 1–99. Regular build orders are removed and no 0x0fd is sent. An unowned planet can be hit; then every player gets 0x083–0x086.
- Comet axis names (0x087, 0x088): the axes named in the message come from a separate random shuffle, not from the axes actually changed. KX-004 S2: a small comet changed gravity (+4) but the message named radiation. LEGACY BUG? For large and huge comets all three axes change, so only the naming order is arbitrary.
- Climate change (0x0fd): 1 in 20 chance per year, random planet. It has the same protection for large owned planets before year 20, but no 10-year minimum (KX-004 S3: unowned planet changed in year 5 while a comet was suppressed). Shift on one random axis: ±4 or ±5 (1/3 each), or ±6, ±7, ±8 (1/9 each). It is applied to both the current and the original value. The message comes only if the planet is owned; regular build orders are removed either way.
- Mineral discovery (0x0fe): chance 1/(15 − universe size index) per year, random planet, from year 10. Random mineral; concentration +5 to +19 if it is below 180. Unowned planets change silently.
- Remote terraforming (0x12c/0x12d/0x15a/0x15b): sent every turn for each fleet with terraforming hardware orbiting an owned planet, even when nothing changes. A non-friendly fleet does nothing (and sends nothing) at a planet with a starbase. The planet owner hears only when the fleet owner is someone else and the value changed. Both percentages use the planet owner's race.
- 0x129 is reused for a completed packet lost because the galaxy's object limit is full. The text then gives the wrong reason.
- 0x0d1/0x0d2 are coded but appear unreachable: packet orders without a driver or target are cancelled earlier (0x129), and auto-packet orders build nothing in that case.

### Research, end of game, turn-file checks and viewer messages

| Id | What the player is told | Sent when | To | Slots | Focus | Phase | Status |
|---|---|---|---|---|---|---|---|
| 0x028 | A fleet's target fleet is gone; the fleet goes to its last known position | End of turn: a later waypoint follows a fleet that no longer exists | fleet owner | fleet, fleet | fleet | P8a | BINARY-ONLY |
| 0x029 | A tracked fleet was lost from view at a planet; orders now go to that planet | As 0x028, when the followed fleet still exists but is out of sight and is at a planet | fleet owner | fleet, planet | fleet | P8a | BINARY-ONLY |
| 0x02a | A tracked fleet moved out of scanner range; orders now go to its last known position | As 0x029, when the followed fleet is in deep space | fleet owner | fleet | fleet | P8a | BINARY-ONLY |
| 0x050 | A research field reached a new level; research stays in the same field (or moves to the named field) | A field gains a level and the player does not have Generalized Research. One message per level, so a big surplus can give several. Fields at level 26 (or at level 10 for a player flagged for an invalid or duplicated registration) do not level, and research put into them is lost. The third slot is the field researched next: the chosen next field if the leveled field was the current one and the "next" setting is not "same field" ("lowest field" picks the lowest-level field, the first one on ties); otherwise the current field | field owner | count (new level), field, field | research | P4b (also after battles/invasions, P6) | CONFIRMED (cb5/cb041-sf-joat, ob/ob004, tk2, kx003, kx004) |
| 0x05f | A level-up also made a new component available | After each level-up message: one per component the race may use whose requirement in the leveled field equals the new level. The other five field requirements are not checked here. Not used for hulls, planetary scanners or defenses | field owner | field, part (category, item) | part (inferred: component in tech browser) | P4b | CONFIRMED (cb5/cb041-sf-joat, ob/ob004, kx003, kx004) |
| 0x078 | A level-up made a new ship hull available | As 0x05f, for ship hulls | field owner | field, part | special (inferred: ship design) | P4b | CONFIRMED (ob/ob004, kx004) |
| 0x0aa | Newly found planet is owned by another player | When the turn is opened: a newly seen planet that is owned by someone else | viewer | planet, player | planet | L | BINARY-ONLY (not stored) |
| 0x0ab | Newly found planet is not habitable; colonists would die each year | Newly seen, unowned, details known, not habitable even with terraforming. Percent = negative planet value ×10 / 100 | viewer | percent, planet | planet | L | BINARY-ONLY (not stored) |
| 0x0ac | Newly found habitable planet, with the best yearly growth | Newly seen, unowned, details known, habitable now. Percent = planet value × the race's maximum growth rate | viewer | percent, planet | planet | L | BINARY-ONLY (not stored) |
| 0x0ad | Newly found planet, habitability not known yet | Newly seen, unowned, only a basic scan | viewer | planet | planet | L | BINARY-ONLY (not stored) |
| 0x0ae | Newly found planet that terraforming could make habitable | Newly seen, unowned, not habitable now but positive after terraforming. Percent = terraformed value × maximum growth rate | viewer | percent, planet | planet | L | BINARY-ONLY (not stored) |
| 0x0b5 | Other players have been declared winners | Two or more players alive, the minimum years have passed and the number of required conditions is above 0. Winners = players meeting at least the required number of enabled victory conditions. Repeated every turn while that holds | every living non-winner | players | special: scores (inferred) | P8 | BINARY-ONLY |
| 0x0b6 | The player alone has won | As 0x0b5, with exactly one winner | the winner | - | special: scores (inferred) | P8 | BINARY-ONLY |
| 0x0b7 | You and others have been declared joint winners | As 0x0b5, with several winners | each winner | players (the other winners) | special: scores (inferred) | P8 | BINARY-ONLY |
| 0x0b8 | The player has been eliminated | A winner was declared this turn (as 0x0b5): sent to dead players; or at most one player is left alive: sent to everyone but the top-ranked player. Repeated every turn | dead players; or all but the survivor | - | special: scores (inferred) | P8 | CONFIRMED (cb5/cb041, last-survivor case) |
| 0x0bb | Another race has been wiped out | The first turn a player has no planets and no ships (starbases ignored). The player is then marked dead | every other player, dead and computer players included | player | special: scores (inferred) | P8 | CONFIRMED (cb5/cb041) |
| 0x0bc | You are the last race left | At most one player is left alive, and the top-ranked player is not dead. Repeated every turn | the survivor | - | special: scores (inferred) | P8 | CONFIRMED (cb5/cb041) |
| 0x0d0 | A level-up made a new starbase hull available | As 0x05f, for starbase hulls | field owner | field, part | special (inferred: ship design) | P4b | BINARY-ONLY |
| 0x0ff | A patrolling fleet has picked a target to intercept | End of turn: a fleet on patrol, with no next waypoint that already follows a fleet, chooses the nearest visible enemy fleet that its battle orders allow it to attack, within the patrol range. Targets not yet claimed by another patroller are preferred. A follow-fleet waypoint is inserted | fleet owner | fleet, fleet | fleet | P8a | BINARY-ONLY |
| 0x110 | A waypoint on the Mystery Trader was lost from view | As 0x0f8, for a trader target that is no longer seen | fleet owner | fleet | fleet | P8a | BINARY-ONLY |
| 0x111 | A waypoint on a minefield was lost from view | As 0x0f8, for a minefield the player can no longer see | fleet owner | fleet | fleet | P8a | BINARY-ONLY |
| 0x136 | Same as 0x050, but worded as a primary research focus | As 0x050, for a player with Generalized Research (every level-up uses this id) | field owner | count, field, field | research | P4b | BINARY-ONLY |
| 0x13a | Component technology recovered from battle wreckage | Same once-per-turn 50% gate as 0x0ef. Tried before the research bonus: up to 13 random picks among Mystery Trader items seen on ships killed in the battle (chance per item up to 25%), not already owned | that player | location | part | P6 | BINARY-ONLY |
| 0x13b | Hull technology recovered from battle wreckage | As 0x13a, when the item is the trader hull | that player | location | part | P6 | BINARY-ONLY |
| 0x145 | A level-up gave a new planetary defense, and existing defenses are upgraded | As 0x05f, for planetary defenses | field owner | field, part | part | P4b | CONFIRMED (kx003, kx004) |
| 0x151 | A mass packet is heading for one of your planets, which cannot catch it safely | When the turn is opened: a packet aimed at a planet of the viewer that is faster than the planet's catch speed (best mass driver warp, +1 with two drivers). Any packet owner, the viewer's own included | viewer | object, planet | special (inferred: packet/planet) | L | BINARY-ONLY (not stored in files) |
| 0x152 | A starbase will finish its whole production queue this year | When the turn is opened (not in the tutorial): every queue item at a starbase planet of the viewer is due within a year, and at least one item due this year is not an automatic build item. Orbital forts are excluded (inferred) | viewer | planet | planet | L | BINARY-ONLY (not stored) |
| 0x153 | There is one battle to view | When the turn is opened (not in the tutorial) and it has one battle. Placed first in the list | viewer | - | battle | L | BINARY-ONLY (not stored) |
| 0x154 | Several battle recordings this year | As 0x153, with more than one battle | viewer | count | battle | L | BINARY-ONLY (not stored) |
| 0x157 | A level-up gave a new planetary scanner, and existing scanners are upgraded | As 0x05f, for planetary scanners | field owner | field, part | part | P4b | BINARY-ONLY |
| 0x159 | Spying on other players added research to a field | Super Stealth players only, when at least 2 players are still alive. For each field: bonus = trunc(trunc(total research put into the field this turn by all players, the SS player included, / alive players) / 2). Sent when the bonus is above 1. Level-ups it causes follow afterwards | each Super Stealth player | field, count (resources) | research | P4b | CONFIRMED (tk2/tk113, kx003) |
| 0x15d | Newly found planet and the value it could reach | As 0x0ac/0x0ae/0x0ab, but for a Claim Adjuster player | viewer | planet, percent | planet | L | BINARY-ONLY (not stored) |

- **Research order:** for each level gained, the level message comes first, then that level's component messages. Players are handled in player order and fields in field order. Super Stealth bonuses (0x159) come after all players, followed by any level-ups they cause.
- **0x050 vs 0x136:** the choice depends only on whether the player has Generalized Research.
- **Wrong id in an earlier note:** an earlier private reading had 0x150 for the normal level-up message. The correct id is 0x050, and the oracle files agree.
- **Component announcements:** they check only the leveled field. A component that also needs another field the player has not reached yet may still be announced (open question; experiment listed in research notes).
- **Invasion uses 0x0ef:** a ground invasion that wins can give the attacker research. The message used is 0x0ef, whose wording is about battle wreckage. Invasions never give trader components.
- **Slow-tech research bonus:** under the slow-tech option the bonus from wreckage or invasion is half a level's cost, rounded down. The message shows twice that amount, so an odd cost is reported 1 too low.
- **LEGACY BUG? 0x13e:** a trader planetary device found through battle wreckage would be reported with a ship-scrapping text, and its slots would be misread. It is likely unreachable.
- **Repeating end-game messages:** victory and last-survivor messages (0x0b5–0x0b8, 0x0bc) are re-sent every turn while the condition holds. They are placed at the front of the message list.
- **Death messages:** a player who dies gets no message of their own (0x0b8) unless the game is decided that turn. Only the other players get 0x0bb.
- **LEGACY BUG? last survivor:** the survivor is taken to be the top-ranked player. If the survivor's score ties at 0 with a dead player of a higher player number, the survivor may get 0x0b8 and nobody gets 0x0bc. Untested.
- **Registration penalties:** 0x100/0x101/0x103 come in the order phase. 0x104–0x107 come after terraforming. A fleet with no mineral cargo gets no 0x105.
- **Follow-fleet checks:** the follow check (0x138) runs before movement. The later-waypoint checks (0x028/0x029/0x02a/0x0f8/0x110/0x111, 0x0ff) run while the player's turn file is written, so they show in the next year's messages. A packet or salvage target that disappears is retargeted with no message. For 0x029, the new target is whatever object is nearest the old position, which may not be the planet the message names (open question).
- **Race legality (0x117/0x182):** in a 6-player run, 0x182 reached all four other human players. A computer player's file has no message block, so its copy cannot be observed (apparatus #27, rd/rp12). At game creation, 0x117 is sent even when the offender is a computer player. During a running game it is not.
- **Viewer-load messages (L):** these are not stored in turn files and are recreated every time the turn is opened. A newly found planet's message reappears on every reload in the same year. Computer players and the host file get none.

### Battles and bombing

| Id | What the player is told | Sent when | To | Slots | Focus | Phase | Status |
|---|---|---|---|---|---|---|---|
| 0x00e–0x022 | Older-style battle summaries (blood bath, one-sided wins, observed fights, mutual destruction) | Never: no battle or bombing step produces an id in this range; the battle step picks its summary from 0x07e, 0x08d–0x0a8 and 0x113–0x116 only | - | (as stored) | - | P6 | NEVER SENT |
| 0x060 | Your fleet killed colonists by bombing | No installations destroyed, colonists killed, planet still populated; one attacking fleet; sent even when defenses stopped some bombs | attacker | fleet, planet, colonists | fleet | P6a | CONFIRMED (cs/cs-003) |
| 0x061 | Your fleet destroyed one installation | 1 installation destroyed, no colonists killed, no bombs stopped; one fleet | attacker | fleet, planet, count | fleet | P6a | BINARY-ONLY |
| 0x062 | Your fleet destroyed several installations | 2 or more installations destroyed, no colonists killed, no bombs stopped; one fleet | attacker | fleet, planet, count | fleet | P6a | BINARY-ONLY |
| 0x063 | Your fleet killed colonists and destroyed one installation | 1 installation and some colonists, no bombs stopped; one fleet | attacker | fleet, planet, colonists, count | fleet | P6a | BINARY-ONLY |
| 0x064 | Your fleet killed colonists and destroyed several installations | 2+ installations and some colonists, no bombs stopped; one fleet | attacker | fleet, planet, colonists, count | fleet | P6a | CONFIRMED (cs/cs-003) |
| 0x065, 0x06f, 0x16b, 0x175 | Colonists killed by bombing, with the share of bombs stopped by defenses | Never: when bombing kills only colonists, the plain colonist-kill message (0x060/0x06a/0x166/0x170) is sent even if defenses stopped some bombs | - | fleet, planet, colonists, percent | - | P6a | NEVER SENT LEGACY BUG? |
| 0x066 | Your fleet destroyed one installation; defenses stopped a share of bombs | As 0x061 but planetary defenses stopped some bombs | attacker | fleet, planet, count, percent | fleet | P6a | BINARY-ONLY |
| 0x067 | Your fleet destroyed several installations; defenses stopped a share | As 0x062 with some bombs stopped | attacker | fleet, planet, count, percent | fleet | P6a | BINARY-ONLY |
| 0x068 | Your fleet killed colonists and one installation; defenses stopped a share | As 0x063 with some bombs stopped | attacker | fleet, planet, colonists, count, percent | fleet | P6a | BINARY-ONLY |
| 0x069 | Your fleet killed colonists and several installations; defenses stopped a share | As 0x064 with some bombs stopped | attacker | fleet, planet, colonists, count, percent | fleet | P6a | CONFIRMED (tk/tk005) |
| 0x06a | A fleet bombed your planet, killing colonists | As 0x060 | planet owner | fleet, planet, colonists | planet | P6a | CONFIRMED (cs/cs-003) |
| 0x06b | A fleet destroyed one of your installations | As 0x061 | planet owner | fleet, planet, count | planet | P6a | BINARY-ONLY |
| 0x06c | A fleet destroyed several of your installations | As 0x062 | planet owner | fleet, planet, count | planet | P6a | BINARY-ONLY |
| 0x06d | A fleet killed your colonists and destroyed one installation | As 0x063 | planet owner | fleet, planet, colonists, count | planet | P6a | BINARY-ONLY |
| 0x06e | A fleet killed your colonists and destroyed several installations | As 0x064 | planet owner | fleet, planet, colonists, count | planet | P6a | CONFIRMED (cs/cs-003) |
| 0x070 | A fleet destroyed one of your installations; your defenses stopped a share | As 0x066 | planet owner | fleet, planet, count, percent | planet | P6a | BINARY-ONLY |
| 0x071 | A fleet destroyed several of your installations; defenses stopped a share | As 0x067 | planet owner | fleet, planet, count, percent | planet | P6a | BINARY-ONLY |
| 0x072 | A fleet killed your colonists and one installation; defenses stopped a share | As 0x068 | planet owner | fleet, planet, colonists, count, percent | planet | P6a | BINARY-ONLY |
| 0x073 | A fleet killed your colonists and several installations; defenses stopped a share | As 0x069 | planet owner | fleet, planet, colonists, count, percent | planet | P6a | CONFIRMED (tk/tk005) |
| 0x07e | A battle happened here; open the recording | Battle with 3 or more races in which both your side and the enemy side lost some, but not all, of their forces | each participant | location | battle | P6 | CONFIRMED (cb6/cb042) |
| 0x08d | Your starbase was destroyed and a large population died with it | An Alternate Reality starbase is destroyed in battle and its planet held more than 1000 (×100) colonists; the planet is emptied | starbase owner | location, design, colonists | battle | P6 | BINARY-ONLY |
| 0x08e | Your starbase was destroyed and its whole population died | As 0x08d with at most 1000 (×100) colonists | starbase owner | location, design, colonists | battle | P6 | CONFIRMED (cb5/cb041-sf) |
| 0x08f | Your fleet killed all colonists by bombing | Planet population is 0 after this bombing; one attacking fleet | attacker | fleet, planet | fleet | P6a | CONFIRMED (tk2/tk114) |
| 0x090 | A fleet bombed your planet and killed all colonists | As 0x08f | planet owner | fleet, planet | planet | P6a | CONFIRMED (tk2/tk114) |
| 0x091 | Your ship destroyed the single enemy ship and was not hit | 2-player battle with exactly 2 ships present (starbase counts as a ship); yours survived unhit, the enemy's died | each participant | location, design, design | battle | P6 | CONFIRMED (cs/cs-003) |
| 0x092 | Your ship was destroyed by the enemy ship, which was not hit | Same 2-ship battle; yours died (reported even if the enemy also died); enemy unhit | each participant | location, design, design | battle | P6 | CONFIRMED (cs/cs-003) |
| 0x093 | Your ship destroyed the enemy ship but was damaged | 2-ship battle; yours survived after being hit, enemy died | each participant | location, design, design | battle | P6 | CONFIRMED (cb5/cb035-prevbattle) |
| 0x094 | Your ship was destroyed by the enemy ship, which was damaged | 2-ship battle; yours died, enemy was hit | each participant | location, design, design | battle | P6 | CONFIRMED (cb5/cb035-prevbattle) |
| 0x095 | Neither ship in a one-on-one fight was destroyed | 2-ship battle; both survived | each participant | location, design, design | battle | P6 | CONFIRMED (cs/cs-003) |
| 0x096 | Your stack wiped out the enemy stack without being hit (with ship counts) | 2-player battle with more than 2 ships but exactly 2 stacks; your stack has survivors and was not hit, enemy stack has none | each participant | location, design, count, design, count | battle | P6 | CONFIRMED (cb5/cb040) |
| 0x097 | Your stack was wiped out by an unhit enemy stack | 2-stack battle; your stack has no survivors (takes precedence), enemy not hit | each participant | location, design, count, design, count | battle | P6 | CONFIRMED (cb5/cb040) |
| 0x098 | Your stack wiped out the enemy stack but was damaged | 2-stack battle; yours survived after being hit, enemy wiped | each participant | location, design, count, design, count | battle | P6 | CONFIRMED (cb4/cb026) |
| 0x099 | Your stack was wiped out by a damaged enemy stack | 2-stack battle; yours wiped, enemy was hit | each participant | location, design, count, design, count | battle | P6 | CONFIRMED (cb4/cb026) |
| 0x09a | Neither stack was completely destroyed | 2-stack battle; both have survivors | each participant | location, design, count, design, count | battle | P6 | CONFIRMED (cb5/cb039) |
| 0x09b | Your forces wiped out the enemy with no losses | Other 2-player battles: enemy lost everything, you lost nothing, you had more than one ship | each participant | location, player, count | battle | P6 | CONFIRMED (cb5/cb041-sf) |
| 0x09c | You lost every ship and the enemy lost none | Other 2-player battles: you lost everything (more than one ship), enemy lost none and had more than one ship | each participant | location, player, count | battle | P6 | CONFIRMED (cb5/cb041-sf) |
| 0x09d | Your forces wiped out the enemy but you lost some ships | Other 2-player battles: enemy lost everything (more than one ship), you lost at least one (also when both sides were wiped) | each participant | location, player, count, count | battle | P6 | CONFIRMED (cb5/cb041-joat) |
| 0x09e | All your forces were destroyed, but you destroyed some enemy ships | Other 2-player battles: you lost everything (more than one ship), enemy lost some but not all | each participant | location, player, count, count | battle | P6 | CONFIRMED (cb5/cb041-joat) |
| 0x09f | Neither side was wiped out; totals and losses for both | Other 2-player battles: both sides have survivors, each side had more than one ship | each participant | location, player, count, count, count, count | battle | P6 | CONFIRMED (cb5/cb041-sf-joat) |
| 0x0a0 | Your forces destroyed the single enemy ship with no losses | Other 2-player battles: enemy had one ship and lost it, you lost nothing | each participant | location, player, count, design | battle | P6 | CONFIRMED (tk/tk002) |
| 0x0a1 | Your single ship was destroyed and the enemy lost nothing | Other 2-player battles: you had one ship and lost it, enemy lost none | each participant | location, player, design, count | battle | P6 | CONFIRMED (cb5/cb035-prevbattle) |
| 0x0a2 | Your forces destroyed the single enemy ship but you lost some | Enemy had one ship and lost it, you lost at least one | each participant | location, player, count, design, count | battle | P6 | BINARY-ONLY |
| 0x0a3 | Your single ship was destroyed after destroying some enemy ships | You had one ship and lost it, enemy lost some but not all | each participant | location, player, design, count, count | battle | P6 | BINARY-ONLY |
| 0x0a4 | Multi-race battle: you wiped out all enemies with no losses | Battle with 3 or more races; you lost nothing, every other force was destroyed | each participant | location, count (races), count | battle | P6 | CONFIRMED (cb5/cb036) |
| 0x0a5 | Multi-race battle: all enemies destroyed, you lost some | 3+ races; you lost some, every other force was destroyed (also when you were wiped too) | each participant | location, count (races), count, count | battle | P6 | BINARY-ONLY |
| 0x0a6 | Multi-race battle: you were wiped out without destroying anything | 3+ races; you lost everything, no other force lost anything | each participant | location, count (races), count, count | battle | P6 | CONFIRMED (cb4b/cb033) |
| 0x0a7 | Multi-race battle: you were wiped out but destroyed some enemies | 3+ races; you lost everything, others lost some but not all | each participant | location, count (races), count, count, count | battle | P6 | CONFIRMED (cb5/cb036) |
| 0x0a8 | Multi-race battle: losses and totals for you and everyone else | 3+ races; you lost nothing and the others were not all destroyed; or the others lost nothing and you lost some but not all | each participant | location, count (races), count, count, count, count | battle | P6 | CONFIRMED (cb4b/cb034) |
| 0x0ef | Battle wreckage (or a won invasion) gave research in a field | At most once per player per turn, on a 50% roll: (a) after a battle the player took part in and still has forces at (any survivor in 2-player battles; always in multi-race battles), in deep space, at an unowned planet or at the player's own planet; (b) after the player captures a planet by invasion. Gain = one level's cost in a random field where the opponent's (defender's) tech is higher | that player | location, field, amount | special: research (inferred) | P6, P6c | CONFIRMED (cb4/cb031-n3, cb5/cb041-sf-joat, tk2/tk115) |
| 0x0f0 | Wreckage from a battle at a planet boosted research | After 0x0fa (a non-participant with a fleet at the battle), with the same per-turn roll; no location condition | that fleet's owner | location, field, amount | special: research (inferred) | P6 | CONFIRMED (cb5/cb037-owner); LEGACY BUG? (text says in orbit, also used in deep space) |
| 0x0f1 | A fleet found battle wreckage that boosted research | After 0x0f9 (the battle was at the player's planet and the player was not in it), with the same per-turn roll | that planet's owner | location, field, amount | special: research (inferred) | P6 | BINARY-ONLY; LEGACY BUG? (fleet wording for a planet owner) |
| 0x0f9 | Your colony saw a battle in orbit that you were not part of | Battle at your planet (one with no starbase) without your involvement | planet owner | planet | planet | P6 | BINARY-ONLY |
| 0x0fa | One of your fleets saw a battle it was not part of | You are not in the battle, have a fleet there, and pass a faulty observer test (see Notes) | non-participant fleet owner | fleet, location | fleet | P6 | CONFIRMED (cb5/cb035-prevbattle); LEGACY BUG, same test as `COMBAT.md` CB-037 |
| 0x113 | Your single ship destroyed every enemy ship | Other 2-player battles: you had one ship, lost nothing; enemy had more than one and lost all | each participant | location, player, design, count | battle | P6 | BINARY-ONLY |
| 0x114 | A lone enemy ship wiped out your whole force unharmed | You had more than one ship and lost all; enemy had one ship and lost nothing | each participant | location, player, count, design | battle | P6 | BINARY-ONLY |
| 0x115 | Your single ship and the enemy force both survived; enemy losses | Other 2-player battles: you had one ship and it survived; enemy not wiped | each participant | location, player, design, count, count | battle | P6 | CONFIRMED (cb5/cb035-prevbattle) |
| 0x116 | Your force and the single enemy ship both survived; your losses | You had more than one ship and were not wiped; enemy had one ship that survived | each participant | location, player, count, design, count | battle | P6 | CONFIRMED (cb5/cb038-wm) |
| 0x12e | A single fleet undid some of the planet's terraforming by retro-bombing | Retro bombs moved at least one hab click back toward the original; the attacker has one fleet at the planet | attacker and planet owner (same id) | fleet, planet, value (clicks) | fleet (attacker); planet (owner) | P6a | CONFIRMED (tk/tk001) |
| 0x144 | A starbase you fought was destroyed and its colonists died | An Alternate Reality starbase is destroyed; sent to every other participant, whether or not it fired | every other participant | location, design, colonists | battle | P6 | CONFIRMED (cb5/cb041-sf) |
| 0x166 | Your fleets killed colonists by bombing | As 0x060 with more than one attacking fleet | attacker | fleet, planet, colonists | fleet | P6a | CONFIRMED (tk/tk005) |
| 0x167 | Your fleets destroyed one installation | As 0x061, more than one fleet | attacker | fleet, planet, count | fleet | P6a | BINARY-ONLY |
| 0x168 | Your fleets destroyed several installations | As 0x062, more than one fleet | attacker | fleet, planet, count | fleet | P6a | BINARY-ONLY |
| 0x169 | Your fleets killed colonists and destroyed one installation | As 0x063, more than one fleet | attacker | fleet, planet, colonists, count | fleet | P6a | BINARY-ONLY |
| 0x16a | Your fleets killed colonists and destroyed several installations | As 0x064, more than one fleet | attacker | fleet, planet, colonists, count | fleet | P6a | BINARY-ONLY |
| 0x16c | Your fleets destroyed one installation; defenses stopped a share | As 0x066, more than one fleet | attacker | fleet, planet, count, percent | fleet | P6a | BINARY-ONLY |
| 0x16d | Your fleets destroyed several installations; defenses stopped a share | As 0x067, more than one fleet | attacker | fleet, planet, count, percent | fleet | P6a | BINARY-ONLY |
| 0x16e | Your fleets killed colonists and one installation; defenses stopped a share | As 0x068, more than one fleet | attacker | fleet, planet, colonists, count, percent | fleet | P6a | BINARY-ONLY |
| 0x16f | Your fleets killed colonists and several installations; defenses stopped a share | As 0x069, more than one fleet | attacker | fleet, planet, colonists, count, percent | fleet | P6a | BINARY-ONLY |
| 0x170 | A player's fleets bombed your planet, killing colonists | As 0x166 | planet owner | fleet, planet, colonists | planet | P6a | CONFIRMED (tk/tk005) |
| 0x171 | A player's fleets destroyed one of your installations | As 0x167 | planet owner | fleet, planet, count | planet | P6a | BINARY-ONLY |
| 0x172 | A player's fleets destroyed several of your installations | As 0x168 | planet owner | fleet, planet, count | planet | P6a | BINARY-ONLY |
| 0x173 | A player's fleets killed your colonists and destroyed one installation | As 0x169 | planet owner | fleet, planet, colonists, count | planet | P6a | BINARY-ONLY |
| 0x174 | A player's fleets killed your colonists and destroyed several installations | As 0x16a | planet owner | fleet, planet, colonists, count | planet | P6a | BINARY-ONLY |
| 0x176 | A player's fleets destroyed one of your installations; defenses stopped a share | As 0x16c | planet owner | fleet, planet, count, percent | planet | P6a | BINARY-ONLY |
| 0x177 | A player's fleets destroyed several of your installations; defenses stopped a share | As 0x16d | planet owner | fleet, planet, count, percent | planet | P6a | BINARY-ONLY |
| 0x178 | A player's fleets killed your colonists and one installation; defenses stopped a share | As 0x16e | planet owner | fleet, planet, colonists, count, percent | planet | P6a | BINARY-ONLY |
| 0x179 | A player's fleets killed your colonists and several installations; defenses stopped a share | As 0x16f | planet owner | fleet, planet, colonists, count, percent | planet | P6a | BINARY-ONLY |
| 0x17a | Your fleets undid some terraforming by retro-bombing | As 0x12e, the attacker has more than one fleet at the planet | attacker | fleet, planet, value (clicks) | fleet | P6a | BINARY-ONLY |
| 0x17b | Another player's fleets undid some of your terraforming | As 0x17a | planet owner | fleet, planet, value (clicks) | planet | P6a | BINARY-ONLY |
| 0x17c | Your fleets killed all colonists by bombing | As 0x08f, more than one fleet | attacker | fleet, planet | fleet | P6a | CONFIRMED (tk2/tk121) |
| 0x17d | A player's fleets bombed your planet and killed all colonists | As 0x17c | planet owner | fleet, planet | planet | P6a | CONFIRMED (tk2/tk121) |
| 0x180 | Fleets left out of a crowded battle; their waypoint tasks are skipped this year | Your fleets were left out by the battle size cap; only for non-participants and multi-race participants, never in 2-player battles | owner of the left-out fleet | location | fleet (the highest-numbered left-out fleet, CB-042) | P6 | CONFIRMED (cb6/cb042: 3 races; cb5/cb039: none in 2 races); LEGACY BUG (never in 2-player battles) |

- **Order in battles.** Battle messages go out once per battle, right after the battle is fought, before bombing. Within a battle, players are handled in player order. Each player gets their battle summary, then possibly a research-boost message, then possibly 0x180.
- **Battle counts.** "Forces" count ships, plus 1 for a starbase. A side's total is its losses plus every ship it still has at that location after the battle. Inferred, not tested: this seems to also count fleets that were only watching, or that the battle size cap left out. The named enemy player in 2-player summaries could then be a bystander.
- **Exact-2 shortcuts.** The one-ship and one-stack texts (0x091–0x09a) are used only when the whole location holds exactly 2 ships or exactly 2 stacks. A bystander's fleet at the same spot pushes the battle out of these texts (inferred).
- **Precedence.** If both sides are wiped out, different texts are chosen depending on the battle type:
  - one-on-one and one-stack battles report your loss;
  - other 2-player battles report 0x09d (you won with losses);
  - multi-race battles report 0x0a5.
- **0x07e vs 0x0a8.** In multi-race battles, 0x0a8 is used only when one side lost nothing. When both sides lost part of their forces, the player gets only the generic 0x07e. Sampled 0x0a8 records fit this.
- **Alternate Reality starbase death.**
  - The planet is emptied before any message is sent.
  - The owner gets 0x08d or 0x08e, and every other participant gets 0x144.
  - Nobody gets a research boost or 0x180 from that battle.
- **LEGACY BUG (CONFIRMED) Observer test (0x0fa).** 0x0fa is sent by the same faulty observer test as the wreckage research attempt in `COMBAT.md` ("Players not in the battle", CB-031-obs, CB-037). Whether a non-participant fleet owner gets 0x0fa (and the 0x0f0 research chance) depends on that rule, which mixes up the player's number with the set of watching players. Player 1 (the first player) never gets it. Other players get it depending on which unrelated players were watching.
- **LEGACY BUG? Swapped research texts.** A planet owner whose colony watched gets the text about a fleet finding wreckage (0x0f1). A watching fleet gets the text about a battle in orbit (0x0f0), even in deep space (observed at a deep-space location).
- **LEGACY BUG (CONFIRMED) 0x180 missing in 2-player battles.**
  - The left-out-fleets message is skipped for both participants of a 2-player battle, even when the size cap left fleets out. CB-039 left 25 fleets out and sent no 0x180.
  - In the capped 3-race battle CB-042, each player with left-out fleets got 0x180 at the battle location. Each message pointed at that player's highest-numbered left-out fleet.
- **Bombing order.** Fleets bomb in fleet order. For each bombing:
  1. retro-bombing messages, attacker first, then the planet owner;
  2. the damage messages, attacker first, then the planet owner;
  3. the planet is emptied if no colonists remain.

  Nothing is sent when no installations were destroyed and no colonists were killed.
- **Single vs plural bombing text.** The plural/owner-named texts are chosen when the attacker has more than one fleet at the planet, even if only one carries bombs. The named fleet is always the one that triggered the bombing.
- **Bombing quantities.** The share of bombs stopped is trunc((1 − survive fraction) × 10000) / 100 %. The retro amount is the total number of hab clicks moved back, summed over all three axes, but shown as a percent.
- **Open question:** 0x0fa gives the location as coordinates even when the battle is at a planet. How the viewer shows that is not checked.

### Space objects and the Mystery Trader

| Id | What the player is told | Sent when | To | Slots | Focus | Phase | Status |
|---|---|---|---|---|---|---|---|
| 0x0c0 | The Mystery Trader is starting another trip across the map | Trader reaches its destination, no other trader exists, and a 1/2 roll keeps it: it stops there, warp becomes max(6, warp − 2) + 1, and it gets a new edge destination | every player | object (trader) | special: trader (inferred) | P3 movement | CONFIRMED (ob/ob023) |
| 0x0d5 | Your mass driver caught an incoming packet | Packet reaches an owned planet whose catch speed is at least the packet's speed (catch warp² ≥ packet warp², the catch warp² halved for IT owners); also when a partly caught packet does no damage (the damage rounds to 0, or the owner is AR) | target planet owner | planet, player (packet owner), kT | planet | P3 movement; P5 objects after production (packets launched this turn) | CONFIRMED (ob/ob009) |
| 0x0d6 | Your mass driver only partly caught a packet, and colonists died | Owned planet with colonists, not AR, has a catcher but the packet is faster; damage > 0; colonists killed < population; no defenses lost | target planet owner | planet, kT, player (packet owner), colonists | planet | P3 movement; P5 objects after production | CONFIRMED (ob/ob009) |
| 0x0d7 | Your mass driver only partly caught a packet; colonists and defenses were lost | As 0x0d6, but defenses were also lost | target planet owner | planet, kT, player (packet owner), colonists, count (defenses) | planet | P3 movement; P5 objects after production | BINARY-ONLY |
| 0x0d8 | A packet hit your planet and killed colonists | As 0x0d6, but the planet has no effective catcher (no driver, or IT owner with catch warp 1) | target planet owner | planet, kT, player (packet owner), colonists | planet | P3 movement; P5 objects after production | CONFIRMED (ob/ob009) |
| 0x0d9 | A packet hit your planet; colonists and defenses were lost | As 0x0d8, but defenses were also lost | target planet owner | planet, kT, player (packet owner), colonists, count (defenses) | planet | P3 movement; P5 objects after production | CONFIRMED (ob/ob009) |
| 0x0da | A packet wiped out your colony | Owned non-AR planet with colonists; damage > 0 and colonists killed = max(pop × dmg / 1000, dmg) is at least the population; the planet then becomes uninhabited | target planet owner | planet, player (packet owner) | planet | P3 movement; P5 objects after production | CONFIRMED (ob/ob009) |
| 0x108 | The trader would not trade with your fleet because it carries too few minerals | Fleet at exactly the trader's position after battles, carrying under 5,000 kT ironium + boranium + germanium, and the fleet moved this turn (a stationary fleet gets nothing) | fleet owner | fleet | fleet | P6b object encounters (trader, salvage) | CONFIRMED (ob/ob004) |
| 0x109 | The trader took your fleet and gave you tech levels, and suggests other traders | Trade where the item is research or a part you own and not every field is at the cap; you do not yet own every trader part. Levels L = min(10, 6 + (cargo − 5000)/1200), then by the sum T of your tech levels: T ≥ 108 → 1, 96–107 → 2, 84–95 → L − 3, 72–83 → L − 2, 60–71 → L − 1 | fleet owner | fleet, count (levels) | none | P6b object encounters (trader, salvage) | CONFIRMED (ob/ob004) |
| 0x10a | The trader took your fleet and gave you tech levels | As 0x109, when you already own every trader part | fleet owner | fleet, count (levels) | none | P6b object encounters (trader, salvage) | BINARY-ONLY |
| 0x10b | The trader took your fleet and gave you a new ship part | Trade happens (≥ 5,000 kT, first trade with this trader; the fleet and its cargo are consumed): the trader's item is a part you lack, or, when every tech field is at the cap (26, or 10 for some computer players, inferred), a 4-in-5 roll gives a random part you lack | fleet owner | fleet | part (the part given) | P6b object encounters (trader, salvage) | CONFIRMED (ob/ob004) |
| 0x10c | The trader took your fleet and gave you a new hull | As 0x10b, when the part given is the trader's hull | fleet owner | fleet | part (the hull) | P6b object encounters (trader, salvage) | BINARY-ONLY |
| 0x10e | The trader took your fleet and gave nothing back | Trade where the item is research or a part you already own, every tech field is at the cap, and a 1-in-5 roll fails | fleet owner | fleet | none | P6b object encounters (trader, salvage) | BINARY-ONLY |
| 0x10f | The trader took your fleet and gave you a new planetary device | As 0x10b, when the part given is the trader's planetary device | fleet owner | fleet | part (the device) | P6b object encounters (trader, salvage) | BINARY-ONLY |
| 0x118 | The trader will not trade with you again | Fleet with ≥ 5,000 kT minerals at the trader's position, and its owner has already traded with this trader | fleet owner | fleet | fleet | P6b object encounters (trader, salvage) | CONFIRMED (ob/ob004) |
| 0x12b | A Mystery Trader has appeared and is offering a trade | A trader is created: game year index ≥ 40 and random events on; chance 1/2 when year mod 100 = 71, 1/3 when = 33, 1/4 when year mod 128 = 49, otherwise 1/7 in even years and none in odd years; nothing is sent if the game has no room for another object | every player | object (trader) | special: trader (inferred) | P4c random events | CONFIRMED (kx004) |
| 0x130 | The Mystery Trader changed speed and maybe course | Trader moving before fleet movement, trader warp ≤ 12, 1-in-25 chance: warp +1, and with a further 1/3 a new destination on a random edge of the map; the trader then moves at the new warp | every player | object (trader) | special: trader (inferred) | P3 movement | CONFIRMED (WT batch, warp 8 → 9) |
| 0x131 | Your packet permanently shifted a planet's base environment | PP packet not fully caught; for each mineral (ironium → gravity, boranium → temperature, germanium → radiation, inferred from order) every 100 kT of the uncaught part has a min(kT, 100)/200 chance to terraform, and each success has a 1/10 chance to be permanent; the permanent count moves the original value toward the PP player's ideal (or toward the nearer end for an immune axis); sent when that move is not zero; owned and unowned planets | packet owner | value (raised/lowered), hab, planet, count (clicks) | planet | P3 movement; P5 objects after production | CONFIRMED (mg/mg001) |
| 0x132 | A packet permanently shifted a planet's base environment (text written for the planet owner) | As 0x131, when another player owns the planet | packet owner (see Notes) | value (raised/lowered), hab, planet, count (clicks) | planet | P3 movement; P5 objects after production | CONFIRMED (mg/mg001); LEGACY BUG (went to the packet owner; the planet owner got none) |
| 0x133 | Your packet terraformed a planet's environment | PP packet with at least one terraform success on an axis, the PP player's own terraforming tech allows improving that planet, and the change is not zero: the current value moves by the success count toward the PP player's ideal, limited by the PP player's terraform range (immune axis: half the count toward the nearer end) | packet owner | value (raised/lowered), hab, planet, value (new environment value) | planet | P3 movement; P5 objects after production | CONFIRMED (mg/mg001) |
| 0x134 | A packet terraformed a planet's environment (text written for the planet owner) | As 0x133, when another player owns the planet | packet owner (see Notes) | value (raised/lowered), hab, planet, value (new environment value) | planet | P3 movement; P5 objects after production | CONFIRMED (mg/mg001); LEGACY BUG (went to the packet owner; the planet owner got none) |
| 0x146 | A packet hit your planet but did no damage | Packet reaches an owned planet with no catcher able to slow it (no driver, or IT owner with catch warp 1), and the damage rounds to 0 or the owner is AR | target planet owner | planet, player (packet owner), kT | planet | P3 movement; P5 objects after production | BINARY-ONLY |
| 0x14f | The trader took your fleet and gave you some of its own ships | Trade whose reward is a ship (the trader's item is a ship, or no part you lack was found in 25 random tries); human players only (inferred); you have a free design slot (or an identical design) and fewer than 512 fleets. Ships: 1 (2/3) or 2 (1/3), plus Random(year/100 + 1) after year 100 (unless a game option turns it off, inferred), at most 5, then up to the same number again for the two larger designs | fleet owner | fleet, count (ships) | fleet (the new fleet) | P6b object encounters (trader, salvage) | CONFIRMED (ob/ob026) |
| 0x150 | The trader took your fleet and offered a ship reward that could not be delivered (no free design slot or fleet limit) | Ship reward with no free design slot, or 512 fleets already, or the new fleet could not be created | fleet owner | fleet | none | P6b object encounters (trader, salvage) | BINARY-ONLY |
| 0x181 | A packet hit your planet, but nobody lived there | Owned non-AR planet with no colonists, damage > 0 | target planet owner | planet, kT (holds the packet owner number, see Notes), player (always player 1, see Notes) | planet | P3 movement; P5 objects after production | CONFIRMED (mg/mg001); LEGACY BUG (the kT slot held 0, not the 1,200 kT that hit) |

- Order within one object pass: objects go by kind (minefields, packets, wormholes, trader) and then by owner and number. For each packet the PP environment messages come first (permanent then current, axis by axis), then the impact message. The trader messages 0x130/0x0c0 come after all packet messages in that pass.
- **LEGACY BUG 0x132/0x134 (CONFIRMED, MG-001-A).** The text is written for the planet's owner, but the binary sends it to the packet's owner.
  - A PP player who terraforms another player's planet gets two messages per change (0x131 + 0x132, or 0x133 + 0x134), and the planet owner gets neither.
  - MG-001-A sent a PP packet into player 1's planet. Player 0 got 0x133 + 0x134 on all three axes, and in one stream 0x131 + 0x132 as well. Player 1 got only the impact message 0x0d8.
  - The same packet into an unowned planet gave 0x133 alone (MG-001-B).
  - Observed slots, for example (1, 0, planet, 31): raised, gravity, planet, new value. The current environment went from 30/70/30 to 31/68/32.
- **LEGACY BUG 0x181 (CONFIRMED, MG-001-C).** The stored values do not match the text.
  - A 1,200 kT packet hit player 1's empty planet 23, and the slots were (23, 0, 0, 0). The amount slot held 0, not 1,200.
  - The binary reads the amount as the packet owner's number and the sender as always player 1. The packet owner here was player 0, so this run cannot tell those readings from a constant 0.
- 0x0d5 (caught) can also appear for a packet that was only partly caught when the damage rounds to 0 or the owner is AR. An IT planet with catch warp 1 counts as having no catcher for wording (0x146, 0x0d8, 0x0d9).
- When a packet hits an unowned planet, nobody gets an impact message. The PP launcher still gets 0x131/0x133.
- 0x109/0x10a report the number of level steps the trader planned, not the levels actually gained. The gift stops early once your lowest field reaches the cap, and one step can give more than one level.
- When a computer player's reward is a ship (inferred), the fleet is consumed and no message is sent.
- Each trade also deletes any pending message saying the consumed fleet had completed its orders.
- A trader whose arrival roll fails, or who arrives while another trader exists, leaves without a message.
- Open: how the consumed fleet's name is kept for display after the fleet is gone; mapping the given part to part names.

### Kinds with no sender (NEVER SENT, BINARY-ONLY)

These kinds have a text and a slot count, but nothing in the turn generator or the client sends them.

| Id | Meaning (from its parameters) | Slots |
|---|---|---|
| 0x03b | A planet's defenses were upgraded to a new defense technology | count, planet, part |
| 0x079, 0x07a | A fleet took minerals from another fleet | fleet, amount, mineral, fleet |
| 0x0af–0x0b4 | Automatic mines, factories or defenses hit the operable limit (paused) or the planet's maximum (stopped); one pair per installation | planet |
| 0x0bd | Remote terraforming at a planet has done all the fleet owner's tech allows | fleet, planet |
| 0x0fc | A planet lacks the minerals to launch any packet this year | planet |
| 0x10d | The Mystery Trader took a fleet but had nothing to teach | fleet |
| 0x112 | A planet lacks the minerals to continue its automatic builds | planet |
| 0x11a | Placeholder kind marked obsolete | planet |
| 0x11c | A transfer order involving fuel or colonists with a space object failed | fleet, object |
| 0x11d | A transfer order put fuel on a planet, which cannot store it | fleet, planet |
| 0x17f | A planet failed to launch a packet (the packet counterpart of 0x17e, which is sent) | planet |

## Evidence

- 358 rows cover all 387 kinds (some rows cover a range). 183 rows are
  CONFIRMED by at least one oracle run. The rest are BINARY-ONLY.
- The oracle records come from every corpus in apparatus `evidence/`
  (22,707 message records, including the MG batch of apparatus #32). 177
  distinct kinds appear in them, and every one has a CONFIRMED row. Each was checked against its row: slots in that
  order, sent to that player's file, and the trigger present in the run.
- The minefield facts are CONFIRMED by stars-elegy #47 and apparatus #27:
  - hit messages report damage before shields;
  - a detonating speed bump sends the "stopped" messages even to fleets
    that were not moving;
  - a player at the 512-field limit who lays mines gets 0x17e and the mines
    are lost.
- The race-penalty kinds 0x117 and 0x182 are CONFIRMED by apparatus #27
  `rd/rp12`. In a six-player game 0x182 reached all four other human
  players, and 0x117 went to a race penalized for growth 0 during a game.
- Run the decoder on any dump with `python3 tools/fleetlab/events.py
  DUMP...`.

## LEGACY BUG summary

Items marked (CONFIRMED) were seen in oracle runs; the rest are LEGACY BUG? from the binary. These kinds are sent with a recipient or slots that do not fit the
message's own meaning, or are never sent although their siblings are. Each
row above says what happens.

- **Wrong recipient:**
  - 0x132 and 0x134 go to the packet owner instead of the planet owner (CONFIRMED, MG-001).
  - 0x0f0 and 0x0f1 have their texts swapped between the two kinds of
    watcher.
- **Wrong slots:**
  - 0x0e2 and 0x0e5 name the destination gate where the origin belongs (CONFIRMED, OB-021 and MG-001).
  - 0x0e4 names a design without its owner.
  - 0x04f puts a design number in the planet slot.
  - 0x181 does not carry the packet's kT (CONFIRMED, MG-001).
  - 0x087 and 0x088 name hab axes from a different shuffle than the ones
    changed (KX-004).
  - 0x043–0x04d use colonist wording for fuel.
- **Wrong choice:**
  - 0x023 or 0x040 depends on the planet processed just before (CONFIRMED, MG-002).
  - Plural build counts (0x036, 0x038, 0x03a) are not merged (CONFIRMED for factories, MG-002).
  - 0x0fa uses an observer test that depends on player numbers (CONFIRMED as the `COMBAT.md` CB-037 rule).
  - 0x180 is never sent in 2-player battles (CONFIRMED, CB-039 and CB-042).
  - 0x13e uses a scrap text for a trader reward.
- **Never sent:**
  - 0x065, 0x06f, 0x16b and 0x175: bombing that kills only colonists has
    no "defenses stopped some bombs" variant.

## Open questions

- **Focus screens.** The special focus codes (−2 … −7) are inferred from
  the messages that use them.
- **Viewer-side rendering** of a few edge slots is not checked:
  - a missing origin planet after a fleet's own jump gate from deep space;
  - a fleet that was destroyed in the same step;
  - coordinates given for a battle at a planet.
- **Follow-up batch MG (done).** `experiments/mg` tested the private
  predictions M-1..M-10. Results are in the rows and notes above and in
  `PARITY.md` "Messages to players". Still open:
  - load-optimal fuel with a planet target (did nothing; cause not read);
  - 0x126;
  - the tie case of the last-survivor messages (0x0b8/0x0bc).
