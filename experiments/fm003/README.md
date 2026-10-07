# FM-003 — chases, fuel at free speed (predictions, written before the run)

Same method as FM-001/FM-002: PG001 2407, every player-0 fleet replaced by
the 48 fleets of `fm003.spec`, prop tech 7, one turn. Generator `gen.py`.
Raw evidence: private `stars-oracle-apparatus`, `evidence/fm003/`.

## Questions and predictions

- **CH — chains of fleet targets.** A chases B, B chases Z (warp 9), Z moves
  +60x at warp 5 (A, B, Z start at x = 1200, 1215, 1225). FM-002 ran the id
  order A < B < Z once: B did not move at all, A arrived at B's start, Z
  moved 25. Run in all six id orders, plus a variant where Z has no orders.
  Candidate rules:
  - M1, one level of look-ahead: a chaser first moves its target if that
    target has not moved yet, but a target moved this way does not look
    further; if its own target has not moved yet it stays put for the year.
    Predicts ABZ and AZB: A 1215, B 1215, Z 1250; BAZ, BZA, ZAB, ZBA: all
    three at 1250.
  - M2, full look-ahead (targets resolved transitively): all at 1250 in
    every order. Already contradicted by FM-002's ABZ.
  - S (Z without orders): under M1, B either stays (Z counts as not yet
    moved) with A at 1215, or arrives at Z (1225) with A following.
- **MU — fleets chasing each other.** FM-001/002 gave (low id, high id)
  distances moved: warp 4/4 from 20 ly: 12/8; warp 3/3 from 16 ly: 8/8;
  warp 4/3 from 20 ly: 14/6. Three step models fit all three (simulate the
  year in N sub-steps, low id first, each fleet moving a fixed step toward
  the other's current position and stopping on reaching it): N = 4 with step
  trunc(warp²/4); N = 4 with step round(warp²/4) (identical for every warp,
  since warp² mod 4 is 0 or 1); N = 5 with step ceil(warp²/5). An exact
  4-step version (step warp²/4) does not fit them. Per-fleet predictions are
  in `predictions.tsv`; the warp-1 pair (6 ly apart, trunc model: neither
  moves) and the pairs too far apart to meet (warp 3 at 40 ly: 8 vs 10 vs 9;
  warp 5 at 60 ly: 24 vs 25) separate the models. MU-D repeats warp 4/4 on a
  diagonal (12,16) to see how sub-step positions are rounded.
- **FG — fuel at free speed.** FM-002: a Quick Jump 5 scout with no fuel at
  warp 1 moved 1 ly and ended with 1 mg (message 243); one at warp 2 with no
  fuel did not move (message 139). Candidates: (a) +1 mg only when the tank
  was empty; (b) a fixed gain per year at warp 1 whenever the tank is not
  full; (c) a gain for any fleet that does not burn fuel, moving or not;
  (d) a gain scaled by ship count or design. FG covers non-empty tanks,
  stationary fleets, warp 2 (cost rounds to 0), another engine, another
  hull, 5 ships, and a tank 1 mg short of full.
- **FA — distance charged on arrival beyond warp².** FM-002 showed fuel is
  charged on ceil(distance) for arrivals within warp². For arrivals at 25.96
  and 25.30 ly at warp 5 (100.97 kt fleet): ceil(d) = 26 gives 14 mg,
  capping at warp² gives 13. 25.00 ly is the control (13).
- **K — fuel constant.** FM-002 put C in [18000, 18100). m·e·d = 21960 at
  warp 6: 1 mg if C < 18040 (the "truncate to tenths of a mg, then round
  up" reading, C = 18000), 2 otherwise.

RNG: as before, nothing here is expected to draw random numbers.
