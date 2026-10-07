# Stars! J-RC3 Parity Notes

## Population Growth

Status: DOCUMENTED / PARTIALLY MEASURED

### Confirmed behavior

For a planet with positive habitability:

- racial maximum growth rate is specified as a percentage per year;
- at 100% habitability, population may grow at the race's full growth rate;
- lower positive habitability scales the growth rate proportionally;
- growth begins to slow after the planet reaches 25% of its population capacity;
- population capacity is based on habitability.

For negative habitability:

- population dies each year;
- annual death percentage is `abs(habitability) / 10`.

### Measured behavior — uncrowded positive growth

#### PG-001 — growth carry

Ruleset: J-RC3

Scenario:

- ordinary race;
- 10% racial growth rate;
- 100% habitability;
- 1,000,000 population capacity;
- population below 25% capacity for the measured uncrowded interval.

Observed population, in units of 100 colonists:

| Year | Population |
|---:|---:|
| 2400 | 250 |
| 2401 | 275 |
| 2402 | 302 |
| 2403 | 332 |
| 2404 | 365 |
| 2405 | 402 |
| 2406 | 442 |
| 2407 | 486 |
| 2408 | 535 |
| 2409 | 588 |
| 2410 | 647 |
| 2411 | 712 |
| 2412 | 783 |
| 2413 | 861 |
| 2414 | 948 |
| 2415 | 1042 |
| 2416 | 1147 |
| 2417 | 1261 |
| 2418 | 1387 |
| 2419 | 1526 |
| 2420 | 1679 |
| 2421 | 1847 |
| 2422 | 2031 |
| 2423 | 2234 |
| 2424 | 2458 |
| 2425 | 2704 |

The complete uncrowded sequence above is reproduced exactly by carrying the
fractional remainder of growth forward between turns.

For the measured 100%-habitability, 10%-growth case, an equivalent integer
calculation is:

```go
numerator := populationHundreds*growthPercent + growthCarry
growthHundreds := numerator / 100
growthCarry = numerator % 100
populationHundreds += growthHundreds
```

For example:

```text
250 * 10 +  0 = 2500 -> +25, carry  0 -> 275
275 * 10 +  0 = 2750 -> +27, carry 50 -> 302
302 * 10 + 50 = 3070 -> +30, carry 70 -> 332
332 * 10 + 70 = 3390 -> +33, carry 90 -> 365
365 * 10 + 90 = 3740 -> +37, carry 40 -> 402
```

This explains the apparent rounding anomaly at `36,500 -> 40,200`: the
previous turns have accumulated a fractional growth remainder.

At `245,800 -> 270,400`, the accumulator returns to zero. This gives a clean
starting condition for measuring the post-25%-capacity crowding curve.

#### Binary confirmation from `.HST`

Eight consecutive PG-001 host files were decoded for years 2400-2407. The
planet record stores population in hundreds of colonists and contains a
separate one-byte field named `excessPop` by StarsAPI. The decoded values were:

| Year | Population units | Display population | `excessPop` | Carry predicted from prior turn |
|---:|---:|---:|---:|---:|
| 2400 | 250 | 25,000 | 0 | 0 |
| 2401 | 275 | 27,500 | 0 | 0 |
| 2402 | 302 | 30,200 | 50 | 50 |
| 2403 | 332 | 33,200 | 70 | 70 |
| 2404 | 365 | 36,500 | 90 | 90 |
| 2405 | 402 | 40,200 | 40 | 40 |
| 2406 | 442 | 44,200 | 60 | 60 |
| 2407 | 486 | 48,600 | 80 | 80 |

The stored `excessPop` value matches the independently inferred growth carry
for all eight snapshots. This is direct binary evidence that J-RC3 maintains a
separate persistent remainder associated with population growth, rather than
merely rounding each year's displayed population independently.

For this measured case, the on-disk state is therefore behaviorally equivalent
to:

```go
type PopulationState struct {
    Hundreds int
    Carry    int // stored as excessPop; observed range here 0..99
}
```

`excessPop` should not be interpreted as ordinary hidden colonists added to the
planet's displayed population. Its observed evolution matches a remainder from
the growth calculation.

Interpretation:

- population is stored in units of 100 colonists in the measured `.HST`
  records;
- simple per-turn rounding or truncation does **not** explain the sequence;
- a persistent fractional growth accumulator explains every measured
  uncrowded transition exactly;
- the `.HST` `excessPop` byte matches that inferred accumulator exactly across
  eight consecutive turns;
- the population/carry representation is therefore binary-confirmed for this
  uncrowded 100%-habitability, 10%-growth scenario.

Supporting observation: an earlier run under the registration/copy-protection
penalty, which halved effective growth to 5%, also matches the same carry model
exactly. After serial validation restored 10% growth, preserving the existing
carry predicts both observed transitions `35,100 -> 38,600 -> 42,500`. This
suggests that the carry persists when the effective growth rate changes, though
that behavior should be retested under a normal gameplay modifier before being
treated as a general rule.

### Maximum population

For an ordinary race on a 100% world:

    1,000,000

Known modifiers:

- Hyper-Expansion: 500,000
- Jack-of-All-Trades: 1,200,000
- Only Basic Remote Mining: +10% capacity

Positive worlds below 5% habitability are treated as 5% for
population-capacity purposes.

### Unknown / needs measurement

- Exact growth formula above 25% capacity. Eleven consecutive turns are
  measured (PG-002 and PG-003: 27.04% to 51.90%). They reject H0, H1 and H2
  as stated, and identify nothing. Observed growth sits 0–4 units below
  truncated 16/9 × (1 − x)².
- `excessPop` across the crowded turns. It has not yet been extracted from
  the preserved PG-002/PG-003 `.HST` files (apparatus `evidence/pg002/`,
  `evidence/pg003/`). PG-001 showed this byte tracking the growth carry
  exactly in the uncrowded case (same decoder: StarsAPI `PartialPlanetBlock`,
  see "Binary confirmation from `.HST`"). Whether it means the same thing
  under crowding is open, but it is an existing observable, not an
  inaccessible quantity.
- Exact handling of `excessPop` / growth carry when habitability or crowding
  introduces additional fractional modifiers.
- Whether growth carry persists across ordinary gameplay changes to effective
  growth rate.
- Exact order of operations between:
  - habitability modifier
  - racial growth rate
  - crowding modifier
  - growth carry / integer truncation
- Exact behavior at 100% capacity.
- Exact overcrowding death curve between 100% and 400%.
- Lifecycle of `excessPop` across migration, colonization, ownership changes,
  hostile-world deaths, and other population-changing mechanics.

### Measured behavior — PG-002, first crowded turn

Status: MEASURED (one turn, one planet, read from the UI). Run on
2026-10-06 with the cloud oracle (`docs/ORACLE.md`).

Question: what does one turn of growth do just above 25% capacity?

Starting state, observed: PG001 at 2425, Endeavor population 270,400
(27.04% of 1,000,000), read in the Stars! UI after advancing the registered
base from 2407 by 18 empty-order turns (`turn PG001.M1`, oracle restarted
between turns). The 2408 reading on this base was 53,500, matching PG-001.
The carry at 2425 is *inferred* to be 0 from the PG-001 carry model.
`excessPop` has not been extracted from the preserved 2425 `.HST` to check
it. Elegy has no native body decoder, but the StarsAPI decoder used for the
PG-001 binary confirmation exposes this byte.

Predictions, written before the run (10% growth, 100% habitability, carry 0,
factor applied to the uncrowded growth before truncation):

| Hypothesis | Factor at 27.04% | Predicted 2426 |
|---|---:|---:|
| H0: no slowdown yet (uncrowded rule continues) | 1.000 | 297,400 |
| H1: quadratic, 16/9 × (1 − x)² (recalled community formula; unverified) | 0.946 | 295,900 |
| H2: linear, (1 − x) / 0.75 | 0.973 | 296,700 |

Observation (UI, Endeavor Status panel and Summary, one run from the
`pg001-2425` snapshot):

| Year | Population | Units of 100 |
|---:|---:|---:|
| 2425 | 270,400 | 2704 |
| 2426 | **295,800** | 2958 |

Growth was 25,400 (254 units). The uncrowded rule would give 270.4 → 270.

Result:

- H0 is rejected: growth slowed in the first turn above 25% capacity.
- H1 and H2, as stated above, are both rejected. H2 misses by 900 colonists.
  H1 misses by 100 colonists (one unit): it predicts 255.89 → 255 units,
  the observation is 254.
- This is one data point. It does not identify a formula, and nothing has
  been tested about whether H1 with a different carry, rounding, or order
  of operations would fit. Those are open questions, not conclusions.

Context of the run, observed:

- Orders were empty (no production queue). The year's messages were the
  empty production queue and an Energy tech level 7 breakthrough with two
  benefits (Shadow Shield, Energy Capacitor). No other population-related
  message was shown.
- Mines and factories stayed at 10 operable; nothing was built.

Evidence: the `.HST` for every year 2407–2426 of this run, the recorder's
`observations.jsonl`, the UI screenshots and a SHA-256 manifest are in the
private `bfaber-centaur/stars-oracle-apparatus` repository, under
`evidence/pg002/`. They are kept out of this repository because the files were
produced by a registered copy and the repository is public. SHA-256:

| Year | `PG001.HST` SHA-256 | Header (turn / flags) |
|---:|---|---|
| 2425 | `e4bf2e0e38250769d6d394391d540fe2d4833a672428d077fa13bf5f2ddae0fc` | 25 / `0xa0` |
| 2426 | `150172b721c8e83676e125ce73bfecf318a9dde5410afd384fe569a2b8303201` | 26 / `0xa0` |

Limits: one turn, one planet, one run. The UI shows population in units of
100 and does not show the carry. The experiment assumes nothing besides
growth changed population.

### Measured behavior — PG-003, crowded turns 2427–2436

Status: MEASURED (ten consecutive turns, one planet, one run, read from the
UI). Run on 2026-10-06 with the cloud oracle (`docs/ORACLE.md`).

Question: how does growth proceed over ten more empty-order turns of PG001
past 2426, and does PG-002's 2426 value (295,800) repeat on a fresh run?

Procedure: from the `registered` snapshot (PG001 2407), 19 × `turn PG001.M1`
to 2426 (oracle restarted between turns) while `stars-record` archived every
`.HST`. Then, for each year 2426–2436, Stars! was restarted, PG001 opened and
Endeavor's population read from the Status panel and the Summary (they agreed
every year), and the next turn was run with `turn PG001.M1`. No orders were
given.

Predictions, written and committed before the run (commit `5472daa`):
multi-step trajectories from the PG-002 observation (2958 units at 2426),
10% growth, 100% habitability, growth truncated to whole units each year,
carry ignored (`excessPop` at 2426 had not been extracted). H1 and H2 are the PG-002
hypotheses; both were already rejected by the single PG-002 point and were
listed only as reference curves.

| Year | H1 16/9 × (1 − x)² | H2 (1 − x) / 0.75 |
|---:|---:|---:|
| 2427 | 3218 | 3235 |
| 2428 | 3481 | 3526 |
| 2429 | 3743 | 3830 |
| 2430 | 4003 | 4145 |
| 2431 | 4258 | 4468 |
| 2432 | 4507 | 4797 |
| 2433 | 4748 | 5129 |
| 2434 | 4980 | 5462 |
| 2435 | 5203 | 5792 |
| 2436 | 5415 | 6116 |

Observation (UI, Endeavor; units of 100 colonists). "x" is the start-of-year
population over capacity (10,000 units). The H1 and H2 columns are
*one-step* values computed afterwards from the observed previous year
(10% × factor × previous population, before truncation), not predictions.

| Year | Population | Units | Growth | x at start | Growth / uncrowded | H1 one-step | H2 one-step |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2426 | 295,800 | 2958 | 254 | 27.04% | 0.9393 | 255.89 | 263.05 |
| 2427 | 321,800 | 3218 | 260 | 29.58% | 0.8790 | 260.78 | 277.74 |
| 2428 | 347,900 | 3479 | 261 | 32.18% | 0.8111 | 263.14 | 290.99 |
| 2429 | 374,000 | 3740 | 261 | 34.79% | 0.7502 | 263.00 | 302.49 |
| 2430 | 399,800 | 3998 | 258 | 37.40% | 0.6898 | 260.55 | 312.17 |
| 2431 | 425,300 | 4253 | 255 | 39.98% | 0.6378 | 256.04 | 319.95 |
| 2432 | 450,000 | 4500 | 247 | 42.53% | 0.5808 | 249.72 | 325.89 |
| 2433 | 473,900 | 4739 | 239 | 45.00% | 0.5311 | 242.00 | 330.00 |
| 2434 | 497,100 | 4971 | 232 | 47.39% | 0.4896 | 233.19 | 332.43 |
| 2435 | 519,000 | 5190 | 219 | 49.71% | 0.4406 | 223.50 | 333.32 |
| 2436 | 540,200 | 5402 | 212 | 51.90% | 0.4085 | 213.47 | 332.85 |

The 2426 row repeats PG-002. This run did not read 2425; its growth and
x use PG-002's 2425 reading (2704 units).

Result:

- PG-002 repeated: 2426 read 295,800 on a second, independent run from the
  registered base.
- H2 as stated is rejected at every point; it overshoots by 9 to 121 units
  per year.
- H1 as stated (truncating the one-step value) is rejected at 10 of 11
  points. It matches only 2427 (260). At every point the observed growth is
  at or below the truncated H1 value, by 0 to 4 units (2435: 223 vs 219).
  The shortfall does not grow steadily with x.
- The multi-step H1 trajectory matched 2427 and then fell behind the
  prediction, ending 13 units below at 2436 (5402 vs 5415).
- Interpretation, not established: growth tracks a quadratic-like slowdown
  closely but not exactly. Carry, rounding of the factor, or the order of
  operations could each account for a shortfall of a few units; none of
  these has been tested, and no formula is inferred here.
- Next observable, before any further oracle turns: `excessPop` for
  2407–2436 from the preserved PG-003 `.HST` files, decoded with the same
  StarsAPI decoder used for PG-001. PG-001 established a persistent sub-unit
  growth accumulator, and the shortfall here is a few units, so the carry
  is the first column to add. It may not explain the shortfall.

Context of the run, observed:

- Messages shown: 2427–2430 and 2432–2435 had one message each (the empty
  production queue). 2431 had two and 2436 had three; only 2436's were read:
  the empty production queue, Energy tech level 9, and a Mass Driver 7
  benefit. No population-related message was seen in 2436. 2431's second
  message was not read.
- Mines and factories stayed at 10 operable every year.
- `.HST` header flags after each turn varied (`0x20`, `0xa0`, `0x60`,
  `0x80`, `0x00`); not investigated.

Evidence: the `.HST` for every year 2407–2436 of this run, the recorder's
`observations.jsonl`, the UI screenshots for 2426–2436, the 2436 messages
and a SHA-256 manifest are in the private `bfaber-centaur/stars-oracle-apparatus`
repository, under `evidence/pg003/`. SHA-256 of `PG001.HST`:

| Year | `PG001.HST` SHA-256 |
|---:|---|
| 2425 | `77708e98779956b1987f7e4ab50b985adf30b26a1d775e4047d4b6b9d41512b4` |
| 2426 | `3b06aa39a905fadb6f6f1a22de89342434a4fb367b4319dd1554b319f3d4ef98` |
| 2427 | `616adbed4cc0adb928245224b0ce5e5d110b46c16179dc8d9e529a2c65dd2932` |
| 2428 | `f17036e80aa74d83302d12ad77d98162fac1db7a2988897620da3eeb3870797a` |
| 2429 | `87b93f79b6979d31dbe96947b411dd3b565cbf332cf41728fbe22819706b2881` |
| 2430 | `7590d3f3f2b4b3ad58bd8e3ccef8ebd15701a8fb856999f6758ae42ff2681e9b` |
| 2431 | `f19299224102cd65eacf31211e3f94e455e84a8c16aafa1e7abfbde2d694339a` |
| 2432 | `18b9e8785d73c2bf4168e3f3cab6ffe07e8676878cd0ac24f088c9d612940f27` |
| 2433 | `4b8caa728f6fad66175784568ac8795984eaa11c0f7ca0bb6ec8dc6ce29f787b` |
| 2434 | `03daf0e3c11c946045e5e4ecbb959e5a41600aae1b53d88b5f3e876ef490e3c5` |
| 2435 | `eec07f3a3dc3ec5af0a196363dcaec822c4ad7400b241659748d3d27c23b54d0` |
| 2436 | `aaf616d1ea0cb14a5fe848ed289ecb73bddf28dfce0366f8fcf4ff8fa667d97d` |

These differ from PG-002's files for the same years; output bytes differ
between runs (`docs/ORACLE.md`, "One PG001 turn").

Limits: one planet, one run past 2426, one race and habitability. The UI
shows population in units of 100 and does not show the carry; `excessPop`
in the preserved files has not been extracted yet. The
experiment assumes nothing besides growth changed population.

### Sources

- Stars! User Manual, Population / Growth Rate / Maximum Population /
  Overcrowding / Killer Planets sections.
- J-RC3 oracle measurements, PG-001.
- Eight consecutive PG-001 `.HST` snapshots, years 2400-2407.
- PG-002, 2026-10-06: PG001 2425 → 2426 from a freshly registered base
  (see "Measured behavior — PG-002" above).
- PG-003, 2026-10-06: PG001 2426 → 2436, second run (see "Measured
  behavior — PG-003" above).
- Cloud oracle re-measurement, 2026-10-06 (`docs/ORACLE.md`): PG001 2407 →
  2408 was generated twice (once by hand, once scripted), both times from
  the same snapshot taken after the serial was accepted. Endeavor's
  population, read in the Stars! UI, went 48,600 → 53,500 both times. That
  matches the 2408 value above, not the 51,100 predicted under the
  halved-growth penalty.
- StarsAPI `PartialPlanetBlock`, which decodes population separately from the
  installation byte it names `excessPop`:
  <https://github.com/stars-4x/starsapi/blob/master/src/main/java/org/starsautohost/starsapi/block/PartialPlanetBlock.java>

### Tests

Planned:

- unit fixture reproducing PG-001 exactly;
- binary fixture asserting the decoded PG-001 population / `excessPop` sequence;
- differential fixture for the clean 10% / 100%-habitability run;
- follow-up tests varying growth rate and habitability to determine how the
  accumulator interacts with other modifiers.

## Fleet Movement

Status: MEASURED (three one-turn oracle batches, FM-001 to FM-003, plus the
FM-000 pilot; 169 fleets). Run on 2026-10-07 with the cloud oracle.

### Method

The starting states are synthetic. `tools/fleetlab` (StarsAPI, pinned)
rewrites PG001's 2407 `.HST`: every player-0 fleet is replaced by fleets with
chosen position, ships, cargo, fuel and waypoints, three scout designs with
other engines are cloned from the Quick Jump 5 scout, and propulsion tech is
set to 7 so those engines are within tech. Stars! loaded the edited files and
generated 2407 → 2408 with no visible complaint. One `turn PG001.M1` per
batch; the 2408 `.HST`/`.M1` are decoded with `fleetlab dump`.

- Race: PG001's (SS, no LRTs). Universe: tiny, one player. All test fleets
  sit in deep space away from the homeworld (two target planets).
- Positions, fuel and waypoints come from the decoded files; event ids
  from the `.M1` (block type 12). Texts read in the UI: 78 "… has completed
  its assigned orders."; 139 "… has run out of fuel. The fleet's speed has
  been decreased to Warp 1."; 243 "…'s ram scoops have produced N mg of fuel
  from interstellar hydrogen."
- Engine fuel tables and part masses used below are StarsAPI's
  (`UNEDITED.MOD`): DOCUMENTED, not read from the binary. Quick Jump 5,
  warp 1–10: 0, 25, 100, 100, 100, 180, 500, 800, 900, 1080.
- FM-001 was run twice from the same file; decoded fleets and events were
  identical. FM-002 and FM-003 were run once. Restarted oracle runs reuse
  nearly the same RNG draws, so the repeat shows reproducibility, not
  independence. No movement here is expected to use the RNG (no LRT, no
  cheater flag).
- FM-000's scout (prop tech 0) and FM-001 fleet 0 (prop tech 7) ended
  identically: (1225,1200), 3 mg.

Predictions were committed before each run (`experiments/fm00N/README.md`
and `predictions.tsv`, commits `90037e5`, `4a56c40`, `bc0ed91`). Observed
values per fleet: `experiments/fm00N/results.tsv`. Raw files, dumps and
message screenshots: private `stars-oracle-apparatus`, `evidence/fm000/` to
`evidence/fm003/`.

### Ordinary waypoints (deep space or planet)

`experiments/fmcheck.py` reproduces position and fuel for all 115 fleets
with ordinary waypoints using the rules below. Several details (the rounding
constant, the arrival test, the charged distance, the empty-tank case) were
chosen after seeing earlier batches; FM-002/003 then tested them with
discriminating cases. They describe this corpus, not a binary reading.

- **Distance (MEASURED).** A fleet that does not arrive moves warp² ly along
  the straight line to its waypoint (warp 1–10 on Quick Jump 5; warps 6 and
  9 on three other engines).
- **End point of a partial move (MEASURED, 8 fleets in all four
  quadrants plus 1 planet target).** Each coordinate is rounded to the
  nearest integer. Truncation toward zero and floor were each contradicted
  by at least two fleets. No exact .5 case was produced (straight lines
  between integer points at warp² distance cannot give one).
- **Arrival (MEASURED).** At warp 5 fleets arrived exactly on the target at
  25.02, 25.30, 25.50, 25.61 (two directions), 25.71 and 25.96 ly, and
  stopped short at 26.00 and 26.02 ly. "Arrive when less than 1 ly would
  remain" (floor(d) ≤ warp²) fits; "rounded end point equals the target"
  and "d ≤ warp² + 0.5" were each contradicted.
- **Fuel (MEASURED, interpretation in brackets).** Used fuel fits
  `floor((M·D + C) / 20000)` with one rounding per fleet:
  - `M` = Σ over ships of mass × engine table value at the warp, cargo
    included (freighter at 0/1/35/70 kt);
  - `D` = warp² for a partial move; for an arrival, ceil(d) capped at warp²
    (FD: six diagonal arrivals rejected the exact and the truncated
    distance; FA: arrivals at 25.30 and 25.96 ly were charged 25);
  - `C` in [18000, 18040) (K: eleven threshold points). [C = 18000 is the
    same as truncating to tenths of a mg and rounding up.]
  - Seven QJ5 scouts used 41 mg, not 7 × 6 = 42: no per-ship rounding. A
    fleet of 3 QJ5 + 1 AD8 scouts used 74, not 75 (per-design rounding).
  - One mixed fleet (QJ5 freighter + AD8 scout, 70 kt cargo in the
    freighter) used 132 mg: the cargo was charged at the freighter's
    engine. Only this one split was observed.
- **Not enough fuel (MEASURED).** A fleet that cannot pay for its move
  moves `floor(fuel × 20000 / M)` ly along the line (position rounded as
  above; two diagonal cases confirm the distance is truncated before
  placing), ends with 0 mg, gets event 139, and the warp of its waypoint is
  set to 1. A fleet with 0 mg does not move at all at warps 2 and 6, even
  at warp 2 where the rounded cost of the move would be 0. With exactly the
  fuel the move costs, it moves the full distance.
- **Free speed and ram scoops (MEASURED).** At warp 1 (table value 0 on
  every engine tested) fleets move 1 ly, use no fuel, and gain 1 mg per
  ship (5 ships: 5 mg), capped at capacity (event 243), with an empty or
  partly full tank, on QJ5 and AD8 scouts and a QJ5 freighter. A full tank
  gains nothing. No gain at warp 2 (0 mg charged after rounding) or for a
  fleet without waypoints. Whether the gain depends on the warp or on the
  table value being 0 is UNKNOWN (no engine with a free warp above 1 was
  tested).
- **Waypoint chaining (MEASURED, 5 fleets).** A fleet that reaches waypoint
  1 stops there for the year, whatever movement is left and whatever warp
  waypoint 2 has. A first waypoint at the fleet's own position also uses up
  the year (no movement, no fuel). Event 78 is only sent when no waypoint
  remains.
- **Planet target (MEASURED, 2).** In range: ends on the planet and orbits
  it (position object = planet). Out of range: partial move as above.

### Fleet targets (chasing)

MEASURED; the interpretations are candidates for the decomp reading, not
established rules.

- **Target with ordinary orders (5 pairs, both id orders).** The chaser
  moves toward the target's end-of-year position, in a straight line from
  its own start (perpendicular case: C1 → (1353,1171), C2 → (1117,1321),
  as predicted for "aim at the final position"). A chaser that reaches it
  arrives (event 78, waypoints cleared).
- **Chains (A chases B, B chases Z, Z moves; all six id orders, one of
  them twice, plus Z without orders).** B stays put for the year (no move, no fuel, keeps its orders,
  no event) whenever A's turn comes before B's (ids ABZ, AZB, ZAB, and with
  Z stationary); A then goes to B's unchanged position. When B's turn comes
  first (BAZ, BZA, ZBA), B reaches Z and A reaches B, all at Z's end point.
  [Candidate: a chaser moves its target first if that target has not moved
  yet, and a target that is itself chasing is not moved that way and loses
  the year.]
- **Two fleets chasing each other (10 cases).** They neither swap places
  nor meet at the midpoint or in proportion to speed. Distances moved (low
  id, high id) for gap/warps: 20/4,4 → 12,8; 16/3,3 → 8,8; 20/4,3 → 14,6;
  20/3,4 → 8,12; 10/4,1 → 9,1; 30/5,3 → 22,8; 6/1,1 → 1,1; 40/3,3 → 9,9;
  60/5,5 → 25,25; a 20 ly diagonal at 4,4 met at (+6,+9) from the low id.
  [Candidate that fits all ten, fitted to FM-001/002 and then adjusted after
  FM-003: the year runs in 5 sub-steps; in each, low id first, a fleet moves
  ceil(warp²/5) ly toward the other's current position, never more than
  warp² in total, its position rounded to integers, stopping when it reaches
  the other. The same sub-step scheme does not reproduce ordinary moves or
  the C1/C2 chases, so it is at most a special case for mutual targets.]

### What the corpus distinguishes

- rounding of partial moves: round-to-nearest vs truncation vs floor;
- arrival test: within 1 ly vs rounded end point vs warp² + 0.5;
- fuel: one rounding per fleet vs per ship vs per design; the rounding
  constant to 40 units of 20000; exact vs truncated vs rounded-up distance
  on arrival; capping at warp² beyond it; cargo in the mass; cargo at the
  carrying ship's engine (one case);
- fuel-limited moves: distance truncated before placing; empty tank never
  moves at a paid warp; warp reset to 1;
- ram-scoop gain: per ship, capped, only while moving at warp 1 here;
- waypoint chaining: stop at each waypoint, zero-length leg uses the year;
- chases: end-of-year target position, the chain freeze, mutual-chase
  distances.

### Open

- Ram-scoop gain for engines with free speeds above warp 1 (Fuel Mizer,
  Settler's Delight, ram-scoop engines), IFE and other LRTs, warp 10+.
- Where cargo is charged in mixed fleets with more than one carrier.
- Whether chain freezing and the mutual-chase scheme hold for three-way
  cycles and in the next year.
- Minefields, stargates, wormholes, refuelling at planets, and movement
  that interacts with other players were deliberately not tested.
