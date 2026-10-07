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

## `cb046-morph` setup change (committed before its rerun)

In the first `cb046-morph` runs the unarmed Mini Morphs (battle speed 7)
left the board in round 3 without being hit, so nothing was destroyed.
The Morphs now carry two Lasers in their last free slot (armed, so they
close in) and player 0 has 80 Phaser Destroyers. Predictions unchanged.

## Results of `cb046` and `cb046-morph`, and a control (committed before the control's run)

No Mystery Trader item was gained: player 0's mask stayed 0000 and its
tech stayed 26 in all 12 distinct streams of `cb046` (all six Anti Matter
Torpedo Destroyers destroyed each time) and all 12 of the armed
`cb046-morph` (all three Morphs destroyed). Player 1 kept nothing.

Control `cb046-bio`: `cb046` with player 0's biotechnology at 3 (the
torpedo requires 21), to show whether player 0 makes attempts at all.
Prediction: player 0 gains biotechnology (to 4) in some streams (about a
third), and still no Mystery Trader item.

### Control result

`cb046-bio` ran the same 12 battle streams as `cb046` (identical battle
records). Player 0 gained biotechnology 3 → 4 in 2 of 12 streams (12000
and 50000) and no Mystery Trader item in any. So player 0 does make
attempts, and in at least those two streams an attempt passed the 50%
gate with Anti Matter Torpedoes among the destroyed ships; in `cb046` the
same streams gave no Mystery Trader item. **MISSED** (no gain anywhere,
24 + 12 streams): either the per-part chance is 0 for these parts, or
parts on destroyed ships are not what makes a part eligible. Open for the
Combat decomp pass.
