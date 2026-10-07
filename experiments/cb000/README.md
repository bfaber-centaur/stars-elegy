# CB-000: ship designer "Initiative / Moves"

Question: does the ship designer's "Initiative / Moves" line match the
battle-speed and initiative rule that the private stars-decomp combat reading
derives from the binary? The designer uses the same rule as battle setup,
without the battle-only terms (war-monger bonus, cargo, jitter), so this
checks the rule with no battle.

Universe: "Combat Lab" (CB), a new 2-player game (two Humanoid players,
tiny, sparse, no random events) made with the Advanced New Game wizard;
see `docs/ORACLE.md`, "Combat Lab". `cb000.spec` replaces both players'
ship designs with the 32 designs below (CombatLab, `tools/fleetlab`), sets
every tech field to 26, and leaves one scout per player. One host turn
2400 → 2401, then each design is opened in the designer of the player's
`.M` file.

`predictions.tsv` (committed before the turn): designer initiative and
moves per design, from the stars-decomp rule (`tools/combat.py`, branch
`claude/project-thread-9j7tt8` at 8cad60f). Moves are squares per round
(code 0..8 → ½ … 2½). The rule as stated publicly:

- initiative = hull initiative + 1 per Battle Computer, 2 per Battle Super
  Computer, 3 per Battle Nexus (capped at 63);
- speed code = w − 4 + maneuvering jets + 2·overthrusters
  + (Enigma Pulsars + 1)/2 − (mass/70)/(engines), clamped 0..8, where
  w = 10 for Interspace-10, Enigma Pulsar, Trans-Star 10,
  Trans-Galactic Mizer Scoop and Galaxy Scoop, otherwise the highest warp
  ≤ 9 whose fuel-table entry is at most 120 (integer divisions);
- moves per round = (code + 2)/4.

## Result

All 32 designs showed the predicted mass, initiative and moves in the
designer (`results.tsv`; screenshots in the apparatus repository,
`evidence/cb/cb000/`). CONFIRMED.
