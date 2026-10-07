# KB: closing KERNEL.md's BINARY-ONLY rules

Each batch takes a group of `docs/KERNEL.md` rules that are still tagged
BINARY-ONLY and tests them with one pinned year per case from the CB base
(2400, two JOAT players). Predictions are committed here before the runs.
`kbmodel.py` computes them from the public rules alone. `run-kb.sh` builds
the starts and runs them. Raw output goes to the private apparatus
repository.

Races are checked for legality first: `combatlab dump` prints each player's
advantage points (`points=`), and every start here is at 0 or more. A
negative total makes the host degrade the race at the start of the year,
which changes colonists per resource and so every resource figure.

## Batch 1: population, resources, mining, AR, remote mining

Random events off for KB-1A and KB-1B; cycles 20000 and 3700. The values
below are the end-of-year state. "Rules out" names the reading that each
case would expose.

### KB-1A (`kb1a.spec`)

Player 0 is JOAT with Only Basic Remote Mining (OBRM). Player 1 is JOAT
with habitat 40–60 on every axis and tech 26. Growth rate 15%, colonists
per resource 1000, factory output 10.

| Planet | Setup | Predicted | Rules out |
|---|---|---|---|
| 13 (P0) | 70/50/50, pop 10,430 | hab 79, maximum `7900 + 1580 = 9480 + 948 = 10,428`, so the population is frozen: 10,430, carry 0 | maximum 10,270 (bonuses added to the base): 10,421, carry 66; a hab other than 79 |
| 9 (P0) | 50/50/50, pop 45,000 (maximum 13,200), 10 factories | effective population `min(26,400, 29,100) = 26,400`, resources 2,650; population 40,662, carry 0 | no `2·max` limit: resources 2,920 |
| 12 (P0) | ironium concentration 4, 500 mines, pop 5,000 | ironium +20 kT, concentration 4, fraction 251 (clamp 10 below 5); boranium and germanium +500 kT each, concentration 97, fraction 12; pop 5,515 | the clamp 25 below 5: fraction 245 |
| 16 (P0) | 95 defenses, Auto Defenses ×100, pop 5,000, 1000 kT each | builds 5: 100 defenses; minerals 975 each; 425 resources left over | no cap of 100 on maximum defenses: about 33 built |
| 17 (P0, homeworld) | as the base | pop 287, carry 50; resources 35 | |
| Player 0 research | all planets but 16 have no queue | 35 + 2,650 + 500 + 1,042 + 425 = 4,652: energy 3 → 8, 222 stored | no `2·max` limit: 4,922, 492 stored |
| 10 (P1) | 90/50/50, pop 1,000, 5 defenses, Auto Defenses ×100, 100 kT each | hab −15 (each axis outside the range counts at most 15): pop 985, carry 0. Maximum defenses `max(10, −60) = 10`: builds 5, ends with 10 defenses, 75 kT each | uncapped hab −30: pop 970; no floor of 10: no defenses built |
| 11 (P1) | 90/90/50, pop 1,000 | hab −30: pop 970, carry 0 | uncapped −60: pop 940 |
| 14 (unowned) | 68/78/76, remote-mined by player 1: 80 Mini-Miners with 2 Robo-Super-Miners each (4,320 robot points) | the fleet's rate is capped at 4,000: +2,720 / +3,120 / +3,040 kT; concentrations 55 / 61 / 60, fractions 147 / 159 / 114 | no cap: +2,937 / +3,369 / +3,283 kT |

### KB-1B (`kb1b.spec`)

Player 1 is Alternate Reality at tech 26, with No Advanced Scanners, Low
Starting Population, Bleeding Edge Technology and No Ram Scoop Engines to
keep the race legal (198 points). None of these acts in this year.

| Planet | Setup | Predicted | Rules out |
|---|---|---|---|
| 13 | Orbital Fort, pop 2,505, hab 100 | maximum 2,500: frozen at 2,505 | a habitability maximum (10,000): 2,880 |
| 9 | Space Dock, pop 5,005, 80/80/80 (hab 3) | maximum 5,000: frozen at 5,005 | habitability maximum 500: 4,404 |
| 12 | Space Station, pop 10,005; Auto Mines, Auto Factories, Auto Defenses ×10; a player 1 Mini-Miner (8 robot points) in orbit with the remote-mining task | frozen at 10,005. Nothing built: mines, factories and defenses stay 0, and the queue is unchanged. Mines `100 + 8 = 108`: ironium +16 (+1 with chance 20%), concentration 15, fraction 247; boranium +88 (+1 at 56%), 82, fraction 107; germanium +48 (+1 at 60%), 45, fraction 211 | AR builds installations; the miner not added: +15 / +82 / +45, fractions 248 / 117 / 214 |
| 10 | Ultra Station, pop 20,005 | maximum 20,000: frozen | maximum 10,000: 19,196 |
| 11 | Death Star, pop 30,005 | maximum 30,000: frozen | maximum 10,000: 27,592 |
| Player 1 score record | | resources R (after growth) 8,054, with planet 9's AR resources taking `max(25, hab) = 25` | no floor of 25: 7,803 |

### KB-1C (`kb1c.spec`): mining's random +1, by replaying the stream

Random events on (option byte 0x40). Five non-homeworld planets with 10
mines each have concentrations that leave a non-zero remainder on every
mineral (15 draws), and each homeworld's germanium adds one (17 draws in
all). The binary reading: after the player-order shuffle (2 draws), one
`Random(100)` per mineral with a non-zero remainder, planets in id order,
then ironium, boranium, germanium; the mineral gains 1 when the draw is
below the remainder. The random events then start at draw 19.

Predicted surface gains (ironium/boranium/germanium, kT) for each cycles
value, by replaying the stream of the startup tick it reaches
(`docs/ORACLE.md`):

| Cycles | Tick | Planet: gains | Random events |
|---|---|---|---|
| 20000 | 164 | 0: 3/6/10, 1: 2/5/8, 2: 7/2/1, 4: 3/9/1, 5: 4/1/6, 8: 3/3/9, 17: 3/3/9 | none |
| 35000 | 109 | 0: 3/6/9, 1: 1/4/8, 2: 6/3/1, 4: 3/9/1, 5: 4/0/6, 8: 3/3/9, 17: 3/3/9 | none |
| 11500 | 329 | 0: 3/6/9, 1: 1/5/8, 2: 6/3/1, 4: 2/8/1, 5: 4/1/7, 8: 3/3/9, 17: 3/3/9 | none |
| 10500 | 384 | 0: 3/6/9, 1: 1/5/8, 2: 7/3/0, 4: 2/9/2, 5: 4/1/6, 8: 3/3/9, 17: 3/3/9 | none |
| 6000 | 659 | 0: 3/6/9, 1: 1/4/7, 2: 7/2/1, 4: 3/9/2, 5: 4/1/6, 8: 3/3/8, 17: 3/3/9 | none |
| 5200 | 768 | 0: 3/6/9, 1: 1/5/8, 2: 7/3/0, 4: 2/9/2, 5: 4/1/6, 8: 3/3/9, 17: 3/3/9 | none |
| 3700 | 1098 | 0: 4/6/9, 1: 2/5/8, 2: 7/2/0, 4: 3/9/1, 5: 4/1/7, 8: 3/3/8, 17: 3/3/9 | climate change on unowned planet 20, temperature −6 |
| 2190 | 1812 | 0: 4/6/9, 1: 1/5/7, 2: 6/3/0, 4: 3/9/1, 5: 5/1/6, 8: 3/3/9, 17: 3/3/9 | climate change on unowned planet 22, gravity −4 |
| 1985 | 2032 | 0: 3/6/9, 1: 1/5/8, 2: 6/3/0, 4: 2/8/2, 5: 4/1/6, 8: 3/3/9, 17: 3/3/9 | none |
| 1750 | 2306 | 0: 4/6/9, 1: 1/4/8, 2: 7/2/1, 4: 3/9/1, 5: 4/1/6, 8: 3/3/9, 17: 3/3/9 | none |
| 1490 | 2691 | 0: 4/6/9, 1: 2/4/8, 2: 7/2/1, 4: 3/9/1, 5: 4/1/6, 8: 3/3/9, 17: 3/3/9 | none |

If mining started at draw 4 instead of draw 2, 68 of these gains would
differ. The year index is 0, so comets and new minerals cannot act;
climate change can, on unowned planets.

### Batch 1 results

Every prediction held in every stream (KB-1A and KB-1B at cycles 20000
and 3700; KB-1C in all 11 streams), with one refinement:

- KB-1A: populations 10,430 (frozen), 40,662, 5,515, 985 and 970; player
  0 research 4,652 (energy 8, 222 stored); planet 12 fraction 251;
  defenses 100 and 10; planet 14 surface 2,720/3,120/3,040, concentrations
  55/61/60, fractions 147/159/114. Player 1's research was 130, which the
  floor of 10 on maximum defenses gives (205 without it).
- KB-1B: every AR planet frozen at its hull's maximum plus 5; nothing built
  on planet 12, queue unchanged; player 1's yearly resources 8,054. The
  starbase count in the score record was 5 of 6 starbases (the Orbital
  Fort is not counted, as KX-003 found).
- **Refinement (KB-1B planet 12):** the AR planet's own miner did mine it,
  but its boranium fraction ended at 106, not the predicted 107. The
  prediction added the miner's 8 robot points to the planet's 100 mines
  and ran one mining step. Two separate steps, each with its own
  truncation (100 mines, then 8 robot points), give 106; ironium and
  germanium (247, 211) are the same either way. Surface gains
  +16/+88/+48 and +16/+88/+49 fit both.
- KB-1C: every planet's three gains matched the replay in all 11 streams
  (77 results, 17 draws per stream). Climate change hit unowned planet 20
  (temperature 44 → 38) at cycles 3700 and planet 22 (gravity 22 → 18) at
  2190, as replayed; the other nine streams had no event.

## Batch 2: production and research leftovers

Random events off. KB-2A and KB-2C run on the normal base and KB-2B on
the slower-tech base (`0x82`), each at cycles 20000 and 3700. Research
fields that the spec cannot set are applied with `hst-edit` after the build
(it edits player 0's race only). `python3 kbmodel.py kb2a|kb2b|kb2c`
prints every figure below.

### KB-2A (`kb2a.spec`)

Player 1 is JOAT with Ultimate Recycling, No Advanced Scanners, Low
Starting Population and Bleeding Edge Technology (123 points). Every field
is at 3, research goes to energy, and the next field is "same". Player 0
is JOAT at levels 25/0/0/5/5/5, energy current, next field "same", with
85,080 stored in energy.

| Item | Setup | Predicted | Rules out |
|---|---|---|---|
| 13 (P1) | pop 5,000, no queue; 10 Mini-Miners scrapped there, no starbase. Owner cost 241 each: Mini-Miner 47, Quick Jump 5 3, Bat Scanner 1, Robo-Mini-Miner 95 ×2, under BET miniaturization at tech 3. So `x` = 2,410 | resources `500 + trunc(2410·500/2910) = 914`; the scrap message shows 414 | no bonus (500); the full `x` added (2,910) |
| 9 (P1) | pop 3,000, scanner present, queue Planetary Scanner ×1 | item removed (message 0xb9), queue freed (0x3e), 300 resources to research | scanner built or kept in the queue |
| 12 (P1) | pop 2,000, no starbase, queue Ironium packet ×1 | item removed (message 0x129), queue freed (0x3e), 200 resources to research | packet built |
| 16 (P1) | pop 4,000, a queue block holding zero items | no research from it and no production message | its 400 resources go to research |
| P1 research | homeworld 35 + 914 + 300 + 200 = 1,449 | energy 3 → 5, 529 stored | 1,035 (no bonus): energy 5, 115 stored; 3,445 (full `x`): energy 7, 675; 1,849 (zero-item queue counted): energy 6, 179 |
| P0 research | homeworld 35 + planet 10 (pop 11,000) 1,100 = 1,135; `L` = 85,080 + 1,135 − 85,100 = 1,115 left after energy 26 | energy 26. The leftover goes to weapons (lowest, first in field order on ties): weapons 1 (cost 460). Then propulsion as if "lowest": propulsion 1 (470). Then weapons again (lowest tie): 185 stored. Levels 26/1/1/5/5/5, current weapons, next field still "same" | "same" kept after the move: weapons 1, then weapons 2 (500), 155 stored, propulsion 0; the stored choice turned to "lowest" |

The research window that separates the two P0 readings is 980 to 1,459, so
a small error in the resource figure does not blur it.

### KB-2B (`kb2b.spec`)

This is the KX-003 S3L start (PARITY.md, KX-003) on the slower-tech base.
Player 0 is Claim Adjuster researching weapons (355 this year). Player 1 is
Super Stealth (216 points) researching energy (95). Under the normal
setting S3L ended with player 1 at energy 118 and weapons 88.

| Player | Predicted | Rules out |
|---|---|---|
| 0 | weapons 3, stored `ceil(355/2)` = 178 | |
| 1 | own energy `ceil(95/2)` = 48; stolen `s` = 23 (energy) and 88 (weapons), shown in two 0x159 messages; stored with `ceil(s/2)`: energy 60, weapons 44 | full scale: energy 71, weapons 88; halved truncating: energy 59 |

### KB-2C (`kb2c.spec`)

Player 1 is JOAT, immune to gravity, with temperature and radiation 45–55
(700 points). Every field is at 3, so its reach is ±3 on every axis.

| Planet | Setup | Predicted | Rules out |
|---|---|---|---|
| 10 (P1) | 20/47/50, pop 5,000, Terraform ×5 | capacity 3 (gravity immune, temperature 47 → 50, radiation at the centre). The order is cut to ×3 (message 0x12f) and built: 20/50/50, item gone | gravity counted: capacity 6, ×5 kept, gravity moved |
| 11 (P1) | 10/50/50, pop 5,000, Terraform ×2 | capacity 0: the order is removed (0x12f), nothing built, 10/50/50 | units built on gravity |

### Batch 2 results

Every prediction held in both streams (cycles 20000 and 3700 gave the same
files' values).

- KB-2A: player 1's research was 1,449 (energy 5, 529 stored). Message
  0x5c carried 414, and planet 13 gained 378/0/99 kT. Planets 9 and 12
  sent 0xb9 and 0x129, then 0x3e, with their queues freed. Planet 16 sent
  nothing and kept its zero-item queue. Player 0 ended at 26/1/1/5/5/5 with
  weapons current, 185 stored and the next field "same". Its level
  messages named weapons, propulsion and weapons as the field research
  continues in.
- KB-2B: player 1 stored energy 60 and weapons 44, and received 0x159 for
  23 (energy) and 88 (weapons). Player 0 stored weapons 178.
- KB-2C: planet 10 went to 20/50/50, with 0x12f, three clicks and 0x3e.
  Planet 11 stayed at 10/50/50, with 0x12f and 0x3e. The first run is void:
  its race had only the gravity centre at 255. The host repaired that
  (0x117, centre forced to 50) and terraformed gravity. The spec now sets
  centre, low and high to 255, and the rerun is the result above.

## Batch 3: the year-wide random draw order

The year's draws, in the program's order:

1. The player shuffle.
2. Before movement, a tech attempt for each scrap at a starbase (and each
   capture).
3. Mining.
4. The random events.
5. After movement, battles, then a draw for each bombing pass.

KB-1C confirmed the shuffle, mining and events part. KB-3A puts a scrap-tech
attempt, mining, the events and a bombing pass in one year, and predicts
every stream by replaying the random generator from its startup tick (the
replay tool is private; the rules it applies are public).

### KB-3A (`kb3a.spec`)

Random events on, year 2400 (year index 0: a comet or new-minerals draw
picks a planet and does nothing; climate change acts).

- **Scrap at a starbase.** Player 0 (tech 26) scraps a Scout with a Long
  Hump 6 at player 1's planet 12, which has an Orbital Fort. Player 1 is at
  tech 0, so only propulsion is behind what it saw. Its tech attempt draws
  `rand(100)`, and below 50 nothing more. Otherwise it draws 13 `rand(13)`
  Trader tries, with no second draws because no Trader part is involved,
  then up to 6 `rand(6)` until propulsion (2) comes up. A gain adds one
  level's cost to propulsion (level 1) and sends 0x13d.
- **Mining** makes 5 draws: planet 8's germanium, planet 13's three
  minerals (25 mines at 114/97/14), and planet 17's germanium.
- **Events** make at least 3 draws: comet, climate change and new
  minerals.
- **Bombing.** Player 0's Mini Bomber with one LBU-17 (installations 16,
  kill 0.2%, no minimum) orbits player 1's planet 13, which has no
  starbase and mines 25, factories 45, defenses 0. Its population is 880
  and 1,012 after growth. Factories lose `10 + [rand(70) < 20]`. There is
  no defense draw. Mines lose the rest. Population loses
  `2 + [rand(1000) ≤ 24]`.

Predicted, for the streams whose tick is known (`docs/ORACLE.md`). The
last two columns say whether that stream would come out differently if
mining came before the scrap draws ("mine-first") or bombing before the
events ("bomb-first"):

| Cycles (tick) | Player 1 gains | Mining 8, 13, 17 (kT) | Climate | Planet 13 factories, mines, pop | mine-first differs | bomb-first differs |
|---|---|---|---|---|---|---|
| 20000 (164) | none | 3/3/9, 29/25/4, 3/3/9 | — | 35, 19, 1010 | yes | yes |
| 35000 (109) | none | 3/3/9, 28/24/4, 3/3/9 | — | 34, 20, 1010 | yes | no |
| 11500 (329) | propulsion 1 (0x13d) | 3/3/9, 28/25/3, 3/3/8 | — | 35, 19, 1010 | yes | no |
| 10500 (384) | propulsion 1 (0x13d) | 3/3/9, 28/24/3, 3/3/9 | — | 35, 19, 1010 | yes | no |
| 6000 (659) | none | 3/3/9, 29/24/3, 3/3/9 | — | 34, 20, 1010 | yes | no |
| 5200 (768) | propulsion 1 (0x13d) | 3/3/9, 29/25/3, 3/3/8 | — | 35, 19, 1010 | yes | no |
| 3700 (1098) | none | 3/3/9, 29/25/4, 3/3/9 | — | 35, 19, 1010 | yes | yes |
| 2190 (1812) | none | 3/3/9, 28/24/4, 3/3/9 | — | 34, 20, 1010 | yes | no |
| 1985 (2032) | propulsion 1 (0x13d) | 3/3/9, 29/25/4, 3/3/9 | — | 35, 19, 1010 | yes | no |
| 1750 (2306) | none | 3/3/9, 29/24/3, 3/3/9 | — | 34, 20, 1009 | yes | yes |
| 1490 (2691) | none | 3/3/9, 29/25/3, 3/3/9 | — | 35, 19, 1010 | yes | no |

No climate change is predicted in these streams. The run adds 12 cycles
values whose ticks are not yet known (2100, 2060, 2030, 2010, 1230,
1220, 1200, 1180, 950, 940, 720, 580). Startup ticks are
`trunc(k·54.925)`. Under this order, a climate change shows up at k = 35
(planet 10, radiation −7), 58 (planet 7, temperature +4), 74 (planet 20,
temperature +4), 97 (planet 18, gravity −6) and 121 (planet 6,
temperature −5), each with its own scrap, mining and bombing outcome.
Each of those runs is matched against every k from 2 to 150, and a run
whose climate change and other values match one k confirms the order with
a visible event.
