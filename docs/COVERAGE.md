# Coverage of the original game by the public specs

A map from what the original J-RC3 host does each year (and what its
client shows) to the spec files here. Its job is to show what is still
missing. It lists behaviors, not code. The mapping comes from a white-box
walk of the original program's turn generation, order replay and
computer-player code (private `stars-decomp`), checked against these files
on `main` as of 2026-10-07 and the open spec pull requests named below.

Levels:
- **Confirmed**: specified, mostly CONFIRMED.
- **Read**: specified, mostly BINARY-ONLY.
- **Partial**: specified, but some behaviors are missing.
- **Missing**: no spec.
- **In progress**: a lane owns it and a pull request is open.

## By part of the year

| Behavior | Spec | Level | What is missing |
|---|---|---|---|
| Accepting and replaying orders, random player order, serial checks | `ORDERS.md` | Partial | Validation and fleet operations are covered. Production-queue replace and the setting orders are in `LIMITS.md` (queue replace CONFIRMED LQ-1..LQ-6; setting orders BINARY-ONLY), to be folded into `ORDERS.md`. |
| Race checks at the start of the year | `KERNEL.md`, RACES.md (#49) | In progress | |
| Tasks before movement: unload, scrap, colonize, drops, load, merge, cargo to other players | `TAKEOVER.md`, `ORDERS.md` | Confirmed | Scrap and transfer details are Read. |
| Packets, wormholes, Mystery Trader | `OBJECTS.md` | In progress | Wormholes and the Trader are owned by the objects and races lane. Packet launch is Read. |
| Fleet movement, fuel, chasing, stargates | `KERNEL.md`, `OBJECTS.md` | Confirmed | |
| Minefields | `OBJECTS.md` | Confirmed | MF-1..12 held in 33 of 35 cases (#47). Open: whether the 512th field depends on object order, the 4050-object limit, SS and SD safe-warp bonuses. |
| Colonists breeding inside fleets (one primary trait) | none | Missing | How carried colonists grow, and where the overflow goes. |
| Mining, resources, research tax, production queues, terraform items | `KERNEL.md`, `PARITY.md` PQ | Confirmed | |
| Ships and starbases leaving production | none | Missing | Where built ships go: one new fleet per build, its number and name, full fuel, the per-player fleet limit and what happens at it, routing to the planet's route destination with the warp chosen, a new fleet's default orders, what replacing or upgrading a starbase does to the old one. |
| Population growth | `KERNEL.md` | Confirmed | |
| Research and tech progression | `KERNEL.md` | In progress | Owned by the KERNEL experiments lane. |
| Random events: meteors, climate change, new minerals, Trader arrival | `KERNEL.md` (#44), `OBJECTS.md` | Confirmed (#44) | KX-004. Check that #44 states meteors and climate change also clear the non-automatic items from a planet's queue. |
| Battles | `COMBAT.md` | Confirmed | |
| Bombing, invasion, colonization, capture | `TAKEOVER.md` | Confirmed | |
| Tasks after movement: remote mining, laying mines, patrol, route, transfer fleet | `KERNEL.md`, `OBJECTS.md`, `SCANNING.md`, `TAKEOVER.md` | Read / Partial | The route task is missing. Patrol target choice is Read. Two transfer-fleet refusals are missing: a computer player never receives a fleet, and a recipient that treats the giver as an enemy refuses. |
| Waypoint upkeep | `KERNEL.md`, `SCANNING.md` | Partial | Repeat orders (reached waypoints move to the end of the list), when a reached waypoint is dropped, waypoints whose target was destroyed or captured. |
| Sweeping, repair | `OBJECTS.md`, `COMBAT.md` | Confirmed | |
| Claim Adjuster and orbital-adjuster terraforming | `KERNEL.md` | In progress | Owned by the KERNEL experiments lane. Currently one paragraph, Read. |
| Duplicate-serial penalties | `KERNEL.md` | Read | |
| What each player knows; estimates | `SCANNING.md` | Confirmed / Read | |
| Scores and victory | `KERNEL.md` (#44) | In progress | |
| New games | `UNIVERSE.md` | Confirmed | |
| Messages to players | none | Missing | About 400 kinds of message. Which event sends which message, to which players, with which values. Battle reports are covered (`COMBAT.md`, battle record); the messages around them are not. Player-to-player mail is not covered either. |
| Computer players | `AI.md` (shared core), `UNIVERSE.md` (starting setup) | In progress | Shared core specified (built-in races, research, starbase designs CONFIRMED; planet automation BINARY-ONLY). Missing: each personality's own turn (docs/ai/). The original's computer players act only through ordinary orders, written by the host before it generates the year. Special rules for computer players inside the year are scattered and mostly missing: no fleet gifts to them, and automatic trading with the Mystery Trader. |
| What the client shows: production completion estimates, arrival estimates, fuel and research estimates, planet value, report history | `ESTIMATES.md`, `SCANNING.md` ("Old reports") | Confirmed | ES-001 matched 149 of 149 readings; ES-002 confirmed stargate legs, "Skipped", Generalized Research, "Maxed Out" and the distance display. |
| Limits: fleets, space objects, minefields, designs, queue length | `LIMITS.md` | Partial | Collected in `LIMITS.md`. Client queue limits CONFIRMED (LQ). Open: the 4050-object limit (not run), waypoints per fleet, the host's 16th battle plan and other crafted-order cases (serial-gated). |

## Largest gaps for a playable game

1. **Computer players.** This is the largest body of the original's code
   with no spec: about an eighth of it. Single-player games need it.
   Before any work starts, the project must decide whether to reproduce
   the original personalities or write Elegy's own and mark the
   difference INTENTIONALLY DIFFERENT. The in-year special rules for
   computer players need a spec either way.
2. **Ships and starbases leaving production.** This happens every year
   for every player. It is already read privately, so a spec section and
   a small oracle corpus would close it.
3. **Waypoint upkeep and the remaining tasks:** repeat orders, dropped
   waypoints, dead targets, the route and patrol tasks, transfer-fleet
   refusals. Every multi-waypoint order depends on these. Mostly read
   privately.
4. **Messages.** They are the player's only account of the year.
5. **Client estimates:** production schedules, arrival years, fuel and
   research estimates. Now specified in `ESTIMATES.md` (CONFIRMED, ES-001
   and ES-002).

After those: colonists breeding inside fleets, packet launch, patrol
targets, and a single list of limits. Not ranked, because a lane already
owns them: research and terraforming, random events (CONFIRMED in #44),
scores and victory, race design, wormholes and the Mystery Trader.
