# CB-011 to CB-015: starbases join, never start; salvage at planets

Round 2, starbase and planet cases (stars-decomp Q-1..Q-5, Q-13 at
4a8c82b). `gen.py` writes the five specs. New in CombatLab: `planet N
owner P pop X starbase D|none` gives player P extra planets with chosen
starbase designs. Pinned RNG (`fixed 20000`, `-g`), tech 26, one
generation each.

Starbase designs: Laser Station (Space Station, 40 Lasers, 32 Mole-skin),
Unarmed Station (Space Station, 16 Mole-skin), Bare Fort (Orbital Fort,
nothing). Planets: player 0 owns 18 (Laser Station), 19 (Unarmed
Station; Bare Fort in CB-015), 21 (Laser Station), 15 (Laser Station),
22 (no starbase); player 1 owns 5 and 12 (Unarmed Stations).

CB-011..014 use one-sided relations: player 0 sees player 1 as an enemy,
player 1 sees player 0 as neutral. They differ only in player 0's plan 0
attack-who (the plan stations use): CB-011 enemies, CB-012 everyone,
CB-013 player 1, CB-014 nobody.

| | Where | Player 0 | Player 1 |
|---|---|---|---|
| S1 | planet 18 (P0, Laser Station) | station only | 5 Laser Frigates, attack enemies |
| S2 | planet 19 (P0, Unarmed Station) | station only | 5 Laser Frigates, attack enemies |
| S3 | planet 21 (P0, Laser Station) | station only | 3 Small Freighters, attack enemies |
| S4 | planet 5 (P1, Unarmed Station) | 5 Laser Frigates, primary unarmed, no secondary | station only |
| S5 | planet 12 (P1, Unarmed Station) | 5 Laser Frigates, primary armed, no secondary | station only |
| S6 | planet 15 (P0, Laser Station) | 10 Laser Frigates, any, enemies | 6 Small Freighters, nobody |
| S7 | planet 22 (P0, no starbase) | 10 Laser Frigates, any, enemies | 6 Small Freighters, nobody |

CB-015, mutual enemies, player 0 plan 0 = primary starbase, no
secondary, enemies: T1 planet 18, 5 player-0 Laser Frigates (any) and
5 player-1 Laser Frigates; T2 planet 19 (Bare Fort), 10 player-1 Laser
Frigates.

## Predictions (committed before the run)

stars-decomp 4a8c82b:

- S1 (Q-1): CB-011: a battle; player 1's fleet is an aggressor whose own
  attack set is empty (it sees player 0 as neutral), the station supplies
  the attack, and the station fires at player 1's ships.
- S2, S3 (Q-1 controls b, c): no battle (unarmed station; unarmed
  visitor). Also in CB-012..014.
- S1 in CB-012 (everyone) and CB-013 (player 1) (Q-2): usually no battle
  (the attack-mask write goes to the wrong player); a battle would mean
  the stale index happened to equal player 0. CB-014 (nobody, Q-1
  control a): no battle.
- S4 (Q-4): the unarmed station counts as an armed target: player 0's
  frigates (primary unarmed, secondary none) do not fire at it; a battle
  record may exist with no hits. S5 (primary armed): they fire at it.
- S6, S7 (Q-13): no salvage object; a third of the destroyed freighters'
  mineral cost (Small Freighter at tech 26: 4 Ironium, 0 Boranium, 5
  Germanium) goes to the planet surface, ×8/10 with a starbase (S6), ×5/10
  without (S7). Planet minerals start at 0 and these planets have no
  mines. Rounding per kill event is not predicted.
- T1 (Q-3): the station fires at player 1's ships although plan 0's
  primary target is "starbase" with no secondary (stations always use
  any/any/maximize damage).
- T2 (Q-5): station damage below death is recorded in 1/500 of its armor,
  rounded down, at least one step more than before; if destroyed, planet
  19 has no starbase after the turn.
- Every recorded hit replays through `combat.py check` (4a8c82b).
