# CB-040: salvage past 30000 kT

Round 5 (COMBAT.md "Salvage", deep space: an object holds at most 3000
steps of 10 kT; a mineral that does not fit fills the object to exactly
3000 steps and a new object is created at the same position; BINARY-ONLY).
Two-player Combat Lab base, deep space. Player 1: one fleet of 16 Super
Freighters (3 Long Hump 6; cargo capacity 3000 each) carrying 48000 kT of
ironium. Player 0: 40 Phaser DDs. Pinned at cycles 20000 and 30000.

## Predictions (committed before the run)

- All 16 Super Freighters are destroyed.
- Salvage per kill event: a third of the design cost (ironium 60, germanium
  24 per ship) plus the destroyed share of the cargo, less a quarter. In
  total about 0.75 · (48000 + 16·20) ≈ 36240 kT ironium and about 96 kT
  germanium, which does not fit in one object.
- Two salvage objects at the battle point: the first holds **exactly 3000
  steps**, the second the rest. Nothing is lost to the limit: the two
  together hold the sum of the per-event additions.
