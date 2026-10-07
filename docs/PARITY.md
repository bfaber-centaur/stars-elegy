# Stars! J-RC3 Parity Notes

The rules established here are restated as an implementer's specification,
with test vectors and a CONFIRMED / BINARY-ONLY status per rule, in
`KERNEL.md`.

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

- ~~Exact growth formula above 25% capacity.~~ Resolved: CONFIRMED in
  `KERNEL.md` ("Population growth"). The white-box rule (16/9 × (1 − x)²
  evaluated in integer permille of capacity, then the carry) reproduces
  every population 2400–2436, including the eleven crowded turns of PG-002
  and PG-003 that rejected H0, H1 and H2 as stated below.
- ~~`excessPop` across the crowded turns.~~ Resolved: decoded from the
  preserved PG-003 `.HST` files (apparatus `evidence/pg003/`) for
  2408–2436; it matches the carry of the same rule every year (values in
  `KERNEL.md`).
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

### KX-001 Z — Alternate Reality with zero maximum population

Status: MEASURED, matches the binary reading (Z1–Z3 plus a Host Mode
repeat of Z1, 2026-10-07). Predictions were committed (`a874f82`) before
any case ran; results follow them.

Question (`KERNEL.md`, "Open experiments"): an Alternate Reality planet
without the owner's starbase has maximum population 0, and the crowding
rule divides by the maximum population. What does a year do?

Reachability: when an AR race colonizes, the planet receives a starbase.
The binary reading has two ways to lose it: a destroyed starbase also
uninhabits an AR planet, but deleting the starbase's design clears the
planet's starbase without touching its population. So the state is
reachable in play.

Method: edit PG001 2407 (both files): player 1's PRT to Alternate Reality,
Endeavor's starbase removed (Z1, Z3) or kept (Z2), no other planet edits
(population 486, `excessPop` 80, no production queue, 10 mines). Endeavor
is a 100% planet for this race, and its starbase is a Space Station hull.

Binary reading (`stars-decomp`): the hostile-planet branch is taken
before the maximum population is consulted, so it is safe. On a planet
with habitability ≥ 0 the crowding test computes
`trunc(1000·P / max)` whenever `trunc(max/4) ≤ P`, which is always true
for `max = 0`; the 32-bit division helper then executes an integer divide
by zero. The same function is also used to show next year's growth on the
planet screen. Resources: AR effective population is
`min(2·max, max + trunc((P − max)/2))` = 0, so resources are raised from
0 to the minimum 1.

Candidate outcomes for Z1:

| | Outcome |
|---|---|
| a (binary) | integer divide-by-zero fault: the year is not generated (no 2408 host file), with a Windows or Stars! error; possibly already when the player file is opened and the planet is drawn |
| b | the fault is ignored or trapped and garbage `c` feeds the overcrowding branch: deaths of up to 6% a year, or an arbitrary change |
| c | population unchanged or planet abandoned (some guard the reading missed) |

Predictions:

| Case | Edit | Predicted 2408 |
|---|---|---|
| Z1 | AR, starbase removed, hab 100 | outcome a: no new year |
| Z2 | AR, starbase kept (control) | year generates; maximum 10,000 (Space Station), pop 486 → 535, carry 80 → 40; research 99 (AR resources with floating `E/R0`: `trunc(sqrt(48.6·2)·100·0.1 + 0.999)`; `KERNEL.md`'s `trunc(E/R0)` gives 98); mining with `trunc(sqrt(486)) = 22` mines: +6/+24/+18, each +0 or +1 (random) |
| Z3 | AR, starbase removed, race gravity range 70–100 (hab −15) | year generates (hostile branch); pop 479, carry 51; deaths message; research 1; mining as Z2 |

Z2 separates "the race edit broke the files" from a real zero-maximum
effect in Z1, and settles the AR resource rounding. Z3 checks that only
the habitable branch divides. Random: mining's +1 per mineral (Z2, Z3);
the population results draw no random numbers.

Observation:

| Case | Observed | vs prediction |
|---|---|---|
| Z1 | The player file opened normally (planet screen: "Resources/Year 1 of 1", mines 22, "no starbase"). After Turn → Generate, Windows showed "Application Error — integer divide by 0"; no 2408 files were written | outcome a |
| Z1 repeat | The same starting files generated from the Host Mode dialog (no planet screen drawn): the same "integer divide by 0" error; the host file stayed at 2407 | outcome a |
| Z2 | pop 535, carry 40; research 99; minerals +7/+25/+19 | match (both random +1s came up) |
| Z3 | pop 479, carry 51; research 1; minerals +7/+25/+18; message "population died" (id 0x25, 486 → 479) | match |

Result:

- An Alternate Reality planet with population, habitability ≥ 0 and no
  starbase stops turn generation with an integer divide-by-zero error.
  The year cannot be generated while that state exists. LEGACY BUG: the
  original defines no behavior an implementation could copy.
- The same planet with a hostile environment (Z3) generates normally on
  the hostile-planet death rule, so only the habitable branch divides.
- AR resources use floating division of population by colonists per
  resource (Z2: 99, not 98), and AR mines are `trunc(sqrt(population))`
  (22 here; ten installed mines would have given +3/+11/+8).
- Not tested: reaching the state in play (the reading's route is deleting
  the starbase design), AR maximum population by hull (Z2 was uncrowded),
  and a population of 10 or fewer (the division happens before the
  "within 10 of maximum" test in the reading, so it should fault too).

Evidence: `evidence/kx001/` in the private apparatus repository (raw files,
screenshots of both error dialogs, decoded dumps).

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

## Production Queues

Status: MEASURED (PQ-001: 15 cases plus two repeats and a pilot, 20
generated years, one planet, one race; 2026-10-07). This section is the production track; it does not
touch population or movement results.

### PQ-001 — production-queue boundary corpus

Question: does one year of J-RC3 production follow the queue algorithm
read from the binary in the private `stars-decomp` notes, at the boundaries
where plausible implementations differ (partial builds, mineral shortfall,
auto items, alchemy, research tax, queue caps)?

Method. Every case starts from the `registered` oracle snapshot (PG001,
2407). Before the turn, Endeavor (planet 7) and player 1 are edited in both
`PG001.HST` and `PG001.M1` with the StarsAPI codec (decode, change fields,
re-encode; an unmodified file round-trips byte-identically). Then
`turn PG001.M1` runs one year with no client orders. The 2408 `.HST` and
`.M1` are decoded for surface minerals, installations, the production
queue, the player's "resources to research this year" field and the year's
event records.

Common starting edits, unless a case says otherwise: mines 0 (so nothing is
mined), factories 0, defenses 10 (unchanged), research budget 0%,
"contribute only leftover resources to research" off, surface minerals
500/500/500 kT, `excessPop` 80 (unchanged). With no factories the planet's
resources are `R = population / 10` (population in units of 100).
Race costs (PG001, observed in the player block): factory 10 resources +
4 kT germanium, mine 5 resources, defense 15 resources + 5/5/5 kT, alchemy
100 resources.

Model under test (behavioral summary of the decomp reading):

- The research tax `floor(R × budget% / 100)` is taken first, unless the
  leftover-only box is set.
- Items are processed in order. A unit is completed when every remaining
  cost component (cost − already spent) is available.
- Otherwise the item gets a partial percentage. Per component with
  available `a` (including what is already spent) and cost `c`:
  `p = max(floor((a+1)·100/c) − 1, floor(a·100/c))`. The formula is the
  rule. It is close to "the largest whole percentage whose truncated cost
  does not exceed `a`" but not equal to it: when `c` does not divide
  `(a+1)·100` it can be one lower (`c = 9`, `a = 4`: 54, where 55 would
  still cost only 4; KX-001 M4 observed 54). The item's
  percentage is the minimum over components. Every component is then
  charged up to `floor(c·p/100)`. The amount already spent on a partial
  unit is `floor(c·pct/100)`.
- A non-auto item that ends partial stops the queue; later items get
  nothing. An auto item that is short of a mineral is skipped (nothing
  spent) and the walk continues.
- Auto items build at most `min(count, cap)` per year, cap = operable
  installations after this year's growth minus installed; they stay in the
  queue. A resource-limited auto item that ends partial inserts a hidden
  ×1 item of the real type at the queue front carrying the percentage, and
  stops the queue.
- Auto Alchemy as the last item ignores its count, converts 100 resources
  into 1 kT of each mineral per unit, and leaves a Mineral Alchemy ×1
  partial at the front. Auto Alchemy before another item buys exactly that
  item's mineral shortfall (1 kT of all three minerals per 100 resources)
  and is removed with it when that item completes.
- A non-auto installation order above `max(maximum, operable) − installed`
  is clipped to that cap, with a message.
- All resources left at the end go to research. A queue that empties, or
  is walked to the end with nothing mineral-blocked, sends "completed its
  orders".

Predictions (written before any PQ-001 case ran). Queue notation:
`Item ×count @pct%`. "Research" is the player's resources-to-research for
the year. Minerals are Fe/Bo/Ge.

| Case | Start (differences from common) | Queue | Predicted 2408 |
|---|---|---|---|
| C01 | pop 1050 (R 105) | Factory ×20 | factories 10; Ge 458; queue Factory ×10 @59%; research 0 |
| C01 year 2 | (C01 result, no edits) R = 115 + 10 | — | factories 20; Ge 420; queue empty; research 30; "completed its orders" |
| C02 | pop 2000 (R 200), Ge 10 | Factory ×5, Mine ×5 | factories 2, mines 0; Ge 0; queue Factory ×3 @74%, Mine ×5; research 173 |
| C03 | pop 2000, Ge 2 | Auto Factories ×100, Mine ×5 | factories 0, mines 5; Ge 2; queue Auto Factories ×100; research 175; no "completed" message |
| C04 | pop 230 (R 23) | Auto Mines ×100 | mines 4; queue Mine ×1 @79%, Auto Mines ×100; research 0 |
| C05 | pop 2500 (R 250), minerals 100/100/100 | Auto Alchemy ×1 | minerals 102/102/102; queue Mineral Alchemy ×1 @50%, Auto Alchemy ×1; research 0; alchemy message |
| C06 | pop 4000 (R 400), minerals 100/100/1 | Auto Alchemy ×1, Factory ×1, Mine ×2 | factories 1, mines 2; minerals 103/103/0; queue empty; research 80 |
| C07 | pop 2500, minerals 100/100/1 | Auto Alchemy ×1, Factory ×1, Mine ×2 | factories 0, mines 0; minerals 102/102/2; queue Mineral Alchemy ×1 @46%, Auto Alchemy ×1, Factory ×1 @49%, Mine ×2; research 0 |
| C08a | pop 1070 (R 107), budget 15% | Factory ×20 | factories 9; Ge 464; queue Factory ×11 @19%; research 16 |
| C08b | as C08a, leftover-only on | Factory ×20 | factories 10; Ge 457; queue Factory ×10 @79%; research 0 |
| C09 | pop 500, factories 50, mines 48 (R 100) | Auto Mines ×100, Auto Factories ×3 | mines 55, factories 53; queue unchanged; research 35; "completed its orders"; minerals = start + mined − 12 Ge (mining not predicted) |
| C10 | pop 1000, factories 995 (R 200) | Factory ×10 | factories 1000; Ge 480; queue empty; research 150; clipped-order message |
| C11 | pop 50 (R 5), minerals 100/100/2 | Factory ×1 @59%, Mine ×10 | factories 1; Ge 0; queue Mine ×10 @19%; research 0 |
| C12 | pop 1000 (R 100), minerals 3/2/100 | Defenses ×5, Mine ×2 | defenses 10, mines 0; minerals 1/0/98; queue Defenses ×5 @59%, Mine ×2; research 92 |

Second batch, predicted after C01–C12 had run and before these ran:

| Case | Start (differences from common) | Queue | Predicted |
|---|---|---|---|
| C13 | pop 1010 (R 101), defenses 40 | Auto Defenses ×100 | defenses 45; minerals 475/475/475; queue unchanged; research 26; "completed its orders" |
| C14 | C04 repeated, two years | Auto Mines ×100 | 2408 as C04; 2409: mines 9, queue Mine ×1 @79%, Auto Mines ×100, research 0 |
| C07r | C07 repeated | as C07 | as C07 |

C13 tests the operable-defenses cap `ceil(P/25)` with P the population
after this year's growth (1111 → 45, so 5 may be built; `floor` gives 4,
pre-growth population gives 1). C14 tests that the hidden partial item is
completed first the next year and the auto item spawns a new one.

What each case discriminates:

- C01, C08, C11: the partial percentage (59% for 5 of 10 resources, not
  50%), and the remaining cost of a carried partial (C11: a 59% factory
  needs exactly 5 resources and 2 kT Ge, not 41% of cost). C11 also
  predicts that a zero-resource partial records 19% with nothing spent.
- C02 vs C03: a non-auto item short of minerals stops the queue; an auto
  item short of minerals is skipped.
- C04, C05: hidden partial items spawned by auto items; C05 also whether
  Auto Alchemy's count is ignored (count respected would give 101/101/101,
  research 150).
- C06, C07: the alchemy prefix, including that alchemy raises all three
  minerals, not only the missing one.
- C08a vs C08b: research tax before production, and the leftover-only box.
- C09: auto caps come from operable installations after growth, and the
  auto count limits the build.
- C10: the clip of non-auto installation orders.
- C12: the partial percentage is the minimum over components (Bo 59%, not
  Fe 79% or a 40% ratio).

Observation (2408 unless noted; decoded from the oracle's `.HST` and `.M1`;
every value in the predicted columns was also checked: minerals,
installations, queue, research, messages):

| Case | Observed | vs prediction |
|---|---|---|
| C01 | factories 10; Ge 458; Factory ×10 @59%; research 0 | match |
| C01 year 2 (2409) | factories 20; Ge 420; queue gone; research 30; "factories built" (10) and "completed its orders" | match |
| C02 | factories 2, mines 0; Ge 0; Factory ×3 @74%, Mine ×5; research 173 | match |
| C03 | mines 5, factories 0; Ge 2; Auto Factories ×100 left; research 175; no "completed" message | match |
| C04 | mines 4; Mine ×1 @79%, Auto Mines ×100; research 0 | match |
| C05 | minerals 102/102/102; Mineral Alchemy ×1 @50%, Auto Alchemy ×1; research 0; alchemy message | match |
| C06 | factories 1, mines 2; minerals 103/103/0; queue gone; research 80; alchemy, factory, mines and "completed" messages | match |
| C07, C07r | minerals 102/102/2; Mineral Alchemy ×1 @46%, Auto Alchemy ×1, Factory ×1 @49%, Mine ×2; research 0; alchemy message | match, both runs |
| C08a | factories 9; Ge 464; Factory ×11 @19%; research 16 | match |
| C08b | factories 10; Ge 457; Factory ×10 @79%; research 0 | match |
| C09 | mines 55, factories 53; queue unchanged; research 35; "completed its orders"; minerals 514/554/528 | match (mining was not predicted: +14/+54/+40 kT from 48 mines) |
| C10 | factories 1000; Ge 480; queue gone; research 150; clipped-order message first | match |
| C11, C11r | factories 1; Ge 0; Mine ×10 @19%; research 0 | match, both runs |
| C12 | defenses 10; minerals 1/0/98; Defenses ×5 @59%, Mine ×2; research 92; no event at all | match |
| C13 | defenses 45; minerals 475/475/475; Auto Defenses ×100 left; research 26; "completed its orders" | match |
| C14 | 2408 as C04; 2409: mines 9, Mine ×1 @79%, Auto Mines ×100, research 0, "5 mines built" | match |

Pilot P0 (unedited PG001 plus Factory ×5, budget 15%): 5 factories, Ge
545 + 8 mined − 20 = 533, research 8 = floor(58 × 15%), queue gone,
"completed its orders".

Result:

- Every predicted quantity matched in all 15 cases, both repeats and the
  pilot. The corpus confirms, for this race and planet:
  - research tax first, truncating; leftover-only box skips it (C08);
  - partial percentage = `max(floor((a+1)·100/c) − 1, floor(a·100/c))`
    per component (not always the largest percentage that fits; see
    the model above), minimum over cost components, all components charged to it (C01, C08,
    C12); spent amount of a carried partial = `floor(cost × pct / 100)`
    (C01 year 2, C11);
  - a zero-resource partial records a percentage with nothing spent (C11:
    19% on a 5-resource mine);
  - a non-auto item short of a mineral stops the queue (C02); an auto item
    short of a mineral is skipped, spends nothing, and suppresses
    "completed its orders" (C03);
  - auto mines/factories/defenses build `min(count, cap)`, cap from the
    operable count after this year's growth (C09, C13: `ceil(P/25)` for
    defenses), and stay queued;
  - a resource-limited auto item leaves a hidden ×1 partial of its real
    item at the queue front, which is finished first next year (C04, C14);
  - Auto Alchemy ignores its count when last (C05), and as a prefix buys
    the item's mineral shortfall as kT of all three minerals and leaves a
    Mineral Alchemy partial when resources run short (C06, C07);
  - non-auto installation orders above `max(maximum, operable) − installed`
    are clipped with a message (C10);
  - leftover resources go to research whether the queue empties or stops
    (C02, C06, C09, C10, C13).
- Nothing contradicted the white-box reading.
- Repeats (C07r, C11r) were identical. Nothing in these cases is known to
  draw random numbers; mining (C09, C14 year 2) was not predicted.

Not covered (open): ship and starbase designs, terraforming, mineral
packets, planetary scanners, Genesis Device, Mineral Alchemy LRT rates,
other race costs (e.g. cheap factories), ultimate-recycling scrap bonus,
non-100% habitability caps, items with count 0 or an empty queue block,
whether "completed its orders" repeats every year for an auto-only queue
(seen for one year in C09/C13), and message wording (only ids were read).

Evidence: edited inputs, every resulting game file, decoded dumps, the
prediction model and a SHA-256 manifest are in the private
`bfaber-centaur/stars-oracle-apparatus` repository under `evidence/pq001/`.
Tooling to repeat a case: `scripts/oracle/edit-turn` with
`scripts/oracle/hst-edit` (docs/ORACLE.md, "Setting up a state").

### KX-001 — Auto Alchemy before a multi-count item; race cost options

Status: MEASURED, matches the binary reading (9 cases, one year each,
2026-10-07). Predictions below were committed (`a874f82`) before any case
ran; results follow them.

Questions (`KERNEL.md`, "Open experiments"):

1. With an Auto Alchemy prefix before a ×n item, does alchemy buy the
   shortfall one unit at a time, for the whole remaining count, or only
   for the first unit, and how are the item's partial and the alchemy
   ordered when resources run short?
2. Do the Mineral Alchemy LRT and race options that change installation
   costs (factory and mine resource cost, "factories cost 1 kT less
   germanium", Inner Strength defenses) change production as the binary
   reading says?

Method: as PQ-001 (edit PG001 2407 `.HST` and `.M1` with
`scripts/oracle/hst-edit`, generate one year, decode). Common edits as
PQ-001: mines 0, factories 0, defenses 10, research budget 0%, minerals
500/500/500, `excessPop` 80. Race options are edited in player 1's race
data (`prt=`, `lrt=`, `stat=` keys, added to `hst-edit` for this
experiment). PG race costs, unless changed: factory 10 resources + 4 kT
germanium, mine 5, defense 15 + 5/5/5, alchemy 100 resources per kT of
each mineral.

Model (binary reading, `stars-decomp`; the PQ-001 model with costs taken
from the race):

- Alchemy prefix before a ×n item works **one unit at a time**. For each
  unit short of a mineral, the unit first takes its partial percentage
  (spending to that percentage on every component, as for any partial),
  then alchemy buys that unit's shortfall in the limiting mineral (one
  "unit" of alchemy = 1 kT of each of the three minerals). If it can buy
  the whole shortfall the unit completes and the next unit starts the same
  way. If it cannot, it buys what it can, the unit keeps the percentage
  it had **before** the alchemy, any resources left become a Mineral
  Alchemy ×1 partial at the queue front, and the queue stops; the prefix
  and the item (count reduced) stay. If every unit completes, the item and
  the prefix are removed.
- An auto item after the prefix (Auto Factories) skips the partial spend
  and goes straight to alchemy.
- Mineral Alchemy LRT: alchemy costs 25 resources per unit instead of 100
  (both as a final Auto Alchemy and as a prefix).
- Factory resource cost = race factory cost; germanium 3 kT instead of 4
  with "factories cost 1 kT less germanium"; mine cost = race mine cost;
  Inner Strength defenses cost `trunc(c·3/5)` of every component (9
  resources + 3/3/3 kT).

Competing outcomes for A1 (Factory ×5, no germanium, 900 resources), to
show what each case separates:

| Hypothesis | A1 factories | A1 minerals | A1 queue |
|---|---|---|---|
| per unit (model) | 2 | 108/108/0 | Mineral Alchemy ×1 @78%, Auto Alchemy, Factory ×3 @24%, Mine ×2 |
| whole count first (buy 9 of the 20 kT short, nothing left to build) | 0 | 109/109/9 | Auto Alchemy, Factory ×5, Mine ×2; research 0 |
| first unit only, then a plain mineral-short partial | 1 | 104/104/0 | Auto Alchemy, Factory ×4 @24%, Mine ×2; research 488 |

Predictions (2408). Pop in units of 100; `R = pop/10` resources (no
factories). "Research" is the player's resources-to-research field.

| Case | Race | Start (differences from common) | Queue | Predicted |
|---|---|---|---|---|
| A1 | PG | pop 9000 (R 900), minerals 100/100/0 | Auto Alchemy, Factory ×5, Mine ×2 | factories 2; minerals 108/108/0; queue Mineral Alchemy ×1 @78%, Auto Alchemy ×1, Factory ×3 @24%, Mine ×2; research 0; alchemy message (8), factories message |
| A2 | PG | pop 9000, minerals 100/100/6 | as A1 | factories 3; minerals 108/108/2; queue Mineral Alchemy ×1 @68%, Auto Alchemy ×1, Factory ×2 @24%, Mine ×2; research 0 |
| A3 | PG | pop 9000, minerals 100/100/0 | Auto Alchemy, Auto Factories ×5, Mine ×2 | factories 2; minerals 108/108/0; queue Mineral Alchemy ×1 @80%, Auto Alchemy ×1, Auto Factories ×5, Mine ×2; research 0 |
| A4 | PG | pop 8200 (R 820), minerals 100/100/0 | Auto Alchemy, Factory ×2, Mine ×2 | factories 2; minerals 108/108/0; queue Mine ×2 @19%; research 0 (prefix removed with the item; 0 resources left) |
| M1 | Mineral Alchemy LRT | pop 2600 (R 260), minerals 100/100/100 | Auto Alchemy | minerals 110/110/110; queue Mineral Alchemy ×1 @43%, Auto Alchemy ×1; research 0 (without the LRT: 102/102/102, @60%) |
| M2 | Mineral Alchemy LRT | pop 3000 (R 300), minerals 100/100/0 | Auto Alchemy, Factory ×5, Mine ×2 | factories 2; minerals 111/111/3; queue Mineral Alchemy ×1 @15%, Auto Alchemy ×1, Factory ×3 @24%, Mine ×2; research 0 |
| M3 | factory cost 7, mine cost 3, factories −1 kT Ge | pop 310 (R 31) | Factory ×3, Mine ×4 | factories 3, mines 3; minerals 500/500/491; queue Mine ×1 @65%; research 0 (PG costs would give Ge 488, Mine ×4 @39%) |
| M4 | Inner Strength | pop 400 (R 40) | Defenses ×5 | defenses 14; minerals 487/487/487; queue Defenses ×1 @54%; research 0 (PG costs: defenses 12, Defenses ×3 @72%) |

A2 also checks that a unit already holding part of its germanium spends
its partial first and buys only the rest (2 kT, not 4), and that the last
unit keeps 24% although alchemy has just added 2 kT of germanium.
Nothing in these cases draws random numbers (mining is off: no mines).

Observation (2408, decoded from the oracle's `.HST` and `.M1`; every
predicted quantity checked):

| Case | Observed | vs prediction |
|---|---|---|
| A1 | factories 2; minerals 108/108/0; Mineral Alchemy ×1 @78%, Auto Alchemy ×1, Factory ×3 @24%, Mine ×2; research 0; alchemy message (8 units), factories message (2) | match |
| A2 | factories 3; 108/108/2; Mineral Alchemy ×1 @68%, Auto Alchemy ×1, Factory ×2 @24%, Mine ×2; research 0 | match |
| A3 | factories 2; 108/108/0; Mineral Alchemy ×1 @80%, Auto Alchemy ×1, Auto Factories ×5, Mine ×2; research 0 | match |
| A4 | factories 2; 108/108/0; Mine ×2 @19%; research 0 | match |
| M1 | 110/110/110; Mineral Alchemy ×1 @43%, Auto Alchemy ×1; research 0; alchemy message (10) | match |
| M2 | factories 2; 111/111/3; Mineral Alchemy ×1 @15%, Auto Alchemy ×1, Factory ×3 @24%, Mine ×2; research 0; alchemy message (11) | match |
| M3 | race-tamper message (id 0x117); the race's colonists-per-resource setting went from 1000 to 2400 during the turn; factories 1; Ge 495; Factory ×2 @84%, Mine ×4; research 0 | prediction void: the race was changed before production (below) |
| M3b | factories 2; Ge 494; Mine ×4 @24%; research 0; no tamper message | match |
| M4 | defenses 14; 487/487/487; Defenses ×1 @54%; research 0 | match |

M3 used a race the game judged over budget: factory cost 7 and mine cost 3
are cheaper than the PG race's 10 and 5 and nothing paid for them. The
year's first step flagged it and degraded it (white-box reading:
`stars-decomp` race sanitising, which raises colonists per resource until
the race's advantage points reach a threshold, message 0x117). With
2,400 colonists per resource, `R = trunc(310/24) = 12`, and the model
then gives exactly what was observed: one factory at 7 resources + 3 kT
germanium, then 84% of the second (`max(6·100/7 − 1, 5·100/7) = 84`,
spending 5 resources and `trunc(3·84/100) = 2` kT). So M3 still confirms
the factory cost 7 and the 3 kT germanium. M3b repeated the cost test
with costs above the PG race's (factory 15, mine 8, plus the germanium
option), predicted with the same model after M3 and before M3b ran (not
committed separately): two factories at 15 + 3 kT, then the mine partial
at 24% of 8 (`max(2·100/8 − 1, 1·100/8)`; cost 5 would give 39%).

Result:

- Auto Alchemy before a ×n item works one unit at a time, as read (A1–A4,
  M2). Each mineral-short unit first takes its partial percentage, then
  alchemy buys that unit's shortfall; A2's last unit kept 24% although the
  alchemy had just added 2 kT of germanium. When alchemy runs out the queue
  stops behind a Mineral Alchemy partial at the front and the prefix stays;
  when every unit completes, item and prefix are removed (A4). An auto item
  after the prefix goes straight to alchemy without a partial (A3: 80%
  Mineral Alchemy, not 78%).
- Mineral Alchemy LRT: 25 resources per alchemy unit, final and prefix
  (M1, M2).
- Factory and mine resource costs come from the race settings, the
  "factories cost 1 kT less germanium" option makes a factory 3 kT (M3,
  M3b), and Inner Strength defenses cost 9 resources + 3/3/3 kT (M4).
- A race edited beyond its advantage-point budget is degraded by the game
  before production that year (M3, MEASURED once; the threshold and the
  points formula are not measured).
- Nothing contradicted the white-box reading. Nothing here draws random
  numbers.

Follow-up A5 (predicted and committed before it ran): does an Auto
Alchemy prefix stay in the queue after the auto item it serves builds
everything it can? Binary reading: an auto item whose count (capped by
operable installations) is used up returns "done for this year", which
moves to the next item without removing anything; only a non-auto item
that completes removes its prefix. Case A5: pop 9000 (R 900), minerals
100/100/0, queue Auto Alchemy, Auto Factories ×2, Mine ×2. Predicted:
factories 2, mines 2; minerals 108/108/0; queue Auto Alchemy ×1, Auto
Factories ×2 (prefix kept); research 70; alchemy (8), factories, mines and
"completed its orders" messages. If the prefix were removed with the auto
item's year, the queue would be Auto Factories ×2 alone.

A6, A7 (predicted and committed before they ran). Re-reading the
binary for the tie question showed that "limited by a mineral" is not
decided by the minimum alone. While the percentages are compared
(minerals first, then resources; a component replaces the current minimum
only when strictly lower), two flags are kept: "some mineral is short"
and "resources were strictly lowest". An **auto** item is treated as
mineral-limited (skipped without a prefix, alchemy with one) whenever
some mineral is short, even if resources are strictly lower; with a prefix
the alchemy then uses the shortfall of the component that was lowest,
which can be the resource shortfall. A **non-auto** item with a prefix
buys minerals unless resources were strictly lowest, so a resource/mineral
tie goes to the mineral. Ties between minerals keep the first in Fe, Bo,
Ge order. The PQ-001 and KX-001 cases never had resources strictly below
a short mineral on an auto item, so they did not test this.

| Case | Start | Queue | Predicted (binary) | If only the minimum decided |
|---|---|---|---|---|
| A6 | pop 10 (R 1), minerals 100/100/0 | Auto Alchemy, Auto Factories ×2 | queue Mineral Alchemy ×1 @1%, Auto Alchemy ×1, Auto Factories ×2; minerals 100/100/0; research 0 | Factory ×1 @19% at the front |
| A7 | pop 10 (R 1), minerals 100/100/0 | Auto Factories ×2, Mine ×1 | Auto Factories skipped; queue Auto Factories ×2, Mine ×1 @39%; research 0; no "completed" message | Factory ×1 @19% at the front, Mine untouched |

(At pop 10 the auto cap is one factory. Germanium 0 gives 24% for the
factory's germanium; 1 resource gives 19% for its 10 resources.)

Not covered: terraforming costs (Total Terraforming, Claim Adjuster),
packets, scanners, starbase and ship costs, the tamper check's points
formula.

Evidence: private `bfaber-centaur/stars-oracle-apparatus`,
`evidence/kx001/` (edited inputs, every resulting file, decoded dumps, the
model and a SHA-256 manifest). Tooling: `scripts/oracle/edit-turn` with the
race keys of `scripts/oracle/hst-edit` (`ORACLE.md`).

## Fleet Movement

Status: MEASURED (four one-turn oracle batches, FM-001 to FM-004, plus the
FM-000 pilot; 224 fleets). Run on 2026-10-07 with the cloud oracle. FM-004
tested predictions made from the private binary reading (stars-decomp)
before the turn was run; all 55 matched (see "Binary-model check" below).
Rules marked CONFIRMED below agree with both the binary reading and the
oracle.

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
and `predictions.tsv`, commits `90037e5`, `4a56c40`, `bc0ed91`, `28fd54f`). Observed
values per fleet: `experiments/fm00N/results.tsv`. Raw files, dumps and
message screenshots: private `stars-oracle-apparatus`, `evidence/fm000/` to
`evidence/fm004/`.

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
  - Superseded by FM-004 (CONFIRMED): rounding is per ship design, not per
    fleet; see "Binary-model check". The fleet-level formula above
    reproduces FM-001..003 but fails four mixed fleets in FM-004.
- **Not enough fuel (MEASURED; distance refined by FM-004).** A fleet that cannot pay for its move
  moves `floor(fuel × 20000 / M)` ly along the line (position rounded as
  above; two diagonal cases confirm the distance is truncated before
  placing), ends with 0 mg, gets event 139, and the warp of its waypoint is
  set to 1 (FM-004: to the fastest free warp, which is 1 for these
  engines). A fleet with 0 mg does not move at all at warps 2 and 6, even
  at warp 2 where the rounded cost of the move would be 0. With exactly the
  fuel the move costs, it moves the full distance.
- **Free speed and ram scoops (MEASURED).** At warp 1 (table value 0 on
  every engine tested) fleets move 1 ly, use no fuel, and gain 1 mg per
  ship (5 ships: 5 mg), capped at capacity (event 243), with an empty or
  partly full tank, on QJ5 and AD8 scouts and a QJ5 freighter. A full tank
  gains nothing. No gain at warp 2 (0 mg charged after rounding) or for a
  fleet without waypoints. FM-004 measured engines free above warp 1; see
  "Binary-model check".
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

### Binary-model check (FM-004)

Status: CONFIRMED for every rule in this subsection (stars-decomp reading of
fleet movement, predictions computed from it and committed before the run;
55 of 55 fleets matched position, fuel, waypoint warp, orbit, waypoints left
and events, `experiments/fm004/compare.py`). The FM-001..003 description
above failed 37 of the 55. The decomp model also reproduces all 169
FM-001..003 fleets, chases included, without fitted constants (checked by
re-running its checker on this corpus). One run, one race (SS, no LRT);
the Fuel Mizer, Settler's Delight and Radiating Hydro-Ram Scoop scouts were
FleetLab clones (Fuel Mizer and Settler's Delight normally need IFE and the
HE race type).

Below, `f` is an engine's fuel-table value at the warp (StarsAPI's tables
agree with the binary's), `m` a ship's mass in kT, `n` a ship count.

- **Fuel for `d` ly.** Ship stacks (one per design in the fleet) are taken
  in ascending `f`; each stack carries cargo up to its cargo capacity
  before the next stack takes any (so cargo rides on the cheapest engine
  first). Each stack with `f > 0` costs `floor(f·d·(n·m + cargo carried) /
  2000)` tenths of a mg; the fleet pays `ceil(Σ tenths / 10)` mg. `d` is
  warp² for a partial move and ceil(distance) for an arrival.
  - MS: QJ5+LH6 scouts at warp 2 paid 0 mg (one fleet-level rounding: 1);
    QJ5+FM at warp 5 paid 3 (4); 2 LH6+DLL7 at warp 5 paid 9 (10);
    QJ5+SD at warp 8 paid 60 (61).
  - CA: a QJ5 freighter + LH6 freighter fleet carrying 70 kt paid 30 mg at
    warp 6 (cargo at the LH6 engine; at the QJ5 engine it would be 40);
    with 100 kt, 40 mg (70 kt at LH6, 30 kt at QJ5).
- **Range on the fuel left.** `R = floor(fuel·1000 / floor(T/10))` ly, where
  `T` is the tenths-of-mg cost of 1000 ly from the line above. When a move
  needs more than the fleet has (and the fleet could not pay for the whole
  leg), it moves `R` ly, the tank is set to 0. LR: six fleets where this
  differs from `floor(fuel·20000/M)` each moved the 1 ly further that `R`
  predicts.
- **Warp after running dry.** The waypoint's warp becomes one less than
  the lowest warp at which the whole leg (from the fleet's position at the
  start of the year) would cost fuel, with
  event 139 (whose text names that warp). Observed: Fuel Mizer 7 or 9 → 4;
  Settler's Delight 8 or 10 → 6; Hydro-Ram 8 → 6; QJ5/LH6/DLL7/AD8 → 1. A
  Fuel Mizer with 0 mg at warp 7 did not move and dropped to 4; with a
  2-ly leg, to 5 (2 ly at warp 5 costs 0 mg, so warp 6 is the first that
  costs fuel).
- **Fuel gained at a free warp.** A moving fleet whose engine is free at
  its warp gains `Σ n · e · k · d'` mg, capped at capacity (event 243):
  `e` engines per ship; `k` = 1, 3, 6 or 10 when 1, 2, 3 or 4 consecutive
  warps starting at the current one are free; `d'` = the distance moved,
  or ceil(distance) − 1 on the arriving year. Observed: Fuel Mizer warps
  1–4: +10, +24, +27, +16; Settler's Delight warps 1–6: +10, +40, +90,
  +96, +75, +36, and none at 7; Hydro-Ram 4 and 6 as Settler's Delight;
  3 Fuel Mizers at warp 2: +72; QJ5 + Fuel Mizer at warp 2: +24 (the QJ5
  stack's 0.9-tenth cost rounded to 0); arrivals at 10 ly and at
  (7,7) on Settler's Delight warp 4: +54 and +48; at 3 ly on Fuel Mizer
  warp 2: +12; QJ5 and AD8 at warp 1: +1. Not gained in the year a fleet
  runs dry. Any engine qualifies, not only ram scoops.
- **Top-up on an affordable leg.** If the fleet had fuel for the whole leg
  when the year began and the rounded per-year charge leaves less than the
  rest of the leg costs, the tank is raised to that cost (never above
  capacity). QJ5 scout, warp 9, 126 ly, 102 mg: 37 mg after the year
  (102 − 66 = 36 raised to 37); with 101 mg (not enough for the leg) it
  ended at 35. QJ5 freighter with 70 kt, warp 6, 143 ly: 98 (97 raised).
- **Starbase refuelling.** After moving, a fleet at its own planet with a
  dock-capable starbase (PG001's homeworld starbase) has its tank set to
  capacity: stationary at 50 mg → 300, 10 → 130 (freighter), and 400
  (over capacity) → 300; arriving there → 300. A fleet arriving at a planet
  without a starbase was not refuelled; one leaving the homeworld was not.
  A fleet in deep space keeps 400 mg in a 300 mg tank.
- **Orbit.** A deep-space waypoint placed exactly on a planet's
  coordinates puts the fleet in orbit of that planet (and refuels it at
  the homeworld).

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
  distances;
- FM-004: per-design vs per-fleet fuel rounding; which stack carries cargo;
  the two range formulas; warp after running dry for engines free above
  warp 1; fuel gain by warp, ship count, cap and arrival year; top-up vs
  none; starbase refuelling; orbit by exact coordinates.

### Open

- IFE and other LRTs (the binary reading has IFE cut engine fuel by 15%
  and Cheap Engines fail at warp 7–10 at random), warp-10 ship losses
  (random in the binary reading), fuel transports and anti-matter
  generators, and fuel transfer orders: not tested.
- The chase candidates above are now explained by the binary reading
  (white-box: chasers move after the other fleets in steps of about a fifth
  of warp² while their target has not moved; a chaser landing on a target
  that is itself chasing stops it for the year). The oracle side has only
  the FM-001..003 cases.
- Whether chain freezing and the mutual-chase scheme hold for three-way
  cycles and in the next year.
- Minefields, stargates, wormholes, and movement
  that interacts with other players were deliberately not tested.

## Combat

Status: MEASURED (round 1 CB-000 to CB-008, round 2 CB-009 to CB-019,
2026-10-07; cloud oracle). Predictions from the private binary reading
(stars-decomp `docs/combat-predictions.md`: P-1..P-29 at 8cad60f for
round 1, Q-1..Q-14 at 4a8c82b for round 2) were committed before every
run (`experiments/cbNNN/README.md`).
Rules marked CONFIRMED agree with both that reading and the oracle;
CONTRADICTED means the oracle disagrees with the prediction as stated.
This section states behavior only.

### Method

- Universe "Combat Lab" (CB, see `docs/ORACLE.md`): new 2-player game, two
  Humanoid (JOAT) players, tiny, sparse, no random events. Every start is
  the 2400 host file rewritten by `tools/fleetlab/combatlab build`
  (designs, starbase designs, battle plans, relations, tech, LRTs, fleets);
  one Host Mode generation 2400 → 2401 per experiment
  (`tools/fleetlab/host-turn`).
- Both players at tech 26 in every field (so nothing can be learned from
  battle) and mutual enemies. Test fleets sit in deep space on y = 1230,
  40 ly apart, so one turn holds up to 8 separate battles.
- Battle records were read from both players' `.M` files (identical
  records) with `combatlab dump`, and every hit was replayed through the
  binary-derived damage model: 189 hit records matched, 0 mismatched,
  2 not checkable (hits on a starbase), over 32 battles in 9 runs.
- Round 1 was not reproducible: CB-001 run twice from the same file gave
  different token movement. Hit counts of the torpedo salvos, which the
  rule makes independent of random draws, were identical. Round 2 pins
  the random stream (`tools/fleetlab/pinned-turn`, `docs/ORACLE.md`):
  the same file and DOSBox cycle setting gave byte-identical battle
  records in every repeat tried.
- Raw files, dumps, check outputs and designer screenshots: private
  `stars-oracle-apparatus`, `evidence/cb/`.

### Designer (CB-000, CONFIRMED 32/32)

The ship designer's "Initiative / Moves" and mass agreed with the
prediction for all 32 designs (16 engines, computers, jets, overthrusters,
1–4 engines, masses 10–602). Rule (also the battle speed rule, without
battle-only terms):

- initiative = hull initiative + 1 per Battle Computer, 2 per Battle Super
  Computer, 3 per Battle Nexus (capped at 63);
- speed code = w − 4 + maneuvering jets + 2·overthrusters
  + (Enigma Pulsars + 1)/2 − (mass/70)/engines, clamped 0..8 (integer
  divisions), where w = 10 for Interspace-10, Enigma Pulsar, Trans-Star 10,
  Trans-Galactic Mizer Scoop and Galaxy Scoop, otherwise the highest warp
  ≤ 9 whose fuel-table entry is at most 120;
- moves per round = (code + 2)/4 squares, shown as ½ … 2½.

Per-design values: `experiments/cb000/predictions.tsv` and `results.tsv`.

### Board and tokens (CONFIRMED)

- With two players, player 0's tokens start on square (1,4) and player 1's
  on (8,5) of the 10×10 board (P-2; 32 battles).
- One token per (fleet, design). Token values in the record matched the
  prediction: initiative, weapon initiative, computer % (BSC 30), jammer %
  (20, 50), capacitor (2 × Flux + Energy Capacitor → 132%), deflector
  (90%), shield and armor per ship, mass and speed code (P-3).
- Regenerating Shields: shield per ship is 7/5 of the design value
  (2 Mole-skin → 70), and armor from armor parts is halved (2 Tritanium on
  a Destroyer → 250, although the edited design record said 300: the game
  recomputes armor) (P-24).
- An Energy Dampener in the battle sets every ship token's speed code 4
  lower (2 → 0) (P-8).
- Starbase tokens: kind starbase, initiative 14, mass shown as 65535;
  Gatling initiative 26 on a station.

### Movement (MEASURED, partly)

- Tokens move ½ … 2½ squares per round from the speed code, as an
  alternating pattern: speed code 1 moved 1,1,0,1…; code 5 moved 2,2,1,2
  (P-7).
- A disengaging (or unarmed, fleeing) token leaves the board on its 8th
  move; the remaining-move counter is visible in the move record (P-10).
  A stack on "disengage if challenged" switched to disengaging after it
  first took armor damage and kept firing (CB-003/004 D).
- Tactics "maximize net damage" vs "maximize damage ratio" (P-11, Q-9):
  CONTRADICTED. With the stream pinned, one Long Destroyer (Phaser
  Bazooka, Colloidal Phaser) attacking an immobile Laser Station moved
  identically until round 6, then stopped on (5,5) under tactic 3 and on
  (5,6) under tactic 4 (both 3 squares from the station), with the same
  hits, in both of two seeds (CB-019).

### Weapons and damage (CONFIRMED by replay)

- **Torpedo salvos of more than 200 torpedoes.** Such a salvo at hit
  chance p% hits exactly floor(N·p/100) times: 202 Beta torpedoes hit
  90 / 125 / 103 / 72 times for p = 45 (no computer), 62 (BSC), 51 (BSC vs Jammer 20), 36 (BSC vs
  Jammer 50) — the same numbers in both CB-001 runs (P-17, P-18). Hit
  chance: with c = max(0, computer − jammer) and j = max(0, jammer −
  computer), p = 100 − (100 − c)(100 − accuracy)/100 if c > 0, else
  accuracy·(100 − j)/100 (integers). The fixed count was tested only with
  N = 202. For salvos of 200 or fewer the binary reading draws each
  torpedo at random; that case was not checked against the oracle beyond
  the replay of recorded hits.
- **Missiles** (Jihad) do double damage to a stack with no shields:
  202 Jihads at 20% hit 40 times for 6800 damage on two 3650-armor Hulks
  (one killed, the survivor shown 432/500 damaged) (P-20).
- Torpedoes and missiles against a target with 0 shields leave no miss
  records (P-19, partial; misses against shields not observed).
- **Beams** do full damage at distance 0 and drop off linearly to 90% at
  the weapon's range (Laser 90% at distance 1; Phaser Bazooka and
  Colloidal Phaser at distances 0–3). Deflector applies before range
  dropoff; capacitors multiply (P-12, P-14).
- **Gatling**: one shot hits every enemy stack in range with full damage
  and no dropoff; a station's Gatling hit two attacking stacks at range 3
  in one shot (starbase range +1) (P-13).
- **Sappers** hit only shields: no hit record on unshielded freighters
  while a shielded stack was present, and hits on the shielded stack
  removed shields only (P-15).
- Armor damage first destroys whole ships, already-damaged ships first
  (each costing its remaining armor). The rest is spread evenly over the
  survivors: rounded down when no surviving ship was already damaged;
  when some were, their existing damage is added first and the share is
  rounded up. The record shows per-ship damage in 1/500ths of armor,
  rounded up (P-22, P-23).
  Beams hit shields before armor; a torpedo hit splits half to shields,
  half to armor.
- Regenerating Shields: at the start of each later round a stack whose
  shields are above 0 regains 10% of its maximum (+7 per ship); none once
  shields reach 0 (CB-008, 39 hits) (P-24).
- Range dropoff was exercised: beam hits at distances 0–3, torpedo hits at
  2–5.

### Who fights (MEASURED)

- No battle when both sides' plans attack nobody (P-5), or when the only
  side whose plan attacks enemies is unarmed (CB-006).
- A stack whose plan attacks nobody fires back once a battle has started
  (P-6).
- **Lone starbases did not start battles — CONTRADICTED the round-1
  prediction; the binary reading now agrees (only fleets start battles,
  see round 2).** In all six tested cases an armed starbase whose owner had no
  armed fleet there started no battle with an enemy fleet in orbit:
  - CB-002 C9: Laser station, plan 0 attack everyone; unarmed visitor
    attacking nobody.
  - CB-002 C10: Gatling station, plan 0 enemies; unarmed visitors
    attacking nobody.
  - CB-003 S2 / CB-004 S2: Laser station, plan 0 enemies / neutrals and
    enemies; unarmed visitor attacking nobody.
  - CB-006: Laser station, plan 0 enemies, armed visitor attacking nobody;
    Gatling station, plan 0 enemies, unarmed visitor attacking enemies.
  The binary reading predicted that plan 0 "enemies" makes the station
  attack. Other plan settings, armed visitors that attack, and other
  hulls were not tested, so this is not a general rule. P-29 (plan 0
  "everyone" may fail) cannot be tested as stated.
- **Starbases in a battle started by fleets.** When fleets fought at a
  planet, its starbase appeared as a token: an armed station whose owner's
  fleet started the battle (CB-003/004 S1, never in range, did not fire);
  an armed Gatling station attacked by enemy fleets (CB-005, fired); and an
  **unarmed** station at a planet where its owner's fleet attacked enemy
  fleets (CB-005). The unarmed case CONTRADICTS P-4 ("unarmed starbase is
  not a token").

### Salvage (CONFIRMED, one case)

Destroyed ships leave one salvage object per battle location. In CB-001
B1, three kill events (3, 4 and 3 Small Freighters; 4 Ironium,
5 Germanium each at tech 26) left 10 Ironium and 13 Germanium:
per kill event, a third of the destroyed ships' mineral cost, then a
quarter of that lost (integer at each step) (P-26).

### Round 2 (CB-009 to CB-019)

Pinned RNG, tech 26 unless stated. All hits replayed through the
stars-decomp checker at 4a8c82b except where noted below.

- **One kill per missile (Q-8, CONFIRMED).** 202 Jihads at 20% (40 hits
  of 170 = 6800, enough armor for 272 Small Freighters) killed 202 per
  salvo in four salvos, leaving survivors undamaged (CB-009 K1).
- **Carried beam damage is rescaled (Q-7, CONFIRMED).** After a beam
  destroys a stack, the next stack in the same action receives damage
  from R' = min(R − 1, R·L/dp) passed again through deflector and range
  dropoff (L leftover, dp the damage that was applied). A checker using
  only this rule replayed all 59 hits of CB-010 (Colloidal Phaser frigates
  vs Beam-Deflector frigates); carrying the raw leftover mismatched 8.
- **Beam target order (Q-6, CONFIRMED in 4 cases × 2 seeds).** Among
  stacks in range the attacker chose: a 5-ship stack over a 3-ship stack
  of the same design; the more expensive design at equal armor (Fuel Tank
  frigates); an already damaged stack over a fresh one; the lower token
  index between identical stacks. In one of the two seeds or both, the
  first three choices went to the stack with the higher token index, so
  they are not the index rule.
- **Torpedo misses against shields (Q-14, CONFIRMED).** A salvo that
  misses a shielded target writes a miss record (flags 0xc4) before the
  hit record; the misses do floor(misses × damage / 8) to shields in
  total (Beta 12: 14 misses → 21).
- **Starbases join, never start (Q-1, CONFIRMED).** With player 1 seeing
  player 0 as neutral, player 1's armed fleet (attack enemies) at
  player 0's Laser Station planet fought, and the station fired, when
  player 0's plan 0 was "enemies". No battle when the station was
  unarmed, when the visitor was unarmed, or when plan 0 was "nobody".
- **Plan 0 "everyone" / "player 1" (Q-2, CONTRADICTED).** The same S1
  battle happened, identical to the "enemies" case, with plan 0
  "everyone" (three seeds) and "player 1" (one seed). The binary reading
  predicted that usually no battle happens.
- **Station targets ignore plan 0 (Q-3, CONFIRMED).** With plan 0
  primary "starbase" and no secondary, the Laser Station fired at enemy
  frigates (CB-016).
- **An unarmed station is an armed-class target (Q-4, CONFIRMED).**
  Frigates with primary "unarmed", no secondary, produced a battle record
  with no hits against an unarmed station; with primary "armed" they
  destroyed it.
- **Starbase damage and loss (Q-5, CONFIRMED in part).** An unarmed Space
  Station (400 shields) took 100-damage laser hits: shields first, then
  90, 190, …, 490 per 500 of armor, destroyed at the next hit; a Bare
  Orbital Fort died in one hit. Both planets had no starbase after the
  turn. Queued ships were not tested.
- **Starbase beam dropoff (MEASURED, against the checker).** A Laser
  Station (8 Lasers per slot, 80 damage) hit frigates at distance 2 with
  64 per slot: 80% dropoff, i.e. distance × 10 / 1, using the Laser's own
  range, although the station's reach is range + 1. The stars-decomp
  checker at 4a8c82b mismatched these hits and the hits on the unarmed
  station (CB-011..013, CB-016); the values above are the record's.
- **Salvage at a planet (Q-13, CONFIRMED, one case each).** Six Small
  Freighters destroyed in one kill event left no salvage object; the
  planet surface gained 6 Ironium, 8 Germanium with a starbase (⅓ of
  cost × 8/10) and 4 Ironium, 5 Germanium without (× 5/10).
- **Repair (Q-12, CONFIRMED, 10 locations × 2 turns).** Per turn, in
  1/500 of armor per damaged ship: 10 stationary in deep space, 15
  orbiting another player's or an unowned planet, 25 at an own planet
  without starbase, 40 with an Orbital Fort, 100 with a Space Dock or
  Space Station; a Fuel Transport in the fleet adds 25 and a Super-Fuel
  Xport 50. The damaged-ship percentage stayed 100%.
- **Tech from battle (Q-11, MEASURED).** Player 0 (weapons 3, research
  0%, every other field 26) destroyed three frigates armed with Colloidal
  Phasers. Without a battle weapons stayed 3; with it, weapons was 4 in
  the 2401 file for 4 of 6 distinct random streams (2 streams gained
  nothing), with every research accumulator 0. A random gain matches the
  binary reading; the level rising in the same generation contradicts
  its "the level stays until the next generation's research update".

### Resolved reconciliation

- Energy Dampener frigate token mass: the battle record shows 19 (CB-002
  C8), which is the game's part-table sum (Frigate 8 + Long Hump 6 9 +
  Energy Dampener 2). An earlier figure of 23 came from a binary-analysis
  tool that defaulted to 3 dampeners in the slot; it was not a game
  discrepancy.

### Not tested

Stack movement order by weight (P-9), queued ships lost with a starbase
(P-25), the "moved" repair rate, starbase repair, salvage at more than one
point (E-8), three or more players, minefields, bombing and invasion.
