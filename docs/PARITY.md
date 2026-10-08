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
- ~~Carry handling with habitability and crowding modifiers.~~ Resolved:
  CONFIRMED in `KERNEL.md` "Population growth" (KX-002 H3–H6, P1–P3,
  G1–G3; KB-1A).
- ~~Whether the carry persists across changes to the effective growth
  rate.~~ Resolved: the carry is a per-planet byte. Each year's rule adds
  that year's remainder to it, whatever `g` is (`KERNEL.md`; KX-002
  vectors start from a non-zero carry).
- ~~Order of operations: habitability, growth rate, crowding, carry.~~
  Resolved: `g = G·hab`, then crowding, then `t`, `q`, `r` and the carry
  (`KERNEL.md` "Population growth", CONFIRMED).
- ~~Behavior at 100% capacity.~~ Resolved: from `max` to `max + 10` the
  population and carry are frozen (KX-002 G2, KB-1A planet 13).
- ~~Overcrowding death curve.~~ Resolved: `g = 4·max(−300, trunc(c/−10) +
  99)` (KX-002 G1), CONFIRMED.
- ~~Lifecycle of `excessPop`.~~ Resolved for the cases that change it: an
  emptied or captured planet keeps its carry (`TAKEOVER.md`, T-27), and
  hostile deaths use it (KX-002 H5, H6). Growth and deaths run only on
  owned planets with population.

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

Observation (A5–A7, 2408):

| Case | Observed | vs prediction |
|---|---|---|
| A5 | factories 2, mines 2; minerals 108/108/0; queue Auto Alchemy ×1, Auto Factories ×2; research 70; alchemy (8), factories, mines, "completed its orders" | match |
| A6 | queue Mineral Alchemy ×1 @1%, Auto Alchemy ×1, Auto Factories ×2; minerals 100/100/0; research 0 | match (binary) |
| A7 | queue Auto Factories ×2, Mine ×1 @39%; research 0; no events | match (binary) |

So an Auto Alchemy prefix stays in front of an auto item after that item
builds (A5), and an auto item counts as mineral-blocked whenever any
mineral is short, even when resources give the lower percentage (A6 with
a prefix, A7 without). Tie-breaking (resources vs a mineral, mineral vs
mineral) is not observed; it rests on the binary reading.

Not covered: terraforming costs (Total Terraforming, Claim Adjuster),
packets, scanners, starbase and ship costs, the tamper check's points
formula.

Evidence: private `bfaber-centaur/stars-oracle-apparatus`,
`evidence/kx001/` (edited inputs, every resulting file, decoded dumps, the
model and a SHA-256 manifest). Tooling: `scripts/oracle/edit-turn` with the
race keys of `scripts/oracle/hst-edit` (`ORACLE.md`).

## Kernel Rule Sweep

### KX-002 — untested BINARY-ONLY kernel rules

Status: MEASURED (25 cases, 2026-10-07). Predictions were committed
(`35e057e`) before any case ran; results follow them. 24 of 25 matched in
every predicted field; G1 (overcrowding) did not, and the published rule
was wrong by a factor of 2 (below).

Question: which `KERNEL.md` rules still tagged BINARY-ONLY hold in the
original, for the rules a playable game exercises every year? Chosen from a
sweep of `KERNEL.md` on main (`96fd2e7`): habitability off the race
centre, maximum population with HE, JOAT and OBRM, growth outside the one
confirmed branch (`g < 1000`, overcrowding, within 10 of max, zero
growth, hostile deaths), effective population above max, installation
caps below 100% habitability, multi-turn mining with many mines and a
homeworld concentration below 30, research cost settings, several
level-ups in a year, next-field switching, Generalized Research, the
level-26 cap, and terraforming (cost, Total Terraforming, range limits
and axis choice). Remote mining and scrap belong to the takeover corpus;
production rules PQ-001 confirmed are not repeated.

Method: as KX-001. Each case edits PG001 2407 (`registered` snapshot;
Endeavor, planet 7, the player's homeworld; race centre 50, range 15–85 on
every axis, growth 10%, every stat 10 except mine cost 5) with
`scripts/oracle/edit-turn` and generates one year (N2: three). Every case
sets the growth carry to 0 unless stated. Population is in units of 100
colonists. Predictions come from a script that implements the `KERNEL.md`
rules as written (private evidence, `tools/kx2_model.py`); the terraform,
cap and production rows are worked by hand from `KERNEL.md` "Production"
and the terraforming rules in the binary reading (stated in each row).

Races must stay inside the race wizard's point budget (`KERNEL.md`, "Item
costs"). Cases that change the race (HE, JOAT, OBRM, TT, GR, research
costs) are checked for message 0x117 and a changed race line; a case that
trips it is void and reported as such.

Nothing predicted below depends on a random draw: the N2 mineral outputs
are exact multiples of 100 kT, so the `+1` draw never happens, and the
other cases' mineral deltas are not predicted.

#### Population and habitability (no production queue, so all resources go to research)

| Case | Edits | hab | max | Predicted 2408 pop, carry | Discriminates |
|---|---|---:|---:|---|---|
| H1 | env 60/50/50, pop 1000 | 92 | 9,200 | 1092, 0 | hab vector 92 (each hab point is 10 units here) |
| H2 | env 70/70/50, pop 1000 | 58 | 5,800 | 1058, 0 | two axes off centre |
| H3 | env 80/80/80, pop 300 | 3 | 500 | 300, 24 | hab 3; max 500 below hab 5; crowded `g < 1000` branch (`g = 30 → 8`) |
| H4 | env 85/50/50, pop 3000 | 41 | 4,100 | 3015, 60 | edge of range; crowded `g < 1000` (`g = 410 → 52`) |
| H5 | env 90/50/50, pop 1000 | −5 | 500 | 995, 0 | hostile deaths |
| H6 | env 10/95/50, pop 1234, carry 10 | −15 | 500 | 1215, 59 | hostile deaths with a carry borrow |
| G1 | pop 12000 | 100 | 10,000 | 11949, 60 | overcrowded deaths |
| G2 | pop 10005 | 100 | 10,000 | 10005, 0 | within 10 of max: frozen |
| G3 | pop 9995 | 100 | 10,000 | 9995, 1 | zero growth adds 1 to the carry |
| P1 | PRT HE, pop 3000 | 100 | 5,000 | 3168, 0 | HE: growth doubled (`g = 2000 → 560`) and max halved; with max 10,000 it would be 3522 |
| P2 | PRT JOAT, pop 10005 | 100 | 12,000 | 10045, 2 | JOAT +20% (an ordinary race is frozen at 10005) |
| P3 | LRT OBRM, pop 10005 | 100 | 11,000 | 10015, 0 | OBRM +10% |

Research the same year (current field energy, levels 2/0/0/0/5/0, energy
accumulated 65; resources `trunc(E/10) + 10` from 10 factories, with `E`
the effective population):

| Case | Research | Energy level, accumulated | Discriminates |
|---|---:|---|---|
| H1, H2 | 110 | 2, 175 | |
| H3 | 40 | 2, 105 | |
| H4, P1 | 310 | 3, 175 | |
| H5 | 85 | 2, 150 | hostile planet above its max 500: `E = 500 + trunc(500/2) = 750` (not 1000) |
| H6 | 96 | 2, 161 | same, `E = 500 + trunc(734/2) = 867` |
| G1 | 1110 | 5, 255 | `E = 10000 + trunc(2000/2) = 11000` (1210 if `E = P`); three level-ups in one year |
| G2, P2, P3 | 1010 | 5, 155 | |
| G3 | 1009 | 5, 154 | |

#### Mining over three years

N2: pop 10000 (frozen at max, so the same every year), 1000 mines (all
working: maximum and operable mines are both 1000), concentrations set to
20/113/84 (ironium below the homeworld floor of 30), fractions as in PG001
(242/86/157). Predicted:

| Year | Surface gain Fe/Bo/Ge | Concentration | Fraction (stored, 0 = 256) | Energy level, accumulated |
|---:|---|---|---|---|
| 2408 | +300/+1130/+840 | 20/104/79 | 88/73/34 | 5, 155 |
| 2409 | +300/+1040/+790 | 19/96/74 | 189/11/77 | 6, 515 |
| 2410 | +300/+960/+740 | 19/88/70 | 35/241/11 | 7, 525 |

What it tests: the floor (ironium output from 30, not 20: +300, not +200,
while the stored value keeps falling, 20 → 19), depletion from the floored
`prod` (2408 ironium fraction 88; 139 without the floor), the `cc = 25`
clamp below 25 (118 with `cc = 20`), several concentration points in one
year, and `cc` re-evaluated after each point (germanium 84 → 79 in one
year; with `cc` fixed at 84 for the year the 2408 fraction would differ).
Each later year starts from the files the earlier year wrote.

#### Research settings (no production queue)

| Case | Edits | Research | Predicted levels; accumulated; field byte | Discriminates |
|---|---|---:|---|---|
| R1 | energy "costs 75% more", biotech level 1, pop 2930 | 303 | energy 3; energy 0; current energy, next same | level 3 costs `2·210 − trunc(210/4) = 368`, exactly 65 + 303 (rounding the other way leaves 1) |
| R2 | energy "costs 50% less", weapons "costs 75% more", pop 9900 | 1000 | energy 6; energy 280 | halved costs 100, 145, 215, 325; four level-ups |
| R3 | next field "lowest", pop 3900 | 400 | 3/1/0/0/5/0; propulsion 135, others 0; current propulsion, next "lowest" | leftover chains energy → weapons (lowest, first of the tied zeros) → propulsion, and "lowest" stays set |
| R4 | next field biotech, pop 2250 | 235 | energy 3; biotech 100, energy 0; current biotech, next "same" | leftover moves to the chosen field, and the choice resets |
| R5 | LRT GR, pop 2010 | 211 | levels unchanged; 171/32/32/32/32/32 | GR split: current `trunc(212/2) = 106`, others `trunc((633+19)/20) = 32` |
| R6 | energy level 26, pop 2010 | 211 | energy 26; energy still 65 | research into a level-26 field is lost |

#### Installation caps below 100% habitability (production queue; PQ-001 common edits: mines 0, factories 0, defenses 10, research budget 0%, minerals 500/500/500)

| Case | Edits | Caps | Predicted 2408 | Discriminates |
|---|---|---|---|---|
| C1 | env 70/70/50 (hab 58), pop 1000, Factory ×700 | max factories 580; operable 105 | order cut to 580 (message 0x12a); 10 factories; Ge 460; Factory ×570 @9%; research 0 | `max(10, trunc(5800·10/100))` (×690 if the cap were 1000) |
| C2 | env 80/80/80 (hab 3), pop 500, defenses 0, Defenses ×50 | max defenses 12; operable 12 | cut to 12 (0x12a); 3 defenses; minerals 484 each; Defenses ×9 @39%; research 0 | `min(100, max(10, 4·hab))` (×47 if the cap were 100) |
| C3 | env 85/50/50 (hab 41), pop 1000, Mine ×999 | max mines 410; operable 104 | cut to 410 (0x12a); 20 mines; Mine ×390 @19%; research 0 | `max(10, trunc(4100·10/100))` |

#### Terraforming (production queue; same common edits)

Rule being tested (binary reading, not yet in `KERNEL.md`): each
Terraform Environment unit moves one axis one click toward the race
centre. The reachable range on an axis is the planet's original value ±
the best terraform the owner has for it (Total Terraforming counts for all
three axes), clipped to 1–99 and stopping at the centre. Each unit picks
the axis whose remaining range gives the largest average hab change per
click (first axis on ties). An order larger than the clicks left is cut
(message 0x12f). Cost 100 resources, 70 with TT.

| Case | Edits | Range | Predicted 2408 | Discriminates |
|---|---|---|---|---|
| T1 | env and original 60/50/50, propulsion 1, biotech 1 (Gravity Terraform ±3), pop 2000 (200 resources), Terraform ×5 | gravity 60 → 57: 3 clicks | order cut to 3; 2 units: env 58/50/50; Terraform ×1 @0%; research 0 | cost 100; range ±3; cut to capacity |
| T2 | LRT TT, env and original 60/45/50, pop 2000 (hab 87), Terraform ×5 | gravity 3, temperature 3: 6 clicks | not cut; 2 units, both temperature: env 60/47/50; Terraform ×3 @86%; research 0 | TT cost 70 (with 100: env 60/47/50, ×3 @0%); TT ±3 on all axes; axis choice (temperature scores 101 a click vs gravity 67) |
| T3 | env 58/50/50, original 60/50/50, propulsion 1, biotech 1, pop 2000, Terraform ×5 | gravity down to 57 (60 − 3): 1 click | cut to 1; env 57/50/50; order done; research 100 | range measured from the original value, not the current one |

#### Results

Observed 2408 (2408–2410 for N2) in the generated `.HST`, with the `.M1`
messages. No case got message 0x117, and every edited race was unchanged
after the year, so all race edits were within the point budget.

| Case | Observed | vs prediction |
|---|---|---|
| H1 | pop 1092 carry 0; research 110; energy 2, 175 | match |
| H2 | 1058, 0; 110; 2, 175 | match |
| H3 | 300, 24; 40; 2, 105 | match |
| H4 | 3015, 60; 310; 3, 175 | match |
| H5 | 995, 0; 85; 2, 150 | match |
| H6 | 1215, 59; 96; 2, 161 | match |
| G1 | **11899, 20**; 1110; 5, 255 | population **differs** (predicted 11949, 60); research matches |
| G2 | 10005, 0; 1010; 5, 155 | match |
| G3 | 9995, 1; 1009; 5, 154 | match |
| P1 (HE) | 3168, 0; 310; 3, 175 | match |
| P2 (JOAT) | 10045, 2; 1010; 5, 155 | match |
| P3 (OBRM) | 10015, 0; 1010; 5, 155 | match |
| N2 | every surface gain, concentration and fraction in the table, all three years; research 1010 a year; energy 5/155, 6/515, 7/525 | match |
| R1 | 303; levels 3/0/0/0/5/1; accumulated all 0 | match |
| R2 | 1000; energy 6, 280; level-up messages for energy 3, 4, 5, 6 | match |
| R3 | 400; levels 3/1/0/0/5/0; propulsion 135, others 0; current propulsion, next "lowest" | match |
| R4 | 235; energy 3; biotech 100, energy 0; current biotech, next "same" | match |
| R5 (GR) | 211; 171/32/32/32/32/32 | match |
| R6 | 211; energy 26, still 65 | match |
| C1 | message 0x12a; 10 factories; Ge 460; Factory ×570 @9%; research 0 | match |
| C2 | 0x12a; 3 defenses; 484/484/484; Defenses ×9 @39%; research 0 | match |
| C3 | 0x12a; 20 mines; Mine ×390 @19%; research 0 | match |
| T1 | message 0x12f; two 0x7b; env 58/50/50; Terraform ×1 @0%; research 0 | match |
| T2 (TT) | no cut; two 0x7b; env 60/47/50; Terraform ×3 @86%; research 0 | match |
| T3 | 0x12f; env 57/50/50; queue empty; research 100 | match |

G1: 12,000 units at max 10,000 lost 101 units and the carry went 0 → 20,
which is `t = −10080`, i.e. `g = −84` = `4·(trunc(1200/−10) + 99)`. The
published rule had `2·`. Re-reading the binary's population-change
routine: the overcrowded branch doubles its value and then joins the
quantized crowded branch at its final doubling, so the result is doubled
twice. `KERNEL.md` now gives `4·max(−300, trunc(c/−10) + 99)` (deaths of
at most 12% a year) as CONFIRMED at this one point. The `−300` floor
itself is not reached by any case (it needs a population above 4 times
the maximum).

Interpretation:

- Habitability, maximum population (including HE, JOAT, OBRM and the
  floor of 500), every growth branch, hostile deaths and effective
  population above max now have an oracle point each.
- Mining: the homeworld floor applies to output and depletion while the
  stored concentration keeps falling below 30, `cc` follows the stored
  value within a year, and several points can go in one year.
- Research: both cost settings (75% more rounds up), several level-ups a
  year, switching to an explicit field or to the lowest field (with a
  chain in one year), the GR split and the level-26 loss.
- Installation caps below 100% habitability and the terraform rules
  (cost, TT, range from the original value, capacity cut, axis score) are
  as read.

Still BINARY-ONLY after KX-002: the 15-click hostile cap, HE/JOAT/OBRM
combined, the `2·max` limit on effective population, the `cc = 10`
clamp, slower tech, the level-10 cap for capped players, Super Stealth
research stealing, Claim Adjuster, auto terraform items, orbital
adjusters, and ties in the terraform axis choice. Scores have no public
rule yet, so there was nothing to test.

Evidence: private `bfaber-centaur/stars-oracle-apparatus`,
`evidence/kx002/` (edited inputs, every resulting file, decoded dumps, the
model and a SHA-256 manifest). Tooling: `scripts/oracle/edit-turn` with
the `hst-edit` keys `field=` and `conc=` added for this corpus.

### KX-003 — scores, victory conditions, slower tech, Claim Adjuster, Super Stealth

Status: MEASURED (5 runs, 2026-10-07). Every predicted value held, except
a side note in S1 (player 1's research, a prediction-script error below)
and S3, where the Super Stealth race was over budget; S3L repeated it
legally and matched. Predictions were committed (this work's first commit) before any
case ran. Correction
before S2 and S3 ran (after S1): the first prediction commit fed research
with resources after growth, a script error; `KERNEL.md` says research
uses this year's resources before growth. S2's populations were changed
to keep the case discriminating and the S2/S3 research figures
recomputed; no rule changed. S1's score predictions are unaffected (the
score uses resources after growth).

Question: how does the original score a player and test the victory
conditions, which a playable game needs and `KERNEL.md` does not describe;
and do the remaining BINARY-ONLY research and terraforming rules (slower
tech, Claim Adjuster, Super Stealth research stealing) hold?

Method: Combat Lab two-player starts (game 82222, `experiments/kx003/*.spec`
built with `tools/fleetlab/combatlab`), generated with
`tools/fleetlab/pinned-turn`. Game options and victory conditions are set
in the game record of `CB.XY` with the new `hst-edit xy` command; the
edited `CB.XY` goes in the run's base directory. Both races: JOAT (except
S3), centre 50 and range 15–85 on every axis, growth 15%, every research
cost normal. Population is in units of 100 colonists. Scores are read from
the score block (type 45) in each player's `.M` file, which `hst-edit
dump` now prints as hex. Predictions come from a script implementing
`KERNEL.md` growth and resources plus the score rule below (private
evidence, `tools/`).

#### Score rule under test (from the binary reading)

Computed per player once a year, after production and growth:

- **Planets:** each owned planet scores `min(6, ceil(colonists/100000))` (`ceil(pop/1000)` in units of 100).
- **Starbases:** 3 for each owned starbase whose hull has dock capacity
  (an Orbital Fort scores 0; a Space Station scores 3).
- **Resources:** `trunc(R/30)`, R = the year's resources over all owned
  planets.
- **Tech:** per field at level L: L for L ≤ 3, `2L − 3` for 4–6,
  `3(L − 3)` for 7–9, `4L − 18` for 10 and above.
- **Ships:** every ship in the player's fleets is unarmed (power 0),
  an escort (power below 2000) or a capital ship (2000 and above). With N
  owned planets, U unarmed, E escorts and C capital ships:
  `trunc(min(N, U)/2) + 2·min(N, E) + trunc(8·N·C/(N + C))` (last term 0
  when C = 0).
- **Power of a design:** beams `(range + 3)·damage·count/4` (÷3 for
  sappers), multiplied by the capacitor factor (each capacitor multiplies
  1000 by `(100 + pct)/100`; if not 1000, `beam·min(255, f/10)/100`), then
  `beam + beam·(speed − 4)/10` with the COMBAT.md battle speed; torpedoes
  and missiles `(range − 2)·damage·count/2`; bombs
  `(kill% in tenths + installations killed)·count·2`. The sum.

Victory conditions (game record bytes `0x14 + i`, bit 7 enabled, low
7 bits v): 0 owns `(v + 4)·5`% of all planets, counted as
`round(total·pct/100)`; 1/2 tech level `v + 8` in `v + 2` fields;
3 score `(v + 1)·1000`; 4 lead `(v + 2)·10`% over second place;
5 resources `(v + 1)·10` thousand; 6 capital ships `(v + 1)·10`;
7 highest score after `(v + 3)·10` years; 8 the number needed; 9 minimum
years `(v + 3)·10`. The yearly record holds a flag per condition met,
whether or not the condition is enabled: 0x40 planets, 0x80 tech, 0x100
score, 0x200 lead, 0x400 resources, 0x800 capital ships, 0x1000 highest
score; low 5 bits the player, 0x20 always set. Rank is 1 + the number of
strictly higher scores.

#### Predictions

S1 (`kx3s1.spec`; victory bytes `80 81 81 00 80 00 00 00 01 00`:
planets 20% enabled, tech level 9 in 3 fields enabled, score 1000 off,
lead 20% enabled, resources 10k off, capital ships 10 **off**, highest
score off, 1 needed, 30 minimum years). Player 0: tech 26 everywhere,
homeworld 250 with a Space Station, planets of 871 (Orbital Fort), 870
(Space Station), 5300 and 7100, 7 unarmed scouts, 2 Omega4 (4 Omega
torpedoes, power 1896, escort), 1 Mini Bomber with 2 Cherry bombs (140,
escort), 10 Omega5 (5 torpedoes, 2370, capital). Player 1: tech 3, 4, 6,
7, 9, 10; homeworld 250 with an Orbital Fort, planets of 999, 1 and 3000,
5 X-Ray scouts (escort), 1 unarmed scout.

| Player | Planets | Starbases | Resources | Tech | Ships | Score | Flags word | Rank |
|---|---|---|---|---|---|---:|---|---:|
| 0 | 1+2+1+6+6 = 16 | 2 → 6 | 1552 → 51 | 6·86 = 516 | 2 + 6 + 26 = 34 | **623** | `0x0ae0` (planets 5 ≥ 5, tech, lead, capital ships though disabled) | 1 |
| 1 | 1+2+1+4 = 8 | 0 | 498 → 16 | 69 (level sum 39) | 0 + 8 = 8 | **101** | `0x0021` (4 planets < 5; 4 would pass with truncation) | 2 |

Populations after growth: 287, 1001, 1000, 5739, 7412 and 287, 1148, 1,
3450. No victory: the 30-year minimum is not reached. Player 1's research
goes to energy (cost 600), no level.

S2 (`kx3s2.spec`, slower tech: game record byte `0x10` = `0x82`; two
years). Rule under test: the stored accumulation S is half-scale; each
year `L = 2S + research`, a level costs twice the normal cost, and what
is left is stored as `ceil(L/2)`. Both players at level 3 in every field,
researching energy with all resources (no queue).

| Player | Year | Research | Energy level | Stored | Normal-speed result |
|---|---|---:|---:|---:|---|
| 0 (planet 4000) | 2401 | 435 | 3 | 218 (`ceil(435/2)`) | level 4, 45 |
| 0 | 2402 | 485 | 4 | 71 (`436 + 485 − 780 = 141`) | |
| 1 (planet 9020) | 2401 | 937 | 4 | 79 (`937 − 780 = 157`) | level 5, 17 |
| 1 | 2402 | 954 | 5 | 26 (`158 + 954 − 1060 = 52`) | |

If S were not doubled, player 0 would stay at level 3 in 2402 (`218 + 485
< 780`).

S3 (`kx3s3.spec`, player 0 Claim Adjuster, player 1 Super Stealth, both
tech 3; player 0 researches weapons, player 1 energy). JOAT → CA is known
legal; JOAT → SS is checked for message 0x117.

- Claim Adjuster (rule under test: after production each CA planet's
  axes move in one step to the full reachable value, `orig ± t` toward the
  centre, here t = 3 from the ±3 parts): planet 0 60/42/56 (original the
  same) → **57/45/53**; planet 1 58/50/50 (original 60) → **57/50/50**;
  no Terraform items built, no resources spent. The original value can
  drift one click toward the centre at random (a 1-in-10 roll per planet
  and year, then a population-weighted roll); if it does on an axis,
  that axis ends one click further.
- Super Stealth (rule under test: after all players research, an SS
  player gains, per field, `trunc(trunc(spent/players)/2)` where spent
  is every player's research in that field, its own included, when that
  is more than 1; message 0x159): player 0 spends 355 on weapons (no level),
  player 1 spends 95 on energy. Player 1 ends with energy **118**
  (95 + 23) and weapons **88**. Excluding its own research would give
  energy 95.

#### Results

| Run | Predicted | Observed | |
|---|---|---|---|
| S1 player 0 record | score 623, R 1552, 5 planets, 2 starbases, U/E/C 7/3/10, tech sum 156, flags `0x0ae0`, rank 1 | the same | OK |
| S1 player 1 record | score 101, R 498, 4 planets, 0 starbases, U/E/C 1/5/0, tech sum 39, flags `0x0021`, rank 2 | the same | OK |
| S1 player 1 research | 498 into energy | 435 | prediction-script error: research uses resources before growth (`KERNEL.md`), the script used the after-growth figure; found here and corrected before S2/S3 ran (the second commit) |
| S2 2401 | P0 3 / 218, P1 4 / 79 | P0 3 / 218, P1 4 / 79 | OK |
| S2 2402 | P0 4 / 71, P1 5 / 26 | P0 4 / 71, P1 5 / 26 | OK |
| S3 CA planets | 57/45/53, 57/50/50; originals unchanged | the same | OK |
| S3 SS | energy 118, weapons 88 | energy 56, weapons 88; message 0x117 and the SS race's colonists-per-resource raised from 10 to 24 | void: JOAT → SS is over the race budget. Its own research (45) still gave 45 + 11 = 56, which fits the rule |
| S3L (S3 + LRTs `0x1b80` for player 1) | energy 118, weapons 88; CA as S3 | energy 118, weapons 88, two messages 0x159 (23 energy, 88 weapons); CA 57/45/53 and 57/50/50; no 0x117 | OK |

S2 and S3L's score records also follow the score rule (worked from their
populations, levels and starbases): S2 2401 43 and 61, 2402 46 and 64;
S3L 40 and 26. In every run each player's `.M` held only that player's
score record.

Interpretation:

- The score rule, the class boundaries for ships (power 1896 escort,
  2370 capital), the starbase dock rule (an Orbital Fort scores 0), the
  planet cap of 6 and the use of after-growth resources hold. Rank is
  1 + the number of higher scores.
- Victory-condition flags are set when a condition is met even if it is
  disabled (capital ships, disabled in S1, flagged). The planets threshold
  rounds (5 of 24 at 20%; 4 did not count).
- Slower tech stores research at half scale and doubles it back the next
  year (S2 player 0 levelled in 2402 only because of the doubling).
- Super Stealth steals half of each field's per-player average,
  including its own research.
- Claim Adjuster planets jump to the full reachable environment at the
  end of the year; growth that year used the old environment.

Still BINARY-ONLY after KX-003: capacitor, sapper and speed adjustments
to power; the score, resources and highest-score flags; deciding the game
(dead players, minimum years, number needed, win messages); CA original
drift; CA's half-price terraform items; slower tech with GR or stolen
research.

Evidence: private `bfaber-centaur/stars-oracle-apparatus`,
`evidence/kx003/` (specs, edited `CB.XY`, every resulting file, dumps,
the model and a SHA-256 manifest). Tooling: `hst-edit xy` and the score
and game-record dump lines.

### KX-004 — random events and turn-time game options

Status: CONFIRMED (comets, climate change, new minerals, public scores,
random events off), with one draw-order correction (two draws, not three,
for the struck-mineral shuffle) found in S1 and applied before S2–S5.
Predictions were committed before any case ran; round 2 predictions
before S2–S4 were examined. Rules: `KERNEL.md` "Random events" and "Game
options during a turn".

Question: what do the yearly random events (comet strikes, planetary
climate change, new mineral deposits) do, when, and how often; and what do
the game options change during a turn? Mystery Trader and wormholes are
in `OBJECTS.md`, creation-time options (maximum minerals, BBS, clumping)
in `UNIVERSE.md`, and slower tech in `KERNEL.md` (KX-003).

Method: Combat Lab game CB (tiny, 24 planets, two JOAT players), start
`experiments/kx004/kx4e1.spec`: planets 0–7 and 9–16 owned (population
30, 45, 600 or 3000; environment 50/50/50; no mines, factories or
defenses; queue Auto Factories ×5, Factory ×1, design 0 ×1), 18–23
unowned, homeworlds 8 and 17. With no mines, an owned planet's
concentrations, surface minerals and environment change only through
events. `experiments/kx004/run-kx4.sh` generates one year per
`pinned-turn` process with cycles `15000 + 37·year` (a different random
stream each year).

- **E1:** game option byte `0x40` (random events on, public scores on),
  300 years (2400 → 2700) planned; stopped after 148 (see Results).
- **E0 (control):** option byte `0x80` (random events off, public scores
  off), 40 years.

Messages are read from each player's `.M` event list (format in
`ORACLE.md`).

#### Rules under test (from the binary reading)

At the end of production, after research, when random events are on, in
this order:

1. **Comet strike.** With chance 1/20 a uniformly random planet (any
   owner, or none) is chosen. Nothing happens before year index 10, or
   if the planet is owned with more than 5,000 colonists and the year
   index is below 20. Size `e` = 0–3 (small, medium, large, huge), equally
   likely.
   - Every player gets a message naming the planet. A non-AR owner's
     message says the colonists killed (25/45/65/85%) and names `e + 1`
     environment axes (all three for e = 3).
   - A non-AR owner loses `trunc(P·(20e + 25)/100)` of its population P
     (after this year's growth).
   - `min(e + 1, 3)` distinct random minerals each gain concentration
     `50 + rand(50)` (huge: a further `15 + rand(15)`), capped at 200.
   - Surface minerals: each struck mineral gains
     `trunc((50 + rand(250) + 3000 + rand(17000))/16)` kT (190–1268); every
     other mineral gains `trunc((50 + rand(250))/16)` (3–18).
   - Environment: axes gravity, then temperature, then radiation, the
     first `min(e + 1, 3)` of them (not a random choice), each move by
     `±(3 + rand(3))` (huge: `±(6 + rand(3) + rand(3))`, 6–10), the current
     and the original value alike, clamped to 1–99.
   - The production queue loses every item except the auto items (Auto
     Mines, Factories, Defenses, Alchemy, Min/Max Terraform, Mineral
     Packets), which keep their counts.
   - The owner's message names its axes from a separate random shuffle,
     so for small and medium comets it can name axes other than the ones
     that moved.
2. **Climate change.** With chance 1/20 a random planet, with the same
   protection (owned, more than 5,000 colonists, year index below 20); no
   year-10 minimum. One random axis moves by 4 or 5 (1/3 each) or 6, 7
   or 8 (1/9 each), sign random, current and original alike, clamped
   1–99. The owner (if any) gets a message naming the axis; its queue is
   cut to the auto items.
3. **New minerals.** With chance `1/(15 − size)` (1/15 on tiny) a random
   planet; nothing before year index 10. One random mineral: the owner
   (if any) gets a message even when nothing changes; the concentration
   rises by `5 + rand(15)` if it is below 180.

With random events off, none of these happen.

Public scores: a player's file contains another player's score record
only if the game is decided, that player is dead, or public scores are on
and the year index is at least 20.

#### Predictions

E1, per year, from each year's before and after files:

1. Every change of an owned planet's environment, concentration or
   surface minerals, and every change of an unowned planet's environment
   or concentration, is explained by exactly the events above. No other
   change happens.
2. Comets: none before 2410. For each, every player has a comet message
   for that planet; the size `e` from the message matches the number of
   struck minerals and moved axes and the ranges above. Gravity always
   moves, and temperature for `e ≥ 1`, whichever axes the message names.
   A non-AR owner's population is the year's growth result minus
   `trunc(G·(20e + 25)/100)`. The queue keeps only Auto Factories ×5.
3. Climate: one axis, `|Δ|` in {4, 5, 6, 7, 8} unless clamped, current and
   original alike; the owner's message names that axis; queue cut to Auto
   Factories ×5. None on a protected planet before 2420.
4. New minerals: none before 2410; one mineral `+5..+19`; an owner message
   for owned planets.
5. Frequencies are reported against the expected counts (about 14.5
   comets, 15 climate changes and 19 new-mineral events over 300 years);
   these counts test nothing exact.
6. Queues of owned planets without an event stay as set.
7. Public scores: each `.M` holds only its own score record through 2419
   and both from 2420 on.

E0: no environment or concentration change on any planet other than the
homeworlds' mining, no event message of these kinds, and only the own
score record in every year, 2420 on included.

#### Round 2 predictions: replaying the random stream

Committed after E1 years 1–148 and the first cycles sweep (S1), before S2,
S3 and S4 were examined.

E1 drew no event at all in 148 years (public scores matched). The reason
is the harness, not the game: a `pinned-turn` process seeds its random
stream from the startup tick, which under fixed cycles is
`trunc(k·54.925)` ms for a small k, so the cycles range E1 used
(15037–26100) reaches only two or three streams, and with no mines,
battles or other random draws the year's events always read the same
draw positions. ORACLE.md "Pinned battle RNG" already warned that few
streams are reachable. A year's events are therefore a deterministic
function of the startup tick, and the original's generator
(stars-decomp `tools/starsrng.py`) can be replayed for any tick.

S1 (one year from E1's 2430 state, 29 cycles values from 60000 to 3400)
gave three comets and two new-mineral events. Replaying each candidate
tick with the event rules located the events four draws after seeding
and showed one correction: the shuffle that picks the struck minerals
makes two draws, not three. With that, every S1 run's planet changes and
messages are reproduced exactly by exactly the tick its cycles value
reaches, including a large comet on the owned planet 17 (population 8110
after growth → 2839, `8110 − trunc(8110·65/100)`).

Predictions for the remaining runs, each from the replay at draw
position 4 (tiny universe, 24 planets):

- **S2** (2430 state, cycles `70000/k` for k = 20..80): each run shows
  exactly the events the replay gives for the tick it reaches, and none
  otherwise. Ticks with events at year index 30 include:
  - 1812: a medium comet on owned planet 11 (boranium +85, germanium
    +86; gravity +3, temperature +4; the owner's message names axes 1
    and 0), then new minerals on homeworld 8 (boranium +5);
  - 2032: a huge comet on owned planet 2 (concentrations +88/+84/+76;
    environment −7/+8/+10; the owner loses 85% of its grown population);
  - 3460: climate change on owned planet 7, radiation −6, owner message
    naming axis 2, queue cut to the auto items;
  - 4284: a small comet on owned planet 15 (ironium +86, gravity +4).
  Owned-planet comets: population `G − trunc(G·(20e + 25)/100)`, the
  queue keeps Auto Factories ×5 only.
- **S3** (E1's 2405 state, year index 5): cycles 10500 (tick 384): the
  comet is too early and changes nothing, but climate change still moves
  unowned planet 18's gravity by −6 (no year minimum). Ticks 109 and 768
  (cycles 35000, 5200): no new-mineral change before year index 10.
  Ticks 329, 659: no comet. Tick 1098 (cycles 3700): no change
  (protected and early).
- **S4** (E1's 2415 state, year index 15): ticks 329, 384 and 659 give the
  same unowned comets as at 2430 (year index ≥ 10 suffices); 109 and 768
  give the same new minerals; 1098 changes nothing: planet 17 has more
  than 5,000 colonists and the year index is below 20.

#### Results

S1–S5 used `experiments/kx004/sweep.sh` (one year from a saved E1 state
per cycles value).

| Run | State | Runs | Outcome |
|---|---|---|---|
| E0 | events off, public scores off | 40 years | no event message, no environment or concentration change; own score record only (2401–2440) — as predicted |
| E1 | events on, public scores on | 148 years (2401–2548) | public scores as predicted: own record only through 2419, both from 2420. No random event in any year: the cycles range reached only a few ticks (above) |
| S1 | 2430, cycles 60000–3400 | 29 | 3 comets, 1 large comet on owned planet 17, 2 new-mineral finds; all reproduced after the shuffle correction |
| S2 | 2430, cycles 3500–880 | 61 | medium comet on owned 11 with new minerals on 8, small comet on owned 15, 8 new-mineral finds; the rest no event; every run as replayed |
| S3 | 2405 (index 5) | 6 | comet at tick 384 suppressed (too early), climate change on unowned 18 (gravity −6) still happens; new minerals at ticks 109 and 768 suppressed; tick 1098 nothing |
| S4 | 2415 (index 15) | 5 | unowned comets (ticks 329, 384) and new minerals (109, 768) as at 2430; owned planet 17 protected at tick 1098 |
| S5 | 2430, cycles 1995–1135 | 12 | huge comet on owned planet 2; climate change on owned planet 7 (radiation −6, message axis 2, queue cut) |

Every event run is reproduced exactly by one tick's replay: each changed
planet's concentrations and environment, every event message with its
parameters, and for owned planets the surface minerals, population and
queue. Totals: 9 comets (small, medium, large and huge; owned and
unowned), 2 climate changes, 12 new-mineral finds, from 17 distinct
startup ticks. E1 year 2422 failed once to generate and succeeded on a
retry with identical inputs; `run-kx4.sh` now retries once.

Owned-planet comet vectors (population after growth → after the comet):
small 9237 → 6928, medium 9237 → 5081, large 8110 → 2839, huge 9237 →
1386, i.e. `P − trunc(P·(20e + 25)/100)`. Each queue kept Auto Factories ×5
only.

Interpretation:

- The comet's environment change hits the first `e + 1` axes in index
  order, while the owner's message names axes from a separate shuffle.
  S2's small comet on planet 15 moved gravity and its message named
  radiation: a deterministic LEGACY BUG in the message.
- The oracle's random events are a fixed function of the startup tick
  for a given state. Sampling frequencies needs different streams, not
  more years; the probabilities stay BINARY-ONLY.
- Not reached: an Alternate Reality owner (plain message, no population
  loss), the 180 concentration cap for new minerals, a clamp at 1 or 99,
  the original environment value (not in the dumps used), and deciding
  the game or dead players for score visibility.

Raw evidence: stars-oracle-apparatus `evidence/kx004/`.

#### Mystery Trader appearance (addendum)

Committed before runs S6–S10 were examined. `OBJECTS.md` gives the
Trader's appearance rule as BINARY-ONLY ("From year index 40 …"); its
draws come right after new minerals, so the same replay predicts it. Read
from the binary, in draw order: the chance draw (`rand(2)` when year index
mod 100 = 71, `rand(3)` when = 33, `rand(4)` when index mod 128 = 49, else
none in odd years and `rand(7)` in even ones; a Trader appears on 0);
warp `8 + rand(5)`; two free coordinates `1020 + rand(361 + 400·size)`
(start, then destination); `rand(2)`: 0 puts the start on the low edge
(1020) and the destination on the high edge (`1380 + 400·size`), 1 the
reverse; `rand(2)`: 0 makes the free coordinate x, 1 makes it y; then the
item (`OBJECTS.md`). Every player gets the appearance message.

Each run generates one year from an E1 state. Predicted Traders (tiny
universe: edges 1020 and 1380; item 0 is research, 0x1000 a ship, other
values a part bit):

| Run | State (index) | Cycles → tick | Trader: warp, start → destination, item |
|---|---|---|---|
| S6 | 2449 (49, 1/4) | 10500 → 384 | 8, (1380, 1172) → (1020, 1135), 0x100 |
| S6 | | 5200 → 768 | 12, (1330, 1020) → (1351, 1380), 0 |
| S6 | | 3700 → 1098 | 9, (1032, 1020) → (1188, 1380), 0x10 |
| S6 | | 1165 → 3460 | 8, (1020, 1363) → (1380, 1091), 0 |
| S6 | | 35000 → 109, 2190 → 1812 | none |
| S7 | 2471 (71, 1/2) | 11500 → 329 | 10, (1165, 1380) → (1100, 1020), 0 |
| S7 | | 1490 → 2691 | 9, (1098, 1380) → (1304, 1020), 0x20 |
| S7 | | 1210 → 3295 | 12, (1020, 1255) → (1380, 1024), 0x20 |
| S7 | | 2190 → 1812 | 8, (1362, 1380) → (1142, 1020), 0 |
| S7 | | 6000 → 659, 930 → 4284 | none |
| S8 | 2472 (72, 1/7) | 1985 → 2032 | 8, (1380, 1121) → (1020, 1283), 0 |
| S8 | | 880 → 4503 | 11, (1380, 1104) → (1020, 1173), 0x1000 (ship) |
| S8 | | 5200 → 768 | 12, (1330, 1020) → (1351, 1380), 0 |
| S8 | | 10500 → 384 | none |
| S9 | 2473 (73, odd) | 5200, 3700, 1165 | none (the same ticks give Traders at 2449/2471/2472) |
| S10 | 2533 (133, 1/3) | 35000 → 109 | 12, (1380, 1233) → (1020, 1294), 0x1000 (ship) |
| S10 | | 1190 → 3405 | 10, (1047, 1380) → (1299, 1020), 0x200 |
| S10 | | 1135 → 3570 | 11, (1020, 1166) → (1380, 1041), 0x200 |
| S10 | | 1165 → 3460 | 8, (1020, 1363) → (1380, 1091), 0x20 |
| S10 | | 11500 → 329 | none |

The comets, climate changes and new minerals of each tick are as at 2430
(the planet states differ only in population, and no planet is
protected after index 20).

**Results.** All 24 runs matched: the 15 predicted Traders appeared with
exactly the predicted warp, start, destination and item, every player got
the appearance message (0x12b, parameter: the Trader's object id), and
none appeared in the 9 runs predicted empty, including all three at the
odd index 73 whose ticks give Traders at 49, 71 and 72. The comets,
climate changes and new minerals in the same runs also matched. Items
seen: research (0), a ship (0x1000) twice, and parts 0x10, 0x20 (×3),
0x100 and 0x200 (×2). The index-133 runs show `mod 100 = 33` is tested
before the odd-year rule (133 is odd). Status of the appearance rule:
CONFIRMED (draw order, chance per index class, warp, edges and
coordinates, item draw for the outcomes seen). Not exercised: the part
reroll and its late-year research conversion, and the `mod 128 = 49`
branch at an index where `mod 100` also matches.

### KX-005 — research, tech progression and terraforming

Status: CONFIRMED (research GR under slow tech, GR-fed level-ups, part
announcements, level 26; terraform ties, Auto Min/Max, Claim Adjuster cost
and drift, Orbital Adjusters), with two prediction misses explained below.
Predictions were committed before any case ran (stars-elegy `0b610f8`).
Rules: `KERNEL.md` "Research" and "Terraforming".

Question: which research and terraforming rules in `KERNEL.md` are still
BINARY-ONLY, and do they hold? Already settled elsewhere: level cost,
cost settings, field switching, Generalized Research shares, level-26 loss
(KX-002); slower tech and Super Stealth stealing (KX-003); miniaturization
and what a race can build (`COMPONENTS.md`, CS-001); tech gained from
battles, captures and scrapping (`COMBAT.md` "Tech from battle",
`TAKEOVER.md`). Still open: Generalized Research under slower tech, a
GR-fed field levelling without switching, reaching level 26 with "same
field", which parts a level-up announces, and the terraforming rules
marked BINARY-ONLY (ties, Auto Min/Max, Claim Adjuster cost, Orbital
Adjusters, Claim Adjuster drift).

Binary reading (stars-decomp `docs/research.md`, `mining-terraform.md`):

- **Part announcements.** After a level-up in field `f`, every part the
  race may use whose requirement in `f` equals the new level is announced,
  **provided all six requirements are met** after the level-up (the lookup
  returns "available" only then). Race-restricted parts and Mystery Trader
  parts the player does not own are not announced. (An earlier private
  note read the check as field `f` only; corrected.)
- **Generalized Research under slower tech.** The current field gets
  `(res+1)/2` at full scale, so it is stored as half (rounded up) like
  normal research; each other field's 15% share `o` is added to its stored
  value as `trunc(o/2)`.
- **Level-ups in a GR-fed field** do not switch fields; their message is
  the GR variant (as every level-up message of a GR player).
- **Reaching 26** in a field whose next-field choice is "same field" turns
  the choice into "lowest field", so research moves to the lowest field
  (first in field order on ties) the same year with the leftover.
- **Auto Min Terraform** builds (up to the terraform capacity) only when
  the planet's population change this year is negative or its
  habitability for the owner is 0 or less; Auto Max always up to the
  capacity.
- **Claim Adjuster** terraform items cost half (100 → 50).
- **Orbital Adjusters:** after movement, each fleet orbiting an owned
  planet makes one click per Orbital Adjuster (whatever its value), with
  the fleet owner's terraform tech and the planet owner's habitat. If the
  fleet's owner is the planet's owner or has the planet owner as a
  *friend*, the click improves the planet (axis chosen as for production);
  otherwise (neutral or enemy) it worsens it, pushing each axis to the
  reachable end farther from the owner's centre (`orig ± reach`), unless
  the planet has a starbase, in which case nothing happens. No test of
  whether the fleet moved this year.
- **Claim Adjuster drift:** per CA planet in planet order, `rand(3)` picks
  an axis; if that axis's original value differs from the centre,
  `rand(10) = 0` is needed, then population ≥ 1000 units passes, else
  `rand(1000) < population`; the original value moves 1 toward the centre
  before the year-end terraform.

Method: Combat Lab game CB (two JOAT players), one year per run with
`pinned-turn`; specs `experiments/kx005/`. Population in units of 100;
resources = population / 10 (no factories) plus 35 at each homeworld.

#### Research cases

`kx5r`: player 0 Generalized Research, levels 10/0/3/3/3/3, energy
current, next "lowest", 100% research, four planets of 4,900 (research
1,995); player 1 levels 9/3/3/3/3/3, energy, next "same", eight planets
of 5,000 (research 4,035). Run R1 on the normal base, R2 on base `0x82`
(slower tech). `kx5l` (run R3): player 0 energy 25 with stored 85,080,
next "same", homeworld only (35).

| Run | Player | Predicted levels | Predicted stored research | Predicted messages |
|---|---|---|---|---|
| R1 | 0 (GR) | 10/**1**/3/3/3/3 | 998/30/300/300/300/300; field energy, next lowest (no switch) | GR level-up weapons 1 (continuing energy); part: Radiation Terraform ±3 |
| R1 | 1 | **10**/3/3/3/3/3 | 25/0/0/0/0/0 | level-up energy 10; parts: Bear Neutrino Barrier, Laser Battery, Temp Terraform ±11 (not Battle Nexus, which needs electronics 19) |
| R2 | 0 (GR, slow) | 10/0/3/3/3/3 (no level) | 499/150/150/150/150/150 | none |
| R2 | 1 (slow) | 9/3/3/3/3/3 | 2018/0/0/0/0/0 | none |
| R3 | 0 | **26**/3/3/3/3/3 | 0/**15**/0/0/0/0; field **weapons**, next lowest | level-up energy 26, continuing in weapons; no parts |
| R3 | 1 | 3/3/3/3/3/3 | 35/0/0/0/0/0 | none |

Alternatives these discriminate: GR shares stored at full scale under
slow tech (R2 player 0 would gain weapons 1, stored 30/…); announcements
checked on field `f` only (R1 player 1 would also announce Battle Nexus);
level 26 keeping "same field" (R3: research stays in energy and is lost,
weapons stored 0).

#### Terraforming cases

`kx5t0`, `kx5t1`, `kx5t2` differ only in player 1's relation to player 0
(neutral, friend, enemy). Player 0: JOAT, tech 3 (reach ±3 per axis),
research 0%. Player 1: Claim Adjuster, propulsion 10, biotech 6 (reach
gravity ±11, temperature and radiation ±3), research 0%, and Orbital
Adjuster fleets (one Mini-Miner with two adjusters each). Player 0 sees
player 1 as a friend, so no battle.

| Planet (owner) | Start (env = orig) | Queue / fleet | Predicted end of year |
|---|---|---|---|
| 0 (P0) | 50/60/60, pop 1000 (100 res.) | Terraform ×1 | 50/**59**/60: temperature and radiation tie, first axis wins |
| 1 (P0) | 50/60/58, pop 8000 (800) | Auto Max ×9 | 6 built (capacity), 50/57/55 |
| 2 (P0) | 50/60/60, pop 3000, growing | Auto Min ×5 | nothing built, unchanged |
| 3 (P0) | 50/86/50 (hab −1), pop 2000 (120) | Auto Min ×1 | 1 built, 50/85/50 |
| 9 (P0) | 50/60/60, pop 16000 (over capacity, shrinking; 1298) | Auto Min ×9 | 6 built, 50/57/57 |
| 5 (P1, CA) | 60/60/60, pop 1200 (120) | Terraform ×3 | queue left **Terraform ×1 at 41%** (cost 50: two built); at cost 100 it would be ×2 at 20%. Year end: env 50/57/57 |
| 15 (P0) | 60/60/60 | P1 fleet in orbit, 2 adjusters | neutral, enemy: **62**/60/60; friend: **58**/60/60 |
| 19 (P0, starbase) | 60/60/60 | P1 fleet in orbit | neutral, enemy: unchanged; friend: 58/60/60 |
| 21 (P0) | 60/60/60 | P1 fleet arriving this year (30 ly at warp 6) | as planet 15 |
| 4, 6, 13, 14, 16 (P1, CA) | 60/60/60, pop 3000 | none | env 50/57/57 (year-end Claim Adjuster), orig 60/60/60 unless drifted |
| 7 (P1, CA) | 60/60/60, pop 500 | none | as above; drift needs `rand(1000) <` its grown population (~554) |

Hostile adjusters: gravity's reachable ends are 49 and 71; 71 is farther
from the centre 50, and its average habitability loss per click (score
137) beats temperature's (86, toward 67) and radiation's (67, toward 63),
so both clicks go to gravity (`KERNEL.md` "Terraforming", Orbital
Adjusters). Friendly: gravity toward 50 (score 111) beats the others.

Claim Adjuster drift, replayed from each startup tick at draw offset 4
(the offset at which KX-004's events began; it is one value for every run
from this state and is fitted if 4 misses), planets in order 4, 5, 6, 7,
8, 13, 14, 16 (8 is the homeworld, original = centre, one draw):

| Cycles → tick | Predicted drift (original value moves 1 toward 50) |
|---|---|
| 35000 → 109 | 14 radiation (env 50/57/**56**) |
| 3700 → 1098 | 14 temperature (env 50/**56**/57) |
| 2190 → 1812 | 5 temperature |
| 1490 → 2691 | 4 radiation |
| 1210 → 3295 | 6 radiation |
| 1165 → 3460 | 4 temperature, 6 gravity (env unchanged: target stays 50), 14 temperature |
| 1135 → 3570 | 13 radiation |
| 11500 → 329, 10500 → 384, 6000 → 659, 5200 → 768, 1985 → 2032, 1190 → 3405, 930 → 4284, 880 → 4503 | none |

Runs: T0 (neutral) at all 15 cycles values; T1 (friend) at 3700; T2
(enemy) at 1165.

#### Results

Research (R1–R3, one run each; no randomness involved):

- R1: as predicted for both players, every stored value and level. Player
  0's GR message for weapons 1 named energy as the field continuing, and
  one part message (Radiation Terraform ±3). Player 1 got its level-up
  message and exactly three part messages (Bear Neutrino Barrier, Laser
  Battery, Temp Terraform ±11); Battle Nexus was not announced.
- R2: as predicted (499/150×5; 2018), no messages.
- R3: energy 26, weapons current with 15 stored, energy 0, level-up
  message naming weapons, as predicted. **Miss:** the stored next-field
  choice stayed "same field", not "lowest". Re-reading the binary: the
  promotion to "lowest" is held in a local variable; the switch writes
  only the new current field and keeps the stored choice. `KERNEL.md`
  states the observed rule.
- The non-GR level-up message is event id 0x50 in the `.M` file (the
  private note had 0x150; the id arithmetic wraps).

Terraforming (T0 at 15 cycles values, T1, T2):

- Production on player 0's planets was identical in all 17 runs and as
  predicted: planet 0 → 50/59/60 (tie to temperature); planet 1: six
  units, 50/57/55, Auto Max ×9 kept; planet 2: nothing; planet 3: one
  unit, 50/85/50; planet 9 (overcrowded, population 16000 → 15667): six
  units, 50/57/57. Claim Adjuster planet 5: queue left Terraform ×1 at
  41% (cost 50).
- **Miss (prediction setup, not a rule):** both players researched
  during the year (planets without a queue send everything to research)
  and went from energy 3 to 5, which gives Temp Terraform ±7. Production
  had already run, so it used ±3; the Claim Adjuster year-end step and
  the Orbital Adjusters ran after research and used ±7. Year-end CA
  environment was 50/53/57, not the predicted 50/57/57; recomputed with
  reach 11/7/3 every CA planet matches (and 50/52/57 or 50/53/56 after a
  temperature or radiation drift).
- Orbital Adjusters: neutral (T0, all 15 runs) and enemy (T2): planets 15
  and 21 → 62/60/60 as predicted (gravity, unchanged by the energy
  change); planet 19 (starbase) unchanged. Friend (T1): 60/58/60 on all
  three, including the starbase planet; predicted 58/60/60 with the
  start-of-year reach, 60/58/60 with the reach after research (temperature
  toward 53 scores higher than gravity). The fleet arriving that year
  terraformed in every run. Messages: friendly 0x12c, hostile 0x15a, to
  both players, with (fleet, planet, old habitability, new habitability).
- Claim Adjuster drift: 17 of 17 runs exactly as replayed at offset 4,
  13 drifts in all (the predicted table above, plus T1 at 1098 and T2 at
  3460 as for those ticks). A gravity drift on planet 6 changed only the
  original value (its target stays at the centre). Each drift sent the
  owner message 0x15c.

Raw evidence: stars-oracle-apparatus `evidence/kx005/`.

### OT — turn order, breeding in transit, AR loss gate, score speed code

Status: CONFIRMED. Every case matched its committed prediction at cycles
20000 and 3700 (two streams). Predictions were committed before the runs
(stars-elegy `2eb2c1e` for OT-1..5, `649078a` for OT-6). Specs, start
builder and prediction tables: `experiments/ot/`. Raw evidence: private
apparatus `evidence/ot/`. Rules: `KERNEL.md` "Turn order", "Alternate
Reality colonists in flight", "Inner Strength colonists breed in transit",
"Score".

Question: the program fixes the order of each year's steps, but five
neighbouring pairs that an implementation could visibly get wrong had not
been separated by a run. Also open: when an Alternate Reality fleet counts
as moving, how Inner Strength colonists breed in a fleet, and which speed
code the score's ship power uses.

Setup: one pinned year per case from the CB base (2400, two players,
random events off), edited with `CombatLab` planet sets (new key
`driver=DEST[,WARP]` for a starbase's mass-driver destination).

| Case | Separates | Observation | Result |
|---|---|---|---|
| OT-1 | Trader encounter (6b) before unload (6c) | A fleet ordered to unload exactly 5,000 kT at the Trader's arrival planet was consumed (reward message 0x109); nothing reached the planet | CONFIRMED |
| OT-2 | Battle (6) before encounter (6b) | Battle at the Trader's arrival point; no freighter lost; then the freighters traded | CONFIRMED |
| OT-3 | Launch-year packet flight (5) before bombing (6a) | The packet emptied the planet (0xda); the four bombers orbiting it sent no bombing message | CONFIRMED |
| OT-4 | CA terraforming (7.3) before Orbital Adjusters (7.4) | Final environment 50/50/51; at 3700 the original also drifted and the result was the same | CONFIRMED |
| OT-5 | Breeding in transit (3b) before production and growth (4) | Full 2100 kT IS fleet over its own planet: 157 landed (0x158), and the planet ended equal to the control planet that started 157 higher. 200 kT in a 210 kT hold in deep space: +10 (0x0fb), 5 lost. Full fleet over an enemy planet: nothing, no message | CONFIRMED |
| OT-6 AR | When an AR fleet counts as moving | 22 kT moving: kept, no 0x0c1; 23: 22 with 0x0c1; 100 kT with waypoint 1 on its own position: 97; with no fuel (did not move): 97; chasing: 97 (once); warp 0: 100, no message | CONFIRMED |
| OT-6 power | Speed code in the score's ship power | A 7-Big-Mutha-Cannon Battle Cruiser counted as an escort for a War Monger owner as well as a non-War Monger one (power 1963 without the WM bonus, 2320 with it); a 9-Disruptor design counted as capital for both (2088). Records: U/E/C 8/1/1 and 1/1/1 | CONFIRMED |

OT-6's two races were not legal (advantage points below 0), so the host
degraded colonists per resource at the start of the year. No OT-6
measurement depends on it.

Interpretation: all five orders agree with the program. The AR loss is
taken when a fleet with a waypoint at warp above 0 starts its move, before
the fuel limit and chase deferral, and only losses of at least 1 kT send a
message. The score's power uses the design's own speed code with no race
bonus.

### KB batch 1 — population, resources, mining, AR, remote mining

Status: CONFIRMED, with one refinement (AR planets' own miners). Every case
ran at two cycles values (KB-1C at 11). Predictions were committed before
the runs (stars-elegy `e936175`); `experiments/kb/` has the specs, the
model (`kbmodel.py`, public rules only) and the tables. Raw evidence:
private apparatus `evidence/kb/`. Rules: `KERNEL.md` "Habitability",
"Maximum population", "Resources and installation caps", "Mining" and
"Remote mining".

Question: which of KERNEL.md's population, resource and mining rules that
were still BINARY-ONLY hold?

| Case | Rule | Observation | Result |
|---|---|---|---|
| KB-1A 13 | JOAT + OBRM maximum; hab 79 at 70/50/50 | Population 10,430 frozen: maximum 10,428 | CONFIRMED |
| KB-1A 9 | Effective population at most `2·max` | 45,000 units at maximum 13,200 gave 2,650 resources (not 2,920); the player's research total was 4,652 as predicted | CONFIRMED |
| KB-1A 12 | Depletion clamp 10 below concentration 5 | Concentration 4, fraction 251 (clamp 25 gives 245) | CONFIRMED |
| KB-1A 16, 10 | Maximum defenses `min(100, max(10, 4·hab))` | 95 + 5 at hab 100; 5 + 5 at hab −15 | CONFIRMED |
| KB-1A 10, 11 | Hostile cap of 15 per axis | 1,000 → 985 (one axis 30 outside), → 970 (two axes) | CONFIRMED |
| KB-1A 14 | Remote mining capped at 4,000 per fleet | 4,320 robot points mined 2,720/3,120/3,040 kT, depletion exact | CONFIRMED |
| KB-1B | AR maximum population by starbase hull | Fort, Dock, Station, Ultra Station and Death Star planets frozen at 2,500, 5,000, 10,000, 20,000 and 30,000 plus 5, one of them at hab 3 | CONFIRMED |
| KB-1B 12 | AR maximum mines, factories and defenses 0 | Auto Mines, Factories and Defenses built nothing | CONFIRMED |
| KB-1B | AR resources `max(25, hab)` | Yearly resources 8,054 (7,803 without the floor) | CONFIRMED |
| KB-1B 12 | The owner's miner at an AR planet | It mined, as a separate step from the planet's own mines: boranium fraction 106 (one combined step gives 107) | Refined |
| KB-1C | Mining's random +1 and its draw order | 77 planet results in 11 streams as replayed; climate change on planets 20 and 22 as replayed | CONFIRMED |

Interpretation: all the readings tested hold. The remote-mining reading
that an AR owner's miners add their robot points to the planet's mines is
replaced by "a separate mining step".

Also found: an earlier ship-launch discrepancy (SL-12, a Station upgrade
at 88% with about 120 resources where 170 were expected) came from that
batch's illegal test races. The host degraded colonists per resource
from 1,000 to 2,400 before production, and with that value the resource
rule gives exactly 120 left after the research tax. CombatLab's dump now
prints each player's advantage points so a start can be checked first.

### KB batch 2 — production pre-checks, research switching, slow-tech stealing, immune terraforming

Status: CONFIRMED. Each case ran at cycles 20000 and 3700 with identical
results. Predictions were committed before the runs (stars-elegy
`734498a`); `experiments/kb/` has the specs, model and tables. Raw
evidence: private apparatus `evidence/kb/`. Rules: `KERNEL.md`
"Research" ("Level cost", "Allocation"), "Production" and
"Terraforming".

Question: do KERNEL.md's remaining production and research rules hold,
including the Ultimate Recycling bonus, the queue pre-checks and the
zero-item queue? And field switching after a "same field" research reaches
26, stealing under slower tech, and terraforming with an immune axis?

| Case | Rule | Observation | Result |
|---|---|---|---|
| KB-2A 13 | Ultimate Recycling scrap bonus `r + trunc(x·r/(x+r))` | 10 ships of owner cost 241 (`x` 2,410) at a 500-resource planet with no queue: research total 1,449 (500 + 414 + others); the message carried 414. Minerals 378/0/99 = `9C/20` | CONFIRMED |
| KB-2A 9 | A scanner order on a planet with a scanner | Removed (0xb9), queue freed (0x3e), 300 resources to research | CONFIRMED |
| KB-2A 12 | A packet order with no driver | Removed (0x129), queue freed (0x3e), 200 to research | CONFIRMED |
| KB-2A 16 | Zero-item queue | Nothing to research, no message; the empty queue block stayed | CONFIRMED |
| KB-2A P0 | "Same field" at 26 acts as "lowest" for the rest of the year | Research 1,135: energy 26, weapons 1, propulsion 1, then weapons current with 185; three level messages naming weapons, propulsion, weapons as next; stored choice still "same" ("same" kept would give weapons 2 with 155) | CONFIRMED |
| KB-2B | Stolen research halved rounding up under slower tech | Super Stealth stored energy 48 + 12 = 60 and weapons 44 (two 0x159 messages showing 23 and 88); the other player's weapons 355 stored as 178 | CONFIRMED |
| KB-2C | An immune axis is not terraformed and adds no capacity | Gravity-immune race: 20/47/50, Terraform ×5 cut to ×3 (0x12f) → 20/50/50; 10/50/50, ×2 removed (0x12f), nothing built | CONFIRMED |

Interpretation: every reading tested holds. KB-2C's first run was void.
Its race marked gravity immune with only the centre byte at −1, and the
host repaired it before production: message 0x117, gravity centre forced
to the midpoint of low and high (50), and both planets were then
terraformed in gravity. An immune axis needs centre, low and high all at
−1 (`docs/ORACLE.md`); the rerun used that.

### KB batch 3 — the year-wide random draw order

Status: CONFIRMED. Predictions were committed before the runs
(stars-elegy `75900b5`). `experiments/kb/` has the spec and the table.
The replay tool is private, and the raw evidence is in apparatus
`evidence/kb/`. Rule: `KERNEL.md` "Random draws".

Question: in one year with a tech attempt from scrapping at a starbase,
mining, the random events and a bombing pass, do the draws follow the
program's order? That order is the shuffle, the scrap attempt, mining,
the events, then bombing.

Setup (KB-3A): events on, year 2400. Player 0 scraps a Scout with a Long
Hump 6 at player 1's Orbital Fort planet; player 1 is at tech 0. Mining
makes five draws. Player 0's one-LBU-17 bomber orbits player 1's planet
13, with 45 factories, 25 mines, no defenses and 1,012 population after
growth.

| Streams | Observation | Result |
|---|---|---|
| 11 of known tick | Player 1's propulsion gain (with 0x13d, else 0x141), every mining gain, and planet 13's factories, mines and population all as replayed | CONFIRMED in 11 of 11 |
| 12 of unknown tick | Each matched the predicted order at some k (`trunc(k·54.925)`). 2100 and 2060 both showed planet 10's radiation 35 → 28, the climate change predicted at k = 35, with every other value matching. Under either alternative order no k matches them | CONFIRMED, with a visible event |

Alternatives ruled out: mining before the scrap attempt (11 of 11
known-tick streams differ), and bombing before the events (3 of 11 differ,
and neither climate stream matches).

Interpretation: the scrap tech attempt draws before mining, and bombing
draws after the events. Capture and artifact draws, battles, Trader
rewards and the movement-phase draws keep the places read from the
program (BINARY-ONLY).

### KB batch 4 — movement and fuel leftovers

Status: CONFIRMED. Every fleet matched the prediction in both streams
(cycles 20000 and 3700). Predictions were committed before the run
(stars-elegy `a71bc70`), and `experiments/kb/` has the spec and table.
Raw evidence: apparatus `evidence/kb/`. Rules: `KERNEL.md` "Fuel cost",
"Not enough fuel", "Chasing another fleet", "Refuelling at a starbase"
and "Other movement rules".

Setup (KB-4A): player 0 is an Interstellar Traveler with Improved Fuel
Efficiency at tech 26. Player 1 treats player 0 as a friend.

| Fleet | Rule | Observation | Result |
|---|---|---|---|
| KB-4A G1, G2 | Anti-matter Generator +50, capped | 100 → 150; 230 → 250 (tank 250) | CONFIRMED |
| KB-4A X1, X2 | Fuel transport +200, capped | 1,000 → 1,200; 2,150 → 2,250 (tank 2,250) | CONFIRMED |
| KB-4A E | IFE factor `f − trunc(15f/100)` | 300 → 295 at warp 6 over 36 ly (294 without IFE) | CONFIRMED |
| KB-4A K | A fleet that cannot afford the leg but keeps fuel keeps its warp | 20 → 15, warp 6, no out-of-fuel message | CONFIRMED |
| KB-4A H, H0 | Radiating Hydro-Ram Scoop colonist loss | 70 → 58 moving (message 0x74); 70 stationary | CONFIRMED |
| KB-4A Q | Equal engine factors keep the fleet's design order for cargo | 300 → 243 (the other order gives 244) | CONFIRMED |
| KB-4A C | Fuel-limited chaser of a finished target | 5 mg, moved 7 ly to (1026, 1013), 0 mg, warp 1, out-of-fuel message, waypoint on the target's end | CONFIRMED |
| KB-4A T1, T2 | Transport task holds a fleet until satisfied | "wait for 50%" with nothing to load held the fleet; "unload all" unloaded 10 kT and the fleet moved 25 ly | CONFIRMED |
| KB-4A F1–F5 | Refuelling: dock required, own or friend's starbase | friend's Space Station 10 → 300, 400 → 300; neutral owner's 10; own Orbital Fort 10; own Space Station 10 → 300 | CONFIRMED |

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

Settled since this list was written (kept for the record):

- ~~IFE and other LRTs, warp-10 ship losses, fuel transports and
  anti-matter generators~~: CONFIRMED in Round 2 (FM-101..105) and KB batch
  4 (KB-4A: IFE factor, generator and transport caps, refuelling at a
  friend's or own dock). Cheap Engines failures and warp-10 losses are
  MEASURED rates (Round 2).
- ~~Fuel transfer orders~~: `ORDERS.md` "Cargo amounts and clamps"
  (FO-01..07).
- ~~Chase candidates, oracle side only FM-001..003~~: chasing a finished
  target CONFIRMED (KB-4A C); per-pass steps and the chain freeze MEASURED
  (MF-02, MF-02b, "Followers" below).
- ~~Minefields, stargates, wormholes~~: covered by the MF, GT and WT
  corpora (`OBJECTS.md`).

Still open:

- Whether chain freezing and the mutual-chase scheme hold for three-way
  cycles and in the next year.

### Round 2 (FM-101 to FM-105)

Status: MEASURED, 2026-10-07. Tests the KERNEL.md movement and fuel rules
that FM-001..004 did not reach. Combat Lab (two JOAT players, tech 26),
pinned generations; FM-104 runs two years. Predictions were committed
before the runs, mostly computed by `experiments/fm2/model.py` (KERNEL.md
as code). Every case and value is in `experiments/fm2/README.md`; raw
evidence is in stars-oracle-apparatus `evidence/fm2/`. 54 of 56 checks
held.

**CONFIRMED:**

- Improved Fuel Efficiency: factor `f − trunc(15f/100)`, both in the cost
  of a move and in the range of a fleet short of fuel (two discriminating
  cases).
- Cheap Engines: 2 of 40 fleets at warp 7 did not move (they kept their
  fuel and waypoint); none of 20 at warp 6 (MEASURED, one sample).
- Warp 10 on engines not rated for it: 11 of 100 ships lost, and 5 of 50
  in a fleet whose other 50 ships had a rated engine (MEASURED, one
  sample each). Fuel leaves with the lost ships in proportion:
  `30000 − trunc(30000·11/100)` before the survivors pay for the move.
- Ram scoops with two engines per ship: `k` scales with the engine
  count (192 at warp 4, 80 at warp 2, Radiating Hydro-Ram Scoop).
- Anti-matter generator +50 and Super-Fuel Xport +200 per ship per year,
  moving or not, capped at the tank.
- Refuelling: at a friend's Space Dock and Space Station, but not at a
  friend's Orbital Fort, an enemy's Space Dock or the player's own Orbital
  Fort. The planet owner's relation toward the fleet's owner decides.
- A fleet laying mines at waypoint 0 does not move. A transport task that
  finished before movement does not hold the fleet (it moved on).
- A fleet that cannot afford its whole leg but keeps fuel keeps its warp.
- Designs with equal engine factors take cargo in design order.
- A chaser of a stationary fleet follows the ordinary fuel rules
  (fuel-limited, ram scoop, top-up).
- Fleets of player 0 move before player 1's, whatever their numbers (a
  mutual chase).
- Rounding toward smaller coordinates is half away from zero.
- Radiating Hydro-Ram Scoop colonist losses (JOAT radiation 15–85):
  18 of 100, 1 of 3, none when stationary.
- Waypoint chains over two years: no carry-over after a waypoint; a first
  waypoint at the fleet's own position uses up the year; a fleet that ran
  dry crawls at warp 1 the next year and its scoop gives 1 mg.

**Contradicted:**

- **Fuel unloaded onto a planet** by a waypoint "unload all" is not lost:
  nothing moved and the fleet kept its fuel (the task was cleared).
  KERNEL.md says it is lost; a direct cargo order is not tested.
- **A design whose engine slot is not full** (a Large Freighter with one
  of its two engines) moved its whole warp-5 distance and emptied its
  tank. The range estimate overflows 32 bits (99999 × 1000 × 134 wraps),
  so the fleet moves `fuel·1000/25748` ly at most, here 25, then pays
  16750 mg it does not have. Three more cases (200, 50 and 500 mg: 7, 1
  and 19 ly) followed that rule (FM-105, predicted before the run).
  Probably only reachable with edited designs (LEGACY BUG candidate).

## Fleet Operations

Status: MEASURED, 2026-10-07 (FO-01 to FO-07). Tests the "Fleet
operations" rules of `ORDERS.md` (stars-elegy #40) that can be set up with
waypoint tasks in the host file. Predictions were committed before each
batch of runs. Specs, predictions and the checker are in
`experiments/fo/` (`gen.py`, `check.py`); every case and value is in
`experiments/fo/README.md`. Raw evidence is in stars-oracle-apparatus
`evidence/fo/`.

### Method

Combat Lab (CB, two JOAT players), one pinned generation per run. Fleets
are Medium Freighters with Long Hump 6 (cargo 210 kT, fuel 450 mg) in deep
space or at own planets without a starbase. CombatLab can now point
waypoint 0 at a fleet and write the merge and transfer-fleet tasks
(`ORACLE.md`).

### Transport amounts and clamps (CONFIRMED)

- A load takes at most the free cargo hold and what the source has. The
  four cargo kinds are handled in order Ir, Bo, Ge, colonists, so "load
  all" of Ir and Bo from 150/150 into an empty 210 kT hold took 150 Ir
  and 60 Bo.
- Fuel is clamped by the free fuel tank, independently: a fleet with a
  full hold took 250 mg into its 200/450 tank. An own planet without a
  starbase gave no fuel to a "load all" fuel order.
- An unload into another fleet is capped by that fleet's free space; the
  rest stays aboard (200 kT offered to a fleet with 110 kT free: 110
  moved, 90 kept). The same holds for fuel.
- Action amounts, loading from an own planet: fill to 50% loads half the
  hold (105); set amount to 80 loads 80; set waypoint to 100 leaves 100
  on the planet; wait for 100% keeps the fleet at the planet while unmet,
  where fill to 100% lets it leave. "Load optimal" fuel with a single
  waypoint gives all of the fleet's fuel to the target fleet.
- Transport task after a short or refused load (rereading FO-01, FO-04
  and TK-302: apparatus `evidence/kb/holds`). Short fill to 100% (100 of
  210, FO-01-J) and short load exactly (25 of 40, TK-302) ended the task.
  Wait for 100% (FO-01-I) kept it. A load from another player's fleet
  (FO-04) loaded nothing, sent 0x120 and ended the task in the same
  generation.
- Colonists loaded from an own planet before growth (87 → 57, then
  growth).

### Turn placement (CONFIRMED)

Waypoint loads and merges at the starting waypoint happen before
movement: the loaded cargo and merged ships leave with the fleet. Tasks at
an arrival waypoint run after movement (load from a planet, load from or
unload into a fleet, merge). A fleet whose only waypoint targets another
of its owner's fleets loaded from it before movement and then followed it
to the target's destination.

### Another player's fleet (CONFIRMED)

Minerals unloaded into another player's fleet moved when the receiver's
relation toward the giver was neutral, and nothing moved when it was
enemy; the giver's own relation did not matter. Colonists were refused in
both cases. A fleet without a cargo-stealing scanner loaded nothing from
another player's fleet, and a merge into another player's fleet was
refused.

### Transfer fleet task (CONFIRMED)

Giving a fleet to another player worked when the recipient's relation
toward the giver was not enemy: the recipient got a fleet at the same
place with the same ships, cargo and fuel, under a free design slot that
holds a copy of the design (it was not matched to the recipient's existing
Medium Freighter design, which differs in parts). It was refused when the
recipient was an enemy toward the giver, and for a fleet carrying
colonists.

### Merge with Fleet task

- **Ships, cargo, fuel (CONFIRMED).** The ordering fleet joins the target,
  which keeps its id; ship counts add per design; cargo and fuel add up.
- **Damage (MEASURED).** Per design slot, with `D = max(1, pct·count/100)`
  damaged ships in each damaged stack and `n` ships after the merge, the
  new percentage is `ceil(100·ΣD/n)`. When only one of the two stacks is
  damaged, its damage units are kept. When both are, the units become
  `ceil(Σ D·units / n)`: divided by **all** ships of the slot, not by the
  damaged ones, which dilutes the damage (10 ships at 100 units on 50%
  plus 10 at 200 on 20% gave 45 units on 35%). Seen in seven cases; the
  year's repair then applied normally.
- **No ship-count cap (MEASURED).** 32000 + 767 ships gave 32767;
  32000 + 768 and 32000 + 1000 left a fleet with **no ships** (its cargo
  and fuel kept). This contradicts the 32766 cap in `ORDERS.md` for the
  waypoint task; the cap may still apply to the direct merge order, which
  is not tested.
- **Distance.** A merge task whose waypoint 0 sat at the orderer's own
  position but targeted a fleet 195 ly away was refused and cleared. The
  interface does not create that state, so this says only that the task
  is not applied from a distance.

### Not tested (waiting on the serial decision)

Split, the direct transfer between own fleets (and its capacity-based
sharing), direct merges, and the order-time placement of direct cargo
orders need an order file accepted by the registered host. Also not
tested: steal mode, a fleet that may not carry colonists, transfers to an
AI player.

## Combat

Status: MEASURED (round 1 CB-000 to CB-008, round 2 CB-009 to CB-019,
round 3 CB-020 to CB-022, round 4 CB-023 to CB-034, round 5 CB-035 to CB-041, round 6 CB-042 to CB-047, 2026-10-07; cloud
oracle). Predictions from the private binary reading (stars-decomp
`docs/combat-predictions.md`: P-1..P-29 at 8cad60f for round 1, Q-1..Q-14
at 4a8c82b for round 2, R-8..R-10 at 134256d for round 3; round 4 from the
BINARY-ONLY rules in `docs/COMBAT.md` and stars-decomp 385b473) were
committed before every run (`experiments/cbNNN/README.md`).
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
  (20, 50), capacitor (one Flux Capacitor and one Energy Capacitor
  compound once per item, 1.2 × 1.1 → 132%), deflector (90%), shield
  and armor per ship, mass and speed code (P-3).
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
  hits, in both of two seeds (CB-019). Round 3 (R-8) predicted the end
  square for tactics 3, 4 and 5 in six streams and all matched.

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
  predicted that usually no battle happens. Round 3 (R-10) shows the
  outcome depends on what the game handled earlier in the turn.
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
  Round 3 (R-9) predicted which streams gain, and all six matched.

### Round 3 (CB-020 to CB-022)

Every run was pinned (`tools/fleetlab/pinned-turn`). Cycle counts 8000,
12000, 16000, 20000, 30000 and 50000 gave six distinct battle records for
each setup. The binary reading predicted exact squares and outcomes for each
stream. Every hit in the round-3 records replayed with the binary-derived
checker (stars-decomp 134256d) with no mismatches.

- **Tactic movement (R-8, CONFIRMED, 14 new cells).** In the CB-019 setup
  (one Long Destroyer, Phaser Bazooka range 2 and Colloidal Phaser range 3,
  against an immobile Laser Station), the final square matched the
  prediction for tactics 3, 4 and 5 in every stream. Under tactic 5
  ("maximize damage") the destroyer closed in and was destroyed in round 9
  in all six streams. The binary reading's account, consistent with all
  18 observed cells: tactics 3 and 4 score squares the same way, but
  tactic 3 (like 5) limits how far it looks using the shortest weapon
  range and tactic 4 the longest; ties use the random stream.
- **Tech from battle per stream (R-9, CONFIRMED 6/6).** Player 0 (weapons
  3, research 0%, other fields 26) had a Laser Station at its homeworld;
  three player-1 frigates armed with Colloidal Phasers attacked it. The
  frigates' squares in rounds 0 to 4 matched in all six streams, all died
  in round 4, and weapons rose to 4 in the 2401 file in exactly the three
  predicted streams (12000, 16000, 20000), not in the other three.
- **Plan 0 "player i" and "everyone" (R-10, LEGACY BUG).** Player 0 owns a
  planet with a Laser Station; player 1 sees player 0 as neutral, and
  player 1's armed fleet attacking "enemies" sits there. Player 1's other
  fleet, a lone hauler with a lower fleet number, is in a battle-free spot.
  - With plan 0 "player 1", the game wrote a battle record with one
    player, two tokens (the visitor's stack at (1,4), the station at
    (4,4)) and no actions, in both seeds (CONFIRMED).
  - With plan 0 "enemies", it was an ordinary battle: the station destroyed
    all five frigates in round 4 (CONFIRMED).
  - With plan 0 "everyone", the record was the same degenerate one,
    byte-identical to the "player 1" record (CONTRADICTED; predicted an
    ordinary battle).
  - With plan 0 "player 1" and no lone hauler, no battle record at all.

  Together with round 2, where "everyone" and "player 1" behaved like
  "enemies" right after another battle, a station's plan 0 attack-who
  other than "enemies" does not act as written: the outcome depends on
  what the game handled earlier in the same turn.

### Round 4 (CB-023 to CB-031)

Every run was pinned. Setups with a random element ran at twelve cycle
counts (5000 to 50000), which gave twelve distinct battle records each;
the others ran at two or three. Every hit replayed with the stars-decomp
checker (385b473) with no mismatches. CB-031 used a new three-player
game built with `tools/fleetlab/new-game` (`experiments/cb031/cb3p.def`).
Planet-side starbase damage was set with the new `planetset sbdmg` key.

- **Fuel lost with destroyed ships (CB-023, CONFIRMED by fuel capacity).**
  Two Fuel Transports (fuel capacity 750 each) died out of a fleet with
  three Small Freighters (130 each). The fleet kept
  `F − ⌊F·Σ lost capacity / Σ capacity⌋` = 1000 − ⌊1000·1500/1890⌋ = 207,
  in both seeds. The committed number (124) **missed** because it assumed
  the fleet's start fuel, 600: each Fuel Transport adds 200 fuel per turn,
  and that happens **before** battles (the no-battle control went
  600 → 1000). A share by ship count would have left 400.
- **Repair (CB-024, CONFIRMED, 28 of 28 values).** With and without
  Inner Strength: moved, deep space, other player's planet, own planet
  without a starbase, own planet with an Orbital Fort, docked at a Space
  Station, and a Fuel Transport in the fleet. IS doubles every rate except
  the Fuel Transport's 25. Starbases repair 50, or 75 with IS.
- **Dump cargo (CB-025, CONFIRMED).** A battle plan with "dump cargo"
  drops the whole cargo at setup: in deep space a salvage object with
  exactly the cargo (no quarter lost, and nothing destroyed); at a planet,
  the full amount onto its surface. Speed codes matched COMBAT.md: 0 for
  the dumping Freighters, 1 for the loaded one that did not dump.
- **Range-0 beams (CB-026, CONFIRMED).** A station with Blackjacks (range
  0) first fired at distance 1, and every hit delivered full damage (no
  dropoff at distance 1).
- **Starbase target score (CB-027, CONFIRMED).** A Hunter with one
  Colloidal Phaser and "any" as its primary target had a Bare Station and a
  Fuel Transport in reach for 8 shots (2 seeds), with the station's damage
  at most 97/500. Every shot went to the station: its score uses its plain
  cost (a halved cost would have chosen the Fuel Transport).
- **Disengage (CB-025, CB-028, CONFIRMED in part).** A disengaging token
  leaves on its 8th move, which may be in round 7 (one move a round) or
  round 14 (speed 0, moves in even rounds only). Each move record carries a
  counter that counts down from 7 to 0. Every disengage move in 6 records
  changed square, so whether a move that keeps a token on its square
  counts is **not tested**.
- **Wiped-out participant, two players (CB-029, CONFIRMED 12/12).** All of
  player 0's ships died while destroying a weapons-10 design; player 0
  (weapons 3, research 0%) stayed at 3 in all twelve streams.
- **Three-player battles (CB-031-n3, CONFIRMED).** The record holds three
  players (mask 0x7). Player 0 was wiped out in every stream and still
  reached weapons 4 in 5 of 12 streams: with three players every
  participant attempts. Start squares: player 0 (4,1), player 1 (8,8),
  player 2 (1,8), as in the COMBAT.md table, in all twelve streams.
- **Observer attempt (CB-031-obs, LEGACY BUG, CONFIRMED 12/12).** Player 0
  had a fleet at a battle between players 1 and 2, and a weapons-10 design
  was destroyed. Player 0 stayed at weapons 3 in all twelve streams; the
  intended observer rule would give it an attempt. The battle record went
  to players 1 and 2 only; player 0's file had none.
- **Movement order (CB-030, CONFIRMED in 2 streams).** Two Heavy (mass 165)
  and two Light (mass 23) stacks per side: inside every movement phase both
  Heavy tokens moved before any Light token, and the order between the two
  Heavy tokens varied.
- **Not tested:** the firing live-token recheck and "step 5 only ends the
  battle". In these battles attack sets are symmetric (every player that
  can attack another is attacked back), so a player whose last token dies
  has no attacker left. A discriminating setup needs four or more players
  with one-sided attack sets, or a plan-0 setup like CB-022.

### Round 4b (CB-032 to CB-034)

Setups from the Combat decomp pass after round 4 (stars-elegy #38,
stars-decomp #17); predictions committed before the runs. Each ran at six
cycle counts (8000 to 50000), giving six distinct records; every hit
replayed with the checker. CB-033 used a new five-player game
(`experiments/cb033/cb5p.def`).

- **Out players still fire, friends join (CB-033, CONFIRMED 6/6).** Five
  players in deep space. Player 0 (one Laser Frigate) and player 1 (four
  Phaser Destroyers) name each other. Player 2 (one Phaser Frigate)
  attacks nobody and considers player 0 a friend. Players 3 and 4 name
  each other. In every stream:
  - The record holds five players (mask 0x1f), and player 2 has a token,
    so it joined through its friend. Start squares: (4,1), (6,8), (1,4),
    (8,4), (2,8) for players 0 to 4, as in the COMBAT.md table for five.
  - Player 1 destroyed player 0's frigate in round 2 with one shot, and
    never fired again; it never fired at player 2.
  - Player 2 fired at player 1 in rounds 0 to 15, 13 times after player 0
    was gone. So a player found out at step 5 (player 2 names only player
    1, which names only the dead player 0) keeps firing.
  - Players 3 and 4 fired only at each other, and the battle ran all 16
    rounds.
- **Stay-put disengage (CB-032, CONTRADICTED as predicted; rule still not
  tested).** Three players: players 0 and 2 (two Laser Destroyers each)
  name player 1, whose only token is an unarmed Freighter starting at
  (8,8). The prediction was a first move to (9,9) and six stays there.
  In all six streams the Freighter changed square on every one of its 8
  moves (it reached (9,9) only once, in one stream), often moving towards
  the Destroyers, and left in round 7. No move kept it on its square, so
  whether such a move counts is still open. No shots were fired. The
  Combat decomp pass traced this to the out-of-reach damage estimate,
  which is flat at distance 2 or more for these Laser stacks (#38).
- **Stay-put disengage (CB-034, CONFIRMED 6/6).** CB-032's geometry, with
  12 Delta Torpedo Destroyers per enemy stack whose target types (armed
  ships, then starbases) the Runner does not match. The enemies never
  moved or fired. In every stream the Runner moved to (9,9), stayed there
  on moves 2 to 7 (each a move record to (9,9), counter 6 … 1) and left
  on its 8th move, in round 7. A move that keeps a disengaging token on
  its square counts.

### Round 5 (CB-035 to CB-041)

The plan-0 X (Elegy's open question A6) and the observable open
experiments of `docs/COMBAT.md` (#38). Predictions were committed before
each batch (50e3a52; b74b693 and 313c796 for setups added after the
first runs). Pinned runs at six to twenty cycle counts; streams are
counted by distinct battle record. Every hit replayed with the checker,
0 mismatches. CB-035 to CB-037 use a 16-player game
(`experiments/cb035/cb16p.def`).

- **Plan-0 X at the first location (CB-035).** Player 0's armed station,
  plan 0 "player 1", with player 1 and 13 other players' Frigates in
  orbit, as the first location of the turn:
  - No battle in 36 of 36 runs (12 cycle counts, and 6 each with extra
    stationary or moving fleets elsewhere). X was never one of the 16
    players. Its exact value is not observable this way.
  - Control, a lone player-0 fleet first: X = 0 and the station fired, 6
    of 6.
  - **X from the previous location, CONFIRMED for a nonzero player.**
    After a battle-less location whose last fleet was player 3's, the
    station's "player 1" went into player 3's set: player 3, whose own
    plan attacks nobody, attacked player 1 at player 0's planet (players
    {0, 1, 3}, 6 of 6). Player 1 fired back, as retaliation says. After a
    location with a battle, X = 0 (6 of 6).
- **Start squares, CONFIRMED (CB-036, 2 streams).** `n` = 4: (1,1),
  (8,8), (1,8), (8,1). `n` = 6: (1,4), (8,5), (2,8), (7,1), (6,8), (3,1).
  An uninvolved starbase owner in a two-player battle at its planet takes
  (1,4), and the two fighters, at ranks 1 and 2, take (8,5) and (4,1): the
  flattened-table rule past row `n`.
- **Observer LEGACY BUG for players 1 to 3, CONFIRMED (CB-037, 8 streams
  per setup).** Observers 1, 2 and 3 in deep space, with weapons 3 and no
  research: player 1 never gained (1 AND 0b1110 = 0), player 2 gained in
  2 streams and player 3 in 3. A player with no fleet there never gained.
  At a planet whose owner (player 1, fighting) has no starbase, observer 3
  gained in 3 of 8 streams; in the same streams in deep space it never
  did (3 AND 0b1000 = 0).
- **Speed code (CB-038, 2 streams).** War Monger adds 2, CONFIRMED on six
  stacks. A stack's cargo share is **divided over its ships**: a
  two-freighter stack carrying 1 kT kept mass 69 and code 2, where one
  freighter with 1 kT had mass 70 and code 1. The battle record's token
  mass is this per-ship mass. (MISSED: the prediction added the share
  once.)
- **Token cap is 255 (CB-039, 2 streams).** Two players with 140 one-ship
  fleets each: 255 tokens, player 0 127 and player 1 128 (MISSED: 256,
  129/127). The same fleets sat out in both streams (player 0's fleets 1
  to 13, player 1's fleets 0 to 11) and survived untouched.
- **Salvage past 30000 kT, CONFIRMED (CB-040, 2 streams).** 16 Super
  Freighters with 48000 kT of ironium destroyed in deep space left two
  objects at the battle point: 30000 ironium (exactly 3000 steps) and
  6098 ironium + 50 germanium. Nothing was lost; the germanium went to the
  second object.
- **AR starbase destroyed (CB-041).** The planet is left uninhabited
  (owner none, population 0), CONFIRMED in 17 of 17 streams where an AR
  Orbital Fort died; a JOAT owner keeps it. The no-attempt rule was not
  discriminated: a **JOAT** owner at its own planet with ten Freighters
  left, after losing its Fort and destroying propulsion-9 Destroyers,
  never gained in 8 streams (about 4% at the expected 1/3), and gained in
  1 of 4 streams where its Fort survived. Resolved after the round by the
  Combat decomp pass's exact replay of every CB-041 battle from its stream
  (stars-decomp #22): the JOAT result is as predicted in 12 of 12 streams
  (the 0 of 8 was chance), and in 4 AR streams an attempt would have
  gained and none did, so the AR no-attempt rule holds (CONFIRMED by
  replay, no new run).

### Round 6 (CB-042 to CB-047)

Predictions from the Combat decomp pass (stars-decomp #22, COMBAT.md #38)
and committed here before each batch (bd91da5; 62e2792 and 69e1ef9 for
two setups added after the first runs). Pinned runs; streams counted by
battle record. The tooling check for this round is ORACLE.md "Production
queues and Mystery Trader parts".

- **Token cap, CONFIRMED (CB-042 to CB-044, 2 streams each).** Each
  player first gets `255 / n` stacks; a starbase counts toward the 255
  but not toward a quota; the second pass skips a fleet that does not fit
  and goes on.
  - Three players with 100 fleets each: 255 tokens, 85 each; left out
    player 0's fleets 1..15 and players 1 and 2's fleets 0..14.
  - At player 1's planet with an armed Orbital Fort, 140 and 131 fleets
    (one with three designs): player 0 127 stacks, player 1 127 stacks
    plus the Fort; left out player 0's 1..13 and player 1's 0..5.
  - CB-039 with player 1's fleet 12 holding two designs: 255 tokens, 127 /
    128; fleet 12 sat out and fleet 11 fought.
  - The checker replayed every hit except one carried-damage hit in each
    three-player stream. Resolved after the round: a checker defect (it
    retried an earlier shot's carried amount, which also killed, and so
    carried the wrong rest). Fixed in stars-decomp `tools/combat.py`, every
    hit of both streams replays.
- **Cargo in the speed code, CONFIRMED (CB-045, 2 streams).** Each ship's
  mass is its design mass plus `C · c / F`, truncated (fleet cargo `C`,
  the ship's cargo capacity `c`, fleet capacity `F`): a Medium and a Small
  Freighter sharing 140 kT weighed 174 and 69 (codes 0 and 2); three
  Medium Freighters with 212 kT weighed 139 each and with 213 kT 140.
- **Queued ships lost with a starbase, CONFIRMED (CB-047, 2 streams).**
  Player 1's homeworld queued 50 Destroyers, then 20 factories. Without
  attackers the queue ended the year as 49 Destroyers (92% done on the
  next) and the factories. When the Station was destroyed the Destroyer
  item was gone and the factories stayed; the Destroyer built that year
  (production comes before battles) fought and died.
- **Mystery Trader items from battle: none gained (CB-046, MISSED).** A
  player with every field at 26 and no Mystery Trader items destroyed six
  Anti Matter Torpedo Destroyers (12 streams) or three Mini Morphs with
  five more Mystery Trader parts (12 streams) and never gained an item.
  With its biotechnology at 3 instead, the same 12 streams gave a
  biotechnology level in 2 and still no item, so attempts happen.
  Resolved after the round by the Combat decomp pass (COMBAT.md "Mystery
  Trader chances"): a part's chance grows by its slot count per kill
  event, up to 25, so these battles gave chances of 2 to 8. An exact
  replay of every battle from its stream predicts no item in all 36
  streams and the two biotechnology gains exactly. A nonzero chance
  giving an item is still untested.

### Round 7 (CB-048, CB-049) and scanning SC-035/SC-036

Predictions committed here before each batch: 11b00a2 (CB-048), 1f528ce
(CB-049) and 7229c97 (SC-035/036). The SC-035 setup was changed in
ba6b0d1 before its second run. Experiment READMEs hold the details.

- **Mystery Trader items from battle, CONFIRMED (CB-048: 24 runs, 20
  streams; control 12).** The round-6 miss is resolved by the
  reconciled rule (decomp combat pass, COMBAT.md):
  - each kill event adds, for each Mystery Trader part type on the
    destroyed design, its slot count to that item's chance;
  - the chance is capped at 25, and hulls never count.

  Thirty one-ship Mini Morph fleets (five Mystery Trader part types)
  gave one item in 10 of 20 streams. The same 30 Morphs in one fleet
  gave one in 1 of 12. The decomp's replay matched every move. It
  also named exactly the gaining streams and the item in each, in all
  36 runs. The checker replayed every hit.
- **Battle movement beyond the replayed cases (CB-049, 6 streams):
  replayed.** There were seven moving stacks on tactics 1 to 4, with
  target-type mismatches, weapons of ranges 1, 3 and 4, capacitors,
  deflectors, sappers and shields. The decomp's battle replay (round 8)
  matched every move and every hit in all 6 streams. The one hit the
  checker first missed (cycles 7000, round 4, a Mixed DD on the shielded,
  deflected Shield DD) was a checker fault in pairing torpedo records,
  not a rule gap. The unarmed freighter token was recorded with tactic 0
  under a tactic-3 plan.
- **Scanning after bombing, CONFIRMED (SC-035, 2 streams).** A
  scannerless bomber fleet emptied an enemy colony with no starbase.
  Its owner then got a normal report of the now-unowned planet; at an
  unowned control planet it got position only.
- **Designs and players from a three-player battle, CONFIRMED (SC-036,
  2 streams).** Players 0 and 1 (friends) and player 2 (enemy of both)
  fought in deep space. Each participant's file then held the other two
  players' designs in full, the ally's included, and player blocks for
  both. Before the battle it held only its own.
- **Battle plans.** New fleets got plan 0 in every SL run, over 40 new
  fleets (below).
  - Not run: the 16-plan limit and delete-and-renumber, which need
    client or crafted orders.
  - Not run: the stale "Default" attack-who, which needs two games in
    one client session.
  - Not re-run: the five starting plans, already MEASURED on 22 games.

### Ship launch (SL-01 to SL-12)

Predictions from the decomp ship-launch reading and the public
ship-launch spec, committed here before the runs (4c2ae44). Two
setups were added later, each committed before its own runs: a starbase
control (70745c8) and an SL-10 follow-up (428e68d). Each case ran on 2
pinned streams, and the two always agreed. Details are in
`experiments/sl/README.md`.

The SL races were illegal: player 0 (JOAT + ISB) was at −42 advantage
points and player 1 (AR + ISB) at −94. The host degraded them before
production, raising colonists per resource to 2,400 and 2,500. That
changes resources only. The ship-launch spec explains
why no other SL result depends on it. Combat Lab builds now refuse a
negative race score unless `COMBATLAB_ALLOW_ILLEGAL_RACE=1` is set.

- **New fleets, CONFIRMED (SL-01..03).**
  - Each queue item makes its own fleet with full fuel, plan 0 and one
    waypoint at the planet.
  - A new fleet takes the lowest unused number (2 and 4 when 0, 1 and 3
    were in use).
  - Byte 5 bit 0x20 is clear on a new fleet in its build year and set
    on fleets that stayed put.
  - Fleets routed to their own planet still lacked it in year 2, and so
    did a remote-mining AR Mini-Miner.
- **Route warp, CONFIRMED (SL-04..07, 28 of 28 warps).** Waypoint 1 is
  the route destination with task 8. The warp is the engine's ideal
  warp, stepped down while `trunc(trunc(d/w)/w)` is unchanged and while
  the leg costs more than the fuel aboard.
  - The dock rule applies only when the destination is the builder's
    own planet with a dock and both planets have starbases: Scout 7 and
    QJ5 9 at 72 ly, where the no-dock rule gives 5/5. The builder's Fort
    and the other player's Station gave the no-dock warps.
  - Safe gates at both ends gave warp 11. Beyond the gate's 250 ly range
    the dock rule applied.
  - A route to the building planet itself gave warp 2.
  - Route words are planet + 1 and survive the turn.
- **The 512-fleet limit, CONFIRMED (SL-08..10).**
  - At 511 fleets, the next item makes fleet 511 and the following item
    joins it.
  - At 512 with no fleet at the planet, ships are not built, their
    queue items go, and their minerals are spent (12/6/13 kT below the
    control). Research could not be compared, because both runs were at
    tech 26.
  - At 512 with fleets at the planet, the lowest-numbered fleet whose
    stack stays at most 32765 receives the ships.
  - The merged damage follows the prediction: 10 Scouts at 50% / 100
    units plus 1 gave 45% / 125. At 300 units it gave 45% / 375. The
    starbase's repair of 100 units that year came afterwards (observed
    25 and 275).
- **Default orders, CONFIRMED (SL-11).** An AR builder's new Mini-Miner
  has waypoint 0 task remote mining; a JOAT builder's has task none.
  The AR miner did not mine in its build year and did in year 2.
  - Not predicted: an AR planet with no mines and no miner gained
    +19/+3/+27 kT a year (control).
- **Replacing a starbase, CONFIRMED (SL-12).**
  - Station → Dock and Death Star → Ultra Station removed the queued
    ships; Dock → Station and Station → Station did not.
  - A replaced starbase keeps its damage, which is then repaired as
    usual: 200 → 150, the same as the unreplaced control.
  - An Orbital Fort builds ships.
  - A Space Dock built a 574 kT Mini-Miner (LEGACY BUG: no dock-size
    check).

### Round 8 (CB-050, CB-051)

Predictions from the decomp combat pass, restated in the experiment
READMEs and committed before the runs (2a7107c). Each setup ran on 6
distinct streams, and the decomp's battle replay matched every move in
all 18 runs and every hit in CB-051.

- **Torpedo estimate shield term, CONFIRMED (CB-050, 6 of 6).** A
  shielded runner (tactic 0) facing an Upsilon Torpedo stack and a Jihad
  Missile stack that never fire moved to (9,9) and stayed there for
  7 moves before leaving. The unshielded control alternated between
  (9,9) and (8,9) in all 6 streams, starting on (9,9) in 4 of them and
  on (8,9) in 2. The shield term in the estimate decides between the
  two squares.
- **Secondary target fallback, CONFIRMED (CB-051, 6 of 6).** A stack
  whose primary target type (starbase) has no match on the board moves
  on its secondary (armed ships) from its first move. A "freighters,
  else any" stack falls back to "any" after the freighter leaves; the
  full replay through fire shows the fallback is rechecked on every
  move.

### Round 9 (CB-052)

Prediction from the decomp combat pass, restated in
`experiments/cb052/README.md` and committed before the runs (ac73ab4).

- **No leftover after a starbase hit, CONFIRMED (CB-052, 6 of 6).** Ten
  destroyers with one Colloidal Phaser each (plan: starbase, else any)
  first fired in round 2 at distance 3, putting 234 into an unarmed
  Orbital Fort with 100 armor. A stack of 5 enemy destroyers sat on the
  Fort's square in range, on a plan with no target type present. Each
  stream's fire action held one record, the Fort destroyed. A carry
  would have added a record on that stack (133 damage). The stack never
  moved and was first hit in round 3. Every hit replayed.

### Battle plans through the client (BP)

The original client gave the orders (`tools/fleetlab/client-orders`), and
one pinned host year applied them. Predictions from the decomp lane's
battle-plan rules were committed first (5aaa4d1). Details:
`experiments/bp/README.md`.

- **Delete renumbering, CONFIRMED (BP-1).** With plans 0..6 and fleets on
  plans 3, 5, 2 and 6, deleting plan 3 left six plans. The fleets ended on
  2, 4, 2 and 5: every fleet on a plan at or above the deleted one moves
  down one, so the users of the deleted plan get the plan before it, not
  plan 0, and later plans keep their identity (P5 and P6 kept their
  fields). The client warns before deleting a plan that fleets use, and
  its Delete is disabled for plan 0.
- **Plan limit in the client: 15, MEASURED (BP-L, twice).** The client
  refused a 16th plan (Copy did nothing), and the host kept 15. After a
  delete the client copied again. The host's own limit of 16 can't be
  reached with client orders, so it stays BINARY-ONLY.
- **Stale single-human Default: MISSED (BP-2).** Three single-player games
  made one after another in one client session all had attack-who 2 on
  Default for both players. The predicted carry-over of the single-human
  setting to the next game did not show in this path.

### Resolved reconciliation

- Energy Dampener frigate token mass: the battle record shows 19 (CB-002
  C8), which is the game's part-table sum (Frigate 8 + Long Hump 6 9 +
  Energy Dampener 2). An earlier figure of 23 came from a binary-analysis
  tool that defaulted to 3 dampeners in the slot; it was not a game
  discrepancy.

### Not tested

Salvage at more than one point (E-8), the firing live-token recheck (no
observable effect), minefields. Mystery Trader items from battle were
never observed (CB-046). Bombing and invasion: see
"Planet Takeover".

## Scanning

Status: MEASURED (SC-001 to SC-023, 25 valid runs, 2026-10-07; cloud
oracle). Predictions
S-1..S-24 from the private binary reading (stars-decomp
`docs/scanning-predictions.md`, PR #6 at 3b5de74) were restated as a
behavior model (`experiments/sc/sclib.py`) and committed with every case
before the runs (`experiments/sc/README.md`; commits 91b46a5, 376cc45,
04e892f). CONFIRMED below means the rule agreed with the oracle in every
case that tested it; the counts say how many. This section states behavior
only.

### Method

- Universe "Combat Lab" (`docs/ORACLE.md`), two JOAT players, one pinned
  generation 2400 → 2401 per run (`tools/fleetlab/pinned-turn`). Both
  homeworlds' planetary scanners removed (`planet N scanner none`) unless
  the run tests planet scanners; tech 26 everywhere unless stated;
  stationary fleets; viewers are player 0.
- Targets sit at exact integer squared distances d² from one viewer, in
  pairs just inside and just past each predicted bound. For every case the
  case table names the plausible alternative rules that would predict the
  other outcome.
- Observation: each player's 2401 `.M` section (`combatlab dump`): partial
  fleets (kind 3) or cargo-bearing ones (kind 4), planet report level and
  starbase bit, foreign design blocks (partial or full), other players'
  blocks. `experiments/sc/check.py` compares each case and also the whole
  view of both players with the model.
- Result: 453 cases in 25 runs, all as predicted, and no other
  difference in either player's view (fleets, planets, designs, player
  blocks). One further run, SC-021, was invalid: the game removed a
  scanner part above the owner's tech from the design, and the view
  matched the stripped design (`docs/ORACLE.md`); SC-023 repeated the
  test with legal tech.
- SC-001 regenerated under a different random stream (cycles 30000) gave
  different bytes but the same views.
- Raw files, dumps and checks: private `stars-oracle-apparatus`,
  `evidence/sc/`.

### Ranges

- **Ship scanners (S-1, CONFIRMED at the edges tested).** Normal range:
  Rhino 50 (d² 2500 seen, 2501 not), Mole 100 (10000 / 10001), Bat 0
  (nothing at 1 ly). Penetrating range (edges below): Ferret 50,
  Chameleon 45, Dolphin 100, Robber Baron 120, Elephant 200. Distance is
  compared as d² ≤ R²; a target 50.01 ly from a 50 ly scanner is not
  seen.
- **Several scanners on one design (S-2, CONFIRMED).** Ranges combine as
  ⌊⁴√Σ rᵢ⁴⌋: two Rhinos on a Large Freighter reach d² 3481 (59) but not
  3482.
- **No combination across a fleet (S-3, CONFIRMED).** A fleet uses its best
  design's range: a fleet of two Rhino designs and a fleet of two Rhino
  ships both missed a target at 55 ly.
- **JOAT hull scanner (S-10, CONFIRMED).** A JOAT Scout with no scanner
  part scans 20·elec / 10·elec (electronics 10: deep space 200 seen,
  √40001 not; planet at 100 reported, √10001 not). With a scanner part
  the two combine like S-2: Scout + Possum at electronics 10 saw 214 ly
  (d² 45796) and not √45797; Scout + Elephant at electronics 16
  penetrated to 217 (planet at d² 47089 reported, 47090 not), past the
  Elephant's own 200.
- **NAS (S-9, CONFIRMED).** Ship normal ranges double (Rhino 100: 10000
  seen, 10001 not); ship penetrating ranges stay (NAS Ferret still
  reported the planet at d² 2500 and saw the freighter orbiting it).
  Planets use the best non-penetrating planetary scanner, doubled:
  electronics 10 / energy 3 / bio 3 gave 560 ly and no penetration
  (every deep-space freighter seen, none of 13 orbiting ones, no planet
  reports).
- **Planet scanners (S-7, S-8, CONFIRMED).** A planet scans with the best
  planetary scanner the owner's current tech allows: electronics 5 →
  150 ly, 6 → 220, and electronics 10 with energy and bio 3 → 320 with
  160 penetration (planets within 160 reported; freighters orbiting
  planets within 160 seen, beyond 160 not). The homeworld's installed
  scanner did not limit this.

### Penetration, planets and orbit (S-5, S-6, CONFIRMED)

- Planets are reported only through penetrating range: a Mole 30 ly from
  a planet reported no planet at all; with Ferret, Chameleon, Dolphin,
  Robber Baron and Elephant the planet at d² = P² was reported and the
  one at the next representable d² past it was not.
- A fleet in orbit is seen only within both the normal and the
  penetrating range: a freighter orbiting 30 ly from a Mole viewer was
  unseen, and at each penetrating edge the orbiting freighter was seen at
  d² = P² and unseen just past it.
- The cloak test uses the penetrating range for an orbiting fleet: a
  Stealth (35%) freighter orbiting the edge planet was unseen, while one in
  deep space at the same distance was seen.

### Cloaking (S-12, S-13, S-14, CONFIRMED)

- Cloak points: Stealth 70, Super-Stealth 140, Ultra-Stealth 540,
  Transport Cloaking 300. A fleet's points are weighted by stack mass and
  divided by the fleet's mass plus its cargo (not fuel): u =
  Σ(points·stack mass) / (Σ stack mass + cargo). Percent: u/2 up to 100;
  50 + (u−100)/8 up to 300; 75 + (u−300)/24 up to 612; 88 + (u−612)/64
  up to 1124; 96 (97 from 1380) below 1612; 98 above (all divisions
  truncate).
- Detection bound for cloak c: d² ≤ ⌊⌊(100−c)·R²/100⌋·(100−c)/100⌋.
  Tested against R 50 (c 35, 17, 10, 55, 75, 85 and a mixed fleet at 18),
  R 59 (c 26, 31, 45, where a single rounding would differ by one) and
  R 100 under NAS (c 35). Shrinking the range first (⌊R(100−c)/100⌋) is
  ruled out (SC-001 cases at d² 1053, 1721, 505, 153, 53).
- Cargo dilutes: one Stealth Small Freighter (31 kT) is 35% empty, 17%
  with 31 kT of cargo, 10% with 70 kT. Fuel does not (130 mg of fuel left
  it at 35%). A Stealth freighter and a plain one in one fleet are 18%,
  not the better stack's 35%.
- Tachyon Detectors scale the target's cloak by 95% (one) and 93% (two),
  rounded down: against Transport Cloaking (75%), a Mole saw to d² 625
  with none, 841 with one (cloak 71) and 961 with two (cloak 69; rounding
  to 70 would stop at 900).

### Co-location and orbit reports (S-4, S-15, CONFIRMED)

- A fleet at exactly the viewer's position is seen regardless of the
  viewer's scanner or the target's cloak: a scannerless freighter saw a
  98% fleet on its own square, and that blind 98% fleet saw it back. One
  ly away, neither a blind nor a Bat Scanner viewer saw anything.
- A planet orbited by a scannerless fleet is reported at level 1, by any
  scanner (Bat included) at level 3, by a Robber Baron at level 4.

### Starbases (S-16, CONFIRMED)

A planet inside penetrating range whose starbase cloak c gives
d² > ⌊(100−c)²·P²/10000⌋ is reported without its starbase (level 3, the
starbase bit clear, no starbase design sent). Dolphin (P 100) against a
Space Station with one Stealth Cloak (35%, unweighted points): starbase
shown at d² 4225, hidden at 4226; with two (55%): shown at 2025, hidden
at 2026.

### Disclosure (S-20, CONFIRMED)

- Designs of seen enemy ships arrive partial (hull and mass); a War
  Monger viewer receives them in full (SC-015, whose race was over its
  point budget and was degraded in the generated year, and SC-015L, a
  legal War Monger race with five cheap LRTs).
- A Claim Adjuster viewer receives each known player's block with that
  player's habitability ranges and every tech level zero; with no contact
  (SC-016N) no block for the other player is written at all.
- Pick Pocket and Robber Baron viewers see the cargo of an enemy fleet at
  their exact position (kind 4); 30 ly away, or with a Rhino at the same
  position, the fleet arrives without cargo.

### Allies (S-23, CONFIRMED in one run)

Setting both players to friends (SC-001F) left both views identical to
SC-001: allies do not share scanner coverage.

### Universe objects (S-17, S-18, S-19, IT gates, SD detection: CONFIRMED)

Universe-objects corpus OB-011..OB-014, OB-017, OB-018 and OB-020 (section
"Universe objects" below for method). Viewer player 1; homeworld scanner
removed; positions are those after the year's wormhole moves and packet
moves.

- **Minefields and wormholes the viewer does not know** are seen within
  R/4 of a normal scanner or within a penetrating range. Rhino on a Small
  Freighter (R 50, P 0): fields at 12 ly seen and at 13 and 40 ly not; a
  wormhole 34 ly away after its move not seen, one 10 ly away seen
  (OB-018 A, B, D, H, I).
- A fleet inside a minefield sees it, whatever the distance to the centre
  (OB-018-C, 30 ly; OB-011).
- **A minefield the viewer already knows** (its "known" mask holds the
  viewer) is seen within the full normal range: 40 and 50 ly seen, 51 not
  (OB-018 E–G; OB-011 at 40 and 51 with R 66).
- **A wormhole the viewer already knows** (its "seen" mask holds the
  viewer) is seen within the full normal range, like a known minefield. A
  known wormhole 34 ly from a Rhino freighter was seen; an unknown one 37
  ly from the other freighter was not (OB-020 A, B). A known wormhole far
  from every viewer scanner was not in the file (OB-011-H, OB-020-C).
- Packets are seen within the normal range: about 48 ly seen and 53 not
  (OB-018 J, K). A packet's mark from the host file or from an earlier
  player's pass does not make it visible (OB-017 D–F).
- The Mystery Trader is in every player's file, 69 ly or more from any
  scanner (OB-011-J).
- Seeing another player's minefield or packet, and none of that player's
  fleets or planets, still put that player's block in the viewer's file
  (OB-011, OB-018). In OB-017 the viewer saw only wormholes and got no
  block for the other player.
- **Packet Physics:** every packet appears in a PP player's file, and a
  moving PP packet scans as a penetrating scanner of range warp²: a warp-5
  packet saw a fleet and a minefield at 20 ly and missed both at 30 ly
  (OB-012).
- **Interstellar Traveler:** an IT player sees an enemy planet with a
  stargate within its own gate's range at level 3: 75 ly from a range-250
  gate it was level 3, at 259 ly level 0, and a starbase without a gate
  at 138 ly level 0 (OB-013).
- **Space Demolition:** an SD player's minefield shows it enemy fleets
  inside the field that are not orbiting a planet. Of three scouts, the
  one in deep space inside the field was in the SD player's file; the one
  orbiting a planet inside the field and the one far away were not
  (OB-014-B, one stream).

### Round 4: rules SCANNING.md marked BINARY-ONLY (SC-024..SC-033)

Predictions were committed before the runs (3547942, follow-ups SC-032 and
SC-033 in bb65db9, SC-034 in 18d99b2); `experiments/sc/README.md` has the case tables and
`experiments/sc/round2.py` the checker. One pinned stream each (cycles
20000), 2400 → 2401. Both players JOAT at tech 26, no planetary scanners,
bare starbases. 86 cases, 4 of them recorded only: 77 held and 5 did not.
Two checks were corrected after the run, without changing a predicted
rule: the dump now decodes heading bytes (stored as value + 127), and the
defense estimate applies the operable cap SCANNING.md states.

**Held (MEASURED, one stream each):**

- **Fleets at your planets.** An enemy fleet orbiting the viewer's planet
  is seen with no planetary scanner and no viewer fleet: a 98% Ghost at
  the homeworld and a plain freighter at a colony without a starbase. The
  same designs 1 ly away in deep space were not (SC-024 A–D). A fleet at
  the planet's exact position *without* the orbit flag was also seen
  (SC-024-E, recorded only), so the rule may be positional.
- **Starbase and owner in a position-only report.** A blind freighter
  orbiting an enemy homeworld with a starbase got level 1 (no
  environment, estimates 0) with the starbase bit and the partial
  starbase design, and the owner's block (partial) arrived although
  nothing else of that player was seen. The planet's owner saw the
  orbiter with no planetary scanner. 1 ly away in deep space: nothing,
  either way (SC-025, SC-026; SC-024 for player 1's view of player 0's
  homeworld).
- **Heading.** Six moving fleets: the shown vector is the waypoint minus
  the start position, halved toward zero while a component is ≥ 128:
  (300,100) → (75,25); (50,−120); (−127,0); (−128,3) → (−64,1); (300,−7) →
  (75,−1); (−1,−395) → (0,−98) (floor halving would give (75,−2) and
  (−1,−99)). Warp is the waypoint's warp. In the file each component is
  stored as `value + 127` in one byte; a fleet that did not move stores
  0/0 and warp 0 (SC-027). A fleet that reached its waypoint this year
  showed (10,0) warp 5, the vector of the move it finished (recorded
  only).
- **Partial fleet mass and cargo.** Ship mass plus ironium, boranium,
  germanium and colonists, without fuel: 29; 29 + 10 + 20 + 30 + 40 = 129;
  two ships with 50 kT of colonists 108. Cargo is shown as 0 (SC-027).
- **Defense coverage estimate.** `max(1, min(15, trunc((104 − k)/6)))`,
  `k = round(100·(1 − v/1000)ⁿ)`, Neutron Shield `v = 38`, with `n` the
  operable defenses: 1, 3, 5, 10 defenses → 1, 2, 3, 6; 0 → 0. Planet 12
  (40 defenses, hab below 0, so at most 10 operable) → 6; planet 4 (100
  defenses, population 104,400 → `ceil(1044/25) = 42` operable) → 14. The
  committed prediction left the operable cap out (13 and 15); SCANNING.md
  states it, and with it all 9 planets match.
- **Population estimate.** All 9 estimates (in 400s) fall in the stated
  range computed from the year's final population, including 300
  colonists → 1 (one stream; the draw itself is random).
- **Three Tachyon Detectors** on one design: factor 91. A 75% target
  (68%) seen at d² 27688, not at 27689 (SC-033); an 85% target (77%) seen
  at 14297, not at 14305 (SC-028).
- **Detectors over designs and ships.** A fleet's factor comes from its
  best single design: Mole + 1 detector with a 1-detector design, and two
  Mole + 1 detector ships, both 95 (d² 841 seen, 842 not); Mole + 2 with a
  1-detector design 93 (961 seen, 962 not). Detectors do not add up
  (SC-029).
- **Super Stealth.** A plain SS freighter is 75% (d² 5625 seen, 5626
  not); with 50 kT of cargo still 75% (dilution would have given 51%).
  The SS player's bare Space Station is 75%: at d² 3600 from a P 200
  viewer the planet was reported (level 3) without its starbase. JOAT →
  SS with `lrt 1 0x1b80` gave no message 0x117 (SC-030).
- **Langston Shell cloak points** (SC-034, added later): 20 per shell. One
  shell on a Small Freighter gives 10% (seen by a Mole at d² 8100, not
  8101); five on a Super Freighter give 100 points, 50% (seen at 2500,
  not 2501).
- **Design disclosure after battle.** A Laser Cruiser and a Laser
  Destroyer that fought each got the other's design in full, the
  destroyed Destroyer included. Designs seen without a battle stayed
  partial (SC-031).

**Did not hold:**

- **Blind orbit of an owned planet without a starbase gives a normal
  report**, not position only (SC-024 planet 20, SC-031 planet 12,
  SC-032). SC-032 separated the readings: a blind freighter in orbit got
  level 3 (environment, population and defense estimates; no surface
  minerals) at an enemy colony without a starbase and at an enemy
  homeworld whose starbase was removed; level 1 at an enemy colony with a
  starbase and at an unowned planet. So the starbase, not the homeworld
  flag, decides. SCANNING.md ("position only if that fleet has no
  scanner") covers only the unowned and starbase cases. MEASURED; the
  cause is not known (sent to the scanning decomp).
- **No planet report from a battle.** A scannerless Cruiser that fought
  at an unowned planet, and one that fought at an enemy colony with a
  starbase, got level 1 like a blind orbiter (SC-032). The battle-report
  rule in SCANNING.md ("a fleet that bombed, fought or hit a minefield at
  a planet gives a normal report") did not show for fighting; bombing and
  minefield hits were not tested. SC-031's level 3 at planet 5 is the
  no-starbase rule above.
- SC-028-T75-out is a setup artifact, not a rule: its fleet was placed at
  y 920 and the game put it at y 1000, inside the bound. SC-033 repeated
  the case from the centre.

### Design knowledge across years (SC-037, MEASURED)

Read from the AIX computer-player corpus (`PARITY.md` "Computer players (AI-0..AI-25)",
"Corpora"): six computer viewers' turn and history files after each of 61
generations, 2400–2460. No experiment was set up for it.

- **Turn file: this year's sightings only.** Another player's design is
  in a viewer's turn file only in a year when that viewer sees one of its
  ships or starbases, or met it in a battle. 2,599 of 2,625 foreign design
  records matched a fleet or starbase in the same file; the other 26 were
  all full records, consistent with designs disclosed by a battle in which
  the ships died. A design sighted again later is partial again unless it
  was disclosed again that year: 431 records went from full to partial in a
  later turn file, every one with the same hull.
- **History file: kept, never downgraded.** The history file after year
  `y + 1` held exactly the history file after year `y` plus the turn file
  of year `y`, each design at the higher of the two levels: 2,320 of
  2,320 turn-file records. Over 4,364 year-to-year comparisons no design
  left the history file and no full record became partial; 2,219 records
  (305 of them full) stayed while that year's turn file did not show the
  design. Once, a history record took a new hull (starbase slot, partial
  both times) the year after the turn file showed a different design in
  that slot.
- Not observed: a full history record replaced by a different design in
  the same slot, and whether a design its owner deleted is ever removed.
  These were computer players' history files, which the host writes; a
  human player's history file is written by the client and was not
  examined.

### Space objects in player files (SC-038, MEASURED)

Question: when a player sees a space object, how much of the host's
record of it reaches the player's turn file, and does any of it stay in
the player's history file? Read from existing evidence (`PARITY.md`
"Computer players (AI-0..AI-25)", "Corpora": OB, MF and AIX); no
experiment was set up for it. Raw comparison: private
`stars-oracle-apparatus` `evidence/sc/sc038`.

Method: every object record in a turn file after the year that the
viewer does not own (wormholes and the Mystery Trader always count) was
compared byte for byte with the host file's record of the same object.
Turn files: both players' files of every OB and MF run (135 host files,
270 turn files; the SC runs hold no objects). History files: the six
AIX computer players' files after each of 61 generations (366 files).

- **Turn file: the whole record.** 3,381 records compared: minefields
  3,198, mineral packets 23, salvage 18, Mystery Trader 24, wormholes
  118. Every one had a host record of the same object, and every one
  equalled it except the per-player markers, which held only the
  viewer's own entry of the host's value: in minefield records the
  "known" word differed 513 times and the "seen" word 513 times; in
  wormhole records the "known" word differed 2 times.
  The objects came from OB-001..OB-031 (and an OB setup probe) and
  MF-1..MF-15; the per-kind run lists are in the raw comparison.
- **Wormhole records (follow-up, adding the WT runs: 364 turn files,
  345 wormhole records).** The partner id, the class-and-years word and
  the whole "knows where it leads" record equalled the host's in all 345:
  163 records named the partner although the viewer had never travelled
  through (23 of them in files without the partner end), and 27 showed
  another player's entry while the viewer's own was clear. Class 3
  appeared only where a WT start file wrote it. Raw comparison:
  `wormholes.py` and `wormholes.txt` in the same evidence directory.
- **History file: no objects.** None of the 366 AIX history files held
  an object record.
- Not examined: a human player's history file, which the client writes.

### Not tested

SD detection of cloaked fleets (S-21, random), AR planet scanners (S-11),
chase retargeting (S-24), scanners on more than two players, planet
reports after bombing, minefield hits or a lost planet, built-in scanners
in Mega Poly Shell, Multi Contained Munition and Langston Shell, cloak
points of non-device parts, the Improved Starbases starbase bonus, and
headings of fleets travelling by stargate or chasing a fleet.

## Planet Takeover

Status: MEASURED (TK-001 to TK-007, 2026-10-07; cloud oracle). Predictions
from the private binary reading (stars-decomp `docs/takeover-predictions.md`
T-1..T-35, PR #8) were committed before every run
(`experiments/tk/README.md`, which has every case, prediction and value).
This section states behavior only. Populations are in **units of 100
colonists** (the file's unit) unless written as colonists.

### Method

- Combat Lab universe (`docs/ORACLE.md`), one generation 2400 → 2401 per
  run with the random stream pinned (`tools/fleetlab/pinned-turn`). Specs
  from `experiments/tk/gen.py`; one case per planet, up to 21 per run.
- Player 1 owns the target planets, environment 50/50/50 (100%
  habitability; both races are the same JOAT race, growth 15%), no
  production queue. Player 0 attacks: bombers orbit the target from the
  start; transports and colony ships arrive this turn from 20 ly
  (waypoint 1 with the task), or sit in orbit with the task on waypoint 0.
- Player 0 at tech 26 in every field from run2 on (see "Design parts
  dropped" below). Mutual enemies unless stated.
- Values read from the 2401 `.HST` with `combatlab dump` / `hst-edit dump`.
  Raw files: private `stars-oracle-apparatus`, `evidence/tk/`.

### Order within the turn (CONFIRMED)

- Population growth (and production, research) happens before bombing,
  and bombing happens before colonists that **arrive** this turn land.
  Every bombing and arrival case matched only when computed on P', the
  population after this year's growth.
- A transport already **in orbit** with an unload-colonists order lands
  before growth: 100 colonists units against 87 left 20, which then grew as
  the attacker's colony to 23 (T-5).
- A colony ship already in orbit with a colonize order colonizes before
  growth (25 → 28 the same year); one that arrives colonizes after growth
  (exactly the 25 carried) (T-1).
- Research done this year applies to this year's bombing: player 1's
  energy rose from 3 to 5 during TK-001 and its defenses then covered as
  Missile Batteries (T-8).
- A starbase destroyed in this year's battle no longer protects the
  planet: the bombers bombed it in the same year (T-2).

### Who bombs (CONFIRMED)

- Only planets owned by another player are bombed, and any starbase,
  even an unarmed Orbital Fort, prevents bombing (T-3).
- The bombing fleet's battle plan "attack who" decides: "nobody" and
  "player 0 only" (the attacker itself) did not bomb; "player 1 only" and
  "everyone" did; "enemies" bombed an enemy but not a neutral, and with
  players neutral "player 1 only" and "everyone" still bombed. With
  players friends, "everyone" bombed (T-19).
- All of one player's fleets at a planet bomb as one: their bombs are
  summed into one pass (10 Cherry in two fleets = 25%, not two passes)
  as soon as **one** of them has an attacking plan, whatever the others'
  plans and whichever comes first in the fleet list. A Laser Frigate with
  an attacking plan and no bombs triggered the bombing by a bomber fleet
  whose plan was "nobody" (T-20). This contradicts the binary reading's
  medium-confidence detail that an earlier non-attacking fleet is left
  out.

### Kill arithmetic (CONFIRMED)

Bomb kill rates in tenths of a percent and installations per bomb, as
used below: Lady Finger 6/2, Cherry 25/10, LBU-17 2/16, LBU-32 3/28,
Hush-a-Boom 30/2, Smart 13/0, Peerless 50/0.

- **Normal bombs add.** A = Σ kill rates (permille), M = minimum kill =
  3 units per bomb for Lady Finger, Black Cat, M-70, M-80 and Cherry
  only. Kill = floor(P'·A/1000), plus one unit with probability
  (r + 1)/1000 when the remainder r is non-zero; a zero kill becomes 1
  when A > 0; then at least M, at most P'. 10 Cherry on 920 → 230 (25%,
  not 1 − 0.975¹⁰); 1 Lady Finger on 10 → 3 (the minimum); 1 LBU-17 on
  10 → 1 (no minimum); Hush-a-Boom on 50 → 1 or 2, never 3.
- **Smart bombs multiply:** S = 1000 − 1000·Π(1 − kill/1000), rounded;
  kill = floor(P'·S/1000), at most P' − 1, so smart bombs never empty a
  planet. 20 Peerless: 1150 → 412 (64.2%); 1 → 1.
- **Smart bombs act first,** normal bombs on the rest: 10 Smart + 10
  Cherry on 921 → 606.
- **Installations** (I = Σ installations per bomb): factories lose
  floor(I·F/T) (+1 with probability (I·F mod T)/T), defenses likewise,
  mines take the remainder of I; T = mines + factories + defenses.
  LBU-32 on mines 30 / factories 30 → 16 / 16; LBU-17 on mines 20 /
  factories 10 → factories 5 or 4, mines always the rest of 16.
- **Retro bombs** move every environment axis toward the original by one
  click per bomb, each axis separately: 3 Retro on 55/47/52 (original
  50/50/50) → 52/50/50 (T-16).
- **Orbital Construction Module counts as a bomb**: a minimum kill of 20
  units per module with no percentage. One OCM ship (plan "enemies") took
  100 → 80 (T-17, the reading's least certain item).
- **Multi Contained Munition counts as a bomb**: 2% kill, minimum 3
  units, 5 installations per item. One MCM frigate: 100 → 97, mines
  10 → 5 (T-18).

### Planetary defenses against bombs (CONFIRMED)

- Coverage per defense c = 1% (SDI) or 2% (Missile Battery): the
  planet owner's best defense at its **current** energy tech, not the
  one built. Counted defenses n = min(installed, the owner's
  habitability cap (not varied here: 100 at 100%), ceil(colonists/2500)).
- s = (1 − c)ⁿ; normal kill rate and minimum ×s, smart ×(1 − c/2)ⁿ,
  installations ×(1 − (1 − s)/2), each rounded to nearest.
- 100 SDI, 20 Cherry: 1000 → 666 (40 counted), 100 → 42 (only 4 counted
  at 10,000 colonists, so the minimum 58 decides); 20 Smart: 1000 → 812,
  no defense lost. With Missile Batteries the same cases gave 777, 45 and
  846.

### Ground combat (CONFIRMED)

- Attacker strength per player = floor(colonist units·110/100) (165 for
  WM, not tested), times s' = s + (1 − s)/4, i.e. defenses work at 75%
  against troops. Defender strength D = population units (×2 for IS, not
  tested).
- D > strength: all attackers die and the defender loses
  floor(P·strength/D): 200 vs 110 → 90.
- D ≤ strength (a tie goes to the attacker): one attacking player keeps
  floor(troops·(strength − D)/strength) units, at least 1: 100 units
  (strength 110) vs D 100 → 9; vs D 110 → 1; 600 vs 500 with 20 SDI
  (strength 569) → 72; 300 vs 200 with 10 SDI (strength 310) → 106. With 20 Missile Batteries the 600
  attackers had strength 495 < 500 and the defender kept 5.
- A planet with any starbase refuses the drop: the transport keeps its
  colonists (event id 0x135) (T-28).
- Unloading colonists on a **friend's** planet (order set in the file)
  invades it exactly like an enemy's (T-29).
- Colonists unloaded on a planet that was unowned at the start of the
  turn do not land; the transport keeps them (event id 0x55). A planet
  bombed empty this turn is different: an arriving transport (no colony
  module) colonized it with all 50 units it carried (T-4).

### Capture (CONFIRMED)

The captured planet keeps its mines, factories, surface minerals,
concentrations and environment, and the population growth carry byte
(set to 37 before growth, 42 after growth and capture: T-27, readable
with `hst-edit dump` as `excess`). It loses its defenses and its
planetary scanner. Whether the new owner's default production queue
replaces the old queue was not tested (no player in this game has one).

### Colonization (CONFIRMED)

- No habitability check: a colony ship colonized a red planet (T-31).
- Colony ship minerals: the new colony received 18/6/17 kT from a tech-3
  colony ship and 4/1/5 from a tech-26 one (Long Hump 6 + Colonization
  Module on a Colony Ship hull). Both equal ¾ of the fleet's design cost
  after miniaturization (25/9/23 and 6/2/7), truncated: `TAKEOVER.md`,
  "Colonization" (CONFIRMED there, T-30).
- **Contested colonization (asymmetric, LEGACY BUG candidate).** Two
  players' colony ships arriving at the same unowned planet: strengths
  as for troops. Player 0 25 vs player 1 12: player 0 got it with all 25.
  Player 0 12 vs player 1 25: player 1 got it with 12, reduced by the
  lower-index player's strength (25·(27 − 13)/27). Equal 25 vs 25: nobody
  got it, both ships were consumed, and the planet received both ships'
  minerals (T-32).

### Random roundings (MEASURED)

Outcomes stayed inside the reading's predicted sets in every run. Over 7
distinct random streams: Hush-a-Boom on 50 gave 48 in 42 of 98 cases
(predicted p 0.501); Smart + Cherry on 1000 gave 657 in 5 of 14
(p 0.251); the LBU-17 factory split was 7 / 7 (p 2/3 for the larger
kill).

### Design parts dropped (MEASURED)

With player 0 at tech 3 in every field, the generated year removed Cherry,
Smart, Peerless, LBU-17 and LBU-32 bombs from player 0's ship designs
(slots written back empty) and those ships did not bomb; Lady Finger,
Hush-a-Boom, Retro, Orbital Construction Module and Multi Contained
Munition parts stayed and acted. At tech 26 nothing was removed. This
agrees with the scanning corpus (SC-021: a scanner above the owner's
tech was removed). Hush-a-Boom and Retro are above tech 3 but stayed:
the check removes only parts the owner lacks tech for, and skips
race-restricted parts (Retro) and Mystery Trader parts (Hush-a-Boom, Multi
Contained Munition): `TAKEOVER.md`, "Design parts dropped when the year is
generated" (CONFIRMED in one setting there).

### Round 2 (TK-101 to TK-121)

Status: MEASURED, 2026-10-07. Predictions from `TAKEOVER.md` (and the
rules of stars-elegy #34) committed before each run; specs, predictions
and the checker are `experiments/tk/gen2.py` and `check2.py`; every case
and value is in `experiments/tk/README.md` "Round 2". Combat Lab as above,
except TK-113: TK3, a tiny three-player game (`tools/fleetlab/new-game`,
three players of the PG000 race, Super Stealth, growth 10%). Race changes
were legal (no message 0x117): WM, AR and CA with NRSE, CE, OBRM, LSP and
BET; IS alone; JOAT with UR plus the same five (UR alone was penalized).
CombatLab gained `defqueue`, `defleftover` and `field`, and its dump prints
production queues.

**Ground combat by race (CONFIRMED, T-24).** War Monger troops count 165
per 100 and an Inner Strength defender counts double:

| Attacker | Defender (after growth) | Observed |
|---|---|---|
| WM 100 | JOAT 150 | attacker lands 9 |
| WM 600 | JOAT 500, 20 SDI | attacker lands 248 |
| JOAT 150 | IS 100 | defender keeps 18 |
| JOAT 300 | IS 100 | attacker lands 118 |
| WM 150 | IS 100 | attacker lands 28 |

**Alternate Reality (CONFIRMED, T-33).** An AR transport's unload on an
enemy planet was refused and the fleet kept its colonists. An AR colony
ship (Orbital Construction Module) colonized an unowned planet, which got
a starbase of the owner's starbase design 0. AR colonists in a fleet
**moving** this year lose `trunc((C + 11)·3/100)` when the cargo C is over
10 (TK-107: 100 → 97, 25 → 24 before colonizing; TK-117: 10 and 11 kept,
40 → 39, 200 → 194, and 200 kept by a stationary fleet).

**Default queue and leftover setting (CONFIRMED, T-26).** A planet captured
by invasion and a new colony both got the new owner's default production
queue and its "only leftover to research" setting, in queue order. Alternate
Reality skipped items 0–2 (auto mines, factories, defenses) and Claim
Adjuster items 4–5 (auto minimum/maximum terraform); WM kept all five.

**Claim Adjuster capture.** TK-108 (CA attacker, CA defender) ended with
the captured planet at 50/50/50, its race's ideal: the new CA owner's
end-of-year terraforming covers any revert, so this case could not show it
(a corpus error in the prediction). TK-116, JOAT attacker against a CA
defender: the captured planet went back to its original 55/47/52 (the file
then no longer stores separate original values).

**Claim Adjuster capturing Claim Adjuster (CONFIRMED, T-40, TK-118..120).**
A CA attacker captured a CA planet at 60/40/60 with original 80/20/80. The
environment went back to 80/20/80, then the new owner's end-of-year CA
terraforming moved each axis from the original toward its centre by up to
the best terraform part it may use, never past the centre: 65/35/65 with
axis parts (±15, tech 26, no TT), 50/50/50 with Total Terraform (TT,
±30), and 80/20/80 with no terraform tech (the original then is not stored
separately). A CA planet at 60/40/60 whose owner had only ±3 parts stayed
put: no target inside original ± 3 improved it.

**Scrap (CONFIRMED, T-34).** 30 ships costing 180/60/210 kT in total:

| Where | Minerals |
|---|---|
| own planet with starbase | 144/48/168 (4C/5) |
| own planet, no starbase | 60/20/70 (C/3) |
| UR player's planet with starbase (fleet owner not UR) | 162/54/189 (9C/10) |
| UR player's planet, no starbase | 81/27/94 (9C/20) |
| unowned planet | 60/20/70 on its surface |
| deep space | a salvage object with 60/20/70 (written as a packet-type object with no destination) |

Mineral cargo was added on top. Colonists in a scrapped fleet joined the
fleet owner's own planet before growth (87 + 50 → 157 after growth) and
were lost at another player's planet. A fleet with a second waypoint was
scrapped where it started. A fleet that **arrived** with a scrap order was
intact at the end of that year and scrapped the next year.

**Remote mining (CONFIRMED, T-35).** A fleet with 24 robot points at an
unowned planet with concentrations 100/50/25 mined 24/12/6 kT a year when
it started the year there; one that arrived that year mined nothing until
the next year. Miners at an owned planet (own or enemy) mined nothing.

**Several players bombing one planet (CONFIRMED in one setting).** With players 0 and 2
over player 1's planets, each player's pass was applied in turn, player 0
first: 10 + 10 Cherry on 800 left 450 (one merged pass would leave 400);
player 0 Smart, player 2 Cherry on 40 left 6; player 0 Cherry, player 2
Smart left 9 (the reverse order gives 9 and 6; a merged pass 10).

**Phase-start ownership (CONFIRMED).** An unowned planet colonized before
movement and then bombed empty in the same year still took an arriving
freighter's unload as a colonization (50 landed): the after-movement phase
records owners before bombing. With no colonization, the same unload was
refused and the freighter kept its 50.

**Unload amounts on an own planet (CONFIRMED).** Before movement, unloaded
colonists joined before growth (87 + 50 → 157); after movement they did
not (100 + 50). "Unload exactly" moved `min(v, cargo)`, "set amount to"
moved `cargo − v`, "set waypoint to" moved `v − planet` colonists (capped
by cargo), and unloaded minerals went onto the surface.

**Colonize is tried once (CONFIRMED, T-39).** Every colonize failure ended
the order. A colony ship in orbit at an enemy planet that was bombed empty
the same year, and a freighter with colonists but no colony module at an
unowned planet, both kept their colonists with the waypoint task cleared,
and the planets stayed unowned (TK-121).

**Colonize retries (CONTRADICTED: MISS).** After a tie emptied a planet
(players 0 and 2 dropping 150 each on 100), a player 0 colony ship whose
colonize failed in the same phase did **not** retry: before movement and
after movement alike, the ship kept its colonists, its waypoint task was
cleared (message 0x4e), and the planet stayed unowned with no minerals.
The reading in stars-elegy #34 (a load-phase retry, and the after-movement
LEGACY BUG) is not supported by this case; the binary reading was since
corrected to "colonize is tried once" (stars-elegy #37), which T-39 above
confirms.

**Tech on capture (MEASURED).** Player 0 at tech 3 captured two planets of a
player at weapons 10 (other fields 3). Over 8 cycle settings, weapons went
3 → 4 in 5 and stayed 3 in 3; never above 4 and no other field, consistent
with one attempt per capture sharing a once-a-year gain (predicted chance of
a gain 0.56).

**Colony minerals at intermediate tech (CONFIRMED, T-36).** The Colony Ship
+ Long Hump 6 + Colonization Module left 17/6/15, 12/4/12 and 9/3/8 kT at
tech 5, 10 and 15 in every field: ¾ of the COMPONENTS.md owner cost. With
BET (WM, CA races at tech 26) it left 3/1/4 (JOAT 4/1/5), and an AR Orbital
Construction Module ship 5/2/5: BET miniaturization (80%) applies.

**Design check (CONFIRMED, T-37).** With electronics 7 and everything else
26, LBU-17 (electronics 8) and LBU-32 (electronics 10) were removed whether
the research field was energy or electronics; Hush-a-Boom (Mystery
Trader), Retro (CA only) and every other part stayed.

### Round 3 (TK-201 to TK-203)

Status: MEASURED, 2026-10-07. A sweep of the rules `TAKEOVER.md` still
tagged BINARY-ONLY after round 2. Predictions in `experiments/tk/gen3.py`
and `experiments/tk/README.md` "Round 3" were committed before the runs
(60cac43); `check3.py` summarizes the dumps. Combat Lab, two JOAT players,
enemies; raw files in private `stars-oracle-apparatus` `evidence/tk3/`.
Every prediction held. Fuel at a planet was settled separately (MG-006,
`MESSAGES.md`).

**Order across planets (CONFIRMED, TK-201 A, B; cycles 20000 and
30000).** Freighters 0, 1 and 12 of player 0 invaded planets 14, 3 and 8
before movement: the capture messages came in that order (fleet order),
not planet order. Bombers 2 and 3 over planets 13 and 2: both players'
bombing messages named 13 before 2. Every value matched (captures landed
90, 103 after growth; Cherry pairs took 100 to 94).

**Minerals to another player's or an unowned planet (CONFIRMED, TK-201
C–E).** 50 kT ironium unloaded on an enemy planet without a starbase, one
with an Orbital Fort, and an unowned planet: each surface went 0 → 50, the
fleets kept none, and each owner got 0x02d.

**Deep space (CONFIRMED, TK-201 F).** A freighter unloading 50 kT ironium
and 50 colonists at an empty point lost the ironium (0x02d, no object
created) and kept the colonists (0x165, then 0x04e).

**Loading every colonist (CONFIRMED, TK-201 G).** "Load all" colonists
took all 50 off player 0's planet 12 and off its homeworld 17 (0x02c). Both
planets were lost at growth (0x040: the planet before each had grown) and
were unowned at the end of the year.

**Homeworld mark (CONFIRMED, T-41: MG-005, TK-201 G2, I).** MG-005 (`experiments/mg`) captured player 1's homeworld 8 before movement: it stayed marked under player 0, with player 1's record still naming it. The emptied homeworld 17 kept
its mark at the end of that year and of a second year, with player 0's
record still naming it. Player 1's homeworld 8, captured while player 1 kept
other planets, stayed marked under player 0; player 1's record still named
8 and no other player 1 planet was marked.

**Colonize failures (CONFIRMED, TK-201 H).** A colony ship in deep space got
0x051 and one with no colonists at an unowned planet 0x053; each then got
0x04e, kept its cargo and had its task cleared.

**Mines never go negative (CONFIRMED, TK-202, 12 cycle settings, 10
distinct outcome vectors).** One Lady Finger over 20 Neutron Shields (`I =
1`, mines 1, factories 20, defenses 20): every planet went 1000 → 997, and
the 72 installation outcomes were mines 0 alone (21; predicted chance
0.262), one factory or one defense with mines kept (40), and one factory
and one defense with mines **still 1** (11; never 2). Two Lady Fingers (`I
= 3`): 1000 → 994, mines lost only when exactly one factory and one defense
were lost (7 of 24). Undefended, two fleets: 1000 → 988, mines 10 → 6 and
1 → 0.

**Bombing messages for several fleets (CONFIRMED, TK-202).** 0x169/0x173,
0x16a/0x174 and 0x16f/0x179 as predicted. LEGACY BUG (CONFIRMED): the
installation count in a bombing message keeps the negative mine remainder,
so it reported 1 (and the singular text) when two installations were lost
to `I = 1`, and 3 when four were lost to `I = 3`.

**Tech from scrapping at a starbase (CONFIRMED, TK-203, 12 cycle
settings).** Player 0 scrapped a Scout with Long Hump 6 (propulsion 3) at
each of two starbases of player 1 (tech 0 everywhere) and at a third planet
without one. Player 1 gained propulsion 1 in 8 of 12 settings (7 at the
first starbase; 1 at the second after the first gave nothing; predicted
chance 0.555), never 2 and never another field; the gaining scrap sent
0x13d (field propulsion) instead of 0x141, and the third planet 0x140.
Player 1's leftover research reached energy 1 only in the runs without the
gain (level costs rise with levels held).

### Round 4 (TK-301 to TK-306)

Status: MEASURED, 2026-10-07. The rest of `TAKEOVER.md`'s open list that
legal host-file orders reach. Predictions in `experiments/tk/gen4.py` and
`experiments/tk/README.md` "Round 4" were committed before the runs; raw
files in private `stars-oracle-apparatus` `evidence/tk4/`. TK-303 and
TK-304 ran on copies of the Combat Lab base with random events on (and,
for TK-304, slower tech).

**Laser Battery and Planetary Shield (CONFIRMED, TK-301, TK-302).** Player
1 at energy 10 and 16. On planet 13 (1000 after growth, 100 defenses, 40
counted) 20 Cherry left 811 and 852 and destroyed every defense; on planet
2, 20 Smart left 858 and 874 with the defenses kept. 600 troops against 500
with 20 defenses: strength 469 and 434, so the defender kept 31 and 66
(grown to 35 and 75). All as predicted.

**Load exactly (CONFIRMED, TK-301, TK-302).** 30 colonists from a 100
planet (fleet 30, planet 70 then growth); 40 ironium asked with 25 there
(fleet 25, surface 0); 300 asked with 500 there and a 210 kT hold (fleet
210, surface 290).

**Ancient artifacts (CONFIRMED, TK-303, TK-304, TK-306; amounts MEASURED,
six cycle settings for colonies, three for owned planets).** A colony on an
unowned artifact planet sent 0x05e to the new owner with a field 0–5 (all
six seen) and 122–272 points with 2,500 colonists, 53–196 with 500; the
artifact was gone. TK-304 with slower tech gave identical fields and points
in every setting: no halving. TK-303's owned-planet cases (A1, A4, A5) were
void: Combat Lab had set only the file flag, which the host ignores on a
planet with an installations block, so every owned planet lost its
artifact unseen. After the fix TK-306 held all 12 checks: a capture gave
0x05e to the captor, a defender that beat off 10 troops got 0x05e itself
(392 points, enough to raise construction 3 → 4 that year), and an
untouched owned planet and an own-planet unload kept the artifact with no
message. The TK-303 prediction for A4 (no 0x05e when the defender holds)
contradicted the binary reading it cited; TK-306 C2 follows the reading
and held.

**Mystery Trader parts from scrapping (MEASURED, TK-305, 12 cycle
settings).** A 12-design Hush-a-Boom fleet scrapped at each of player 1's
three starbases (player 1 at tech 0). First starbase: the Hush-a-Boom
(0x13c, player 1's part bit set) in 5 settings, a level in 5 (0x13d:
electronics, propulsion, construction, biotechnology twice), nothing in 2;
the other two starbases always sent 0x141. The electronics level also sent
0x157 (new planetary scanner). Predicted: an attempt passes half the
time, and a passing attempt gives the part with chance 0.215. Observed
10 of 12 first attempts passed and 5 of 10 gains were the part, both above
the model (TK-203 also gained more often than predicted: 7 of 12 first
attempts against 0.33).

**Resolved by replaying the random stream (CONFIRMED, TK-307).** With the
roll at the first starbase placed at the third draw of the year, the
binary rule reproduces every TK-305 run exactly (outcome and field). The
12 cycles values reached only 9 streams, and 3 parts in 7 gaining streams
is within chance. TK-307 then predicted five new cycles values before the
run, including gains at the second and third starbase after earlier
failures; all five matched (four at the expected stream, one at its
listed neighbour). `experiments/tk/tk307.md` has the tables.

### Round 5: manual cargo transfers (TK-501, TK-502)

Status: MEASURED, 2026-10-07, one run each (cycles 20000). The transfers
were given in the original client through client automation
(client-orders, added to `docs/ORACLE.md` by the combat oracle lane): one pinned year from a Combat Lab start
made player 0's turn, the client gave the orders, and a second pinned year
ran them. Predictions (`experiments/tk/gen5.py`, TK-401 to TK-412 in
`experiments/tk/manual-transfers.md`) were committed before the runs; raw
files, order files and screenshots are in private `stars-oracle-apparatus`
`evidence/tk5/`.

| Case | Transfer | Predicted | Observed |
|---|---|---|---|
| TK-401 | 30 colonists to an enemy planet of 100 | defender keeps 67 (77 after growth); 0x000 / 0x003 | as predicted |
| TK-402 | 200 colonists to an enemy planet of 100 | captured with 109 (125); 0x00c / 0x007 | as predicted |
| TK-403 | 200 by hand and 50 by an unload task, same planet | one fight of 250: 159 (182) | as predicted; 0x007 names 250 colonists |
| TK-404 | 30 colonists to an unowned planet | lost, planet unowned, 0x002 | as predicted |
| TK-405 | 100 ironium to an enemy planet | surface +100; 0x042 / 0x044 | surface +100, **no message** |
| TK-410 | 30 colonists to the enemy homeworld (starbase) | lost; 0x058 | as predicted |
| TK-411 | 200 colonists to a friend's planet | captured as an enemy's | as predicted |
| TK-412 | 100 ironium to a friend's planet | surface +100; 0x042 / 0x044 | surface +100, **no message** |

The planets were resolved in the order of the client's order records
(fleets 7, 6, 5, 2, 1), and the unload task's drop joined the manual drop
at its planet. These agree with the XF-1 observation of the combat oracle
lane (colonists lost with 0x058 at a foreign homeworld and 0x002 at an
unowned planet; minerals added), which had no committed prediction.

### Round 7: gifts to another player's fleet (TK-406 to TK-409, TK-413, TK-414)

Status: MEASURED, 2026-10-07, one run each (cycles 20000), given through
the client's fleet panel ("Other Fleets Here", Cargo). Predictions were
revised before the runs (`experiments/tk/manual-transfers.md`) and made
concrete in `experiments/tk/gen7.py`; raw files are in private
`stars-oracle-apparatus` `evidence/tk7/`.

| Case | Gift | Predicted (revised) | Observed |
|---|---|---|---|
| TK-406 | 100 ironium to an enemy fleet with 50 kT free | 50 received, giver loses 100, 0x0dd, no 0x046/0x048 | as predicted; the client did not cap the order |
| TK-407 | 100 ironium to a full enemy fleet | nothing received, giver loses 100, 0x0dd | as predicted |
| TK-408 | 20 colonists to an enemy fleet | received, no message | **the client wrote no order**: colonists stay with the giver |
| TK-409 | 50 mg fuel to an enemy fleet | received, no message | as predicted |
| TK-413 | ironium to a fleet with an unload task | unloaded the same year | void: the task was cleared in year 1 |
| TK-414 | 20 colonists to a friend's fleet | as TK-408 | the client wrote no order |

0x042–0x04d did not appear. The shortfall notice 0x0dd (CONFIRMED) is
sent by the order replay, which places the credit at order time.

### Round 8: a gift to a fleet that moves away (TK-415, TK-416)

Status: MEASURED, 2026-10-07, one run (cycles 20000), given through the
client's fleet panel. Predictions (`experiments/tk/gen8.py`,
`experiments/tk/README.md` "Round 8 predictions") were committed before
the run; raw files are in private `stars-oracle-apparatus`
`evidence/tk8/`. Each receiver moved 49 ly east at warp 7 in the year
the gift was ordered; three player 1 Freighters on the same legs with no
gift are the controls (C0: empty, 0 mg; C200: empty, 200 mg; C100:
100 kT ironium, 200 mg).

| Case | Gift | Receiver after the year | Controls |
|---|---|---|---|
| TK-415 | 200 mg fuel to an empty Freighter with 0 mg | moved 49 ly, 124 mg left | C200: moved 49 ly, 124 mg; C0: did not move, 0 mg |
| TK-416 | 100 kT ironium to an empty Freighter with 200 mg | moved 49 ly, 100 kT aboard, 13 mg left | C100: moved 49 ly, 13 mg; C200: 124 mg |

Both receivers match the control that started with the gift, so the
gift was aboard before movement: it is credited when the order is
replayed. A credit after movement would have left TK-415's receiver
where C0 stayed and TK-416's with C200's 124 mg. No 0x042–0x04d were
sent. (Incidental, one observation: the Long Hump 6 Freighter with 0 mg
did not move at all at warp 7.)

### Round 6: bombing message variants (TK-601 to TK-606)

Status: CONFIRMED, 2026-10-07, one run (cycles 20000). Predictions
(`experiments/tk/gen6.py`, `experiments/tk/README.md` "Round 6
predictions") were committed before the run; raw files are in private
`stars-oracle-apparatus` `evidence/tk6/`.

| Case | Setup | Observed |
|---|---|---|
| TK-601 | one LBU-17 bomber, planet with one factory | factory gone, 1 colonist unit killed; 0x063 / 0x06d |
| TK-602 | as TK-601 plus a second (unarmed) fleet | 0x169 / 0x173 |
| TK-603 | one LBU-17 behind 69 counted Planetary Shields | 9 installations, no colonists (kill rate rounds to 0); 0x067 / 0x071, 87.77% stopped |
| TK-604 | as TK-603 plus a second fleet | 0x16d / 0x177 |
| TK-605 | LBU-17 and a second fleet, planet with one defense | 0x16e / 0x178 |
| TK-606 | three Retro bombs and a second fleet | 8 clicks; 0x17a / 0x17b, no damage message |

Every prediction held. The "installations only, no defenses" and "one
installation, no colonists, defenses" texts are left as not reachable
(`docs/MESSAGES.md` LEGACY BUG summary).

### Not tested

The year's
full draw order through the random stream (owned by the KERNEL
experiments); Alternate Reality `k = 0` in a contested drop (not reachable
with legal orders).

## Universe objects

Status: MEASURED (OB-001 to OB-020, 2026-10-07; cloud oracle). Predictions
O-1..O-40 from the private binary reading (stars-decomp `docs/objects.md`,
`docs/objects-predictions.md`, PR #10) were restated per case and
committed before the runs (`experiments/ob/README.md`; commits c3d94fe,
172ef28, 1c7ae56, 6a78bee, 335c5b9). CONFIRMED below means every case that
tested the rule agreed; the case ids say which. This section states behavior only.

### Method

- Universe "Combat Lab" (`docs/ORACLE.md`), two JOAT players, one pinned
  generation 2400 → 2401 per run (`tools/fleetlab/pinned-turn`, cycles
  20000; the random cases also at five other settings). Combat Lab has
  no objects, so minefields, packets, wormholes and the Mystery Trader
  were written into the start file (`thing` lines, `docs/ORACLE.md`
  "Universe objects experiments").
- Player 0 at tech 26 (no design part stripped), player 1 at tech 3,
  research 0%, mutual enemies unless stated. Each minefield case sits
  alone, with the planets inside it checked by `gen.py`.
- Wormhole creation (O-27) used new games built from definition files
  (`tools/fleetlab/new-game`).
- Raw files, dumps and checks: private `stars-oracle-apparatus`,
  `evidence/ob/`.

### Minefield decay (CONFIRMED)

Each year a field loses p% of its mines, where
p = min(50, 4·N + 2) for a non-SD owner and min(50, N + 2) for a Space
Demolition owner, and N is the number of planets inside the field
(d² ≤ mines). Planet owners do not matter. The loss is
max(p, ⌊mines·p/100⌋), and at least 10 for standard and heavy fields;
speed-bump fields have no minimum of 10. A detonating field adds 25 to p.

- No planets: 1000 → 980; 100 → 90; speed bump 100 → 98 (OB-002 A–C).
- 2 planets: 1000 → 900; 3 planets including the owner's own homeworld:
  2000 → 1720 (OB-002 D, E). SD owner, 2 planets: 1000 → 960 (OB-014-A).
- 22 planets: 40000 → 20000 (the 50 cap, OB-015); SD owner: 40000 → 30400
  (OB-016).
- Decay comes before laying: a field laid this year is first decayed next
  year (OB-002-F).

### Laying (CONFIRMED except where marked)

- A stationary fleet with the lay-mines task lays, per ship, the sum of its
  dispensers' ratings, doubled on Mini Mine Layer (and, per the binary
  reading, Super Mine Layer) hulls: one Mini Mine Layer with two Mine
  Dispenser 40 lays 160; three such ships lay 480; a Frigate with two
  Mine Dispenser 40 lays 80; a Frigate with one Multi Contained Munition
  lays 40; a Frigate with three Speed Trap 20 lays a 60-mine speed-bump
  field (OB-002 F, H, J, K, L).
- Each kind lays its own field: a ship with two Mine Dispenser 40 and two
  Heavy Dispenser 50 laid a standard 160 and a heavy 200 (OB-002-I).
- New mines merge into the layer's own field of the same kind that
  contains the fleet. The count adds, and the centre moves to the
  count-weighted mean, truncated: a layer 10 ly east of its 400 field's
  centre (390 after decay) laying 160 made one field of 550 centred 2 ly
  east (OB-002-G).
- The years word: 0 lays once and clears the task (OB-002-N).
- A Space Demolition fleet travelling toward a lay-mines waypoint lays half
  the amount at its end-of-year position: 80 from a Mini Mine Layer with
  two Mine Dispenser 40 (OB-014-C).
- **A lay-mines task on waypoint 0 holds a non-SD fleet in place.** A
  Mini Mine Layer set to lay indefinitely, with waypoint 1 25 ly away,
  stayed put for three years. It laid the full 160 each year, so its field
  went 160 → 310 → 460 (2% decay with the minimum of 10 in between), and
  both waypoints were kept (OB-019-A, OB-014-D).
- Years word 1 lays twice and then clears the task: 160, 310, then 300
  from decay alone (OB-019-B).

### Sweeping (CONFIRMED)

- A fleet's sweep rating is Σ over its beam weapons of count × damage ×
  range², with range 4 for gatling-type beams (Mini Gun, Gatling Gun) and
  range + 1 on a starbase. Sappers sweep nothing. The rating multiplies by
  the number of ships, and speed-bump fields lose a third of it.
  - Destroyer with 2 Lasers: 1000 → 980 (decay) → 960.
  - Mini Gun DD: 980 → 772 (13·16 = 208, not range 2).
  - Gatling DD in a 2000 field: 1960 → 968 (992).
  - Pulsed Sapper DD: no change.
  - Three Laser DDs in one fleet: 920. Two separate fleets: 940; each
    fleet sweeps in full.
  - Speed bump: 980 → 974.
  - A Laser Fort (2 lasers) starbase inside a field with that planet:
    1000 → 940 (6% decay) → 860 (2·10·4 = 80).
  (OB-001 B–J, OB-007-C.)
- A sweeper never sweeps past itself: a fleet rated 992 sitting 20 ly
  (d² 400) from a 1000 field's centre left 399 mines, so it is still just
  outside the field (OB-001-A).
- A fleet sweeps only fields whose owner its battle plan would attack:
  - plan "attack nobody": no sweep (OB-001-E);
  - plan "enemies" against a neutral: no sweep;
  - plans "neutrals and enemies" and "everyone" against a neutral: sweep
    (OB-007 A, B, E).
- Against a friend's field (OB-008):
  - plan "neutrals and enemies": no sweep;
  - plans "everyone" and "player 1 only": both swept, 1000 → 960
    (MEASURED, one case each);
  - a starbase did not sweep a friend's field but did sweep a neutral's
    (OB-008-A, OB-007-C).
- Sweeping comes after laying in the same year. A 160-mine field laid at
  an enemy homeworld whose Space Station has 32 Lasers was gone at the end
  of the year (OB-007-D).
- A fleet that ends its move inside an enemy field sweeps it the same year
  (OB-010-S: 2940 → 2840 after five Laser DDs crossed and stopped inside).

### Detonation (MEASURED, one case: OB-002-M)

A detonating standard field damaged everything inside it except its owner's
Mini Mine Layer. Every one of the owner's five Laser DDs took 50% of its
armor, every one of the enemy's five Medium Freighters 80%, and the layer
nothing. The field lost 27% (2% + 25%) and nothing more for the hits:
1000 → 730.

### Hits while moving (MEASURED)

- Five warp-9 fleets, each moving only 30 ly inside a heavy field (safe
  speed 6), were never hit in six cycles settings, 30 fleet-years
  (OB-010 H0–H4). The binary reading takes the warp from the distance
  actually travelled (30 ly → warp 6). Warp 9 would give each fleet
  about a 60% hit chance.
- A warp-9 fleet of five Laser DDs crossing 76 ly of a 3000-mine
  standard field gave 3 distinct outcomes in six settings (OB-010-S):
  - no hit, in three settings;
  - a stop at the field's centre (55 ly inside it) in two settings, and
    64 ly inside it in one.
- On a hit:
  - the fleet stopped where it was hit;
  - every ship took 50% of its armor;
  - the field lost 50 before its 2% decay: 3000 → 2950 → 2891. Decay
    first would give 2890.
  - The stopped fleet then swept 100, so the field ended at 2791.
  - Re-checked against the MF-4 year order (stops during movement, then
    decay counting planets inside the field as the stops left it, then
    sweeping; no planet lies inside this field at 3000 or 2950): the three
    no-hit settings ended at 2840 and the three hit settings at 2791, as
    predicted (stars-elegy `experiments/mf/README.md`). The hit settings
    have mine-hit messages (0xc6) at the stop point; the no-hit ones have
    none. No contradiction with MF-4.
- Hit odds per ly and shrink amounts for other field sizes (O-14, O-15)
  are not yet measured.

### Packets (CONFIRMED except where marked)

- **An uncaught packet delivers one ninth of its cargo** to the planet's
  surface, truncated:
  - 1000 kT ironium at warp 10 into an unowned planet: +111 (OB-003-A);
  - 300/200/100 kT: +33/+22/+11 (OB-003-B).
  This contradicts the common player belief that all minerals arrive.
- A planet whose mass driver catches part of the packet receives the caught
  part in full and a ninth of the rest. A Mass Driver 7 starbase against a
  warp-10 packet catches 49%: 1000 kT gave +546 (OB-009-C). A packet no
  faster than the driver is caught whole: +1000, no damage (OB-009-D).
- Decay on arrival keeps at least 10 kT per non-empty mineral: a class-1
  (10%/yr) 100 kT packet arriving with a 5% share of a year lost 10, and
  the planet got ⌊90/9⌋ = 9 (OB-003-C).
- Damage to a populated planet, in units of 100 colonists, with population
  growth controlled (OB-009):
  - 1000 kT at warp 10, no driver, no defenses, 1000 units: 625 killed
    (100·1000/160), leaving 375 (OB-009-F).
  - Against a Mass Driver 7 catcher (49%): 318 killed (OB-009-C).
  - With 50 SDI defenses (tech 3): 418 killed, and the defenses fell to 30
    (OB-009-H).
  - Own packets hurt their owner's planets the same way (OB-009-E).
  - Damage at or above the population leaves the planet uninhabited
    (500 units, OB-009-G, OB-003-G).
- Packets in flight move warp² ly per year whether or not their "moved"
  flag is set. Class 2 keeps 75% of its cargo per year, class 3 keeps 50%
  (OB-003 J, K).
- Packet impacts come before population growth in the year.

### Wormholes (CONFIRMED except where marked)

- An end that does not jump moves by at most 12 ly on each axis, and its
  years counter goes up by 1 (OB-005-A, OB-017).
- A fleet with a wormhole as its next waypoint that reaches it ends the
  year on the partner's position from before that year's wormhole moves
  (OB-005-C: the partner had moved −5,−11 in the same files). A fleet that
  falls short stays in normal space (OB-005-D).
- **MEASURED (OB-005-B, 4 distinct streams):** a class-2 pair inserted
  at 30 years jumped once in eight end-years. In that stream one end
  jumped (moved −59,−25, years reset to 0) and its partner jiggled (years
  31), so the ends roll separately.

### Wormhole creation (MEASURED, OB-006)

New games built from definition files, three seeds per size. Every count
fell inside the binary reading's range; three games per size do not test
the range ends.

| Size | Pairs (seeds 11, 22, 33) | Binary-reading range |
|---|---|---|
| Tiny | 0, 0, 0 | 0–2 |
| Small | 1, 2, 3 | 1–3 |
| Medium | 2, 2, 1 | 1–5 |
| Large | 5, 3, 3 | 3–6 |
| Huge | 6, 6, 7 | 4–8 |

- With random events off there were no wormholes (tiny and huge, three
  seeds each).
- Every end started with years 0 and stability class 0, 1 or 2. Class 3
  never appeared. The two ends of a pair often had different classes.

### Mystery Trader (CONFIRMED, OB-004)

The Mystery Trader works with random events off.

- A fleet at its position with 4999 kT of minerals was kept, whether it was
  stationary or had just moved there. With exactly 5000 kT (colonists not
  counted) the fleet was removed.
- Player 1 (tech 3 everywhere) gave 5000 kT for a research gift and gained
  6 tech levels in total.
- A second player 1 fleet with 5000 kT at the same trader in the same year
  was kept: each player gets one reward per trader.

### Round 5: rules OBJECTS.md marked BINARY-ONLY (OB-021..OB-027)

Status: MEASURED, 2026-10-07. Predictions were committed before the runs
(`experiments/ob/README.md` "Round 5"; pushed as e1873db and 4c63088,
re-applied as c0476b2 and 2cf004d after #42 was squash-merged), one
pinned year each (cycles 20000) unless stated. OB-021 and OB-024 were also
generated at cycles 15000, 25000, 30000, 40000 and 60000. In the base
stream, 44 of 49 predicted cases held. The misses were the two IT packet
cases and OB-025-F1..F3 (wormhole targets). In other streams, OB-024-A and
C missed for a reason outside the objects rules, and OB-021-G's fuel check
missed when a ship was lost. Details below.

#### Stargates (CONFIRMED, OB-021, OB-022)

- Gate travel is waypoint warp 11. A Laser DD jumped 100 ly between two
  100/250 gates and arrived undamaged with its fuel unchanged.
- **Danger.** Every case matched OBJECTS.md's formula:
  - Range is judged by the source gate only. A 150/600 → 100/250 jump of
    372 ly was safe. The reverse jump (danger 12%) left the DD with 60/500
    of its armor as damage.
  - Mass is per ship and is checked against both gates. Super Freighters
    (mass 202) between 100/250 gates had danger 44%. Over 357 ly, range
    and mass multiplied to 50%, not 44%.
  - Every survivor took ⌊pct·armor/100⌋, written as one damage word on
    100% of the ships: 5 DDs at 13% got 65/500, freighters 220/500 and
    250/500.
- **Losses** are random. In 6 streams:
  - 5 DDs at 13% (4% each) lost none.
  - 3 freighters at 44% (14% each) lost one in 3 streams.
  - 3 freighters at 50% (16% each) lost one in 2 streams.
  - When one of 3 ships was lost, fleet fuel went from 100 to 67, and the
    survivors' damage word was unchanged.
- **Refusal.** A ship over 5× a mass limit (mass 502 vs 100) was refused:
  no move and no damage.
- **Cargo dump (LEGACY BUG, MEASURED).** The refused freighter's 100 kT
  ironium was still unloaded onto the source planet. A successful jump
  unloaded 100/50/25 kT and 10 kT of colonists onto the source planet. The
  population added before growth (1010 → 1161).
- No destination gate, or an enemy's source gate, meant no jump.
- **IT (OB-022):** at 13% danger, all 5 DDs survived with the same damage.
  Neither the refused nor the successful freighter unloaded its cargo.

#### Stargates, round 2 (GT-001, GT-002)

Pinned years (cycles 20000) on a new medium universe (`experiments/gt`):
two human players, tech 26, no random events. Player 0 is JOAT with Cheap
Engines; player 1 is JOAT. Player 1 lists player 0 as a friend, and
player 0 lists player 1 as an enemy. The predictions were stars-decomp
O-54..O-67, committed before the run (47b39ac). GT-001 had 36 cases: 34
held, 1 missed (H2), and 1 was a control. GT-002 tested the reconciled
reading (370c76b), and all 5 cases held. Raw evidence is in
stars-oracle-apparatus `evidence/gt/`.

- **Jump Gates (CONFIRMED).**
  - Two Jump Gate freighters flew 200 ly from deep space to an own 100/250
    gate. They kept their 100 kT and their fuel.
  - At 300 ly, five took 20/500 each. That is danger 5% from the
    destination gate's 250 ly range, so the destination's limits stand
    for both ends.
  - A fleet with one ship lacking the part did not move (message 0xde).
  - A Jump Gate freighter sitting at an own gated planet used that
    planet's gate: it unloaded its 60 kT there and took the source gate's
    danger.
  - With no gate at the destination (a starbase without one, or no
    starbase), the jump was refused with message 0xe2.
- **Friends (CONFIRMED).** What counts is how the gate's owner treats the
  fleet's owner:
  - Player 0 (who calls player 1 an enemy) used player 1's gates as
    source and as destination.
  - Player 1 (who calls player 0 a friend) was refused at player 0's
    source gate (0xe6) and destination gate (0xe5).
  - Player 1 got no message about player 0's fleet arriving at its gate.
- **Cargo at a friend's gate (CONFIRMED).**
  - 70 kT of ironium went onto player 1's planet, and both players got
    message 0xec.
  - With colonists aboard, the jump was refused (0x15e) and nothing was
    unloaded.
  - When the destination also had no gate, the refusal was 0xe2, and
    nothing was unloaded.
- **Range refusal and the 5× boundary (CONFIRMED).** A freighter jumping
  1301 ly from a 100/250 gate was refused (0xe3) after unloading its
  50 kT. Three Jump Gate DDs (truncated distances to a 100/250 gate):
  - at 1251 ly: refused, unharmed;
  - at exactly 1250 ly: the fleet was deleted (0xe7);
  - at 1249 ly: danger 99%. Two of three were lost, and the survivor
    carried 495/500 damage.
- **Mass exactly 5× (CONFIRMED).** A 500 kT ship through a 100 kT gate was
  lost (0xe7), not refused.
- **Mixed fleets (MEASURED, LEGACY BUG).** GT-001-H2 missed: a 500 kT ship
  and a safe Laser DD in one fleet were all deleted (0xe7). GT-002 fits
  this reading: each design lost entirely counts twice against the
  fleet's number of designs, and the fleet is deleted when the count
  comes to exactly zero.

  | Designs in the fleet | Designs lost entirely | Count | Result |
  |---|---|---|---|
  | 500 kT, DD, freighter | 1 | 1 | DD and freighter arrive |
  | 500 kT, 500 kT, DD, freighter | 2 | 0 | deleted |
  | 500 kT, 500 kT, DD | 2 | −1 | DD arrives |
  | 500 kT, DD | 1 | 0 | deleted |
  | 500 kT, 500 kT | 2 | — | deleted (every design lost) |

  The survivors kept only a little fuel (5 and 2 of 100), because fuel
  goes with the lost capacity.
- **After the jump (CONFIRMED).**
  - A stack at 250/500 damage that jumped safely still had 250/500 after
    the year. The same stack parked, and the same stack refused (0xe2),
    both repaired to 210.
  - Every fleet that jumped had the no-repair flag set, and its
    stationary flag cleared. Refused fleets kept the stationary flag.
  - In player 1's file, a fleet that had gated showed warp 0 and no
    heading. A fleet that moved normally showed warp 6 and its heading.
  - Player 1's fleet chasing a gating fleet kept its waypoint at the
    departure gate. Player 0's own chaser had its waypoint moved to the
    destination. A control chaser of a fleet moving normally followed it.
- **Cheap Engines (CONFIRMED).** 20 gating fleets of the Cheap Engines
  player all arrived, with no message 0xf2. In the control, 1 of 20 warp-9
  fleets failed.
- **No planet at the destination (CONFIRMED).** A warp-11 waypoint in deep
  space was refused (0x147).
- **Gate types (CONFIRMED, one stream).** The damage words matched the
  formula for any/300 at 402 ly (40), 150/600 at 699 ly (20), 300/500 with
  a 500 kT ship (80), 100/any with 202 kT ships (125; one of three lost,
  fuel 100 → 67), and any/800 at 905 ly (15). any/any was safe at 901 ly
  with 202 kT ships.

#### Packets (OB-022, OB-023)

- **Packet Physics decay (CONFIRMED):** classes 1, 2, 3 lost 5, 12 and 25%
  per year (1000 kT → 950, 880, 750). Each non-empty mineral lost at least
  5: 50 → 45, and a 100/100/0 packet → 88/88/0. A non-PP class-1 packet
  lost 10% (1000 → 900), with at least 10 (50 → 40).
- **IT targets: the OBJECTS.md rule missed (MEASURED).** OBJECTS.md halves
  both the packet's w² and the catcher's c² when the target's owner is
  IT.
  - A warp-10 1000 kT packet into an IT planet with no starbase killed 625
    units, as for any other owner (pop 1000 → 375 → 431 after growth).
  - Into an IT planet with a Mass Driver 7, it added 324 kT and killed 475
    units (pop 525 → 603). Both fit c² halved to ⌊49/2⌋ = 24 with w² = 100
    unhalved: caught 240‰, damage ⌊(100 − 24)·1000/160⌋ = 475.
  - So an IT catcher works at half its speed squared, and the packet's
    speed is not reduced. Sent to the objects decomp for reconciliation.

#### Minefield hits (CONFIRMED, OB-024)

- **Mines lost to a hit:**
  - heavy 400: −20 (N/20), then the 2% decay with the minimum of 10, to
    370 (one stream);
  - heavy 6000: −60 (N/100, since N/20 > 50), then 10% decay with two
    planets inside, to 5346 (all six streams);
  - speed bump 400: −20, then 2% with no minimum, to 373.
- A speed-bump stop left the fleet undamaged. The stops were 7 and 13 ly
  into the field.
- **Salvage (LEGACY BUG candidate, MEASURED).** Destroyed fleets with no
  cargo left salvage at the stop point. Each mineral was 0–9 kT: 4/5/0,
  8/5/6, 6/3/1, 2/3/0 and 7/3/9.
- **Setup caveat.** At warp 10 a Long Hump 6 ship can be lost before
  moving: the fleet was deleted with message 0xe1, with no hit and no
  salvage (one fleet in 4 of 6 streams). This is the overspeed rule for
  engines not rated for warp 10 (`docs/COMPONENTS.md`), not a minefield
  rule. Those streams' OB-024-A and C misses are this, not a field
  result.
- The Super Mine Layer doubles: two Mine Dispenser 40 laid 160.

#### Lay-mines duration and wormholes over three years (OB-025, OB-027)

- **Years word (CONFIRMED).** Word 2 laid three years (160, 310, 460), and
  the task was cleared after the third. Word 3 was still laying after
  three years. With word 0 (one year, OB-002-N) and word 1 (two years,
  OB-019), a word of 0–3 lays word + 1 years.
- **Wormhole ages (CONFIRMED).** A class-1 pair aged 0 jiggled each year:
  years 1, 2, 3, class unchanged, at most 12 ly per axis.
- **Jumps (MEASURED).** Twenty class-2 ends aged 40–42 (6% per end per
  year) gave 5 jumps in 60 end-years. A jump reset years to 0 and kept the
  class, and the new position was far away (for example (1180,1240) →
  (1090,1034)).
- **Wormhole targets (MEASURED; the prediction missed).** A waypoint aimed
  at a wormhole its owner had not seen at the start of the year became a
  deep-space waypoint at the wormhole's old position after the first
  jiggle (OB-025-F1, OB-027-B, 8 fleets). It made no difference that the
  owner saw the wormhole that year. With the owner's seen bit set at the
  start, the waypoint kept the wormhole and moved with it (OB-027-A, 4
  fleets). This agrees with the decomp's rule; the OB-025 prediction had
  assumed the scouts' scanning would count in the same year.

#### Mystery Trader (CONFIRMED, OB-023, OB-026)

- A Trader that reached its destination while another Trader existed was
  removed.
- The only Trader, arriving at its edge destination, stayed: warp 8 → 7,
  with a new destination on an edge ((1380,1300) → dest (1098,1380)). The
  other outcome, leaving with 1/2, was not seen in this stream.
- A part offer (item bit 0) traded to a tech-3 player gave exactly that
  part. Its Mystery Trader part word, read little-endian at byte 0x4a of
  the player block, gained bit 0, and tech was unchanged.
- A ship offer gave a new fleet of one Nubian (mass 499) at the trade
  point, added as a new design. The traded fleet was removed.
- A warp-9 Trader moved 81 ly in a year.

### Minefield lane (MF-1..MF-13)

Status: MEASURED, 2026-10-07. Tests the minefield rules OBJECTS.md marks
BINARY-ONLY (stars-decomp MF-1..MF-12). Predictions were committed before
the runs (`experiments/mf/README.md`: 789bffa, follow-ups 7241879, 631b0ce,
416ad73). One pinned year per run (cycles 20000 unless stated); the rate
cases were repeated at cycles 15000 and 30000, the only other distinct
streams for these starts. 33 of 35 cases held. MF-11 (the per-player
field limit) missed by one, and the MF-2 chain claim held only for one
fleet numbering. MF-04b first missed because the prediction counted the
planets inside the field before the year's stops (see "Order" below).

Setup: both players at tech 26, unarmed 3200-armor "Tank" destroyers on
straight 81-ly warp-9 legs through 50,000-mine fields. Damage is read from
the damage word, stops from the fleet position and from the hit messages.

#### Stop odds (CONFIRMED, MF-1, MF-3)

- A fleet makes one draw per whole ly travelled inside the field. The
  stop odds per ly are (e − safe) × {3, 10, 35} per mille for standard,
  heavy and speed-bump fields, with safe warps 4, 6 and 5. A stop on the
  first draw leaves the fleet where it started (offset 0).
  - Heavy, warp 9: 69 stops in 2137 draws over 3 streams, 32.3 per mille
    (95% interval 25.4–40.3; predicted 30).
  - Standard, warp 9: 43 in 2709 draws over 2 streams, 15.9 (11.6–21.0;
    predicted 15).
- **Effective warp comes from the distance travelled this year** (e = the
  smallest warp 3..10 with e² ≥ d − 1), not the waypoint warp. Warp-9
  fleets whose waypoint was 17 ly ahead in a standard field (e 4 = safe) or
  36 ly ahead in a heavy field (e 6 = safe) were never stopped (0 in 204
  and 432 draws; waypoint warp would give 23% and 66% per fleet). A 26-ly
  leg (standard, e 5) stopped 1 fleet of 12; a 50-ly leg (heavy, e 7) gave
  17 per mille (7.4–32.7; predicted 10).
- **Cloak plays no part:** Super-Stealth-cloaked Tanks were stopped at 29.1
  per mille (34 in 1168 draws) and uncloaked ones at 36.1 (35 in 969).
- **Relation (MF-5, MF-6):** what counts is the field owner's relation
  toward the fleet's owner. With the owner treating the victim as a friend
  (the victim treating the owner as an enemy), 24 fleets crossed with no
  stop in 1944 draws; reversed, they were stopped as in MF-1. The owner's
  own fleets are never stopped.
- One stopping hit per fleet per year; the fleet ends at the stop point.

#### Damage (CONFIRMED, MF-9)

Per design, (ships × {100, 500} + shortfall) × engines, with {125, 600}
when the engine burns no fuel at warp 4. A fleet under 5 ships is brought
up to a fleet minimum of {500, 2000} ({600, 2500}), all of the shortfall
going to the first design. Shields absorb at most half. Every stopped fleet
in two standard and one heavy run matched:

| Fleet | Standard | Heavy |
|---|---|---|
| Tank (Trans-Galactic Drive) | 500 → 78/500 | 2000 → 312/500 |
| Tank with Trans-Galactic Fuel Scoop | 600 → 93/500 | 2500 → 390/500 |
| Tank with Fuel Mizer (not a ram scoop, no fuel at warp 4) | 600 → 93/500 | 2500 → 390/500 |
| Tank with Complete Phase Shield (500) | 250 → 39/500 | 1500 → 234/500 |
| Tank + cloaked Tank (2 ships) | 400 and 100 → 62/500, 15/500 | 1500 and 500 → 234/500, 78/500 |

The engine rule is "no fuel at warp 4", not "is a ram scoop" (the Fuel
Mizer took the higher figures). The hit messages report the damage before
shields (the shielded Tank's message said 500, its damage word 250).

#### Which field loses mines; order in the year (CONFIRMED, MF-4)

- Heavy F1 (10,000 at 1160,1200) and heavy F2 (400 at 1210,1200, wholly
  inside F1): 11 stops, 10 of them inside F2. F2 only decayed (400 → 390),
  so F1 paid every stop: the paying field is the one with the smallest
  d² − count at the stop point, not the nearest centre or edge. F1 alone
  with the same fleets ended at the same count; F2 alone lost 20 per stop.
- **Order:** stops shrink the field as the fleets move (each stop takes
  max(10, count/20), or max(50, count/100) when count/20 > 50, from the
  current count). Decay comes after movement and counts the planets inside
  the shrunken field: F1 lost two of its five planets to the stops, so it
  decayed 14%, not 22%. Starbase sweeping comes after decay. This order
  fit the final count of every run exactly (for example MF-01: 50,000,
  24 stops, 50% decay, 1,280 swept → 18,367).

#### Followers (MF-2: chains CONTRADICTED as predicted, mutual chases CONFIRMED)

The minefield check of a fleet following another fleet uses the step it
moves in each movement pass, not its year's distance.

- **Mutual chases** (MF-02b): 12 pairs of Tanks 80 ly apart in a heavy
  field, each following the other at warp 9: no stop in either stream
  (per-year warp 9 would stop about 70% of them). Each pass moves a fifth
  of warp² (17 ly, effective warp 4). The west fleet, processed first,
  moved 17 + 17 + 12 ly and landed on the east one, which had moved 34 ly
  and moved no further.
- **Chains (MF-02):** C flies 81 ly, B (10 ly behind) follows C, A (10 ly
  behind B) follows B.
  - Numbered C < B < A: B and A each moved their whole remainder in one
    step after their target finished, and A was stopped in 2 of 6 chains.
    The prediction "A is never stopped" does not hold for this numbering.
  - Numbered A < B < C: A moved first, reached B's start in its first
    17-ly step (10 ly) and was never stopped. **B never moved at all**: a
    follower that lands on a still-waiting target ends the target's
    movement for the year (LEGACY BUG candidate, MEASURED 6 of 6).

#### Detonation (CONFIRMED, MF-7, MF-8)

Fields were set to detonate by HST edit; owners were not SD unless stated.

- **Heavy** field of 1000: the enemy Tank and the owner's own Tank each
  took 2000 (312/500). The owner's Mini Mine Layer took nothing. Nobody
  moved. The field decayed 27% to 730. With the owner treating the victim
  as a friend, the victim's Tank took the same 2000.
- **Speed bump** field of 1000: no damage, field 730 (no minimum of 10).
  Each fleet inside still got a "stopped in a mine field" message
  (0xc5/0xc9), though none was moving.
- **Standard** field of 1000 (MF-8): the owner's Laser DD at 250/500
  damage was destroyed (100 + 400 shortfall on 200 armor). An enemy fleet
  of 5 Tanks at 250/500 went to 265/500 (1600 + 100 per ship). A fresh
  single Tank took 500 (78/500).
- **SD owner:** a detonating standard field gave the SD owner full designs
  of both enemy designs it damaged (a Scoop Tank, 600, and a Shield Tank,
  250 after shields). A non-SD owner got only the partial designs it saw.
  The field decayed 27% (SD planet factor 1, no planets).

#### Laying (MF-10, MF-11, MF-12)

- **Merge cap (CONFIRMED):** an own standard field that held 1,050,000
  mines after decay made the layer start a new 160-mine field. One that
  held 999,500 merged (centre moved 1 ly toward the layer).
- **Per-player field limit (MEASURED; predicted 511, measured 512).** With
  511 own fields (numbers 0..510), a layer in open space made field number
  511. With 512 fields (0..511) it made none: the mines were lost and the
  owner got "failed to lay mines this year due to technical difficulties"
  (0x17e). A layer inside an existing field merged normally in all three
  runs.
- **Field 511 depends on object order (MEASURED, MF-13; LEGACY BUG
  candidate).** With numbers 0..510 taken, field 511 was made only when no
  universe object sorted after the owner's minefields. Objects sort by type
  (minefields, packets and salvage, wormholes, the Mystery Trader), then
  owner, then number. A player-1 field elsewhere (MF-13a) or a salvage
  object (MF-13b) blocked player 0's 512th field: no field, message 0x17e,
  mines lost. A player-0 field did not block player 1's 512th field, which
  was made as number 511 (MF-13c). So the limit is 511 fields when anything
  sorts after the owner's fields, and 512 otherwise (one run each).
- **Laying order (CONFIRMED):** two layers of 160 in one 390-mine field
  merge one after the other, in fleet-number order. With the east layer
  first: (1301,1252) 710; with the north layer first: (1382,1051) 710. A
  single weighted merge would give (+2,+2) in both.

#### Questions from the Elegy implementation (MF-14, MF-15)

Status: MEASURED, 2026-10-08. Two runs for questions the Elegy minefield
implementation raised (`OBJECTS.md` "Arithmetic details"). Predictions from
the stars-decomp reading were committed before the runs
(`experiments/mf/README.md`, e3f59ce). One pinned year each, cycles 20000.
Raw evidence: private `stars-oracle-apparatus` `evidence/mf/mf14`,
`evidence/mf/mf15`. Both held.

- **MF-14, cargo after a partial loss (MEASURED; LEGACY BUG candidate).**
  12 player-1 fleets, each of 4 Small Freighters (armor 25, cargo 70) and
  one armored Privateer (armor 3150, cargo 250), carrying 100/100/100 kT
  of minerals and 50 kT of colonists, crossed a standard field at warp 9.
  The 11 stopped fleets each lost the 4 freighters and kept the Privateer
  at 15/500. Each was left with 0/0/0 minerals and 24 kT of colonists, and
  a salvage object at its stop point held 47/47/48 kT. So the destroyed
  ships' capacity share (53/53/52/26: ⌊350·280/530⌋ = 184 kT, split by
  type rounding down, the 2-kT remainder to iron and boranium) was lost,
  and the survivors' minerals became salvage. Fuel was 176 against the
  unstopped fleet's 316: 316 − ⌊316·520/1170⌋, the ship-move sharing of
  `ORDERS.md` "Split". The earlier wording, "their minerals become
  salvage", is replaced.
- **MF-15, due-north and due-south legs (MEASURED; LEGACY BUG).** A heavy
  field of 10,000 (radius 100):
  - 8 Tanks starting 3 ly outside and flying 81 ly due north into the
    field: none stopped (about 78 ly inside; an east leg is stopped about
    90% of the time).
  - 8 Tanks starting 90 ly from the centre and flying due south, out of the
    field after 10–13 ly: 6 stopped, at 2, 9, 10, 18, 19 and 31 ly. Three
    of those stops lie outside the field. The original checks such a leg
    for its first ⌊√(10000 − 90²)⌋ = 43 ly from the start whatever the
    direction.
  - 8 east-leg controls entering from outside: 8 stopped.

Not tested: the detonate-order validation gap (needs crafted orders), SS
and SD safe-warp bonuses, fleets moving through gates in a field, steep
but not due-north legs, and the stop-point rounding on diagonal legs.

### Wormholes and Mystery Trader, round 2 (WT-001 to WT-005)

Predictions O-43..O-53 come from the objects decomp lane. They were
committed before the runs (`experiments/wt/README.md`). Deterministic
runs were made at two cycles values; WT-004 ran over 16 streams. Raw
evidence: stars-oracle-apparatus `evidence/wt/`.

In the host file a wormhole has two player masks, the **known** mask
(which players have the end on their map) and the **destination** mask
(which players know where it leads).

- **CONFIRMED: only transit reveals the destination (O-43, WT-001 A, G).**
  - A player 0 fleet transited an end that both players already knew.
    Player 0's bit went into the destination mask of both ends.
  - Player 1 saw both ends of that pair in the same year and did not get
    the bit. Neither did player 1 for a second, unknown pair it saw that
    year: it got the known bit on both ends, and the destination mask
    stayed 0.
- **CONFIRMED: a jump keeps the destination (O-44, WT-004, 18 jumps in
  16 streams).**
  - Every jumped end kept player 0's destination bit and reset its years
    to 0.
  - 14 of the 18 jumped ends also lost the known bit. The other 4 landed
    near a ship player 0 had just received from the Trader the same year,
    were in player 0's file, and so were known again.
  - Those 4 ends were 21, 27, 72 and 107 ly from the receiving fleet. That
    is within the fleet's penetrating range (about 33 for an M.T. Scout
    and 132 for an M.T. Lifeboat) but beyond R/4. An end 52 ly from an
    M.T. Scout was not seen. These are MEASURED observations for the
    scanning record; the scanning rule for a just-jumped end was not the
    question here.
  - All 302 ends that did not jump moved at most 12 ly on each axis, aged
    one year and kept both masks.
- **CONFIRMED: what transits (O-46, WT-001 B, C, D, E).**
  - A fleet whose waypoint was the wormhole's position as a plain point
    ended there, in normal space. A fleet whose waypoint was the wormhole
    itself transited.
  - The B2 wormhole was unknown to player 0 at the start of the year, and
    the fleet still transited in that year. This fits OB-025/OB-027: an
    unseen target turns into a plain position only at the end-of-year
    waypoint check, after movement.
  - A fleet whose straight move passed over an end did not transit.
  - A warp-10 packet whose 100 ly move ended exactly on an end stayed
    there, and so did a Trader whose 64 ly move ended on an end.
- **MEASURED, contradicts O-47: a fleet aimed at the Trader goes to where
  the Trader is after the Trader's move (WT-001 F1, WT-005, two streams
  each).**
  - The Trader moves before fleets. A fleet 30 ly west of the Trader's
    start, aimed at the Trader at warp 6, flew its full 36 ly east to
    (1206,1300), past the start (1200,1300).
  - A fleet 50 ly east of the start flew 31 ly east to the Trader's end
    point (1281,1300). It traded there and was consumed. The decomp
    predicted that both fleets fly to the start-of-year position.
  - A fleet flying onto the Trader's end point with a plain waypoint also
    traded (WT-001 F2), as in OB-004.
- **CONFIRMED: part rewards (O-48, WT-003 A).**
  - Twelve Traders offering item bits 0–11 each gave player 0 (tech 26,
    no parts) the part for that bit. After the year its Trader-item mask
    was 0x0fff and its tech was unchanged.
  - Every trade consumed the fleet.
  - Messages: id 0x10b for ten parts, 0x10c for Mini Morph (bit 8), 0x10f
    for the Genesis Device (bit 10).
  - The bit-to-part map is in `experiments/wt/README.md` (WT-003 rows).
- **CONFIRMED: a full design table (O-49, WT-003 B).** A player with all
  16 design slots used traded for a ship. Its fleet was consumed, and it
  got no ship and no new design. Message 0x150.
- **CONFIRMED: ship gifts (O-49, O-51, WT-004 B, C; 30 meetings, 2 void).**
  - Every ship gift was one of three designs:
    - M.T. Lifeboat: a Nubian hull with 1 or 2 ships;
    - M.T. Scout: a Mini Morph with Langston Shells, 1 to 4 ships;
    - M.T. Probe: a Mini Morph with Mega Poly Shells, 1 to 4 ships.
  - The design went into the player's first empty design slot. The new
    fleet was at the trade point with full fuel. The Trader-item mask and
    tech were unchanged.
  - A player at tech 26 owning all twelve parts, offered item 0, got
    nothing (message 0x10e) in 3 of 15 meetings and a ship in the other
    12. The prediction was 1/5 nothing, else always a ship.
  - Counts over 30 meetings: Lifeboat 5, Scout 11, Probe 11, nothing 3.
    The predicted shares were 1/4, 3/8 and 3/8 of ships.
- **CONFIRMED: a research step keeps accumulated research (O-50, WT-002
  A).** A player with biotech 0 and 20 accumulated in biotech, all other
  fields 26, traded for research. Biotech went to 1, its accumulated
  research stayed 20, and the other fields stayed 26. Message 0x109.
- **CONFIRMED: an owned offered part becomes research (O-52, WT-002 B).**
  A player at tech 5 everywhere that owned the Anti Matter Torpedo traded
  7,400 kT with a Trader offering it. It gained exactly 8 levels (3,2,1,0,0,2
  and 1,3,2,0,0,2 in the two streams), and its item mask stayed 0x0040.
- **MEASURED: the Trader's yearly warp bump.** 4 Traders, in about 80
  Trader-years, changed warp 8 → 9 before moving, with message 0x130.
  One of the 4 also got a new destination on the map's west edge (x
  1020). The meetings staged for those Traders were void. This fits the
  decomp's reading of 1/25 a year for the bump and then 1/3 for a new
  destination.
- **Message records.** In the player file's event block, a message record
  starts with a little-endian word: the id in the low 9 bits and flags
  above. 0x109 was written as `09 01` or `09 03`; the following bytes
  carry the level count. The rest of the layout is not decoded.
- **Not tested:**
  - stability names (O-45, report text);
  - computer-player planets trading (O-53; since measured, see "Computer
    players: stage 1");
  - the 25th-redraw ship LEGACY BUG, which is too rare to reach by
    sampling streams;
  - Trader appearance (KX-004).

### Round 6: the rest of OBJECTS.md's BINARY-ONLY rules (OB-028..OB-031, GT-003, TP-001, TP-002)

Status: MEASURED, 2026-10-07. Predictions were committed before the runs
(stars-elegy ee169d3: `experiments/ob/README.md` "Round 6",
`experiments/gt/README.md` "GT-003", `experiments/tp/README.md`), one
pinned year each at cycles 20000; OB-031 also at 30000 and 60000. Every
predicted case held (16 launch cases, 9 PP cases, 2 OB-030 cases, OB-031
in three streams, 12 GT-003 cases, 6 TP cases). Raw evidence: apparatus
`evidence/ob/ob028`..`ob031-*`, `evidence/gt/gt003`, `evidence/tp/`.

- **Packet launch (OB-028).** Warp 9 from a Mass Driver 7 launched as
  class 2; a speed of 11 (above `Dw + 3`) fell back to 7; two Mass Driver
  7s in the two orbital slots of a Space Station launched at 8 with the
  speed unset, Mass Driver 7 with Mass Driver 5 at 7; two items in one
  queue made one 200 kT packet; no destination: no packet, minerals
  unchanged, two messages to the owner. Every packet stood at `⌊W²/2⌋` ly
  after its launch year, decayed for half a year (class 2: 100 → 88;
  class 3: 75). A class-3 packet that arrived in its launch year after
  70% of the year kept 413 of 500 kT (half of its 70% share of the
  year's decay) and added 45 kT to an unowned planet. An Interstellar
  Traveler launcher added 1 to the class (warp 7: class 1, 90 kT) and
  stopped at 3 (warp 10).
- **Launch spend (MEASURED, side check).** 110 kT of the mineral per
  100 kT item (IT 120, PP 70); 44 of each per mixed item (PP 25).
- **Packet Physics (OB-029).** Items launched 70 kT, mixed 25 kT of each.
  1000 kT of only ironium, boranium or germanium at warp 10 into an
  unowned 20/20/20 planet moved only gravity (+3), temperature (+6) or
  radiation (+2) toward the PP player's ideal, with the original values
  unchanged, and added 111 kT. A 500 kT packet into a populated planet
  killed as the damage rule says (pop 791 as predicted). OB-029-D2: the PP
  player's file showed no foreign design after hitting a Laser Fort;
  without a control this does not settle whether the design becomes
  known.
- **Alternate Reality target (OB-030-A).** 1000 kT at warp 10: surface
  +111, population equal to the control planet's: no damage.
- **Two Traders at one point (OB-030-T).** Trader 0 consumed player 0's
  first fleet and player 1's fleet and refused player 0's second fleet;
  Trader 1 consumed it. All three fleets gone.
- **Lone Trader arrival (OB-031).** A warp-6 Trader 20 ly from its
  destination arrived, stayed and took warp 7 with a new destination on
  an edge, in all three streams. With OB-023 that is four lone arrivals,
  all staying; the 1/2 chance of leaving has not been observed (four
  stays in a row would happen 1 time in 16 if it holds).
- **Stargate refusal order (GT-003 R1–R6).** Each fleet had two reasons
  to be refused and got one message: source gate before destination gate
  and before a deep-space destination; destination owner before range and
  before mass; foreign colonists before mass, minerals kept aboard; range
  before mass, with the hold unloaded onto the source planet first.
- **Loss-roll wipe-out (GT-003 W0–W5).** A 491 kT freighter (32% loss
  chance) with a Laser DD through a 100/250 gate: in W2 and W3 the roll
  destroyed the freighter and the fleet arrived with its Laser DD, so a
  design wiped out by the roll counts once (GT-002: a design lost
  entirely at `pct = 100` counts twice). In the other four the freighter
  survived.
- **Computer players' planets (TP-001, TP-002).** An expert Turindrone
  homeworld gained the offered part and lost all its surface minerals; with
  that part already owned it drew another (bit 6). An expert Automitron
  homeworld at tech 10,10,10,13,10,10 went to 12,11,11,13,11,11 and paid
  5,000 kT, germanium first then boranium; at tech sum 150 nothing
  happened. The human homeworld never traded.

#### GT-004: what makes a gate (MEASURED, one year)

Predictions committed before the run (487627f). Starbase design 0 of both
players was redefined as a Space Station with a Stargate any/any in its
first orbital slot. Laser Destroyers with a warp-11 waypoint to another
such planet jumped (message 0x4e), for a player at tech 26 and for one at
tech 3. So did one leaving a Space Station whose gate sat in the second
orbital slot. One aimed at a planet whose starbase had no gate stayed,
with only message 0xe2. The fleets that ended over a Space Station were
refilled with fuel, as any fleet over a starbase that can refuel is.

### Not tested

Packet limits (32,760 and 16,300 kT), PP terraforming as rates and the
design-known rule, wormhole jump odds to a measured rate (O-28), Mystery
Trader leaving with 1/2 and ship counts after year index 100. (Harder
computer players' planets were later traded in O-53.)

## Components (CS-001, CS-002, CS-003)

Question: does the part, hull and planetary-item table read from the binary
(private `stars-decomp` `tools/components.py`), with its cost and race
rules, match the original game? Result: `data/components.json` and
`docs/COMPONENTS.md`. Predictions were committed before each comparison.

### Technology Browser, designer, planet panel (CS-001, MEASURED 2026-10-07)

- 13 race setups (`experiments/cs001/configs.txt`): SS at tech 0 and with
  Mystery Trader items not owned; HE, SS + IFE/TT/ARM/ISB, WM + NRSE/NAS,
  CA + CE/OBRM, IS + BET, SD + IFE/ARM/NAS, PP + TT/ISB, IT + NRSE/CE,
  AR + ISB/OBRM, JOAT at tech 26; SS + BET at tech 0.
- 3,095 of 3,095 browser readouts as predicted: name, displayed minerals
  and resources, mass, tech requirement, Available / UnAvail / research
  cost, and each value the description states (armor, shield, cloak %,
  jammer %, damage, range, initiative, accuracy, mines swept and laid,
  bomb kill rates, battle speed, capacitor %, tachyon %, fuel and cargo
  capacity, deflection, minefield parameters, mining rate, stargate
  limits, mass driver warp, scanner ranges, dock capacity, terraform
  amount).
- Discriminating: perturbing any predicted value by 1 makes the
  comparison fail. Costs at tech 26 exercise miniaturization at the cap
  (75%, BET 80%); the race setups exercise every PRT/LRT cost case and
  every restriction rule; tech 0 with BET exercises the doubling.
- Terraform and planetary items are not miniaturized and not doubled by
  BET in any setup (the binary leaves the doubling test reading an unset
  value for them; observed outcome: never doubled).
- Mystery Trader items are not listed unless owned (227 items with mask 0).
- Designer: all 37 hull and starbase slot layouts and each race's
  hull list as predicted. Starbase hull costs shown there are
  `(c − c/5 + 1)/2` with ISB or AR and `(c + 1)/2` without (Death Star
  for AR: 62/41/180/384); the browser shows `c − c/2` regardless of
  ISB/AR.
- Defense coverage, 10 defenses: 9.56, 18.29, 21.56, 26.25, 32.11% for
  SDI, Missile Battery, Laser Battery, Planetary Shield, Neutron Shield;
  `1 − (1 − c/1000)^10` truncated to two decimals (rounding would give
  21.57 and 26.26).

### Engine fuel tables (CS-002, CONFIRMED 2026-10-07)

- 144 fleets, all 16 engines at warps 2–10: every charge, ram-scoop gain
  and end position as predicted (`experiments/cs002`).
- Warp 10 on engines not rated for it: 3 of 22 ships destroyed (message
  223 for the fleet), 0 of 10 with rated engines. The fleet paid the full
  charge, then kept `trunc(x·survivors/ships)` of its fuel and cargo.
- Engines the race may not build (Settler's Delight, Fuel Mizer,
  Interspace-10, Galaxy Scoop for an SS race without LRTs) were kept in
  the designs at tech 26 and used as given.

### The remaining BINARY-ONLY columns (CS-003, CONFIRMED 2026-10-07)

CS-003 aimed at the 63 rows CS-001/CS-002 left with a BINARY-ONLY column.
80 cases in 6 Combat Lab runs (`experiments/cs003`, predictions committed
first): 77 matched, 3 could not tell the two readings apart and were
re-run as CS-003-C2, which matched. No case contradicted the table.
Every row of `data/components.json` is now CONFIRMED.

- **Warp-10 rating** (CS-003-W): 6 fleets of 10 Small Freighters per
  engine at warp 10. The 5 rated engines lost 0 of 300 ships; each of the
  11 others lost ships, 58 of 660 in all (8.8%; per engine 1 to 10 of 60).
  Losses per 10-ship fleet: 0 in 28 fleets, 1 in 21, 2 in 15, 3 in 1,
  4 in 1, close to independent 1-in-10 draws per ship (KERNEL.md).
- **Battle warp**: already shown by CB-000. Each engine's scout (mass
  under 70) showed moves `(battle_warp − 4 + 2)/4` (plus one step for the
  Enigma Pulsar), which identifies the warp for all 16 engines.
- **Fuel transports** (CS-003-W): stationary fleets with no fuel ended
  the year with 200 mg (one Fuel Transport), 600 (three), 200 (one
  Super-Fuel Xport, not more for the bigger hull) and 0 (a Medium
  Freighter control).
- **Sweeping** (CS-003-S): one Scout per plain beam at the centre of an
  enemy field with no planets swept exactly `damage × range²` after the
  2% decay, for all 16 plain beams and the Multi Contained Munition (1260).
  Blackjack, Bludgeon and Blunderbuss (range 0) swept nothing, which rules
  out the gatling reading (range 4).
- **Range-0 beams are beams** (CS-003-C): each hit an unarmed, unshielded
  Orbital Fort (armor 100) for armor damage (Blackjack: 450/500 = 90 on
  the first hit; Bludgeon and Blunderbuss destroyed it with one hit). A
  sapper would have done nothing.
- **Mine laying** (CS-003-S): a Super Mine Layer with two Mine Dispenser
  40 laid 160 ("this year only"), as the Mini Mine Layer control did.
- **Torpedoes and missiles** (CS-003-C, C2): each hit record on an
  unshielded target replayed with the COMBAT.md damage rule. The 8
  torpedoes did `d`, the 4 capital missiles `2d`. One Alpha Torpedo hit
  did 4, not 5: the two halves `d/2` are each truncated (CS-003-C2,
  700-armor target: 3 units per hit). Missile hit records carry flag
  0x08 in addition to the torpedo flag 0x04 (0x0c); torpedo records
  carry 0x04 only.
- **Open for the combat lane (record format, not behavior):** every
  torpedo shot that missed an **unshielded** target still left a record
  with flag 0x80 and no change (CS-003-C2: 7 for the Alpha Torpedo, 12
  and 11 for the missiles, one per missed shot). COMBAT.md "Torpedoes and
  missiles" step 3 says misses are recorded only against a target with
  shields. Both may hold if a salvo with no hit is recorded differently
  from the misses of a salvo that hits; not tested.
- **Designer** (CS-003-D): four Enigma Pulsars on a Battleship showed
  cloak 40% (20 points each; 21 would show 42%) and moves 2¼; Midget
  Miners with 0, 1 and 2 Alien Miners moved 1, 1¼, 1¼, and with an
  Enigma Pulsar and an Alien Miner 2¼, so the two parts share one
  `(n + 1)/2` term. Mega Poly Shell on a Medium Freighter showed scanner
  80/40, Multi Contained Munition on a Cruiser 150/75. Cloak and jam
  percentages matched SCANNING.md and COMBAT.md (2 Alien Miners: 52%/51%).
  For one design with no cargo these readouts also show the cloak points
  of Enigma Pulsar (20), Alien Miner (60), Mega Poly Shell (40) and Multi
  Contained Munition (20), which SCANNING.md "Fleet cloak" lists as
  BINARY-ONLY, and the Alien Miner term of COMBAT.md's speed code.
- **Bombs** (CS-003-B, environment 50/50/50, no defenses):
  - one LBU-17, LBU-32, LBU-74 or Hush-a-Boom on P' = 10 killed exactly 1
    (no minimum of 2 or more; a minimum of 1 unit would act the same,
    since a bomb with a kill rate always kills at least 1);
  - one Smart, Neutron, Enriched Neutron, Peerless or Annihilator bomb on
    P' = 1 with 20 mines and 20 factories left all three unchanged (no
    minimum, no installation kills);
  - one Retro Bomb on P' = 10 killed nobody and destroyed nothing;
  - one Multi Contained Munition on P' = 1000 killed 20 (2%) and took
    mines 10 → 5. T-18 had shown its minimum of 3 units.
- **Colonizing** (CS-003-B): a Colony Ship with an Orbital Construction
  Module colonized an unowned planet (JOAT race), as one with a
  Colonization Module did; an empty Colony Ship did not.
- **Remote mining** (CS-003-B): two Orbital Adjusters on a Midget Miner
  mined nothing; two Robo-Midget Miners (rate 5 each) at concentrations
  100 added 10 kT of each mineral (KERNEL.md "Remote mining", MEASURED
  for this one case).

### StarsAPI comparison (private)

StarsAPI's `UNEDITED.MOD` agrees with the binary table on every item:
names (its file has a damaged ± character), tech, mass, cost, category
values, hull cargo, fuel, armor and slots. No disagreement between binary,
game and StarsAPI was found.

## Turn Orders

Status: PARTIALLY MEASURED. The ingestion and validation rules are
restated for implementers in `ORDERS.md`; this section holds the
experiment records behind them. Only the registered-copy gate is measured
so far; the rest of `ORDERS.md` is BINARY-ONLY and listed there under Open
experiments (oracle prefix OX).

### OX registered-copy gate (MEASURED, 2026-10-07)

Ruleset: J-RC3, registered host.

A player order file that carried the host's expected registration
credential and set research to a new allocation changed that player's
research when generated. The byte-identical order file with the credential
absent (and nothing else changed) left the player's research unchanged
across three consecutive generations, and set no cheater or tamper flag.

Interpretation: a registered host accepts a player's order file only when
it carries the expected registration credential; a file without it is
silently skipped, and a missing credential is distinct from the anti-tamper
cheater check. The credential value is not recorded in this public
repository. Raw files are kept in private apparatus.

## Universe generation

Status: MEASURED (UG01 to UG30, 2026-10-07; cloud oracle; UG22..UG30 in
"Round 3" below). Predictions
UG-1..UG-9 from the private binary reading (stars-decomp
`docs/universe-gen.md`, `docs/universe-gen-predictions.md`, PR #15) and a
whole predicted game per case were committed before the runs
(`experiments/ug/README.md`; stars-decomp 1327269, apparatus 80e6c1b).
CONFIRMED below means every case that tested the rule agreed, field by
field; the case ids say which. This section states behavior only.

### Method

- Each game is built from a game definition file with
  `tools/fleetlab/new-game` (`docs/ORACLE.md` "New games from a definition
  file"); the new `.HST` is read with `combatlab dump` and
  `experiments/ug/homeworlds.py`.
- UG01..UG15: the SS race file PG000.R1 and computer players, every size
  and density, 2 to 16 players, the max-minerals, BBS, clumping and
  no-random-events options. UG16..UG21: legal WM, SD, IT, JOAT and PP
  races made from PG000.R1 by changing only the primary trait and the
  leftover-points spend (`tools/fleetlab/racelab`), with 2 to 16 players.
- The private model was compared on planet positions, name ids, every
  planet's environment, concentrations and artifact flag, owners,
  homeworlds, starting tech, designs, fleets, logos, wormholes and the
  option word. All 21 games and a rerun of UG01 matched with 0
  mismatches.
- Raw files, dumps and checks: private `stars-oracle-apparatus`,
  `evidence/ug/`.

### Determinism and seeds (CONFIRMED)

- A definition file that gives a seed produces the same game every time.
  UG01 built at two DOSBox speeds (cycles 20000 and 30000) decoded
  identically apart from the game id. The game id is the only difference,
  and since the files are encrypted with it, compare decoded dumps, not
  raw bytes.
- Seeds that are equal modulo 4096 gave the same game in both pairs run:
  seed 57 and seed 12345 (UG11 vs the first OB new game, huge), seed 4107
  and seed 11 (UG14 vs OB-006's large game). Seeds 0 and 64 also gave
  identical games (UG12, UG13). The binary reading says only the low 12
  bits are used, as two 6-bit halves, and a seed whose halves are equal
  behaves like the one with the upper half bumped by one; that explains
  the 0/64 pair, the only such pair run.
- Without a seed the game comes from the startup clock (not tested here).

### Planet counts (MEASURED)

Planets per game, by size and density:

| size | sparse | normal | dense | packed |
|---|---|---|---|---|
| tiny | 24 (UG01) | 32 (UG08, UG12, UG13, UG19) | | 57 (UG22), 59 (UG23) |
| small | 96 (UG06, UG18) | 128 (UG02) | 160 (UG09) | 239 (UG24) |
| medium | | 288 (UG07, UG16, UG20) | 360 (UG03) | 540 (UG10) |
| large | | 512 (UG14, UG17) | | 912 (UG04, clumped), 900 (UG25) |
| huge | | 800 (UG11, UG21) | 940 (UG05) | 940 (UG15) |

With W the galaxy width (400, 800, 1200, 1600, 2000 ly from tiny to
huge), the normal-density counts are W²/5000, sparse 3/4 of that, dense
5/4 and medium packed 15/8. Large packed and huge dense or packed come
near the generator's limit of 999 candidates, and the binary reading says
their count then depends on the seed (a too-close pass removes a variable
number). Huge dense and huge packed gave the identical game at the same
seed (UG05, UG15). Round 3 confirmed the seed dependence: large packed
gave 912 and 900 for two seeds, and tiny and small packed fell below their
usual 60 and 240 for the seeds the model picked (UG22..UG24).

### Round 3: BINARY-ONLY generation rules (UG22..UG30)

Predictions committed before the runs (stars-elegy 7726cc3,
`experiments/ug/README.md` "Round 3"; apparatus ff01ff25). All nine games
matched the whole predicted game field by field (37 to 44 fields each, 0
mismatches).

- **Seed-dependent counts** (UG22..UG25): 57, 59, 239 and 900 planets, as
  predicted.
- **Options with no effect at creation** (UG26..UG28): slower tech,
  computer alliances and public scores each gave UG01's galaxy planet for
  planet; only the option word differs.
- **Second-planet redraw limit (LEGACY BUG, UG29, UG30).** A PP race with
  40–60 on every axis: in UG29 the second planet used all 100 redraws and
  took the homeworld's 50/50/50 environment; in UG30 (another seed) it
  kept its redrawn 40/42/45.

### Options (CONFIRMED)

- **Maximum minerals** (UG02, UG09): every planet's concentrations are
  100/100/100, except the homeworlds.
- **BBS** (UG03, UG09, UG21) raises
  concentrations below 40 by 5, homeworld surface minerals by 1/4, and
  multiplies homeworld population by (growth% × k + 5)/5, k = 2 for HE and
  1 otherwise. PG000.R1 (SS, 10%) starts with 750 colonists instead of
  250 (UG03); IT, 4/5 of that, with 600 (UG21).
- **No random events** (UG08, UG09): no wormholes and no artifacts.
  UG19 (tiny, events on) also had no wormholes; no artifact appeared in
  any game of this corpus.
- **Clumping** (UG04, UG10) and player positions 0–3 (all games) moved
  planets and homeworlds as the model predicted.

### Starting tech by PRT (CONFIRMED)

Energy/weapons/propulsion/construction/electronics/biotech for the human
races of UG16..UG21 (all with the same research settings as PG000.R1):

| PRT | tech |
|---|---|
| WM | 1/6/1/0/0/0 |
| SD | 0/0/2/0/0/2 |
| IT | 0/0/5/5/0/0 |
| PP | 4/0/0/0/0/0 |
| JOAT | 3/3/3/3/3/3 |
| SS (PG000.R1) | 0/0/0/0/5/0 |

Computer races start with their own settings on top (for example SS
0/0/1/0/5/0, CA 3/3/3/3/3/6 and AR 1/0/1/0/0/0 in UG21). Starting designs and fleets
per PRT matched the model in UG16..UG21; examples from UG21: WM with
construction 0 has only a scout (Quick Jump 5, Bat Scanner, Yakimora Light
Phaser) and a colony ship; SD
has two Mini Mine Layers; IT a Destroyer and a Privateer; JOAT six
designs and six fleets.

### Starting planets (CONFIRMED)

- Homeworld installations are 10 mines, 10 factories and 10 defenses
  before leftover-point spends. AR homeworlds have no installations;
  their starbase design 1 is a Space Station and design 0 an empty
  Orbital Fort.
- **IT and PP second planet.** On a map larger than tiny, an IT or PP
  player starts with a second planet holding 2/5 of the homeworld's
  starting population, 10 mines and 4 factories; the homeworld keeps
  4/5 (IT and PP in UG16, UG17, UG18, UG20, UG21; computer PP in UG03).
  On a tiny map there is no second planet and the homeworld keeps the
  full population (UG19). IT starbases carry a Stargate 100/250 and an
  Orbital Fort gate design exists; PP's carry a Mass Driver 5.
- **Leftover advantage points.** With L = min(50, points left), all of
  this corpus's races had L = 50. The spend selected in the race file
  added, on the homeworld:
  - mines: +25 (10 → 35; WM UG16, PP UG20);
  - factories: +10 (10 → 20; SD UG16);
  - defenses: +5 (10 → 15; IT UG16);
  - surface minerals: +500 kT, +250 on the smallest of the three and +125
    on each other (JOAT UG16: 423/253/234 → 548/378/484);
  - mineral concentrations: +25 on the lowest and +13 on all three (JOAT
    UG20: 53/30/82 → 66/68/95, with the 30 the floored value below).
  Computer races of harder and expert levels also showed the
  concentration and surface boosts (UG17, UG21).

### Shared homeworld minerals (LEGACY BUG, MEASURED)

In every game with two or more players (UG16..UG21 checked directly;
up to 16 players in UG21), all homeworlds start, before spends, with:

- the **same surface minerals**, one draw for the whole game; and
- the **same concentrations: those of planet 0** (the first planet in
  the planet list), each raised to at least 30, not the homeworld's own.

Examples: UG16, planet 0 has 15/70/90, and the WM, SD, IT and JOAT
homeworlds all have 30/70/90 with surface 423/253/234 (JOAT's minerals
spend gives it 548/378/484). UG21, planet 0 has 47/37/29; the eight
homeworlds without a concentration spend all have 47/37/30, and the ten
without a minerals spend all have 438/262/450.

Interpretation: the binary reading attributes this to the homeworld
setup reading the first planet's record instead of the homeworld's. It
is deterministic and observable, so it is recorded as LEGACY BUG; it
makes every start mineral-identical, which may be what players have
long seen as "fair starts". Elegy can reproduce it as one isolated rule.

## Race design (RD-1..RD-7, RW08, RD-P1..RD-P21)

Predictions were committed before the runs (80037c8). `experiments/rd/` holds
the case tables (`races.tsv`, `README.md`) and the game definitions. Raw race
files, games and checks are in the private apparatus, `evidence/rd/`. Each
new game was generated once (`tools/fleetlab/new-game`, cycles 20000), and
each penalty case is one pinned year (cycles 20000). The comparison with the
predicted games (every generated field, each player's race and name) was
private. The behavior it confirmed is recorded here.

### Advantage points and leftover (MEASURED, RD-1..RD-4)

- 48 legal races with predicted points 1..50 (RD-1..RD-3, one per case in
  `races.tsv`) each got leftover `L = points`, seen in the homeworld's surface
  minerals: the smallest mineral gains `10·L/4 + (10·L mod 4)` kT, and all
  three gain `10·L/4` more. The races cover every growth-table row from 3 to
  20, one to three immunities, a 0–20 axis, the factory and mine settings,
  colonists per resource from 700 to 2500, AR, NAS with PP, SS and JOAT, LRT
  sets, research settings, and every PRT. The 48 point values are the
  `predicted points` column, all confirmed.
- Boundaries (RD-4): a 0-point race is legal with L 0. Races with 50 and 51
  points both get L 50.
- Leftover spends 5 and 6, which the wizard does not offer, act as spend 0
  (surface minerals).
- racelab (StarsAPI's calculator) gives the same points except:
  - it is one lower on 11 races (float truncation; the 9 the decomp named,
    plus RD-4 e and i);
  - it disagrees on the growth-0 race.
  Before 18d99b2 it also ignored "expensive fields start at tech 3" and
  "factories cost one less germanium", so it overstated races with those
  traits by about 60 points each.

### Illegal, malformed and Random races at game creation (MEASURED, RD-4..RD-6)

- **Illegal human races are replaced.** A −1-point race and a −1433-point
  race became the default race: JOAT, growth 15, 15–85 on every axis, the
  standard economy and research, a computer name (Bulushi, American), L 25,
  and race flag 0x10.
- **Malformed fields are repaired, and the race is kept with flag 0x10:**
  - a habitat centre one off its range midpoint was moved back;
  - race stat 15 = 1 was reset to 0;
  - growth 0 became growth 1, which left 5851 points and so L 50.
- **A race file whose checksum is wrong is refused**, before any of this.
  The game shows "The game file X.r1 appears to be corrupt, unable to load
  file" and no game is created. Three corpus files first had bad checksums.
  They were rewritten with `racelab edit` (only the checksum changed) and
  RD-4 was run with them.
- **Random races.** The wizard's Random race (RD-4 k..n; RD-5, RD-6) became
  a generated race with a computer name. A Random race named Zorgon kept its
  name. Generated races scored:
  - 21, 21, 44 and 23 (RD-4);
  - 12, 5, 35, 38, 8 and 32 (RD-5);
  - 32, 3, 16 and 42 (RD-6).
  That is 14 races, all within 0..50. Each matched the decomp's exact
  prediction, as did every later draw of those games.
- **Computer players are not checked.** RD-4's computer players kept races
  worth 963 and −75 points; RD-5 kept one worth −173.

### Turn-time penalty (RD-P1..RD-P10)

Base: a one-player SS game in year 2407 (KX-001 A1). Player 0's race was
edited with hst-edit, and one year was generated.

| Case | Edit | Points after edit | Observed | vs prediction |
|---|---|---|---|---|
| P1 | two economy stats | −444 | message 0x117, flag 0x10; colonists per resource 2500, growth 7 (1042 points) | held |
| P2 | six economy stats | −2092 | 2500, growth 4 (1602) | held |
| P3 | P2 + research + LRTs | −3667 | 2500, growth 3 (1457) | held |
| P4 | habitat centre 51 | 245 | punished: centre back to 50, colonists 1700 (525) | held |
| P5 | race stat 15 = 1 | 245 | stat reset to 0 silently: no message, no flag, colonists unchanged | **missed** (predicted a penalty) |
| P6 | colonists per resource 2600 | 845 | clamped to 2500 silently: no message, no flag | **missed** |
| P7 | PRT 10 | 299 | became JOAT silently: no message, no flag, colonists unchanged | **missed** |
| P8 | gravity low −5, centre 40 | 212 | punished: gravity 0–85, centre 42, colonists 1800 (532) | held |
| P9 | 0 points exactly | 0 | not punished, unchanged, no message | held |
| P10 | −1 point | −1 | 2500, growth 9 (559) | held |

So in a running game, negative points and malformed habitat are punished
(0x117, flag 0x10, colonists per resource raised until the race reaches 500
points, growth lowered when that is not enough). Out-of-range PRT,
colonists per resource and race stat 15 are repaired without any penalty.
That differs from game creation, where stat 15 = 1 set the flag. The base
game has one player, so message 0x182 to other players was not observable.
A second year after a punished case was not run.

### Follow-up: AR spends, growth 0, several players (MEASURED, RD-7, RD-P11, RD-P12)

Predictions were committed before the runs (60bd6ef, 50f14ba). The decomp's
model matched every case: `universe.py check` gave 93 matches and 0
mismatches, and `races.py turn` gave 5 of 5 in each penalty year.

- **AR leftover spend (RD-7).** Five human AR races (34 points, L 34)
  differed only in the spend, plus one computer player.
  - The minerals spend (0) and the concentrations spend (1) applied as for
    other PRTs: 98/88/85 became 107/97/111.
  - The mines, factories and defenses spends (2, 3, 4) were lost. Those
    homeworlds had no installations and unchanged minerals and
    concentrations: an AR homeworld's installations are set to 0 after the
    spend.
- **Growth 0 in a running game (RD-P11)** is punished, unlike growth above
  20: message 0x117, flag 0x10, growth set to 1. Nothing else changed,
  since growth 1 gives 7329 points.
- **Several players (RD-P12).** Player 0's race in the 6-player RD-7 game
  was edited to −1058 points.
  - It was first clamped silently into range, then repaired: colonists per
    resource 2500, growth 7, 985 points, flag 0x10.
  - Player 0 got 0x117, and each of the four other human players got
    0x182 ("hacked race discovered"). The computer player's `.M` file has
    no message block at all, so whether it is told is not observable.

### Round 3: the remaining BINARY-ONLY rules (MEASURED, RW08, RD-P13..RD-P21)

Predictions were committed before the runs (7726cc3, fcbcf6e;
`experiments/rd/README.md` "Round 3"). `universe.py check` matched RW08
field by field (65 matches, 0 mismatches) and `races.py turn` matched every
penalty year. Every prediction held except the RD-P21 candidate, which was
written to explain an apparent miss and was ruled out.

- **Repairs at creation (RW08).** A gravity low equal to the immune marker
  made the axis immune (centre and high set to the marker); a high of 120
  became 100 (centre 57); growth 25 became 20. All three races were kept,
  marked tampered.
- **Silent clamps in a running game.** Growth 25 with colonists 2500 (159
  points) became 20 with no message and no flag (RD-P13). Growth −3 became
  1, silently (RD-P18). A research share of 150% became 15%, silently
  (RD-P15; the base share was 0%, and that year's research advanced a
  field, so the year did research with a nonzero share).
- **Clamp before the check (RD-P14).** Growth 25 at −440 points was scored
  at growth 20, still negative, and punished: colonists 2500, growth 16
  (502 points), message 0x117, flag 0x10.
- **Habitat repairs (RD-P16, RD-P17).** A high of 120 was repaired to 100
  and punished (colonists 1800, 538 points). A low equal to the immune
  marker made the axis immune and was punished (colonists 2500, 527).
- **No second punishment (RD-P19, RD-P21).** After RD-P1's punishment the
  race (1042 points, tampered) was left alone for two more years; so were
  RW08's three tampered races (159 to 413 points) in their first year.
  The 0x117 and 0x182 messages seen in those years' turn files are the
  earlier messages carried over (below), not new ones.
- **Computer player (RD-P20).** A computer race at −1173 points with its
  gravity centre one below the midpoint: centre moved back, flag 0x10 set,
  nothing else changed, and the human player got no message.
- **Message carry-over (MEASURED, an oracle side effect).** In these
  pinned runs no player submitted orders, and each year's `.M` message
  block began with the whole previous block, new messages after it
  (RD-P19: 3, 6, 9 messages in years 1 to 3; RD-P21: the 8 messages written
  at creation, then 2 new ones: 0x03f for an owned planet's empty queue and
  0x159 for Super Stealth spying, neither from the penalty). Count only the
  messages after the carried prefix when a multi-year run has no orders.

## Messages to players

Status: catalogue in `MESSAGES.md` (2026-10-07). All 387 message kinds are
listed with trigger, recipient, slots, focus and phase. Rows are CONFIRMED
against message records decoded from the oracle turn files of every corpus
in the apparatus (189 kinds seen, `tools/fleetlab/events.py`), and the rest
are BINARY-ONLY. Elegy writes its own message text from the slots (project
rule); no original string is used.

The MG batch (`experiments/mg`, predictions committed before each run) and
earlier runs settled the binary reading's LEGACY BUG? candidates:

- **CONFIRMED LEGACY BUG:**
  - 0x132/0x134 go to the packet owner (MG-001);
  - 0x181 does not carry the kT (MG-001);
  - 0x0e2/0x0e5 put the destination in the departure slot (OB-021, MG-001);
  - 0x023/0x040 is chosen by the previous planet's growth (MG-002);
  - plural build counts are not merged (MG-002);
  - 0x180 is never sent in 2-player battles, but is sent in 3-race ones (CB-039, CB-042);
  - 0x0fa uses the CB-037 observer test.
- **MEASURED:** load-optimal fuel never takes on fuel.
  - With a fleet target it reports 0x03c/0x03d or hands over the surplus (MG-003).
  - With a planet target, every fuel action is skipped (MG-002, MG-004, MG-006). The binary reading explains this: fuel is handled only for fleet and deep-space targets (`TAKEOVER.md`).

## Client estimates (ES-001)

`docs/ESTIMATES.md` specifies the projections the original client shows:
travel time, fuel use and range of fleets, leg distance, production
completion, research estimates, population growth, value and optimal
value, mining rate. The rules were read from the original program
(private `stars-decomp` `docs/estimates.md`) and measured once.

### Method

One pinned Combat Lab generation 2400 → 2401 (`experiments/es001/gen.py`,
cycles 20000). Player 0 had 9 fleets with two or three legs each (warp 0
and warp 1 legs, a zero-length leg, a 25.495 ly leg, multi-year legs with
a ram-scoop ship and a Fuel Transport, a route through its homeworld's
Space Station, a fleet without the fuel for its first leg), one Scout per
engine with a part-filled tank, 10 planets with production queues
(resource-limited, germanium-limited, no germanium, automatic items, Auto
Alchemy in the middle and at the end), planets of habitability −10% to
100% including one above its maximum population, and research at 10% on
weapons. Predictions were computed from the generated host file with
`experiments/es001/estimates.py` and committed (503745c) before the
client was opened. Raw evidence and screenshots: private
`stars-oracle-apparatus` `evidence/es/es-001/`.

### Result (CONFIRMED, 2026-10-07)

`experiments/es001/check.py`: 149 of 149 readings matched.

| Screen | Readings |
|---|---:|
| Fleet Waypoints tile: distance, travel time, est. fuel usage (and red) per waypoint | 63 |
| Fleet Composition tile: Est. Range (every engine, three mixed fleets) | 23 |
| Production tile: Completion of each queue item | 19 |
| Planet report: Value (optimal value), Mining Rate | 20 |
| Population popup | 10 |
| Research dialog | 5 |
| Fleet report: ETA column, red | 9 |
| Not counted: queue colours, the planet report's resources "A / R" | |

Discriminating cases that held:

- A 25.495 ly leg at warp 5 is 1 year (`trunc(D) ≤ w²`), while its fuel is
  priced as 2 years.
- Fuel estimates priced year by year, the ram-scoop and Fuel Transport
  credits (45 and 25 mg, against 114 and 103 for the whole leg at once),
  and the running total restarting after a waypoint at the homeworld
  (251, not 362).
- The ideal warp for range: each engine's warp in `ESTIMATES.md`,
  including the scoops' free-warp step down and warp 10 only for the five
  named engines.
- The production estimate's carried item (an alchemy item left over from
  the real year), Auto Alchemy as the target ("As Needed") and as the last
  item ("14 - ??? years"), automatic items blocked by germanium
  ("Unknown") and a factory with no germanium ("Never").
- Projected research budget (163) from the first estimated year of every
  queue.

Not exercised by ES-001 (ES-002 below): stargate legs, "Skipped", Generalized Research, a field at
level 26, distances with a zero tens-of-hundredths digit (e.g. 20.05).

## Client estimates follow-up (ES-002)

### Question

Do the five client estimates ES-001 left unmeasured behave as read:
stargate legs, "Skipped", Generalized Research, a field at level 26 and
distances whose hundredths have a leading zero?

### Method

One pinned Combat Lab generation 2400 → 2401 (`experiments/es002/gen.py`,
cycles 20000). Player 0 (Generalized Research, a legal LRT set) had gates
100/250 on three planets and Space Station gate 100/250 on a fourth, a
150/600 gate on a fifth, and 12 fleets: scouts and freighters ordered
through gates (usable, two gate legs in a row, cargo, beyond range, over
the mass limit, to an own planet without a gate, from a planet without a
gate, to deep space, to another player's planet, to an unowned planet),
and two scouts on short non-gate legs chosen for distances like 20.02.
Two queues held automatic items with nothing to do. Player 1 researched
energy at level 25 with "next field" left at "same field" and enough
resources stored to reach 26 during the year (`KERNEL.md` KX-005).
Predictions were committed (0600161) before the client was opened, with
`expect.tsv` for the host-side result. Raw evidence and screenshots:
private `stars-oracle-apparatus` `evidence/es/es-002/`.

### Result (2026-10-07)

`experiments/es002/check.py`: 81 of 83 matched. Both misses are fleet 7
(own gate → an unowned planet): its waypoint tile and report ETA showed
"Uncertain", predicted "Never".

Interpretation: the prediction model treated every unowned planet as
reported to the viewer this year. That planet was not in player 0's
2401 `.M1` (its reports list planets 0, 2, 4, 11, 15–19, 21), so the
client's rule as read ("Never" only for an unowned planet reported this
year) gives "Uncertain". `estimates.py` now takes the reported planets
(`predict.py after.dump m1.dump` gives "Uncertain" for both). The
"reported unowned planet → Never" branch itself was not exercised and
stays BINARY-ONLY.

| Item | Observed | Status |
|---|---|---|
| Stargate legs (11 fleets) | 1 year, cumulative after the gate; "Unload" with cargo; "Danger" beyond range and over the mass limit; "Never" without a gate at either end or in deep space; "Uncertain" for another player's or an unreported planet; fuel 0mg; warp box "Use Stargate" | CONFIRMED |
| Distances | 319.01 → "319.1", 20.02 → "20.2", 10.05 → "10.5", 7.07 → "7.7" | CONFIRMED, LEGACY BUG (display) |
| "Skipped" | Auto Defenses at the defense limit, Auto Mines at the mine limit: "Skipped" in grey; following items unaffected | CONFIRMED |
| Planet report, queue of one skipped item | "--- Queue is Empty ---" | MEASURED |
| Generalized Research | 801 needed, projected 261 → 7 years | CONFIRMED |
| Level 26 (KX-005) | energy 26, current field weapons, next field `<Same field>`; weapons 595 needed, 16 years; energy "Maxed Out" (needed and time) | CONFIRMED |

Not predicted, observed: player 0's Est. Range for the three designs (561,
166, 175 l.y.).

## Computer players: Turindrone and Automitron designs (AP-001..AP-005)

Specs: `docs/ai/turindrone.md`, `docs/ai/automitron.md`. Predictions were
committed in the private binary reading before the runs. Raw evidence:
private `stars-oracle-apparatus`, `evidence/ai/ap/` (AP-001, AP-002) and
`evidence/ai/ai01/` (AP-003).

- **Setup (AP-001, AP-002).** A small map (size 1, density 1, positions 1,
  seed 4101, random events on) with three players: a human race (player
  1), an expert Turindrone (player 2) and an expert Automitron (player 3).
  The built-in races were Turindrone SS with IFE, ARM, MA and RS, and
  Automitron IS with GR, OBRM, NAS and LSP (`AI.md` §3). Before 2400 was
  generated, both computer players' tech was edited in the `.HST`
  (`hst-edit … player=N tech=…`): AP-001 to energy 10, weapons 10,
  propulsion 10, construction 13, electronics 10, biotech 10; AP-002 to 20
  in every field. Two years were generated at cycles 20000, and each
  computer player's order file was captured.
- **Year 2400:** no ship-design orders. The `.HST` already held the
  edited tech, but a computer player plans from its own player file, which
  still held the old tech (`ORACLE.md`).
- **Year 2401 (CONFIRMED):** every ship-design order of both players in
  both games was as predicted. The table gives 33 slot records in all.
  Each part is listed with its count, in hull slot order. Turindrone
  deleted slot 2 first, because its starting Midget Miners were scrapped
  in 2400. Automitron deleted slot 1 first, because its starting Colony
  Ship was scrapped in 2400.

| Game | Player | Slot | Design |
|---|---|---|---|
| AP-001 | Turindrone | 8, 15 | Rogue: 2 Trans-Galactic Fuel Scoop, 3 Shadow Shield, 2 Super Cargo Pod, 1 Pick Pocket Scanner, 2 Neutronium, 2 Delta Torpedo, 2 Maneuvering Jet, 1 Jammer 20, 1 Battle Computer |
| AP-001 | Turindrone | 9 | Galleon: 4 Trans-Galactic Fuel Scoop, 2 Bear Neutrino Barrier, 2 Neutronium, 3 Delta Torpedo, 3 Maneuvering Jet, 2 Battle Computer, 2 Super Cargo Pod, 2 Pick Pocket Scanner |
| AP-001 | Turindrone | 10 | Destroyer: 1 Trans-Galactic Fuel Scoop, 1 Delta Torpedo ×3 slots, 2 Depleted Neutronium, 1 Maneuvering Jet, 1 Battle Computer |
| AP-001 | Turindrone | 2 | Miner: 2 Trans-Galactic Fuel Scoop, 2 Maneuvering Jet, Robo-Super-Miner 2, 1, 2, 1 |
| AP-001 | Turindrone | 12 | Privateer: 1 Trans-Galactic Fuel Scoop, 2 Shadow Shield, 1 Jammer 20, 1 Mine Dispenser 50 ×2 slots |
| AP-001 | Turindrone | 13 | Stealth Bomber: 2 Trans-Galactic Fuel Scoop, 4 M-70 Bomb, 4 Neutron Bomb, 1 Jammer 20, 3 Jammer 20 |
| AP-001 | Turindrone | 4 | Battleship: 4 Trans-Galactic Fuel Scoop, 1 Jammer 20, 8 Bear Neutrino Barrier, Delta Torpedo 6, 6, 2, 2, 4, 6 Depleted Neutronium, 3 Jammer 20, 3 Battle Computer (template b, the only one buildable) |
| AP-001 | Automitron | 4 | Medium Freighter: 1 Trans-Galactic Fuel Scoop, 1 Super Cargo Pod, 1 Croby Sharmor |
| AP-001 | Automitron | 5 | Super Freighter: 3 Trans-Galactic Fuel Scoop, 3 Super Cargo Pod, 5 Croby Sharmor, 2 Jammer 20 |
| AP-001 | Automitron | 14 | Destroyer: 1 Radiating Hydro-Ram Scoop, 1 Delta Torpedo ×2 slots, 1 Maneuvering Jet, 2 Neutronium, 1 Maneuvering Jet, 1 Battle Computer |
| AP-001 | Automitron | 1 | Medium Freighter: 1 Radiating Hydro-Ram Scoop, 1 Colonization Module, 1 Croby Sharmor |
| AP-001 | Automitron | 6 | Privateer: 1 Radiating Hydro-Ram Scoop, 2 Croby Sharmor, 1 Jammer 20, 1 Mine Dispenser 50, 1 Speed Trap 20 |
| AP-001 | Automitron | 2 | B-17 Bomber: 2 Trans-Galactic Fuel Scoop, 4 M-70 Bomb ×2 slots, 1 Jammer 20 |
| AP-001 | Automitron | 9 | Battleship: as Turindrone's slot 4, with 8 Croby Sharmor and 6 Neutronium (template b) |
| AP-002 | Turindrone | 8, 15 | Rogue: 2 Galaxy Scoop, 3 Elephant Hide Fortress, 2 Super Cargo Pod, 1 Robber Baron Scanner, 2 Valanium, 2 Rho Torpedo, 2 Overthruster, 1 Jammer 30, 1 Battle Nexus |
| AP-002 | Turindrone | 9 | Galleon: 4 Galaxy Scoop, 2 Elephant Hide Fortress, 2 Valanium, 3 Rho Torpedo, 3 Overthruster, 2 Battle Nexus, 2 Super Cargo Pod, 2 Robber Baron Scanner |
| AP-002 | Turindrone | 10 | Destroyer: 1 Galaxy Scoop, 1 Rho Torpedo ×3 slots, 2 Valanium, 1 Overthruster, 1 Battle Nexus |
| AP-002 | Turindrone | 2 | Miner: 2 Galaxy Scoop, 2 Overthruster, Robo-Ultra-Miner 2, 1, 2, 1 |
| AP-002 | Turindrone | 12 | Privateer: 1 Galaxy Scoop, 2 Elephant Hide Fortress, 1 Jammer 30, 1 Mine Dispenser 50 ×2 slots |
| AP-002 | Turindrone | 13, 14 | Stealth Bomber: 2 Galaxy Scoop, 4 Cherry Bomb, 4 Enriched Neutron Bomb, 1 Jammer 30, 3 Jammer 30 |
| AP-002 | Turindrone | 4 | Battleship: 4 Galaxy Scoop, 1 Jammer 30, 8 Elephant Hide Fortress, 6 Gatling Gun, 6 Disruptor, 2 Bludgeon, 2 Disruptor, 4 Phased Sapper, 6 Valanium, 3 Energy Capacitor ×2 slots (template a) |
| AP-002 | Automitron | 4 | Medium Freighter: 1 Trans-Galactic Mizer Scoop, 1 Super Cargo Pod, 1 Elephant Hide Fortress |
| AP-002 | Automitron | 5 | Super Freighter: 3 Trans-Galactic Mizer Scoop, 3 Super Cargo Pod, 5 Elephant Hide Fortress, 2 Jammer 30 |
| AP-002 | Automitron | 14 | Destroyer: 1 Radiating Hydro-Ram Scoop, 1 Rho Torpedo ×2 slots, 1 Overthruster, 2 Valanium, 1 Overthruster, 1 Battle Nexus |
| AP-002 | Automitron | 1 | Medium Freighter: 1 Radiating Hydro-Ram Scoop, 1 Colonization Module, 1 Elephant Hide Fortress |
| AP-002 | Automitron | 6 | Privateer: 1 Radiating Hydro-Ram Scoop, 2 Elephant Hide Fortress, 1 Jammer 30, 1 Mine Dispenser 50, 1 Speed Trap 20 |
| AP-002 | Automitron | 2 | B-17 Bomber: 2 Trans-Galactic Mizer Scoop, 4 Cherry Bomb ×2 slots, 1 Jammer 30 |
| AP-002 | Automitron | 3 | B-52 Bomber: 3 Trans-Galactic Mizer Scoop, 4 Cherry Bomb ×4 slots, 2 Jammer 30, 2 Elephant Hide Fortress |
| AP-002 | Automitron | 9 | Battleship: 4 Trans-Galactic Mizer Scoop, 1 Jammer 30, 8 Elephant Hide Fortress, Rho Torpedo 6, 6, 2, 2, 4, 6 Valanium, 3 Jammer 30, 3 Battle Nexus (template b) |

- **AP-003 (MEASURED)** is the AI01 capture: one expert of each type,
  2400–2402, with no edits (`AI.md` Status). Turindrone in 2400:
  - queued 5 of design 0 on a 128-planet map;
  - merged and scrapped its two Midget Miner fleets;
  - loaded 25 kT of colonists into its Colony Ship, which then stayed at
    home through 2402;
  - wrote no design orders in 2400–2402.

  Automitron:
  - scrapped its Colony Ship in 2400;
  - in 2401 and 2402, deleted and rewrote slot 1 as a Medium Freighter
    with 1 Long Hump 6, 1 Colonization Module and 1 Cow-hide Shield, at
    tech 3 in every field (predicted exactly);
  - queued no ships, because homeworld population was below the
    production threshold.

- **AP-004, AP-005 (MEASURED, one stream each).** One generated year from
  AP-001's year-2401 game (apparatus `evidence/ai/ap/`, run001/y2401
  base), predictions committed before the runs. AP-005 ran it unedited;
  AP-004 emptied both homeworld queues, raised Automitron's homeworld to
  160,000 colonists and set its Scout fleet's fuel to 0. Held:
  - Turindrone deleted and rewrote slots 1, 2 and 12 (none of their ships
    alive) exactly as predicted and kept slot 0;
  - Turindrone queued nothing while its queue held a ship (AP-005); with
    an empty queue it queued four colony ships, then three Privateers
    (AP-004);
  - Turindrone's starting Scout got a scrap task at the homeworld;
  - Automitron rewrote slot 1 as predicted; it queued nothing at 25,800
    colonists (AP-005) and three of design 6 at 160,000 (AP-004);
  - Automitron's two-waypoint Scout fleet at 0 mg was scrapped (AP-004).

  One prediction missed: Automitron's Scout fleet with fuel (AP-005) was
  predicted to get no order, but in both runs its second waypoint's warp
  went 6 → 5, target and task unchanged. The personality's rule did leave
  the fleet alone; the change is the shared core's whole-year arrival
  slowdown (`AI.md`, AI-11). Extra queue lines in both runs were the shared automation's.

## Computer players (AI-0..AI-25)

`docs/AI.md` specifies the original computer players' shared rules. They
were read from the original program (private `stars-decomp` `docs/ai.md`)
and checked by capturing every computer player's order file as the host
wrote it during pinned generations (the host deletes these files after
use). Raw captures: private `stars-oracle-apparatus` `evidence/ai/`.

### Corpora

- **AIX**: small map, seed 211, one human race that submits nothing and
  one expert computer player of each type; 61 pinned generations,
  2400–2460, cycles 20000.
- **AI01**: another small map (seed 4101), same line-up, 2400–2402; a
  rerun at the same cycles gave identical orders, and another stream
  changed only design names, starbase pictures and packet destinations.
- **AI02, AI03, AI04**: the stage-1 games, one computer player of each
  type at easy, standard and harder; 2400–2424, 2400–2424 and 2400–2454.
- **UG**: the universe-generation corpus's computer players (73 players).
- **OB**, **MF**: the universe-objects and minefield runs (OB-001..OB-031,
  MF-1..MF-15; "Universe objects"). Most are one pinned year in the
  Combat Lab universe with two JOAT players and the objects written into
  the start file. Exceptions, as each case says: wormhole creation
  (OB-006) used new games built from definition files; some runs span
  more than one year (OB-019, OB-025 and OB-027 three); and some
  cases give a player another race, such as a Space Demolition or
  Packet Physics owner. Their after-year files are also read as a
  corpus of object sightings (SC-038).

### Cases

| Case | Prediction | Result |
|---|---|---|
| AI-0 | Built-in race table (`AI.md` §3) equals every computer player's race record | CONFIRMED: 85 players (UG 73, AIX 6, AI01 6), 23 of 24 type × level pairs, no mismatch |
| AI-1 | Research budget, field and next field each year, and when the research order is written (`AI.md` §4) | CONFIRMED: 384 of 384 player-years (AIX 366, AI01 18) |
| AI-2 | Starbase designs created each year: slots, hull, parts, counts, picture (`AI.md` §5) | CONFIRMED: 320 of 320 player-years (HE SS IS CA PP), including the 2450 family switch |
| AI-3 | Robotoid scraps fleets holding its slot-0 Scout until year index 20 | MEASURED once: AIX 2400, the Scout fleet is scrapped and gone the next year |
| AI-5 | Macinti scraps early fleets and builds and scraps its slot-1 colonizer each year until design 7 exists | MEASURED: AIX 2400–2406 |
| AI-8 | Robotoid ship designs each year: ageing deletes, the design ladder, the slot-0 Frigate rebuild; slot, hull, parts, counts and picture (`docs/ai/robotoid.md` §2) | CONFIRMED: 61 of 61 player-years (AIX), covering 7 design orders and every year without one |
| AI-9 | Robotoid production: each planet's newly queued ships follow the order freighter, colonizers, frigates, armada or warships, slot 14/15, using each group's newest design; none at planets without a starbase or with fewer than 20,000 colonists (`docs/ai/robotoid.md` §3) | MEASURED: 1,205 of 1,205 planet-years (AIX), 70 with ships queued |
| AI-10 | Computer players keep no memory between years: the memory block in the history file is never read back (`AI.md` §1) | CONFIRMED (prediction committed before the runs): for one AIX year, replacing Robotoid's memory block with junk hubs, with hubs on all its planets, or putting an attack cooldown into Cybertron's block left the orders and memory output unchanged; a rerun reproduced the year exactly. Only a header word of the written history file differed when the input file size changed. Earlier indirect evidence: Cybertron's cooldown is never a decremented value in 61 years |
| AI-11 | Waypoint-1 warp re-pick at the end of every computer player's turn (`AI.md` §11 "Warp choice") | CONFIRMED: AIX 1,680 of 1,680 rewritten warps, 2,043 of 2,043 fleets left alone, 207 of 207 warps set earlier in the turn; 38 fleets in enlarged foreign minefields all in the random set; the AI oracle's round-2 runs all agree, including a Scout's 6 → 5 |
| AI-12 | Robotoid fleet orders each year: waypoint-0 task and waypoint-1 target and task per own fleet (`docs/ai/robotoid.md` §4), with the planet view of `AI.md` §1 | MEASURED: every own Robotoid fleet in AIX's 61 years agrees (146 colonize targets, 58 unloads at foreign planets, 219 freighter targets, 22 armada and 123 attack orders as outcome sets, 1,251 fleets left alone); obsolete fleets, join-up and wormholes never occurred. The planet-view rule is CONFIRMED by two edited AI oracle runs (history-file owners of other players → scrap; the same planets as its own → colonize) |
| AI-13 | Cross-player leak of empty design slots (`AI.md` §1 "State leaking between computer players"): Macinti's slot-4 rule reads the creation year Cybertron left in slot 3 | MEASURED (prediction committed before the runs): from AIX 2448, moving only Cybertron's slot-3 creation year from 2442 to 2428 made Macinti create slot 4 (a Cruiser) in 2449 in 2 of 2 random streams; unedited controls never did; Cybertron's own orders were unchanged. Later years then differed for other computer players through the shared random stream |
| AI-14 | Rototill never makes, deletes, ages, splits or merges ship designs (`docs/ai/rototill.md` §1) | MEASURED: no ship design order in 166 Rototill player-years (AIX 2400–2460, AI02/AI03 2400–2424, AI04 2400–2454); only starbase design orders |
| AI-15 | Rototill production: at most one Colony Ship a year, on the lowest-id own planet with a starbase and 100,000 colonists, when none is alive or alive + 1 < U (`docs/ai/rototill.md` §2) | MEASURED: 3 colony ships queued as predicted (AIX 2444, 2446; AI02 2414), 108 qualifying planet-years and 70 other planet-years with none; the alive + 1 < U branch never reached (U ≤ 2) |
| AI-16 | Rototill colony ships: invasion unload or route cut in pass 1; load 2,500 colonists and colonize the nearest seen planet habitable after terraforming, or a wormhole, in pass 2; empty ones go home (`docs/ai/rototill.md` §3) | MEASURED: 98 idle colony-ship years (4 colonize, 2 wormhole, 92 no target), 1 unload, 1 cut, 1 move home, colonist loads in 166 of 166 years; ignoring habitability breaks 89 rows |
| AI-17 | Rototill scouts move to the nearest never-seen planet (in neither turn file nor history file) not targeted by another own fleet, 5% wormhole when orbiting (`docs/ai/rototill.md` §3) | MEASURED: 75 of 75 scout moves; counting history-only planets as never seen breaks 31; fallbacks not exercised |
| AI-18 | Cross-player leak of armada parameters (`AI.md` §1 "State leaking between computer players"): Cybertron's armada stay-or-leave test reads values only Robotoid, Turindrone, Automitron and Macinti set | MEASURED (prediction committed before the runs): for AIX 2453–2460, with the earlier computer players' captured orders submitted but their turns not run (values 0), every Cybertron armada idle at an own planet left home, 11 of 11 armada-years; with Automitron's values all stayed. Skipping a turn alone does not move them. Skipping Robotoid's turn shifted 17–19 of Cybertron's random-dependent order lines (shared random stream) |
| AI-19 | Cybertron ship designs each year: the slot-0 delete, the Destroyer, Privateer, warship-group and guard steps with their list ranges; slot, hull, parts and counts (`docs/ai/cybertron.md` §2) | CONFIRMED: 61 of 61 player-years (AIX), including every year without a design order; random ranges checked as sets of allowed outcomes |
| AI-20 | Cybertron starbase queueing: which own planets without a starbase get a starbase item, and from which family, counting colonists moved by the same turn's fleet pass (`docs/ai/cybertron.md` §4.3) | MEASURED: 335 of 335 planet-years (AIX); four planets under 50,000 colonists at the start of the year got their item only because Cybertron's freighters unloaded there earlier in the turn |
| AI-21 | Cybertron fleet orders each year: merges, waypoints, cargo, scrap and battle plan per own fleet, with the planet view of `AI.md` §1 and the inherited armada parameters (`docs/ai/cybertron.md` §5) | MEASURED: 2,064 of 2,064 own fleet-years (AIX), 4 of them as sets of allowed outcomes (buddy joins); 356 cargo, 174 waypoint-add and 278 waypoint-change records reproduced. Deliberately wrong variants each fail: keeping the fleet pass's planet notes (64 fleet-years differ), no planet history (22), no in-turn cargo effect (20), zero armada parameters (13). The zero-parameter case was also run on the oracle: every idle armada left home (11 of 11 armada-years). Obsolete fleets, minelayers, invasions and armada departures never occurred |
| AI-22 | Turindrone fleet orders each year: merges, waypoint-0 task and waypoint-1 target and task per own fleet, with the planet view of `AI.md` §1 and scout targeting (`docs/ai/turindrone.md` "Fleet pass") | MEASURED: every own Turindrone fleet in AIX's 61 years agrees, 689 of 689 fleet-years (618 fully determined, 71 as outcome sets from random gates), including one scout wormhole jump. Discriminating misreadings break rows: every planet known 54, ignoring the history file 73, Robotoid's per-task colonize marks 23, no unload-or-clear step 17, unarmed-fleet test dropped 58. Bombers never occurred, so the armada parameters were not exercised |
| AI-23 | Automitron fleet orders each year, rule order: multi-waypoint fuel scrap, Privateers, colonizers, transports, bombers, scouts (`docs/ai/automitron.md` "Fleet pass") | MEASURED: every own Automitron fleet in AIX's 61 years agrees, 264 of 264 fleet-years (251 fully determined, 13 as outcome sets), including one scout wormhole jump and one colony ship scrapped at 0 mg of fuel. Every planet known breaks 20 rows, ignoring the history file 62. Bombers never occurred |
| AI-24 | Cybertron packets each year (`docs/ai/cybertron.md` §6): attack and scanner-shot warps `w`, attack packet counts, scanner-shot destinations from the edge-point, slide and inset rule, and packet marks on the planet one id above a scanner shot's destination; draw bounds `Random(3W/10)` and `3W/20` | MEASURED: AIX 2400–2460, 118 of 118 scanner warps and 16 of 16 attack warps and packet counts; 118 of 118 scanner destinations reachable from the recorded direction (the band covers about 6 of 128 planets; the neighbouring directions reach only 12 and 19); none was Cybertron's own; directions only 1..6; 85 of 85 scanner packets marked the planet one id higher, and 105 of 105 marks are explained. The individual draws were not replayed (stream position unknown). Draw bounds: the same floating-point instructions run in the oracle's DOSBox give exactly 0.3·W and 0.15·W for all five galaxy sizes at both 64- and 53-bit precision settings (not a game run); real x87 hardware is UNRESOLVED |
| AI-25 | Robotoid's lay-mines waypoint keeps duration 5 (indefinitely) and its second field 5 from year to year (`docs/ai/robotoid.md` §4) | MEASURED: AIX, Robotoid fleets 5 and 6 held the task with both fields 5 in 20 and 10 consecutive host files (2441–2460, 2441–2450), 30 fleet-years, never changed; every other computer player's lay-mines waypoint carried the same values. Raw reading: private `stars-oracle-apparatus` `evidence/ai/aix/laymines` |

In 2400 every expert type except Rototill scrapped at least one starting
fleet at its homeworld (waypoint-0 scrap order; the fleets were gone the
next year).

## Computer players: stage 1 (AI-1..AI-5, O-53)

Question: do the computer players' yearly research choices, starbase
designs and early fleet scrapping follow the rules read from the binary, at
every level, and do computer planets trade with the Mystery Trader as
predicted? Predictions were committed before the runs (private
`stars-decomp` AI-1..AI-5 and O-53). Raw evidence is in the private
`stars-oracle-apparatus` `evidence/ai/stage1` and `evidence/ai/ap/round2`.

Method: pinned years (`pinned-turn` with `PINNED_CAPTURE`, cycles 20000) on
small maps with a human player and one computer player of each type. The
host writes each computer player's orders before it generates the year, and
the capture keeps them. Each player-year is compared with the prediction.

- **CONFIRMED: research choices (AI-1) and starbase designs (AI-2) at Easy,
  Standard and Harder.** Easy and Standard games of 25 years and a Harder
  game of 55 years (so past year index 50, where the starbase design family
  changes). They agree on 150, 150 and 330 player-years. Earlier Expert runs
  agreed on 384 and 320 player-years.
- **MEASURED: Robotoid scraps its scout fleets early (AI-3).** While the
  year index is at most 20, every Robotoid fleet holding its first ship
  design is scrapped. This agreed in 105 of 105 player-years over the three
  levels.
- **MEASURED: Macinti's early scrapping and colonizer loop (AI-5).** It
  agreed in 105 of 105 player-years over the three levels.
  - While the year index is below 11, Macinti scraps fleets holding its first
    or third ship design.
  - While no seventh ship design exists, it also scraps an idle colonizer
    fleet at a planet, which, with a new colonizer each year, gives a
    build-and-scrap loop.
  - The loop ended in 2400 (Easy), 2413 (Standard) and 2407 (Expert). In each
    case it ended in the year the player created its seventh design, and a
    design created in that year's orders already counts.
  - The scrap pass sees fleets after that year's whole-fleet merges. At
    Harder in 2400 a merge emptied and deleted a fleet before scrapping. The
    same fleet number then went to the next year's new colony ship.
- **MEASURED: Robotoid scraps an idle colonizer with no target (AI-4).**
  In two setups (Harder, year index 5), Robotoid had three idle colonizer
  fleets at its homeworld.
  - With every other planet owned in its own view, all three were scrapped.
  - With one planet left free, the first fleet went to colonize it, and the
    other two were scrapped. A planet one colonizer takes is not offered to
    the next in the same year.
- **MEASURED: a computer player plans from its own view, not the host file.**
  - Changing planet owners only in the host file left its orders unchanged.
    The first setups therefore did not test AI-4: the colonizers flew to the
    newly owned planets and came back.
  - Owner records added to its player file changed the orders as predicted.
  - Owner records added only to its history file count too, once the file is
    well formed (its planet-record count raised, and a record for the owner
    player). The colonizers were then scrapped exactly as with the player-file
    edit. An earlier history-file edit without those two fixes had no effect.
  - History records that name the computer player itself as owner read as
    unowned: with such records it colonized as if they were not there.
- **CONFIRMED: computer planets trade with a waiting Mystery Trader (O-53).**
  - Setup: four computer planets near the Trader's end point, each with a
    starbase, one at each of Standard, Harder and Expert (two Expert).
    Surface minerals were 3,600 kT, or 6,000 kT on one Expert planet.
  - The Harder planet (3,600 ≥ 3,500) and the 6,000 kT Expert planet traded
    for the research item. Each player gained six tech levels, given to the
    lowest fields (0,0,1,0,0,0 → 2,1,1,1,1,1). Each planet paid its level's
    threshold: 3,500 or 5,000 kT, germanium first, then boranium, then
    ironium.
  - The Standard planet and the 3,600 kT Expert planet (below 5,000) did not
    trade.
  - No messages reached the computer players. There was no second trade the
    next year.
  - The result was the same with a human fleet waiting at the Trader's end
    point.
- **Oracle note: removing fleets breaks computer orders.** A host file built
  without a computer player's fleets made the host reject that player's
  order file ("appears to be corrupt") and stop, since the orders named
  fleets that no longer existed. Keep the computer players' fleets when
  building such setups.
- **Turindrone and Automitron production and fleet passes (AP-004, AP-005).**
  Seven predictions held, about these behaviors:
  - which ship designs get rebuilt while none of their ships is alive;
  - scrapping a long-lived scout;
  - the Turindrone's colony-ship and privateer production on an empty queue;
  - the Automitron's production only above 150,000 colonists;
  - scrapping a fleet that has run out of fuel.

  One miss: the Automitron changed its scout's second waypoint to a new
  planet, where the prediction left a two-waypoint fleet alone. This went to
  the objects lane.

## Production-queue edits through the client (LQ-0..LQ-7)

Status: CONFIRMED for LQ-1..LQ-4, LQ-5b and LQ-6; MEASURED for LQ-5 and
LQ-7 (predictions missed), 2026-10-07. Rules: `LIMITS.md` "Production-queue
replace" and "Production queue"; the case table is `LIMITS.md` "LQ".

### Question

What the host keeps when the client replaces a planet's production queue,
and which limits the client's Production dialog enforces.

### Method

Predictions from the decomp lane, committed before each batch. Combat Lab
with research at 100%, so production barely touches the queue, and a
pinned base year. Each case is one client session
(`tools/fleetlab/client-orders`) and one pinned year (cycles 20000). LQ-3
edits the host file's old queue between the client's view and the host
year, so the client submits progress the host has no record of. Commands
and specs: `experiments/lq/`. Raw files: private apparatus `evidence/lq/`.

### Result

- A partially built item keeps its progress when moved or when its count
  changes; an item removed and added again starts at 0.
- The host keeps a submitted percentage only against an old partial item of
  the same id and kind, matched in queue order, count ignored: in LQ-3 the
  client's 49% Factory was kept against an old 20% Factory ×9, and the
  client's 30% Mine, second Factory and 50% Probe went to 0.
- Clear leaves no queue and message 0x3f.
- The dialog refuses a 41st item, clips a count at 1020 and holds Auto
  Alchemy at 1.
- Missed: Add with the Top row selected merged into the Factory below it
  (LQ-7); and the factories in the whole queue are limited to 1020 (LQ-5),
  after which Factory leaves the buildable list.

## Ship-count boundary through the client (CO-06)

Status: MEASURED, 2026-10-07. Full record: `experiments/fc/README.md`
"CO-06, ship-count boundary". Summary for `LIMITS.md`:

- The client's Merge Fleets was disabled for two 16000-ship fleets (it was
  enabled for 10 + 10 and 2 + 2), so the direct merge order's boundary is
  not reachable with legal orders.
- The two-fleet ship exchange instead: the client stops the destination at
  32766; the host stored 32765 each time (the extra ship lost), and moved
  cargo and fuel by the share of ships moved. Controls kept 32765 and 32000.

The same file records the other client-order cases, among them CO-07 and
CO-08 (deleting and editing designs in use).
