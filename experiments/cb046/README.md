# CB-046: Mystery Trader items from battle

Round 6. COMBAT.md (#38) "Tech from battle": a successful attempt
(`rand(100) ≥ 50`) first makes up to 13 tries `rand(13)` for a Mystery
Trader part; the part is given if it appeared among the destroyed ships
with a per-part chance `c`, the player lacks it, and `rand(100) < c`. A
success ends the attempt. The chances `c` are not published.

Two-player Combat Lab base, deep space. Player 0 has every field at 26 (so
no field can gain) and owns no Mystery Trader items (`mt 0 0`); its Phaser
Destroyers destroy all of player 1's ships, so only player 0 attempts.
Pinned at the twelve cycle counts 5000 … 50000 plus 6000, 7000, 9000 and
14000 (streams counted by battle record).

- `cb046`: player 1 has 6 Destroyers, each with two Anti Matter Torpedoes.
- `cb046-morph`: player 1 has 3 Mini Morphs with Enigma Pulsar engines,
  Multi Cargo Pods, a Multi Function Pod, a Mega Poly Shell and a Langston
  Shell (six Mystery Trader items with the hull).

## Predictions (committed before the run)

- Player 0's tech is unchanged in every stream.
- Player 0's Mystery Trader mask gains at most one bit per stream, and in
  at most about half of the streams (the 50% gate).
- Any bit gained is one of the parts on the destroyed ships: in `cb046`
  always the same bit (the Anti Matter Torpedo's).
- Player 1 has nothing left and gains nothing.
