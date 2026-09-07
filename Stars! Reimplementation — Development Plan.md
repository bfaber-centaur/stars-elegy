# Stars! Reimplementation — Development Plan

## Goal

Recreate **Stars! J-RC3** closely enough that two players can play a complete game with behavior that is recognizably and measurably faithful to the original.

Longer term:

- preserve a `JRC3` compatibility ruleset;
- add a `JRC3Fixed` ruleset for obvious bugs/exploits;
- eventually experiment with modernized gameplay and UX.

The immediate goal is **not** UI parity, file-format compatibility, AI, or network multiplayer.

The immediate goal is a small, deterministic, well-tested game engine.

---

# 1. Design principles

## Engine first

The simulation must not depend on:

- Wails;
- Svelte;
- a database;
- networking;
- filesystem layout;
- original Stars! file formats.

The engine should be usable from tests or a command-line program with no application shell.

Conceptually:

```text
GameState + PlayerOrders + Ruleset
                |
                v
          GenerateTurn()
                |
                v
NewGameState + PlayerReports
```

## Deterministic simulation

Given:

```text
same state
same orders
same ruleset
same RNG state
```

we should always generate exactly the same next turn.

Randomness belongs explicitly in game state or in a deterministic RNG object passed through turn generation.

This is important for:

- reproducible tests;
- debugging;
- multiplayer hosting;
- save-game integrity;
- differential testing against J-RC3.

## Separate truth from knowledge

The authoritative universe and each player's knowledge of that universe are distinct concepts.

```text
GameState
  ├── actual planets
  ├── actual fleets
  ├── actual players
  └── actual universe state

PlayerIntel
  ├── known planets
  ├── observed fleets
  ├── scanner information
  └── stale observations
```

The eventual UI should receive a `PlayerView`, not unrestricted `GameState`.

## Rulesets are explicit

Avoid scattering legacy compatibility behavior through arbitrary conditionals.

Prefer:

```go
type Ruleset interface {
    ...
}
```

with implementations such as:

```text
JRC3
JRC3Fixed
Modern
```

Exact shape can wait until we know what actually varies.

## Favor data and pure functions

Where practical:

```go
newPlanet := GrowPopulation(oldPlanet, race, rules)
```

is preferable to stateful objects with large method surfaces.

The game's complexity will come primarily from **interaction between systems**, so keeping individual transformations easy to test matters.

---

# 2. Proposed repository structure

Start small rather than prematurely creating every package below.

```text
stars/
├── cmd/
│   └── stars-sim/
│
├── engine/
│   ├── game.go
│   ├── turn.go
│   ├── orders.go
│   ├── player.go
│   ├── race.go
│   ├── planet.go
│   ├── fleet.go
│   └── rules.go
│
├── internal/
│   └── ...
│
├── docs/
│   ├── DEVELOPMENT.md
│   ├── PARITY.md
│   └── REFERENCES.md
│
├── testdata/
│   └── ...
│
├── go.mod
└── README.md
```

Do not create subsystem packages merely because we expect to need them.

Split packages when the code demonstrates a useful boundary.

Eventually we may naturally grow toward:

```text
engine/economy
engine/research
engine/combat
engine/scanning
engine/minefields
engine/ships
```

but there is no need to predict that perfectly now.

---

# 3. Phase 0 — Archaeology and specification

This runs continuously alongside implementation.

Create:

```text
docs/PARITY.md
```

Every mechanic gets tracked as one of:

```text
CONFIRMED
MEASURED
DOCUMENTED
UNKNOWN
LEGACY BUG
INTENTIONALLY DIFFERENT
```

Example:

```text
## Population growth

Status: DOCUMENTED

Known formula:
...

Sources:
...

Tests:
...

Open questions:
...
```

This document becomes the behavioral specification.

Also maintain:

```text
docs/REFERENCES.md
```

for:

- official manual;
- Stars! FAQ;
- J-RC3 documentation;
- patch notes;
- strategy guides containing mechanical information;
- TotalHost;
- starsapi / format documentation;
- craig-stars;
- experimentally measured original behavior.

### Rule

**Do not silently guess mechanics.**

If something is unknown, implement the best current hypothesis but record it explicitly.

---

# 4. Phase 1 — Engine skeleton

## Objective

Prove that we can represent a game and advance turns deterministically.

Initial types probably include:

```go
type Game struct {
    Year    int
    Seed    uint64
    Players []Player
    Planets []Planet
}

type Player struct {
    ID   PlayerID
    Race Race
}

type Planet struct {
    ID       PlanetID
    Position Point
    Owner    *PlayerID

    Population int64
    Minerals   Minerals
}

type PlayerOrders struct {
    PlayerID PlayerID
}
```

Exact numeric types should be chosen deliberately once original ranges and overflow behavior are understood.

## First API

Something approximately like:

```go
func GenerateTurn(
    game Game,
    orders []PlayerOrders,
    rules Ruleset,
) (TurnResult, error)
```

where:

```go
type TurnResult struct {
    Game    Game
    Reports map[PlayerID]PlayerReport
}
```

Do not optimize this API too early.

The first useful implementation can simply:

1. validate orders;
2. advance year;
3. execute economic updates;
4. produce reports.

## Acceptance criteria

- game state can be constructed programmatically;
- one turn can be generated;
- twenty turns can be generated;
- identical inputs produce identical outputs;
- invalid orders fail deterministically;
- tests don't require UI/files/database.

---

# 5. Phase 2 — First vertical slice

This is the first major milestone.

## Goal

Simulate approximately the first 20–30 peaceful turns of Stars!.

Implement only enough systems for:

```text
race
 ↓
homeworld
 ↓
population growth
 ↓
resources
 ↓
factories/mines
 ↓
production queue
 ↓
research
 ↓
technology progress
```

No fleets required initially beyond whatever minimal representation becomes necessary.

## Systems

### Race definition

Start with traits required by economic calculations:

- hab ranges;
- growth rate;
- factory settings;
- mine settings;
- research costs;
- population efficiency.

Primary/lesser racial traits can initially exist as identifiers even if most have no behavior.

### Planet environment

Represent:

- gravity;
- temperature;
- radiation;
- mineral concentrations;
- mineral reserves.

Implement habitability calculation.

### Population

Implement:

- maximum population;
- growth;
- overcrowding behavior;
- hostile-environment penalties;
- deaths if applicable.

### Economy

Implement:

- resource generation;
- factories;
- mines;
- factory construction costs;
- mine construction costs;
- mineral extraction.

### Production queue

Orders should represent player **intent**, not UI operations.

For example:

```go
type QueueOrder struct {
    PlanetID PlanetID
    Items    []QueueItem
}
```

rather than concepts like:

```text
clicked production button
dragged queue item
```

### Research

Implement:

- six research fields;
- tech costs;
- resource allocation;
- level advancement.

## Milestone test

Construct one deterministic race and homeworld.

Run 25 turns with predefined production/research orders.

Assert exact yearly values for:

- population;
- factories;
- mines;
- resources;
- minerals;
- research progress;
- technology levels.

Once we can trust this test, the project has a real simulation kernel.

---

# 6. Phase 3 — Expansion and fleets

Next add the systems that make the map meaningful.

## Galaxy generation

Implement:

- universe dimensions;
- star placement;
- planet environment generation;
- mineral generation;
- homeworld placement.

Generation must use deterministic seeded RNG.

Do not initially reproduce every Stars! galaxy-generation option.

Start with one small-universe configuration.

## Ship components and designs

Represent:

```text
engines
weapons
armor
shields
scanners
fuel tanks
cargo pods
minelayers
special components
```

Then:

```text
ship hull
component slots
ship design
mass
cost
fuel capacity
cargo capacity
```

A component should primarily be data with behavior supplied by systems.

## Fleets

Implement:

- ship stacks;
- coordinates;
- ownership;
- cargo;
- fuel;
- waypoints;
- speed.

## Movement

Implement:

- waypoint orders;
- warp speed;
- travel distance;
- fuel usage;
- engine limitations;
- interception/co-location behavior as discovered.

## Colonization

Implement:

- colonizer components;
- population transport;
- colonization;
- abandoning worlds if applicable.

### Milestone

Two players can:

1. begin on separate homeworlds;
2. build scouts and colonizers;
3. explore;
4. move fleets;
5. colonize new worlds;
6. grow multi-planet economies.

At this point the headless simulation should already feel recognizably like Stars!.

---

# 7. Phase 4 — Information model

Implement scanning before combat becomes complicated.

Systems include:

- planetary scanners;
- ship scanners;
- penetrating vs normal scans;
- fleet detection;
- planet information;
- stale intel;
- ownership discovery;
- design knowledge.

Introduce an explicit:

```go
type PlayerView struct {
    ...
}
```

generated from:

```go
func ViewForPlayer(game Game, player PlayerID) PlayerView
```

Nothing in this result may reveal information the player should not possess.

### Security property

Later multiplayer code must be able to serialize `PlayerView` safely without trusting the frontend to hide secrets.

---

# 8. Phase 5 — Combat

Combat should be implemented as its own deterministic subsystem.

Inputs:

```text
participating fleets
ship designs
battle orders
player relationships
battle location
RNG state
```

Outputs:

```text
survivors
damage
destroyed ships
salvage/debris if applicable
battle report
updated RNG state
```

Build combat using tiny scenarios.

Examples:

```text
1 scout vs 1 scout
10 beam ships vs 10 beam ships
missiles vs shields
different initiative
different battle plans
retreat behavior
```

Avoid validating combat only through full games.

---

# 9. Phase 6 — Remaining major Stars! systems

Add roughly in this order, unless dependencies suggest otherwise:

1. starbases;
2. battle plans;
3. minefields;
4. minelaying/minesweeping;
5. terraforming;
6. mineral packets;
7. remote mining;
8. bombing/invasion;
9. cloaking;
10. gates;
11. racial-trait mechanics;
12. diplomacy/player relations;
13. mystery trader/random events;
14. wormholes and lower-priority special mechanics.

Each subsystem should get:

```text
mechanical spec
unit tests
turn integration tests
parity status
```

before moving on.

---

# 10. Differential testing against original Stars!

Once original save/turn-file inspection is practical, start constructing oracle tests.

Example scenario:

```text
J-RC3:
Year 2400
Race X
Planet Y
Population Z
Factories A
Mines B
Queue C

Generate one turn.
```

Extract result.

Then construct identical state in our engine.

Compare:

```text
population
resources
minerals
tech
fleet positions
fuel
battle results
scanner results
etc.
```

Store scenarios under:

```text
testdata/jrc3/
```

Eventually:

```text
testdata/jrc3/pop_growth_001/
testdata/jrc3/fuel_007/
testdata/jrc3/minefield_012/
testdata/jrc3/combat_beams_004/
```

These become regression fixtures.

This is where `PARITY.md` progresses from documentation toward empirical specification.

---

# 11. Persistence

Delay choosing the real save format.

Initially tests and CLI can create state directly.

When persistence becomes useful, define serialization around our own model rather than reproducing Stars!' binary structure.

Likely requirements:

- deterministic;
- versioned;
- inspectable during development;
- migration-capable.

JSON is perfectly acceptable for early development.

Long term we can decide between:

```text
JSON
SQLite
protobuf
custom binary format
```

based on actual requirements.

Original Stars! formats should be treated as **import/export compatibility**, not our native domain model.

---

# 12. CLI development tool

Before any GUI, create:

```text
cmd/stars-sim
```

Useful commands might eventually include:

```text
stars-sim new
stars-sim turn
stars-sim inspect
stars-sim run --turns 100
stars-sim scenario
```

The CLI is not the product.

It is our engine workbench.

Especially useful capabilities:

```text
dump state
run N turns
seed RNG
load scenario
apply orders
print reports
```

This gives us excellent tooling before Wails enters the repository.

---

# 13. UI phase

Only begin this when the simulation is already useful headlessly.

Current intended stack:

```text
Wails v2
Svelte
TypeScript
HTML/CSS
SVG galaxy map initially
```

Possible escalation:

```text
SVG → Konva
```

if map interaction becomes cumbersome.

UI communicates through an application layer:

```text
Svelte
   |
   v
Go application service
   |
   v
engine
```

Avoid binding arbitrary engine internals directly into Wails.

Commands:

```text
SetProductionQueue
SetFleetWaypoint
SetResearchAllocation
EndTurn
```

Queries:

```text
GetPlanet
GetFleet
GetGalaxyView
GetResearchStatus
```

This boundary also prepares us for eventual network multiplayer.

---

# 14. Multiplayer

Do not build networking into turn simulation.

Eventually:

```text
               authoritative host
                       |
                  GameState
                 /    |    \
                /     |     \
        PlayerView PlayerView PlayerView
```

Players submit:

```text
PlayerOrders
```

Host calls:

```text
GenerateTurn()
```

This maps naturally to Stars!' original PBEM model without requiring original file formats.

Potential delivery models can wait:

- local hotseat;
- local host + clients;
- HTTP server;
- hosted web service;
- PBEM-like file exchange.

---

# 15. Testing strategy

Use several layers.

## Unit tests

For formulas:

```text
habitability
population
resources
fuel
research costs
weapon damage
mine damage
```

## System tests

For subsystem interactions:

```text
production queue
fleet movement
scanner detection
combat
colonization
```

## Turn tests

Given:

```text
state + orders
```

assert:

```text
next state
```

## Scenario tests

Run tens or hundreds of turns with fixed seed and orders.

Assert important checkpoints.

## J-RC3 parity tests

Original executable serves as behavioral oracle wherever feasible.

---

# 16. Development discipline

Every meaningful mechanic should ideally arrive as:

```text
1. document expected behavior
2. write focused test
3. implement behavior
4. integrate into turn generation
5. update PARITY.md
```

Not every change needs ceremonial TDD, but mechanics should not exist solely because "the implementation looked plausible."

For uncertain original behavior:

```text
hypothesis → experiment → fixture → implementation
```

---

# 17. Explicit non-goals for early development

Do not spend early effort on:

- graphical UI;
- pixel-perfect original UI;
- AI opponents;
- sound;
- original artwork;
- networking;
- account systems;
- matchmaking;
- original file-format writing;
- installers;
- Steam;
- mobile;
- localization;
- mod support;
- balance improvements.

Those can all become reasonable projects later.

---

# 18. Version milestones

## v0.0.1 — Turn engine exists

- game state;
- race;
- planet;
- deterministic turn generation;
- tests.

## v0.0.2 — Peaceful economy

- population;
- habitability;
- factories;
- mines;
- minerals;
- production;
- research.

Can simulate a homeworld for decades.

## v0.0.3 — Expansion

- galaxy generation;
- ships;
- fleets;
- movement;
- fuel;
- colonization.

Two players can expand across a galaxy.

## v0.0.4 — Fog of war

- scanners;
- intel;
- `PlayerView`.

Players no longer possess omniscient state.

## v0.0.5 — War

- combat;
- starbases;
- battle plans;
- bombing/invasion.

A player can meaningfully defeat another.

## v0.0.6 — Core Stars! systems

- minefields;
- terraforming;
- packets;
- gates;
- racial mechanics;
- remaining major economy/fleet mechanics.

## v0.1.0-alpha — Headless Stars!

A complete multiplayer game can be played through structured orders / developer tooling.

No graphical UI required.

## v0.2.0 — Desktop playable

- Wails;
- Svelte;
- galaxy map;
- planet/fleet controls;
- ship designer;
- production;
- research;
- turn submission.

## v0.x — J-RC3 parity push

Differential tests and edge-case fixes.

## v1.0 — Faithful modern Stars!

Complete game, usable desktop UI, stable saves, J-RC3-compatible ruleset behavior within documented scope.

---

# 19. First implementation sprint

The first coding session should stay deliberately tiny.

### Step 1

Initialize:

```text
go.mod
README.md
docs/DEVELOPMENT.md
docs/PARITY.md
```

### Step 2

Define:

```go
Game
Player
Race
Planet
PlayerOrders
Ruleset
```

only with fields required by the first experiment.

### Step 3

Implement:

```go
GenerateTurn()
```

that advances the year.

Test it.

### Step 4

Implement population growth for one owned planet.

Test several known cases.

### Step 5

Run a 20-turn scenario.

Something like:

```go
func TestHomeworldTwentyTurns(t *testing.T)
```

with deterministic expected population values.

### Step 6

Add resources/factories/mines one subsystem at a time.

The first meaningful project checkpoint is:

> **We can describe a race and homeworld in Go, run twenty deterministic Stars!-like economic turns, and explain every number produced.**

Everything else grows outward from that.