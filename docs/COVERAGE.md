# Coverage of the original game by the public specs

A map from what the original J-RC3 host does each year (and what its
client shows) to the spec files here. Its job is to show what is still
missing. It lists behaviors, not code. The mapping comes from a white-box
walk of the original program's turn generation, order replay and
computer-player code (private `stars-decomp`), checked against these files
on `main` as of 2026-10-07 (night). Every spec file named here is on
`main`.

Levels:
- **Confirmed**: specified, mostly CONFIRMED.
- **Read**: specified, mostly BINARY-ONLY.
- **Partial**: specified, but some behaviors are missing.
- **Missing**: no spec.
- **In progress**: a lane owns it and a pull request is open.

## By part of the year

| Behavior | Spec | Level | What is missing |
|---|---|---|---|
| Accepting and replaying orders, random player order, serial checks | `ORDERS.md`, `KERNEL.md`, `LIMITS.md` | Partial | Validation, ownership, fleet operations and design legality are covered. Production-queue replace (CONFIRMED, LQ-1..LQ-6) and the setting orders (Read) are in `LIMITS.md`, to be folded into `ORDERS.md`. |
| Race checks at the start of the year | `RACES.md`, `KERNEL.md` "Item costs" | Confirmed | Advantage points and the degrading of an over-budget race. |
| Tasks before movement: unload, scrap, colonize, drops, load, merge, cargo to other players | `TAKEOVER.md`, `ORDERS.md` | Confirmed | Split, merge and own-fleet transfer orders by client orders (CO-01..CO-08). Cargo to other players: drops before movement CONFIRMED (TK-501), the in-place fleet gift MEASURED (TK-406, TK-407, TK-409); a deferred cross-owner credit path is an unresolved hypothesis (`ORDERS.md` "Cross-owner cargo"). Scrap details are Read. |
| Packets, wormholes, Mystery Trader | `OBJECTS.md`, `KERNEL.md` "Random events" | Confirmed / Read | Wormholes (WT), the Trader's appearance, movement, meeting and rewards. Packet launch is Read. |
| Fleet movement, fuel, chasing, stargates | `KERNEL.md`, `OBJECTS.md` | Confirmed | Stargates (GT corpus) and the chain-freeze LEGACY BUG included. |
| Minefields | `OBJECTS.md` | Confirmed | MF-1..MF-13. Open: the 4050-object limit, SS and SD safe-warp bonuses. |
| Colonists breeding inside fleets (one primary trait) | `KERNEL.md` | Confirmed | OT-5. The case where a fleet breeds 0 and a random draw gives 1 is Read. |
| Mining, resources, research tax, production queues, terraform items | `KERNEL.md`, `PARITY.md` PQ | Confirmed | |
| Ships and starbases leaving production | `PRODUCTION-LAUNCH.md` | Confirmed | SL-01..SL-12. The same-hull replacement cost and the research share of an unbuilt ship are Read. |
| Population growth | `KERNEL.md` | Confirmed | |
| Research and tech progression | `KERNEL.md` "Research" | Confirmed | KX-002, KX-003, KX-005 and KB-2 (field switching at 26, stealing under slower tech). The level-10 cap for capped players is Read. |
| Random events: meteors, climate change, new minerals, Trader arrival | `KERNEL.md` "Random events", `OBJECTS.md` | Confirmed | KX-004. |
| Battles, battle plans | `COMBAT.md` | Confirmed | Battle movement confirmed by exact replays. |
| Bombing, invasion, colonization, capture | `TAKEOVER.md` | Confirmed | |
| Tasks after movement: remote mining, laying mines, patrol, route, transfer fleet | `KERNEL.md`, `OBJECTS.md`, `ORDERS.md`, `SCANNING.md`, `TAKEOVER.md` | Confirmed | The WU batch confirmed the patrol target rule, the route task (ideal-warp case) and the transfer-fleet refusals (enemy, colonists aboard, computer player). Routing through a stargate is MEASURED (wuRSG2). |
| Waypoint upkeep | `ORDERS.md` "Waypoint upkeep and the remaining tasks", `SCANNING.md` | Confirmed | The WU batch confirmed repeat versus drop, the idle message, live and gone fleet targets, both repeat fall-backs and follower linkage. A planet target captured mid-turn keeps the waypoint (MEASURED, wuCAP); a fleet target changing owner in place stays BINARY-ONLY (not reachable by client orders). |
| Sweeping, repair | `OBJECTS.md`, `COMBAT.md` | Confirmed | |
| Claim Adjuster and orbital-adjuster terraforming | `KERNEL.md` "Terraforming" | Confirmed | KX-005 (drift, year-end step, half-price terraform), OT-4, TK-108 and TK-118..120 (after a capture). |
| Duplicate-serial penalties | `KERNEL.md`, `MESSAGES.md` | Read | |
| What each player knows | `SCANNING.md` | Confirmed | |
| Scores and victory | `KERNEL.md` "Scores and victory conditions" | Confirmed / Read | Score KX-003; the victory conditions are Read. |
| New games | `UNIVERSE.md`, `RACES.md` | Confirmed | |
| Messages to players | `MESSAGES.md` | Confirmed / Read | All 387 kinds are catalogued (sender, recipients, values, phase); 198 rows are CONFIRMED. The rest are listed under "Kinds not yet observed, and how to reach them" and as gap 3 below. Player-to-player mail is not covered. |
| Computer players | `AI.md` (shared core), `UNIVERSE.md` (starting setup) | In progress | Shared core specified (built-in races, research and starbase designs CONFIRMED; planet automation Read). Robotoid, Rototill and Cybertron are checked against oracle captures and are the faithful candidates (`AI.md` project policy; AI-8, AI-9, AI-12, AI-14..AI-17, AI-19..AI-21). Turindrone, Automitron and Macinti are legacy reference only; Turindrone's and Automitron's fleet passes are checked (AI-22, AI-23) without an implementation commitment. The cross-player leaks are AI-13 and AI-18. Special rules for computer players inside the year are scattered: no fleet gifts to them (`ORDERS.md`), automatic trading with the Mystery Trader (`OBJECTS.md`). |
| What the client shows: production completion estimates, arrival estimates, fuel and research estimates, planet value, report history | `ESTIMATES.md`, `SCANNING.md` ("Old reports") | Confirmed | ES-001 matched 149 of 149 readings; ES-002 confirmed stargate legs, "Skipped", Generalized Research, "Maxed Out" and the distance display. |
| Limits: fleets, space objects, minefields, designs, queue length | `LIMITS.md`, `PRODUCTION-LAUNCH.md` (fleets), `OBJECTS.md` (minefields and objects) | Partial | Collected in `LIMITS.md`. Fleets (512), minefields (512, or 511) and the client's queue limits (LQ) are CONFIRMED or MEASURED. Open: the 4050-object limit (not run), waypoints per fleet, the host's 16th battle plan and other crafted-order cases (serial-gated). |

## Largest gaps for a playable game

1. **Computer players' own turns.** Elegy reproduces faithfully only the
   checked personalities (`AI.md` project policy). The shared core is in
   `AI.md`; Robotoid, Rototill and Cybertron are specified and checked
   (`docs/ai/`). Turindrone, Automitron and Macinti stay legacy reference
   (Turindrone's and Automitron's fleet passes are checked, AI-22 and
   AI-23); further work on them needs a concrete reason. Cross-player state
   leaks (AI-13, AI-18) are a legacy-compatibility switch, off by default.
2. **The plain setting orders** (research settings, relations, planet
   flags, renames): written only in `LIMITS.md` "Setting orders" (Read);
   they still need folding into
   `ORDERS.md` and an oracle check. The production-queue replace rule is
   done (LQ-1..LQ-6).
3. **Messages not yet observed** (`MESSAGES.md`, "Kinds not yet observed,
   and how to reach them"). Most are reachable with legal orders and
   Combat Lab setups, and the messages lane batches them. Targeted
   experiments for the rest:
   1. Manual cargo transfers (0x002, 0x042–0x04d, 0x0db–0x0dd): legal
      client orders, now being run through client orders. Transfers to
      another player's fleet (0x046–0x04d partial and refused, fuel
      0x043/0x045) still need a client path, since the Cargo Transfer
      dialog the tool opens shows only the orbited planet.
   2. Kinds the client makes when a turn is opened and never writes to a
      file (0x0aa–0x0ae, 0x15d newly found planets, 0x151 incoming packet
      the planet cannot catch, 0x152 starbase finishing its whole queue,
      0x153/0x154 battle count): read the client's message list after legal
      setups, using client automation.
   3. Registration penalties (0x100–0x107): need a player flagged for an
      invalid or shared serial; waiting on Bobby's serial decision.
   4. Never sent (0x00e–0x022, 0x065, 0x06f, 0x16b, 0x175, 0x0d1, 0x0d2,
      0x124, 0x125 and the "no sender" table): no experiment is possible;
      the check is negative, and no corpus has shown one so far.
4. **Limits still open** (`LIMITS.md`): the
   4050-object limit, waypoints per fleet, and the crafted-order cases
   that wait on the serial decision.

Not ranked, because a lane already owns them or they are covered:
research and terraforming, random events, scores and victory, race
design, wormholes and the Mystery Trader, stargates, ships leaving
production, waypoint upkeep and the remaining tasks (WU batch), battle
plans and client estimates.

## Targeted experiments outside the main gaps

Behaviors that are specified but that legal orders or new games cannot
easily reach, or that show only in the client. Each row says how it
could be reached.

| Behavior | Spec | Reach |
| --- | --- | --- |
| Wormhole stability names in the report | `OBJECTS.md` | Client only: read the report through client automation. |
| Computer-player counts in unseeded wizard games; the wizard's own rules | `RACES.md` "Wizard" | Client only: drive the new-game wizard. |
| The penalty's research-field step | `RACES.md` | Needs growth 1 while staying under 500 points; looks unreachable. |
| A second punishment for an already-tampered race that goes negative again | `RACES.md` | Runnable, but low value. |
| Mystery Trader appearance: the part reroll, late-year conversion, ship counts after year index 100, the 25th-redraw LEGACY BUG, leaving with 1 in 2 at an edge | `OBJECTS.md` | A sampling job over many seeds and years; 0 of 4 lone arrivals have left so far. |
| Harder computer players' Trader threshold (3,500 kT) and the 100 ly edge | `OBJECTS.md` | A game with a Harder computer player; a candidate for the computer-player oracle. |
| Packet limits (32,760 and 16,300 kT), PP terraforming rates, and whether a PP packet reveals the catcher's starbase design | `OBJECTS.md` | Legal packet orders; the last one needs a control. |
| Seed-dependent planet-count distributions | `UNIVERSE.md` | A sampling job over seeds against the model's sampled ranges. |
