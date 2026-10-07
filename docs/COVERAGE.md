# Coverage of the original game by the public specs

A map from what the original J-RC3 host does each year (and what its
client shows) to the spec files here. Its job is to show what is still
missing. It lists behaviors, not code. The mapping comes from a white-box
walk of the original program's turn generation, order replay and
computer-player code (private `stars-decomp`), checked against these files
on `main` and the open spec changes as of 2026-10-07 (evening). A spec
file named here that is not on `main` yet arrives with its open change:
`RACES.md`, `MESSAGES.md`, `AI.md` and `PRODUCTION-LAUNCH.md`.

Levels:
- **Confirmed**: specified, mostly CONFIRMED.
- **Read**: specified, mostly BINARY-ONLY.
- **Partial**: specified, but some behaviors are missing.
- **Missing**: no spec.
- **In progress**: a lane owns it and a pull request is open.

## By part of the year

| Behavior | Spec | Level | What is missing |
|---|---|---|---|
| Accepting and replaying orders, random player order, serial checks | `ORDERS.md`, `KERNEL.md` | Partial | Validation, ownership, fleet operations and design legality are covered. Nothing states the effects of the plain setting orders (research settings, relations, planet flags, renames), or that replacing a production queue keeps the progress of matching items. |
| Race checks at the start of the year | `RACES.md`, `KERNEL.md` "Item costs" | Confirmed | Advantage points and the degrading of an over-budget race. |
| Tasks before movement: unload, scrap, colonize, drops, load, merge, cargo to other players | `TAKEOVER.md`, `ORDERS.md` | Confirmed | Scrap and transfer details are Read. |
| Packets, wormholes, Mystery Trader | `OBJECTS.md`, `KERNEL.md` "Random events" | Confirmed / Read | Wormholes (WT), the Trader's appearance, movement, meeting and rewards. Packet launch is Read. |
| Fleet movement, fuel, chasing, stargates | `KERNEL.md`, `OBJECTS.md` | Confirmed | Stargates (GT corpus) and the chain-freeze LEGACY BUG included. |
| Minefields | `OBJECTS.md` | Confirmed | MF-1..MF-13. Open: the 4050-object limit, SS and SD safe-warp bonuses. |
| Colonists breeding inside fleets (one primary trait) | `KERNEL.md` | Confirmed | OT-5. The case where a fleet breeds 0 and a random draw gives 1 is Read. |
| Mining, resources, research tax, production queues, terraform items | `KERNEL.md`, `PARITY.md` PQ | Confirmed | |
| Ships and starbases leaving production | `PRODUCTION-LAUNCH.md` | Confirmed | SL-01..SL-12. The same-hull replacement cost and the research share of an unbuilt ship are Read. |
| Population growth | `KERNEL.md` | Confirmed | |
| Research and tech progression | `KERNEL.md` "Research" | Confirmed | KX-005. |
| Random events: meteors, climate change, new minerals, Trader arrival | `KERNEL.md` "Random events", `OBJECTS.md` | Confirmed | KX-004. |
| Battles, battle plans | `COMBAT.md` | Confirmed | Battle movement confirmed by exact replays. |
| Bombing, invasion, colonization, capture | `TAKEOVER.md` | Confirmed | |
| Tasks after movement: remote mining, laying mines, patrol, route, transfer fleet | `KERNEL.md`, `OBJECTS.md`, `ORDERS.md`, `SCANNING.md`, `TAKEOVER.md` | Read / Partial | Route, patrol and transfer-fleet rules (with the computer-player and enemy refusals) are in `ORDERS.md`, mostly Read and waiting on the WU batch. |
| Waypoint upkeep | `ORDERS.md` "Waypoint upkeep and the remaining tasks", `SCANNING.md` | Read | Repeat orders, reached and dropped waypoints, targets that moved, died or were captured. Waiting on the WU batch. |
| Sweeping, repair | `OBJECTS.md`, `COMBAT.md` | Confirmed | |
| Claim Adjuster and orbital-adjuster terraforming | `KERNEL.md` "Terraforming" | Confirmed | KX-005, OT-4. |
| Duplicate-serial penalties | `KERNEL.md`, `MESSAGES.md` | Read | |
| What each player knows | `SCANNING.md` | Confirmed | |
| Scores and victory | `KERNEL.md` "Scores and victory conditions" | Confirmed / Read | Score KX-003; the victory conditions are Read. |
| New games | `UNIVERSE.md`, `RACES.md` | Confirmed | |
| Messages to players | `MESSAGES.md` | Confirmed / Read | All 387 kinds are catalogued (sender, recipients, values, phase); 198 rows are CONFIRMED. The rest are listed under "Kinds not yet observed, and how to reach them" and as gap 4 below. Player-to-player mail is not covered. |
| Computer players | `AI.md` (shared core), `UNIVERSE.md` (starting setup) | In progress | Shared core specified (built-in races, research and starbase designs CONFIRMED; planet automation Read). Each personality's own turn is in progress (`docs/ai/`). Special rules for computer players inside the year are scattered: no fleet gifts to them (`ORDERS.md`), automatic trading with the Mystery Trader (`OBJECTS.md`). |
| What the client shows: production completion estimates, arrival estimates, fuel and research estimates, planet value, report history | `ESTIMATES.md`, `SCANNING.md` ("Old reports") | Confirmed | ES-001 matched 149 of 149 readings; ES-002 confirmed stargate legs, "Skipped", Generalized Research, "Maxed Out" and the distance display. |
| Limits: fleets, space objects, minefields, designs, queue length | `PRODUCTION-LAUNCH.md` (fleets), `OBJECTS.md` (minefields and objects) | Partial | Fleets (512) and minefields (512, or 511) are CONFIRMED or MEASURED. Design-slot and queue limits are not collected anywhere. |

## Largest gaps for a playable game

1. **Computer players' own turns.** Bobby chose to reproduce the original
   personalities. The shared core is in `AI.md`; each personality's turn
   is being read (`docs/ai/`), with predictions checked against captured
   computer-player orders.
2. **Waypoint upkeep and the remaining tasks:** specified in `ORDERS.md`
   (Read); the WU batch will confirm it. Every multi-waypoint order
   depends on these.
3. **The plain setting orders** (research settings, relations, planet
   flags, renames) and the production-queue replacement rule: nothing
   states them.
4. **Messages not yet observed** (`MESSAGES.md`, "Kinds not yet observed,
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
5. **A single list of limits:** design slots, queue length, space objects.

Not ranked, because a lane already owns them or they are covered:
research and terraforming, random events, scores and victory, race
design, wormholes and the Mystery Trader, stargates, ships leaving
production, battle plans and client estimates.
