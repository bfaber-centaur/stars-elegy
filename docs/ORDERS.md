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

**Merge order** (a direct "merge these fleets now" order). Each per-design
stack is held to at most 32766 ships. BINARY-ONLY — this path is read from
the program but not yet oracle-tested.

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

## Open experiments

These rules are read from the original program and not yet measured in the
original game. Each is a numbered prediction with the discriminating
observation that would confirm it; the proposed oracle corpus prefix is
**OX** (orders).

The fleet-operation clamps, turn placement, the transfer-fleet owner check
and the Merge-with-Fleet task (including its damage dilution and the missing
ship-count cap) have since been measured — see the Fleet operations section
and `PARITY.md`, "Fleet Operations" (FO-01..07). Still open there:

- **OX merge-order cap.** The direct merge order's 32766 per-design cap is
  read but untested (only the waypoint task was measured, and it has no cap);
  confirm whether the order path clamps.
- **OX split.** Split some ships off a loaded fleet; confirm the new fleet
  has exactly the ordered ships, a capacity-proportional share of the cargo,
  and the source's battle plan and waypoints. Confirms "Split".

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
