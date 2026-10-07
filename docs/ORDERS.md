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
validated on its own. The original's validation is **uneven** across kinds,
which matters most in multiplayer (see "Ownership" below).

**Chosen rule (Elegy):** a rejected order is dropped and the rest of the file
still applies.

**Host behaviour.** BINARY-ONLY and LEGACY BUG. The original does *not* stop at
a bad record: it keeps applying the remaining records in the file and then
fails the file as a whole, aborting turn generation for it. Reaching this needs
a malformed or crafted order file, so it is serial-gated and cannot be produced
by the registered client; Elegy keeps the drop-and-continue rule above and does
not reproduce the whole-file abort. (See `LIMITS.md`, stars-elegy #65.)

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
- **Battle-plan fields.** BINARY-ONLY and LEGACY BUG (plan semantics from the
  combat decomp, stars-elegy #59 / stars-decomp #28; order validation
  `COMBAT.md` "Order validation", stars-elegy #71). The original does **not**
  range-check a battle-plan definition: a hand-built definition with a tactic
  of **6** or a primary or secondary **target of 8** — each exactly one past
  its legal set — is stored as given, and one can even **delete plan 0** (the
  default plan). Nor does anything validate the plan number a
  *fleet battle-plan assignment* names. These are multiplayer trust gaps of the
  same shape as the ownership asymmetry below. Elegy's chosen rule: **reject**
  an out-of-range tactic or target, never delete plan 0, and validate a fleet's
  battle-plan number against the owner's plans. See #59 for plan semantics (the
  16-plan limit and the renumbering of later plans when one is deleted).
  Confirming the original's acceptance needs the OX runs.

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
the same shape as the not-re-checked fleet orders above. Elegy's chosen rule
matches what the normal client can send: it accepts a detonate setting only
from a **Space Demolition** player, only on that player's **own** minefields,
and only on **standard** minefields — the three conditions the client's offer
is held to (see `OBJECTS.md`). Every field kind can in fact detonate (MF-7 and
MF-8 in `PARITY.md`), so the limit is the client's offer, not a test of which
kinds detonate. Confirming the original's open acceptance needs the OX runs.

**Production queue (starbase dock).** BINARY-ONLY and LEGACY BUG (launch
context in stars-elegy #57, `PRODUCTION-LAUNCH.md`). The host does **not**
check a starbase's dock capacity when it reads a production-queue change, so a
hand-built queue can build a ship at a starbase whose dock could never queue it
through the normal client. Elegy's chosen rule rejects such a queue order when
it is given. Confirming the original's open acceptance needs the OX runs.

**Production-queue replace.** CONFIRMED (`LIMITS.md` "Production-queue
replace", stars-elegy #65, LQ-1..LQ-6). A production-queue change replaces the
planet's whole queue with the submitted list, **in the submitted order**, after
the owner is checked (the order is rejected if the submitter does not own the
planet). An **empty** submitted list **removes** the queue entirely
(message `0x3f`).

A partial-build percent is carried across the replace this way: each submitted
item is matched, **in queue order and ignoring count**, against an as-yet
unmatched **old partial item of the same id and kind**. A submitted item that
finds such a match keeps its **submitted (client) percent**; one that does not
has its percent set to **0**. So the host trusts the percent the client sent
rather than recomputing from the old item's accumulated progress — LEGACY BUG.
**Elegy's chosen rule:** on a match, keep the **old** item's accumulated
percent instead of the client's submitted value (`LIMITS.md` records this
choice next to the host behaviour).

**Production-queue client limits (setting orders).** BINARY-ONLY (`LIMITS.md`
"Setting orders", stars-elegy #65). The limits the registered client enforces
while composing a queue order, which a crafted file can exceed:

- at most **40** items in a queue;
- item counts capped at **1020**;
- **Auto Alchemy** held at a count of **1**;
- **mines** and **factories** capped, across the whole queue, at
  `min(1020, max − installed)`;
- **Add** merges into the selected row, or the row just after it, when that
  row is already the same item (LQ-7).

Elegy enforces these as the client-legal bounds; a queue order that exceeds
them is reachable only by a crafted file (serial-gated).

### Cross-owner cargo

A *cargo transfer* order (the manual transfer, as opposed to a waypoint
transfer task) is resolved **in place while orders are applied** (turn order
step 1), not deferred to movement. The mechanics below are CONFIRMED; see
`TAKEOVER.md` "Manual cargo transfers to other players" (stars-elegy #69,
commit `9cef650`; colonist drop CONFIRMED by TK-501).

A transfer whose source and destination have the **same** owner is applied in
place at order time, subject to the destination's capacity. A cross-owner
transfer is also resolved at step 1 (not deferred), under these rules:

- **Owner check only.** The manual path compares **owners**; it makes **no**
  relation (enemy) check, so a gift to an enemy's fleet or planet is allowed
  here. (The *waypoint* task that transfers a fleet to another player's fleet
  is the path that refuses an enemy — see "Transfer fleet".)
- **Two passes, in place.** Within step 1 the host runs all **debits first**
  and then all **credits**, so same-step transfers draw from pre-transfer
  stocks. A manual gift is credited to the destination at this time, **not**
  after movement, and there is **no** queued-gift step for manual orders.
- **Colonists** onto a planet the giver does not own are a **drop**, resolved
  in the first drop step **before** movement (CONFIRMED, TK-501) —
  colonisation or invasion under the takeover/objects rules — not in the
  post-movement waypoint phase and not credited silently to the planet.
- **Missing endpoint.** A transfer record whose source or destination object
  is missing is **skipped whole**; neither side changes.
- **Receiver short of room.** A receiver without capacity takes **what fits**;
  the giver is sent message `0x0dd` and the remainder is **lost** (it is not
  returned to the giver).

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
none of it needs a crafted order file or the registered serial.

Most of this section has now been **measured** with that method: the WU oracle
batch (`CombatLab`-built starts on the two-player Combat Lab base, one pinned
host turn each; raw evidence in private `stars-oracle-apparatus`
`evidence/wu/`). Lines below are tagged CONFIRMED where a measurement agrees
with the binary reading, and BINARY-ONLY where still only read from the
program.

### Reaching a waypoint

When a fleet arrives at its next waypoint (its position equals waypoint 1),
that waypoint is consumed, and how depends on the fleet's **repeat-orders**
flag:

- **Repeat off:** the reached waypoint is dropped — the list shortens by one
  and the fleet goes on to what was the next waypoint. CONFIRMED (a three-
  waypoint fleet run onto its second waypoint came back with two).
- **Repeat on:** the reached waypoint is instead moved to the **end** of the
  list, so the fleet cycles through its waypoints indefinitely. CONFIRMED (the
  same fleet with repeat on kept three waypoints, the reached one now last).
  Two cases fall back even with repeat on. A list of only two waypoints — one
  forward leg — collapses to a single standing waypoint once that leg is
  reached: the circuit is not regenerated, so the fleet ends idle exactly as if
  repeat were off. And a reached waypoint whose position already equals the
  current last waypoint is not appended again, so the list does not grow. Both
  CONFIRMED (a two-waypoint repeat fleet came back with only the
  current-position waypoint; a three-waypoint repeat fleet whose last two
  waypoints shared a position came back with those two coincident waypoints and
  no third added).
- A **patrol** waypoint never repeats, even with repeat orders on. BINARY-ONLY.
- When a fleet reaches its **last** waypoint with no continuing task and no
  planet route to follow, it goes idle and its owner is messaged that the
  orders are complete. CONFIRMED (a fleet run onto its only waypoint ended
  idle with the completion message).

### Targets that moved, died or were captured

A waypoint can name a fleet (or a moving universe object) as its target
instead of fixed coordinates. Each upkeep pass re-resolves that target:

- **Target still exists:** the waypoint's coordinates are refreshed to the
  target's current position, so a fleet ordered to meet a moving fleet keeps
  chasing it. CONFIRMED (a waypoint aimed at a fleet that moved north came
  back with the target's new coordinates). Only a position is copied; the
  target's owner is not re-checked, so a waypoint keeps tracking a target fleet
  even if it has changed hands (been captured) — the captured case is
  BINARY-ONLY. An exception bit on the waypoint suppresses the refresh (the
  waypoint then holds its coordinates) — BINARY-ONLY.
- **Target gone (destroyed, or no longer a fleet):** the target is cleared
  and the waypoint becomes a plain go-to-coordinates waypoint at the
  last-known position; the fleet still travels there and then treats it as an
  ordinary reached waypoint. The order is not dropped outright. CONFIRMED (a
  waypoint aimed at a fleet id that did not exist came back cleared to a plain
  go-to at the last coordinates, not dropped).
- **Ordering with moving objects:** this re-resolution runs *after* Mystery
  Traders and mineral packets have moved but *before* fleets move, so a
  waypoint aimed at a moving Trader or packet reads that object's post-move
  position for the turn; wormholes move after fleets (objects decomp, stars-
  elegy #49, `OBJECTS.md`). Tracking a fleet target reads the target's
  position as of this same upkeep pass.

### Following another fleet (leader linkage)

CONFIRMED for the upkeep link, with the movement-phase freeze deferred to
`KERNEL.md` (stars-elegy #53). A fleet whose waypoint targets another fleet is
a **follower**; the targeted fleet is its **leader**. Upkeep resolves the link
each turn (the tracking rule above fixes the follower's waypoint onto the
leader's current position), and the movement phase then resolves chains and
cycles of followers:

- The leader is simply the fleet named by the waypoint target; a follower can
  itself be a leader to another follower (a **chain**), and two fleets can name
  each other (a **cycle**). CONFIRMED (a three-fleet chain came back with each
  follower advanced toward its leader and its waypoint re-pointed at the
  leader's new position for the next turn; a two-fleet cycle of equal-warp
  fleets met at the midpoint and both waypoints cleared to a plain go-to once
  the two fleets were co-located).
- Chains and cycles are what produce the chase-order freeze recorded in
  `KERNEL.md`: fleets move in id order, a follower that lands on its leader
  finishes, and a leader that is itself an unfinished follower stops for the
  year where it is caught. This document defers the movement resolution to
  `KERNEL.md` (the chaser rules, CONFIRMED there via FM-001..003): the measured
  symmetric cycle above converged cleanly, matching FM-001, and the id-order
  freeze is the asymmetric case recorded there. The upkeep link itself is the
  plain waypoint target, re-resolved each turn.

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

CONFIRMED for the ideal-warp case: a fleet carrying the route task at a planet
whose route pointed to another planet ~161 ly away came back with a fresh
two-waypoint order to that planet at warp 6 (the Long Hump 6 ideal warp, with
fuel to spare) and had begun moving. The stargate case is BINARY-ONLY (the
base starbases have no gate). This routing rule is the same one new fleets use
when they leave production; the shared statement lives in `PRODUCTION-LAUNCH.md`
(stars-elegy #57), which this section defers to rather than restating.

### Patrol task

Patrol sets a fleet to watch for enemy fleets and move to intercept one. It
never repeats (above). The target choice and warp were the one item here that
needed a direct measurement rather than a reading; the WU patrol runs pin them.
CONFIRMED:

- **Which enemy:** the patrol fleet intercepts the **nearest** enemy fleet
  within an engage radius of about **50 ly** (an enemy at 50 ly was engaged, one
  at 55 ly was not). That radius is a property of the patrol, not of scanning:
  it did not widen when the patrol fleet carried a 300 ly scanner, and enemies
  it could plainly see at 80–200 ly were left alone. Enemies beyond the radius
  are ignored even when in sensor range.
- **Ties:** among enemies at equal distance the choice is by **fleet order**
  (the lowest-numbered / first-found fleet), **not** by fleet strength — the
  same fleet was chosen whether it was the strong or the weak stack.
- **Warp:** the intercept warp is `min(10, range / 5)`, where *range* is the
  fleet's stored patrol range (patrol range 20 → warp 4, 40 → warp 8, 90 and
  250 → warp 10). The normal client's smallest patrol range already saturates
  this at warp 10.
- The intercept is written as a fleet-targeted waypoint at the enemy's
  position; the patrol fleet does not move the turn it acquires the target.

Elegy reproduces this: nearest enemy within the ~50 ly radius, ties by fleet
order, intercept warp `min(10, range/5)`.

### Transfer fleet (give a whole fleet to another player)

The transfer-fleet task hands the entire fleet to a named recipient. The host
refuses it in four cases; an implementation that validates the gift up front
reproduces the original:

- **Recipient is an empty or eliminated slot.** The gift is refused with its
  own message to the giver. BINARY-ONLY (the oracle bases carry no absent or
  eliminated player to aim at). This is the only refusal that keys off the slot
  being vacant rather than off the recipient's disposition or the cargo.
- **Recipient is a computer player.** A computer player never accepts a gifted
  fleet: the transfer is refused and the fleet keeps its owner. CONFIRMED (on a
  base of computer opponents, a non-colonist fleet gifted to an expert computer
  was refused and stayed with the giver). This is **not** a separate
  computer-only rule — it is the enemy refusal below. A live computer is an
  ordinary, present player, so it is not caught by the vacant-slot case; an
  expert computer is simply hostile to the human, so the gift fails the
  recipient-relation check. Forcing the computer's stored relation to the giver
  to neutral does not change the outcome (the computer is still hostile when the
  gift is evaluated), so there is no setting under which a computer accepts a
  gift.
- **Recipient treats the giver as an enemy.** If the recipient's relation
  toward the giver is "enemy" (or the recipient otherwise declines gifts),
  the transfer is refused. CONFIRMED (a gift to a recipient whose relation to
  the giver was "enemy" was refused; the fleet kept its owner, with a message).
- **The fleet carries colonists.** A colonist-carrying fleet cannot be
  gifted; the transfer is refused. CONFIRMED (a colonist-carrying gift to a
  willing non-enemy was refused; the fleet kept its owner).

Otherwise the fleet changes owner — CONFIRMED (an empty fleet gifted to a
willing non-enemy human became that player's fleet). (The coverage audit
flagged the computer-player and treated-as-enemy refusals as missing; both are
now measured, and the colonist refusal was already read.)

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

- **OX merge-order cap and loss.** The direct merge order's per-design cap is
  read but untested (only the waypoint task was measured, and it has no cap);
  push a direct merge past 32767 and confirm a stack of 32767 is kept while one
  that would reach 32768 or more is slammed to 32766 with the excess lost (not
  spilled, not refused) — the same boundary as the Merge-with-Fleet task above
  (32767 kept, 32768+ becomes 32766). Confirms "Merge order".
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
editing**, not crafted order files, so none needed the registered serial, and
most have now been **run** (the WU batch; `experiments/wu/` here, raw evidence
in private `stars-oracle-apparatus` `evidence/wu/`). Measured and folded into
the sections above as CONFIRMED: repeat vs drop, the idle message, live and
gone fleet targets, the route task (ideal-warp case), the enemy and
colonist transfer refusals plus the empty-fleet success, the patrol target
rule (nearest enemy within ~50 ly, ties by fleet order, warp `min(10,range/5)`),
the two repeat fall-backs (a two-waypoint circuit and a coincident reached/last
waypoint), the follower-linkage upkeep (a three-fleet chain and a two-fleet
cycle), and the computer-player transfer refusal (a fleet gifted to an expert
computer, measured on a computer-opponents base built with the fleetlab
`keepfleets-ordered` directive).

Still open (fleetlab HST editing, no serial):

- **WU patrol no-repeat.** Repeat flag on, a patrol waypoint reached; confirm
  it is not rotated to the end.
- **WU captured target.** Track a fleet target that changes owner mid-turn;
  confirm the waypoint keeps tracking it (owner not re-checked), and that the
  suppress bit holds coordinates instead.
- **WU route stargate.** Route between two gated planets with an empty fleet;
  confirm it is sent through the stargate rather than at warp.

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
- **OX battle-plan-range.** Submit a battle-plan definition with an
  out-of-range tactic (6) and target (8), a definition that deletes plan 0, and
  a fleet battle-plan assignment naming a plan the owner does not have; confirm
  the original stores the out-of-range plan, lets plan 0 be deleted, and
  applies the bad fleet assignment (rather than rejecting any of them).
  Confirms "Battle-plan fields" (stars-elegy #59).
- **OX starbase-dock.** Submit a production-queue change that builds a ship at
  a starbase whose dock could not queue it; confirm the original accepts it.
  Confirms "Production queue (starbase dock)" (stars-elegy #57).
- **OX ownership.** For each not-re-checked kind, have one player submit an
  order naming another player's object; confirm the original applies it
  (and, for cargo, applies the cross-owner redirection). Confirms
  "Ownership" and "Cross-owner cargo". Keep the crafted inputs for this item
  in private apparatus.
- **OX conflict.** Pin the generator, submit two players' conflicting orders
  on one object, and vary only the generator seed; confirm which player's
  order wins tracks the replay permutation. Confirms "Conflicts between
  players".
