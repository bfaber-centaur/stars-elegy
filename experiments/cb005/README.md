# CB-005 / CB-006: starbases in battle

CB-002..004 found that an armed starbase alone never fought an unarmed
enemy visitor whose plan attacks nobody, for plan-0 attack-who 1, 2 and 3,
while a station did join (as a token, not firing) a battle that one of
its owner's fleets started (CB-003/004 S1). These two turns separate the
cases. Combat Lab, tech 26, mutual enemies, one host turn each.

CB-005 (`cb005.spec`):
- planet 8 (player 1's Gatling Station, plan 0 attack enemies): two
  player-0 fleets of 5 Laser Frigates attacking enemies.
- planet 17 (player 0's station replaced by an unarmed Space Station,
  shields only): 5 player-0 Laser Frigates attack 5 player-1 Laser
  Frigates whose plan attacks nobody.

CB-006 (`cb006.spec`):
- planet 17 (player 0's default armed station, plan 0 enemies): a lone
  ARMED player-1 visitor (5 Laser Frigates) attacking nobody.
- planet 8 (Gatling Station, plan 0 enemies): a lone UNARMED player-0
  visitor (3 Small Freighters) whose plan attacks enemies.
- (1020,1230): control, 5 player-0 Laser Frigates vs 3 player-1 freighters.

## Predictions (committed before the run)

From the stars-decomp reading (8cad60f) unless marked:

- CB-005 planet 8: battle; the station token (initiative 14, gatling
  range 3, initiative 26) fires at every attacking stack within range 3
  in one shot, full damage each, no dropoff (P-13).
- CB-005 planet 17 (P-4): battle between the fleets; the unarmed station
  does not appear as a token.
- CB-006 planet 17: decomp: the armed station (plan 0 enemies) attacks
  the visitor, which then fires back. CB-002..004 suggest instead that a
  lone station starts nothing; this case adds an armed visitor.
- CB-006 planet 8 (P-5): an unarmed fleet never starts a battle, so the
  only possible starter is the station (decomp: it does; CB-002..004:
  no battle).
- Control: battle.

## Result

- CB-005 planet 8: battle; one Gatling shot hit both attacking stacks with
  the full 62 at range 3. 13 hit records replay; 2 hits on the station are
  outside the check. CONFIRMED.
- CB-005 planet 17: battle; the **unarmed** station appears as a token.
  Contradicts P-4.
- CB-006: no battle at planet 17 or planet 8; the control fought.
  Contradicts the binary reading: across CB-002..006 a starbase alone never
  started a battle.
