# Handoff

## Current question

The original's turn generation is now mapped and mostly specified across
the spec files in `docs/`. The public gap list is `docs/COVERAGE.md`
(owned by the scanning/launch lane; its latest refresh rides the
PRODUCTION-LAUNCH.md pull request). The project-level question is what new
capacity should do now that the specs have outrun Elegy's implementation.

## State

- Specs on `main`: KERNEL, COMBAT, COMPONENTS, ESTIMATES, MESSAGES,
  OBJECTS, ORDERS, SCANNING, TAKEOVER, UNIVERSE; PARITY.md holds the
  measurements; `vectors/` holds parity vectors; `tools/speclint` runs in CI.
- Open spec pull requests (2026-10-07 evening): RACES.md and stargates
  (#49), ORDERS.md waypoint upkeep (#51), KERNEL.md full turn order and
  terraforming (#53), PRODUCTION-LAUNCH.md and COVERAGE.md (#57), battle
  plans (#59), ship launch and combat rounds 7–8 (#61), AI.md shared core
  (#63, merge before #49), vectors (#65, #66).
- The PG-003 crowding question from the previous handoff is settled:
  growth is CONFIRMED in KERNEL.md "Population growth" (the quadratic in
  integer permille plus the carry reproduces 2400–2436, and the decoded
  `excessPop` matches the carry every year); KX-002 corrected the
  overcrowding factor to 4.

## What we know

- The five largest gaps of the first coverage audit are closed or owned:
  ships leaving production (SL-01..12), waypoint upkeep (WU), messages
  (catalogue of 387 kinds), client estimates (ES-001/002), computer
  players (shared core AI-0..AI-2 CONFIRMED; personalities in progress).
- Every open Elegy assumption already has an answer on an open spec PR.
  Elegy does not yet implement the orders layer, space objects,
  production launch, terraforming, messages or computer players.

## What still matters

- No oracle miss is unexplained right now: every MISSED or CONTRADICTED
  case has been reconciled with a corrected rule or traced to a setup or
  checker defect. Still open are committed predictions not yet run
  (KB-2A..C, TK-301..305, packet launch O-16..19, O-45, O-53, WU patrol
  no-repeat / captured target / route via stargate, the M-2 follow-up and
  M-10 tie, AI-4, AI-7, the Turindrone/Automitron production and fleet
  round) and every crafted-order (OX) case, which waits on the serial
  decision. Some OX cases are legal client actions and may be reachable
  through client-orders (ORACLE.md "Client orders", #61); untested.
- Doc defects to fix by their owners: MESSAGES.md part announcements
  (KX-005 shows all six requirements are checked); OBJECTS.md open item 5
  on #49 ("counted once", GT-002 measured twice); AI.md links a
  `docs/ai/macinti.md` that does not exist yet; PARITY.md population
  "Unknown" list is stale.
- Not owned by any lane: the effects of plain setting orders (research
  settings, relations, planet flags, renames) and of replacing a
  production queue; one collected list of limits (design slots, queue
  length, space objects, battle plans); player-to-player mail.
- The year-wide random draw order (KERNEL lane).

## Best next move

Bias new capacity toward Elegy: implement settled specs (orders layer
first) and send the questions implementation surfaces back into the
experiment loop. Keep every active lane running to its own checkpoint.
