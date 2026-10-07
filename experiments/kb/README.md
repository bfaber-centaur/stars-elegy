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

Random events off for KB1-A and KB1-B; cycles 20000 and 3700. The values
below are the end-of-year state. "Rules out" names the reading that each
case would expose.

### KB1-A (`kb1a.spec`)

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

### KB1-B (`kb1b.spec`)

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

### KB1-C (`kb1c.spec`): mining's random +1, by replaying the stream

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
