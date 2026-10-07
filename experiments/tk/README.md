# TK: planet takeover corpus (TK-001 to TK-004)

Tests the stars-decomp takeover reading (`docs/takeover.md`,
`docs/takeover-predictions.md` T-1..T-35, `tools/takeover.py`, branch
`claude/project-thread-sgfw6k`, PR #8) against the original game.
Predictions below were committed **before** any TK run.

## Setup

Combat Lab (`docs/ORACLE.md`), one generation 2400 → 2401 per run with the
random stream pinned (`tools/fleetlab/pinned-turn`, cycles fixed 20000
unless stated). Specs: `tkNNN.spec`, written by `gen.py`.

- Player 1 owns every target planet (`planet N owner 1`), with the
  environment set to 50/50/50 (100% habitability for both players' races,
  which are identical JOAT races, growth 15%) and no production queue.
  Player 0 attacks. Mutual enemies unless stated. Player 1 has energy
  tech 3 (best planetary defense: SDI, 1% each) unless stated.
- Bombers orbit the target from the start. Transports and colony ships
  start 20 ly away and arrive this turn (warp 6), so they act after
  movement; "in orbit" means the task is on waypoint 0.
- Population in this document is in **units of 100 colonists** (the
  file's unit). P = population at the start of the turn; P' = population
  after this turn's growth, which happens before bombing and before the
  arrival drops. For an uncrowded 100% planet,
  P' = P + floor((15·P + carry)/100). Planet 5 in TK-001 and TK-003 is a
  growth control.

## Predictions (stars-decomp reading)

Bombing (TK-001, deterministic: no random rounding is needed in these
cases).

| Planet | Case | P → P' | Predicted after the turn | Alternative it rules out |
|---|---|---|---|---|
| 5 | control, carry 37 | 87 → 100 | pop 100, carry 42 | |
| 0 | T-12: 10 Cherry | 800 → 920 | **690** (25% added) | ≈715 if percentages compound |
| 1 | T-10: 1 Lady Finger | 9 → 10 | **7** (minimum 300 colonists) | 9 or 10 without a minimum |
| 2 | T-11: 1 LBU-17 | 9 → 10 | **9** (no minimum; a 0 kill becomes 1) | 7 with a minimum |
| 3 | T-14: 20 Peerless | 1000 → 1150 | **412** (smart bombs multiply: 64.2%) | 0 if they added (100%) |
| 4 | T-14: 20 Peerless | 1 → 1 | **1** (smart bombs never empty a planet) | 0 |
| 6 | T-15: 1 LBU-32, mines 30, factories 30 | 870 → 1000 | pop **997**, mines **16**, factories **16** | |
| 7 | T-6: 20 Cherry, 100 SDI | 870 → 1000 | pop **666**, defenses **0** | 500 with no coverage |
| 9 | T-7: 20 Cherry, 100 SDI | 87 → 100 | pop **42** (only 4 defenses count at 10,000 colonists), defenses 0 | ≈82 if all 100 counted |
| 10 | T-9: 20 Smart, 100 SDI | 870 → 1000 | pop **812**, defenses **100** (half coverage for smart bombs; no installation damage) | 846 at full coverage, 770 at none |
| 11 | T-17: 1 Orbital Construction Module | 87 → 100 | pop **80** (2,000 colonists per module) | 100 if the OCM is not a bomb |
| 12 | T-18: 1 Multi Contained Munition, mines 10 | 87 → 100 | pop **97** (2% → minimum 300), mines **5** | 100, mines 10 |
| 13 | T-16: 3 Retro, env 55/47/52, original 50/50/50 | 87 | environment **52/50/50** (3 clicks per axis) | e.g. 52/50/52 or 50/49/52 if 3 clicks are shared |
| 14 | T-19: plan "nobody" | 800 → 920 | **920** (no bombing) | 690 |
| 15 | T-19: plan "player 0 only" | 800 → 920 | **920** | 690 |
| 16 | T-19: plan "player 1 only" | 800 → 920 | **690** | 920 |
| 22 | T-19: plan "everyone" | 800 → 920 | **690** | 920 |
| 18 | T-20: 3+2 ships (6+4 Cherry), first fleet attacks, second "nobody" | 800 → 920 | **690** (one pass, 25%) | 704 (two passes) |
| 19 | T-20: same, first fleet "nobody", second attacks | 800 → 920 | **828** (the earlier non-attacking fleet is left out: only the second fleet's 4 Cherry, 10%; medium confidence) | 690 |
| 20 | T-20: same, both attack | 800 → 920 | **690** | 704 if each fleet bombed separately |
| 23 | T-13: 10 Smart + 10 Cherry | 801 → 921 | **606** (smart first, then 25% of the rest) | 607 normal first |

Starbases, ground combat, colonization (TK-002; enemies, SDI).

| Planet | Case | P → P' | Predicted |
|---|---|---|---|
| 0 | T-21/T-26/T-27: 100 arriving vs P 87, carry 37, mines 20, factories 15, scanner 0 | 87 → 100 | owner **0**, pop **9**; mines 20, factories 15 kept; defenses 0; planetary scanner none (31); carry **42** (not reset); production queue = player 0's default |
| 1 | T-22: 100 vs 110 | 96 → 110 | tie goes to the attacker: owner 0, pop **1** |
| 2 | T-23: 100 vs 200 | 174 → 200 | owner 1, pop **90** |
| 3 | T-25: 600 vs 500, 20 SDI | 435 → 500 | troops at 75% of the bomb coverage → strength 569: owner 0, pop **72** |
| 5 | T-26: 300 vs 200, 10 SDI, mines 20, factories 15, scanner 0 | 174 → 200 | owner 0, pop **106**; defenses 0, scanner 31, mines 20, factories 15 |
| 4 | T-28: 100 vs a planet with a bare Orbital Fort | 87 → 100 | refused: the freighter keeps 100 colonists; planet 1/100 |
| 6 | T-5: 100 **in orbit** (unload on waypoint 0) | 87 | invasion before growth: 100 vs 87 → 20 land, then grow as player 0's colony → **23** (an after-growth invasion would give 9) |
| 18 | T-4: 4 Cherry in orbit + 50 arriving (unload), P 9, mines 20, factories 15 | 9 → 10 | bombed empty (minimum 12 units ≥ 10), then the transport colonizes it: owner 0, pop **50**, mines 20, factories 15 |
| 16 | T-4 control: 50 arriving at a planet unowned at the start of the turn | — | nothing lands; the freighter keeps **50** |
| 19 | T-3: 10 Cherry vs a bare Orbital Fort | 800 → 920 | no bombing: **920** |
| 20 | T-2: 10 Cherry + 2 Laser Frigates vs a bare Orbital Fort | 800 → 920 | the fort dies in battle, bombing follows in the same turn: **690**, no starbase |
| 13 | T-1: colony ship in orbit, colonize on waypoint 0, 25 | — | colony made before growth: pop **> 25** this turn |
| 21 | T-1/T-30: colony ship arriving, colonize, 25 | — | colony made after growth: pop exactly **25**; surface minerals = ¾ of the ship's mineral cost |
| 7 | T-31: colony ship arriving at a red planet | — | colonized (no habitability check): owner 0, pop **25** |
| 9 | T-32: player 0 25 vs player 1 12, both arriving | — | owner **0**, pop **25** (not reduced) |
| 10 | T-32: player 0 12 vs player 1 25 | — | owner **1**, pop **12** (reduced by the lower-index rival: 25·(27−13)/27) |
| 14 | T-32: 25 vs 25 | — | **nobody**: planet stays unowned, both colony ships consumed |

TK-003: player 1 at energy 5 (Missile Battery, 2% each); players are
**friends**.

| Planet | Case | P → P' | Predicted |
|---|---|---|---|
| 3 | T-25/T-8: 600 vs 500, 20 Missile Batteries | 435 → 500 | strength 495 < 500: owner 1 keeps **5** |
| 7 | T-8: 20 Cherry (plan "everyone"), 100 Missile Batteries | 870 → 1000 | pop **777**, defenses 0 (SDI would give 666) |
| 0 | T-29: 100 arriving at a **friend's** planet | 87 → 100 | invades like an enemy's: owner 0, pop **9** |
| 5 | control | 87 → 100 | 100 |

TK-004, random cases, several cycle settings; outcome distribution from
`takeover.py bomb`:

| Planet | Case | P → P' | Predicted outcomes |
|---|---|---|---|
| 0 | T-11: 1 Hush-a-Boom (3.0%, no minimum) | 44 → 50 | pop 48 (p 501/1000) or 49 (p 499/1000); a 300-colonist minimum would give 47 |
| 6 | T-15: 1 LBU-17, mines 20, factories 10 | 870 → 1000 | pop 998; factories 5 / mines 9 (p 2/3) or factories 4 / mines 10 (p 1/3); kills always sum to 16 |
| 12 | T-13: 10 Smart + 10 Cherry | 870 → 1000 | pop 658 (p 749/1000) or 657 (p 251/1000) |

### Setup change after run1 (before run2; predictions unchanged)

TK-001..003 run1 used player 0 at tech 3 with 15% research. The generated
2401 files had Cherry, Smart, Peerless, LBU-17 and LBU-32 bombs removed from
player 0's designs (slots empty); Lady Finger, Hush-a-Boom, Retro, the
Orbital Construction Module and the Multi Contained Munition stayed, and
only those bombed. Player 1's energy also rose from 3 to 5 in TK-001 run1
through research. From run2 on, player 0 has tech 26 in every field and
both players research 0%.

### Added after run2, predictions committed before running them

In TK-001 run2 player 1's energy rose from 3 to 5 during the year (all of
its resources went to research: its planets have no production queue),
so the bombing there met Missile Batteries. TK-005 repeats the SDI cases
with only four player-1 planets.

| Run | Planet | Case | P → P' | Predicted |
|---|---|---|---|---|
| TK-005 | 7 | T-6 with SDI (player 1 stays at energy 3) | 870 → 1000 | pop 666, defenses 0 |
| TK-005 | 9 | T-7 with SDI | 87 → 100 | pop 42 |
| TK-005 | 10 | T-9 with SDI | 870 → 1000 | pop 812, defenses 100 |
| TK-005 | 19 | T-20: a Laser Frigate with plan "enemies" (first fleet) and 10 Cherry with plan "nobody" (second fleet) | 800 → 920 | **690**: one attacking fleet triggers bombing with every bomb its owner has at the planet (the reading has no check that the trigger fleet carries bombs) |
| TK-006 | 14 | T-19, players **neutral**, plan "enemies" | 800 → 920 | 920 (no bombing) |
| TK-006 | 16 | neutral, plan "player 1 only" | 800 → 920 | 690 |
| TK-006 | 22 | neutral, plan "everyone" | 800 → 920 | 690 |
| TK-006 | 5 | control | 87 → 100 | 100 |

TK-007 (random cases, committed before running): 14 Hush-a-Boom planets
as in TK-004 planet 0 (48 with p 501/1000, else 49), two T-13 planets
(658 with p 749/1000, else 657) and two T-15 planets (factories 5 / mines
9 with p 2/3, else 4 / 10), one generation per cycles value. The draws
should be independent across planets; the vector of outcomes identifies
the random stream of each run.

## Results

Runs: TK-001..003 run1 (player 0 at tech 3, see above; only the parts
that survived are used), TK-001..004 run2, TK-005/006 run1, TK-004 and
TK-007 under 12 and 14 cycle settings. Values read from the 2401 host file
with `combatlab dump` (`pdetail` lines) and `hst-edit dump`. Raw files:
private `stars-oracle-apparatus`, `evidence/tk/`.

Bombing (TK-001 run2 unless stated):

| Planet | Case | Predicted | Observed | |
|---|---|---|---|---|
| 5 | growth control | 100, carry 42 | 100, carry 42 | matches |
| 0 | T-12 10 Cherry | 690 | 690 | CONFIRMED |
| 1 | T-10 Lady Finger | 7 | 7 (also run1) | CONFIRMED |
| 2 | T-11 LBU-17 | 9 | 9 | CONFIRMED |
| 3 | T-14 20 Peerless | 412 | 412 | CONFIRMED |
| 4 | T-14 20 Peerless on 1 | 1 | 1 | CONFIRMED |
| 6 | T-15 LBU-32 | 997, mines 16, factories 16 | 997, 16, 16 | CONFIRMED |
| 7 | T-6 | 666 (SDI) | 777 | player 1 reached energy 5 during the year; 777 is the Missile Battery value. TK-005: **666** with SDI. CONFIRMED |
| 9 | T-7 | 42 (SDI) | 45 | Missile Battery value (n = 4, s = 0.98⁴: A 461, minimum 55). TK-005: **42**. CONFIRMED |
| 10 | T-9 | 812 (SDI), defenses 100 | 846, defenses 100 | Missile Battery value (smart coverage 0.99⁴⁰). TK-005: **812**. CONFIRMED |
| 11 | T-17 OCM | 80 | 80 (also run1) | CONFIRMED |
| 12 | T-18 MCM | 97, mines 5 | 97, mines 5 (also run1) | CONFIRMED |
| 13 | T-16 3 Retro | env 52/50/50 | 52/50/50, original kept (also run1) | CONFIRMED |
| 14, 15 | T-19 nobody / player 0 only | 920 | 920 | CONFIRMED |
| 16, 22 | T-19 player 1 only / everyone | 690 | 690 | CONFIRMED |
| 18 | T-20 first attacks, second nobody | 690 | 690 | CONFIRMED |
| 19 | T-20 first nobody, second attacks | 828 | **690** | CONTRADICTED: the earlier non-attacking fleet's bombs were included |
| 20 | T-20 both attack | 690 | 690 | CONFIRMED |
| 23 | T-13 Smart + Cherry | 606 | 606 | CONFIRMED |
| TK-005 19 | Laser Frigate (enemies) + bombers (nobody) | 690 | 690 | CONFIRMED |
| TK-003 7 | T-8 Missile Batteries, friends, plan everyone | 777 | 777 | CONFIRMED |
| TK-006 14 | neutral, plan enemies | 920 | 920 | CONFIRMED |
| TK-006 16, 22 | neutral, player 1 only / everyone | 690 | 690 | CONFIRMED |

Starbases, ground combat, colonization (TK-002 run2; run1 gave the same
ground-combat and colonization results):

| Planet | Case | Predicted | Observed | |
|---|---|---|---|---|
| 0 | T-21/T-26/T-27 | owner 0, 9; mines 20, factories 15, defenses 0, scanner none, carry 42 | owner 0, 9, 20, 15, 0, scanner id 31, carry 42 | CONFIRMED (queue: see below) |
| 1 | T-22 tie | owner 0, 1 | owner 0, 1 | CONFIRMED |
| 2 | T-23 | owner 1, 90 | owner 1, 90 | CONFIRMED |
| 3 | T-25 SDI | owner 0, 72 | owner 0, 72 | CONFIRMED |
| 5 | T-26 | owner 0, 106, defenses 0 | owner 0, 106, defenses 0, mines 20, factories 15, scanner 31 | CONFIRMED |
| 4 | T-28 fort | refused, freighter keeps 100 | planet 100, freighter 100 | CONFIRMED |
| 6 | T-5 in orbit | owner 0, 23 | owner 0, 23 | CONFIRMED |
| 18 | T-4 bomb and drop | owner 0, 50; mines 20, factories 15 | owner 0, 50; mines **0**, factories **0** | pop CONFIRMED; the installation figures in the prediction table were an error of this corpus, not of the reading: 4 Cherry destroy 40 installations, i.e. all 35 (`takeover.py` gives 0/0) |
| 16 | T-4 control | freighter keeps 50 | 50 | CONFIRMED |
| 19 | T-3 fort, bombers only | 920, fort kept | 920, fort kept | CONFIRMED |
| 20 | T-2 fort, bombers + frigates | 690, no starbase | battle at planet 20, fort gone, 690 | CONFIRMED |
| 13 | T-1 in orbit | > 25 | 28 | CONFIRMED |
| 21 | T-1 arrival | 25 | 25 | CONFIRMED |
| 7 | T-31 red planet | owner 0, 25 | owner 0, 25 | CONFIRMED |
| 9 | T-32 25 vs 12 | owner 0, 25 | owner 0, 25 | CONFIRMED |
| 10 | T-32 12 vs 25 | owner 1, 12 | owner 1, 12 | CONFIRMED |
| 14 | T-32 25 vs 25 | nobody | unowned, pop 0, both colony ships gone, surface 22/7/22 = both ships' contributions (4/1/5 + 18/6/17) | CONFIRMED |
| TK-003 3 | T-25 Missile | owner 1, 5 | owner 1, 5 | CONFIRMED |
| TK-003 0 | T-29 friend | owner 0, 9 | owner 0, 9 | CONFIRMED |

- T-26 queue: no captured planet had a production-queue block afterwards,
  and neither did player 0's homeworld; this game's default queue may be
  empty, so the queue part is not tested.
- T-30: an arriving colony ship of player 0 left 18/6/17 kT on the new
  colony at tech 3 (run1) and 4/1/5 at tech 26 (run2); player 1's (tech 3)
  18/6/17. Not compared with a cost table here.
- Events: the attacker's `.M1` event block has a record with id 0x135
  naming the refused freighter and planet 4, and one with id 0x55 naming
  the TK-002 planet-16 freighter (read from the hex; the record layout is
  otherwise not decoded).

Random roundings (TK-004 under 12 cycle settings, TK-007 under 14):

| Draw | Predicted | Observed |
|---|---|---|
| Hush-a-Boom on 50 | 48 p 0.501, 49 p 0.499; never 47 | TK-007: 42 × 48, 56 × 49 over 7 distinct streams × 14 planets; never 47 |
| Smart + Cherry on 1000 | 658 p 0.749, 657 p 0.251 | TK-007: 9 × 658, 5 × 657 (7 streams × 2) |
| LBU-17, mines 20, factories 10 | f 5 / m 9 p 2/3, f 4 / m 10 p 1/3; pop 998 | TK-007: 7 / 7 (7 streams × 2); pop always 998; never another split |

TK-007's 14 cycle settings gave 7 distinct outcome vectors: 10000,
12000, 15000, 17000 each their own; 20000 = 22000 = 25000; 30000 = …
= 45000; 50000 = 60000 = 70000. The host files differed byte-wise
between all settings, including settings with identical outcomes, while
two runs at 20000 were byte-identical (TK-004).


# Round 2: TK-101 to TK-115

Round 2 tests the takeover rules round 1 could not reach (docs/TAKEOVER.md
"Open experiments"), plus the rules added in stars-elegy #34 (order inside a
phase, phase-start ownership, unload amounts, colonize retries, tech on
capture). Specs and predictions are written by `gen2.py`; the predictions
below were committed before any of these runs. `check2.py` compares them
with the run dumps.

## Round 2 setup

- Combat Lab (CB, game id 82222, two JOAT players), as round 1, except
  TK-113, which uses **TK3**: a tiny three-player game built with
  `tools/fleetlab/new-game` (definition: tiny, seed 11, no random events,
  three human players of the PG000 race file: Super Stealth, growth 10%,
  hab 50±35). Homeworlds: player 0 planet 16, player 1 planet 12, player
  2 planet 19.
- Race changes (all checked legal before the runs: no message 0x117 in a
  generated year): War Monger, Alternate Reality and Claim Adjuster with
  NRSE, CE, OBRM, LSP and BET (`lrt 0x1b80`); Inner Strength alone; JOAT
  with Ultimate Recycling needs the same five (`lrt 0x1ba0`; UR alone gave
  0x117 and the race was penalized). BET changes miniaturization (80% at
  26 instead of 75%), so colony minerals of these races differ from JOAT's.
- Default production queue and "only leftover to research" (new CombatLab
  keys `defqueue`, `defleftover`): player 0 queue auto factories 10, auto
  mines 5, auto defenses 3, auto min terraform 2, auto max terraform 1
  (item ids 1, 0, 2, 4, 5), leftover on. CB has no default queue, so a
  capture or colony gets this queue only from the rule under test.
- Player 0 tech 26 unless stated, research 0% for everyone. Ship costs
  are computed with COMPONENTS.md "Cost for an owner" (`gen2.py
  item_cost`). Colonizer (Colony Ship + Long Hump 6 + Colonization Module)
  at tech 26 costs 6/2/7 kT; 30 of them 180/60/210.
- Unowned planets start with no surface minerals.
- Populations in units of 100 colonists; growth before the after-movement
  phase (KERNEL.md), so P = 87 is 100 at the after-movement drops.

## Round 2 predictions

### TK-101: T-36 colony ship minerals, player 0 at tech 5 in every field

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-36 | Colonizer (Colony Ship + Long Hump 6 + Colonization Module) arrives at unowned planet 21, colonize 25, tech 5 | planet 21: owner 0, pop 25, surface 17/6/15 |

### TK-102: T-36 colony ship minerals, player 0 at tech 10 in every field

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-36 | Colonizer (Colony Ship + Long Hump 6 + Colonization Module) arrives at unowned planet 21, colonize 25, tech 10 | planet 21: owner 0, pop 25, surface 12/4/12 |

### TK-103: T-36 colony ship minerals, player 0 at tech 15 in every field

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-36 | Colonizer (Colony Ship + Long Hump 6 + Colonization Module) arrives at unowned planet 21, colonize 25, tech 15 | planet 21: owner 0, pop 25, surface 9/3/8 |

### TK-104: T-37 player 0 tech 26 except electronics 7; research field energy

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-37 | designs after generation; research field energy | design 0 kept; design 1 kept; design 2 kept; design 3 kept; design 4 part removed; design 5 part removed; design 6 kept; design 7 kept; design 8 kept; design 9 kept; design 10 kept; design 11 kept; design 12 kept; design 13 kept |

### TK-105: T-37 player 0 tech 26 except electronics 7; research field elec

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-37 | designs after generation; research field elec | design 0 kept; design 1 kept; design 2 kept; design 3 kept; design 4 part removed; design 5 part removed; design 6 kept; design 7 kept; design 8 kept; design 9 kept; design 10 kept; design 11 kept; design 12 kept; design 13 kept |

### TK-106: T-24/T-26 War Monger attacker (NRSE CE OBRM LSP BET), default queue and leftover

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-24 | WM 100 arriving vs P=131 (150 after growth) | planet 0: owner 0, pop 9 |
| A2 | T-26 | the captured planet gets the WM default queue and leftover setting | queue 0: 1:10, 0:5, 2:3, 4:2, 5:1; planet 0: leftover True |
| B | control | P=131, nothing arrives | planet 5: owner 1, pop 150 |
| C | T-25 | WM 600 arriving vs P=435 (500), 20 SDI | planet 3: owner 0, pop 248, defenses 0 |
| D | T-26/BET | WM (BET) Colonizer arrives at unowned planet 21, colonize 25 | planet 21: owner 0, pop 25, surface 3/1/4; queue 21: 1:10, 0:5, 2:3, 4:2, 5:1; planet 21: leftover True |

### TK-107: T-33 Alternate Reality player 0 (NRSE CE OBRM LSP BET), default queue

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-33 | AR OCM ship arrives at unowned planet 21, colonize 25 | planet 21: owner 0, pop 25, surface 5/2/5; queue 21: 4:2, 5:1; planet 21: leftover True; planet 21 starbase design 0 |
| B | T-33 | AR freighter 100 arriving, unload on player 1 planet P=87 | planet 0: owner 1, pop 100; fleet 0/1: col 100 |

### TK-108: T-26 Claim Adjuster both players (NRSE CE OBRM LSP BET), default queue

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-26 | CA 100 arriving vs CA P=87, env 50/50/50 orig 55/47/52 | planet 0: owner 0, pop 9, env 55/47/52; queue 0: 1:10, 0:5, 2:3 |
| B | control | CA P=87, env 50/50/50 orig 55/47/52, nothing arrives | planet 5: owner 1, pop 100, env 50/50/50 |
| C | T-26/BET | CA Colonizer arrives at unowned planet 21, colonize 25 | planet 21: owner 0, pop 25, surface 3/1/4; queue 21: 1:10, 0:5, 2:3; planet 21: leftover True |

### TK-109: T-24 Inner Strength defender

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-24 | 150 arriving vs IS P=87 (100) | planet 0: owner 1, pop 18 |
| B | T-24 | 300 arriving vs IS P=87 (100) | planet 3: owner 0, pop 118 |
| C | control | IS P=87, nothing arrives | planet 5: owner 1, pop 100 |

### TK-110: T-24 War Monger attacker against Inner Strength

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-24 | WM 150 arriving vs IS P=87 (100) | planet 0: owner 0, pop 28 |
| B | control | IS P=87, nothing arrives | planet 5: owner 1, pop 100 |

### TK-111: T-34 scrap and T-35 remote mining over two years; player 1 UR (plus NRSE CE OBRM LSP BET)

Game CB, 2 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| S1 | T-34 | 30 Colonizers scrap at player 0 planet 0 with a starbase: 4C/5 | planet 0: surface 144/48/168 |
| S2 | T-34 | 30 Colonizers scrap at player 0 planet 1 without a starbase: C/3 | planet 1: surface 60/20/70 |
| S3 | #34/T-34 | S2 at planet 2 with cargo 100/0/0 and 50 colonists: cargo added, colonists join before growth | planet 2: surface 160/20/70, pop 157 |
| S4 | T-34 | 30 Colonizers scrap at UR player 1 planet 3 with a starbase: 9C/10 | planet 3: owner 1, surface 162/54/189 |
| S5 | T-34 | 30 Colonizers scrap at UR player 1 planet 4 without a starbase: 9C/20 | planet 4: owner 1, surface 81/27/94 |
| S6 | T-34 | S5 at planet 5 with 50 colonists: colonists do not join (P 87 -> 100) | planet 5: owner 1, pop 100, surface 81/27/94 |
| S7 | T-34 | 30 Colonizers scrap at unowned planet 6: C/3 on the surface | planet 6: owner -1, surface 60/20/70 |
| S8 | T-34 | 30 Colonizers scrap in deep space at (1200,1220): C/3 salvage | salvage at 1200,1220: 60/20/70 |
| S9 | T-34 | 30 Colonizers scrap at player 0 planet 7, second waypoint to planet 10: scrapped at 7 | planet 7: surface 60/20/70 |
| S10 | T-34 | 30 Colonizers arrive at player 0 planet 9 with scrap: nothing in year 1, C/3 in year 2 | planet 9: surface 0/0/0; fleet 0/9: ships 12:30; planet 9: surface 60/20/70 (year 2) |
| M1 | T-35 | Miner24 (24 robots) stationary at unowned planet 13, conc 100/50/25 | planet 13: surface 24/12/6; planet 13: surface 48/24/12 (year 2) |
| M2 | T-35 | Miner24 arrives at unowned planet 14, conc 100/50/25: nothing in year 1, mines in year 2 | planet 14: surface 0/0/0; planet 14: surface 24/12/6 (year 2) |
| M3 | T-35 | Miner24 stationary at player 1 planet 15: nothing | planet 15: surface 0/0/0 |
| M4 | T-35 | Miner24 stationary at player 0 planet 16: nothing | planet 16: surface 0/0/0 |

### TK-113: several bombers on one planet; colonize retries after a tie (three players, Super Stealth, growth 10%)

Game TK3, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| B1 | bombing order | players 0 and 2, 10 Cherry each, on player 1 P=728 (800): 800 -> 600 -> 450 | planet 13: owner 1, pop 450 |
| B2 | bombing order | player 0 10 Smart, player 2 10 Cherry, on P=37 (40): smart first 40 -> 36 -> 6 | planet 9: owner 1, pop 6 |
| B3 | bombing order | player 0 10 Cherry, player 2 10 Smart, on P=37 (40): cherry first 40 -> 10 -> 9 | planet 3: owner 1, pop 9 |
| R1 | #34 retry | before movement: players 0 and 2 unload 150 each on P=100 (tie, emptied), player 0 Colonizer in orbit retries: player 0 owns 25 after movement | planet 23: owner 0, pop 25, surface 4/1/5; fleet 0/3 gone |
| R2 | #34 retry LEGACY BUG | after movement: players 0 and 2 arrive with 150 each on P=100 (110), player 0 Colonizer arrives: retry consumes it, colonists lost, planet unowned | planet 26: owner -1, surface 4/1/5; fleet 0/5 gone |

### TK-114: #34 phase-start ownership record and own-planet unload amounts; player 1 Lady Finger bombers

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| PS1 | #34 phase start | unowned planet 13: player 0 Colonizer in orbit colonizes 25 (28 after growth), player 1 10 Lady Finger bomb it empty, player 0 freighter arrives with 50 and unloads: player 0 owns 50 | planet 13: owner 0, pop 50, surface 4/1/5; fleet 0/1: col 0 |
| PS2 | T-4 control | unowned planet 16 with player 1 bombers in orbit; player 0 freighter arrives with 50: refused, keeps 50 | planet 16: owner -1; fleet 0/2: col 50 |
| U1 | #34 unload | own planet 0 P=87, freighter in orbit unloads all 50 before growth: 137 -> 157 | planet 0: pop 157; fleet 0/3: col 0 |
| U2 | #34 unload | own planet 1 P=87, freighter arrives and unloads all 50 after growth: 100 + 50 | planet 1: pop 150; fleet 0/4: col 0 |
| U3 | #34 unload | own planet 2 P=87, in orbit, cargo 100/40/0/50: unload exactly 30 Ir, all Bo, exactly 20 colonists | planet 2: pop 123, surface 30/40/0; fleet 0/5: fe 70, bo 0, col 30 |
| U4 | #34 unload | own planet 3 P=87, in orbit, cargo 100/0/0/50: set amount Ir 60, colonists 10 | planet 3: pop 146, surface 40/0/0; fleet 0/6: fe 60, col 10 |
| U5 | #34 unload | own planet 4 P=87, in orbit, cargo 100/0/0/50: unload exactly 500 Ir (capped at 100), set waypoint colonists to 120 (unloads 33) | planet 4: pop 138, surface 100/0/0; fleet 0/7: fe 0, col 17 |

### TK-115: #34 tech on capture: player 0 tech 3, player 1 weapons 10; two captures

Game CB, 1 year(s). Cycles 20000, 12000, 15000, 25000, 30000, 40000, 50000, 17000.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | #34 tech | 100 arriving vs P=87 (100) on planet 0: captured with 9 | planet 0: owner 0, pop 9 |
| B | #34 tech | 100 arriving vs P=87 (100) on planet 5: captured with 9 | planet 5: owner 0, pop 9 |
| T | #34 tech | player 0 ends at weapons 3 or 4 (one gain at most per year), other fields 3 | tech (0,) weapons 3 or 4; others 3 |


## Round 2 follow-up predictions (written after TK-101..TK-115 ran, before these runs)

TK-108 A kept 50/50/50 because player 0 is also Claim Adjuster and its
end-of-year terraforming would undo a revert, which the prediction forgot;
TK-116 repeats the capture with a JOAT attacker. TK-107 lost AR colonists in
flight (100 → 97, 25 → 24); TK-117 tests the loss rule
`trunc((C + 11)·3/100)` for C > 10, in moving fleets only (stars-decomp
fleet-movement reading).

### TK-116: T-26 Claim Adjuster defender captured by a JOAT attacker

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-26 | JOAT 100 arriving vs CA P=87, env 50/50/50 orig 55/47/52: env back to 55/47/52 | planet 0: owner 0, pop 9, env 55/47/52, orig 55/47/52 |
| B | control | CA P=87, env 50/50/50 orig 55/47/52, nothing arrives | planet 5: owner 1, pop 100, env 50/50/50 |

### TK-117: Alternate Reality colonists in moving and stationary freighters

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | AR loss | AR freighter with 10 moving through deep space: loses trunc((C + 11)·3/100) if C > 10 | fleet 0/0: col 10 |
| B | AR loss | AR freighter with 11 moving through deep space: loses trunc((C + 11)·3/100) if C > 10 | fleet 0/1: col 11 |
| C | AR loss | AR freighter with 40 moving through deep space: loses trunc((C + 11)·3/100) if C > 10 | fleet 0/2: col 39 |
| D | AR loss | AR freighter with 200 moving through deep space: loses trunc((C + 11)·3/100) if C > 10 | fleet 0/3: col 194 |
| E | AR loss | AR freighter with 200 stationary in deep space: no loss | fleet 0/4: col 200 |


## Round 2 results

Checked with `python3 experiments/tk/check2.py RUNDIR` (pinned-turn output
per run; raw files in private `stars-oracle-apparatus` `evidence/tk2/`).
Every run at cycles 20000; TK-115 also at seven other settings; TK-111 ran
2401 and then 2402 from its own output.

| Run | Checks | Result |
|---|---|---|
| TK-101..103 | T-36 colony minerals at tech 5/10/15 | all OK: 17/6/15, 12/4/12, 9/3/8 |
| TK-104, 105 | T-37 design check, field energy / electronics | all 28 OK: LBU-17 and LBU-32 removed in both |
| TK-106 | WM invasions, queue, leftover, BET colony | all 8 OK |
| TK-107 | AR colonize, queue, starbase, refused unload | 4 OK, 2 MISS: colonists lost in flight (25 → 24 landed, 100 → 97 kept) |
| TK-108 | CA capture, queue, colony | 5 OK, 1 MISS: env 50/50/50, not 55/47/52 |
| TK-109, 110 | IS defender, WM vs IS | all 5 OK |
| TK-111 | scrap S1–S10, remote mining M1–M4, two years | all 18 OK (salvage: a packet-type object, dest 1023, 60/20/70) |
| TK-113 | several bombers B1–B3, colonize retries R1, R2 | B1–B3 OK; R1, R2 MISS (no retry) |
| TK-114 | phase-start ownership, own-planet unload amounts | all 14 OK |
| TK-115 | tech on capture, 8 cycle settings | all OK; weapons 3 → 4 in 5 of 8, never more, no other field |
| TK-116 | CA defender, JOAT attacker | env back to 55/47/52 (OK); `orig` no longer stored, see below |
| TK-117 | AR colonists in flight | all 5 OK: 10 → 10, 11 → 11, 40 → 39, 200 → 194 moving; 200 stationary kept |

Misses and what they show:

- **TK-107 A and B (prediction error).** AR colonists in a moving fleet
  lose `trunc((C + 11)·3/100)` for C > 10 (a movement rule the prediction
  left out; TK-117 then confirmed it): 25 → 24 before colonizing, 100 →
  97 in the refused freighter. The rules under test held: the colony got a
  starbase of design 0 and the queue minus items 0–2; the unload was
  refused and the colonists stayed in the fleet.
- **TK-108 A (prediction error).** Both players were Claim Adjuster, so the
  new owner's end-of-year CA terraforming put the captured planet back at
  its ideal 50/50/50. TK-116, with a JOAT attacker, showed the revert:
  55/47/52 after capture. The file then no longer marks the planet as
  terraformed (no separate original values), which fits env = original;
  the `orig` part of that check was over-specified.
- **TK-113 R1 and R2 (reading contradicted).** After players 0 and 2 tied
  (150 each on 100: planet emptied, nobody landed), player 0's colony ship
  whose colonize had failed in that phase did not retry, before movement
  or after. It ended in orbit with its 25 colonists and its waypoint task
  cleared (event 0x4e to player 0 for each ship); the planet stayed
  unowned with no minerals. stars-elegy #34's load-phase retry and its
  after-movement LEGACY BUG did not occur here.

## Round 2b predictions (T-39, T-40; written before these runs)

stars-decomp #16 reconciled TK-113: every colonize failure ends the order
(no retry). It adds T-39 (other colonize failures end the order too) and
T-40 (a CA capturing a CA planet: the revert to the original environment,
then the new owner's end-of-year CA terraforming from it, by `c` per axis,
the best terraform part it may use, never past its centre 50). T-39c (the
order given again by `.X` the next year) needs crafted orders and is not
run. Whether a CA without TT may use Total Terraform parts is the open
point between TK-118 (axis parts, c = 15) and TK-119 (TT, c = 30); TK-119's
race (`lrt 0x1b82`) is checked for 0x117 in its own run.

### TK-118: T-40 CA attacker, tech 26, no Total Terraform (axis parts: c = 15), captures a CA planet

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-40 | CA 100 arriving vs CA P=87, env 60/40/60 orig 80/20/80, attacker c = 15 | planet 0: owner 0, pop 9, env 65/35/65, orig 80/20/80 |
| B | control | CA P=87 (player 1, tech 3: c = 3), env 60/40/60 orig 80/20/80, nothing arrives: no target inside orig ± 3 improves it, env stays | planet 5: owner 1, pop 100, env 60/40/60, orig 80/20/80 |

### TK-119: T-40 CA attacker, tech 26 with Total Terraform (TT; c = 30), captures a CA planet

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-40 | CA 100 arriving vs CA P=87, env 60/40/60 orig 80/20/80, attacker c = 30 | planet 0: owner 0, pop 9, env 50/50/50, orig 80/20/80 |
| B | control | CA P=87 (player 1, tech 3: c = 3), env 60/40/60 orig 80/20/80, nothing arrives: no target inside orig ± 3 improves it, env stays | planet 5: owner 1, pop 100, env 60/40/60, orig 80/20/80 |

### TK-120: T-40 CA attacker, no terraform tech (biotech 0: c = 0), captures a CA planet

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-40 | CA 100 arriving vs CA P=87, env 60/40/60 orig 80/20/80, attacker c = 0 | planet 0: owner 0, pop 9, env 80/20/80, orig None |
| B | control | CA P=87 (player 1, tech 3: c = 3), env 60/40/60 orig 80/20/80, nothing arrives: no target inside orig ± 3 improves it, env stays | planet 5: owner 1, pop 100, env 60/40/60, orig 80/20/80 |

### TK-121: T-39 colonize failures end the order

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-39a | Colonizer (25) in orbit at player 1 planet P=9 (10), 10 Cherry bomb it empty: the colony ship keeps 25, task 0; planet unowned | planet 0: owner -1; fleet 0/0: col 25, task 0 |
| B | T-39b | Freighter (25, no colony module) in orbit at unowned planet 21 with colonize: keeps 25, task 0, planet unowned with no minerals | planet 21: owner -1, surface 0/0/0; fleet 0/2: col 25, task 0 |


## Round 2b results

| Run | Result |
|---|---|
| TK-118 | env 65/35/65, original 80/20/80 kept (OK); control env unchanged (OK) |
| TK-119 | env 50/50/50, original 80/20/80 (OK); TT race legal (no 0x117) |
| TK-120 | env 80/20/80, no separate original stored (OK) |
| TK-121 | T-39a and T-39b all OK: the ships kept 25 colonists, task 0; planets unowned, no minerals |

Every environment check held. The population values in TK-118..120 were
the corpus author's error: at 60/40/60 the race's habitability is below
100%, so P = 87 grew to 96 (not 100), and the captures then landed 12
(110 against 96, the ground combat rule) instead of 9. The checker shows
these as MISS on `pop` only.


# Round 3: TK-201 to TK-203

Round 3 sweeps the rules `docs/TAKEOVER.md` still tagged BINARY-ONLY after
rounds 1 and 2 (the rest were confirmed by round 2, the FO corpus and the
MG runs; see the TAKEOVER.md tags). Specs and predictions are written by
`gen3.py`, which reuses the round-2 spec writer; the predictions below were
committed before any of these runs. They restate the private binary
reading (stars-decomp `docs/takeover.md`, `docs/messages/`) as behavior.

## Round 3 setup

- Combat Lab (CB), two JOAT players, enemies, research 0%; player 0 tech
  26. Player 1 tech 3, except TK-202 (energy 26, so Neutron Shield
  defenses, `c = 38`) and TK-203 (tech 0 in every field).
- Bombers fly plan 0 ("Enemies"); freighters and colony ships fly plan 1
  ("Nobody"), so they never start a bombing pass.
- Message order is read from the order of records in each player's `.M`
  file (`tools/fleetlab/events.py`).
- TK-201 runs two years at cycles 20000 and 30000 (the second year only for
  the homeworld mark). TK-202 and TK-203 run one year at twelve cycle
  settings that reached different streams before (ORACLE.md).

## Round 3 predictions

Working for TK-202. Twenty Neutron Shields counted: `s = 0.962^20 =
0.4610`. One Lady Finger: `I = round(2·0.7305) = 1`, `A = round(6·s) = 3`,
`M = round(3·s) = 1`, so 1000 → 997 with no population draw. Two Lady
Fingers: `I = 3`, `A = 6`, `M = 3`, 1000 → 994. Undefended, two Lady
Fingers: `I = 4`, `A = 12`, `M = 6`, 1000 → 988. With `I = 1` on mines 1,
factories 20, defenses 20 (`T = 41`), factories and defenses each lose 1
with chance 20/41, and the mines take the rest, `1 − f − d`. When both lose
one, the rest is −1: the rule says the mines then lose nothing (they stay
at 1, not 2).

Scrap tech (TK-203). Each scrap at a starbase is one attempt for the planet
owner: a 1/2 draw, then 13 Mystery Trader draws that give nothing, then up
to 6 field draws until one names a field where the scrapped ships' parts
needed more than the owner has. Long Hump 6 needs propulsion 3 and the
Scout hull nothing, so only propulsion can come up.

### TK201: order across planets, foreign and deep-space unloads, emptying own planets, colonize failures; second year for the homeworld mark

Game CB, 2 year(s). Cycles 20000, 30000.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | drop order | fleet 0 Freighter unloads 100 colonists on player 1 planet 14 (P 10); fleet 1 Freighter unloads 100 on player 1 planet 3 (P 10); both in orbit, before movement | planet 14: owner 0, pop 103; planet 3: owner 0, pop 103; player 0 invasion messages: planet 14 before planet 3 (fleet order), not planet order |
| B | bombing order | fleet 2 Cherry2 bomber at player 1 planet 13 (P 87); fleet 3 Cherry2 at player 1 planet 2 (P 87); no defenses or installations | planet 13: owner 1, pop 94; planet 2: owner 1, pop 94; player 0 bombing messages: planet 13 before planet 2; player 1's the same order |
| C | minerals to a foreign planet | fleet 4 Freighter with 50 kT ironium unloads all on player 1 planet 9 (P 87, no starbase, surface 0) | planet 9: owner 1, surface 50/0/0; fleet 0/4: fe 0 |
| D | minerals to a foreign planet | fleet 5 the same at player 1 planet 10 with an Orbital Fort | planet 10: owner 1, surface 50/0/0; fleet 0/5: fe 0 |
| E | minerals to an unowned planet | fleet 6 the same at unowned planet 4 (surface 0) | planet 4: owner -1, surface 50/0/0; fleet 0/6: fe 0 |
| F | deep space unload | fleet 7 Freighter at (1200,1230) with 50 kT ironium and 50 colonists: unload all ironium and all colonists | fleet 0/7: fe 0, col 50; 0x02d for the 50 ironium, then 0x165 (colonists refused); no salvage object |
| G1 | loading every colonist | player 0 planet 11 (P 870, growing) and planet 12 (P 50); fleet 8 empty Freighter at planet 12 loads all colonists | fleet 0/8: col 50; planet 12: owner -1, pop 0; 0x02c (50 colonists), then at growth 0x040 for planet 12 (planet 11 before it grew) |
| G2 | emptying the homeworld | player 0 homeworld 17 set to P 50 with no starbase; player 0 planet 16 (P 870, growing); fleet 9 empty Freighter at 17 loads all colonists | fleet 0/9: col 50; planet 17: owner -1, pop 0; planet 17 homeworld mark True, player record names 17; planet 17 homeworld mark True, player record names 17 (year 2) |
| H1 | colonize failure | fleet 10 Colonizer with 25 colonists at (1100,1230), task colonize | fleet 0/10: col 25, task 0; 0x051 (not orbiting a planet), then 0x04e |
| H2 | colonize failure | fleet 11 Colonizer with no colonists at unowned planet 22, task colonize | fleet 0/11: col 0, task 0; planet 22: owner -1; 0x053 (no colonists), then 0x04e |
| I | homeworld mark (T-41) | fleet 12 Freighter unloads 100 colonists on player 1's homeworld 8 (P 10, no starbase); player 1 keeps other planets | planet 8: owner 0; planet 8 homeworld mark True, player record names 8 |

### TK202: mines never go negative; bombing messages for several fleets; player 1 energy 26 (Neutron Shield)

Game CB, 1 year(s). Cycles 20000, 30000, 50000, 10000, 12000, 15000, 17000, 11500, 9800, 6000, 5200, 3700.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| M0 | mines floor | one Lady1 bomber at player 1 planet 0: P 870, mines 1, factories 20, defenses 20 (Neutron Shield, 20 counted): I = 1, T = 41 | planet 0: owner 1, pop 997; factories 20 or 19 (19 w.p. 20/41), defenses the same, independently; mines 0 only when both stay at 20 (p 0.262), else 1; never 2 |
| M2 | mines floor | one Lady1 bomber at player 1 planet 2: P 870, mines 1, factories 20, defenses 20 (Neutron Shield, 20 counted): I = 1, T = 41 | planet 2: owner 1, pop 997; factories 20 or 19 (19 w.p. 20/41), defenses the same, independently; mines 0 only when both stay at 20 (p 0.262), else 1; never 2 |
| M3 | mines floor | one Lady1 bomber at player 1 planet 3: P 870, mines 1, factories 20, defenses 20 (Neutron Shield, 20 counted): I = 1, T = 41 | planet 3: owner 1, pop 997; factories 20 or 19 (19 w.p. 20/41), defenses the same, independently; mines 0 only when both stay at 20 (p 0.262), else 1; never 2 |
| M9 | mines floor | one Lady1 bomber at player 1 planet 9: P 870, mines 1, factories 20, defenses 20 (Neutron Shield, 20 counted): I = 1, T = 41 | planet 9: owner 1, pop 997; factories 20 or 19 (19 w.p. 20/41), defenses the same, independently; mines 0 only when both stay at 20 (p 0.262), else 1; never 2 |
| M13 | mines floor | one Lady1 bomber at player 1 planet 13: P 870, mines 1, factories 20, defenses 20 (Neutron Shield, 20 counted): I = 1, T = 41 | planet 13: owner 1, pop 997; factories 20 or 19 (19 w.p. 20/41), defenses the same, independently; mines 0 only when both stay at 20 (p 0.262), else 1; never 2 |
| M14 | mines floor | one Lady1 bomber at player 1 planet 14: P 870, mines 1, factories 20, defenses 20 (Neutron Shield, 20 counted): I = 1, T = 41 | planet 14: owner 1, pop 997; factories 20 or 19 (19 w.p. 20/41), defenses the same, independently; mines 0 only when both stay at 20 (p 0.262), else 1; never 2 |
| D20 | several fleets | two Lady1 fleets at player 1 planet 20, as M: I = 3, A = 6, M = 3 | planet 20: owner 1, pop 994; factories 19 or 18 (18 w.p. 19/41), defenses the same; mines 0 only when both are 19 (p 0.288), else 1; player 0 gets 0x16f and player 1 0x179 (several installations, defenses stopped a share) |
| D22 | several fleets | two Lady1 fleets at player 1 planet 22, as M: I = 3, A = 6, M = 3 | planet 22: owner 1, pop 994; factories 19 or 18 (18 w.p. 19/41), defenses the same; mines 0 only when both are 19 (p 0.288), else 1; player 0 gets 0x16f and player 1 0x179 (several installations, defenses stopped a share) |
| U21 | several fleets | two Lady1 fleets at player 1 planet 21: P 870, mines 1, no factories or defenses | planet 21: owner 1, pop 988, mines 0; 0x169 to player 0, 0x173 to player 1 (colonists and one installation) |
| U23 | several fleets | two Lady1 fleets at player 1 planet 23: P 870, mines 10, no factories or defenses | planet 23: owner 1, pop 988, mines 6; 0x16a to player 0, 0x174 to player 1 (colonists and several installations) |

### TK203: tech learned from scrapping at a starbase; player 1 tech 0 in every field

Game CB, 1 year(s). Cycles 20000, 30000, 50000, 10000, 12000, 15000, 17000, 11500, 9800, 6000, 5200, 3700.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| S0 | scrap tech | player 0 Scout (Long Hump 6: propulsion 3) scraps at player 1 planet 0 with an Orbital Fort (P 87) | attempt 1: 1/2 to pass, then up to 6 field draws until propulsion comes up: gain w.p. 1/2 x (1 - (5/6)^6) = 0.333; a gain sends player 1 0x13d (field propulsion) instead of 0x141 |
| S2 | scrap tech | player 0 Scout (Long Hump 6: propulsion 3) scraps at player 1 planet 2 with an Orbital Fort (P 87) | attempt 2, made only when S0 gained nothing (else no draws and 0x141): 1/2 to pass, then up to 6 field draws until propulsion comes up: gain w.p. 1/2 x (1 - (5/6)^6) = 0.333; a gain sends player 1 0x13d (field propulsion) instead of 0x141 |
| S3 | scrap tech | the same at player 1 planet 3 with no starbase (control) | 0x140 to player 1, no tech attempt |
| Y | scrap tech | player 1 tech at the end of the year | per stream: propulsion 0 or 1 (1 w.p. 0.555), never 2; every other field 0; the fleet owner (player 0) never gains |


## Round 3 results

Runs in private apparatus `evidence/tk3/`; `python3 experiments/tk/check3.py
RUNDIR` prints the table below from the dumps.

| Run | Result |
|---|---|
| TK-201 (20000, 30000) | every check OK (planet 12's `pop` reads None in the checker because an unowned planet stores none). Capture messages 14, 3, 8 and bombing messages 13, 2: fleet order. Surfaces 50/0/0 at planets 9, 10, 4. Deep space: 0x02d, 0x165, 0x04e, colonists kept, no object. Planets 12 and 17 lost at growth with 0x040. Homeworld 17 unowned and marked in years 1 and 2; homeworld 8 marked under player 0. 0x051 and 0x053 then 0x04e |
| TK-202 (12 settings, 10 outcome vectors) | pop 997 / 994 / 988 everywhere. Single Lady Finger (72 planets): mines 0 with f20/d20 21×, mines 1 with one of f19/d19 40×, mines 1 with f19 and d19 11× (never 2). Two Lady Fingers (24): mines 0 only at f19/d19 (7×). U21 mines 0, U23 mines 6. Messages 0x068/0x072 (count 1 even when 2 were lost), 0x16f/0x179 (count 3), 0x169/0x173, 0x16a/0x174 |
| TK-203 (12 settings) | propulsion 0 → 1 in 8 runs (S0 7, S2 1), never 2 or another field; 0x13d (field 2) on the gaining scrap, 0x141 otherwise, 0x140 at planet 3. Without the gain, leftover research took energy to 1 |

Side observation: the bombing message's installation count is `f + d +
rest` with a negative rest kept (LEGACY BUG, `MESSAGES.md`).


# Round 4: TK-301 to TK-306

Round 4 closes what legal orders can reach on TAKEOVER.md's open list:
Laser Battery and Planetary Shield against bombs and troops, the "load
exactly" action, ancient artifacts (random events on, and with slower
tech), and Mystery Trader parts scrapped at a starbase. Specs and
predictions are written by `gen4.py`; the predictions below were committed
before any of these runs. Colonists given to a foreign planet by a manual
cargo transfer need a client order; their predictions (TK-401 to TK-410)
are in `manual-transfers.md` and wait on client automation. The year's
full draw order went to the owner of `KERNEL.md`'s turn order.

## Round 4 setup

- Combat Lab, two JOAT players (the unedited races, which the host leaves
  unchanged), enemies, research 0%. Player 0 tech 26 (TK-303/304: 10 in
  every field, so artifact points are not added to a maxed field).
- TK-301/302: player 1 energy 10 (best defense Laser Battery, `c = 24`) or
  16 (Planetary Shield, `c = 30`), other fields 3.
- TK-303/304 run on a copy of the base whose `.XY` game options byte
  (offset 0x10) is 0x00 (random events on) or 0x02 (random events on,
  slower tech); Combat Lab has 0x80. CombatLab's new `planetset N
  artifact=1` sets a planet's ancient-artifact flag, and the dump prints
  `artifact`.
- TK-305: player 1 tech 0; player 0's twelve designs each carry 2
  Hush-a-Boom, so the scrapped fleet "shows" 24 Hush-a-Booms (the binary
  caps the count at 25).

## Round 4 predictions

The working for TK-301/302 is in `gen4.py` (single-precision coverage, as
`TAKEOVER.md` "Planetary defenses against bombs").

### TK301: Laser Battery (player 1 energy 10) against bombs and troops; "load exactly"

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| B | defenses | 10 Cherry2 bombers (20 Cherry) at player 1 planet 13: P 870, defenses 100, no other installations; best defense Laser Battery | planet 13: owner 1, pop 811, defenses 0 |
| S | defenses | 10 Smart2 bombers (20 Smart) at player 1 planet 2: P 870, defenses 100 | planet 2: owner 1, pop 858, defenses 100 |
| G | defenses | Freighter (600 colonists) unloads on player 1 planet 14 before movement: P 500, defenses 20 | planet 14: owner 1, pop 35 |
| L1 | load exactly | player 0 planet 11 (P 100): empty Freighter loads exactly 30 colonists | fleet 0/3: col 30; planet 11: owner 0, pop 80 |
| L2 | load exactly | player 0 planet 12 (P 100, surface ironium 25): load exactly 40 ironium | fleet 0/4: fe 25; planet 12: owner 0, surface 0/0/0 |
| L3 | load exactly | player 0 planet 16 (P 100, surface ironium 500): load exactly 300 ironium into a 210 kT hold | fleet 0/5: fe 210; planet 16: owner 0, surface 290/0/0 |

### TK302: Planetary Shield (player 1 energy 16) against bombs and troops; "load exactly"

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| B | defenses | 10 Cherry2 bombers (20 Cherry) at player 1 planet 13: P 870, defenses 100, no other installations; best defense Planetary Shield | planet 13: owner 1, pop 852, defenses 0 |
| S | defenses | 10 Smart2 bombers (20 Smart) at player 1 planet 2: P 870, defenses 100 | planet 2: owner 1, pop 874, defenses 100 |
| G | defenses | Freighter (600 colonists) unloads on player 1 planet 14 before movement: P 500, defenses 20 | planet 14: owner 1, pop 75 |
| L1 | load exactly | player 0 planet 11 (P 100): empty Freighter loads exactly 30 colonists | fleet 0/3: col 30; planet 11: owner 0, pop 80 |
| L2 | load exactly | player 0 planet 12 (P 100, surface ironium 25): load exactly 40 ironium | fleet 0/4: fe 25; planet 12: owner 0, surface 0/0/0 |
| L3 | load exactly | player 0 planet 16 (P 100, surface ironium 500): load exactly 300 ironium into a 210 kT hold | fleet 0/5: fe 210; planet 16: owner 0, surface 290/0/0 |

### TK303: ancient artifacts, random events on

Game CB, 1 year(s). Cycles 20000, 30000, 50000, 10000, 12000, 15000. Base: random events on.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A1 | artifact | Freighter (100) captures player 1 planet 14 (P 10, artifact) before movement | planet 14: owner 0; 0x05e to player 0: planet 14, a field 0-5, points 100-400 added to that field's research; the planet's artifact flag cleared |
| A2 | artifact | Colonizer (25) colonizes unowned planet 21 (artifact) before movement | planet 21: owner 0; 0x05e to player 0: planet 21, points 100-400; flag cleared |
| A3 | artifact | Colonizer (5) colonizes unowned planet 22 (artifact) before movement | planet 22: owner 0; 0x05e: points scaled by 5/10, so 50-200; flag cleared |
| A4 | artifact | Freighter (10) unloads on player 1 planet 3 (P 100, artifact): the defender wins | planet 3: owner 1; no 0x05e; flag kept |
| A5 | artifact | player 1 planet 9 (P 87, artifact), no fleet | no 0x05e; flag kept (an owned artifact planet gives nothing) |

### TK304: ancient artifacts, random events on, slower tech

Game CB, 1 year(s). Cycles 20000, 30000, 50000, 10000, 12000, 15000. Base: random events on, slower tech.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A1 | artifact | Freighter (100) captures player 1 planet 14 (P 10, artifact) before movement | planet 14: owner 0; 0x05e to player 0: planet 14, a field 0-5, points 100-400 added to that field's research; the planet's artifact flag cleared |
| A2 | artifact | Colonizer (25) colonizes unowned planet 21 (artifact) before movement | planet 21: owner 0; 0x05e to player 0: planet 21, points 100-400; flag cleared |
| A3 | artifact | Colonizer (5) colonizes unowned planet 22 (artifact) before movement | planet 22: owner 0; 0x05e: points scaled by 5/10, so 50-200; flag cleared |
| A4 | artifact | Freighter (10) unloads on player 1 planet 3 (P 100, artifact): the defender wins | planet 3: owner 1; no 0x05e; flag kept |
| A5 | artifact | player 1 planet 9 (P 87, artifact), no fleet | no 0x05e; flag kept (an owned artifact planet gives nothing) |
| Y | artifact | slower tech on | points are not halved (binary: the halving comes after the points are added and is unused, LEGACY BUG): A1/A2 still 100-400, A3 50-200. If halving applied, every A1/A2 value would be at most 200 |

### TK305: Mystery Trader parts scrapped at a starbase; player 1 tech 0

Game CB, 1 year(s). Cycles 20000, 30000, 50000, 10000, 12000, 15000, 17000, 11500, 9800, 6000, 5200, 3700.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| S0 | scrap MT | a fleet of 12 Hush-a-Boom bombers (12 designs, 2 Hush-a-Boom each) scraps at player 1 planet 0 with an Orbital Fort |  |
| S2 | scrap MT | a fleet of 12 Hush-a-Boom bombers (12 designs, 2 Hush-a-Boom each) scraps at player 1 planet 2 with an Orbital Fort |  |
| S3 | scrap MT | a fleet of 12 Hush-a-Boom bombers (12 designs, 2 Hush-a-Boom each) scraps at player 1 planet 3 with an Orbital Fort |  |
| Y | scrap MT | player 1 at the end of the year | one gain at most per stream. Each attempt: 1/2 to pass; then 13 rand(13) picks, each giving Hush-a-Boom with chance 24% when it names Hush-a-Boom (P(part) = 1 - (1 - 0.24/13)^13 = 0.215); otherwise a level in a field the bombers needed (construction, propulsion, weapons, electronics or biotech), never energy. The first attempt that passes gains (P = 0.875 per stream). A part gain sends 0x13c and sets player 1's Hush-a-Boom bit; a level sends 0x13d |

TK-306 was added after TK-303's owned-planet cases turned out void (see
results). Its predictions were committed before its runs.

### TK306: ancient artifacts on owned planets, random events on

Game CB, 1 year(s). Cycles 20000, 30000, 50000. Base: random events on.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| C1 | artifact | Freighter (100) captures player 1 planet 14 (P 10, artifact) before movement | planet 14: owner 0, artifact False; 0x05e to player 0 (the new owner): planet 14, a field 0-5, points 100-400 |
| C2 | artifact | Freighter (10) unloads on player 1 planet 3 (P 100, artifact): the defender holds | planet 3: owner 1, artifact False; 0x05e to player 1 (the defender): planet 3, points 100-400; nothing to player 0 |
| C3 | artifact | player 1 planet 9 (P 87, artifact), no fleet | planet 9: owner 1, artifact True; no 0x05e; flag kept |
| C4 | artifact | player 0 planet 11 (P 100, artifact): a player 0 Freighter unloads 10 colonists onto it | planet 11: owner 0, artifact True; no 0x05e; flag kept (inferred: unloading on one's own planet is not a landing) |

## Round 4 results

`python3 experiments/tk/check4.py RUNDIR` prints the checks and the
artifact and scrap messages per setting (`check2.parse` now accepts the
dump's bare `artifact` and `artbit` tokens). Raw files are in apparatus
`evidence/tk4/`. The three tk305 runs at cycles 20000, 30000 and 50000 and
tk304 at 15000 were re-dumped after the host had run, because the dump
step hit a Combat Lab rebuild; the host files are unchanged.

| Run | Result |
|---|---|
| TK-301, TK-302 | All 18 checks held: bombs 811/852 (Cherry) and 858/874 (Smart), defender keeps 31/66 (grown 35/75), load exactly 30 colonists, 25 and 210 ironium |
| TK-303 | A2, A3 held in all six settings: 0x05e to player 0, fields 0–5 all seen, points 122–272 (A2) and 53–196 (A3). A1, A4, A5 void: owned planets lost the artifact because Combat Lab set only the file flag (the host reads the installations bit on owned planets). A4's prediction (no 0x05e) also contradicted the binary reading |
| TK-304 | Same fields and points as TK-303 in every setting: slower tech does not halve them |
| TK-305 | First starbase: Hush-a-Boom part 5, level 5, nothing 2 of 12; second and third starbases 0x141 always. Above the model's rates (part 0.215 of passing attempts, pass 0.5); open |
| TK-306 | All 12 checks held in three settings: capture gives 0x05e to the captor, a defender that holds gets 0x05e, an untouched owned planet and an own-planet unload keep the artifact |# TK: planet takeover corpus (TK-001 to TK-004)

Tests the stars-decomp takeover reading (`docs/takeover.md`,
`docs/takeover-predictions.md` T-1..T-35, `tools/takeover.py`, branch
`claude/project-thread-sgfw6k`, PR #8) against the original game.
Predictions below were committed **before** any TK run.

## Setup

Combat Lab (`docs/ORACLE.md`), one generation 2400 → 2401 per run with the
random stream pinned (`tools/fleetlab/pinned-turn`, cycles fixed 20000
unless stated). Specs: `tkNNN.spec`, written by `gen.py`.

- Player 1 owns every target planet (`planet N owner 1`), with the
  environment set to 50/50/50 (100% habitability for both players' races,
  which are identical JOAT races, growth 15%) and no production queue.
  Player 0 attacks. Mutual enemies unless stated. Player 1 has energy
  tech 3 (best planetary defense: SDI, 1% each) unless stated.
- Bombers orbit the target from the start. Transports and colony ships
  start 20 ly away and arrive this turn (warp 6), so they act after
  movement; "in orbit" means the task is on waypoint 0.
- Population in this document is in **units of 100 colonists** (the
  file's unit). P = population at the start of the turn; P' = population
  after this turn's growth, which happens before bombing and before the
  arrival drops. For an uncrowded 100% planet,
  P' = P + floor((15·P + carry)/100). Planet 5 in TK-001 and TK-003 is a
  growth control.

## Predictions (stars-decomp reading)

Bombing (TK-001, deterministic: no random rounding is needed in these
cases).

| Planet | Case | P → P' | Predicted after the turn | Alternative it rules out |
|---|---|---|---|---|
| 5 | control, carry 37 | 87 → 100 | pop 100, carry 42 | |
| 0 | T-12: 10 Cherry | 800 → 920 | **690** (25% added) | ≈715 if percentages compound |
| 1 | T-10: 1 Lady Finger | 9 → 10 | **7** (minimum 300 colonists) | 9 or 10 without a minimum |
| 2 | T-11: 1 LBU-17 | 9 → 10 | **9** (no minimum; a 0 kill becomes 1) | 7 with a minimum |
| 3 | T-14: 20 Peerless | 1000 → 1150 | **412** (smart bombs multiply: 64.2%) | 0 if they added (100%) |
| 4 | T-14: 20 Peerless | 1 → 1 | **1** (smart bombs never empty a planet) | 0 |
| 6 | T-15: 1 LBU-32, mines 30, factories 30 | 870 → 1000 | pop **997**, mines **16**, factories **16** | |
| 7 | T-6: 20 Cherry, 100 SDI | 870 → 1000 | pop **666**, defenses **0** | 500 with no coverage |
| 9 | T-7: 20 Cherry, 100 SDI | 87 → 100 | pop **42** (only 4 defenses count at 10,000 colonists), defenses 0 | ≈82 if all 100 counted |
| 10 | T-9: 20 Smart, 100 SDI | 870 → 1000 | pop **812**, defenses **100** (half coverage for smart bombs; no installation damage) | 846 at full coverage, 770 at none |
| 11 | T-17: 1 Orbital Construction Module | 87 → 100 | pop **80** (2,000 colonists per module) | 100 if the OCM is not a bomb |
| 12 | T-18: 1 Multi Contained Munition, mines 10 | 87 → 100 | pop **97** (2% → minimum 300), mines **5** | 100, mines 10 |
| 13 | T-16: 3 Retro, env 55/47/52, original 50/50/50 | 87 | environment **52/50/50** (3 clicks per axis) | e.g. 52/50/52 or 50/49/52 if 3 clicks are shared |
| 14 | T-19: plan "nobody" | 800 → 920 | **920** (no bombing) | 690 |
| 15 | T-19: plan "player 0 only" | 800 → 920 | **920** | 690 |
| 16 | T-19: plan "player 1 only" | 800 → 920 | **690** | 920 |
| 22 | T-19: plan "everyone" | 800 → 920 | **690** | 920 |
| 18 | T-20: 3+2 ships (6+4 Cherry), first fleet attacks, second "nobody" | 800 → 920 | **690** (one pass, 25%) | 704 (two passes) |
| 19 | T-20: same, first fleet "nobody", second attacks | 800 → 920 | **828** (the earlier non-attacking fleet is left out: only the second fleet's 4 Cherry, 10%; medium confidence) | 690 |
| 20 | T-20: same, both attack | 800 → 920 | **690** | 704 if each fleet bombed separately |
| 23 | T-13: 10 Smart + 10 Cherry | 801 → 921 | **606** (smart first, then 25% of the rest) | 607 normal first |

Starbases, ground combat, colonization (TK-002; enemies, SDI).

| Planet | Case | P → P' | Predicted |
|---|---|---|---|
| 0 | T-21/T-26/T-27: 100 arriving vs P 87, carry 37, mines 20, factories 15, scanner 0 | 87 → 100 | owner **0**, pop **9**; mines 20, factories 15 kept; defenses 0; planetary scanner none (31); carry **42** (not reset); production queue = player 0's default |
| 1 | T-22: 100 vs 110 | 96 → 110 | tie goes to the attacker: owner 0, pop **1** |
| 2 | T-23: 100 vs 200 | 174 → 200 | owner 1, pop **90** |
| 3 | T-25: 600 vs 500, 20 SDI | 435 → 500 | troops at 75% of the bomb coverage → strength 569: owner 0, pop **72** |
| 5 | T-26: 300 vs 200, 10 SDI, mines 20, factories 15, scanner 0 | 174 → 200 | owner 0, pop **106**; defenses 0, scanner 31, mines 20, factories 15 |
| 4 | T-28: 100 vs a planet with a bare Orbital Fort | 87 → 100 | refused: the freighter keeps 100 colonists; planet 1/100 |
| 6 | T-5: 100 **in orbit** (unload on waypoint 0) | 87 | invasion before growth: 100 vs 87 → 20 land, then grow as player 0's colony → **23** (an after-growth invasion would give 9) |
| 18 | T-4: 4 Cherry in orbit + 50 arriving (unload), P 9, mines 20, factories 15 | 9 → 10 | bombed empty (minimum 12 units ≥ 10), then the transport colonizes it: owner 0, pop **50**, mines 20, factories 15 |
| 16 | T-4 control: 50 arriving at a planet unowned at the start of the turn | — | nothing lands; the freighter keeps **50** |
| 19 | T-3: 10 Cherry vs a bare Orbital Fort | 800 → 920 | no bombing: **920** |
| 20 | T-2: 10 Cherry + 2 Laser Frigates vs a bare Orbital Fort | 800 → 920 | the fort dies in battle, bombing follows in the same turn: **690**, no starbase |
| 13 | T-1: colony ship in orbit, colonize on waypoint 0, 25 | — | colony made before growth: pop **> 25** this turn |
| 21 | T-1/T-30: colony ship arriving, colonize, 25 | — | colony made after growth: pop exactly **25**; surface minerals = ¾ of the ship's mineral cost |
| 7 | T-31: colony ship arriving at a red planet | — | colonized (no habitability check): owner 0, pop **25** |
| 9 | T-32: player 0 25 vs player 1 12, both arriving | — | owner **0**, pop **25** (not reduced) |
| 10 | T-32: player 0 12 vs player 1 25 | — | owner **1**, pop **12** (reduced by the lower-index rival: 25·(27−13)/27) |
| 14 | T-32: 25 vs 25 | — | **nobody**: planet stays unowned, both colony ships consumed |

TK-003: player 1 at energy 5 (Missile Battery, 2% each); players are
**friends**.

| Planet | Case | P → P' | Predicted |
|---|---|---|---|
| 3 | T-25/T-8: 600 vs 500, 20 Missile Batteries | 435 → 500 | strength 495 < 500: owner 1 keeps **5** |
| 7 | T-8: 20 Cherry (plan "everyone"), 100 Missile Batteries | 870 → 1000 | pop **777**, defenses 0 (SDI would give 666) |
| 0 | T-29: 100 arriving at a **friend's** planet | 87 → 100 | invades like an enemy's: owner 0, pop **9** |
| 5 | control | 87 → 100 | 100 |

TK-004, random cases, several cycle settings; outcome distribution from
`takeover.py bomb`:

| Planet | Case | P → P' | Predicted outcomes |
|---|---|---|---|
| 0 | T-11: 1 Hush-a-Boom (3.0%, no minimum) | 44 → 50 | pop 48 (p 501/1000) or 49 (p 499/1000); a 300-colonist minimum would give 47 |
| 6 | T-15: 1 LBU-17, mines 20, factories 10 | 870 → 1000 | pop 998; factories 5 / mines 9 (p 2/3) or factories 4 / mines 10 (p 1/3); kills always sum to 16 |
| 12 | T-13: 10 Smart + 10 Cherry | 870 → 1000 | pop 658 (p 749/1000) or 657 (p 251/1000) |

### Setup change after run1 (before run2; predictions unchanged)

TK-001..003 run1 used player 0 at tech 3 with 15% research. The generated
2401 files had Cherry, Smart, Peerless, LBU-17 and LBU-32 bombs removed from
player 0's designs (slots empty); Lady Finger, Hush-a-Boom, Retro, the
Orbital Construction Module and the Multi Contained Munition stayed, and
only those bombed. Player 1's energy also rose from 3 to 5 in TK-001 run1
through research. From run2 on, player 0 has tech 26 in every field and
both players research 0%.

### Added after run2, predictions committed before running them

In TK-001 run2 player 1's energy rose from 3 to 5 during the year (all of
its resources went to research: its planets have no production queue),
so the bombing there met Missile Batteries. TK-005 repeats the SDI cases
with only four player-1 planets.

| Run | Planet | Case | P → P' | Predicted |
|---|---|---|---|---|
| TK-005 | 7 | T-6 with SDI (player 1 stays at energy 3) | 870 → 1000 | pop 666, defenses 0 |
| TK-005 | 9 | T-7 with SDI | 87 → 100 | pop 42 |
| TK-005 | 10 | T-9 with SDI | 870 → 1000 | pop 812, defenses 100 |
| TK-005 | 19 | T-20: a Laser Frigate with plan "enemies" (first fleet) and 10 Cherry with plan "nobody" (second fleet) | 800 → 920 | **690**: one attacking fleet triggers bombing with every bomb its owner has at the planet (the reading has no check that the trigger fleet carries bombs) |
| TK-006 | 14 | T-19, players **neutral**, plan "enemies" | 800 → 920 | 920 (no bombing) |
| TK-006 | 16 | neutral, plan "player 1 only" | 800 → 920 | 690 |
| TK-006 | 22 | neutral, plan "everyone" | 800 → 920 | 690 |
| TK-006 | 5 | control | 87 → 100 | 100 |

TK-007 (random cases, committed before running): 14 Hush-a-Boom planets
as in TK-004 planet 0 (48 with p 501/1000, else 49), two T-13 planets
(658 with p 749/1000, else 657) and two T-15 planets (factories 5 / mines
9 with p 2/3, else 4 / 10), one generation per cycles value. The draws
should be independent across planets; the vector of outcomes identifies
the random stream of each run.

## Results

Runs: TK-001..003 run1 (player 0 at tech 3, see above; only the parts
that survived are used), TK-001..004 run2, TK-005/006 run1, TK-004 and
TK-007 under 12 and 14 cycle settings. Values read from the 2401 host file
with `combatlab dump` (`pdetail` lines) and `hst-edit dump`. Raw files:
private `stars-oracle-apparatus`, `evidence/tk/`.

Bombing (TK-001 run2 unless stated):

| Planet | Case | Predicted | Observed | |
|---|---|---|---|---|
| 5 | growth control | 100, carry 42 | 100, carry 42 | matches |
| 0 | T-12 10 Cherry | 690 | 690 | CONFIRMED |
| 1 | T-10 Lady Finger | 7 | 7 (also run1) | CONFIRMED |
| 2 | T-11 LBU-17 | 9 | 9 | CONFIRMED |
| 3 | T-14 20 Peerless | 412 | 412 | CONFIRMED |
| 4 | T-14 20 Peerless on 1 | 1 | 1 | CONFIRMED |
| 6 | T-15 LBU-32 | 997, mines 16, factories 16 | 997, 16, 16 | CONFIRMED |
| 7 | T-6 | 666 (SDI) | 777 | player 1 reached energy 5 during the year; 777 is the Missile Battery value. TK-005: **666** with SDI. CONFIRMED |
| 9 | T-7 | 42 (SDI) | 45 | Missile Battery value (n = 4, s = 0.98⁴: A 461, minimum 55). TK-005: **42**. CONFIRMED |
| 10 | T-9 | 812 (SDI), defenses 100 | 846, defenses 100 | Missile Battery value (smart coverage 0.99⁴⁰). TK-005: **812**. CONFIRMED |
| 11 | T-17 OCM | 80 | 80 (also run1) | CONFIRMED |
| 12 | T-18 MCM | 97, mines 5 | 97, mines 5 (also run1) | CONFIRMED |
| 13 | T-16 3 Retro | env 52/50/50 | 52/50/50, original kept (also run1) | CONFIRMED |
| 14, 15 | T-19 nobody / player 0 only | 920 | 920 | CONFIRMED |
| 16, 22 | T-19 player 1 only / everyone | 690 | 690 | CONFIRMED |
| 18 | T-20 first attacks, second nobody | 690 | 690 | CONFIRMED |
| 19 | T-20 first nobody, second attacks | 828 | **690** | CONTRADICTED: the earlier non-attacking fleet's bombs were included |
| 20 | T-20 both attack | 690 | 690 | CONFIRMED |
| 23 | T-13 Smart + Cherry | 606 | 606 | CONFIRMED |
| TK-005 19 | Laser Frigate (enemies) + bombers (nobody) | 690 | 690 | CONFIRMED |
| TK-003 7 | T-8 Missile Batteries, friends, plan everyone | 777 | 777 | CONFIRMED |
| TK-006 14 | neutral, plan enemies | 920 | 920 | CONFIRMED |
| TK-006 16, 22 | neutral, player 1 only / everyone | 690 | 690 | CONFIRMED |

Starbases, ground combat, colonization (TK-002 run2; run1 gave the same
ground-combat and colonization results):

| Planet | Case | Predicted | Observed | |
|---|---|---|---|---|
| 0 | T-21/T-26/T-27 | owner 0, 9; mines 20, factories 15, defenses 0, scanner none, carry 42 | owner 0, 9, 20, 15, 0, scanner id 31, carry 42 | CONFIRMED (queue: see below) |
| 1 | T-22 tie | owner 0, 1 | owner 0, 1 | CONFIRMED |
| 2 | T-23 | owner 1, 90 | owner 1, 90 | CONFIRMED |
| 3 | T-25 SDI | owner 0, 72 | owner 0, 72 | CONFIRMED |
| 5 | T-26 | owner 0, 106, defenses 0 | owner 0, 106, defenses 0, mines 20, factories 15, scanner 31 | CONFIRMED |
| 4 | T-28 fort | refused, freighter keeps 100 | planet 100, freighter 100 | CONFIRMED |
| 6 | T-5 in orbit | owner 0, 23 | owner 0, 23 | CONFIRMED |
| 18 | T-4 bomb and drop | owner 0, 50; mines 20, factories 15 | owner 0, 50; mines **0**, factories **0** | pop CONFIRMED; the installation figures in the prediction table were an error of this corpus, not of the reading: 4 Cherry destroy 40 installations, i.e. all 35 (`takeover.py` gives 0/0) |
| 16 | T-4 control | freighter keeps 50 | 50 | CONFIRMED |
| 19 | T-3 fort, bombers only | 920, fort kept | 920, fort kept | CONFIRMED |
| 20 | T-2 fort, bombers + frigates | 690, no starbase | battle at planet 20, fort gone, 690 | CONFIRMED |
| 13 | T-1 in orbit | > 25 | 28 | CONFIRMED |
| 21 | T-1 arrival | 25 | 25 | CONFIRMED |
| 7 | T-31 red planet | owner 0, 25 | owner 0, 25 | CONFIRMED |
| 9 | T-32 25 vs 12 | owner 0, 25 | owner 0, 25 | CONFIRMED |
| 10 | T-32 12 vs 25 | owner 1, 12 | owner 1, 12 | CONFIRMED |
| 14 | T-32 25 vs 25 | nobody | unowned, pop 0, both colony ships gone, surface 22/7/22 = both ships' contributions (4/1/5 + 18/6/17) | CONFIRMED |
| TK-003 3 | T-25 Missile | owner 1, 5 | owner 1, 5 | CONFIRMED |
| TK-003 0 | T-29 friend | owner 0, 9 | owner 0, 9 | CONFIRMED |

- T-26 queue: no captured planet had a production-queue block afterwards,
  and neither did player 0's homeworld; this game's default queue may be
  empty, so the queue part is not tested.
- T-30: an arriving colony ship of player 0 left 18/6/17 kT on the new
  colony at tech 3 (run1) and 4/1/5 at tech 26 (run2); player 1's (tech 3)
  18/6/17. Not compared with a cost table here.
- Events: the attacker's `.M1` event block has a record with id 0x135
  naming the refused freighter and planet 4, and one with id 0x55 naming
  the TK-002 planet-16 freighter (read from the hex; the record layout is
  otherwise not decoded).

Random roundings (TK-004 under 12 cycle settings, TK-007 under 14):

| Draw | Predicted | Observed |
|---|---|---|
| Hush-a-Boom on 50 | 48 p 0.501, 49 p 0.499; never 47 | TK-007: 42 × 48, 56 × 49 over 7 distinct streams × 14 planets; never 47 |
| Smart + Cherry on 1000 | 658 p 0.749, 657 p 0.251 | TK-007: 9 × 658, 5 × 657 (7 streams × 2) |
| LBU-17, mines 20, factories 10 | f 5 / m 9 p 2/3, f 4 / m 10 p 1/3; pop 998 | TK-007: 7 / 7 (7 streams × 2); pop always 998; never another split |

TK-007's 14 cycle settings gave 7 distinct outcome vectors: 10000,
12000, 15000, 17000 each their own; 20000 = 22000 = 25000; 30000 = …
= 45000; 50000 = 60000 = 70000. The host files differed byte-wise
between all settings, including settings with identical outcomes, while
two runs at 20000 were byte-identical (TK-004).


# Round 2: TK-101 to TK-115

Round 2 tests the takeover rules round 1 could not reach (docs/TAKEOVER.md
"Open experiments"), plus the rules added in stars-elegy #34 (order inside a
phase, phase-start ownership, unload amounts, colonize retries, tech on
capture). Specs and predictions are written by `gen2.py`; the predictions
below were committed before any of these runs. `check2.py` compares them
with the run dumps.

## Round 2 setup

- Combat Lab (CB, game id 82222, two JOAT players), as round 1, except
  TK-113, which uses **TK3**: a tiny three-player game built with
  `tools/fleetlab/new-game` (definition: tiny, seed 11, no random events,
  three human players of the PG000 race file: Super Stealth, growth 10%,
  hab 50±35). Homeworlds: player 0 planet 16, player 1 planet 12, player
  2 planet 19.
- Race changes (all checked legal before the runs: no message 0x117 in a
  generated year): War Monger, Alternate Reality and Claim Adjuster with
  NRSE, CE, OBRM, LSP and BET (`lrt 0x1b80`); Inner Strength alone; JOAT
  with Ultimate Recycling needs the same five (`lrt 0x1ba0`; UR alone gave
  0x117 and the race was penalized). BET changes miniaturization (80% at
  26 instead of 75%), so colony minerals of these races differ from JOAT's.
- Default production queue and "only leftover to research" (new CombatLab
  keys `defqueue`, `defleftover`): player 0 queue auto factories 10, auto
  mines 5, auto defenses 3, auto min terraform 2, auto max terraform 1
  (item ids 1, 0, 2, 4, 5), leftover on. CB has no default queue, so a
  capture or colony gets this queue only from the rule under test.
- Player 0 tech 26 unless stated, research 0% for everyone. Ship costs
  are computed with COMPONENTS.md "Cost for an owner" (`gen2.py
  item_cost`). Colonizer (Colony Ship + Long Hump 6 + Colonization Module)
  at tech 26 costs 6/2/7 kT; 30 of them 180/60/210.
- Unowned planets start with no surface minerals.
- Populations in units of 100 colonists; growth before the after-movement
  phase (KERNEL.md), so P = 87 is 100 at the after-movement drops.

## Round 2 predictions

### TK-101: T-36 colony ship minerals, player 0 at tech 5 in every field

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-36 | Colonizer (Colony Ship + Long Hump 6 + Colonization Module) arrives at unowned planet 21, colonize 25, tech 5 | planet 21: owner 0, pop 25, surface 17/6/15 |

### TK-102: T-36 colony ship minerals, player 0 at tech 10 in every field

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-36 | Colonizer (Colony Ship + Long Hump 6 + Colonization Module) arrives at unowned planet 21, colonize 25, tech 10 | planet 21: owner 0, pop 25, surface 12/4/12 |

### TK-103: T-36 colony ship minerals, player 0 at tech 15 in every field

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-36 | Colonizer (Colony Ship + Long Hump 6 + Colonization Module) arrives at unowned planet 21, colonize 25, tech 15 | planet 21: owner 0, pop 25, surface 9/3/8 |

### TK-104: T-37 player 0 tech 26 except electronics 7; research field energy

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-37 | designs after generation; research field energy | design 0 kept; design 1 kept; design 2 kept; design 3 kept; design 4 part removed; design 5 part removed; design 6 kept; design 7 kept; design 8 kept; design 9 kept; design 10 kept; design 11 kept; design 12 kept; design 13 kept |

### TK-105: T-37 player 0 tech 26 except electronics 7; research field elec

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-37 | designs after generation; research field elec | design 0 kept; design 1 kept; design 2 kept; design 3 kept; design 4 part removed; design 5 part removed; design 6 kept; design 7 kept; design 8 kept; design 9 kept; design 10 kept; design 11 kept; design 12 kept; design 13 kept |

### TK-106: T-24/T-26 War Monger attacker (NRSE CE OBRM LSP BET), default queue and leftover

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-24 | WM 100 arriving vs P=131 (150 after growth) | planet 0: owner 0, pop 9 |
| A2 | T-26 | the captured planet gets the WM default queue and leftover setting | queue 0: 1:10, 0:5, 2:3, 4:2, 5:1; planet 0: leftover True |
| B | control | P=131, nothing arrives | planet 5: owner 1, pop 150 |
| C | T-25 | WM 600 arriving vs P=435 (500), 20 SDI | planet 3: owner 0, pop 248, defenses 0 |
| D | T-26/BET | WM (BET) Colonizer arrives at unowned planet 21, colonize 25 | planet 21: owner 0, pop 25, surface 3/1/4; queue 21: 1:10, 0:5, 2:3, 4:2, 5:1; planet 21: leftover True |

### TK-107: T-33 Alternate Reality player 0 (NRSE CE OBRM LSP BET), default queue

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-33 | AR OCM ship arrives at unowned planet 21, colonize 25 | planet 21: owner 0, pop 25, surface 5/2/5; queue 21: 4:2, 5:1; planet 21: leftover True; planet 21 starbase design 0 |
| B | T-33 | AR freighter 100 arriving, unload on player 1 planet P=87 | planet 0: owner 1, pop 100; fleet 0/1: col 100 |

### TK-108: T-26 Claim Adjuster both players (NRSE CE OBRM LSP BET), default queue

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-26 | CA 100 arriving vs CA P=87, env 50/50/50 orig 55/47/52 | planet 0: owner 0, pop 9, env 55/47/52; queue 0: 1:10, 0:5, 2:3 |
| B | control | CA P=87, env 50/50/50 orig 55/47/52, nothing arrives | planet 5: owner 1, pop 100, env 50/50/50 |
| C | T-26/BET | CA Colonizer arrives at unowned planet 21, colonize 25 | planet 21: owner 0, pop 25, surface 3/1/4; queue 21: 1:10, 0:5, 2:3; planet 21: leftover True |

### TK-109: T-24 Inner Strength defender

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-24 | 150 arriving vs IS P=87 (100) | planet 0: owner 1, pop 18 |
| B | T-24 | 300 arriving vs IS P=87 (100) | planet 3: owner 0, pop 118 |
| C | control | IS P=87, nothing arrives | planet 5: owner 1, pop 100 |

### TK-110: T-24 War Monger attacker against Inner Strength

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-24 | WM 150 arriving vs IS P=87 (100) | planet 0: owner 0, pop 28 |
| B | control | IS P=87, nothing arrives | planet 5: owner 1, pop 100 |

### TK-111: T-34 scrap and T-35 remote mining over two years; player 1 UR (plus NRSE CE OBRM LSP BET)

Game CB, 2 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| S1 | T-34 | 30 Colonizers scrap at player 0 planet 0 with a starbase: 4C/5 | planet 0: surface 144/48/168 |
| S2 | T-34 | 30 Colonizers scrap at player 0 planet 1 without a starbase: C/3 | planet 1: surface 60/20/70 |
| S3 | #34/T-34 | S2 at planet 2 with cargo 100/0/0 and 50 colonists: cargo added, colonists join before growth | planet 2: surface 160/20/70, pop 157 |
| S4 | T-34 | 30 Colonizers scrap at UR player 1 planet 3 with a starbase: 9C/10 | planet 3: owner 1, surface 162/54/189 |
| S5 | T-34 | 30 Colonizers scrap at UR player 1 planet 4 without a starbase: 9C/20 | planet 4: owner 1, surface 81/27/94 |
| S6 | T-34 | S5 at planet 5 with 50 colonists: colonists do not join (P 87 -> 100) | planet 5: owner 1, pop 100, surface 81/27/94 |
| S7 | T-34 | 30 Colonizers scrap at unowned planet 6: C/3 on the surface | planet 6: owner -1, surface 60/20/70 |
| S8 | T-34 | 30 Colonizers scrap in deep space at (1200,1220): C/3 salvage | salvage at 1200,1220: 60/20/70 |
| S9 | T-34 | 30 Colonizers scrap at player 0 planet 7, second waypoint to planet 10: scrapped at 7 | planet 7: surface 60/20/70 |
| S10 | T-34 | 30 Colonizers arrive at player 0 planet 9 with scrap: nothing in year 1, C/3 in year 2 | planet 9: surface 0/0/0; fleet 0/9: ships 12:30; planet 9: surface 60/20/70 (year 2) |
| M1 | T-35 | Miner24 (24 robots) stationary at unowned planet 13, conc 100/50/25 | planet 13: surface 24/12/6; planet 13: surface 48/24/12 (year 2) |
| M2 | T-35 | Miner24 arrives at unowned planet 14, conc 100/50/25: nothing in year 1, mines in year 2 | planet 14: surface 0/0/0; planet 14: surface 24/12/6 (year 2) |
| M3 | T-35 | Miner24 stationary at player 1 planet 15: nothing | planet 15: surface 0/0/0 |
| M4 | T-35 | Miner24 stationary at player 0 planet 16: nothing | planet 16: surface 0/0/0 |

### TK-113: several bombers on one planet; colonize retries after a tie (three players, Super Stealth, growth 10%)

Game TK3, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| B1 | bombing order | players 0 and 2, 10 Cherry each, on player 1 P=728 (800): 800 -> 600 -> 450 | planet 13: owner 1, pop 450 |
| B2 | bombing order | player 0 10 Smart, player 2 10 Cherry, on P=37 (40): smart first 40 -> 36 -> 6 | planet 9: owner 1, pop 6 |
| B3 | bombing order | player 0 10 Cherry, player 2 10 Smart, on P=37 (40): cherry first 40 -> 10 -> 9 | planet 3: owner 1, pop 9 |
| R1 | #34 retry | before movement: players 0 and 2 unload 150 each on P=100 (tie, emptied), player 0 Colonizer in orbit retries: player 0 owns 25 after movement | planet 23: owner 0, pop 25, surface 4/1/5; fleet 0/3 gone |
| R2 | #34 retry LEGACY BUG | after movement: players 0 and 2 arrive with 150 each on P=100 (110), player 0 Colonizer arrives: retry consumes it, colonists lost, planet unowned | planet 26: owner -1, surface 4/1/5; fleet 0/5 gone |

### TK-114: #34 phase-start ownership record and own-planet unload amounts; player 1 Lady Finger bombers

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| PS1 | #34 phase start | unowned planet 13: player 0 Colonizer in orbit colonizes 25 (28 after growth), player 1 10 Lady Finger bomb it empty, player 0 freighter arrives with 50 and unloads: player 0 owns 50 | planet 13: owner 0, pop 50, surface 4/1/5; fleet 0/1: col 0 |
| PS2 | T-4 control | unowned planet 16 with player 1 bombers in orbit; player 0 freighter arrives with 50: refused, keeps 50 | planet 16: owner -1; fleet 0/2: col 50 |
| U1 | #34 unload | own planet 0 P=87, freighter in orbit unloads all 50 before growth: 137 -> 157 | planet 0: pop 157; fleet 0/3: col 0 |
| U2 | #34 unload | own planet 1 P=87, freighter arrives and unloads all 50 after growth: 100 + 50 | planet 1: pop 150; fleet 0/4: col 0 |
| U3 | #34 unload | own planet 2 P=87, in orbit, cargo 100/40/0/50: unload exactly 30 Ir, all Bo, exactly 20 colonists | planet 2: pop 123, surface 30/40/0; fleet 0/5: fe 70, bo 0, col 30 |
| U4 | #34 unload | own planet 3 P=87, in orbit, cargo 100/0/0/50: set amount Ir 60, colonists 10 | planet 3: pop 146, surface 40/0/0; fleet 0/6: fe 60, col 10 |
| U5 | #34 unload | own planet 4 P=87, in orbit, cargo 100/0/0/50: unload exactly 500 Ir (capped at 100), set waypoint colonists to 120 (unloads 33) | planet 4: pop 138, surface 100/0/0; fleet 0/7: fe 0, col 17 |

### TK-115: #34 tech on capture: player 0 tech 3, player 1 weapons 10; two captures

Game CB, 1 year(s). Cycles 20000, 12000, 15000, 25000, 30000, 40000, 50000, 17000.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | #34 tech | 100 arriving vs P=87 (100) on planet 0: captured with 9 | planet 0: owner 0, pop 9 |
| B | #34 tech | 100 arriving vs P=87 (100) on planet 5: captured with 9 | planet 5: owner 0, pop 9 |
| T | #34 tech | player 0 ends at weapons 3 or 4 (one gain at most per year), other fields 3 | tech (0,) weapons 3 or 4; others 3 |


## Round 2 follow-up predictions (written after TK-101..TK-115 ran, before these runs)

TK-108 A kept 50/50/50 because player 0 is also Claim Adjuster and its
end-of-year terraforming would undo a revert, which the prediction forgot;
TK-116 repeats the capture with a JOAT attacker. TK-107 lost AR colonists in
flight (100 → 97, 25 → 24); TK-117 tests the loss rule
`trunc((C + 11)·3/100)` for C > 10, in moving fleets only (stars-decomp
fleet-movement reading).

### TK-116: T-26 Claim Adjuster defender captured by a JOAT attacker

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-26 | JOAT 100 arriving vs CA P=87, env 50/50/50 orig 55/47/52: env back to 55/47/52 | planet 0: owner 0, pop 9, env 55/47/52, orig 55/47/52 |
| B | control | CA P=87, env 50/50/50 orig 55/47/52, nothing arrives | planet 5: owner 1, pop 100, env 50/50/50 |

### TK-117: Alternate Reality colonists in moving and stationary freighters

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | AR loss | AR freighter with 10 moving through deep space: loses trunc((C + 11)·3/100) if C > 10 | fleet 0/0: col 10 |
| B | AR loss | AR freighter with 11 moving through deep space: loses trunc((C + 11)·3/100) if C > 10 | fleet 0/1: col 11 |
| C | AR loss | AR freighter with 40 moving through deep space: loses trunc((C + 11)·3/100) if C > 10 | fleet 0/2: col 39 |
| D | AR loss | AR freighter with 200 moving through deep space: loses trunc((C + 11)·3/100) if C > 10 | fleet 0/3: col 194 |
| E | AR loss | AR freighter with 200 stationary in deep space: no loss | fleet 0/4: col 200 |


## Round 2 results

Checked with `python3 experiments/tk/check2.py RUNDIR` (pinned-turn output
per run; raw files in private `stars-oracle-apparatus` `evidence/tk2/`).
Every run at cycles 20000; TK-115 also at seven other settings; TK-111 ran
2401 and then 2402 from its own output.

| Run | Checks | Result |
|---|---|---|
| TK-101..103 | T-36 colony minerals at tech 5/10/15 | all OK: 17/6/15, 12/4/12, 9/3/8 |
| TK-104, 105 | T-37 design check, field energy / electronics | all 28 OK: LBU-17 and LBU-32 removed in both |
| TK-106 | WM invasions, queue, leftover, BET colony | all 8 OK |
| TK-107 | AR colonize, queue, starbase, refused unload | 4 OK, 2 MISS: colonists lost in flight (25 → 24 landed, 100 → 97 kept) |
| TK-108 | CA capture, queue, colony | 5 OK, 1 MISS: env 50/50/50, not 55/47/52 |
| TK-109, 110 | IS defender, WM vs IS | all 5 OK |
| TK-111 | scrap S1–S10, remote mining M1–M4, two years | all 18 OK (salvage: a packet-type object, dest 1023, 60/20/70) |
| TK-113 | several bombers B1–B3, colonize retries R1, R2 | B1–B3 OK; R1, R2 MISS (no retry) |
| TK-114 | phase-start ownership, own-planet unload amounts | all 14 OK |
| TK-115 | tech on capture, 8 cycle settings | all OK; weapons 3 → 4 in 5 of 8, never more, no other field |
| TK-116 | CA defender, JOAT attacker | env back to 55/47/52 (OK); `orig` no longer stored, see below |
| TK-117 | AR colonists in flight | all 5 OK: 10 → 10, 11 → 11, 40 → 39, 200 → 194 moving; 200 stationary kept |

Misses and what they show:

- **TK-107 A and B (prediction error).** AR colonists in a moving fleet
  lose `trunc((C + 11)·3/100)` for C > 10 (a movement rule the prediction
  left out; TK-117 then confirmed it): 25 → 24 before colonizing, 100 →
  97 in the refused freighter. The rules under test held: the colony got a
  starbase of design 0 and the queue minus items 0–2; the unload was
  refused and the colonists stayed in the fleet.
- **TK-108 A (prediction error).** Both players were Claim Adjuster, so the
  new owner's end-of-year CA terraforming put the captured planet back at
  its ideal 50/50/50. TK-116, with a JOAT attacker, showed the revert:
  55/47/52 after capture. The file then no longer marks the planet as
  terraformed (no separate original values), which fits env = original;
  the `orig` part of that check was over-specified.
- **TK-113 R1 and R2 (reading contradicted).** After players 0 and 2 tied
  (150 each on 100: planet emptied, nobody landed), player 0's colony ship
  whose colonize had failed in that phase did not retry, before movement
  or after. It ended in orbit with its 25 colonists and its waypoint task
  cleared (event 0x4e to player 0 for each ship); the planet stayed
  unowned with no minerals. stars-elegy #34's load-phase retry and its
  after-movement LEGACY BUG did not occur here.

## Round 2b predictions (T-39, T-40; written before these runs)

stars-decomp #16 reconciled TK-113: every colonize failure ends the order
(no retry). It adds T-39 (other colonize failures end the order too) and
T-40 (a CA capturing a CA planet: the revert to the original environment,
then the new owner's end-of-year CA terraforming from it, by `c` per axis,
the best terraform part it may use, never past its centre 50). T-39c (the
order given again by `.X` the next year) needs crafted orders and is not
run. Whether a CA without TT may use Total Terraform parts is the open
point between TK-118 (axis parts, c = 15) and TK-119 (TT, c = 30); TK-119's
race (`lrt 0x1b82`) is checked for 0x117 in its own run.

### TK-118: T-40 CA attacker, tech 26, no Total Terraform (axis parts: c = 15), captures a CA planet

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-40 | CA 100 arriving vs CA P=87, env 60/40/60 orig 80/20/80, attacker c = 15 | planet 0: owner 0, pop 9, env 65/35/65, orig 80/20/80 |
| B | control | CA P=87 (player 1, tech 3: c = 3), env 60/40/60 orig 80/20/80, nothing arrives: no target inside orig ± 3 improves it, env stays | planet 5: owner 1, pop 100, env 60/40/60, orig 80/20/80 |

### TK-119: T-40 CA attacker, tech 26 with Total Terraform (TT; c = 30), captures a CA planet

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-40 | CA 100 arriving vs CA P=87, env 60/40/60 orig 80/20/80, attacker c = 30 | planet 0: owner 0, pop 9, env 50/50/50, orig 80/20/80 |
| B | control | CA P=87 (player 1, tech 3: c = 3), env 60/40/60 orig 80/20/80, nothing arrives: no target inside orig ± 3 improves it, env stays | planet 5: owner 1, pop 100, env 60/40/60, orig 80/20/80 |

### TK-120: T-40 CA attacker, no terraform tech (biotech 0: c = 0), captures a CA planet

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-40 | CA 100 arriving vs CA P=87, env 60/40/60 orig 80/20/80, attacker c = 0 | planet 0: owner 0, pop 9, env 80/20/80, orig None |
| B | control | CA P=87 (player 1, tech 3: c = 3), env 60/40/60 orig 80/20/80, nothing arrives: no target inside orig ± 3 improves it, env stays | planet 5: owner 1, pop 100, env 60/40/60, orig 80/20/80 |

### TK-121: T-39 colonize failures end the order

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | T-39a | Colonizer (25) in orbit at player 1 planet P=9 (10), 10 Cherry bomb it empty: the colony ship keeps 25, task 0; planet unowned | planet 0: owner -1; fleet 0/0: col 25, task 0 |
| B | T-39b | Freighter (25, no colony module) in orbit at unowned planet 21 with colonize: keeps 25, task 0, planet unowned with no minerals | planet 21: owner -1, surface 0/0/0; fleet 0/2: col 25, task 0 |


## Round 2b results

| Run | Result |
|---|---|
| TK-118 | env 65/35/65, original 80/20/80 kept (OK); control env unchanged (OK) |
| TK-119 | env 50/50/50, original 80/20/80 (OK); TT race legal (no 0x117) |
| TK-120 | env 80/20/80, no separate original stored (OK) |
| TK-121 | T-39a and T-39b all OK: the ships kept 25 colonists, task 0; planets unowned, no minerals |

Every environment check held. The population values in TK-118..120 were
the corpus author's error: at 60/40/60 the race's habitability is below
100%, so P = 87 grew to 96 (not 100), and the captures then landed 12
(110 against 96, the ground combat rule) instead of 9. The checker shows
these as MISS on `pop` only.


# Round 3: TK-201 to TK-203

Round 3 sweeps the rules `docs/TAKEOVER.md` still tagged BINARY-ONLY after
rounds 1 and 2 (the rest were confirmed by round 2, the FO corpus and the
MG runs; see the TAKEOVER.md tags). Specs and predictions are written by
`gen3.py`, which reuses the round-2 spec writer; the predictions below were
committed before any of these runs. They restate the private binary
reading (stars-decomp `docs/takeover.md`, `docs/messages/`) as behavior.

## Round 3 setup

- Combat Lab (CB), two JOAT players, enemies, research 0%; player 0 tech
  26. Player 1 tech 3, except TK-202 (energy 26, so Neutron Shield
  defenses, `c = 38`) and TK-203 (tech 0 in every field).
- Bombers fly plan 0 ("Enemies"); freighters and colony ships fly plan 1
  ("Nobody"), so they never start a bombing pass.
- Message order is read from the order of records in each player's `.M`
  file (`tools/fleetlab/events.py`).
- TK-201 runs two years at cycles 20000 and 30000 (the second year only for
  the homeworld mark). TK-202 and TK-203 run one year at twelve cycle
  settings that reached different streams before (ORACLE.md).

## Round 3 predictions

Working for TK-202. Twenty Neutron Shields counted: `s = 0.962^20 =
0.4610`. One Lady Finger: `I = round(2·0.7305) = 1`, `A = round(6·s) = 3`,
`M = round(3·s) = 1`, so 1000 → 997 with no population draw. Two Lady
Fingers: `I = 3`, `A = 6`, `M = 3`, 1000 → 994. Undefended, two Lady
Fingers: `I = 4`, `A = 12`, `M = 6`, 1000 → 988. With `I = 1` on mines 1,
factories 20, defenses 20 (`T = 41`), factories and defenses each lose 1
with chance 20/41, and the mines take the rest, `1 − f − d`. When both lose
one, the rest is −1: the rule says the mines then lose nothing (they stay
at 1, not 2).

Scrap tech (TK-203). Each scrap at a starbase is one attempt for the planet
owner: a 1/2 draw, then 13 Mystery Trader draws that give nothing, then up
to 6 field draws until one names a field where the scrapped ships' parts
needed more than the owner has. Long Hump 6 needs propulsion 3 and the
Scout hull nothing, so only propulsion can come up.

### TK201: order across planets, foreign and deep-space unloads, emptying own planets, colonize failures; second year for the homeworld mark

Game CB, 2 year(s). Cycles 20000, 30000.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A | drop order | fleet 0 Freighter unloads 100 colonists on player 1 planet 14 (P 10); fleet 1 Freighter unloads 100 on player 1 planet 3 (P 10); both in orbit, before movement | planet 14: owner 0, pop 103; planet 3: owner 0, pop 103; player 0 invasion messages: planet 14 before planet 3 (fleet order), not planet order |
| B | bombing order | fleet 2 Cherry2 bomber at player 1 planet 13 (P 87); fleet 3 Cherry2 at player 1 planet 2 (P 87); no defenses or installations | planet 13: owner 1, pop 94; planet 2: owner 1, pop 94; player 0 bombing messages: planet 13 before planet 2; player 1's the same order |
| C | minerals to a foreign planet | fleet 4 Freighter with 50 kT ironium unloads all on player 1 planet 9 (P 87, no starbase, surface 0) | planet 9: owner 1, surface 50/0/0; fleet 0/4: fe 0 |
| D | minerals to a foreign planet | fleet 5 the same at player 1 planet 10 with an Orbital Fort | planet 10: owner 1, surface 50/0/0; fleet 0/5: fe 0 |
| E | minerals to an unowned planet | fleet 6 the same at unowned planet 4 (surface 0) | planet 4: owner -1, surface 50/0/0; fleet 0/6: fe 0 |
| F | deep space unload | fleet 7 Freighter at (1200,1230) with 50 kT ironium and 50 colonists: unload all ironium and all colonists | fleet 0/7: fe 0, col 50; 0x02d for the 50 ironium, then 0x165 (colonists refused); no salvage object |
| G1 | loading every colonist | player 0 planet 11 (P 870, growing) and planet 12 (P 50); fleet 8 empty Freighter at planet 12 loads all colonists | fleet 0/8: col 50; planet 12: owner -1, pop 0; 0x02c (50 colonists), then at growth 0x040 for planet 12 (planet 11 before it grew) |
| G2 | emptying the homeworld | player 0 homeworld 17 set to P 50 with no starbase; player 0 planet 16 (P 870, growing); fleet 9 empty Freighter at 17 loads all colonists | fleet 0/9: col 50; planet 17: owner -1, pop 0; planet 17 homeworld mark True, player record names 17; planet 17 homeworld mark True, player record names 17 (year 2) |
| H1 | colonize failure | fleet 10 Colonizer with 25 colonists at (1100,1230), task colonize | fleet 0/10: col 25, task 0; 0x051 (not orbiting a planet), then 0x04e |
| H2 | colonize failure | fleet 11 Colonizer with no colonists at unowned planet 22, task colonize | fleet 0/11: col 0, task 0; planet 22: owner -1; 0x053 (no colonists), then 0x04e |
| I | homeworld mark (T-41) | fleet 12 Freighter unloads 100 colonists on player 1's homeworld 8 (P 10, no starbase); player 1 keeps other planets | planet 8: owner 0; planet 8 homeworld mark True, player record names 8 |

### TK202: mines never go negative; bombing messages for several fleets; player 1 energy 26 (Neutron Shield)

Game CB, 1 year(s). Cycles 20000, 30000, 50000, 10000, 12000, 15000, 17000, 11500, 9800, 6000, 5200, 3700.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| M0 | mines floor | one Lady1 bomber at player 1 planet 0: P 870, mines 1, factories 20, defenses 20 (Neutron Shield, 20 counted): I = 1, T = 41 | planet 0: owner 1, pop 997; factories 20 or 19 (19 w.p. 20/41), defenses the same, independently; mines 0 only when both stay at 20 (p 0.262), else 1; never 2 |
| M2 | mines floor | one Lady1 bomber at player 1 planet 2: P 870, mines 1, factories 20, defenses 20 (Neutron Shield, 20 counted): I = 1, T = 41 | planet 2: owner 1, pop 997; factories 20 or 19 (19 w.p. 20/41), defenses the same, independently; mines 0 only when both stay at 20 (p 0.262), else 1; never 2 |
| M3 | mines floor | one Lady1 bomber at player 1 planet 3: P 870, mines 1, factories 20, defenses 20 (Neutron Shield, 20 counted): I = 1, T = 41 | planet 3: owner 1, pop 997; factories 20 or 19 (19 w.p. 20/41), defenses the same, independently; mines 0 only when both stay at 20 (p 0.262), else 1; never 2 |
| M9 | mines floor | one Lady1 bomber at player 1 planet 9: P 870, mines 1, factories 20, defenses 20 (Neutron Shield, 20 counted): I = 1, T = 41 | planet 9: owner 1, pop 997; factories 20 or 19 (19 w.p. 20/41), defenses the same, independently; mines 0 only when both stay at 20 (p 0.262), else 1; never 2 |
| M13 | mines floor | one Lady1 bomber at player 1 planet 13: P 870, mines 1, factories 20, defenses 20 (Neutron Shield, 20 counted): I = 1, T = 41 | planet 13: owner 1, pop 997; factories 20 or 19 (19 w.p. 20/41), defenses the same, independently; mines 0 only when both stay at 20 (p 0.262), else 1; never 2 |
| M14 | mines floor | one Lady1 bomber at player 1 planet 14: P 870, mines 1, factories 20, defenses 20 (Neutron Shield, 20 counted): I = 1, T = 41 | planet 14: owner 1, pop 997; factories 20 or 19 (19 w.p. 20/41), defenses the same, independently; mines 0 only when both stay at 20 (p 0.262), else 1; never 2 |
| D20 | several fleets | two Lady1 fleets at player 1 planet 20, as M: I = 3, A = 6, M = 3 | planet 20: owner 1, pop 994; factories 19 or 18 (18 w.p. 19/41), defenses the same; mines 0 only when both are 19 (p 0.288), else 1; player 0 gets 0x16f and player 1 0x179 (several installations, defenses stopped a share) |
| D22 | several fleets | two Lady1 fleets at player 1 planet 22, as M: I = 3, A = 6, M = 3 | planet 22: owner 1, pop 994; factories 19 or 18 (18 w.p. 19/41), defenses the same; mines 0 only when both are 19 (p 0.288), else 1; player 0 gets 0x16f and player 1 0x179 (several installations, defenses stopped a share) |
| U21 | several fleets | two Lady1 fleets at player 1 planet 21: P 870, mines 1, no factories or defenses | planet 21: owner 1, pop 988, mines 0; 0x169 to player 0, 0x173 to player 1 (colonists and one installation) |
| U23 | several fleets | two Lady1 fleets at player 1 planet 23: P 870, mines 10, no factories or defenses | planet 23: owner 1, pop 988, mines 6; 0x16a to player 0, 0x174 to player 1 (colonists and several installations) |

### TK203: tech learned from scrapping at a starbase; player 1 tech 0 in every field

Game CB, 1 year(s). Cycles 20000, 30000, 50000, 10000, 12000, 15000, 17000, 11500, 9800, 6000, 5200, 3700.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| S0 | scrap tech | player 0 Scout (Long Hump 6: propulsion 3) scraps at player 1 planet 0 with an Orbital Fort (P 87) | attempt 1: 1/2 to pass, then up to 6 field draws until propulsion comes up: gain w.p. 1/2 x (1 - (5/6)^6) = 0.333; a gain sends player 1 0x13d (field propulsion) instead of 0x141 |
| S2 | scrap tech | player 0 Scout (Long Hump 6: propulsion 3) scraps at player 1 planet 2 with an Orbital Fort (P 87) | attempt 2, made only when S0 gained nothing (else no draws and 0x141): 1/2 to pass, then up to 6 field draws until propulsion comes up: gain w.p. 1/2 x (1 - (5/6)^6) = 0.333; a gain sends player 1 0x13d (field propulsion) instead of 0x141 |
| S3 | scrap tech | the same at player 1 planet 3 with no starbase (control) | 0x140 to player 1, no tech attempt |
| Y | scrap tech | player 1 tech at the end of the year | per stream: propulsion 0 or 1 (1 w.p. 0.555), never 2; every other field 0; the fleet owner (player 0) never gains |


## Round 3 results

Runs in private apparatus `evidence/tk3/`; `python3 experiments/tk/check3.py
RUNDIR` prints the table below from the dumps.

| Run | Result |
|---|---|
| TK-201 (20000, 30000) | every check OK (planet 12's `pop` reads None in the checker because an unowned planet stores none). Capture messages 14, 3, 8 and bombing messages 13, 2: fleet order. Surfaces 50/0/0 at planets 9, 10, 4. Deep space: 0x02d, 0x165, 0x04e, colonists kept, no object. Planets 12 and 17 lost at growth with 0x040. Homeworld 17 unowned and marked in years 1 and 2; homeworld 8 marked under player 0. 0x051 and 0x053 then 0x04e |
| TK-202 (12 settings, 10 outcome vectors) | pop 997 / 994 / 988 everywhere. Single Lady Finger (72 planets): mines 0 with f20/d20 21×, mines 1 with one of f19/d19 40×, mines 1 with f19 and d19 11× (never 2). Two Lady Fingers (24): mines 0 only at f19/d19 (7×). U21 mines 0, U23 mines 6. Messages 0x068/0x072 (count 1 even when 2 were lost), 0x16f/0x179 (count 3), 0x169/0x173, 0x16a/0x174 |
| TK-203 (12 settings) | propulsion 0 → 1 in 8 runs (S0 7, S2 1), never 2 or another field; 0x13d (field 2) on the gaining scrap, 0x141 otherwise, 0x140 at planet 3. Without the gain, leftover research took energy to 1 |

Side observation: the bombing message's installation count is `f + d +
rest` with a negative rest kept (LEGACY BUG, `MESSAGES.md`).


# Round 4: TK-301 to TK-306

Round 4 closes what legal orders can reach on TAKEOVER.md's open list:
Laser Battery and Planetary Shield against bombs and troops, the "load
exactly" action, ancient artifacts (random events on, and with slower
tech), and Mystery Trader parts scrapped at a starbase. Specs and
predictions are written by `gen4.py`; the predictions below were committed
before any of these runs. Colonists given to a foreign planet by a manual
cargo transfer need a client order; their predictions (TK-401 to TK-410)
are in `manual-transfers.md` and wait on client automation. The year's
full draw order went to the owner of `KERNEL.md`'s turn order.

## Round 4 setup

- Combat Lab, two JOAT players (the unedited races, which the host leaves
  unchanged), enemies, research 0%. Player 0 tech 26 (TK-303/304: 10 in
  every field, so artifact points are not added to a maxed field).
- TK-301/302: player 1 energy 10 (best defense Laser Battery, `c = 24`) or
  16 (Planetary Shield, `c = 30`), other fields 3.
- TK-303/304 run on a copy of the base whose `.XY` game options byte
  (offset 0x10) is 0x00 (random events on) or 0x02 (random events on,
  slower tech); Combat Lab has 0x80. CombatLab's new `planetset N
  artifact=1` sets a planet's ancient-artifact flag, and the dump prints
  `artifact`.
- TK-305: player 1 tech 0; player 0's twelve designs each carry 2
  Hush-a-Boom, so the scrapped fleet "shows" 24 Hush-a-Booms (the binary
  caps the count at 25).

## Round 4 predictions

The working for TK-301/302 is in `gen4.py` (single-precision coverage, as
`TAKEOVER.md` "Planetary defenses against bombs").

### TK301: Laser Battery (player 1 energy 10) against bombs and troops; "load exactly"

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| B | defenses | 10 Cherry2 bombers (20 Cherry) at player 1 planet 13: P 870, defenses 100, no other installations; best defense Laser Battery | planet 13: owner 1, pop 811, defenses 0 |
| S | defenses | 10 Smart2 bombers (20 Smart) at player 1 planet 2: P 870, defenses 100 | planet 2: owner 1, pop 858, defenses 100 |
| G | defenses | Freighter (600 colonists) unloads on player 1 planet 14 before movement: P 500, defenses 20 | planet 14: owner 1, pop 35 |
| L1 | load exactly | player 0 planet 11 (P 100): empty Freighter loads exactly 30 colonists | fleet 0/3: col 30; planet 11: owner 0, pop 80 |
| L2 | load exactly | player 0 planet 12 (P 100, surface ironium 25): load exactly 40 ironium | fleet 0/4: fe 25; planet 12: owner 0, surface 0/0/0 |
| L3 | load exactly | player 0 planet 16 (P 100, surface ironium 500): load exactly 300 ironium into a 210 kT hold | fleet 0/5: fe 210; planet 16: owner 0, surface 290/0/0 |

### TK302: Planetary Shield (player 1 energy 16) against bombs and troops; "load exactly"

Game CB, 1 year(s).

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| B | defenses | 10 Cherry2 bombers (20 Cherry) at player 1 planet 13: P 870, defenses 100, no other installations; best defense Planetary Shield | planet 13: owner 1, pop 852, defenses 0 |
| S | defenses | 10 Smart2 bombers (20 Smart) at player 1 planet 2: P 870, defenses 100 | planet 2: owner 1, pop 874, defenses 100 |
| G | defenses | Freighter (600 colonists) unloads on player 1 planet 14 before movement: P 500, defenses 20 | planet 14: owner 1, pop 75 |
| L1 | load exactly | player 0 planet 11 (P 100): empty Freighter loads exactly 30 colonists | fleet 0/3: col 30; planet 11: owner 0, pop 80 |
| L2 | load exactly | player 0 planet 12 (P 100, surface ironium 25): load exactly 40 ironium | fleet 0/4: fe 25; planet 12: owner 0, surface 0/0/0 |
| L3 | load exactly | player 0 planet 16 (P 100, surface ironium 500): load exactly 300 ironium into a 210 kT hold | fleet 0/5: fe 210; planet 16: owner 0, surface 290/0/0 |

### TK303: ancient artifacts, random events on

Game CB, 1 year(s). Cycles 20000, 30000, 50000, 10000, 12000, 15000. Base: random events on.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A1 | artifact | Freighter (100) captures player 1 planet 14 (P 10, artifact) before movement | planet 14: owner 0; 0x05e to player 0: planet 14, a field 0-5, points 100-400 added to that field's research; the planet's artifact flag cleared |
| A2 | artifact | Colonizer (25) colonizes unowned planet 21 (artifact) before movement | planet 21: owner 0; 0x05e to player 0: planet 21, points 100-400; flag cleared |
| A3 | artifact | Colonizer (5) colonizes unowned planet 22 (artifact) before movement | planet 22: owner 0; 0x05e: points scaled by 5/10, so 50-200; flag cleared |
| A4 | artifact | Freighter (10) unloads on player 1 planet 3 (P 100, artifact): the defender wins | planet 3: owner 1; no 0x05e; flag kept |
| A5 | artifact | player 1 planet 9 (P 87, artifact), no fleet | no 0x05e; flag kept (an owned artifact planet gives nothing) |

### TK304: ancient artifacts, random events on, slower tech

Game CB, 1 year(s). Cycles 20000, 30000, 50000, 10000, 12000, 15000. Base: random events on, slower tech.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| A1 | artifact | Freighter (100) captures player 1 planet 14 (P 10, artifact) before movement | planet 14: owner 0; 0x05e to player 0: planet 14, a field 0-5, points 100-400 added to that field's research; the planet's artifact flag cleared |
| A2 | artifact | Colonizer (25) colonizes unowned planet 21 (artifact) before movement | planet 21: owner 0; 0x05e to player 0: planet 21, points 100-400; flag cleared |
| A3 | artifact | Colonizer (5) colonizes unowned planet 22 (artifact) before movement | planet 22: owner 0; 0x05e: points scaled by 5/10, so 50-200; flag cleared |
| A4 | artifact | Freighter (10) unloads on player 1 planet 3 (P 100, artifact): the defender wins | planet 3: owner 1; no 0x05e; flag kept |
| A5 | artifact | player 1 planet 9 (P 87, artifact), no fleet | no 0x05e; flag kept (an owned artifact planet gives nothing) |
| Y | artifact | slower tech on | points are not halved (binary: the halving comes after the points are added and is unused, LEGACY BUG): A1/A2 still 100-400, A3 50-200. If halving applied, every A1/A2 value would be at most 200 |

### TK305: Mystery Trader parts scrapped at a starbase; player 1 tech 0

Game CB, 1 year(s). Cycles 20000, 30000, 50000, 10000, 12000, 15000, 17000, 11500, 9800, 6000, 5200, 3700.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| S0 | scrap MT | a fleet of 12 Hush-a-Boom bombers (12 designs, 2 Hush-a-Boom each) scraps at player 1 planet 0 with an Orbital Fort |  |
| S2 | scrap MT | a fleet of 12 Hush-a-Boom bombers (12 designs, 2 Hush-a-Boom each) scraps at player 1 planet 2 with an Orbital Fort |  |
| S3 | scrap MT | a fleet of 12 Hush-a-Boom bombers (12 designs, 2 Hush-a-Boom each) scraps at player 1 planet 3 with an Orbital Fort |  |
| Y | scrap MT | player 1 at the end of the year | one gain at most per stream. Each attempt: 1/2 to pass; then 13 rand(13) picks, each giving Hush-a-Boom with chance 24% when it names Hush-a-Boom (P(part) = 1 - (1 - 0.24/13)^13 = 0.215); otherwise a level in a field the bombers needed (construction, propulsion, weapons, electronics or biotech), never energy. The first attempt that passes gains (P = 0.875 per stream). A part gain sends 0x13c and sets player 1's Hush-a-Boom bit; a level sends 0x13d |

TK-306 was added after TK-303's owned-planet cases turned out void (see
results). Its predictions were committed before its runs.

### TK306: ancient artifacts on owned planets, random events on

Game CB, 1 year(s). Cycles 20000, 30000, 50000. Base: random events on.

| Case | Rule | Setup | Predicted |
|---|---|---|---|
| C1 | artifact | Freighter (100) captures player 1 planet 14 (P 10, artifact) before movement | planet 14: owner 0, artifact False; 0x05e to player 0 (the new owner): planet 14, a field 0-5, points 100-400 |
| C2 | artifact | Freighter (10) unloads on player 1 planet 3 (P 100, artifact): the defender holds | planet 3: owner 1, artifact False; 0x05e to player 1 (the defender): planet 3, points 100-400; nothing to player 0 |
| C3 | artifact | player 1 planet 9 (P 87, artifact), no fleet | planet 9: owner 1, artifact True; no 0x05e; flag kept |
| C4 | artifact | player 0 planet 11 (P 100, artifact): a player 0 Freighter unloads 10 colonists onto it | planet 11: owner 0, artifact True; no 0x05e; flag kept (inferred: unloading on one's own planet is not a landing) |

## Round 4 results

`python3 experiments/tk/check4.py RUNDIR` prints the checks and the
artifact and scrap messages per setting (`check2.parse` now accepts the
dump's bare `artifact` and `artbit` tokens). Raw files are in apparatus
`evidence/tk4/`. The three tk305 runs at cycles 20000, 30000 and 50000 and
tk304 at 15000 were re-dumped after the host had run, because the dump
step hit a Combat Lab rebuild; the host files are unchanged.

| Run | Result |
|---|---|
| TK-301, TK-302 | All 18 checks held: bombs 811/852 (Cherry) and 858/874 (Smart), defender keeps 31/66 (grown 35/75), load exactly 30 colonists, 25 and 210 ironium |
| TK-303 | A2, A3 held in all six settings: 0x05e to player 0, fields 0–5 all seen, points 122–272 (A2) and 53–196 (A3). A1, A4, A5 void: owned planets lost the artifact because Combat Lab set only the file flag (the host reads the installations bit on owned planets). A4's prediction (no 0x05e) also contradicted the binary reading |
| TK-304 | Same fields and points as TK-303 in every setting: slower tech does not halve them |
| TK-305 | First starbase: Hush-a-Boom part 5, level 5, nothing 2 of 12; second and third starbases 0x141 always. Above the model's rates (part 0.215 of passing attempts, pass 0.5); open |
| TK-306 | All 12 checks held in three settings: capture gives 0x05e to the captor, a defender that holds gets 0x05e, an untouched owned planet and an own-planet unload keep the artifact |

# Round 5: TK-501, TK-502 (manual cargo transfers)

Specs, client command files and predictions come from `gen5.py` (committed
before the runs); the cases are TK-401..412 of `manual-transfers.md`. Each
run is two pinned years (cycles 20000): year 1 from the Combat Lab start;
then the client automation (`docs/ORACLE.md` "Client orders") gives player
0's transfers in year 1's `.M1`, and year 2 runs with the client's `.X1`.
`python3 experiments/tk/check5.py RUNDIR` reads `RUNDIR/<name>/y2/`.

### TK501: manual cargo transfers to an enemy (client orders)

| Case | Setup | Predicted |
|---|---|---|
| TK-410 | fleet 1 gives 30 colonists to player 1's homeworld 8 (starbase) | colonists lost; 0x058 to player 0; planet 8 unchanged apart from growth |
| TK-404 | fleet 2 gives 30 colonists to unowned planet 21 | planet 21: owner -1; 0x002 to player 0 (colonists 30, planet 21) |
| TK-405 | fleet 3 gives 100 ironium to player 1 planet 2 (surface 0) | planet 2: owner 1, surface [100, 0, 0]; 0x042 to player 0 (fleet 3, 100, ironium, planet 2); 0x044 to player 1 |
| TK-403 | player 1 planet 3 (100): fleet 4 unloads 50 colonists by its waypoint task (set in the client) and fleet 5 gives 200 by hand: one ground combat, 250 troops | planet 3: owner 0, pop 182 |
| TK-402 | fleet 6 gives 200 colonists to player 1 planet 14 (100) | planet 14: owner 0, pop 125 |
| TK-401 | fleet 7 gives 30 colonists to player 1 planet 13 (100) | planet 13: owner 1, pop 77; 0x000 to player 0 and 0x003 to player 1, as for an unload |

### TK502: manual cargo transfers to a friend (client orders)

| Case | Setup | Predicted |
|---|---|---|
| TK-411 | players 0 and 1 are friends; fleet 1 gives 200 colonists to player 1 planet 14 (100) | planet 14: owner 0, pop 125; captured as between enemies (the drop code has no relation check): 0x00c to player 0, 0x007 to player 1 |
| TK-412 | fleet 2 gives 100 ironium to player 1 planet 2 (friend) | planet 2: owner 1, surface [100, 0, 0]; 0x042 to player 0, 0x044 to player 1 |

## Round 5 results

Every planet outcome and every drop message held (TK-401..404, TK-410..411).
TK-405 and TK-412 put the ironium on the surface but sent no 0x042/0x044:
a gift to a planet is silent. Raw files, order files and screenshots are in
apparatus `evidence/tk5/`.

## Round 6 predictions: bombing message variants

`gen6.py` writes `tk601.spec` (one pinned year, cycles 20000, Combat Lab
base). It aims at bombing texts that `docs/MESSAGES.md` still lists as
BINARY-ONLY. Which text is sent depends on the installations killed (T),
the colonists killed (K), whether defenses reduced the bombs, and whether
the attacker has a second fleet at the planet (plural texts). Player 1 has
energy 16 (Planetary Shield). `python3 experiments/tk/check6.py RUNDIR`
reads `RUNDIR/tk601/run-20000/`.

| Case | Setup | Predicted |
|---|---|---|
| TK-601 | one LBU-17 bomber at player 1 planet 13: P 500, one factory, nothing else | planet 13: owner 1, factories 0; 0x063 to player 0 (fleet, planet, colonists killed 1 or 2, 1 installation); 0x06d to player 1 |
| TK-602 | as TK-601 at player 1 planet 2, plus a player 0 Freighter (plan Nobody) in orbit | planet 2: owner 1, factories 0; 0x169 to player 0; 0x173 to player 1 |
| TK-603 | one LBU-17 bomber at player 1 planet 14: P 1500, defenses 100, factories 10, mines 10 (69 defenses count after growth, s 0.122) | planet 14: owner 1, pop 1725; 0x067 to player 0 (fleet, planet, 9 installations, defenses stopped a share); no colonists killed; 0x071 to player 1 |
| TK-604 | as TK-603 at player 1 planet 3, plus a player 0 Freighter (plan Nobody) | planet 3: owner 1, pop 1725; 0x16d to player 0; 0x177 to player 1 |
| TK-605 | one LBU-17 bomber and a Freighter at player 1 planet 16: P 500, one defense, nothing else | planet 16: owner 1, defenses 0; 0x16e to player 0 (colonists killed, 1 installation, defenses stopped a share); 0x178 to player 1 |
| TK-606 | three Retro1 bombers and a Freighter at player 1 planet 9: P 87, environment 55/47/52, original 50/50/50 | planet 9: owner 1, env [52, 50, 50]; 0x17a to player 0 (fleet, planet, clicks); no damage message; 0x17b to player 1 |

Predicted never sent (reading, not a run): the texts for "installations
killed, no colonists killed, no defenses" (0x061, 0x062, owner 0x06b,
0x06c, plural 0x167, 0x168, 0x171, 0x172) and for "one installation, no
colonists, defenses" (0x066, 0x070, 0x16c, 0x176). Without defenses any
bomb that kills installations also has a colonist kill rate, and a
non-zero rate kills at least one colonist. With defenses the rate can
round to zero (TK-603), but the installation kill then stays at 2 or
more (at least 8 for an LBU-17, 2 to 3 for a Multi Contained Munition
behind 100 Neutron Shields); the bombs that kill 2 installations
(Lady Finger, Hush-a-Boom) keep a colonist kill unless coverage reaches
99.8% or 98.3%, and 100 Neutron Shields give 97.9%.

## Round 6 results

All six cases held (`check6.py`: every planet check OK and all twelve
messages seen, cycles 20000). TK-601: one factory killed and one colonist
unit (0x063 slots: fleet, planet, 1 colonist unit, 1 installation).
TK-603/604: 9 installations (1 factory, 7 defenses, 1 mine), population
untouched at 1725, percent slot 8777 (87.77% stopped, `1 − 0.97^69`).
TK-605: percent slot 299. TK-606: 8 clicks (3 + 3 + 2). Raw files are in
apparatus `evidence/tk6/`.

## Round 7 predictions: gifts to another player's fleet

`gen7.py` writes `tk503`/`tk504` specs and client command files (same
shape as round 5; the client gives each gift through the fleet panel's
"Other Fleets Here" Cargo button). Predictions are the revised ones in
`manual-transfers.md`, committed before the runs.
`python3 experiments/tk/check7.py RUNDIR` reads `RUNDIR/<name>/y2/`.

### TK503: manual gifts to an enemy fleet (client orders)

| Case | Setup | Predicted |
|---|---|---|
| TK-406 | giver offers 100 ironium to a player 1 Freighter holding 160 kT (50 free) | fleet 1/0: fe 210; credited at order time: receiver full at 210; no 0x046/0x048 (the client may cap the order at 50; 0x0dd to player 0 if 100 reached the host) |
| TK-407 | giver offers 100 ironium to a full player 1 Freighter (210 kT) | fleet 1/1: fe 210; nothing received; no 0x04a/0x04c (the client may refuse the order) |
| TK-408 | giver gives 20 colonists to an empty player 1 Freighter | fleet 1/2: col 20; fleet 0/3: col 0; received in full at order time; no message to either player |
| TK-409 | giver gives 50 mg of fuel to a player 1 Freighter with 100 mg | fleet 1/3: fuel 150; fleet 0/4: fuel 150; received at order time; no message |
| TK-413 | at player 1 planet 2 (P 87, no starbase, surface 0): giver gives 100 ironium to a player 1 Freighter whose waypoint-0 task is unload all | fleet 1/4: fe 0; planet 2: owner 1, surface [100, 0, 0]; the receiver unloads the gift before movement the same year: 0x02d to player 1 (a queued gift would arrive after the unload and stay in the hold) |

### TK504: manual gifts to a friend's fleet (client orders)

| Case | Setup | Predicted |
|---|---|---|
| TK-414 | players 0 and 1 are friends; giver gives 20 colonists to an empty player 1 Freighter | fleet 1/0: col 20; as TK-408 |


## Round 7 results

Run 2026-10-07 (cycles 20000, `check7.py`); raw files, order files and
screenshots in apparatus `evidence/tk7/`.

- The client wrote a cargo record to the other player's fleet for
  ironium and fuel, and did **not** cap the amount: the Cargo Transfer
  dialog shows a foreign fleet's fuel and hold as 0, so 100 ironium went
  out for TK-406 and TK-407.
- TK-406: the receiver ended at 210 kT (50 received), the giver ended
  empty (all 100 gone), and player 0 got 0x0dd (fleet, shortfall 50,
  ironium, request 100). No 0x046/0x048. As revised.
- TK-407: nothing received, the giver lost 100, 0x0dd (shortfall 100,
  request 100). No 0x04a/0x04c. As revised.
- TK-409: 50 mg of fuel moved, giver 150, receiver 150, no message. As
  revised.
- TK-408 and TK-414: the client did not move colonists to another
  player's fleet (the arrow click left 20 colonists on the giver's side)
  and wrote no record, enemy or friend. Not predicted: a legal client
  cannot give colonists to another player's fleet.
- TK-413 is void: the receiver's transport task was cleared at the end of
  year 1 (nothing to unload, 0x04e), so year 2 had no unload to carry the
  gift. The gift stayed in the receiver's hold. Timing within the year is
  instead shown by the 0x0dd shortfall notices, which the order replay
  sends; a queued gift would have sent 0x046 or 0x04a.
