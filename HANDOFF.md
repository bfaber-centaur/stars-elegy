# Handoff

**Checkpoint, frozen at 2026-10-07 23:12Z.** This file describes what was
known at the revisions below. It is not kept current. Statements about
open pull requests, lanes and implementation status are observations at
that moment. For the live state, see the
[stars-elegy pull requests](https://github.com/bfaber-centaur/stars-elegy/pulls)
and [elegy pull requests](https://github.com/bfaber-centaur/elegy/pulls),
and elegy's `docs/*-STATUS.md` on its current `main`.

| Repository | Revision at the checkpoint |
|---|---|
| stars-elegy | `5469029` (merge of #82, Cybertron) |
| elegy | `b162470` (merge of #13, orders layer) |

## Current question

At the checkpoint, the original's turn generation was specified nearly
end to end in `docs/`, and every spec pull request from the 2026-10-07
waves had merged. The question was how quickly Elegy could consume what
is specified, and which open research items it would run into on the way.

## State (observed at the checkpoint)

- **stars-elegy `5469029`.** The only open pull request was this one
  (#67). `docs/` held:
  - AI.md (the shared core) and `docs/ai/` for Robotoid, Rototill,
    Cybertron, Turindrone and Automitron;
  - COMBAT, COMPONENTS, ESTIMATES, KERNEL, LIMITS, MESSAGES, OBJECTS,
    ORDERS, PRODUCTION-LAUNCH, RACES, SCANNING, TAKEOVER and UNIVERSE.

  `PARITY.md` held the measurements, `vectors/` the parity vectors, and
  `tools/speclint` ran in CI. The public gap list is `docs/COVERAGE.md`.
- **elegy `b162470`.** No pull request was open. Its status files under
  `docs/` recorded these as implemented:
  - the peaceful kernel and fleet movement;
  - battles;
  - per-player knowledge;
  - takeover;
  - the measured component table;
  - fleet merges and scores;
  - new-game generation and race design, including the built-in computer
    races;
  - production queues in the parity harness;
  - the orders layer, including ships leaving production.

  `YearOrders` was not yet called from `GenerateTurn`.

## What we know

- No oracle miss is unexplained. The last one, TK-305 (Mystery Trader
  parts from scrapping), was reconciled as random-stream variation, and
  TK-307 then predicted 5 of 5.
- Every top gap of the first coverage audit is closed or owned: ships
  leaving production, waypoint upkeep, client estimates, the message
  catalogue, setting orders and limits, and the shared core for computer
  players.
- Under the checked-only policy for computer players (`AI.md` "Project
  policy"; Bobby, 2026-10-07):
  - **Candidates for faithful implementation:** Robotoid, Rototill and
    Cybertron. Each matches every captured player-year of its corpus.
  - **Legacy reference:** Turindrone and Automitron, whose fleet passes
    are checked (AI-22, AI-23) but which are not committed to
    implementation, and Macinti. Their bomber paths stay BINARY-ONLY.
  - Reproducing all six personalities is not an objective. A new
    computer-player experiment needs a concrete reason: an Elegy blocker,
    a spec contradiction, or a cheap closure.
  - The state leaks between computer players (AI-13, AI-18) sit behind a
    named legacy-compatibility switch. Elegy defaults to clean per-player
    state.
- Cross-player cargo, in the original:
  - A manual gift is credited in place while orders are replayed,
    before movement, and silently. The timing is MEASURED (TK-406/407/409,
    TK-415/416).
  - A gift to a receiver that is already gone when the gift is replayed
    is skipped whole, and the giver keeps the cargo. This is BINARY-ONLY.
  - A separate queued cross-owner credit path exists, but no legal order
    is known to reach it. `ORDERS.md` keeps it as an **unresolved
    hypothesis, not a rule**, and makes no claim about delivery after
    movement or about cargo lost on that path.
- Every rule keeps its evidence label (CONFIRMED, MEASURED, BINARY-ONLY,
  LEGACY BUG, UNREACHABLE, SERIAL-GATED). A BINARY-ONLY rule is the best
  reading of the original, not yet run against it.

## What still mattered at the checkpoint

Questions on Elegy's path:

- **A gifted receiver removed by a later order in the same turn.** In
  the original the gift is already aboard by then; `ORDERS.md` at
  `5469029` did not say what happens to that cargo. Elegy keeps its own
  two-pass bookkeeping (debit, then credit) and its assumption L9 for
  this case. That bookkeeping is an implementation choice, not a measured
  rule of the original.
- **Spec text that lagged the evidence at `5469029`:**
  - MESSAGES.md said component announcements check only the levelled
    field. KX-005 R1 showed a part with an unmet electronics
    requirement was not announced; that all six requirements are
    checked is the binary reading.
  - AI.md §11 called the combat power estimate unpublished; KERNEL.md
    "Scores" gives the per-design power formula.
  - AI.md "Open experiments" still listed cases that stage 1 settled.
  - OBJECTS.md still listed the Harder computer-planet trade threshold
    as open. O-53 confirmed that a Harder planet trades at 3,600 kT
    against the 3,500 kT threshold; the exact edge is untested.

Research items, none of them blocking:

- 147 message-catalogue rows have no oracle sighting yet (`MESSAGES.md`
  "Kinds not yet observed"); most are reachable with legal orders.
- These have not been run:
  - the SCANNING report edges (S-11, S-21, S-24);
  - packet limits and the Mystery Trader's leaving and part reroll;
  - three-way chase cycles;
  - the victory conditions;
  - the 4050-object limit and waypoints per fleet.
- The plain setting orders are written only in `LIMITS.md`. They still
  need folding into `ORDERS.md` and an oracle check.
- Whether any legal order reaches the queued cross-owner credit path.

Bobby's open decisions at the checkpoint:

- the serial, which crafted-order (OX/OR) cases wait on;
- whether strict whole-program legacy parity for computer players, with
  the leak switch on by default, is ever wanted.

Next Elegy milestones, in the order the public spec supports them:

1. Run the accepted orders inside each year's turn, so that the orders'
   drops and gifts reach the waypoint phases (KERNEL.md "Turn order",
   step 1).
2. The remaining waypoint tasks: load, scrap, transfer, lay mines and
   patrol (`ORDERS.md`, `TAKEOVER.md`).
3. Space objects from `OBJECTS.md`: minefields, mineral packets,
   wormholes, the Mystery Trader and stargates. Their scanning rules
   (`SCANNING.md` "Space objects") come with them.
4. Terraforming beyond the Claim Adjuster's year-end step, and remote
   mining.
5. The three candidate computer players, on top of the `AI.md` shared
   core, with the leak switch off by default.

## Best next move (as judged at the checkpoint)

Send new capacity round this loop: Elegy implementation, then the spec
question the implementation raises, then a bounded prediction and oracle
experiment, then reconciliation. Start with milestone 1, which every
later milestone needs in order to be playable. Do not start broad
archaeology of the original or personality-completion work.
