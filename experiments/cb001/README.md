# CB-001: baseline beams and 202-torpedo salvos

Questions (stars-decomp combat predictions P-2, P-3, P-12, P-16, P-17, P-18,
P-19, P-22; experiments E-1 and E-2): where do tokens start, what token
values does the battle record carry, how much damage does a laser do, and
does a salvo of more than 200 torpedoes hit a fixed, computable number of
times?

Setup: Combat Lab 2400 host file edited by CombatLab (`cb001.spec`): both
players at tech 26 in every field (so no battle tech can be learned), each
player's relation to the other set to enemy, player 0's plan 1 = maximize
damage, any target, attack enemies. Six deep-space locations on y = 1230,
40 ly apart, each holding one stationary fleet per player, so six separate
battles in one host turn 2400 → 2401:

| Battle | x | Player 0 (plan 1) | Player 1 (plan 0, unarmed) |
|---|---|---|---|
| B1 | 1020 | 5 Laser Frigates | 10 Small Freighters |
| B2 | 1060 | 5 Laser Frigates | 4 Frigates with 2 Mole-skin Shields |
| B3 | 1100 | 101 Beta Cruisers (no computer) | 1 Hulk (Battleship, 6 Neutronium) |
| B4 | 1140 | 101 Beta Cruisers with a Battle Super Computer | 1 Hulk |
| B5 | 1180 | 101 Beta Cruisers with BSC | 1 Hulk with Jammer 20 |
| B6 | 1220 | 101 Beta Cruisers with BSC | 1 Hulk with Jammer 50 |

## Predictions (committed before the run)

From the stars-decomp reading (`tools/combat.py`, branch
`claude/project-thread-9j7tt8` at 8cad60f), stated as behavior:

1. Two players: player 0's tokens all start on square (1,4) and player 1's
   on (8,5) of the 10×10 board. One token per (fleet, design).
2. Token values in the record:

   | Design | initiative | computer % | jammer % | shield/ship | armor/ship | speed code | weapon init |
   |---|---|---|---|---|---|---|---|
   | Laser Frigate | 4 | 0 | 0 | 0 | 45 | 2 | 13 |
   | Beta Cruiser | 5 | 0 | 0 | 0 | 700 | 5 | 6 |
   | Beta Cruiser BSC | 7 | 30 | 0 | 0 | 700 | 5 | 8 |
   | Small Freighter | 0 | 0 | 0 | 0 | 25 | 1 | – |
   | Shield Frigate | 4 | 0 | 0 | 50 | 45 | 2 | – |
   | Hulk / J20 / J50 | 10 | 0 | 0 / 20 / 50 | 0 | 3650 | 5 | – |

3. Torpedo hit chance (Beta, 45% accuracy): 45% with no computer;
   62% with BSC vs no jammer; 51% vs Jammer 20; 36% vs Jammer 50.
4. A 202-torpedo salvo (101 ships × 2) hits exactly floor(202·p/100):
   B3 90, B4 125, B5 103, B6 72 hits on the first salvo, independent of the
   random number generator. Each hit does 12 damage to the unshielded Hulk
   (half to shields, which it lacks, half directly to armor); misses leave
   no record against a ship with no shields. First-salvo damage word on the
   one-ship stack: 100% of ships damaged, ceil(12·H·500/3650)/500 of armor:
   B3 148, B4 206, B5 170, B6 119.
5. Laser (10 damage, range 1): a stack's laser slot does ships × 2 × 10;
   90% of it at distance 1, 100% at distance 0. Damage that does not kill
   is spread evenly over the surviving ships of the target stack;
   already-damaged ships die first. Damage left after a stack is destroyed
   carries to the next target. Shield damage is taken first; 4 Shield
   Frigates hold 200 shield points.
6. Every later hit in the record replays exactly through the decomp damage
   model (`combat.py check`).

Random parts not predicted: token order, movement choices and ties.

## Result

Run twice (run1, run2, each after a reset). 6 battles; all 16 hit records
in each run replay through the model, 0 mismatches.

- Start squares, token values and first-salvo hits/damage words
  (90/125/103/72 hits; 148/206/170/119) as predicted, identical in both
  runs. Token movement differed between the runs.
- No miss records against the unshielded Hulks. Laser 90% at distance 1;
  damaged ships died first.
- Unarmed stacks fled and left on their 8th move.
- B1 salvage: 10 Ironium, 13 Germanium (per kill event: cost/3, then a
  quarter lost).
