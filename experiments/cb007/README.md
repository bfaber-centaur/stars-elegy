# CB-007: Regenerating Shields (RS)

Question (P-24, E-4 second half): do RS shields regenerate 10% of their
maximum per round only while above 0, and do RS ships carry 7/5 shields
and half armor from armor parts?

Combat Lab, tech 26, mutual enemies; player 1's lesser racial traits set
to RS only (`lrt 1 0x2000`). One host turn.

- R1 (1020,1230): 5 player-0 Laser Frigates vs 5 player-1 Shield Frigates
  (2 Mole-skin Shields each), unarmed, plan "nobody".
- R2 (1060,1230): 5 player-0 Laser Frigates vs 3 player-1 Armor
  Destroyers (2 Tritanium), unarmed. The `.HST` design record stores the
  non-RS armor 300 (CombatLab does not apply RS), so this also shows
  whether the game recomputes armor.

## Predictions (committed before the run)

stars-decomp (8cad60f):
- Shield Frigate token shield per ship 70 (= 2 × 25 × 7/5).
- At the start of every round after the first, a stack whose shields are
  above 0 regains 10% of its maximum (7 per ship, 35 per stack of 5),
  capped at the maximum; once shields reach 0 they stay 0.
- Armor Destroyer armor 250 per ship (hull 200 + 2 × 50/2), not 300.
- Every hit replays through `combat.py check` (which models regeneration).

## CB-008 (follow-up, predictions committed before its run)

R1 gave only one hit (the unarmed RS stack fled), so regeneration was not
exercised. CB-008 (`cb008.spec`) makes the RS stack armed and aggressive
(5 "RS Gunboats": Laser ×2 + Mole-skin ×2, plan attack enemies) so it
closes and takes fire for several rounds: Q1 vs 4 Laser Destroyers
(2 Tritanium), Q2 vs 10 Laser Frigates. Same predictions: shields 70 per
ship, +35 per round for the stack while above 0, none once at 0; every
hit replays through `combat.py check`.

## Results

- CB-007: shields 70 per ship and Armor Destroyer armor 250, as predicted;
  9 hit records replay. R1 had one hit (the RS stack fled).
- CB-008: 39 hit records replay, 0 mismatches, including +35 per round
  for the stack while its shields were above 0 and none after they reached
  0. CONFIRMED.
