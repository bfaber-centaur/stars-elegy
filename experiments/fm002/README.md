# FM-002 — fleet-movement follow-up (predictions, written before the run)

Same method as FM-001 (`../fm001/README.md`): PG001 2407 with every
player-0 fleet replaced by the 46 fleets of `fm002.spec`, prop tech 7, one
turn. Generator: `gen.py` (shared helpers `../fmlib.py`). Raw evidence:
private `stars-oracle-apparatus`, `evidence/fm002/`.

## What FM-001 left open, and the predictions

Every FM-001 fuel value fits `fuel = floor((Σ mass·table[warp]·distance + C) / 20000)`
with one fleet-wide rounding and 17120 ≤ C < 18200 (`docs/PARITY.md`, FM-001).
That is a fit to one batch, not an established rule. Tests here:

- **K — the constant.** Ten warp-5 arrivals whose `m·e·d mod 20000` is
  1800…2800. Each fleet's fuel use jumps by one exactly when
  C ≥ 20000 − r, so the batch brackets C to 100. A C = 18000 rule (e.g.
  integer tenths of a mg, rounded up) predicts the jump between r = 1900
  and r = 2000.
- **FD — non-integer distance.** Diagonal arrivals (d = 2.83 … 7.07 ly)
  whose fuel differs if the game uses the exact distance, the distance
  truncated to an integer (FD 10–12), or rounded up (FD 13–15).
  Prediction: exact distance.
- **A — arrival just beyond warp².** FM-001 fleets arrived at 25.02 and
  25.30 ly at warp 5. Three rules, each prediction in `predictions.tsv`:
  (i) arrives when the rounded end point equals the target; (ii) arrives
  when less than 1 ly would remain; (iii) arrives when d ≤ warp² + 0.5.
  A16/A21 (25.61 ly) separate (iii) from (i)/(ii); A17 (25.71) and A20
  (25.96) separate (i) from (ii); A19 (26.02) stops under all three.
- **N — fuel-limited movement.** FM-001 fits "distance = floor(fuel·20000 /
  (m·e))" for a fleet that cannot pay for warp²: N25/N26 move diagonally,
  where truncating the distance before placing the fleet (prediction)
  differs from placing it at the exact limit and rounding the position.
  N24 has exactly the FM-001 cost of 36 ly (expect the full move). N27/N28
  have no fuel at warp 1 (table 0) and warp 2 (cost rounds to 0 under the
  fuel rule): either they move warp² ly or, like FM-001's fuel-0 fleet, not
  at all. N29 can pay for its 5 ly arrival. N30 is a 5-scout fleet.
- **X — mixed fleets, warp 7.** X32 (3 QJ5 scouts + 1 AD8 scout): per-design
  rounding gives 75, one fleet-wide rounding 74. X34 carries 70 kt in a QJ5
  freighter + AD8 scout fleet: cargo charged at the freighter's engine gives
  132, at the scout's 63, other splits in between.
- **O — chasing (fleet targets).** FM-001: a chaser reached its target's
  end-of-move position whatever the fleet ids, and two fleets chasing each
  other at equal speed met at the midpoint.
  - C1 (low id) / C2 (high id) chase a target that moves 81 ly
    perpendicular to the line between them. Aiming at the target's final
    position: C1 → (1353,1171), C2 → (1117,1321). Aiming at its start:
    (1365,1150) and (1105,1300). Pursuit integrated in small time steps
    gives a third point (not computed).
  - E (warp 4) and F (warp 3) chase each other from 20 ly apart: midpoint
    1160; meeting where distances are proportional to speed 16:9 → 1163;
    each aiming at the other's start: E 1166, F 1161.
  - T3 heads toward C3 (40 ly apart, both warp 5; T3's own target is 5 ly
    short of C3). Aiming at the final position: C3 meets T3 at 1055.
    Closing in time steps they meet at 1060; C3 then either stays there or
    stays with T3 (1055).
  - A chases B chases Z (Z moves +25x to 1250): B ends at 1250 under every
    rule but "aim at the start"; A ends at 1250 if targets resolve
    transitively.

RNG: as FM-001, nothing here is expected to draw random numbers.
