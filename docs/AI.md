# Computer players: shared core

This file specifies how the original J-RC3 computer players decide their
orders, at the level of behavior: given the game state a computer player
can see, which orders it writes. It covers what all six personalities
share. Each personality's own turn (fleets, ship designs, colonizing,
war) gets its own file under docs/ai/:

| Type (definition file) | Personality | PRT | File | Elegy |
|---|---|---|---|---|
| 1 | Robotoid | HE | `docs/ai/robotoid.md` | faithful candidate |
| 2 | Turindrone | SS | `docs/ai/turindrone.md` | legacy reference: fleet pass checked over AIX (AI-22), not an implementation commitment |
| 3 | Automitron | IS | `docs/ai/automitron.md` | legacy reference: fleet pass checked over AIX (AI-23), not an implementation commitment |
| 4 | Rototill | CA | `docs/ai/rototill.md` | faithful candidate |
| 5 | Cybertron | PP | `docs/ai/cybertron.md` | faithful candidate |
| 6 | Macinti | AR | docs/ai/macinti.md (planned) | legacy reference: early scraps measured (AI-5), fleet pass not fully checked |

**Project policy (2026-10-07).** Elegy reproduces faithfully only the
personalities whose behavior has been checked against the original
with oracle captures: Robotoid, Rototill and Cybertron, each matched over
every captured player-year of its corpus (`../PARITY.md` cases). These
are candidates for faithful implementation. Turindrone, Automitron and
Macinti are documented as legacy-reference behavior: read from the
original and optional future work. Turindrone's and Automitron's fleet
passes are checked over AIX (AI-22, AI-23), which preserves the result
but is not a commitment to implement them; their bomber paths stay
BINARY-ONLY. Reproducing all
six personalities is not an objective. Further computer-player
experiments need a concrete reason: an Elegy implementation blocker, a
contradiction in an existing spec, or a cheap experiment that closes a
bounded question. The shared rules in this file apply to all six.

Related specs:
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
  same order records a human's client writes (seen in the AI-1 capture: design changes,
  production queues, research, waypoint add/change, cargo, split/merge,
  planet packet/route settings). The host then ingests them like any
  player's orders (`ORDERS.md`).
- If an order file for that player already exists when the host runs, the
  computer player does not act that year; the existing file is used.
- **What it sees.** Exactly that player's own view of the game (what its
  player file holds: its planets, fleets, designs, scanned reports) plus
  the planet history its history file keeps, not the true game state
  (CONFIRMED, AI-12: predicted from the AIX fleet check, then held in two
  edited AI oracle runs, where other players' owners recorded in the
  history file led to scrapping and the same planets recorded as its own
  led to colonizing them):
  - A planet the player file does not report keeps the owner the history
    last recorded, so a foreign planet seen earlier still counts as
    foreign.
  - A planet the history records as the player's own that the player
    file no longer lists (a colony it lost) counts as unowned.
  - A planet it has never seen counts as unowned, so it is colonizable
    even when another player owns it. Robotoid flew colonizers to
    planets it had never scanned.
  - Editing owners in the host file changes nothing until the player's
    own files carry it.

  Elegy must run each computer player on that player's
  own view. It never reads other players' hidden state, except through
  the two leaks below. Beyond the planet history every player's history
  file keeps, it has no memory between years: the original writes a
  private computer-player memory block into the history file each year
  but never reads it back on this path, so every turn starts from an
  empty one (CONFIRMED, AI-10: replacing or editing that block before a
  year left the computer player's orders and memory output unchanged). Elegy keeps no private computer-player state across
  years.
- It plans from that player's file as the previous generation wrote it.
  A change made to the host's state between generations (for example a
  tech level edited in the host file) shows in its orders only one year
  later, once the player file carries it (seen in the computer-player oracle runs).
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

### State leaking between computer players (LEGACY BUG)

The host runs all computer players of a year one after another in one
program, in player order (lowest player number first; human players are
skipped). Two pieces of state survive from one computer player to the
next within that run. Each makes a computer player's orders depend on
which computer players ran before it that year.

Elegy keeps each computer player's state separate by default: this
**clean per-player state** is Elegy's normal behavior, and it is
INTENTIONALLY DIFFERENT from the original. The original's whole-program
behavior is reproduced only behind a named legacy-compatibility switch,
for example `legacy_ai_state_leak`, off by default (project decision,
2026-10-07). Clean state means every computer player reads shared state
as the first computer player of a run does in the original:

- an empty ship design slot reads as all zero, creation year 0;
- the armada parameters read as 0 unless that computer player set them
  earlier in its own turn.

What this changes for the checked personalities:

- **Robotoid**: nothing measured. It ran first in every captured game,
  so its checks (AI-8, AI-9, AI-12) were taken under clean state.
- **Rototill**: nothing in normal play. It reads design slots 0 and 1
  without a presence check, but it never deletes its starting designs
  (`docs/ai/rototill.md` §4).
- **Cybertron**: its armadas see armada parameters of 0, so every
  Cybertron armada idle at an own planet leaves home instead of waiting.
  This is measured (AI-18: 11 of 11 armada-years with the values at 0).
  In the AIX corpus, where Automitron ran just before Cybertron, the
  original kept these armadas home in 16 armada-years (2452–2460).
  Cybertron's captured orders are matched only with the switch on and the
  original's player order.

Both leaks are documented below as the switch reproduces them.

- **Empty design slots keep the previous player's bytes.** Loading a
  computer player's file marks its unused ship design slots empty but
  leaves the rest of each slot as the previous computer player (in the
  same run) left it. A rule that reads an empty slot's creation year
  without first checking that the slot holds a design therefore reads the
  previous player's design in that slot. For the first computer player in
  the run an empty slot reads as all zero, creation year 0: loading the
  host file does not touch this table (BINARY-ONLY; that no other load
  precedes the first computer player is inferred). Known readers:
  - Macinti's warship rule reads slot `s − 1`'s creation year this way.
    In AIX, Macinti's slot 4 followed Cybertron's slot-3 design (created
    2442), so Macinti did not create slot 4 in 2445–2460 although it
    could build the design every year (Scanning lane's Macinti reading;
    the Macinti check matches AIX in 61 of 61 years only when this is
    modelled). MEASURED by an edit test (AI-13): with only Cybertron's
    slot-3 creation year moved from 2442 to 2428, Macinti created slot 4
    (a Cruiser) in 2449 in both random streams tried, while Cybertron's
    own orders were unchanged. In AIX the leaked year decides Macinti's
    slot-4 rule in 16 of 61 Macinti player-years (2445–2460). Because all
    players share one random stream, the change then spread to other
    computer players' orders in later years. Details in docs/ai/macinti.md
    (planned).
  - Robotoid's slots 12 and 13 test the previous slot's age without a
    presence check (docs/ai/robotoid.md §2). Robotoid is often the first
    computer player in a run, as in AIX, where this never mattered.
  - Cybertron checks presence first and is not affected.
- **Armada parameters.** The armada potency and size and the two values
  derived from them (§11 "Armada (invasion) fleets") are shared values
  that Robotoid, Turindrone, Automitron and Macinti set during their own
  turns (Robotoid's potency starts at 4, Macinti's at 6). Cybertron's
  armada targeting reads them but never sets them (its own copies are
  never read). So Cybertron uses the values left by the last of those
  computer players that ran before it in the same run, or all 0 when none
  did. In AIX, Automitron runs just before Cybertron, so the values
  happened to match Cybertron's own formulas. MEASURED by an edit test
  (AI-18): when Robotoid, Turindrone and Automitron submitted their
  captured orders without their computer-player turns running, the
  values stayed 0. Every Cybertron armada idle at an own planet then left
  home (11 of 11 armada-years in AIX 2453–2460), where with Automitron's
  values all stayed. In AIX the values decide this in 9 of 61 Cybertron
  player-years (2452–2460, 16 armada-years).

All computer players in one host run also draw from one shared random
stream, in player order. So any change to an earlier computer player's
turn shifts the draws of every later one (MEASURED, AI-18: skipping
Robotoid's turn alone changed 17 to 19 of Cybertron's random-dependent
order lines). The switch does not change this: Elegy runs the computer
players on one shared stream in player order either way, and only the
two leaks above depend on the switch.

## 2. Own-planet order (BINARY-ONLY)

Every per-planet pass of a computer player walks its planets in one
shuffled order, made once per turn: start from its planets in planet-id
order, then for `i = 0 .. n−2`: `j = i + Random(n − i)`, swap `i` and `j`.
In a tutorial game there is no shuffle.

## 3. Built-in races (CONFIRMED, AI-0, for 23 of 24; SS harder BINARY-ONLY)

A definition-file line `# TYPE LEVEL` makes a computer player: TYPE 1–6
as in the table above, LEVEL 1–4 = easy, standard, harder, expert; 0 for
either means random (`UNIVERSE.md` "Computer players"). Each type × level
has a fixed race. Each row's status covers all of its values: CONFIRMED
rows were matched field by field against computer players in oracle game
files (UG corpus, 73 players, plus AIX and AI01, 12 players: 85 players,
23 of the 24 combinations, no mismatch); the Turindrone harder row was
never drawn and is read from the original program only.

Columns: lesser racial traits; growth rate; habitability ranges
(gravity / temperature / radiation in the race wizard's 0–100 click
scale, centre = midpoint; imm = immune); colonists per resource;
factories (resources per 10 factories / resource cost / factories per
10,000 colonists); mines (kT per 10 mines / resource cost / mines per
10,000 colonists); research cost per field (energy, weapons, propulsion,
construction, electronics, biotech: c cheap, n normal, x expensive);
"factories cost 1 less germanium"; "expensive fields start at tech 3".
Built-in names are not listed (`UNIVERSE.md`: 24 built-in names).

| Type | Level | PRT | LRT | Growth | Hab | Col/res | Factories | Mines | Research | Fact. Ge −1 | Exp. start 3 | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HE | easy | HE | IFE MA CE OBRM BET | 5% | imm / imm / imm | 1000 | 12/10/16 | 10/5/10 | n n c n n x | no | no | CONFIRMED |
| HE | standard | HE | IFE MA CE OBRM | 6% | imm / imm / imm | 900 | 13/9/16 | 10/4/11 | n n c n n x | no | no | CONFIRMED |
| HE | harder | HE | IFE UR MA OBRM | 6% | imm / imm / imm | 800 | 13/9/18 | 10/4/12 | n c c c n x | yes | no | CONFIRMED |
| HE | expert | HE | IFE UR MA OBRM | 7% | imm / imm / imm | 800 | 13/9/16 | 10/4/8 | n c n c n x | yes | no | CONFIRMED |
| SS | easy | SS | IFE ARM MA RS | 14% | 27-89 / 7-63 / 35-95 | 1000 | 9/10/9 | 9/5/8 | n x n n n x | no | no | CONFIRMED |
| SS | standard | SS | IFE ARM MA RS | 14% | 32-92 / 6-60 / 26-96 | 1000 | 10/10/10 | 10/5/9 | n n n n n n | yes | no | CONFIRMED |
| SS | harder | SS | IFE ARM MA RS | 14% | 31-95 / 4-52 / 30-94 | 900 | 11/10/10 | 10/5/9 | x n x n n n | yes | no | BINARY-ONLY |
| SS | expert | SS | IFE ARM MA RS | 15% | 31-93 / 5-53 / imm | 800 | 15/10/25 | 10/5/9 | x x x x x x | yes | yes | CONFIRMED |
| IS | easy | IS | GR CE OBRM NAS LSP | 15% | 7-63 / 26-94 / 5-71 | 900 | 11/10/14 | 11/6/14 | x x x x x x | no | yes | CONFIRMED |
| IS | standard | IS | GR CE OBRM NAS LSP | 15% | 7-63 / 26-94 / 5-71 | 800 | 13/9/14 | 10/6/14 | x x x x x x | yes | yes | CONFIRMED |
| IS | harder | IS | GR OBRM NAS LSP | 15% | 7-63 / 26-94 / 5-71 | 800 | 14/9/15 | 14/5/15 | x x x x x x | yes | yes | CONFIRMED |
| IS | expert | IS | GR OBRM NAS LSP | 16% | 7-63 / imm / 0-100 | 800 | 14/9/14 | 14/5/14 | x x x x x x | yes | yes | CONFIRMED |
| CA | easy | CA | TT CE OBRM NAS LSP BET | 15% | 32-68 / 31-69 / 31-69 | 1000 | 10/10/10 | 10/5/10 | x x x x x c | no | yes | CONFIRMED |
| CA | standard | CA | TT OBRM NAS LSP BET | 15% | 32-68 / 31-69 / 31-69 | 800 | 12/10/12 | 14/5/12 | x x x x x c | no | yes | CONFIRMED |
| CA | harder | CA | TT OBRM NAS LSP BET | 15% | 23-77 / 24-76 / 25-75 | 800 | 12/10/12 | 14/5/12 | x x x x x c | no | yes | CONFIRMED |
| CA | expert | CA | TT OBRM NAS LSP BET | 15% | imm / 24-76 / 25-75 | 800 | 15/10/15 | 15/5/15 | x x x x x c | no | yes | CONFIRMED |
| PP | easy | PP | IFE TT OBRM LSP | 12% | 22-78 / 22-78 / 22-78 | 1000 | 9/18/9 | 9/10/8 | n x x n x x | no | yes | CONFIRMED |
| PP | standard | PP | IFE TT OBRM NAS LSP | 17% | 19-81 / 19-81 / 19-81 | 1000 | 10/13/19 | 10/10/7 | n x x n n n | no | yes | CONFIRMED |
| PP | harder | PP | IFE TT MA OBRM NAS LSP | 17% | 18-82 / 18-82 / 18-82 | 1000 | 14/10/20 | 10/10/6 | n n x n n c | yes | yes | CONFIRMED |
| PP | expert | PP | IFE TT MA OBRM NAS LSP | 19% | 17-83 / 17-83 / 17-83 | 1000 | 15/9/25 | 10/10/5 | c c x c n n | yes | yes | CONFIRMED |
| AR | easy | AR | IFE TT ISB GR CE | 10% | 20-80 / 20-80 / 20-80 | 1600 | 10/10/10 | 10/5/10 | n n n n x n | no | no | CONFIRMED |
| AR | standard | AR | IFE TT ISB GR | 14% | 15-85 / 15-85 / 15-85 | 1200 | 10/10/10 | 10/5/10 | c n n n x n | no | no | CONFIRMED |
| AR | harder | AR | IFE TT ARM ISB GR UR MA | 17% | 15-85 / 15-85 / 15-85 | 1000 | 10/10/10 | 10/5/10 | c n n n n n | no | no | CONFIRMED |
| AR | expert | AR | IFE TT ARM ISB GR UR MA | 20% | 15-85 / 15-85 / 15-85 | 1000 | 10/10/10 | 10/5/10 | c n n c n n | no | no | CONFIRMED |

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
starbase rules (docs/ai/macinti.md, planned).

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
race can build. There are 45 classes, 0–44. Parts are named as in
`COMPONENTS.md`. Classes 34–38, 0,
9, 10, 11, 17 and 19 are used by starbases; the rest by ship designs
(personality files).

**Mystery Trader items (BINARY-ONLY).** "The race can build" is one test
for parts and hulls, for starbase and ship designs alike: the race's
traits allow the item (`COMPONENTS.md` "Who can build what"), each of the
player's six tech levels meets the item's requirement, and, for a
Mystery Trader item, the player owns it. Ownership alone is not enough:
Trader items have tech requirements like any other part
(`data/components.json`). So a computer player that owns a Trader part
takes it, ahead of the rest of the class's list, once its tech meets the
part's requirements; a Trader part it does not own is never taken. The
hull test is the same, so an owned Trader hull would count, but Mini
Morph is the only Trader hull and no design rule of Robotoid, Rototill
or Cybertron names it: their ship designs use Privateer, Meta Morph,
Frigate, Destroyer, Cruiser, Battleship, B-52 Bomber and Nubian hulls,
Rototill creates no ship designs, and starbases use Space Station and
Orbital Fort. No oracle run has had a computer player design with a
Trader item.

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
| 40 | Orbital Construction Module |
| 41 | Mega Poly Shell, Jammer 50, Jammer 30, Jammer 20, Jammer 10, Overthruster, Maneuvering Jet, Beam Deflector, Super Fuel Tank, Fuel Tank |
| 42 | Alien Miner, Robo-Ultra-Miner, Robo-Super-Miner, Robo-Maxi-Miner |
| 43 | Alien Miner, Robo-Ultra-Miner, Robo-Midget Miner |
| 44 | Galaxy Scoop, Trans-Galactic Mizer Scoop, Trans-Galactic Super Scoop, Trans-Galactic Fuel Scoop, Sub-Galactic Fuel Scoop, Fuel Mizer |

## 6. Hubs: the AI's private memory (BINARY-ONLY)

A computer player builds a list of up to 64 *hubs* during its turn: each
a planet with up to 8 freighter fleets assigned. The list starts empty
every year (§1), so it is rebuilt from the player's own state each time.
Robotoid, Turindrone, Automitron and Rototill build it from year index 20:

1. Drop hubs whose planet the player no longer owns (with the list
   starting empty, this never matters).
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

1. **Keep fleets moving.** Every own fleet with at least two waypoints
   gets the warp of waypoint 1 re-picked by "Warp choice" (§11). Its
   target and task stay as they are, and only a changed warp makes an
   order. This applies to fleets the personality pass left alone too, so
   a scout heading to a planet at warp 6 can get an order changing only
   its warp to 5 (the same whole-year travel time).
2. **Starbases for hubs** (not Macinti; in a tutorial game only before
   year index 31). Cybertron uses its own rule (docs/ai/cybertron.md §4.3).
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
- **Robotoid (MEASURED, AI-4).** An idle fleet with ships of slot 1 (the
  colonizer) and no slot-0 ships, from year index 5 (from the start when
  player positions are "close"), that finds no planet
  to colonize and no wormhole to explore, and orbits a planet, is
  scrapped. AI oracle: with every planet owned in Robotoid's own view,
  all three idle colonizers at its homeworld were scrapped; with one
  planet left free, one colonizer took it and the other two were
  scrapped, because a planet claimed by one colonizer is not offered to
  the next in the same turn (§11 "Nearest colonizable planet").
- **Robotoid (BINARY-ONLY).** A fleet whose every design is obsolete (a
  ship design in slots 2–15 older than 50 years before year index 120, 70
  before 200, 100 after) orbiting an own planet is scrapped when that
  planet has a starbase, else with chance 1/5 per year.
- **Macinti (MEASURED, AI-5)** scraps its early fleets and repeatedly
  builds and scraps its first colonizer until the year it creates design
  slot 7; docs/ai/macinti.md (planned). The colonizer it scraps in 2401 in
  AIX is the one built in 2400, not a starting ship. Macinti merges its
  fleets every year before its fleet pass (§10 "Merging"), so the scrap
  rules see that turn's merged fleets.
- **Rototill** scraps only an idle empty colony ship it cannot send home
  and a nearly unfuelled Quick Jump 5 scout (`docs/ai/rototill.md` §3;
  neither seen in 166 player-years).
- The other personalities' scrap rules: their files.

## 9. Internal-only effects (BINARY-ONLY)

- It keeps an internal rounding of minefield sizes in its own reckoning;
  no order results.
- "Computer players form alliances" is read only by personality code
  (`KERNEL.md`); see the personality files.

## 10. Ship designs (BINARY-ONLY unless noted)

Personalities create ship designs into their own slots; which slot, when,
with which hull and class lists is in each personality file. They all use
the same builder and the same upkeep.

**Builder.** A ship design is built the way §5 builds a starbase, every
hull slot at its maximum count, with no variant reduction: the hull must
be available to the race (`COMPONENTS.md` "Who can build what"), and each
hull slot takes the first part of its AI part class (§5) that the race
can build now. Any slot without a part means no design (and no random
draws). A personality's class list names one class per hull slot.

**Storing a design.** Writing a design into a slot is a design order.
If the slot still holds a design, a delete order for that slot is
written first, then the new design. Personalities replace a slot only
when no ship of its design is alive. If creation then fails, nothing
more is written: a slot deleted on the way (by an explicit delete or
the ageing rule below) stays empty. The stored design's creation year
is the current year.

**Picture.** The first of the hull's four pictures not used by another
non-empty ship design of the same hull (the design being replaced still
counts), else `Random(4)`.

**Name.** Up to 20 tries of `Random(n)` from a built-in name group for
the hull's role, until the name differs from every non-empty ship
design's name (any hull; the design being replaced counts); after 20
failures `Random(100)` then `Random(n)`, the name with that number
appended, unchecked. Groups (n): cruisers to dreadnoughts 16, destroyers
16, scouts and frigates 10, bombers 12, freighters 8, miners 8,
Privateer/Rogue/Galleon 8, colony ships 8, everything else (fuel
transports, mine layers, Nubian, Mini/Meta Morph) 8. Elegy may use its
own names.

**Ageing.** A personality checks a group of its slots each year with an
age limit `L`. For each non-empty slot in the group: the group's
*newest* design is the one with the latest creation year (ties: the lower
slot), chosen before any deletion. A design older than `L` years
(`year index − creation > L`) with no ship alive is deleted (a delete
order); one older than `L` with ships alive is marked *obsolete* for the
fleet rules. The check reports the ships alive in the group (at most
32,000). Robotoid uses `L` = 50 before year index 120, 70 before 200, 100
after.

**Splitting obsolete ships out.** While the player owns at most 500
fleets: the first own fleet (fleet order) holding both marked and
unmarked designs is split; the marked designs' ships move to a new fleet
at the same place with the same waypoints and battle plan, cargo is
balanced between the two, and the scan restarts. The unmarked ships keep
the old fleet.

**Merging.** For a set of slots: walking own fleets in fleet order, every
fleet with ships of those slots (except fleets already at the maximum
mining rate) is merged into the first such fleet at the same place
(same orbited planet, or same position in space). Up to 32 places are
tracked per pass; further places get another pass. Other designs in the
fleets merge along. A merge removes the merged fleet from the fleet list and closes the gap,
so the walk then skips the fleet that followed it (LEGACY BUG,
BINARY-ONLY: not exercised in AIX).

**Queueing items.** A personality adds production items through the same
production list a human sees: an item the planet cannot build (for
example a ship design without a starbase able to build it) is not added,
and a count is clamped to what that list allows. A queue with more than
200 items gets nothing more. Items go to the front, the back, or replace
the queue, as each rule says.

## 11. Shared fleet rules (BINARY-ONLY)

The personality files call these by name. Distances are between
positions in light-years; "nearest" compares squared distances with a
strict `<`, so on ties the first in scan order wins (planets in id order,
fleets in fleet order). A *move order* replaces the fleet's route: it
keeps waypoint 0 and sets waypoint 1 to the target with the given task
and warp, dropping any later waypoints; if the fleet is already at the
target, the task goes on waypoint 0 and the route is cut to that one
waypoint. When the existing waypoint 0 lies at the fleet's position, the move
order overwrites it in place (BINARY-ONLY).

**Supplies.** When a rule loads colonists or minerals between a planet
and a fleet, the planet and fleet change at once in the computer player's
own picture of the game, so later steps of the same turn (for example
starbase queueing in §7) see the moved cargo. A load is limited to what
the source holds and the target can take. Warp 4 below means the waypoint's warp is written as 4 and later
reset by the warp rule at the end of the turn.

**Fleet classes.** Hull roles: freighters (Small to Super Freighter),
privateers (Privateer, Rogue, Galleon), warships (Destroyer to
Dreadnought), Frigate, Nubian, Meta Morph. A design's *power* is the
same per-design power the score uses (`KERNEL.md` "Scores and victory
conditions", the "Power of a design" list: beams, torpedoes and bombs,
with capacitors and battle speed). The computer player computes it at the
start of its turn for every design in its own view, including other
players' designs it knows (BINARY-ONLY that the AI reads the same value;
the formula is CONFIRMED at the score class boundaries KX-003 reached,
with capacitors and sappers BINARY-ONLY and the speed term CONFIRMED by
OT-6).
- *Attack fleet*: walking its designs in slot order (slots with ships
  only): a warship → yes; a Frigate → yes if its power > 0, else **no,
  stop looking** (LEGACY BUG candidate: an unarmed frigate slot hides a
  later warship slot); a Nubian or Meta Morph with cargo capacity below
  500 and power > 0 → yes; otherwise continue. None → no.
- *Transport fleet*: any freighter or privateer design → yes; a Meta
  Morph with cargo capacity ≥ 500 and power > 0 → yes; otherwise no. (An
  unarmed Meta Morph freighter is neither.)
- *War-fleet strength* (Robotoid's armada rule): `strength = ships in
  slots 2–5 + 2 × ships in slots 6–7`. It is "too weak" when `strength <
  P` (the personality's armada potency). Turindrone calls the same rule
  for its bomber check, where slots 2–7 are not its warships (see
  `docs/ai/turindrone.md`): LEGACY BUG, reproduced as written.

**Nearest colonizable planet.** Candidates are planets unowned in the
player's own view (§1: a planet never scanned counts as unowned) that no
other own fleet is already heading to (its waypoint 1 is that planet:
for Robotoid and Macinti only when that waypoint's task is colonize; for
the others any task). Robotoid and Macinti take any unowned planet,
including planets they have never seen. The others take only planets in
their view (their turn file or history file, §1) and skip planets whose
habitability for the race, after the terraforming the player could
currently do, is negative (MEASURED for Rototill, AI-16: ignoring the
test, using present habitability, or dropping history-only planets each
breaks the Rototill replay).
The nearest candidate to the fleet wins. Robotoid and Macinti recompute
the marks for every fleet, so a colonize order given earlier in the turn
already excludes its planet. The others compute the marks once per turn;
the search itself never marks the planet it returns, so the personality
marks each chosen planet itself, and later fleets that turn skip it:
Rototill (`docs/ai/rototill.md` §3 pass 2, BINARY-ONLY: AI-16's replay
includes the mark, but no variant without it was tested), Cybertron
(`docs/ai/cybertron.md` §5, MEASURED, AI-21: without the mark 184
fleet-years differ) and Turindrone (`docs/ai/turindrone.md` "Fleet pass",
MEASURED, AI-22: dropping it breaks 8). A wormhole choice marks nothing
(BINARY-ONLY). Then, if
the fleet orbits an own planet and the year index is below 120, a
wormhole may be preferred: wormholes within twice the candidate's
distance (any distance when there is no candidate) score
`(7 − its movement class)·10` when known to the player, else 90 when
no farther than the candidate or 50 otherwise; the best (ties: nearer) is
taken if `Random(100)` is below its score. (LEGACY BUG: the distance test
overflows for wormholes about 182 ly or more away, which then count as
near.)

*Wormhole distance arithmetic (LEGACY BUG, BINARY-ONLY).* The
candidate's squared distance `D` is exact: a 32-bit integer, or
99,999,999 when there is no candidate. For each wormhole end, the squared
distance `w` comes from 16-bit integers:

1. `ax = |fleet x − end x|` and `ay = |fleet y − end y|`, from the integer
   map coordinates. Nothing is truncated, because the coordinates and
   differences fit a signed 16-bit value.
2. Keep the low 16 bits of each square, then add the two values modulo
   65,536: `u = (ax·ax + ay·ay) mod 65,536`.
3. Read `u` as a signed 16-bit value: `w = u` when `u < 32,768`, else
   `w = u − 65,536`. This is a wrap, not a saturation.

Every later test uses `w`, signed, against 32-bit values:

- The end is considered only if `w ≤ 4·D`.
- A second test, `w ≤ 46,656` (216²), always passes, because `w` never
  exceeds 32,767.
- The score of an end the player does not know is 90 if `w ≤ D`, else
  50.
- Among equal scores the smaller `w` wins.

So a true squared distance from 32,768 to 65,535 (about 182 to 255 ly)
gives a negative `w`. That end passes both distance tests, scores 90 when
unknown, and wins ties against any correctly measured end. Larger
distances wrap again: at exactly 256 ly in x, `w` = 0.

**Colonize order.** Move order to the planet, task colonize, warp = the
fleet's ideal warp. **Wormhole order**: move order to the wormhole, no
task.

**Nearest own starbase.** From the fleet's waypoint-0 position, the
nearest own planet with a starbase (optionally only with more than 25,000
colonists): move order there, no task, warp 4. None: no order.

**Random nearby planet** (scout moves). A uniform pick among planets
within radius `r` (inclusive; reservoir draw `Random(k)` for the k-th
candidate, the first included). With the avoid-starbase option, a pick
that has a starbase is redrawn up to twice (fresh passes); the last pick
stands.

**Join a buddy.** Among own fleets earlier in fleet order (LEGACY BUG
candidate: later fleets are never considered) holding ships of the given
slots, the nearest: within `r1` → join; within `r2` → join if
`Random(2) != 0`. Joining clears the fleet's waypoint-0 task and gives a
move order to that fleet, no task, warp 6.

**Attack target.** For an attack fleet with a list of own fleets and a
list of other players' fleets (and, when "computer players form
alliances" is on, skipping fleets owned by computer players):
1. For each enemy fleet in list order: let `n` = ships of own fleets
   (other than this one) already targeting it. If `n > 0`, skip it with
   `Random(3) == 0`; then if `5n` exceeds this fleet's ship count, skip it
   with `Random(15) == 0`. Keep the nearest (within 1,000 ly).
2. Nearest within 180 ly: target that fleet.
3. Farther: if the fleet has less than half its fuel and can reach an
   own starbase (rule above), go there instead. Else the planet nearest
   that enemy fleet that no other own fleet targets; if it is not the
   current orbit, target it.
4. No enemy fleet: with the alliance option, retry without skipping
   computer players' fleets. Then the nearest other player's planet; else
   the nearest planet the AI has not marked as visited; else a random
   planet (`Random(planet count)`).
5. If the fleet already heads to a planet and the new target is a
   planet, keep the current route. Otherwise move order, no task, warp 4.

**Armada (invasion) fleets.** Slots 9 and 10 carry troops (colonists);
`strength` as above; personality parameters `P` (potency), `P/2`, `A`
(armada size) and `min(3, A/2 − 1)`.
- An armada already chasing a fleet within 250 ly, or heading to a
  foreign planet, or to an own planet with a starbase, or to a planet not
  seen this year, keeps its route.
- Not orbiting a planet: move to the nearest planet of another player
  within 150 ly, else the nearest object of interest.
- At an own planet with a starbase: if too weak (strength < `P` or
  troop ships < `A`): easy and standard wait; otherwise launch anyway by
  chance (`Random(10) < 5` when strength > `P`·2 or ≥ 60; else `Random(10)
  < 7` when > `3P`; else when > 120 and `Random(10) < 7`; draws only as the
  tests are reached). If strong enough: load colonists (a tenth, fifteenth
  or twentieth of the planet's population above 300,000, 200,000 or
  100,000) and launch.
- Elsewhere and too weak (strength < `P/2` or troops < `min(3, A/2 −
  1)`): clear the waypoint-0 task; harder and expert may still launch by
  chance (as above, thresholds `2P`, `4P`, 120); otherwise retreat to the
  own starbase planet nearest to here.
- Elsewhere and strong: unowned planet → launch; own planet without
  starbase → load a fifth of its population if it has more than 100,000,
  then launch; another player's planet → invade if the troops suffice,
  else do nothing this turn (BINARY-ONLY). With `g` the planet's
  population estimate and `e` its defense coverage estimate, as the
  player's report holds them (`SCANNING.md` "What a planet report
  contains"; `g` in units of 400 colonists, `e` 0..15), and `c` the
  armada's colonist cargo in kT (units of 100 colonists):
  - defense % `= ⌊(e + 1)·18/4⌋` (4 for `e` = 0, 72 for 15);
  - `need = ⌊g·400 / (100 − defense %)⌋`, in colonists;
  - invade when `need < ⌊c/5⌋`, or `need < 200` and `c > 350`, or
    `need < 10` and `c > 150`;
  - drop `min(max(⌊c/2⌋, ⌊5·need/4⌋), c, 30000)` kT of colonists.
  The tests and the drop use `need` (colonists) and `c` (kT) as plain
  numbers, with no conversion between them, as read. UNRESOLVED: whether
  the game really behaves this way (a probable unit slip) until an oracle
  check of an armada invasion exists. No move that turn.
- *Launch target*: the best-scoring planet other than here among those
  with an AI threat mark (§ personality files), score = threat + 7, 5, 4,
  3, 2 or 1 for within 50, 100, 150, 200, 300 or 500 ly; a planet already
  chosen this turn is considered only with `Random(4) == 0` and then
  outranks all others (LEGACY BUG candidate). With "computer players form
  alliances", planets of human players are tried first. Ties: nearer.
  None: the nearest other player's fleet. Move order, no task, warp 4.

**Hub freighters.** A transport fleet works for one *source* planet (its
hub, or the player's first planet with a starbase):
1. The source's scarce mineral: the lowest of Ir/Bo/Ge; mode 0 normal, 1
   when it is under half of a reference value, 2 under a quarter (the
   reference is the minimum before the last update of the running
   minimum, which is not always the second-lowest: LEGACY BUG).
2. Every planet gets a score (0 = not a target), using travel time
   `t = max(1, (distance + 24)/25)` years; planets other fleets of this
   fleet's first design already target are skipped:
   - the source itself (when not there): 25,000 if the fleet is full,
     else `20 × percent full / t`, skipped under 35 %;
   - own planets without starbase and not building a starbase: the
     minerals there (mode 2: the scarce mineral only; mode 1: the scarce
     one in full plus half the others; mode 0: all), as a percent of
     capacity capped by the room left, `× 100 / t`; under 10 kT skipped;
   - unowned planets the AI marked for pickup, and (Robotoid) small
     foreign colonies when the source is crowded: fixed values over `t`.
   - salvage within 200 ly (LEGACY BUG: the box test misses the absolute
     value, so far salvage up or right qualifies); salvage exactly here
     is loaded at once.
3. Move order to the best: task transport. The Ir, Bo and Ge orders
   (MEASURED for Robotoid, AI-26; other personalities and the mode 1
   unowned case BINARY-ONLY):
   - at the source: unload all of each;
   - elsewhere in mode 0: load all of each;
   - elsewhere in mode 2: load all of the scarce mineral, no order for
     the other two;
   - elsewhere in mode 1: the same as mode 2 when the target holds at
     least as much of the scarce mineral as the fleet's free hold (taken
     before any salvage pickup at the fleet's position: BINARY-ONLY). If
     not, at a planet owned by any player (its own or another player's),
     "fill to 66 %" for the scarce mineral and "fill to 33 %" for each
     of the others. At an unowned planet, load all of each.

   "Fill to `v` %" is a percent of the fleet's whole cargo hold: it wants
   `v` % of the hold minus what of that mineral is aboard (the
   subtraction is BINARY-ONLY), and the minerals load in the order Ir,
   Bo, Ge until the hold is full (KERNEL.md "Other movement rules",
   "Which loads are unmet"; PARITY FO-01..FO-07, "Transport amounts and
   clamps": fill to 50 % of an empty 210 kT hold loaded 105, and
   load all of Ir and Bo from 150/150 into an empty 210 kT hold took
   150 Ir and 60 Bo). This step writes no colonist or fuel order;
   colonist orders come only from the personality rules below.
   Personality colonist rules: Turindrone carries 100,000 colonists from
   a crowded source to smaller own planets; Robotoid moves part of the
   source's population to small own colonies and carries 10,000–30,000
   to foreign targets. Salvage targets get no task (LEGACY BUG: their
   load orders do nothing).

**Warp choice** (CONFIRMED, AI-11). At the end of each personality's
fleet work (§7 step 1), every own fleet with at least two waypoints, in
fleet order, gets its waypoint-1 warp re-picked. Target and task are kept,
and an order is written only when the warp changes.
- **Minefields.** For this test, and for the whole turn, the computer
  player sees every minefield as larger than it is: a field of `n` mines
  counts as `⌊√n + 10.5⌋²` (about 10 ly more radius). A fleet inside
  another player's enlarged field (squared distance below that count;
  the first such field in object order) gets: heavy field 6; standard
  field 4 when `Random(10) < 4`, else 5; plus 1 for an SS race. Speed
  bump fields are not considered.
- **Otherwise**, with `ideal` the fleet's ideal warp (`ESTIMATES.md`
  "Fleets") and `raw` the same without the free-warp step-down:
  1. Start from 9 and step down while the warp is above `ideal` and the
     fuel needed to reach waypoint 1 at that warp (the waypoint fuel
     estimate of `ESTIMATES.md` "Fleets") exceeds the fleet's fuel. If `ideal` is 9
     or more, start at `ideal`.
  2. Cap at `raw`, unless waypoint 1's task is colonize or scrap, a ship
     carries a colonization or orbital construction module, or a planet
     lies exactly at waypoint 1's position that the player owns and whose
     starbase slot holds a design other than an Orbital Fort (the slot is
     read even when the planet has no starbase).
  3. Unless waypoint 1 targets a fleet: with `d` = the whole light-years
     from waypoint 0 to waypoint 1, lower the warp while one less (not
     below 2) still gives the same `⌈d / warp²⌉` years.
  4. A stargate route gives 11 (not yet observed).
- Example (AI oracle round 2): a lone Scout with Long Hump 6, 18 ly from
  its target at warp 6, is rewritten to warp 5, which also takes one year.

## Open experiments

Settled by the stage-1 games (`PARITY.md` "Computer players: stage 1"):
AI-3 and AI-5 on further games and levels, AI-4, and the Easy, Standard
and Harder levels of AI-1 and AI-2. Still open:

- §7 planet automation as predictions (AI-7, not run): needs Elegy's
  production and mining estimates to predict queue contents exactly.
- Turindrone harder race (never drawn in UG).
- The "dormant" flag (§1).
