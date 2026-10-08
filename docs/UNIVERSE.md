# Universe generation specification: new games

Behavioral specification of how J-RC3 builds a new game: the galaxy's
planets, the homeworlds, each player's starting state, and the objects that
exist in year 2400. It is written for an implementer working only from this
public repository. It describes what a new game contains and the rules that
shape it, not how any file encodes it.

`PARITY.md`, section "Universe generation", holds the experiment records
(UG01 to UG21, built from game definition files with
`tools/fleetlab/new-game`). This file restates them as rules and adds rules
that so far come only from white-box analysis of the original program
(private `stars-decomp`, promoted here as behavior only).

Rules this file relies on but does not restate: habitability (`KERNEL.md`
"Habitability"), part and hull statistics and race restrictions on parts
(`COMPONENTS.md`, `data/components.json`), and wormhole stability, movement
and placement badness (`OBJECTS.md` "Wormholes").

## Status of each rule

- **CONFIRMED**: a white-box reading agrees with original-game oracle
  observations. The UG games were compared with a whole predicted game,
  field by field (every planet's position, name, environment,
  concentrations and artifact flag, owners, homeworlds, tech, designs,
  fleets, wormholes), and all 30 (UG01–UG30) matched exactly. A rule is CONFIRMED when
  that comparison exercised it; case ids are given where useful.
- **MEASURED**: observed, but in one case only or without a full model
  check.
- **BINARY-ONLY**: read from the original program, with no oracle
  observation yet. Listed again under Open experiments.
- **LEGACY BUG**: looks like an accident of the original implementation.
  Implement it for parity, isolated so it can be switched off.

"Confirmed" covers the measured scope: every size, density and
player-position setting, 2 to 16 players, all ten primary racial traits
(six as computer players, WM, SD, IT, JOAT and PP as race files), all five
leftover-point spends, and the max-minerals, BBS, clumping and
no-random-events options.

## Conventions

- `W` is the galaxy width in light years: `(size + 1) · 400` for size 0
  (tiny) to 4 (huge). Coordinates run from 1000 to `1000 + W` on both axes.
- `d²` is `dx² + dy²`. Divisions truncate.
- `rand(n)` is a uniform integer in `0..n−1`.
- Environment values are on the 0–100 click scale used by `KERNEL.md`
  (axes in order gravity, temperature, radiation); minerals in order
  ironium, boranium, germanium.

## Settings that shape a new game

| Setting | Values |
|---|---|
| universe size | tiny, small, medium, large, huge (0–4) |
| density | sparse, normal, dense, packed (0–3) |
| player positions | close, moderate, farther, distant (0–3) |
| players | 1 to 16, each a race or a computer player (type and level) |
| options | maximum minerals, slower tech advances, accelerated BBS play, no random events, computer players form alliances, public player scores, galaxy clumping |

Slower tech, computer alliances and public scores change nothing at
creation but the option word (CONFIRMED, UG26–UG28: each is UG01's galaxy,
planet for planet). Their later effects belong to other specs.

## Randomness and seeds (CONFIRMED)

- The original builds a game from one random stream. A definition file
  can give a seed; then the same file gives the same game every time, at
  any emulator speed (UG01 at two speeds). Only the low 12 bits of the
  seed matter, so seeds equal modulo 4096 give the same game (UG11, UG14),
  and a few further seeds collide (0 and 64, UG12/UG13). Without a seed the
  game depends on the startup clock.
- Elegy does not need to reproduce the original's random stream. It needs
  the rules and distributions below. A seeded, deterministic generator is
  the natural Elegy equivalent of the definition-file seed.

## Planets

### Count (CONFIRMED)

1. Nominal count `N = W²/5000`; then `N += (N/4)·(density − 1)`; for
   packed, `N += N/4` again; at most 999.
2. The generator places `M = min(999, N + N/7)` candidate points, each
   uniform with `x, y ∈ 1010 .. 1010 + W − 20`.
3. **Minimum spacing** (CONFIRMED, UG01..UG21). The candidates are sorted by `x`.
   Taking each surviving candidate in that order, every later candidate
   within `d² ≤ 144` (12 ly) of it is removed. A removed candidate removes
   nothing, so the later member of each too-close pair goes. No two
   surviving planets are within 12 ly. (The original's sort is not stable
   for equal `x`; which of two equal-`x` candidates comes first is not
   specified here.)
4. Further candidates are removed at random until `N` remain. When the
   spacing pass already removed more than `M − N`, fewer than `N` remain,
   and no candidate is added back.

| size | sparse | normal | dense | packed |
|---|---|---|---|---|
| tiny | 24 | 32 | 40 | 60 |
| small | 96 | 128 | 160 | 240 |
| medium | 216 | 288 | 360 | 540 |
| large | 384 | 512 | 640 | at most 960, seed-dependent (912 in UG04, 900 in UG25) |
| huge | 600 | 800 | at most 999, seed-dependent (940 in UG05) | as dense |

In large packed and huge dense or packed games the count depends on the
seed (CONFIRMED for two seeds each of large packed, UG04 and UG25, and
huge dense, UG05 and UG15). Over 316 sampled streams of the model it
ranged 899–940 for large packed and 930–962 for huge dense or packed
(the ranges BINARY-ONLY). Huge dense and huge packed
are the same galaxy for the same seed (UG05, UG15).

The other cells are the usual count, but the rule in step 4 can also put
them below `N` (CONFIRMED: tiny packed 57 and 59, UG22 and UG23; small
packed 239, UG24; the rates below are 3,000 uniform samples of the
model's steps 2–3 per cell, BINARY-ONLY).
Tiny packed came out 54–60, below 60 in about 13% of games. Tiny dense
came out 36–40, below 40 in about 4%. Small packed came out 235–240, below
240 in about 1%. Medium packed came out 531–540, below 540 in about 0.1%.
None of the UG games hit this (UG runs were not tiny or small packed).

### Clumping option (CONFIRMED, UG04, UG10)

After placement, `N` times: pick a random planet `a`; find its nearest
other planet `b` (`d²`). If `d² > 144`, move `a` toward `b`, per axis:

| `d²` | new position of `a` |
|---|---|
| ≥ 1601 | `(a + 2b)/3` |
| 626–1600 | `(a + b)/2` |
| 325–625 | `(2a + b)/3` |
| 145–324 | `(4a + b)/5` |

Clumping can bring planets closer than the 12 ly minimum spacing.

### Names (CONFIRMED, UG01..UG21)

Every planet gets a distinct name index from the original's 999-name
list: a uniform index, stepped to the next unused one. The name texts are
original game data and are not reproduced here.

### Environment (CONFIRMED)

Per planet:

- gravity `1 + rand(90) + rand(10)` (1–99, peaked in the middle);
  temperature the same; radiation `1 + rand(99)` (uniform 1–99).
- With random events on, an artifact with probability 1/3. No artifact
  with random events off (UG08, UG09).

### Mineral concentrations (CONFIRMED)

Per mineral:

1. `c = 31 + rand(45) + rand(45)` (31–119).
2. On a planet with radiation above 89: `c += rand(99 − c)/2` when
   `c < 99`, else unchanged.
3. BBS option: `c < 40` gains 5.

Then per planet, low overrides: `r = rand(27)`. For `r < 9`, some minerals
are set to `1 + rand(30)`: 4 times for `r = 0`, 3 times for `r = 1–2`, 2
times for `r = 3–6`, once for `r = 7–8`, each time on a random mineral (so
the same mineral can be hit twice). For `9 ≤ r < 18`, once. Otherwise
none.

**Maximum minerals**: every concentration is 100 and no overrides apply
(UG02, UG09). Homeworlds start from planet 0's concentrations (below), so
also 100, and then take any concentration boost from their spend. In UG02
the human player (minerals spend) had 100/100/100. The harder computer
player (concentrations spend, `L = 50`) had 138/113/113: +25 on the first
lowest, then +13 on all.

Surface minerals are 0 on every planet that is not a homeworld or second
planet.

## Homeworld placement (CONFIRMED)

`P` players, player-positions setting `s` (0–3):

- `a = W²/P − 6W`; if negative, 0, else `a·9/10`.
- `v = 6W + s·a/3`. Homeworlds must be at least `d² ≥ 9v/10` from every
  other homeworld, and each new homeworld within `d² ≤ 7v/6` of at least
  one earlier homeworld.

Placement:

1. The first homeworld is a random planet in the central box
   `1000 + [W/4, 3W/4]` on both axes. Boxes include their edges. After 50
   random picks outside it, the pick nearest to the box is used. "Nearest"
   is `dx² + dy²`, where `dx` and `dy` are how far the planet lies outside
   the box on each axis (0 when inside on that axis). The first of equally
   near picks wins.
2. Each further homeworld is a random planet inside a wider box that
   meets the distance rules. The box is `1000 + [W/20, 19W/20]` for 5 or
   more players, `[W/10, 9W/10]` for 3–4 and `[3W/20, 17W/20]` for 1–2.
   A planet qualifies only when it is inside the wide box, at `d² ≥ 9v/10`
   from every earlier homeworld (and not one of them) and within
   `d² ≤ 7v/6` of at least one. After 50 random picks fail, the planet
   list (sorted by `x`) is scanned from the planet after the 50th pick,
   wrapping from the last planet to the first. The first qualifying planet
   is taken. The scan stops without a result on returning to the 50th
   pick, which is not tested again.
3. If no planet qualifies, the minimum shrinks and the maximum grows by
   `v/35` each (the changes accumulate over restarts), and placement
   restarts from the first homeworld. UG01,
   UG05 and UG06 needed restarts.
4. Players are then assigned to the homeworlds in random order.

## Starting players

### Starting tech (CONFIRMED, UG01..UG21)

Energy/weapons/propulsion/construction/electronics/biotech by primary
racial trait:

| PRT | tech |
|---|---|
| HE, IS | 0/0/0/0/0/0 |
| SS | 0/0/0/0/5/0 |
| WM | 1/6/1/0/0/0 |
| CA | 1/1/1/2/0/6 |
| SD | 0/0/2/0/0/2 |
| PP | 4/0/0/0/0/0 |
| IT | 0/0/5/5/0/0 |
| AR | 1/0/0/0/0/0 |
| JOAT | 3/3/3/3/3/3 |

Then:

- A race with the "expensive fields start at tech 3" option raises every
  field whose research cost setting is "costs 75% extra" to 3 (JOAT 4) if
  it is lower.
- CE: propulsion +1. IFE: propulsion +1 (not in the tutorial).

Research starts at 15% of resources for every player (MEASURED,
UG01..UG21; see Relations, research and production). No research is banked.

### Homeworld (CONFIRMED)

Each homeworld starts with:

- 10 mines, 10 factories, 10 defenses, a planetary scanner and starbase
  design 0 (a Space Station; see Starbases);
- population 25,000, or 17,500 with LSP;
- environment at the centre of the owner's habitable range on each axis,
  `lo + (hi − lo)/2`; a random `1 + rand(99)` on an immune axis;
- no artifact;
- surface minerals and concentrations shared by all homeworlds (below).

**Shared starting minerals (LEGACY BUG, CONFIRMED, UG16–UG21).** All
homeworlds in a game get the same surface minerals and the same
concentrations, before spends. Surface minerals are drawn once per game:
per mineral `10 + rand(10·c)`, plus `155 + rand(150)` when that is below
200, where `c` is the concentration of planet 0 (the first planet in the
planet list); BBS adds a quarter. `c` is planet 0's concentration as
generated: after the radiation bonus, the BBS +5 and any low override.
It is not raised to 30; that floor applies only to the homeworlds'
concentrations. The concentrations are planet 0's,
each raised to at least 30, not the homeworld's own. If planet 0 ends up
unowned, its surface minerals are 0. Elegy reproduces this as one
isolated rule (shared draw, concentrations taken from one reference
planet).

**BBS option** (CONFIRMED, UG03, UG09, UG21): homeworld population ×
`(growth% · k + 5)/5`, `k = 2` for HE and 1 otherwise.

**Order of the population steps** (MEASURED, UG03-C, UG21-C). Population
is counted in units of 100 colonists, and each step truncates to a whole
unit before the next: first an expert computer player's +10%
("Computer players" below), then the BBS factor, then the PP/IT split
with the second planet ("Second planet" below). UG03-C player 2 (expert
PP, LSP, growth 19%, BBS): 175 → 192 → `⌊192·24/5⌋ = 921` → homeworld
`⌊921·4/5⌋ = 736`, second planet `⌊921·2/5⌋ = 368`. UG21-C player 9
(expert CA, LSP, growth 15%, BBS): 175 → 192 → `192·20/5 = 768`. Applying
the BBS factor before the +10% gives 739 and 770 instead.

**AR** (CONFIRMED, UG01..UG15 computer players): no mines, factories or defenses and no planetary
scanner. Starbase design 1 (a Space Station) orbits the homeworld, and
design 0 is an empty Orbital Fort.

### Leftover advantage points (CONFIRMED)

`L = min(50, leftover race-design points)`; computer players always have
`L = 50`. The race file's spend setting applies `L` to the homeworld:

| spend | effect |
|---|---|
| surface minerals | `10·L` kT: the smallest mineral (the last of equal smallest) gets `L·10/4` plus the remainder, then all three get `L·10/4`. With `L = 50`: +250 on the smallest, +125 on the others |
| concentrations | `e = L/2` (1 when `L` is 1–2); the lowest concentration (the first of equal lowest) gets `+e`, then all three get `+(e + 1)/2`. With `L = 50`: +25, then +13 |
| mines | `+L/2` |
| factories | `+L/5` |
| defenses | `+(L + 5)/10` |

AR homeworlds get no mines, factories or defenses after the spend, so an
AR race's mines, factories or defenses spend adds nothing: no
installations and surface minerals unchanged (CONFIRMED, RD-7: spends 2,
3 and 4). Its minerals and concentrations spends apply as usual.

A race's points, the replacement of illegal races and the Random race are
in `RACES.md`. Every race in the UG corpus had at least 50.

### Computer players (CONFIRMED, UG01..UG15)

- Six types (HE, SS, IS, CA, PP and AR races built into the original) and
  four levels (easy, standard, harder, expert). A definition file may
  leave either random. Their race settings are in `AI.md` ("Built-in
  races").
- Harder and expert computer players whose spend is surface minerals also
  get the concentration boost (with `L = 50`).
- Expert: homeworld population +10%.
- Each computer player without a name gets one of 24 built-in names;
  duplicate names and duplicate logos are resolved at random.

### Starbases (CONFIRMED, UG01..UG21, except where noted)

- Design 0 for every race: a Space Station. The homeworld's starbase uses
  it. Its 12 slots in hull order (CONFIRMED, UG01..UG21): empty, 8 Laser,
  8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield,
  empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield. That is 32
  Lasers and 32 Mole-skin Shields.
- PP: design 0 also carries a Mass Driver 5 in its first slot. On a map
  larger than tiny, design 1 is an Orbital Fort for the second planet:
  Mass Driver 5, 6 Laser, 6 Cow-hide Shield, 6 Laser, 6 Cow-hide Shield.
  The PP fort's shields are Cow-hide, not Mole-skin.
- IT (not in the tutorial): design 0 also carries a Stargate 100/250 in
  its first slot. On a map larger than tiny, design 1 is an Orbital Fort:
  Stargate 100/250, 6 Laser, 6 Mole-skin Shield, 6 Laser, 6 Mole-skin
  Shield.
- AR: design 1 is the plain Space Station above (same loadout, no
  additions), and it orbits the homeworld. Design 0 is an Orbital Fort
  with all five slots empty.

### Starting ships (CONFIRMED, UG01..UG21)

Each ship below is a one-ship fleet at the homeworld with full fuel and
battle plan 0. The fleets are numbered in this order, and each new design
takes the next design slot:

| PRT | ships |
|---|---|
| HE | Scout (fuel tank); three Mini-Colony Ships of one design |
| SS | Scout (stealth cloak) if energy ≥ 2, else Scout (fuel tank); Small Freighter with Transport Cloaking (human players only); Colony Ship |
| WM | Scout (X-Ray Laser); Destroyer and Mini Bomber if construction ≥ 3; Colony Ship |
| CA | Scout (fuel tank); Colony Ship; Mini-Miner with two Orbital Adjusters |
| IS | Scout (fuel tank); Colony Ship |
| SD | Scout (fuel tank); Colony Ship; Mini Mine Layer (Mine Dispensers); Mini Mine Layer (Speed Traps) |
| PP | Scout (fuel tank); Colony Ship; on a non-tiny map a second Scout of design 0 at the second planet |
| IT | Scout (fuel tank); Colony Ship; Destroyer; Privateer; on a non-tiny map a second Scout of design 0 at the second planet |
| AR | Scout (fuel tank); Colony Ship with an Orbital Construction Module |
| JOAT | Scout (X-Ray Laser); Scout (fuel tank); Colony Ship; Medium Freighter if construction < 4, else Privateer; Destroyer; Mini-Miner (two Robo-Mini-Miners) |

Then a race with ARM and without OBRM gets two Midget Miners (one design).

The base designs (Quick Jump 5 engine, Bat Scanner, plus the items named):

| design | hull | parts |
|---|---|---|
| Scout (fuel tank) | Scout | Fuel Tank |
| Scout (X-Ray Laser) | Scout | X-Ray Laser |
| Scout (stealth cloak) | Scout | Stealth Cloak |
| Small Freighter | Small Freighter | Transport Cloaking (no scanner), Mole-skin Shield |
| Medium Freighter | Medium Freighter | Tritanium |
| Destroyer | Destroyer | Laser, Alpha Torpedo, 2 Tritanium, Fuel Tank, Battle Computer |
| Privateer | Privateer | 2 Crobmnium, Laser, Alpha Torpedo |
| Colony Ship | Colony Ship | Colonization Module (AR: Orbital Construction Module); no scanner |
| Mini-Colony Ship | Mini-Colony Ship | Settler's Delight engine, Colonization Module; no scanner |
| Mini Bomber | Mini Bomber | 2 Lady Finger Bombs; no scanner |
| Mini-Miner | Mini-Miner | 2 Robo-Mini-Miners (CA: 2 Orbital Adjusters) |
| Midget Miner | Midget Miner | 2 Robo-Midget Miners; no scanner |
| Mini Mine Layer | Mini Mine Layer | 2 × 2 Mine Dispenser 40 (SD's second: 2 × 2 Speed Trap 20) |

**Part upgrades** (CONFIRMED for the cases run, UG01..UG21): in every starting design,
a basic part is replaced by the first part in its list that the player may
build (race restrictions and tech, `COMPONENTS.md`):

| part | replaced by the first available of |
|---|---|
| Quick Jump 5 | Radiating Hydro-Ram Scoop, Alpha Drive 8, Daddy Long Legs 7, Fuel Mizer, Long Hump 6. The ram scoop is skipped on a Colony Ship when the race is not radiation-immune and its radiation centre is 84 or less |
| Bat or Rhino Scanner | Possum, Mole, Rhino |
| first two armors | Carbonic Armor, Crobmnium |
| first two shields | Wolverine Diffuse Shield, Cow-hide Shield |
| Laser, X-Ray Laser | Yakimora Light Phaser, X-Ray Laser |
| Alpha Torpedo | Beta Torpedo |
| Lady Finger Bomb | Black Cat Bomb |
| Robo-Midget, Robo-Mini-Miner | Robo-Miner, Robo-Midget Miner |

For example, an SS scout carries a Possum Scanner (electronics 5) and a
WM scout a Yakimora Light Phaser (weapons 6). Starting starbase designs
are not upgraded.

### Second planet: PP and IT (CONFIRMED, UG16..UG21)

On a map larger than tiny, a PP or IT player also owns a second planet:

- A random unowned planet at distance `0.15W ≤ d ≤ 0.23W` from the
  homeworld (all such planets equally likely); if none, the nearest
  unowned planet outside that band (the first in list order on a tie).
  The band is checked on exact `d²` against `(15W/100)²` and `(23W/100)²`,
  with each bound truncated before squaring, and both ends included.
- If its habitability for the owner is below 10% (`KERNEL.md`), its
  environment is redrawn, each axis `2 + rand(97)`, until it reaches 10%,
  at most 100 times. If all 100 redraws were used, the planet takes the
  homeworld's environment instead, even when the last redraw succeeded
  (LEGACY BUG, CONFIRMED: UG29, a PP race with 40–60 on every axis, used
  all 100 redraws and its second planet took the homeworld's 50/50/50;
  UG30, the same race on another seed, kept its redrawn 40/42/45. Whether
  a success on exactly the 100th redraw is also replaced is BINARY-ONLY).
- 10 mines, 4 factories, starbase design 1, a planetary scanner, surface
  minerals `100 + rand(200)` each, and 2/5 of the homeworld's population.
  The homeworld keeps 4/5.

### Relations, research and production (MEASURED)

- When exactly one player is human, every player starts as an enemy of
  every other (OB-006 and UG dumps). With two or more human players,
  every player is neutral to every other, the default (UG16, UG17, UG19,
  UG20 and UG21 have 2 to 6 human players, and their files store no
  relations, which reads as neutral). A game with no human player was
  not run.
- Every player, computer players included, starts with research at 15%
  of resources. The current field is energy, and the next field is "same
  field" (every player in every UG dump).
- No planet has a production queue at the start (no queue in any UG
  dump).

## Space objects at the start (CONFIRMED, UG01..UG21)

- **Wormholes** exist only with random events on. Their number, classes
  and positions follow `OBJECTS.md` "Wormholes" (creation and placement
  badness). The UG games confirm those rules exactly at creation, every
  size, events on and off. The objects are created after the planets and
  players.
- **No Mystery Trader**, minefields or packets exist at the start.

## Open experiments

1. Unseeded new-game wizard games: computer-player counts chosen from size
   and difficulty (BINARY-ONLY), not run.
2. The tutorial galaxy (fixed tiny galaxy, fixed seed) and
   race-wide "75% extra fields start at 3" combined with JOAT (start 4).
3. Seed-dependent planet counts as distributions (the model's sampled
   ranges and rates above).
4. The PP/IT second planet: whether a success on exactly the 100th
   environment redraw is also replaced by the homeworld's environment
   (BINARY-ONLY).
