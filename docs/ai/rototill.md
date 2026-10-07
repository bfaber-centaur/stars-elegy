# Rototill (CA computer player)

Rototill is the computer player of definition-file type 4, with the CA
race of `../AI.md` §3. This file specifies its own turn. The shared
rules it calls (research, starbase designs, hubs, planet automation,
scrap orders and the fleet rules) are in `../AI.md` and are named here by
section.

Status: the turn below is MEASURED (cases AI-14 to AI-17 in
`../PARITY.md`). A replay of these rules agrees with every Rototill
player-year in four captured games: AIX (expert, 2400–2460) and the
stage-1 games AI02 (easy), AI03 (standard) and AI04 (harder), 166
player-years in all. Branches no corpus reached are marked *not
exercised* and are BINARY-ONLY.

Notation: `y` = year index; slot `k` = own ship design slot; `n(k)` =
ships of design `k` alive. "Terraformed habitability" is the planet's
habitability value for the race after the terraforming the player could
currently do (as opposed to its present value). Engines are compared by
their place in the engine list (Settler's Delight, Quick Jump 5, Fuel
Mizer, Long Hump 6, …).

CA's starting designs (`../UNIVERSE.md` sets them up): slot 0 Scout,
slot 1 Colony Ship, slot 2 Midget Miner. The Scout and the Colony Ship
both use the Long Hump 6.

## 1. Turn order

1. Research (`../AI.md` §4: no plan; 0% before year index 20, then 15%,
   lowest field), starbase designs (§5) and hubs (§6).
2. **No ship designs.** Rototill never creates, deletes, ages, splits or
   merges ship designs. It plays the whole game with its three starting
   designs (MEASURED, AI-14: no ship design order from a Rototill player
   in 166 player-years; its only design orders are starbase designs).
3. Count `U`: planets unowned in Rototill's own view (`../AI.md` §1)
   that its file records at knowledge level 3 or more and whose
   terraformed habitability is above 0.
4. Planet loop and production (§2).
5. Fleet pass 1, then fleet pass 2 (§3).
6. Planet automation (`../AI.md` §7) and the production queue fill. CA
   cannot build terraforming items, so the automation's terraforming step
   adds nothing.

Rototill sets no armada parameters (`../AI.md` §11) and reads none.

## 2. Planet loop and production (MEASURED, AI-15)

Every planet in Rototill's view, in planet-id order (not the shuffled
order of `../AI.md` §2):

- **Another player's planet:** gets a destination score of 1, or 2 if it
  has a starbase (used by the armada-destination fallbacks in §3), and a
  "habitable for me" mark when its terraformed habitability is above 0
  (used by the invasion rule in §3).
- **Unowned planet known at level 3 or more:** gets a mineral score, the
  sum over the three minerals of (concentration / 2, integer, or 75 when
  the concentration is above 66), at most 127 (used only by the
  remote-miner rule in §3).
- **Own planet with negative desirability:** flagged for planet
  automation and skipped.
- **Production.** A planet qualifies when it is Rototill's own (with
  desirability not negative), has a starbase and at least 100,000
  colonists, and its queue holds no starbase design other than starbase
  slot 0. As written, an unowned planet with a starbase and 100,000
  colonists would also qualify; Rototill's view cannot contain one.
  The first qualifying planet of the year appends one Colony Ship
  (design 1) to its queue when `n(1) = 0` or `n(1) + 1 < U`. At most one
  is added per year. In year index 0 nothing is queued.

AIX and AI02 show three such colony ships (AIX 2444 and 2446, AI02 2414)
and 108 qualifying planet-years with nothing queued. *Not exercised:* the
`n(1) + 1 < U` branch (`U` was at most 2) and the starbase-item block.
Changing the threshold to 20,000 colonists breaks 2 rows. Dropping the
`U` test breaks 108 rows.

Rototill's queue change and the shared queue changes later in the turn
to the same planet are one queue order when nothing else is ordered in
between, and two otherwise (`../ORDERS.md` describes the queue order).

## 3. Fleets (MEASURED, AI-16, AI-17)

### Pass 1: every fleet, in fleet order

- Another player's fleet goes on the enemy list. An own fleet holding a
  ship of a Scout or warship hull goes on the attack list. Both lists are
  built by prepending, as in Robotoid.
- **Remote miners** (ships of slots 7 or 8; *not exercised*, Rototill
  never has them): in flight with at least two waypoints, their
  waypoint-1 target is marked taken; orbiting an unowned planet, that
  planet is marked taken; orbiting an owned planet, the route is cut to
  waypoint 0 and its task cleared.
- **Transports** (`../AI.md` §11 "Fleet classes") **and fleets with
  Colony Ships:** the planet is waypoint 1's target when the fleet has at
  least two waypoints (none if that target is not a planet), else the
  orbited planet. When that planet belongs to another player:
  - if it is marked habitable for me, the fleet carries colonists and the
    owner is not AR, the waypoint at that planet (waypoint 0 if it names
    the planet, else waypoint 1) becomes a transport waypoint at the
    planet with the order "unload all colonists" (an invasion);
  - otherwise the route is cut to waypoint 0 and its task cleared.
  A transport whose planet is absent from Rototill's view is cut; a
  colonizer is left alone.

AIX: a colony ship whose target was taken by another player in 2455
received the unload order at that planet in 2455 and had its route cut
in 2456.

### Pass 2: own fleets

- **Remote miners** (*not exercised*): orbiting a planet with mineral
  score below 4, they pick a destination by score. Each planet with a
  score above 0 costs one `Random(100)`, and a planet already marked
  taken is accepted only on a draw below 25, after which it outranks the
  others. The order is a move with task remote mining, warp 6, appended.
- Fleets with two or more waypoints: no order.
- Idle fleets, first match:
  1. **Colony Ship fleet.** If it orbits an own planet with at least
     5,000 colonists, or carries colonists:
     - At an own planet it loads 2,500 colonists (`../AI.md` §11
       "Supplies"), whether or not a target is found.
     - Target: the nearest colonizable planet (`../AI.md` §11 "Nearest
       colonizable planet"; Rototill uses habitability marks). The
       wormhole alternative applies only when the Colony Ship's engine
       is later in the list than Quick Jump 5. The chosen planet is
       marked so later fleets this turn skip it.
     - Planet → colonize order; wormhole → wormhole order; neither → no
       order.

     Otherwise (no colonists, not at an own planet with 5,000):
     - at an own planet with a starbase: no order;
     - with an engine of Fuel Mizer or later: go to the nearest own
       starbase (`../AI.md` §11), task none, warp 4;
     - else, or with no own starbase planet in range: scrap (`../AI.md`
       §8).
  2. **Transport** (*not exercised*): the shared hub-freighter rule
     (`../AI.md` §11 "Hub freighters") from the hub that lists the fleet,
     else from the lowest-id own planet with a starbase. With no own
     starbase planet, pass 2 stops here for every later fleet (LEGACY
     BUG).
  3. **Ships of slots 13 or 14** (*not exercised*): at an own starbase
     planet with fewer than two of each, stay; otherwise move (task none,
     warp 4) to the best-scoring armada destination.
  4. **Scout** (slot 0):
     - with a Quick Jump 5 engine and less than 2 mg of fuel: scrap
       (*not exercised*);
     - unarmed (CA's Scout): the nearest planet Rototill has never seen
       (absent from both its turn file and its history file) that no
       other own fleet's waypoint 1 targets. If it orbits a planet,
       `Random(100) < 5` lets a wormhole within that distance win
       instead. With no such planet and no wormhole: the best armada
       destination counted from the homeworld, else `Random(planet
       count)`. Move order, task none, warp = ideal warp. The planet is
       marked taken;
     - armed scouts use the shared attack-target rule (not reachable for
       CA).
  5. **Anything else** (CA's Midget Miner): no orders.

The waypoint warps above are then re-picked by the shared warp rule
(`../AI.md` §11 "Warp choice").

Measured fleet rows: 98 idle colony-ship years (4 colonize orders, 2
wormhole orders, 92 with no target), 75 scout moves (every target a
never-seen planet; 10 with a wormhole among the outcomes), 1 invasion
unload, 1 route cut, 1 move home, 297 fleets left alone, and 166 of 166
years of colonist loads. Discriminating variants: ignoring habitability
in the colonizable-planet search breaks 89 colony-ship rows; using
present instead of terraformed habitability breaks 1; counting planets
known only from the history file as never seen breaks 31 scout and 2
colony-ship rows.

In practice Rototill's scout moves outward one never-seen planet at a
time; its colony ship loads colonists and waits at home until some known
planet becomes habitable after terraforming; it builds a new colony ship
only when none is alive. In AIX it held one planet for most of 61 years.

## 4. Legacy behaviour

Reproduced as written (LEGACY BUG unless noted):

- **Miner slots.** The remote-miner rules look for slots 7 and 8, but
  CA's Midget Miner is slot 2, so the starting miner stays at the
  homeworld all game (observed in all four corpora).
- **Queue test.** Production skips a planet with a starbase design of
  slot 1 or higher queued, not one with a ship queued (Robotoid's test).
  A queued, unbuilt colony ship therefore does not stop another the next
  year while `n(1)` is still 0 (not observed: each was built within a
  year).
- **Transport stop.** See pass 2 step 2.
- **Unset values** (BINARY-ONLY, unreachable for CA): a slot-13/14 fleet
  in space measures its destination from a planet only an earlier
  transport in the same pass sets; a remote miner in flight treats its
  waypoint-1 target as a planet without checking its type; the remote
  miner's "not its own planet" test never excludes anything.
- **Stray waypoint words.** The move home of pass 2 step 1 writes a
  waypoint whose transport words are not cleared, so the order file
  carries arbitrary values there (AIX 2456). The task is none, so they
  have no effect. INTENTIONALLY DIFFERENT: Elegy writes zeros.
- **Design slots read without a presence check.** Rototill reads the
  engines of slots 0 and 1 and `n(1)` without checking that the slots
  hold designs (`../AI.md` §1 "State leaking between computer players").
  It never deletes its starting designs, so this cannot matter in normal
  play.

## Open experiments

- Branches no corpus reached: the `n(1) + 1 < U` colony ship, the
  starbase-item block, both scrap rules and the scout fallbacks. A game
  with a richer habitable set for CA, or edited fuel and engines, would
  reach them.
- What knowledge level 3 means in `../SCANNING.md` terms.
