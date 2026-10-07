# Handoff

## Current question

The original's turn generation is specified nearly end to end in `docs/`,
and every spec pull request from the 2026-10-07 waves has merged. The
question now is how quickly Elegy can consume what is specified, and which
of the remaining open research items it will run into on the way.

## State

Snapshot taken from GitHub on 2026-10-07 at 23:20Z.

- **stars-elegy.** The only open pull request is this one (#67). The specs
  on `main` are AI (the shared core, plus `docs/ai/` for Robotoid,
  Rototill, Cybertron, Turindrone and Automitron), COMBAT, COMPONENTS,
  ESTIMATES, KERNEL, LIMITS, MESSAGES, OBJECTS, ORDERS, PRODUCTION-LAUNCH,
  RACES, SCANNING, TAKEOVER and UNIVERSE. `PARITY.md` holds the
  measurements, `vectors/` the parity vectors, and `tools/speclint` runs in
  CI. The public gap list is `docs/COVERAGE.md`.
- **elegy.** No pull request is open. `main` has the following, each with
  its own status file under `docs/`:
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

## What we know

- No oracle miss is unexplained. The last one, TK-305 (Mystery Trader
  parts from scrapping), was reconciled as random-stream variation, and
  TK-307 then predicted 5 of 5.
- Every top gap of the first coverage audit is closed or owned: ships leaving
  production, waypoint upkeep, client estimates, the message catalogue,
  setting orders and limits, and the shared core for computer players.
- Under the checked-only policy for computer players (`AI.md` "Project
  policy"):
  - **Candidates for faithful implementation:** Robotoid, Rototill and
    Cybertron. Each matches every captured player-year of its corpus.
  - **Legacy reference:** Turindrone and Automitron, whose fleet passes
    are checked (AI-22, AI-23) but which are not committed to
    implementation, and Macinti. Their bomber paths stay BINARY-ONLY.
  - Reproducing all six personalities is not an objective.
  - A new computer-player experiment needs a concrete reason: an Elegy
    blocker, a spec contradiction, or a cheap closure.
  - The state leaks between computer players (AI-13, AI-18) sit behind a
    named legacy-compatibility switch. Elegy defaults to clean per-player
    state.
- Cross-player cargo:
  - A manual gift is resolved in place when orders are replayed, and is
    silent. The timing is MEASURED (TK-406/407/409, TK-415/416).
  - A gift to a receiver that has already gone is skipped whole, and the
    giver keeps the cargo. This is BINARY-ONLY.
  - A separate queued cross-owner credit path exists in the original, but
    no legal order is known to reach it. `ORDERS.md` keeps it as an
    **unresolved hypothesis, not a rule**, and makes no claim about
    delivery after movement or about cargo lost on that path.
- Every rule keeps its evidence label (CONFIRMED, MEASURED, BINARY-ONLY,
  LEGACY BUG, UNREACHABLE, SERIAL-GATED). A BINARY-ONLY rule is the best
  reading of the original but has not been run against it.

## What still matters

Research items:

- 147 message-catalogue rows have no oracle sighting yet (`MESSAGES.md`
  "Kinds not yet observed"); most are reachable with legal orders.
- These have not been run:
  - the SCANNING report edges (S-11, S-21, S-24);
  - packet limits and the Mystery Trader's leaving and part reroll;
  - three-way chase cycles;
  - the victory conditions;
  - the 4050-object limit and waypoints per fleet.
- The plain setting orders are written only in `LIMITS.md` and still need
  folding into `ORDERS.md` and an oracle check.
- Crafted-order cases (OX/OR) wait on Bobby's decision about the serial.
- Whether a legal order ever reaches the queued cross-owner credit path
  (above).
- Bobby has not decided whether strict whole-program legacy parity for
  computer players, with the leak switch on by default, is ever wanted.

Next Elegy milestones, in the order the public spec supports them:

1. Run the accepted orders inside each year's turn. `YearOrders` is not
   yet called from `GenerateTurn`, so the orders' drops and gifts do not
   yet reach the waypoint phases. This is the kernel lane's next step
   (KERNEL.md "Turn order", step 1).
2. Space objects from `OBJECTS.md`: minefields, mineral packets,
   wormholes, the Mystery Trader and stargates. Their scanning rules
   (`SCANNING.md` "Space objects") come with them. Elegy has none of these
   objects yet.
3. Terraforming other than the Claim Adjuster's year-end step.
4. The three candidate computer players, on top of the `AI.md` shared
   core, with the leak switch off by default.

## Best next move

Send new capacity round this loop: Elegy implementation, then the spec
question that implementation raises, then a bounded prediction and oracle
experiment, then reconciliation. Start with milestone 1, which every later
milestone depends on to be playable. Do not start broad archaeology of the
original or new personality-completion work. Let every active lane run to
its own checkpoint.
