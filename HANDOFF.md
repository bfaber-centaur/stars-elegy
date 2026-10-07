# Handoff

## Current question

The original's turn generation is now specified nearly end to end across
`docs/`. The public gap list is `docs/COVERAGE.md` (owned by the
scanning/launch lane). The project-level question is how fast Elegy can
consume what is specified, and which few open research items it will hit.

## State

- Specs on `main`: AI (shared core), COMBAT, COMPONENTS, ESTIMATES,
  KERNEL, MESSAGES, OBJECTS, ORDERS, PRODUCTION-LAUNCH, SCANNING,
  TAKEOVER, UNIVERSE, `docs/ai/robotoid.md`; PARITY.md holds the
  measurements; `vectors/` holds parity vectors; `tools/speclint` runs in CI.
- Open spec pull requests (2026-10-07, 21:30Z): RACES.md, UNIVERSE.md
  answers, OBJECTS.md packets/Trader/stargates incl. GT-004, Turindrone
  and Automitron (#49); KERNEL.md KX-005, OT and KB batches (#53);
  LIMITS.md, setting orders and queue replace, LQ (#65); orders vectors
  (#78); ORDERS.md client-order and WU results (#80); Rototill and
  AI-10, AI-13..17 (#81).
- Elegy waits on these merges: its kernel, orders-layer and new-game
  pull requests follow #53, #80 and #49.

## What we know

- Every top gap of the first coverage audit is closed or owned: ships
  leaving production, waypoint upkeep, client estimates, the message
  catalogue, setting orders and limits, and computer players (shared core
  CONFIRMED; every personality read, designs and production checked for
  four of six).
- Questions raised while implementing Elegy's orders layer were answered
  by client-order runs (CO-01..08) and LIMITS.md the same evening.

## What still matters

- One oracle miss is unexplained: TK-305 (Mystery Trader parts from
  scrapping came far more often than predicted; TK-203 points the same
  way).
- Still not run: about 147 reachable message kinds never seen; SCANNING
  report edges (S-11, S-21, S-24); packet limits and Trader leave/reroll;
  three-way chase cycles; victory edge cases; long captures of each
  computer player's war behaviour. Crafted-order (OX/OR) cases wait on the
  serial decision.
- Text that lags the evidence: MESSAGES.md part announcements (KX-005
  shows every requirement is checked); LIMITS.md merge rows (#65) against
  CO-06; #80's direct-merge clamp wording; AI.md's open list names cases
  stage 1 settled; `docs/ai/macinti.md` and `cybertron.md` are planned
  but not published.
- Bobby's decision on how faithful computer players must be for war and
  long-game behaviour (the leak between computer players is specified as
  a LEGACY BUG switch).

## Best next move

Merge-chain repair, then bias new capacity toward Elegy: space objects
(OBJECTS.md) once #49 merges. Keep every active lane running to its own
checkpoint.
