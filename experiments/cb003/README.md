# CB-003 / CB-004: tactics 3 vs 4, starbase engagement, disengage if challenged

Two host turns (2400 → 2401) from specs that differ only in three plan
fields (`gen.py` writes both):

| | CB-003 (`cb003.spec`) | CB-004 (`cb004.spec`) |
|---|---|---|
| player 0 plan 3 tactic (battle T) | 3 maximize net damage | 4 maximize damage ratio |
| player 0 plan 0 attack-who (station at planet 17) | 1 enemies | 2 neutrals and enemies |
| player 1 plan 0 attack-who (gatling station at planet 8) | 2 neutrals and enemies | 3 everyone |

Battles (Combat Lab, tech 26, mutual enemies):

- T (1020,1230), first in fleet order: player 0's Long Destroyer (Phaser
  Bazooka + Colloidal Phaser, plan 3) vs 5 player-1 Laser Frigates
  (attack enemies).
- G (1060,1230): player 0 Gatling Destroyer vs two slow (speed code 0)
  unarmed player-1 stacks: 3 Deflector Destroyers and 3 Armor Destroyers.
- D (1100,1230): 5 player-0 Laser Frigates vs 3 player-1 Laser Frigates
  on "disengage if challenged" (tactic 1, any target, enemies).
- S1 planet 8 (player 1 homeworld, Gatling Station): two unarmed
  player-0 stacks (plan "nobody") plus 5 player-1 Laser Frigates
  attacking enemies.
- S2 planet 17 (player 0 homeworld, default armed Space Station): a lone
  unarmed player-1 visitor (plan "nobody").

## Why

CB-002 found no battle at either homeworld (C9, C10), although the
decomp reading predicts that an armed starbase whose owner's plan 0 says
"enemies" fights an enemy fleet in orbit (P-29's control case). S1 asks
whether the station joins a battle another fleet starts; S2 repeats the
lone-station case with plan 0 "enemies" (CB-003) and "neutrals and
enemies" (CB-004).

## Predictions (committed before the run)

From stars-decomp `docs/combat-predictions.md` / `tools/combat.py`
(8cad60f):

- T (P-11): tactics 3 and 4 score moves identically, so with the same
  random draws the two turns produce the same move sequence and the same
  hits. Caveat: random draws are only nearly repeated between oracle
  launches; a difference would need a determinism check (CB-001 is run a
  second time for this).
- G (P-13): when both stacks are within range 2 of the gatling, one shot
  produces a hit on each with the full 31 damage (× 90% for the deflector
  stack).
- D (P-10): the player-1 stack switches to disengage the first time it
  takes armor damage and leaves the board on its 8th move after that (a
  move counter 7 → 0, visible in the move records).
- S1: battle happens; the station appears as a token (owner 1, starbase
  kind) and its gatling (range 3, initiative 26) fires if targets come in
  range.
- S2: decomp control case: plan 0 "enemies" (CB-003) and "neutrals and
  enemies" (CB-004) should both start a battle with the lone visitor.
  CB-002 already contradicts this for "enemies" at planet 8.
- Every recorded hit replays through `combat.py check`.
