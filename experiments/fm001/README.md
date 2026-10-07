# FM-001 — first fleet-movement batch (predictions, written before the run)

Oracle: Stars! J-RC3 via `docs/ORACLE.md`. Raw evidence: private
`stars-oracle-apparatus`, `evidence/fm001/`.

## Setup

Starting state is synthetic: PG001 (`PG001.HST`, 2407, one player, SS, no
LRTs, tiny universe) with every player-0 fleet replaced by the 75 fleets of
`fm001.spec`, built with `tools/fleetlab`. Each fleet is an isolated scenario
in deep space (except the two planet-target fleets). Player propulsion tech
is set to 7 so the three cloned scout designs (Long Hump 6, Daddy Long Legs 7,
Alpha Drive 8 instead of Quick Jump 5) are within tech. Nothing else changes.
One turn (2407 → 2408) is generated with `scripts/oracle/turn PG001.M1`; the
resulting `.HST`/`.M1` are decoded with `tools/fleetlab dump`.

Pilot (FM-000, same method, prop tech 0): one Quick Jump 5 scout (18 kt,
300 mg) at (1200,1200) ordered to (1300,1200) at warp 5 ended at (1225,1200)
with 297 mg. Fleet 0 of FM-001 replicates it.

Engine fuel tables and part masses used for predictions come from StarsAPI's
`UNEDITED.MOD` (documented, not verified here).

## Questions and competing predictions

`predictions.tsv` lists every fleet with its start, orders, mass, fuel and
the predicted result. Hypotheses:

- **Distance per year.** A fleet with a waypoint farther than warp² ly moves
  warp² ly along the straight line (W, Q, M, E groups).
- **Partial-move rounding (Q, D, P).** The end point is the exact point
  rounded by (a) truncation toward zero, (b) floor, or (c) round-half-up of
  each coordinate. Q fleets point into all four quadrants so the three differ.
- **Arrival test (D).** A fleet arrives iff the exact distance ≤ warp²
  (prediction), versus a test on a rounded distance. (+25,+1) (25.02 ly) and
  (+24,+8) (25.30 ly) separate them; (+24,+7) and (+20,+15) are exactly 25.
- **Fuel (W, F, M, E).** Working hypothesis, fitted only to the pilot:
  `ceil(mass × table[warp] × distance / 20000)`, distance = distance moved.
  Alternatives the batch separates: floor/round instead of ceil (F steps at
  11/12 and 22/23 ly), per-ship rounding instead of per-fleet (M: 2–7
  scouts), cargo excluded from mass (M: freighter 0/1/35/70 kt), whole warp²
  charged on arrival instead of the distance moved (F).
- **Insufficient fuel (N).** Candidates: no movement; full movement anyway;
  movement shortened to what the fuel pays for at the ordered warp; movement
  at the engine's free speed (warp 1 for Quick Jump 5).
- **Waypoint chaining (C).** After reaching waypoint 1 with movement left
  over, the fleet either stops there for the year (prediction) or continues
  toward waypoint 2 with the remainder (and, for C5, at waypoint 1's or
  waypoint 2's warp). C3 has a zero-length first leg.
- **Planet target (P).** A fleet in range ends at the planet's coordinates
  and orbits it (position object = planet); out of range it stops on the line
  as in Q.
- **Ordering (O).** Chase pairs, fleet targets at warp 9:
  - a (low id) chases b, which moves +25x: chaser reaches b's *start*
    (1320,1300) if targets are read before b moves or fleets move in id
    order; reaches b's new position (1345,1300) if targets are updated first.
  - d (high id) chases c (low id), which moves +25x: id-order movement gives
    d at c's new position (1315,1316); simultaneous movement on start
    positions gives (1290,1316).
  - e/f (warp 4, 20 ly apart) and g/h (warp 3, 16 ly apart) chase each
    other. Simultaneous on start positions: e→(1216,1380), f→(1204,1380);
    g→(1279,1385), h→(1277,1385). Id order: e→(1216,1380), f→(1216,1380);
    g→(1279,1385), h→(1279,1385).

RNG: `_MoveFleets` draws random numbers only for cheater-flagged players and
for one LRT (white-box, private decomp); this race has no LRT and has not been
flagged, so nothing here is expected to depend on the RNG.
