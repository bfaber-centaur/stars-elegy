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
- Open spec pull requests (2026-10-07, 21:40Z): RACES.md, UNIVERSE.md
  answers, OBJECTS.md packets/Trader/stargates incl. GT-004, Turindrone
  and Automitron (#49); KERNEL.md KX-005, OT and KB batches (#53);
  LIMITS.md, setting orders and queue replace, LQ (#65); orders vectors
  (#78); ORDERS.md client-order and WU results (#80); Rototill and
  AI-10, AI-13..17 (#81); Cybertron, AI-19..21 (#82); TK-305
  reconciled, TK-307 (#83).
- Elegy waits on these merges: its kernel, orders-layer and new-game
  pull requests follow #53, #80 and #49.

## What we know

- Every top gap of the first coverage audit is closed or owned: ships
  leaving production, waypoint upkeep, client estimates, the message
  catalogue, setting orders and limits, and computer players (shared core
  CONFIRMED).
- Computer players, under Bobby's stopping rule (2026-10-07, option B,
  checked only for the legacy computer-player program):
  - Candidates for faithful implementation, oracle-checked: Robotoid
    (AI-8/9/12), Cybertron (AI-19..21, #82), Rototill (AI-14..17, #81),
    Turindrone (AI-22, 689/689, #49) and Automitron (AI-23, 264/264, #49).
    Bombers and armadas were never exercised, so the armada parameters
    stay BINARY-ONLY.
  - Reference only, optional future work: Macinti. Its measurements are
    kept.
  - Reproducing all six personalities is no longer an objective. Active
    computer-player lanes finish their current checkpoint and then stop
    unless reauthorized. A new computer-player experiment needs a concrete
    reason: an Elegy implementation blocker, a spec contradiction, a
    high-value question, or a cheap bounded closure.
  - The state leak between computer players is kept behind a named
    legacy-compatibility switch. Normal Elegy semantics use clean
    per-player state.
- Questions raised while implementing Elegy's orders layer were answered
  by client-order runs (CO-01..08) and LIMITS.md the same evening.

## What still matters

- No oracle miss is unexplained. TK-305 (Mystery Trader parts from
  scrapping) was reconciled as random-stream variation, and TK-307
  predicted 5 of 5 (#83).
- Still not run: about 147 reachable message kinds never seen; SCANNING
  report edges (S-11, S-21, S-24); packet limits and Trader leave/reroll;
  three-way chase cycles; victory edge cases. The unrun computer-player
  items are kept as reference, not as a queue. Crafted-order (OX/OR) cases wait on the
  serial decision.
- Text that lags the evidence: MESSAGES.md part announcements (KX-005
  shows every requirement is checked); LIMITS.md merge rows (#65) against
  CO-06; #80's direct-merge clamp wording; AI.md's open list names cases
  stage 1 settled; AI.md still links `docs/ai/macinti.md`, which is
  unpublished (Macinti is now reference only; `cybertron.md` comes with #82).
- Bobby's open decisions: the serial (crafted-order runs), and whether
  strict whole-program legacy parity for computer players is ever wanted.

## Best next move

Merge-chain repair, then send new capacity round the loop Elegy
implementation → implementation-surfaced spec question → bounded
prediction and oracle experiment → reconciliation. Candidates: space
objects (OBJECTS.md) once #49 merges, and the five checked computer
players once #49, #81 and #82 merge. Do not start broad computer-player
archaeology. Keep every active lane running to its own
checkpoint.
