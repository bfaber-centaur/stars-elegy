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
| 19 | T-20: same, first fleet "nobody", second attacks | 800 → 920 | **805** (the earlier non-attacking fleet is left out: 12.5%; medium confidence) | 690 |
| 20 | T-20: same, both attack | 800 → 920 | **690** | 704 |
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
