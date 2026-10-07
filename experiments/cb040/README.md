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

## Results

Both streams: all 16 Super Freighters destroyed in seven kill events
(2, 2, 2, 2, 2, 3, 3 ships), and two salvage objects at (1020,1230):

| object | ironium | boranium | germanium | 10 kT steps |
|---|---|---|---|---|
| first | 30000 | 0 | 0 | **3000** |
| second | 6098 | 0 | 50 | 615 |

- **CONFIRMED:** the first object holds exactly 3000 steps; a second
  object is created at the same position; nothing is lost (the totals
  equal the per-event additions below). The first object holds only
  ironium: when the overflowing addition re-adds the existing minerals,
  ironium comes first and fills it, and the germanium goes to the new
  object.
- The totals fit `Σ (k·c/3 + 3000·k) − quarter` per event with a design
  cost of 25 ironium and 13 germanium per Super Freighter at tech 26
  (fitted, not read from the game). My predicted 60/24 cost was wrong;
  the cost is not what this tested.
