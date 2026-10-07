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

## Open experiments

These rules are read from the original program and not yet measured in the
original game. Each is a numbered prediction with the discriminating
observation that would confirm it; the proposed oracle corpus prefix is
**OX** (orders).

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
