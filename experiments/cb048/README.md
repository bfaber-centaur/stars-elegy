# CB-048: Mystery Trader items from battle, kill events (round 7, MT-A)

`experiments/cb042/gen.py` writes the specs. The setup is the CB-046
armed-Morph setup, changed in one way. Player 1's 30 Mini Morphs each
carry five Mystery Trader part types: Enigma Pulsar ×2, Multi Cargo Pod
×3, Multi Function Pod, Mega Poly Shell and Langston Shell, plus Laser
×2. In CB-048 they are 30 one-ship fleets. Player 0 has 80 Phaser
Destroyers, tech 26 and no Mystery Trader items (`mt 0 0`). The battle
is in deep space. In `cb048-ctl` all 30 Morphs are in one fleet.

## Prediction (stars-decomp #28, MT-A; committed before the runs)

The reconciled rule, as given in the stars-elegy round-6 reconciliation:
- each time a hit destroys ships of a design, each Mystery Trader part
  type on that design gains chance equal to the number of those parts
  in its slot;
- the chance is capped at 25, and hulls never count.

With one-ship fleets every kill is its own kill event:
- all five part types reach 25;
- the per-stream chance of an item is about 0.36;
- each gain is one item per stream, always one of Multi Cargo Pod, Multi
  Function Pod, Langston Shell, Mega Poly Shell or Enigma Pulsar.

The control has three kill events or fewer, so it should gain far less
often.

Rates are counted over distinct streams, identified by battle-record
hash: 24 cycle settings for CB-048 and 12 for the control. The decomp's
`battlesim.py` replays each record to name the streams that should gain.

## Results

(pending)
