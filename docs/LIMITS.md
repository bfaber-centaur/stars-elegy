# Hard limits

Every fixed capacity the host or the client enforces that an
implementation has to reproduce: its value, what happens when it is hit,
and its evidence. Where an owning spec already states a limit, this file
only points there. The production-queue replace and setting-order rules
(sections "Production-queue replace" and "Setting orders") are not written
anywhere else yet; they are meant to move into `ORDERS.md`.

## Status of each rule

Tags as elsewhere: CONFIRMED (predicted, then held in oracle runs),
MEASURED (observed, not predicted), BINARY-ONLY (read from the original,
not run), LEGACY BUG, UNKNOWN. "Serial-gated" means the case needs an order
the original client cannot produce, and waits on the crafted-order decision.

What happens at a limit is one of:

- **refused**: the action does not happen and the player gets a message;
- **dropped**: the action does not happen, with no message;
- **clipped**: the action happens up to the limit;
- **wraps** / **corrupt**: the original misbehaves (a LEGACY BUG; Elegy
  picks a rule).

## Players and universe

| Limit | Value | At the limit | Tag | Where |
|---|---|---|---|---|
| Players per game | 1–16 (the wizard offers 2–16) | — | CONFIRMED (UG01–UG21) | `UNIVERSE.md` "Settings that shape a new game" |
| Planets per universe | at most 999 | the count is capped | CONFIRMED (UG01–UG21) | `UNIVERSE.md` "Count" |
| Galaxy box | `1000 .. 1000 + (size+1)·400` ly on each axis | waypoints are clamped into the box | CONFIRMED (size, UG01–UG21); clamp BINARY-ONLY | `UNIVERSE.md` "Conventions"; `ORDERS.md` "Range and legality clamps" |
| Wormhole pairs | by size, 0–8 | — | CONFIRMED (OB-006) | `OBJECTS.md` "Creation" |
| Seed | only the low 12 bits matter | — | CONFIRMED (UG11, UG14) | `UNIVERSE.md` "Randomness and seeds" |

## Designs and battle plans

| Limit | Value | At the limit | Tag | Where |
|---|---|---|---|---|
| Ship designs | 16 slots per player (0–15) | the client offers no 17th slot. A Mystery Trader ship gift or fleet gift with no free or matching slot gives no ship (messages 0x14a, 0x14b, 0x150). A design order naming a slot past 25 is refused | MEASURED (gift with all 16 used, OB-026); slot count BINARY-ONLY | `MESSAGES.md`; `OBJECTS.md` "Encounters" |
| Starbase designs | 10 slots per player (orders number them 16–25 after the ship slots) | a design order naming a slot past the last is refused | BINARY-ONLY | |
| Names | see "Names" below | | | |
| Parts per hull slot | the hull slot's maximum | extra parts are stripped from the stored design | CONFIRMED (strip, SC-021) | `ORDERS.md` "Range and legality clamps" |
| Battle plans | host 16, client 15 | stated there | MEASURED (client, BP-L in the BP-1..BP-2 runs); host BINARY-ONLY, serial-gated | `COMBAT.md` "Battle plans" |
| Battle-plan fields | tactic and targets one past the legal sets are stored; anything higher is refused | stated there | BINARY-ONLY | `COMBAT.md` "Battle plans"; `ORDERS.md` "Range and legality clamps" |

## Fleets, ships and waypoints

| Limit | Value | At the limit | Tag | Where |
|---|---|---|---|---|
| Fleets per player | 512 | built ships join a fleet at the planet, or are lost | CONFIRMED (SL-08..SL-10) | the production-launch spec, "The 512-fleet limit" (open PR) |
| Fleets made by a split order | no check in the host; the client refuses a split at 512 | a crafted split past 512 would spill into the owner bits | BINARY-ONLY, serial-gated | |
| Design stacks per fleet | 16 (one per design slot) | — | BINARY-ONLY | |
| Ships per stack | 32,767 | the Merge-with-Fleet task has no cap and a total of 32,768 or more leaves no ships (LEGACY BUG); the merge order keeps 32,767 and turns more into 32,766 | CONFIRMED (task, FO-01..FO-07); order BINARY-ONLY | `ORDERS.md` "Merge" |
| Ships moved between own fleets | destination stack at most 32,765 | clipped | BINARY-ONLY | `ORDERS.md` "Transfer between the player's own fleets" |
| Fleet-following passes | 8 | — | BINARY-ONLY | `KERNEL.md` turn order (open PR) |
| Movement chase rounds | 10 | — | CONFIRMED (FM-001..003) | `KERNEL.md` "Chasing another fleet" |
| Waypoints per fleet | **UNKNOWN.** The host checks only that a new waypoint's index is at most the current count; its count is a byte | — | UNKNOWN | |
| Waypoint task | 0–9 | a larger task is refused | BINARY-ONLY | |
| Fleet name | the design name cut to 28 characters plus " #n" | client display | BINARY-ONLY | the production-launch spec, "Fleet names" (open PR) |

## Space objects

Minefields, packets, salvage, wormholes and the Mystery Trader share one
object table.

| Limit | Value | At the limit | Tag | Where |
|---|---|---|---|---|
| Objects in the universe | 4,050 | no new object. Mine laying: the mines are lost, message 0x17e. A finished packet: lost, its cost spent, message 0x129 (reused text). Mystery Trader: not spawned, no message. Salvage, wormholes: UNKNOWN | BINARY-ONLY (not run) | `OBJECTS.md` "Laying" (minefields) |
| Numbers per object type and owner | 512, or 511 once any object sorts after that owner's run (LEGACY BUG) | as above | MEASURED (minefields, MF-11, MF-13); packets and salvage BINARY-ONLY | `OBJECTS.md` "Laying" |
| Mines in one field | a field holding more than 999,999 takes no more; a new field starts | — | CONFIRMED (MF-10) | `OBJECTS.md` "Laying" |
| Packet contents | 32,760 kT per mineral | clipped | BINARY-ONLY | `OBJECTS.md` "Launch" |
| Salvage object | 30,000 kT | the overflow becomes a new salvage object at the same spot | CONFIRMED (CB-040) | `COMBAT.md` "Salvage" |
| Stargate | 5× range or 5× either mass limit | refused (0x0e4) | CONFIRMED (OB-021, OB-022) | `OBJECTS.md` "Stargates" |

## Production queue

| Limit | Value | At the limit | Tag | Where |
|---|---|---|---|---|
| Items in a queue (client) | 40 | the Production dialog refuses a 41st item (it beeps; the queue is unchanged) | CONFIRMED (LQ-6) | this file |
| Items in a queue (host) | 255, from the order-record size; no other check | 254 or more would wrap the stored capacity | BINARY-ONLY, serial-gated | this file |
| Count per item (client) | 1020 | adding to an item clips its count at 1020 | CONFIRMED (LQ-5b) | this file |
| Mines, factories queued (client) | the planet's maximum minus what is installed, at most 1020, summed over the whole queue | each Add takes no more than what is left; the item leaves the buildable list at 0 | MEASURED (LQ-5: 1010 factories accepted with 10 already queued) | this file |
| Defenses queued (client) | the planet's maximum defenses minus those installed, summed over the queue | as above | BINARY-ONLY | `KERNEL.md` "Caps" |
| Auto Alchemy count (client) | 1 | the client holds it at 1; production ignores the count | CONFIRMED (LQ-5b); production CONFIRMED | `KERNEL.md` "Production" |
| Count per item (host) | 1023 (the stored field) | — | BINARY-ONLY | |
| New-colony default queue | 12 items | a longer template order is refused | BINARY-ONLY | |
| Installations ordered | the planet's cap | clipped, message 0x12a | CONFIRMED (PQ-001 C10) | `KERNEL.md` "Caps" |
| Starbase dock | not checked by the host (LEGACY BUG) | — | CONFIRMED (SL-12) | the production-launch and turn-order specs (open PRs) |
| Planetary scanner | one per planet | a second one is removed from the queue, message 0xb9 | BINARY-ONLY | |
| Completion estimate | 99 years | the client shows "never" beyond | BINARY-ONLY | `ESTIMATES.md` |

## Planets and research

| Limit | Value | Tag | Where |
|---|---|---|---|
| Installations stored | 4,095 each | BINARY-ONLY | |
| Maximum and operable installations | formulas, including defenses at most 100 | CONFIRMED (KB-1A) | `KERNEL.md` "Caps" |
| Effective population | 2 × maximum | CONFIRMED (KB-1A) | `KERNEL.md` "Resources per planet" |
| Hostile habitability | −15 per axis | CONFIRMED (KX-002 H5) | `KERNEL.md` "Hostile planets" |
| Environment | 1–99 | BINARY-ONLY | `KERNEL.md` "Planetary climate change" |
| Remote mining | 4,000 kT per fleet | CONFIRMED (KB-1A) | `KERNEL.md` "Mining" (remote mining: open PR) |
| Tech level | 26 per field; research into a field at 26 is lost | CONFIRMED (KX-002 R6) | `KERNEL.md` "Allocation" |
| Research budget | 0–100% | BINARY-ONLY | "Setting orders" below |

## Combat

| Limit | Value | Tag | Where |
|---|---|---|---|
| Battles per location | 1 per year | CONFIRMED (CB-000..CB-008) | `COMBAT.md` |
| Tokens per battle | 255, shared per player as `255/n` | CONFIRMED (CB-039) | `COMBAT.md` "Battle plans" token cap |
| Rounds | 16 | CONFIRMED (CB-000..CB-008) | `COMBAT.md` "Rounds" |
| Initiative 63, capacitors 255%, jammers 95% | clipped | CONFIRMED (CB-000..CB-008) | `COMBAT.md` "Token values" |
| Battle-log size | fixed buffer; size UNKNOWN | UNKNOWN | |

## Messages and order files

| Limit | Value | At the limit | Tag | Where |
|---|---|---|---|---|
| Player messages per year | one buffer of about 64 KB shared by all players | later messages that year are dropped | BINARY-ONLY | `MESSAGES.md` "How messages work" |
| Order record | 1,023 bytes | — | BINARY-ONLY | |
| Cross-owner colonist drops, cross-owner transfers | 1,000 each per year | behaviour when full UNKNOWN | BINARY-ONLY (size) | `ORDERS.md` "Cross-owner cargo" |
| Race settings | ranges and repairs | clipped each year | CONFIRMED (RD-P5..RD-P7) | the races spec, "Race settings" (open PR) |

## Names

BINARY-ONLY except where marked.

- **Characters.** A stored name is a byte string. The file encoding
  packs common characters in one nibble and escapes any other byte, so
  every single-byte character can be stored (the encoding is DOCUMENTED
  by StarsAPI). The client takes whatever its text box accepts.
- **Fleet names.** The client's Rename box takes at most 31 characters,
  and it also cuts the text to what fits in 160 pixels of its font, so a
  name of wide characters is shorter. An empty rename removes the custom
  name, and the fleet shows its default name again (the primary design's
  name cut to 28 characters plus " #n"). The host does not check the
  length beyond the order record's size.
- **Battle-plan names.** The client's name box (Copy and Rename) takes at
  most 31 characters; a plan stores 32 bytes with the terminator. The
  name dialog itself does not check for an empty name.
- **Design names.** The host refuses a design order whose name is longer
  than 32 characters. The ship designer's own limit is UNKNOWN.
- **Game name.** 31 characters (from the game definition).

**Chosen rule for an independent implementation.** Fleet, battle-plan and
design names are at most 31 characters of any single-byte text; an empty
fleet name restores the default name. The 160-pixel cut is client
presentation, not game state.

## Production-queue replace

The client sends a planet's **whole new queue** as one order whenever the
player changes it (OK in the Production dialog). The host:

1. Refuses the order unless the planet belongs to the sender.
2. With an empty list, removes the planet's queue. The planet then has no
   queue: all of its resources go to research, with the empty-queue message
   (0x3f) that year (CONFIRMED, LQ-4).
3. Otherwise replaces the old queue with the new list in the order given.
   Old items that are not in the new list are gone, with what was spent on
   them. Counts are taken as sent.
4. Keeps a submitted progress percentage only if the old queue had an item
   with progress to match it. For each new item with a nonzero percentage,
   in queue order, it looks for the first old item that has nonzero progress,
   the same item and the same kind (planetary item or design). The count is
   not compared.
   - Found: the new item keeps **the percentage the client sent**, and that
     old item cannot be matched again.
   - Not found: the new item's percentage becomes 0.

So progress follows an item when it is moved, or when its count changes
(CONFIRMED, LQ-1, LQ-5b, LQ-6). An item removed and added again starts from 0, because
the client sends the new one with 0% (CONFIRMED, LQ-2). Two items of the
same kind keep progress only as far as the old queue had partial ones
(CONFIRMED, LQ-3).

The host does not check that the submitted percentage equals the old one.
A crafted order could raise it (BINARY-ONLY, serial-gated). Item ids,
counts and the starbase dock are not checked here either; production
checks some of them later.

The client's Production dialog builds that list. Add inserts the chosen
item after the selected row, or adds to the count of the selected row or
the row after it when that row is the same item (MEASURED, LQ-5b, LQ-7);
Remove takes from the selected row and drops it at 0 (LQ-2). Click amounts
are 1, 10 (shift), 100 (ctrl) and, read from the client, 1020 (ctrl+shift), each clipped by the
limits in "Production queue" above.

**Chosen rule for an independent implementation.** A submitted item with a
nonzero percentage keeps it only if the old queue has an item not yet
matched with the same item id, the same kind and **exactly that
percentage**; that old item is then used up. Otherwise the percentage
becomes 0. Items are taken in queue order, as above.

A legal client only sends percentages it read from the planet's current
queue (an item it kept or moved, or one whose count it changed or merged
into) and sends new items at 0. So every percentage it sends has its own
old item, and this rule gives the original's result for every such queue:
LQ-1, LQ-2 (the 20% Factory pairs with the old 20%, not the removed 49%),
LQ-4, LQ-5b, LQ-6 and LQ-7. It never creates progress. It differs from
the original only when the sent percentage is not in the old queue, which
a legal client cannot produce: LQ-3 edited the host file so the client
showed 49% where the host held 20%. The original kept 49%; the chosen rule
gives 0.

## Setting orders

All BINARY-ONLY except where marked. The client writes each of these when
the player changes the setting.

- **Research** (field, budget, next field). The budget is 0–100%. The
  current field is one of the six; "next field" is one of the six, "same
  field" or "lowest field". The client-driven case applied all three and
  spent the year's research on the new field (MEASURED, PQ-1). A budget
  outside 0–100 or a field outside its set makes the host refuse the order,
  but the budget has already been stored by then (serial-gated). Separately,
  a budget outside 0–100 found at the start of a year becomes 15%.
- **Planet settings**: "contribute only leftover resources to research",
  the mass driver's destination and packet warp, and the route destination
  for new ships. The host checks that the planet belongs to the sender, not
  that a destination exists.
- **Relations**: only the sender's own relation row changes.
- **Battle plans**: `COMBAT.md` "Battle plans".
- **No owner check**: assigning a fleet's battle plan, renaming a fleet,
  setting a minefield's detonate flag and the repeat-orders flag act on the
  named object whoever owns it (LEGACY BUG; `ORDERS.md` "Ownership" has the
  chosen rule: check ownership on every order).
- **Applied only during turn generation**: the new-colony default queue and
  one player setting of unknown meaning.

## What "refused" means for a whole order file

`ORDERS.md` says a refused order is dropped and the rest of the file still
applies. The original's turn loop keeps applying the remaining orders but
then reports the file as failed, and turn generation stops with an alert
(BINARY-ONLY). If that holds, a refused order means the year is not
generated at all. No client action produces a refused order, so this is
serial-gated. Elegy's chosen rule stays as `ORDERS.md` states it: drop the
order and apply the rest.

## LQ: production-queue edits through the client (CONFIRMED except LQ-5, LQ-7 MEASURED)

Combat Lab, planet 17 (player 0's homeworld), research budget 100% so that
production barely moves the queue. One pinned year (cycles 20000) made the
base: Factory ×5 at 49%, Mine ×5 at 30%, Defenses ×5, Factory ×5 at 20%,
Armed Probe ×3 at 50%. Each case is one client session
(`tools/fleetlab/client-orders`) and one pinned year. Predictions were
committed before each batch (LQ-5b and LQ-7 after LQ-5). Raw files: apparatus `evidence/lq/` (private).

| Case | Client action | Predicted | Observed |
|---|---|---|---|
| LQ-0 | none (control) | queue unchanged | unchanged |
| LQ-1 | Armed Probe to the top; Mine −2 | the same percentages in the new order | order as predicted; after the year Probe 53% (+3 from production), Factory 49, Mine ×3 at 30, Factory 20 |
| LQ-2 | remove the 49% Factory; add Factory ×5 at the top | the new Factory at 0; the other Factory keeps 20 | sent at 0; after the year 9% (production), the other Factory 20 |
| LQ-3 | host file edited first to Factory ×9 at 0, Mine 0, Factory ×9 at 20, Probe 0; the client (still showing 49/30/20/50) takes one Defenses off | Factory 49 kept (matched by the old 20%, count ignored); Mine, second Factory and Probe 0 | exactly that |
| LQ-4 | Clear | no queue; message 0x3f | no queue; 0x3f |
| LQ-5 | Factory ×1100 after Mine; then two adds by row | Factory ×1020 | MISSED: Factory ×1010, and Factory left the buildable list, so the next two row clicks picked the item below the intended one. 10 factories were already queued: the client limits the factories in the whole queue to 1020 (read: the planet's maximum less those installed, at most 1020) |
| LQ-5b | Armed Probe ×1100 after Mine; Auto Alchemy ×5 at the top; Mine ×3 with Mine selected | Probe ×1020; Auto Alchemy ×1; Mine ×8 at 30 | exactly that |
| LQ-6 | 40-item queue: remove one, add Defenses (40), try Mineral Alchemy (41st) | the 41st refused | 40 items, no Mineral Alchemy; the dialog showed it selected and the queue unchanged |
| LQ-7 | Factory ×8 with Top selected (the next row is Factory ×5 at 49) | a new Factory ×8 item | MISSED: merged into the next row, Factory ×13 at 49 |
