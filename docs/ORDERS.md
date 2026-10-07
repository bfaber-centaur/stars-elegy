# Turn-order specification: how the host ingests each player's orders

Behavioral specification of the J-RC3 rules that decide what the host does
with the orders a player submits for a year: which order file it accepts,
which individual orders it applies, clamps, redirects or rejects, and what
it does for a player who submits nothing. It is written for an implementer
working only from this public repository. It describes what the host does
with an order, not how any file encodes one.

This is the ingestion stage that precedes step 1 of the turn order in
`KERNEL.md` ("players' orders are applied, one player at a time in a random
order"). `PARITY.md` holds the experiment records. Most rules here so far
come only from white-box analysis of the original program (private
`stars-decomp`, promoted here as behavior only) and are listed for oracle
testing under Open experiments.

## Status of each rule

- **CONFIRMED**: a white-box reading agrees with original-game oracle
  observations. Vectors given for it are ground truth.
- **BINARY-ONLY**: read from the original program, with no oracle
  observation yet. Treat these as predictions; they are listed under Open
  experiments.
- **LEGACY BUG**: read behavior that looks like an accident of the original
  implementation rather than a design intent. An independent implementation
  should decide whether to reproduce it; where this document recommends a
  departure, the departure is stated as a rule.

"Confirmed" covers the measured scope only; each rule says what that was.

## Scope and vocabulary

A player submits, for one year, a set of **orders**. Each order is one of a
small number of **kinds**, named here by what it does:

- *production-queue change* — the build queue of one of the player's planets;
- *planet-production flags* — a planet's routing/contribution settings
  (for example, whether leftover resources go to research);
- *design change* — add, edit or delete one of the player's ship or
  starbase designs;
- *battle-plan definition* — the player's named battle plans;
- *fleet battle-plan assignment* — which plan one fleet uses;
- *waypoint edit* — add, change or delete a waypoint (and its task) on a
  fleet;
- *cargo transfer* — load or unload minerals, fuel or colonists between a
  fleet and a planet, another fleet, or space;
- *fleet rename*;
- and housekeeping orders (relations, messages, player settings).

This document is about the host's handling of these kinds, not their
encoding. An independent implementation defines its own order format; it
should not depend on the original's.

## File acceptance

Before any order is applied, the host decides whether to accept the file at
all. The checks below act on the whole file: if the file is rejected, none
of its orders are applied, and the turn still generates for that player as
if they had submitted nothing (see "A player who submits nothing").

### Wrong game or wrong year

BINARY-ONLY.

- An order file stamped for a different game than the host's is rejected as
  not belonging to this game.
- An order file stamped for a year **earlier** than the host's current year
  is rejected as out of date.
- An order file stamped for a year **later** than the host's current year is
  ignored.
- Only a file whose year equals the host's current year is replayed.

### Registered-copy gate

CONFIRMED (measured 2026-10-07, registered host, research order, three
generations; white-box reading of the accept path agrees).

A host running as a **registered** copy accepts a player's order file only
when the file carries the registration credential the host expects. An
order file that does not carry it is **silently skipped** during generation:
its orders are not applied, and the player is **not** flagged as a cheater —
a missing credential is treated as "no usable orders", which is a separate
and later check from the anti-tamper flag.

Scope of the measurement: a structurally valid research order that changed a
registered player's research when it carried the credential left that
player's research unchanged across three consecutive generations when the
credential was absent and nothing else differed.

Implementation note: this gate is a property of the original's registered
build. An independent implementation that does not reproduce the original's
registration scheme has no equivalent of it and should accept a
well-formed, correctly addressed order file on its own terms. The credential
itself is not reproduced in this public repository.

## A player who submits nothing

BINARY-ONLY.

A non-AI player whose order file is absent, rejected or skipped keeps the
state they already had: existing waypoints and fleet tasks continue,
the production queues stand, research allocation is unchanged. No cheater or
tamper flag is set for simply not submitting. The year generates normally
for that player from their standing orders.

## Per-order validation

When a file is accepted, its orders are applied one at a time. Each order is
validated on its own; a rejected order is dropped and the rest of the file
still applies. The original's validation is **uneven** across kinds, which
matters most in multiplayer (see "Ownership" below).

### Range and legality clamps

BINARY-ONLY.

- **Research allocation.** The budget percentage is taken in `0..100`.
  A field or "next field to research" selector outside its legal set causes
  the research order to be rejected whole, leaving the previous allocation.
- **Waypoint coordinates.** A waypoint's target is clamped to the galaxy's
  legal coordinate box; a waypoint-zero (the fleet's current position) that
  is placed illegally is retargeted to a legal position. The clamp runs
  after the order is accepted, so an out-of-box waypoint is corrected, not
  rejected.
- **Design legality (tech strip).** A design that lists a component the
  player has not yet earned the tech for, or that the chosen hull does not
  allow in that slot, has that component **dropped** from the stored design
  rather than rejecting the whole design. The stored design's mass and cost
  reflect the components that survived the strip. (This is the same
  "strip parts the owner lacks" behavior noted for existing designs in
  `PARITY.md`/`ORACLE.md`.)
- **Design legality (Mystery Trader parts kept).** CONFIRMED (oracle,
  stars-elegy #45 / apparatus #21). The strip above removes only parts the
  player's **research tech** cannot reach. A part the player could only have
  obtained from the Mystery Trader is **not** stripped when the player owns
  no Mystery Trader items: the design is accepted and stored with the part
  intact, and the part functions. In the pinned oracle turn a design
  carrying Anti Matter Torpedoes was kept for a player whose Mystery-Trader
  mask was empty, and those torpedoes fired, with every hit reproduced.
  LEGACY BUG — the host recognises the unearned part while reading the
  design (it is the same part the user interface hides from that player),
  but the strip acts only on *insufficient research tech*; a part flagged
  merely "not available to this owner" passes through as long as the hull
  slot accepts its category and count. The same path keeps any component a
  design names that the owner's race or Mystery-Trader status does not
  entitle it to, not only Mystery Trader parts.

  **Chosen rule for an independent implementation.** On reading a design,
  validate every named component against what the owner has actually
  acquired — research tech, racial entitlement, and Mystery-Trader items —
  and drop (or reject) any component the owner is not entitled to, not only
  components above researched tech. Treat the original's keep-behavior as an
  isolated LEGACY BUG, reproduced (if ever wanted) behind a single named
  switch rather than in the normal design-read path. This follows the same
  "choose and state a rule" approach used for the Ownership gap above.
- **Design legality (hull not entitled, or every part stripped).**
  BINARY-ONLY. The design read checks only that the submitter owns the design
  slot; it does **not** tech- or entitlement-gate the **hull** itself, so a
  design built on a hull the owner has not earned is accepted and stored. Nor
  is a design rejected for ending up short of parts: after the per-slot strip,
  if the hull's primary slot (its engine slot) is left empty it is
  **back-filled with Quick Jump 5** (the first unrestricted engine), one per
  ship to that slot's full capacity, and any other stripped slot simply stays
  empty — the stored design is never rejected for want of parts, and the
  mass/cost reflect whatever survived plus the back-fill. The back-fill uses
  Quick Jump 5 specifically, not the engine listed before it (Settler's
  Delight), because that first engine is HE-only while Quick Jump 5 is
  available to every race.
  **Chosen rule.** Validate the hull against the owner's entitlement on design
  read and **reject** a design on an un-entitled hull, consistent with the
  component rule above (Elegy does not carry the hull gap forward). But
  **reproduce the engine-slot back-fill** rather than rejecting a design whose
  engine was stripped: the basic engine is available to every race, so the
  back-fill is legitimate repair to a buildable ship, not a trust gap.
  Confirming the hull-keep and the engine back-fill needs the OX runs.
- **Battle-plan fields.** A battle-plan definition with a tactic or primary
  target outside its legal set is rejected; a legal one is stored.

### Ownership

An order names an object (a planet, a fleet, a design). Whether the host
re-checks that the submitting player owns that object **depends on the
kind of order**:

- **Re-checked** (an order naming an object the submitter does not own is
  rejected): production-queue change, planet-production flags, design
  change, battle-plan definition.
- **Not re-checked** (the order is applied to the named object even though
  the submitter does not own it): fleet battle-plan assignment, waypoint
  edit, fleet rename, and cargo transfer (subject to the cross-owner
  redirection below).

Status: BINARY-ONLY. LEGACY BUG — the asymmetry is an artifact of the
original's per-order handling, not a stated design rule, and it is a
multiplayer trust gap: a client that submits a hand-built order can act on
another player's fleet for the kinds that are not re-checked.

**Chosen rule for an independent implementation.** Validate ownership on
**every** order kind, and reject an order that names an object the
submitting player does not own, rather than reproducing the original's
uneven trust. This is the same "choose and state a rule" approach used for
the Alternate-Reality divide-by-zero case in `KERNEL.md`: the parity record
states the original behavior; the implementation does not carry the gap
forward. This document states the rule; it does not provide a recipe for
exercising the original's gap.

**Minefield detonate-setting.** BINARY-ONLY (minefield context in
stars-elegy #50, `OBJECTS.md`). A detonate-setting order names a minefield,
and the host applies it **without** checking either that the submitter owns
that field or that the field's type is one that can detonate — a trust gap of
the same shape as the not-re-checked fleet orders above. Elegy's chosen rule,
matching what the normal client can send, accepts a detonate setting only on
the submitter's **own** minefields and only for field kinds that can
detonate. Confirming the original's open acceptance needs the OX runs.

### Cross-owner cargo

BINARY-ONLY.

A cargo transfer whose source and destination have the **same** owner is
applied in place at order time, subject to the destination's capacity.
A transfer across **different** owners is not applied in place; it is
deferred:

- **Colonists** unloaded onto a planet the giver does not own become a
  colonist-drop, resolved during the post-movement waypoint phase as
  colonisation or invasion under the rules in the takeover/objects specs,
  not credited silently to the planet.
- **Non-colonist cargo** (minerals, fuel) given to an object of a different
  owner is debited from the source when the order is applied and credited to
  the destination only after movement, with the usual "cargo given to you"
  messages (and loss when the destination is short of capacity).

An independent implementation that adopts the "validate ownership on every
order" chosen rule above still needs the legitimate cross-owner paths —
colonist invasion/colonisation and deliberate cargo gifts — because those
are reached through the owner's own fleet acting on a foreign target, which
is legal. The chosen rule rejects orders that act **on a foreign object the
submitter is pretending to own**, not a fleet owner's legal action against a
foreign target.

## Conflicts between players

BINARY-ONLY.

Players' order files are replayed one player at a time in a **random player
order** each year (`KERNEL.md`, turn order step 1). When two players submit
orders that act on the same object in the same year, the later-replayed
order wins. The replay order is drawn from the game's generator, so the
outcome of a same-year conflict is not fixed; it depends on the draw.
Tests of conflict resolution should pin the generator (`ORACLE.md`).

## Fleet operations

How much moves when a player loads or unloads cargo, merges or splits
fleets, or transfers cargo between two of their own fleets, and when in the
turn it happens. Amounts are integer. Unload and colonist-drop **amounts**
onto planets are specified in `TAKEOVER.md`; this section covers the fleet
side and the clamps, and does not duplicate them.

### Cargo amounts and clamps

CONFIRMED (FO-01..07).

A fleet holds four cargo kinds — three minerals and colonists — in one cargo
hold, and fuel in a separate tank. Every load, unload or transfer clamps the
amount moved:

- **Taking from a hold** moves at most what the hold contains; a hold never
  goes negative.
- **Putting into a fleet** moves at most the destination's free space:
  minerals and colonists against the free **cargo hold**, fuel against the
  free **fuel tank**. The two capacities are independent — a full cargo hold
  does not stop a fuel transfer, and vice versa.
- A transfer is therefore the minimum of what the source has, what the order
  asks, and the destination's free capacity; any shortfall simply stays at
  the source.

Colonists load subject to a fleet condition the host checks (not every hull
can carry them); the exact condition is read but not yet pinned, so an
implementation should treat "this fleet may carry colonists" as a property of
the fleet rather than assume every fleet qualifies.

### Transfer between the player's own fleets

A direct cargo transfer between two of the submitting player's fleets at the
same location applies at order time and is **owner-checked**: both fleets
must belong to the submitter, or the transfer is refused (CONFIRMED,
FO-01..07, which exercised the transfer-fleet task and its refusals). When
it applies, the two fleets' cargo of each kind and their fuel are pooled and
shared out **in proportion to each fleet's capacity**, so nothing is lost
while the combined capacity holds; accumulated ship damage is likewise shared
across the combined ships (BINARY-ONLY — the balancing split itself is read
from the program, not separately measured). Giving cargo to another player's
fleet is the deferred cross-owner path above, not this operation.

### Merge

A merge combines fleets at one location that all belong to the submitter;
the surviving fleet keeps its id. Ships **add together per design**, and the
emptied fleets are removed. There are two ways to order a merge, and they do
**not** behave the same at the limits.

**Merge order** (a direct "merge these fleets now" order). A per-design stack
is summed into a signed 16-bit count, one source fleet at a time, with the
emptied source fleets removed. The boundary, stated exactly:

- a resulting stack of **32766** is kept as 32766;
- a resulting stack of **32767** is kept as 32767 — this is the largest count
  the order can store, not 32766;
- a stack that would reach **32768 or more** is slammed to **32766**, and the
  excess ships are **lost** (not spilled back into a source fleet, and the
  order is not refused). The clamp is applied after each addition, so once a
  running total passes 32767 it becomes 32766 and any further source fleets
  merged into the same slot re-trigger it.

Elegy's chosen clamp reproduces this exactly: keep counts up to 32767, and a
stack that would exceed 32767 becomes 32766 with the remainder dropped. This
path is otherwise BINARY-ONLY — read from the program, not yet oracle-tested.

This path also combines damage by its **own** routine, not the one the
Merge-with-Fleet task uses, and the two do not agree on magnitude. The
**percentage** combines the same way — a damaged stack merged into healthy
ships of the same design has its percent spread over the full post-merge
count, `ceil(100·ΣD/n)` with `D` the damaged-ship count per stack and `n` the
slot total. But the per-ship **damage units** are averaged over the
**damaged** ships only (`Σ(D·units)/ΣD`), not over all `n`, so the merge order
keeps a higher per-ship figure than the task's dilution: for the task's own
example (10 ships at 100 units/50% + 10 at 200 units/20%) both give 35%, but
the merge order yields ~129 units/ship where the task gives 45. An
implementation should therefore not assume ORDERS.md's single damage rule
(stated for the task) holds verbatim here. BINARY-ONLY — this whole path is
read from the program but not yet oracle-tested.

**Merge-with-Fleet waypoint task** (CONFIRMED, FO-01..07). The ordering fleet
joins a target fleet on arrival; ship counts add per design and cargo and
fuel add into the survivor. Two edges differ from the merge order and are
LEGACY BUGs an implementation should isolate so it can switch them off:

- **No ship-count cap.** This path does not apply the 32766 limit. A
  per-design stack reaching 32767 is kept, but a stack pushed to 32768 or
  beyond **overflows and leaves the merged fleet with no ships at all**,
  while its cargo and fuel stay behind (so the minerals/fuel survive in a
  ship-less fleet). CONFIRMED (FO: 32000+767 → 32767; 32000+768 and
  32000+1000 → no ships). LEGACY BUG (a signed 16-bit ship count with no
  clamp on this path).
- **Damage dilution.** Per design slot, with `D = max(1, pct·count/100)`
  damaged ships in each damaged stack and `n` ships in the slot after the
  merge, the merged percentage is `ceil(100·ΣD/n)`. If only one of the two
  stacks was damaged, its damage **units are kept**; if both were, the units
  become `ceil(Σ(D·units)/n)` — divided by **all** ships of the slot, not by
  the damaged ones, which dilutes the damage. CONFIRMED over seven cases
  (FO; e.g. 10 ships at 100 units/50% merged with 10 at 200 units/20% gave
  45 units at 35%). LEGACY BUG (merging a damaged stack into healthy ships of
  the same design reduces the recorded damage).

A Merge-with-Fleet task acts only on a **co-located** target: a task whose
waypoint-0 target fleet is elsewhere is refused and the task is cleared, with
both fleets unchanged (CONFIRMED, FO — a target 195 ly away did nothing). The
normal game only ever creates this task against a fleet the ordering fleet is
travelling to meet, so in normal play the merge happens on arrival.

The task also validates the target before merging (BINARY-ONLY): it resolves
the target fleet by id and merges only when that fleet still exists, is not a
fleet that has **already merged away** earlier in the same replay, and belongs
to the **same owner**. A target that is gone or already merged produces a
"cannot merge" message and no change; a target owned by **another player**
produces a different "not your fleet" message and no change. There is no
distance test in this check — co-location is enforced only by the task firing
on arrival (above). So an implementation that refuses a foreign-owner or
already-merged target, exactly as Elegy does, matches the original; confirming
the precise messages needs the OX runs.

### Split

BINARY-ONLY.

A split creates a new fleet from part of an existing one. The new fleet
carries exactly the ships named in the order, and **inherits the source
fleet's battle plan and its full waypoint list** (so the detached ships keep
following the same orders until changed). The source's cargo and fuel are
then divided between the two fleets in proportion to capacity. "Split all"
is the same operation taken to the limit: one new single-ship fleet per ship.

### Turn placement

CONFIRMED (FO-01..07) for the direct order-time operations; BINARY-ONLY for
the merge order's placement.

Loads and unloads ordered directly, transfers, merges and splits apply while
each player's orders are replayed, before any movement (`KERNEL.md`, turn
order step 1). The Merge-with-Fleet, load and unload **tasks attached to
waypoints** are distinct: they run at the pre-movement and post-movement
waypoint phases (`KERNEL.md`, steps 2 and 6), on arrival at the waypoint, and
the load/unload planet-side amounts are in `TAKEOVER.md`. Cross-owner cargo
given at order time is deferred to those later phases as described under
Cross-owner cargo.

## Waypoint upkeep and the remaining tasks

After movement each turn the host walks every fleet's waypoint list and
tidies it, then runs the tasks that were not covered above (route, patrol,
transfer fleet). This is distinct from the order-time edits: it works on a
fleet's own stored waypoints and state, so every behavior here can be set up
by editing the host state (fleetlab HST editing) and reading the next turn —
none of it needs a crafted order file or the registered serial. Status
BINARY-ONLY throughout (read from the program, not yet measured), unless a
line says otherwise.

### Reaching a waypoint

When a fleet arrives at its next waypoint (its position equals waypoint 1),
that waypoint is consumed, and how depends on the fleet's **repeat-orders**
flag:

- **Repeat off:** the reached waypoint is dropped — the list shortens by one
  and the fleet goes on to what was the next waypoint.
- **Repeat on:** the reached waypoint is instead moved to the **end** of the
  list, so the fleet cycles through its waypoints indefinitely. Two cases
  fall back to a plain drop even with repeat on: a list of only two
  waypoints, and a reached waypoint whose position already equals the current
  last waypoint (no duplicate is appended).
- A **patrol** waypoint never repeats, even with repeat orders on.
- When a fleet reaches its **last** waypoint with no continuing task and no
  planet route to follow, it goes idle and its owner is messaged that the
  orders are complete.

### Targets that moved, died or were captured

A waypoint can name a fleet as its target instead of fixed coordinates. Each
upkeep pass re-resolves that target:

- **Target still exists:** the waypoint's coordinates are refreshed to the
  target's current position, so a fleet ordered to meet a moving fleet keeps
  chasing it. Only a position; the target's owner is not re-checked, so a
  waypoint keeps tracking a target fleet even if it has changed hands
  (been captured). An exception bit on the waypoint suppresses the refresh
  (the waypoint then holds its coordinates).
- **Target gone (destroyed, or no longer a fleet):** the target is cleared
  and the waypoint becomes a plain go-to-coordinates waypoint at the
  last-known position; the fleet still travels there and then treats it as an
  ordinary reached waypoint. The order is not dropped outright.

### Route task

A fleet that reaches a planet while carrying the **route** task, where the
planet belongs to the fleet's owner and has a route destination set, is
automatically sent on to that destination (a fresh two-waypoint order):

- the warp is the **ideal warp** for the distance, then reduced step by step
  if the fleet lacks the fuel to sustain it;
- if both the source and destination planets have a **stargate**, the fleet
  carries no cargo, and the gate can move the fleet's heaviest hull over the
  distance with no loss, the fleet is sent through the stargate instead
  (warp set to the gate code).

This chains across hops: each arrival re-routes. A planet with no route set,
or not owned by the fleet, leaves the fleet idle rather than re-routing.

### Patrol task

Patrol sets a fleet to watch for enemy fleets within a stored **range** and
move to intercept one. It never repeats (above). The rule for **which**
in-range enemy a patrolling fleet intercepts, and the warp it uses, is read
but not yet pinned down — this is the one item in this section that most
needs a direct measurement, not a chosen rule.

### Transfer fleet (give a whole fleet to another player)

The transfer-fleet task hands the entire fleet to a named recipient. The host
refuses it in three cases; an implementation that validates the gift up front
reproduces the original:

- **Recipient is not a real, active player** — an empty or eliminated slot,
  or a **computer player**. A computer player never receives a gifted fleet.
  Refused, with a message to the giver.
- **Recipient treats the giver as an enemy.** If the recipient's relation
  toward the giver is "enemy" (or the recipient otherwise declines gifts),
  the transfer is refused.
- **The fleet carries colonists.** A colonist-carrying fleet cannot be
  gifted; the transfer is refused.

Otherwise the fleet changes owner. (The computer-player and
treated-as-enemy refusals are the two the coverage audit flagged as
missing; the colonist refusal was already read.)

### Oracle plan

Every item above is reachable with **fleetlab HST editing** — set a fleet's
waypoint list and its repeat-orders flag, point a waypoint at another fleet
and then destroy or move that fleet, set a planet's route destination, set a
patrol range with enemy fleets at chosen distances, set player relations, or
include a computer player — then run one host turn and read the result. None
of it needs the serial-gated OX order files, so this whole section can be
measured now. The matching predictions are under Open experiments
(**WU** prefix) below.

## Open experiments

These rules are read from the original program and not yet measured in the
original game. Each is a numbered prediction with the discriminating
observation that would confirm it; the proposed oracle corpus prefix is
**OX** (orders).

The fleet-operation clamps, turn placement, the transfer-fleet owner check
and the Merge-with-Fleet task (including its damage dilution and the missing
ship-count cap) have since been measured — see the Fleet operations section
and `PARITY.md`, "Fleet Operations" (FO-01..07). Still open there:

- **OX merge-order cap and loss.** The direct merge order's 32766 per-design
  cap is read but untested (only the waypoint task was measured, and it has no
  cap); push a direct merge past 32766 and confirm the stack caps at 32766
  with the excess lost (not spilled, not refused). Confirms "Merge order".
- **OX merge-order damage.** Merge (direct order) a damaged stack into healthy
  ships of the same design and read back the stored percent and per-ship
  damage units; confirm the percent dilutes over the full count like the task
  but the units divide by the damaged count, not the slot total (so the figure
  differs from the task path). Confirms the merge-order damage note.
- **OX merge-target validation.** With the Merge-with-Fleet task, aim it at a
  co-located fleet owned by another player, and at a fleet that has already
  merged away the same turn; confirm each is refused with no change. Confirms
  the merge-target note.
- **OX design hull/parts.** Submit a design on a hull above the player's tech,
  and one whose engine is stripped; confirm the original stores both (hull
  kept, engine slot back-filled with Quick Jump 5 to capacity) rather than
  rejecting. Confirms "Design legality (hull not entitled, or every part
  stripped)".
- **OX minefield detonate.** Submit a detonate-setting order naming another
  player's minefield, and one naming a field kind that cannot detonate;
  confirm the original accepts both. Confirms "Minefield detonate-setting".
  Keep the crafted inputs in private apparatus.
- **OX split.** Split some ships off a loaded fleet; confirm the new fleet
  has exactly the ordered ships, a capacity-proportional share of the cargo,
  and the source's battle plan and waypoints. Confirms "Split".

The waypoint-upkeep predictions (**WU** prefix) all use **fleetlab HST
editing**, not crafted order files, so none needs the registered serial:

- **WU repeat vs drop.** Give a fleet three waypoints and run it onto the
  second, once with the repeat-orders flag off and once on; confirm the
  reached waypoint is dropped in the first case and moved to the end of the
  list in the second. Confirms "Reaching a waypoint".
- **WU repeat fallbacks.** Repeat case with only two waypoints, and with a
  reached waypoint equal to the last; confirm both fall back to a plain drop.
- **WU patrol no-repeat.** Repeat flag on, a patrol waypoint reached; confirm
  it is not rotated to the end.
- **WU dead target.** Point a waypoint at another fleet, destroy that fleet,
  and run a turn; confirm the waypoint keeps its last-known coordinates, loses
  its target, and is not dropped. Confirms "Targets that moved, died or were
  captured".
- **WU live target.** Point a waypoint at a moving fleet; confirm the
  waypoint's coordinates track the target's new position each turn.
- **WU route task.** Set a planet's route destination and send an owned fleet
  in on the route task; confirm it is re-dispatched to the destination at the
  ideal warp (reduced for fuel), and that an empty fleet between two gated
  planets is sent through the stargate. Confirms "Route task".
- **WU patrol target.** Set a patrol range with enemy fleets at chosen
  distances and strengths; observe which one the fleet intercepts and at what
  warp. This is the measurement that pins the patrol target rule.
- **WU transfer refusals.** Order a fleet gifted to: a computer player, a
  player who treats the giver as an enemy, and (carrying colonists) a willing
  ally; confirm each is refused, and that an empty fleet to a willing
  non-enemy human transfers. Confirms "Transfer fleet".

The order-ingestion predictions remain open:

- **OX file-acceptance.** Build order files one year below and one year above
  the host year, and with a mismatched game stamp; confirm the orders are
  dropped (out of date / later-year ignored / wrong game) while the turn
  still generates. Confirms "Wrong game or wrong year".
- **OX missing-turn.** Generate with a non-AI player's order file absent;
  confirm waypoints, queues and research are unchanged and no flag is set.
  Confirms "A player who submits nothing".
- **OX research-range.** Submit a research allocation above 100% (and an
  illegal field selector); confirm it is rejected and the previous
  allocation stands, while a `0..100` allocation applies verbatim. Confirms
  "Research allocation".
- **OX waypoint-clamp.** Add a waypoint outside the galaxy box to a fleet;
  confirm it is accepted and clamped to the legal box rather than rejected.
  Confirms "Waypoint coordinates".
- **OX design-strip.** Submit a design carrying a component above the
  player's tech; confirm the stored design has that component dropped and its
  mass/cost reflect the survivors. Confirms "Design legality".
- **OX battle-plan-range.** Submit a battle plan with an out-of-range tactic;
  confirm it is rejected and a legal plan is stored. Confirms "Battle-plan
  fields".
- **OX ownership.** For each not-re-checked kind, have one player submit an
  order naming another player's object; confirm the original applies it
  (and, for cargo, applies the cross-owner redirection). Confirms
  "Ownership" and "Cross-owner cargo". Keep the crafted inputs for this item
  in private apparatus.
- **OX conflict.** Pin the generator, submit two players' conflicting orders
  on one object, and vary only the generator seed; confirm which player's
  order wins tracks the replay permutation. Confirms "Conflicts between
  players".
