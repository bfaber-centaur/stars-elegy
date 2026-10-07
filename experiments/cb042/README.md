# CB-042: token cap with three players (CAP-A)

Round 6. `gen.py` here writes every round-6 spec (CB-042..CB-047).
Predictions from the Combat decomp pass (stars-decomp #22,
`docs/combat-predictions.md` "Round 6", `tools/tokencap.py round6`),
reconciled in COMBAT.md (#38): each player first gets `255 / n` stacks,
taking fleets from the end of the fleet list backwards apart from the
fleet whose location this is; a starbase counts toward the 255 but not
toward a quota; a second pass adds left-out fleets while they fit,
skipping one that does not fit.

Three-player game CB3P (`evidence/cb4/base3p`), all tech 26, mutual
enemies, 100 one-ship Laser Frigate fleets per player at (1060,1080).
Pinned at cycles 20000 and 30000.

## Predictions (committed before the run)

- 255 tokens: 85 per player.
- Left out: player 0's fleets 1..15, player 1's 0..14, player 2's 0..14.
  No second pass (the first fills 255).

## Results

Both streams: **255 tokens, 85 / 85 / 85**. Left out (fleets that
survived without taking part): player 0's 1..15, player 1's 0..14, player
2's 0..14. **CONFIRMED.** The checker replayed 645 + 700 hits with one
mismatch in each stream, both a beam's carried damage onto a second
token of the same player after a kill (reported to the Combat decomp
pass; the cap is not affected).
