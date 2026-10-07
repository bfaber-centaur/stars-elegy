# Computer players: shared core

This file specifies how the original J-RC3 computer players decide their
orders, at the level of behavior: given the game state a computer player
can see, which orders it writes. It covers what all six personalities
share. Each personality's own turn (fleets, ship designs, colonizing,
war) gets its own file under `docs/ai/`:

| Type (definition file) | Personality | PRT | File |
|---|---|---|---|
| 1 | Robotoid | HE | `docs/ai/robotoid.md` (planned) |
| 2 | Turindrone | SS | `docs/ai/turindrone.md` (planned) |
| 3 | Automitron | IS | `docs/ai/automitron.md` (planned) |
| 4 | Rototill | CA | `docs/ai/rototill.md` (planned) |
| 5 | Cybertron | PP | `docs/ai/cybertron.md` (planned) |
| 6 | Macinti | AR | `docs/ai/macinti.md` (planned) |

Elegy reproduces these personalities (project decision). Related specs:
game creation and the starting setup of computer players are in
`UNIVERSE.md`; the research, tech and terraforming mechanics the AI's
choices feed are in `KERNEL.md` ("Research", "Terraforming"); part and
hull stats and who may build what are in `COMPONENTS.md`; the harder and
expert computer players' automatic trades with the Mystery Trader are in
`OBJECTS.md` ("Mystery Trader"); how the host ingests orders is in
`ORDERS.md`.

## Status

- **CONFIRMED**: predicted from the binary, then matched by captured
  computer-player orders. The capture corpus (private evidence) records
  every computer player's order file as the host writes it during pinned
  generations: corpus AIX (one expert of each type, years 2400–2460) and
  AI01 (the same line-up on another map, 2400–2402).
- **MEASURED**: seen in the capture, rule read from the binary, not yet
  tested as a prediction on a second game.
- **BINARY-ONLY**: read from the original program, not yet checked
  against the original's output.
- **LEGACY BUG**: the original's behavior looks unintended; Elegy keeps
  it behind a named switch unless stated otherwise.

"Year index" is the year minus 2400. `Random(n)` is a draw from the
host's generator, uniform in `0..n−1` (see "Random numbers" below).

## 1. When a computer player acts (BINARY-ONLY unless noted)

- Before the host generates a year, it runs each computer player in
  player order. A computer player acts only through ordinary orders: the
  same order records a human's client writes (MEASURED: design changes,
  production queues, research, waypoint add/change, cargo, split/merge,
  planet packet/route settings). The host then ingests them like any
  player's orders (`ORDERS.md`).
- If an order file for that player already exists when the host runs, the
  computer player does not act that year; the existing file is used.
- **What it sees.** Exactly that player's own view of the game (what its
  player file holds: its planets, fleets, designs, scanned reports) plus a
  private memory it keeps between years (§6). It never reads other
  players' hidden state.
- A computer player whose "dormant" flag is set writes an empty order set
  (the flag's meaning is not yet settled).
- **Random numbers.** Computer players draw from the host's single
  generator, before the year is generated. Every draw shifts the year's
  later draws. To reproduce a host's year exactly, Elegy runs the
  computer players first, in player order, on the shared generator.
- Each personality's turn starts with the shared steps below, in this
  order: research (§4, which also maintains the starbase designs of §5 and
  the hub memory of §6 for HE, SS, IS, CA and PP), then the personality's
  own work, then the planet automation of §7.

## 2. Own-planet order (BINARY-ONLY)

Every per-planet pass of a computer player walks its planets in one
shuffled order, made once per turn: start from its planets in planet-id
order, then for `i = 0 .. n−2`: `j = i + Random(n − i)`, swap `i` and `j`.
In a tutorial game there is no shuffle.

## 3. Built-in races (CONFIRMED for 23 of 24; SS harder BINARY-ONLY)

A definition-file line `# TYPE LEVEL` makes a computer player: TYPE 1–6
as in the table above, LEVEL 1–4 = easy, standard, harder, expert; 0 for
either means random (`UNIVERSE.md` "Computer players"). Each type × level
has a fixed race. Matched field by field against every computer player in
the UG corpus (73 players, 23 of the 24 combinations).

Columns: lesser racial traits; growth rate; habitability ranges
(gravity / temperature / radiation in the race wizard's 0–100 click
scale, centre = midpoint; imm = immune); colonists per resource;
factories (resources per 10 factories / resource cost / factories per
10,000 colonists); mines (kT per 10 mines / resource cost / mines per
10,000 colonists); research cost per field (energy, weapons, propulsion,
construction, electronics, biotech: c cheap, n normal, x expensive);
"factories cost 1 less germanium"; "expensive fields start at tech 3".
Built-in names are not listed (`UNIVERSE.md`: 24 built-in names).

| Type | Level | PRT | LRT | Growth | Hab | Col/res | Factories | Mines | Research | Fact. Ge −1 | Exp. start 3 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HE | easy | HE | IFE MA CE OBRM BET | 5% | imm / imm / imm | 1000 | 12/10/16 | 10/5/10 | n n c n n x | no | no |
| HE | standard | HE | IFE MA CE OBRM | 6% | imm / imm / imm | 900 | 13/9/16 | 10/4/11 | n n c n n x | no | no |
| HE | harder | HE | IFE UR MA OBRM | 6% | imm / imm / imm | 800 | 13/9/18 | 10/4/12 | n c c c n x | yes | no |
| HE | expert | HE | IFE UR MA OBRM | 7% | imm / imm / imm | 800 | 13/9/16 | 10/4/8 | n c n c n x | yes | no |
| SS | easy | SS | IFE ARM MA RS | 14% | 27-89 / 7-63 / 35-95 | 1000 | 9/10/9 | 9/5/8 | n x n n n x | no | no |
| SS | standard | SS | IFE ARM MA RS | 14% | 32-92 / 6-60 / 26-96 | 1000 | 10/10/10 | 10/5/9 | n n n n n n | yes | no |
| SS | harder | SS | IFE ARM MA RS | 14% | 31-95 / 4-52 / 30-94 | 900 | 11/10/10 | 10/5/9 | x n x n n n | yes | no |
| SS | expert | SS | IFE ARM MA RS | 15% | 31-93 / 5-53 / imm | 800 | 15/10/25 | 10/5/9 | x x x x x x | yes | yes |
| IS | easy | IS | GR CE OBRM NAS LSP | 15% | 7-63 / 26-94 / 5-71 | 900 | 11/10/14 | 11/6/14 | x x x x x x | no | yes |
| IS | standard | IS | GR CE OBRM NAS LSP | 15% | 7-63 / 26-94 / 5-71 | 800 | 13/9/14 | 10/6/14 | x x x x x x | yes | yes |
| IS | harder | IS | GR OBRM NAS LSP | 15% | 7-63 / 26-94 / 5-71 | 800 | 14/9/15 | 14/5/15 | x x x x x x | yes | yes |
| IS | expert | IS | GR OBRM NAS LSP | 16% | 7-63 / imm / 0-100 | 800 | 14/9/14 | 14/5/14 | x x x x x x | yes | yes |
| CA | easy | CA | TT CE OBRM NAS LSP BET | 15% | 32-68 / 31-69 / 31-69 | 1000 | 10/10/10 | 10/5/10 | x x x x x c | no | yes |
| CA | standard | CA | TT OBRM NAS LSP BET | 15% | 32-68 / 31-69 / 31-69 | 800 | 12/10/12 | 14/5/12 | x x x x x c | no | yes |
| CA | harder | CA | TT OBRM NAS LSP BET | 15% | 23-77 / 24-76 / 25-75 | 800 | 12/10/12 | 14/5/12 | x x x x x c | no | yes |
| CA | expert | CA | TT OBRM NAS LSP BET | 15% | imm / 24-76 / 25-75 | 800 | 15/10/15 | 15/5/15 | x x x x x c | no | yes |
| PP | easy | PP | IFE TT OBRM LSP | 12% | 22-78 / 22-78 / 22-78 | 1000 | 9/18/9 | 9/10/8 | n x x n x x | no | yes |
| PP | standard | PP | IFE TT OBRM NAS LSP | 17% | 19-81 / 19-81 / 19-81 | 1000 | 10/13/19 | 10/10/7 | n x x n n n | no | yes |
| PP | harder | PP | IFE TT MA OBRM NAS LSP | 17% | 18-82 / 18-82 / 18-82 | 1000 | 14/10/20 | 10/10/6 | n n x n n c | yes | yes |
| PP | expert | PP | IFE TT MA OBRM NAS LSP | 19% | 17-83 / 17-83 / 17-83 | 1000 | 15/9/25 | 10/10/5 | c c x c n n | yes | yes |
| AR | easy | AR | IFE TT ISB GR CE | 10% | 20-80 / 20-80 / 20-80 | 1600 | 10/10/10 | 10/5/10 | n n n n x n | no | no |
| AR | standard | AR | IFE TT ISB GR | 14% | 15-85 / 15-85 / 15-85 | 1200 | 10/10/10 | 10/5/10 | c n n n x n | no | no |
| AR | harder | AR | IFE TT ARM ISB GR UR MA | 17% | 15-85 / 15-85 / 15-85 | 1000 | 10/10/10 | 10/5/10 | c n n n n n | no | no |
| AR | expert | AR | IFE TT ARM ISB GR UR MA | 20% | 15-85 / 15-85 / 15-85 | 1000 | 10/10/10 | 10/5/10 | c n n c n n | no | no |

## 4. Research choice (CONFIRMED, AI-1)

Every year each computer player sets its research budget and its current
and next research fields. How research then progresses is `KERNEL.md`
"Research".

**Budget** (percent of resources), by year index `y`:

| Personality | Budget |
|---|---|
| Robotoid HE | 0 before `y` = 10, then 15 |
| Turindrone SS | 15 |
| Automitron IS | 0 before 10, then 20 |
| Rototill CA | 0 before 20, then 15 |
| Cybertron PP | 17 |
| Macinti AR | 15 |

If all six tech levels are 24 or more, the budget is 0 instead.

**Field.** Each personality except Rototill has a research plan, a list
of (field, level) goals (E energy, W weapons, P propulsion, C
construction, El electronics, B biotech):

- Robotoid: P2 C3 W3 C4 E2 El3 P6 W5 C6 B4 El5 E6 W7 C10 E6 El7 W10 P9
  P12 C13 W14 C16 E9 El10 P16 B10 E15 W20 P20 El16 B12 W24 El19 C24 E22
  C26
- Turindrone: P2 C4 B4 E4 W5 P6 C6 W8 E6 El6 P9 B7 C8 El8 B5 C9 E7 El10
  W10 P12 C11 E10 W12 El13 P16 W14 C15 El14 B10 W16 E14
- Automitron: El6 C4 P5 W5 B4 E4 El7 C6 P7 W8 B6 E7 El12 C13 P9 W11 B7
  E10
- Cybertron: C4 P2 El3 B3 W3 P6 C6 El6 E10 C10 P8 C13 W6 B9 El9 W7 P9
  C16 E14 W11 El12 B11 P13 C18 W15 E18 El17 W17 C20 P17 B18 El21 E23 P22
  C21 W23 P26 El26 E26 W26 C26 B26
- Macinti: E3 P2 E20 C17 P20 W20 C23 W23

The first goal not yet met (current level in that field below the goal
level) sets the current field. If that goal is exactly one level away and
is not the last goal, the next field becomes the following goal's field;
otherwise the next field keeps its previous setting. A research order is
written every year while a goal is unmet, even when nothing changes.

With no plan (Rototill), or once every goal is met, the current field
becomes the lowest tech level (first in E W P C El B order on ties), and
the research order is written only if the field changes.

## 5. Starbase designs (CONFIRMED, AI-2; Macinti and the planned files differ)

Robotoid, Turindrone, Automitron, Rototill and Cybertron maintain their
starbase designs every year, before their own work. Macinti has its own
starbase rules (`docs/ai/macinti.md`).

**Slots and families.** Starbase design slots 0–9 form two families of
Space Stations, A = (0, 2, 4) and B = (5, 7, 9), and two of Orbital
Forts, A = (1, 3) and B = (6, 8). Within a family the slots are
variants 1, 2, 3 in that order; the Orbital Fort families have variants 1
and 3. Slot 0 is the starting starbase design (`UNIVERSE.md`); for
Cybertron slot 1 is the starting Orbital Fort with a Mass Driver 5.

**Each year:**

1. If slot 2 is empty: create slot 2 (variant 2) and slot 4 (variant 3).
   If slot 1 is empty: create slot 1 (variant 1). If slot 3 is empty:
   create slot 3 (variant 3).
2. From year index 50: take the newest Space Station design of slots
   0, 2, 4, 5, 7, 9 (creation year; on ties the later slot). If it is 40
   or more years old and no starbase built from the other family's three
   slots exists, create the other family: its three slots as variants 1,
   2, 3. The same for Orbital Forts: the newest of 1, 3, 6, 8; if 40 or
   more years old and no starbase of the other family's two slots exists,
   create them as variants 1 and 3. (CONFIRMED at the 2450 switch.)

A design creation is a design order for that slot (`ORDERS.md`).

**Creating a design.** Variant-1/2/3 slots of the Space Station families
use the Space Station hull; Orbital Fort slots the Orbital Fort hull. If
the hull is not available to the race (`COMPONENTS.md` "Who can build
what"), nothing is created. Each hull slot gets a part from its *AI part
class* (below): the first part in the class's list that the race can
build now. If any slot's class has no such part, nothing is created.
Counts: start with the hull slot's maximum; for variants 1 and 2 a slot
whose maximum is 4 or more gets `max >> (3 − variant)` (so 1/4 and 1/2);
for variant 1 only, except Cybertron, a slot with fewer than 4 that holds
an orbital part or more than one item loses one.

Hull slots, in hull order, use these classes:

- Space Station: 34, 35, 37, 0, 17, 10, 11, 38, 19, 36, 34, 9
- Orbital Fort: 34, 0, 17, 36, 37

**Picture.** The first of the hull's four starbase pictures not used by
another starbase design of the same hull; if all four are used,
`Random(4)` picks one.

**Name.** Up to 20 tries of `Random(13)` from a list of 13 built-in
starbase names, until the name is unused among starbase designs of the
same hull; after 20 failures, the last name tried with a number from
`Random(100)` (exact form BINARY-ONLY). Elegy may use its own 13 names.

### AI part classes

Each class is a list tried in order; the AI takes the first entry the
race can build. Parts are named as in `COMPONENTS.md`. Classes 34–38, 0,
9, 10, 11, 17 and 19 are used by starbases; the rest by ship designs
(personality files).

| Class | Parts, in order of preference |
|---|---|
| 0 | Anti Matter Torpedo, Omega Torpedo, Upsilon Torpedo, Rho Torpedo, Epsilon Torpedo, Delta Torpedo, Beta Torpedo, Alpha Torpedo |
| 1 | Armageddon Missile, Doomsday Missile, Juggernaut Missile, Jihad Missile |
| 2 | Multi Contained Munition, Mega Disruptor, Heavy Blaster, Colloidal Phaser |
| 3 | Anti-Matter Pulverizer, Disruptor, Mark IV Blaster, Phaser Bazooka |
| 4 | Streaming Pulverizer, Myopic Disruptor, Mini Blaster, Yakimora Light Phaser, X-Ray Laser, Laser |
| 5 | Blunderbuss, Bludgeon, Blackjack |
| 6 | Big Mutha Cannon, Gatling Neutrino Cannon, Gatling Gun, Mini Gun |
| 7 | Syncro Sapper, Phased Sapper, Pulsed Sapper |
| 8 | Galaxy Scoop, Enigma Pulsar, Trans-Galactic Mizer Scoop, Trans-Galactic Super Scoop, Trans-Galactic Fuel Scoop, Sub-Galactic Fuel Scoop, Radiating Hydro-Ram Scoop, Fuel Mizer |
| 9 | Superlatanium, Mega Poly Shell, Valanium, Depleted Neutronium, Neutronium, Fielded Kelarium, Kelarium, Organic Armor, Strobnium, Carbonic Armor, Crobmnium, Tritanium |
| 10 | Complete Phase Shield, Elephant Hide Fortress, Langston Shell, Gorilla Delagator, Croby Sharmor, Shadow Shield, Bear Neutrino Barrier, Wolverine Diffuse Shield, Cow-hide Shield, Mole-skin Shield |
| 11 | Battle Nexus, Battle Super Computer, Battle Computer |
| 12 | Multi Function Pod, Jammer 50, Jammer 30, Jammer 20, Jammer 10, Beam Deflector, Overthruster, Maneuvering Jet |
| 13 | Multi Function Pod, Overthruster, Maneuvering Jet, Ultra-Stealth Cloak, Beam Deflector, Super-Stealth Cloak, Stealth Cloak |
| 14 | Flux Capacitor, Energy Capacitor, Jammer 50, Jammer 30, Jammer 20, Jammer 10, Super Fuel Tank, Fuel Tank |
| 15 | Beam Deflector, Flux Capacitor, Energy Capacitor, Jammer 50, Jammer 30, Jammer 20, Jammer 10, Jammer 50, Jammer 30, Jammer 20, Jammer 10, Super Fuel Tank, Fuel Tank |
| 16 | Multi Cargo Pod, Super Cargo Pod, Cargo Pod |
| 17 | Mega Poly Shell, Superlatanium, Valanium, Mega Poly Shell, Neutronium, Depleted Neutronium, Fielded Kelarium, Kelarium, Organic Armor, Strobnium, Carbonic Armor, Crobmnium, Tritanium |
| 18 | Overthruster, Maneuvering Jet, Beam Deflector, Super Fuel Tank, Fuel Tank |
| 19 | Jammer 50, Jammer 30, Jammer 20, Jammer 10, Battle Nexus, Battle Super Computer, Battle Computer |
| 20 | Flux Capacitor, Energy Capacitor, Jammer 50, Jammer 30, Jammer 20, Jammer 10, Jammer 50, Jammer 30, Jammer 20, Jammer 10, Multi Function Pod, Ultra-Stealth Cloak, Super-Stealth Cloak, Stealth Cloak, Battle Nexus, Battle Super Computer, Battle Computer |
| 21 | Hush-a-Boom, Cherry Bomb, M-80 Bomb, M-70 Bomb, Black Cat Bomb, Lady Finger Bomb |
| 22 | Hush-a-Boom, Retro Bomb, Annihilator Bomb, Peerless Bomb, Enriched Neutron Bomb, Neutron Bomb, Smart Bomb |
| 23 | Hush-a-Boom, Annihilator Bomb, Peerless Bomb, Enriched Neutron Bomb, Neutron Bomb, Smart Bomb, Cherry Bomb, M-80 Bomb, M-70 Bomb, Black Cat Bomb, Lady Finger Bomb, Retro Bomb |
| 24 | Galaxy Scoop, Radiating Hydro-Ram Scoop |
| 25 | Mine Dispenser 130, Mine Dispenser 80, Mine Dispenser 50, Mine Dispenser 40 |
| 26 | Elephant Scanner, Robber Baron Scanner, Dolphin Scanner, Chameleon Scanner, Ferret Scanner, Gazelle Scanner, Possum Scanner |
| 27 | Robber Baron Scanner, Pick Pocket Scanner, Chameleon Scanner, Pick Pocket Scanner, Possum Scanner, DNA Scanner, Mole Scanner, Rhino Scanner, Bat Scanner |
| 28 | Alien Miner, Robo-Ultra-Miner, Robo-Super-Miner, Robo-Maxi-Miner, Robo-Miner, Robo-Mini-Miner, Robo-Midget Miner |
| 29 | Orbital Adjuster |
| 30 | Trans-Star 10, Enigma Pulsar, Radiating Hydro-Ram Scoop, Trans-Galactic Super Scoop, Trans-Galactic Fuel Scoop, Sub-Galactic Fuel Scoop, Trans-Galactic Drive, Alpha Drive 8, Daddy Long Legs 7, Long Hump 6 |
| 31 | Orbital Construction Module, Colonization Module |
| 32 | Speed Trap 50, Speed Trap 30, Speed Trap 20 |
| 33 | Multi Contained Munition |
| 34 | Ultra Driver 13, Ultra Driver 12, Ultra Driver 11, Ultra Driver 10, Super Driver 9, Super Driver 8, Mass Driver 7, Mass Driver 6, Mass Driver 5, Multi Function Pod, Ultra-Stealth Cloak, Super-Stealth Cloak, Stealth Cloak, Jammer 50, Jammer 30, Jammer 20, Jammer 10, Battle Nexus, Battle Super Computer, Battle Computer |
| 35 | Armageddon Missile, Omega Torpedo, Doomsday Missile, Upsilon Torpedo, Rho Torpedo, Epsilon Torpedo, Delta Torpedo, Beta Torpedo, Alpha Torpedo |
| 36 | Anti-Matter Pulverizer, Streaming Pulverizer, Disruptor, Myopic Disruptor, Mark IV Blaster, Mini Blaster, Phaser Bazooka, Yakimora Light Phaser, X-Ray Laser, Laser |
| 37 | Langston Shell, Complete Phase Shield, Elephant Hide Fortress, Gorilla Delagator, Langston Shell, Bear Neutrino Barrier, Shadow Shield, Croby Sharmor, Wolverine Diffuse Shield, Cow-hide Shield, Mole-skin Shield |
| 38 | Mega Disruptor, Heavy Blaster, Colloidal Phaser, Phaser Bazooka, Laser |
| 39 | Jammer 50, Jammer 30, Jammer 20, Jammer 10, Multi Function Pod, Ultra-Stealth Cloak, Super-Stealth Cloak, Stealth Cloak |

## 6. Hubs: the AI's private memory (BINARY-ONLY)

A computer player keeps a list of up to 64 *hubs* between years: each a
planet with up to 8 freighter fleets assigned. Robotoid, Turindrone,
Automitron and Rototill update it every year from year index 20:

1. Drop hubs whose planet the player no longer owns.
2. Every own planet with a starbase becomes a hub. A starbase-less own
   planet becomes a hub when it has population ≥ 8,000, ≥ 20 mines, ≥ 20
   factories and `Σ over minerals (surface + 4·concentration²) ≥ 7000`;
   for Robotoid only if no existing hub is within 50 ly.
3. Every own freighter fleet not yet assigned goes to the nearest hub with
   fewer than 8.
4. Each hub with fewer than 4 then takes one fleet from the first hub that
   has at least 2 more than it.

What counts as a freighter fleet, and how freighters use hubs, is in the
personality files.

## 7. Planet automation (BINARY-ONLY)

After its own work, every computer player runs these steps, in order.

1. Keep fleets moving (fleet rules: personality files).
2. **Starbases for hubs** (not Macinti; in a tutorial game only before
   year index 31). Cybertron uses its own rule (`docs/ai/cybertron.md`).
   The others: every own planet with no starbase, population ≥ 8,000, not
   marked by the personality's own pass, that is a hub (§6), gets the
   current starbase design (slot 0, or 5 when slot 5 is newer) ×1 appended
   unless a starbase is already queued.
3. **Per planet**, in the shuffled order (§2). A planet is eligible with
   population ≥ 4,000 (Robotoid) or ≥ 6,000 or marked (others). For each
   eligible planet, compare *available* (surface minerals plus this year's
   expected mining; resources after the research budget) with the full
   cost of its current queue. Except Macinti, skip the planet if any
   mineral available is below the queue's cost of it. Then:
   - Robotoid, or an unmarked planet: the first of these that queues
     something: starbase upgrade, packet fling, planetary scanner,
     defenses.
   - Cybertron, marked planet: starbase upgrade only.
   - Not Robotoid and nothing queued so far: terraforming.
4. **Under attack** (not tutorial; from year index (universe size + 2)·10,
   size 0 = tiny): quick defenses on threatened planets.
5. **Blocked queues**: mines or alchemy in front of a mineral-starved head.

Then every computer player fills its queues with mines and factories.

**Starbase upgrade.** A planet with a starbase and no starbase item queued
(Cybertron: only from year index 40). Families are Space Station (current
base slot 0 or 5) or Orbital Fort (current base 1, or 6 when slot 6 is
newer than slot 1).
- The starbase's design is in the current family: no upgrade if it is
  already the top variant or the next variant's slot (+2) is empty; else
  with chance 6/100 (`Random(100) ≤ 5`) and all surface minerals ≥ 200,
  queue the next variant.
- It is in the old family: `e = year index − creation year index of the
  current base − 10`, at least 0, halved when below 50; with chance
  `(e + 5)/100` (`Random(100) < e + 5`) queue the same variant in the
  current family.
Macinti has its own rule.

**Packet fling.** Harder and expert only, not Cybertron: no packet item
queued, Ir + Bo + Ge available > 3000, the planet's starbase has a mass
driver rated warp 10 or more, and `Random(4) == 0`. Targets: planets of
another player within the driver's range (range per driver, tripled if
any mineral is above 12,500; values BINARY-ONLY, to be tabulated), whose
report is at most 2 years old, whose defense estimate is low, not owned by
an AR player, and not a PP player's planet with a starbase. One target is
picked uniformly (`Random(k)` reservoir over candidates in planet order).
The planet's packet destination is set to it at warp 13 (a planet-settings
order). Packets queued: Ge > 20,000 → with chance 2/3 (`Random(3)`) 80
germanium packets first; then Ir ≥ 3001, Bo ≥ 4001 and Ge ≥ 3001 → 30
mixed packets; else Ir ≥ 1501, Bo ≥ 2251 and Ge ≥ 1501 → 15 mixed; else
for each mineral above 1250 / 2500 / 1250 (Ir / Bo / Ge),
`clamp((amount − threshold)/200, 1, 25)` packets of it.

**Planetary scanner.** This step never queues anything in J-RC3: it looks
for production items the production list never offers. (Captured queues
in AIX hold no scanner. LEGACY BUG; nothing to reproduce.)

**Defenses.** Population ≥ 160,000, defenses below population/8,000, none
queued, room to build → append `min(room, 4)` defenses.

**Terraforming** (not Cybertron). Population ≥ 20,000, none queued, the
planet is off the race's centre on some axis and terraforming is
possible → append `min(available steps, 4)` terraform items.
(Terraforming mechanics: `KERNEL.md` "Terraforming".)

**Under attack.** A planet is threatened when a foreign fleet with a
bomber orbits it. Quick defenses, if none are queued and resources after
research `r ≥ 50`: `n = r/25`, if `n > 5` then `n −= n/6`; `r −= r/10`;
`n` at most the defense room; `m = min(100, smallest mineral/5)`. If
`n > m`: `extra = max(0, (r − m·k)/150)` with `k = 25` for MA races and
100 otherwise; queue `m + extra` defenses and `5·extra` alchemy. Defenses
go to the front, then alchemy in front of them.

**Blocked queues.** For each own planet whose queue head is not mines,
auto alchemy, alchemy or terraforming: if the head will take more than a
year and its resource cost is at most `(years − 1) ×` the planet's
resources (so minerals, not resources, are holding it): `m = min(mine
room, resources / mine cost)`; with `m < 1` put one auto alchemy in front.
Otherwise try `m` mines in front and auto alchemy in front, comparing the
head's completion estimate: keep auto alchemy only if it is strictly
better than both the original and the mines; keep the mines if they are
at least as good as alchemy and better than the original; else leave the
queue unchanged.

**Mines and factories**, every own planet in the shuffled order, using
`left = available − queue cost` per mineral and resources:
- resources left < 0: nothing.
- Macinti with terraform room: insert `min(room, ⌈resources/70⌉)`
  terraform items at the front; nothing else.
- some mineral left ≤ 0: if the head is auto alchemy or alchemy, nothing;
  else insert `min(mine room, resources / mine cost)` mines at the front.
- otherwise append `min(factory room, Ge left / factory Ge, resources /
  factory cost)` factories (tutorial: limited by all three minerals), then
  insert `min(mine room, resources left / mine cost)` mines at the front.
- all six techs at 26 and year index > 100: also alchemy, `resources
  left / alchemy cost + 1`.

"Room" is operable minus operating minus already queued.

## 8. Scrap orders

A computer player scraps a fleet by setting its waypoint-0 task to
scrap; the fleet is scrapped where it is (the waypoint's warp is
irrelevant). Captured 2400 orders: every expert type except Rototill
scraps at least one starting fleet at its homeworld.

- **Robotoid (MEASURED, AI-3).** Until year index 20, every Robotoid
  fleet that holds a ship of design slot 0 (the starting Scout) is
  scrapped, whatever its orders. AIX 2400: the Scout fleet, gone the next
  year.
- **Robotoid (BINARY-ONLY, AI-4).** An idle fleet with ships of slot 1 (the
  colonizer) and no slot-0 ships, from year index 5 (from the start when
  player positions are "close"), that finds no planet
  to colonize and no wormhole to explore, and orbits a planet, is
  scrapped.
- **Robotoid (BINARY-ONLY).** A fleet whose every design is obsolete (a
  ship design in slots 2–15 older than 50 years before year index 120, 70
  before 200, 100 after) orbiting an own planet is scrapped when that
  planet has a starbase, else with chance 1/5 per year.
- **Macinti (MEASURED, AI-5)** scraps its early fleets and repeatedly
  builds and scraps its first colonizer; `docs/ai/macinti.md`.
- The other personalities' scrap rules: their files.

## 9. Internal-only effects (BINARY-ONLY)

- It keeps an internal rounding of minefield sizes in its own reckoning;
  no order results.
- "Computer players form alliances" is read only by personality code
  (`KERNEL.md`); see the personality files.

## Open experiments

- AI-3, AI-5 on a second game; AI-4 needs a colonizer with no target.
- Easy/standard/harder levels for AI-1 and AI-2 (variant counts and the
  planet-automation thresholds are level-independent in the reading;
  only the packet fling checks the level).
- §7 planet automation as predictions: needs Elegy's production and
  mining estimates to predict queue contents exactly.
- Turindrone harder race (never drawn in UG).
- The "dormant" flag (§1).
