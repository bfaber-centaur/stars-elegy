# Kernel specification: peaceful economy and fleet movement

Behavioral specification of the J-RC3 rules an independent implementation
needs for a peaceful single-player turn and for ordinary fleet movement:
habitability, population, resources, installation caps, mining, research,
production, movement and fuel. It is written for an implementer working
only from this public repository.

`PARITY.md` holds the experiment records these rules come from. This file
restates them as rules with test vectors and adds rules that so far come
only from white-box analysis of the original program (private
`stars-decomp`, promoted here as behavior only).

## Status of each rule

Every rule carries one status:

- **CONFIRMED**: a white-box reading agrees with original-game oracle
  observations. The test vectors given for it are ground truth.
- **ORACLE**: measured in the original game but not yet matched to a
  white-box reading.
- **BINARY-ONLY**: read from the original program's arithmetic, with no
  oracle observation yet. Vectors are worked from the rule, not observed.
  Expect most of these to hold, but treat them as predictions: they are
  listed for oracle testing.

"Confirmed" covers the measured scope only (race, habitability, cases).
Each rule says what that scope was.

## Conventions

- Integers. Every division truncates toward zero (`trunc`). Where the
  operands can be negative this is said explicitly; it differs from floor.
- Population is held in **units of 100 colonists** ("units"). 1,000,000
  colonists = 10,000 units.
- Percentages are integers (hab 100 = 100%).
- `rand(n)` is a uniform draw in `0..n−1` from the game's random generator.
  The oracle restarts the game for each generated year, which makes random
  draws nearly identical from year to year (`ORACLE.md`). Random outcomes in
  the oracle corpus are therefore correlated, not independent samples.
  Tests of random rules should inject the generator.

## Turn order (BINARY-ONLY except where noted)

One year, in order:

1. Players' orders are applied, one player at a time in a random order.
2. Waypoint tasks that act before movement (unload, scrap, colonist drops,
   load).
3. Mineral packets, wormholes and other space objects move; then fleets
   move (see Movement).
4. Production, in this order inside the phase: mining for every planet,
   then per planet resources, research tax and production queue, then
   population growth for every planet, then research level-ups, then
   random events.
   CONFIRMED (PG-001..003, PQ-001): mining and resources use the population
   **before** this year's growth; installation caps for auto items use
   population **after** growth (see Production); research uses this year's
   resources.
5. Space objects move again; fleets refuel.
6. Battles (`COMBAT.md`); then waypoint tasks that act after movement:
   unload (including remote mining), colonist drops, a **second research
   level-up check**, then load. The second check raises every field whose
   accumulated research now covers its next level. Research gained from a
   battle therefore becomes a level in the same year (CONFIRMED, CB-018,
   CB-021); the step-4 level-ups have already run by then.
7. Mine sweeping, ship repair, automatic and remote terraforming.
8. The year advances; scores are computed; files are written.

## Habitability

Race: for each axis (gravity, temperature, radiation) a center `c`, a low
`lo` and a high `hi` on the 0–100 internal scale, or "immune" on that axis.
Planet: current environment `v` per axis on the same scale.

Rule (BINARY-ONLY; CONFIRMED only for a planet at the race's center on all
three axes, which gives 100):

1. If any axis is outside `lo..hi`, the planet is hostile:
   `hab = −Σ min(15, distance beyond the nearer edge)` over the axes outside
   their range (−1 to −45).
2. Otherwise, start with `S = 0`, `M = 10000`. Per axis:
   - immune: `S += 10000`;
   - else `d = |v − c|`, `w = c − lo` if `v < c` else `hi − c`,
     `e = 100 − trunc(100·d / w)`, `S += e²`; and if `2d − w > 0`
     (more than halfway to the edge), `M = trunc(M·(2w − (2d − w)) / (2w))`.
3. `x = trunc(sqrt(S/3) + 0.9)` (floating point), `hab = trunc(x·M / 10000)`.

Vectors (race center 50, low 15, high 85 on every axis; BINARY-ONLY except
the first):

| Planet (g, t, r) | hab | Status |
|---|---:|---|
| 50, 50, 50 | 100 | CONFIRMED (PG001) |
| 60, 50, 50 | 92 | BINARY-ONLY |
| 70, 50, 50 | 79 | BINARY-ONLY |
| 85, 50, 50 | 41 | BINARY-ONLY |
| 70, 70, 50 | 58 | BINARY-ONLY |
| 80, 80, 80 | 3 | BINARY-ONLY |
| 90, 50, 50 | −5 | BINARY-ONLY |
| 10, 95, 50 | −15 | BINARY-ONLY |

## Maximum population

In units. Rule:

- ordinary race: `max = 100·hab` for `hab ≥ 5`; `max = 500` for `hab < 5`
  (hostile included). CONFIRMED for hab 100 (10,000 units).
- Hyper-Expansion: `max −= trunc(max/2)`. Jack of all Trades:
  `max += trunc(max/5)`. Then Only Basic Remote Mining:
  `max += trunc(max/10)`. BINARY-ONLY (agrees with the documented
  500,000 / 1,200,000 / +10%).
- Alternate Reality: 0 unless the planet has the owner's starbase; then by
  starbase hull, in hull order: 2,500, 5,000, 10,000, 20,000, 30,000 units,
  regardless of habitability (OBRM +10% still applies). BINARY-ONLY.
- Alternate Reality with maximum 0 (population on a planet without the
  owner's starbase): the original cannot generate the year. If the planet's
  habitability is ≥ 0, population growth divides by the maximum and the
  program stops with an integer divide-by-zero error; no file is written.
  CONFIRMED (KX-001 Z1, from both the player screen and Host Mode).
  LEGACY BUG: there is no original behavior to reproduce, so an
  implementation must choose one and say so. A hostile planet (`hab < 0`)
  takes the hostile death rule, which does not use the maximum, and
  generates normally (CONFIRMED, KX-001 Z3). AR colonization gives the
  planet a starbase; the route to this state in play is deleting the
  starbase's design, which removes the starbase and keeps the population
  (BINARY-ONLY).

Vectors (BINARY-ONLY): HE at hab 100 → 5,000; JOAT at hab 100 → 12,000;
OBRM at hab 100 → 11,000; hab 3 → 500; JOAT+OBRM at hab 79 → 10,428.

## Population growth

State per planet: population `P` (units) and a growth **carry** `k`
(hundredths of a unit, 0–99). The carry is persistent: it is the byte
StarsAPI calls `excessPop`. Race growth rate `G` (percent; doubled for
Hyper-Expansion, BINARY-ONLY).

### Positive habitability (`hab ≥ 0`)

1. `g = G·hab` (growth in hundredths of a percent).
2. Crowding, with `max` from above:
   - `P < trunc(max/4)`: no change to `g`;
   - otherwise, if `P < max`: `c = trunc(1000·P / max)` (permille), and
     `g = trunc(g·(1000 − c)² / 562500)` if `g < 1000`, else
     `g = 10·trunc(trunc(g/10)·(1000 − c)² / 562500)`;
   - if `max ≤ P ≤ max + 10`: no change at all this year (P and k kept);
   - if `P > max + 10` (overcrowded): `g = 2·max(−300, trunc(c/−10) + 99)`
     with `c` as above (negative: deaths).
3. `t = trunc(g·P / 100)` (hundredths of a unit). (For very large products
   the game computes `trunc(g/100)·P`; it uses that value whenever it is at
   least 10,000,000.)
4. `q = trunc(t/100)`, `r = t − 100q` (both truncate toward zero, so negative
   when `t` is). If `q = 0` and `r = 0`, set `r = 1`.
5. `k += r`; if `k ≥ 100`: `q += 1`, `k −= 100`; if `k < 0`: `q −= 1`,
   `k += 100`. `P += q`.

Status: CONFIRMED for an ordinary race (growth 10%, hab 100,
max 10,000) over 36 consecutive years 2400–2436, 11 of them crowded
(27% to 54% of capacity), population **and** carry every year. That race
has `g = G·hab = 1000` exactly, so its crowded years exercise the
quantized branch, and the boundary is inclusive: the unquantized formula
would give 2425 → 2426 growth of 256 units, not the observed 254. The
`g < 1000` branch, other `g` values, overcrowding and the "within 10 units
of max" rule are BINARY-ONLY. The 16/9·(1−x)² curve in `PARITY.md` (H1) is
this rule; its 0–4 unit misses come from the permille truncation, the
quantization of `g` to a multiple of 10, and the carry.

Vectors, CONFIRMED (PG-001..003, `G = 10`, hab 100, max 10,000, start
P 250, k 0 in 2400):

| Year | P | k | | Year | P | k | | Year | P | k |
|---:|---:|---:|---|---:|---:|---:|---|---:|---:|---:|
| 2400 | 250 | 0 | | 2413 | 861 | 90 | | 2426 | 2958 | 17 |
| 2401 | 275 | 0 | | 2414 | 948 | 0 | | 2427 | 3218 | 47 |
| 2402 | 302 | 50 | | 2415 | 1042 | 80 | | 2428 | 3479 | 12 |
| 2403 | 332 | 70 | | 2416 | 1147 | 0 | | 2429 | 3740 | 4 |
| 2404 | 365 | 90 | | 2417 | 1261 | 70 | | 2430 | 3998 | 10 |
| 2405 | 402 | 40 | | 2418 | 1387 | 80 | | 2431 | 4253 | 97 |
| 2406 | 442 | 60 | | 2419 | 1526 | 50 | | 2432 | 4500 | 64 |
| 2407 | 486 | 80 | | 2420 | 1679 | 10 | | 2433 | 4739 | 14 |
| 2408 | 535 | 40 | | 2421 | 1847 | 0 | | 2434 | 4971 | 35 |
| 2409 | 588 | 90 | | 2422 | 2031 | 70 | | 2435 | 5190 | 7 |
| 2410 | 647 | 70 | | 2423 | 2234 | 80 | | 2436 | 5402 | 86 |
| 2411 | 712 | 40 | | 2424 | 2458 | 20 | | | | |
| 2412 | 783 | 60 | | 2425 | 2704 | 0 | | | | |

Worked crowded step (2425 → 2426): `g = G·hab = 10·100 = 1000`, which is
not below 1000, so the quantized branch applies. `c = trunc(1000·2704/10000) = 270`,
`(1000 − c)² = 532900`, `g = 10·trunc(100·532900/562500) = 940`;
`t = trunc(940·2704/100) = 25417`; `q = 254`, `r = 17`; P 2958, k 17.

Vectors, BINARY-ONLY (start `(P, k)`, max, G, hab → result):

| Start | max | G | hab | Result | Case |
|---|---:|---:|---:|---|---|
| 1000, 0 | 7900 | 15 | 79 | 1118, 50 | uncrowded |
| 5000, 30 | 10000 | 15 | 100 | 5330, 30 | crowded, `g ≥ 1000` quantization |
| 3000, 0 | 8600 | 10 | 86 | 3194, 70 | crowded, `g < 1000` |
| 9995, 0 | 10000 | 10 | 100 | 9995, 1 | zero growth adds 1 to the carry |
| 10005, 0 | 10000 | 10 | 100 | 10005, 0 | within 10 units of max: frozen |
| 12000, 0 | 10000 | 10 | 100 | 11949, 60 | overcrowded deaths |

### Hostile planets (`hab < 0`) (BINARY-ONLY)

`t = max(1, trunc(|hab|·P / 10))` hundredths of a unit die:
`q = trunc(t/100)`, `r = t − 100q`; `k −= r`, and if `k < 0`, `k += 100`
and `q += 1`; `P −= q`. (Matches the documented `|hab|/10` percent per
year.) Growth and deaths are computed only for owned planets with a
non-zero population, so the `max(1, …)` never acts on an empty planet
(BINARY-ONLY). Vectors: `P 1000, k 0, hab −5` → `995, 0`;
`P 1234, k 10, hab −15` → `1215, 59`.

### Duplicate-serial penalty (BINARY-ONLY)

A player flagged for a duplicate or invalid serial has `g` halved
(`trunc(g/2)`, applied before crowding) during turn generation, and its
planets' production resources (with a queue) multiplied by 4/5 (truncating).
Not part of normal play; listed because `PARITY.md` records the earlier
halved-growth observation.

## Resources and installation caps

Race settings used: colonists per resource `R0` (in units: the race
wizard's value / 100), factory output `F` (resources per 10 factories),
factories operated `Fo` and mines operated `Mo` (per 10,000 colonists, i.e.
per 100 units).

### Resources per planet

1. Effective population `E = P` if `P ≤ max`, else
   `min(2·max, max + trunc((P − max)/2))` (BINARY-ONLY above max).
2. Non-AR: `resources = trunc(E / R0) + trunc((F·n + 9) / 10)`, where
   `n = min(installed factories, operable factories)`.
3. Alternate Reality: `trunc(sqrt((E / R0)·max(1, energy tech))·
   max(25, hab)·0.1 + 0.999)`, all in floating point, including `E / R0`.
   CONFIRMED at one point (KX-001 Z2: `E = 486`, `R0 = 10`, energy 2,
   hab 100 → `trunc(9.859·100·0.1 + 0.999) = 99`; truncating `E / R0`
   first would give 98).
4. A result of 0 becomes 1 (unless `P = 0`, which gives 0).

AR with maximum 0 has `E = 0`, so 1 resource (CONFIRMED, KX-001 Z3).

CONFIRMED (PG-001..003, `R0 = 10`, `F = 10`, 10 factories): this year's
research resources are `trunc(P/10) + 10` from last year's population, for
every year 2408–2436. Vectors: P 486 → 58, 1042 → 114, 2704 → 280,
5190 → 529. PQ-001 confirms `resources = trunc(P/10)` with no factories.

### Caps (units for `P`, `max`)

| Quantity | Rule | Status |
|---|---|---|
| maximum mines | `max(10, trunc(max·Mo/100))` (AR: 0) | BINARY-ONLY |
| maximum factories | `max(10, trunc(max·Fo/100))` (AR: 0) | BINARY-ONLY |
| maximum defenses | `min(100, max(10, 4·hab))` (AR: 0) | BINARY-ONLY |
| operable mines | `max(1, min(max mines, trunc(P'·Mo/100)))` | CONFIRMED for auto mines (PQ C04, C09, C14) |
| operable factories | `max(1, min(max factories, trunc(P'·Fo/100)))` | CONFIRMED for auto factories (PQ C09) |
| operable defenses | `min(max defenses, 1000, ceil(P'/25))` | CONFIRMED (PQ C13) |
| mines working this year | `min(installed, operable with P' = P)`; AR: `trunc(sqrt(P))` | CONFIRMED (PG mining; AR: KX-001 Z2, Z3, P 486 → 22) |

`P'` is `P` for the year's mining and resources, and `P` plus this year's
growth when production caps are computed. Production caps differ by order
kind:

- **Auto Mines, Auto Factories, Auto Defenses** build at most
  `operable − installed` this year (and at most their count). CONFIRMED
  (PQ C04, C09, C13, C14). Auto Alchemy is not an installation; its count
  is ignored (PQ C05).
- **Plain Mine, Factory and Defenses orders** larger than
  `max(maximum, operable) − installed` are cut to it when the queue
  reaches them, with a message; the order is edited permanently, and
  removed if that is 0 or less. CONFIRMED (PQ C10).

Vectors (PG race, `Mo = Fo = 10`, 100% planet, so maximum mines and
factories are 1000 and maximum defenses 100):

- C09: 48 mines, population 550 after growth → operable 55; Auto Mines ×100
  builds 7 (`max(maximum, operable) − installed` would allow 952).
- C13: 40 defenses, population 1111 after growth → operable
  `ceil(1111/25) = 45`; Auto Defenses ×100 builds 5 (not 60).
- C10: 995 factories, Factory ×10 → cut to `max(1000, operable) − 995 = 5`;
  factories end at 1000.

## Mining

Per planet with an owner and population, per mineral (ironium, boranium,
germanium), with concentration `conc` (stored byte), a per-mineral
depletion fraction `f` (stored byte, 1/256ths of the current concentration
point remaining, 0 meaning a full 256) and `m` working mines:

1. Homeworld floor: on a homeworld, `conc` below 30 counts as 30 for output
   (the stored value is not raised). BINARY-ONLY (PG's ironium sits exactly
   at 30).
2. `prod = conc_used·m`; output `amt = trunc(prod·eff/10)` with
   `eff` = race mine output (AR: 10).
3. Surface minerals gain `trunc(amt/100)`, plus 1 with probability
   `(amt mod 100)/100` (one `rand(100) < amt mod 100` draw per mineral with a
   non-zero remainder). The `+1` mechanism is BINARY-ONLY; the oracle's +0/+1
   pattern is consistent with it but its draws are correlated (see
   Conventions). Draw order (BINARY-ONLY): every planet is mined before any
   planet's production, planets in id order, and within a planet ironium,
   boranium, germanium.
4. Depletion uses `p = trunc(prod/100)` (before `eff` and before the random
   +1) and the stored `conc` clamped for this purpose to
   `cc = 100` if above 100, `25` if below 25 (`10` if below 5):
   repeat while `p > 0` and stored `conc > 1`:
   - `cc` from the current stored `conc` (re-evaluated on every repetition,
     so it changes when `conc` drops below 25 or 5 within the year;
     BINARY-ONLY);
   - `s = f` (or 256 if `f = 0`); `need = trunc(trunc(s·12500/256) / cc)`;
   - if `need ≤ p`: `p −= need`, `conc −= 1`, `f = 0`, and continue;
   - else `f' = trunc((need − p)·256 / trunc(12500/cc))`, raised to 1 if
     smaller and lowered to `s − 1` if not below `s`; set `f = f'` (and if
     that is 0, `conc −= 1`) and stop.

   So one concentration point costs about `12500/cc` units of `p`.
   CONFIRMED: concentration and fraction bytes after every one of 48 PG
   years (homeworld, 10 mines, race mine output 10, concentrations 30, 113,
   84 at 2407).

Vectors (CONFIRMED, PG002 run, 10 working mines, `eff = 10`; fraction shown
as stored, 0 = 256):

| Year | conc I/B/G | frac I/B/G | surface I/B/G | Next year surface delta |
|---:|---|---|---|---|
| 2407 | 30/113/84 | 242/86/157 | 550/713/545 | +3/+11/+8 |
| 2408 | 30/113/84 | 240/61/143 | 553/724/553 | +3/+11/+9 |
| 2409 | 30/113/84 | 238/36/129 | 556/735/562 | +3/+12/+8 |
| 2410 | 30/113/84 | 236/12/114 | 559/747/570 | +3/+11/+9 |
| 2411 | 30/112/84 | 234/243/100 | 562/758/579 | |

Worked: boranium 2407 → 2408: `prod = 1130`, `amt = 1130`, gain 11 (+1 with
probability 30%; this year 0). `p = 11`, `cc = 100`, `s = 86`:
`need = trunc(4199/100) = 41 > 11`, so `f = trunc(30·256/125) = 61`.
Boranium 2410 → 2411: `s = 12`, `need = trunc(585/100) = 5 ≤ 11`: conc
113 → 112, `p = 6`; then `s = 256`, `need = 125 > 6`,
`f = trunc(119·256/125) = 243`.

Remote mining (BINARY-ONLY): a fleet with a remote-mining task, at an
unowned planet, that did not move this year, mines after production with
its mining-robot rate as `m` and `eff` ignored (`amt = prod`), same random
+1 and depletion; no homeworld floor. Robot rates per robot: Robo-Midget 5,
Robo-Mini 4, Robo 12, Robo-Maxi 18, Robo-Super 27, Robo-Ultra 25, Alien 10;
a fleet's total is capped at 4,000.

## Research

Six fields (energy, weapons, propulsion, construction, electronics,
biotech), each with a level (0–26) and accumulated research toward the next
level.

### Level cost

`cost(level L) = base[L] + 10·(sum of the player's six current levels)`,
then by the field's research-cost setting: "costs 75% more" →
`2c − trunc(c/4)`; "normal" → `c`; "costs 50% less" → `trunc(c/2)`; then
doubled when the game's slower-tech option is set.

`base[L]` for L = 1..26: 50, 80, 130, 210, 340, 550, 890, 1440, 2330, 3770,
6100, 9870, 13850, 18040, 22440, 27050, 31870, 36900, 42140, 47590, 53250,
59120, 65200, 71490, 77990, 84700.

CONFIRMED for the normal setting, levels 3–9 of one field (PG). Other
settings and slower tech: BINARY-ONLY.

### Allocation

- Planets without a production queue send all their resources to research
  (CONFIRMED, PG). Planets with a queue send the research tax first
  (`trunc(resources·budget%/100)`, skipped with the leftover-only option)
  and whatever is left after the queue (CONFIRMED, PQ-001).
- All research goes to the current field. Level-ups: while
  `accumulated ≥ cost(level+1)`, subtract the cost and raise the level;
  the excess carries over (CONFIRMED, PG). Several levels per year are
  possible (BINARY-ONLY).
- When a level is gained in the current field and the "next field" choice
  is not "same field", the leftover moves to the new field and the current
  field's accumulation becomes 0; "lowest field" picks the lowest level,
  first in field order on ties (BINARY-ONLY). The new field is checked for
  level-ups the same year with that leftover. An explicit next-field
  choice is used once and then resets to "same field"; "lowest field"
  stays set. Only a level-up in the current field switches fields, also
  with Generalized Research (BINARY-ONLY).
- Generalized Research: the current field gets `trunc((res+1)/2)`; each
  other field gets `trunc((3·res + 19)/20)` (15% rounded up)
  (BINARY-ONLY).
- Research into a field at level 26 (or level 10 for a capped player) is
  lost (BINARY-ONLY).
- Super Stealth gains, per field, `trunc(trunc(spent_by_all/players)/2)`
  when it exceeds 1 (BINARY-ONLY).

Vectors, CONFIRMED (PG003: one player, energy current, next "same field",
other levels 0, 0, 0, 5 (electronics), 0; research = all resources):

| Year | Research added | Energy level | Energy accumulated |
|---:|---:|---:|---:|
| 2407 | | 2 | 65 |
| 2408 | 58 | 2 | 123 |
| 2409 | 63 | 2 | 186 |
| 2410 | 68 | 3 | 54 |
| 2413 | 88 | 4 | 7 |
| 2417 | 124 | 5 | 15 |
| 2421 | 177 | 5 | 638 |
| 2422 | 194 | 6 | 182 |
| 2426 | 280 | 7 | 163 |
| 2431 | 409 | 8 | 389 |
| 2435 | 507 | 8 | 2274 |
| 2436 | 529 | 9 | 343 |

Worked 2435 → 2436: `2274 + 529 = 2803 ≥ cost(9) = 2330 + 10·(8+5) = 2460`;
level 9, carry 343.

## Production

The PQ-001 model in `PARITY.md` ("Production Queues") is CONFIRMED in all
15 cases and is the production specification: research tax first, partial
percentage per component, stopping vs skipping, auto items and their hidden
partial items, Auto Alchemy, installation-order clipping, leftover to
research. Its predictions table doubles as the test vectors.

Partial percentage of one component with `a` available (including what is
already spent on the unit) and cost `c`:
`p = max(trunc((a + 1)·100/c) − 1, trunc(a·100/c))` (100 if `a ≥ c`). Use
this formula as written. It is usually, but not always, the largest
percentage whose truncated cost fits in `a`: for `c = 9`, `a = 4` it gives
54, although 55 would also cost only 4 (CONFIRMED, KX-001 M4: Inner
Strength defense, 4 resources left, 54%).

Which component limits a unit (CONFIRMED where cases are cited,
BINARY-ONLY otherwise): the components are compared in the order Fe, Bo,
Ge, resources, and one replaces the current lowest only if its percentage
is strictly lower. So the first of tied minerals wins, and a mineral wins
a tie with resources (BINARY-ONLY). Two facts are recorded: whether **any**
mineral is short, and whether resources were **strictly** the lowest.

- An auto item with any mineral short is mineral-blocked: without an
  alchemy prefix it is skipped with nothing spent, even when resources
  give the lower percentage (CONFIRMED, KX-001 A7).
- Otherwise the unit is charged up to the lowest percentage (all
  components), and the queue stops there unless an alchemy prefix applies
  (next section).

### Item costs

Per unit, as resources and Fe/Bo/Ge kT, from the owner's race:

| Item | Cost | Status |
|---|---|---|
| Factory (and Auto Factories) | race factory cost; Ge 4, or 3 with "factories cost 1 kT less germanium" | CONFIRMED (PQ-001 cost 10; KX-001 M3 cost 7, M3b cost 15; Ge 3 in M3, M3b) |
| Mine (and Auto Mines) | race mine cost | CONFIRMED (PQ-001 cost 5; KX-001 M3b cost 8) |
| Defenses (and Auto Defenses) | 15 + 5/5/5; Inner Strength `trunc(c·3/5)` of each component (9 + 3/3/3) | CONFIRMED (PQ-001; KX-001 M4) |
| Mineral Alchemy, Auto Alchemy | 100 resources per unit (1 kT of each mineral); 25 with the Mineral Alchemy LRT | CONFIRMED (PQ-001; KX-001 M1, M2) |
| Terraform | 100 resources per step; 70 with Total Terraforming; halved for Claim Adjuster | BINARY-ONLY |

Race settings outside the race wizard's advantage-point budget do not
survive: at the start of turn generation the game sends the player a
message and degrades the race before production (MEASURED once, KX-001
M3: colonists per resource went from 1,000 to 2,400). The binary reading
says the trigger is a negative advantage-point total; the points formula
is not specified here. Test races must be legal.

### Auto Alchemy before a multi-count item (CONFIRMED, KX-001)

An Auto Alchemy that is not the last item does nothing itself; it lets the
next item buy minerals. For a ×n item the purchase is made **one unit at a
time** inside the item's normal unit loop:

1. If the unit's remaining cost is available, it completes; go to the next
   unit.
2. Otherwise the unit takes its partial percentage as usual (every
   component charged up to it). Unless resources were strictly the lowest
   component, alchemy then buys `k = min(trunc(resources / rate), s)`
   units, where `s` is the lowest component's shortfall for this unit
   (`cost − available − already spent`, taken before the partial charge)
   and `rate` the alchemy cost; each unit adds 1 kT of all three minerals.
   An auto item with any mineral short skips the partial charge and goes
   straight to alchemy, even when resources were the lowest; `s` is then
   the resource shortfall (CONFIRMED, KX-001 A6: 1 resource, no germanium,
   Auto Factories → nothing bought, Mineral Alchemy ×1 @1% at the front,
   not a 19% factory).
3. If `k = s`, retry the unit (it now completes). Otherwise the unit keeps
   the percentage from step 2, unchanged by the minerals just bought; if
   resources `r` remain, they become a Mineral Alchemy ×1 item at
   `pct = max(trunc((r + 1)·100/rate) − 1, trunc(r·100/rate))` (the same
   partial-percentage formula as any item; it is not always the largest
   percentage that fits), charging `trunc(rate·pct/100)`, inserted at the
   queue front; the queue stops. The prefix and the item (with its reduced
   count) stay.
4. If every unit of a non-auto item completes, the item and its prefix
   are removed and the walk continues. An auto item stays in the queue
   when it has built its year's count, and so does its prefix, which
   applies again next year (CONFIRMED, KX-001 A5: Auto Alchemy, Auto
   Factories ×2, Mine ×2 with 900 resources and no germanium → 2
   factories, 2 mines, queue Auto Alchemy, Auto Factories ×2, research
   70).

Vectors (PG race: factory 10 + 4 kT Ge, mine 5, alchemy 100; no tax;
minerals 100/100/g before the year):

| Case | Resources | g | Queue | Result |
|---|---:|---:|---|---|
| A1 | 900 | 0 | Auto Alchemy, Factory ×5, Mine ×2 | 2 factories; 108/108/0; Mineral Alchemy ×1 @78%, Auto Alchemy, Factory ×3 @24%, Mine ×2; research 0 |
| A2 | 900 | 6 | same | 3 factories; 108/108/2; Mineral Alchemy ×1 @68%, Auto Alchemy, Factory ×2 @24%, Mine ×2 |
| A3 | 900 | 0 | Auto Alchemy, Auto Factories ×5, Mine ×2 | 2 factories; 108/108/0; Mineral Alchemy ×1 @80%, Auto Alchemy, Auto Factories ×5, Mine ×2 |
| A4 | 820 | 0 | Auto Alchemy, Factory ×2, Mine ×2 | 2 factories; 108/108/0; Mine ×2 @19% (0 resources left) |
| M2 (alchemy 25) | 300 | 0 | Auto Alchemy, Factory ×5, Mine ×2 | 2 factories; 111/111/3; Mineral Alchemy ×1 @15%, Auto Alchemy, Factory ×3 @24%, Mine ×2 |

Worked A1: unit 1 has no germanium, so it takes 24% (`max(1·100/4 − 1, 0)`),
spending 2 resources and 0 kT; alchemy buys the 4 kT short (400); the unit
completes with the remaining 8 resources (410 in all). Unit 2 the same:
80 resources left. Unit 3 takes 24% (2 resources), alchemy can buy none,
and the remaining 78 become Mineral Alchemy @78%. Minerals: +8 kT each,
8 kT of germanium used.

Additional rules, BINARY-ONLY:

- A planet with a production queue of zero items contributes nothing to
  research that year, not even the research tax. (A queue emptied during
  the year is removed, so the next year takes the no-queue path and sends
  everything to research.)
- Resources from ships scrapped at a planet this year with Ultimate
  Recycling (`x`) raise that planet's production resources `r` to
  `r + trunc(x·r/(x + r))`.
- A planetary scanner order on a planet that already has one is removed
  with a message; a mass-driver packet order without a driver or
  destination is removed with a message; a terraform order above the
  remaining terraform capacity is clipped (or removed at 0).
- A planet with 0 resources builds nothing and sends no messages.

## Fleet movement

Coordinates are integers (light-years). `D` = straight-line distance from
the fleet to its current destination (waypoint 1), floating point. `w` =
the warp ordered for that leg (1–10). Engine fuel table `f(w)` per engine
(J-RC3 values in StarsAPI / the game's part data; e.g. Quick Jump 5:
0, 25, 100, 100, 100, 180, 500, 800, 900, 1080 for warps 1–10).

### Distance and arrival (CONFIRMED, FM-001..003)

1. Allowed distance `A = min(trunc(D + 0.9999), w²)`.
2. The fleet arrives exactly on the destination if
   `trunc(D − 0.99999) < A` (equivalently `D < w² + 0.99999` when not fuel
   limited), or if `trunc(D − 0.99999) ≤ 0`.
3. Otherwise it moves `A` along the line: each coordinate becomes
   `x0 + trunc(dx·A/D ± 0.5)`, `+0.5` when the destination coordinate is
   greater than the start, `−0.5` otherwise (round half away from zero; an
   exact half cannot occur between integer points at integer distance).
4. A fleet is in orbit of a planet exactly when its coordinates equal the
   planet's, including a deep-space waypoint that lies exactly on a planet
   (FM-004 OR).
5. Reaching waypoint 1 ends the fleet's movement for the year; leftover
   movement is not carried to the next waypoint. A first waypoint at the
   fleet's own position also uses up the year.

Vectors (FM-001/002, one Quick Jump 5 scout at warp 5, w² = 25, fuel 300;
every one ends with 297 mg):

| Corpus fleet | Start | Destination | D | End | Arrived |
|---|---|---|---:|---|---|
| FM-001 12 | (1250, 1020) | (1275, 1020) | 25.000 | (1275, 1020) | yes |
| FM-001 13 | (1310, 1020) | (1336, 1020) | 26.000 | (1335, 1020) | no |
| FM-001 17 | (1310, 1065) | (1334, 1073) | 25.298 | (1334, 1073) | yes |
| FM-002 18 | (1270, 1015) | (1295, 1020) | 25.495 | (1295, 1020) | yes |
| FM-002 19 | (1305, 1010) | (1331, 1011) | 26.019 | (1330, 1011) | no |
| FM-002 20 | (1200, 1050) | (1207, 1075) | 25.962 | (1207, 1075) | yes |
| FM-001 23 | (1110, 1190) | (1200, 1227) | 97.308 | (1133, 1200) | no |

Worked (FM-001 23): `A = 25`, `25/97.308 = 0.2569`;
`x = 1110 + trunc(90·0.2569 + 0.5) = 1133`,
`y = 1190 + trunc(37·0.2569 + 0.5) = 1200`.
The full per-fleet tables are `experiments/fm00N/{predictions,results}.tsv`
in the movement corpus.

### Fuel cost (CONFIRMED, FM-001..004)

For a move of `L` light-years at warp `w`:

1. Group the fleet's ships by design. Each design has a mass per ship `m`,
   a ship count `n`, a cargo capacity per ship and an engine factor
   `f(w)`.
2. Assign the fleet's cargo (minerals and colonists in kT; fuel has no
   mass) to designs in order of increasing `f(w)`, each up to `n ×` its cargo
   capacity. Designs with equal `f(w)` keep the fleet's own design order
   (BINARY-ONLY).
3. Cost in tenths of a mg per design: `trunc(f(w)·L·(n·m + cargo assigned)
   / 2000)`; designs with `f(w) = 0` cost nothing.
4. Fleet cost in mg: `trunc((Σ tenths + 9) / 10)` (rounded up once per
   fleet).

`L` is `A` from the distance rule: `w²` for a partial move,
`min(trunc(D + 0.9999), w²)` on arrival.

Vectors (CONFIRMED):

- One QJ5 scout (18 kT), 25 ly at warp 5: `trunc(100·25·18/2000) = 22`
  tenths → 3 mg (FM-001 0).
- Seven QJ5 scouts, 36 ly at warp 6: `trunc(180·36·126/2000) = 408` tenths
  → 41 mg, not 7 × 6 (FM-001 42).
- Three QJ5 scouts and one AD8 scout (31 kT), 49 ly at warp 7:
  `trunc(500·49·54/2000) + trunc(100·49·31/2000) = 661 + 75` tenths →
  74 mg (FM-002 32).
- A QJ5 freighter carrying 70 kT with an AD8 scout: the cargo is charged
  at the freighter's engine (FM-002 34).
- Per-design truncation (FM-004 MS): a QJ5 scout and an LH6 scout (23 kT),
  4 ly at warp 2: `trunc(25·4·18/2000) + trunc(20·4·23/2000) = 0 + 0` →
  0 mg (one truncation of the sum would give 1). A QJ5 scout and a Fuel
  Mizer scout (20 kT), 25 ly at warp 5: `22 + trunc(35·25·20/2000) = 22 +
  8 = 30` tenths → 3 mg (not 4).
- Cargo on the cheapest engine first (FM-004 CA): a QJ5 freighter (31 kT)
  and an LH6 freighter (36 kT, 70 kT hold), 36 ly at warp 6 (factors 180
  and 105). With 70 kT: all on the LH6 freighter,
  `trunc(105·36·106/2000) + trunc(180·36·31/2000) = 200 + 100` → 30 mg.
  With 100 kT: 70 on the LH6, 30 on the QJ5,
  `200 + trunc(180·36·61/2000) = 200 + 197` → 40 mg.
- A warp-9 scout chasing a fleet that ends 55 ly away:
  `trunc(900·55·18/2000) = 445` tenths → 45 mg (FM-001 67).

### Not enough fuel (CONFIRMED, FM-001..004)

- Range on the current fuel: `R = trunc(fuel·1000 / C1000)` where `C1000 =
  trunc(Σ_designs trunc(f(w)·1000·(n·m + cargo)/2000) / 10)` (the cost of
  1000 ly in mg, truncated, not rounded up; above 100,000 the game uses
  `trunc(fuel / trunc(C1000/1000))`; `C1000 = 0` means unlimited). A fleet with enough fuel for
  the whole leg uses `max(R, w²)` instead.
- If the allowed distance exceeds `R`, the fleet moves exactly `R` (placed
  by rule 3 above) and its fuel becomes 0. Otherwise it pays the cost of
  the distance it moves, never going below 0.
- **Running dry.** After paying, the fleet has run dry when all of these
  hold: its fuel is 0; it was limited by `R` or paid a non-zero cost; it
  could not afford the whole leg at the start of the year; and it does not
  reach its destination this year (`A + 0.99999 ≤ D`), or `R = 0`. Paying
  the full cost of this year's move does not prevent it (FM-002 24 below).
  A fleet that has run dry gets the out-of-fuel message, gains no ram-scoop
  fuel this year, and the warp of its leg is lowered
  to the fastest warp at which the whole leg would cost no fuel (the
  lowest warp with a non-zero cost, minus one). CONFIRMED for QJ5, where
  this is warp 1; Fuel Mizer → 4, Settler's Delight → 6, Radiating
  Hydro-Ram Scoop → 6 (FM-004 WD). "Cost" is the rounded fleet cost of
  the whole remaining leg, so a short leg can give a higher warp: a Fuel
  Mizer scout with 0 mg and a 2 ly leg gets warp 5, because 2 ly at warp 5
  costs `trunc((trunc(35·2·20/2000) + 9)/10) = 0` mg. BINARY-ONLY: no
  free warp at all → the warp is left unchanged (a different message);
  every J-RC3 engine is free at warp 1, so this should not arise.
- A fleet with `R = 0` does not move.
- With exactly enough fuel for this year's move it moves the full
  distance, and it has still run dry if that leaves 0 and the destination
  is further away. A fleet that arrives with exactly enough fuel has not.
- A fleet that cannot afford the whole leg but keeps some fuel after this
  year's move has not run dry: it keeps its warp (BINARY-ONLY; no corpus
  case).
- Top-up (CONFIRMED, FM-004 TU): a fleet that had enough fuel for the whole
  leg at the start of the year ends the year with at least the fuel the
  rest of the leg needs (capped at its tank; the cap was not exercised), so
  per-year rounding never strands it.

Vectors (CONFIRMED, FM-001, QJ5 scout at warp 6 heading +160 x; fuel →
distance moved, end fuel 0, warp set to 1): fuel 1 → 6 ly, 3 → 18, 5 → 30,
fuel 0 → no move. At warp 9, fuel 10 → 12 ly.

Running dry while paying in full (CONFIRMED, FM-002, QJ5 scout, 18 kT,
warp 6, `C1000 = 162`):

| Fleet | Leg | Fuel | `R` | Moves | Pays | End fuel | Warp after | Event |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 24 | +100 x | 6 | 37 | 36 | 6 | 0 | 1 | out of fuel |
| 29 | +5 x | 1 | 6 | 5 (arrives) | 1 | 0 | 6 | completed orders only |

Fleet 24 is not limited by `R` (37 ≥ 36) and pays exactly its fuel
(`trunc(180·36·18/2000) = 58` tenths → 6 mg), but it needed 17 mg for the
100 ly leg and stops 64 ly short, so it has run dry.

Vectors (CONFIRMED, FM-004 LR, each heading +100 x, ends with 0 mg; these
are the cases where `R` and `trunc(fuel·20000/M)` differ by 1 ly):

| Fleet | Warp | Fuel | `C1000` | Moves | Warp after |
|---|---:|---:|---:|---:|---:|
| LH6 scout (23 kT) | 6 | 3 | 120 | 25 | 1 |
| DLL7 scout (27 kT) | 7 | 4 | 148 | 27 | 1 |
| LH6 scout | 8 | 25 | 862 | 29 | 1 |
| 3 AD8 scouts (93 kT) | 8 | 31 | 534 | 58 | 1 |
| LH6 freighter (36 kT) + 10 kT | 6 | 7 | 241 | 29 | 1 |
| Settler's Delight scout (16 kT) | 10 | 23 | 460 | 50 | 6 |

Worked (first row): `C1000 = trunc(trunc(105·1000·23/2000)/10) =
trunc(1207/10) = 120`; `R = trunc(3·1000/120) = 25` (the corpus formula
gives `trunc(3·20000/2415) = 24`).

Top-up vectors (CONFIRMED, FM-004 TU, QJ5 scout, warp 9, leg 126 ly):
fuel 102 → moves 81, pays 66, has 36, topped up to 37 (the remaining 45 ly
cost 37); fuel 101 → cannot afford the whole leg (103), no top-up, ends
with 35.

### Ram scoops and free warps

A moving fleet that did not run dry and was not stopped by a minefield
gains fuel when its engines are free at the ordered warp:
`gain = Σ_designs n·k·L'`, where `L'` = `min(trunc(D − 0.99999), A)` and,
for a design whose engine (first slot) has `f(w) = 0`, `k` = engines per
ship `e` × (1, or 3 if also free at `w+1`, 6 if free at `w+1` and `w+2`, 10
if free through `w+3`); capped at the tank's free space.
CONFIRMED (FM-002..004): warp 1 on every engine, Fuel Mizer at warps 1–4,
Settler's Delight at 1–6, Radiating Hydro-Ram Scoop at 4 and 6, several
ships of one design, a mixed fleet (only the free design gains), the tank
cap, and arrival years. Not exercised: designs with more than one engine
(`e > 1`), an engine outside the first slot, minefield stops.

Note that `L'` is `trunc(D − 0.99999)`, not `D`, on arrival: a Settler's
Delight scout arriving 10 ly away at warp 4 gains `6·9 = 54`; at
(+7, +7) (`D = 9.90`) it gains `6·8 = 48`.

Vectors (CONFIRMED, FM-004 RS, one scout, 100 mg, heading +100 x, gain):

| Engine | w1 | w2 | w3 | w4 | w5 | w6 | w7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fuel Mizer (free to 4) | 10 | 24 | 27 | 16 | 0 | | |
| Settler's Delight (free to 6) | 10 | 40 | 90 | 96 | 75 | 36 | 0 |
| Radiating Hydro-Ram (free to 6) | | | | 96 | | 36 | |

Three Fuel Mizer scouts at warp 2 gain 72; a QJ5 scout with a Fuel Mizer
scout at warp 2 gains 24. A Settler's Delight scout with 250 mg of 300 at
warp 3 gains 50 (raw 90, capped).

### Chasing another fleet (CONFIRMED, FM-001..003)

1. Fleets move in id order. Fleets whose destination is another fleet are
   deferred until every ordinary fleet has moved.
2. Deferred fleets then move in rounds (at most 10), in id order. A chaser
   has `rem = w²` and `moved = 0` at the start of the year. In a round, its
   step is `rem` if its target has already finished moving, else
   `min(rem, trunc((rem + moved + 4)/5))` (a fifth of `w²`, rounded up). It
   heads for the target's current position, using the distance, arrival
   and rounding rules above with `A = min(trunc(D + 0.9999), step)`.
3. A chaser that arrives on its target has finished. If that target is
   itself a chaser that has not finished, the target stops for the year
   (its waypoint is then settled by rule 8 below).
4. Otherwise `moved += step`, `rem −= step`, and it stays deferred while
   `rem > 0`.
5. Fuel is charged on the year's total distance (`moved + step`), refunding
   the previous round's charge, so rounds add no extra rounding.
6. BINARY-ONLY (FM-001..003 chasers all had full tanks): each round applies
   the ordinary fuel rules to the step, with `R` reduced by `moved` and
   "the whole leg" meaning the distance to the target's current position.
   A chaser limited by `R` moves only that far and ends with 0; a chaser
   that runs dry has its warp lowered as above and stops for the year; a
   chaser that could afford the whole leg is topped up after each round;
   ram-scoop fuel is gained per round on that round's step.

After every fleet has moved, waypoints are settled (CONFIRMED, FM-001..003):

7. Every waypoint whose destination is a fleet takes that fleet's position
   at the end of movement.
8. Every fleet whose position equals its next waypoint exactly completes
   that waypoint ("completed orders" when it was the last one). This
   applies to a fleet that has used its movement or never moved.

So when a chaser lands on a fleet that is chasing it, both complete their
waypoints. A fleet that is caught while heading somewhere else keeps its
orders, and a chaser that did not reach its target keeps chasing, its
waypoint now at the target's end-of-year position.

Vectors (CONFIRMED): two fleets 20 ly apart chasing each other at warp 4:
the lower id moves 12, the higher 8. A at 1200 chasing B at 1215 (warp 9),
B chasing Z at 1225 (warp 9), Z moving +60 at warp 5: with ids in order
A < B < Z, A reaches 1215 and B does not move; with B < A < Z, all three
end at 1250.

Waypoint vectors (CONFIRMED; ids in order, start → end, waypoints left
after the year):

| Case | Lower id | Higher id | Result |
|---|---|---|---|
| FM-001 71/72, mutual chase, warp 4 | 1200 → 1212 | 1220 → 1212 | both complete |
| FM-002 39/40, mutual chase, warps 4 and 3 | 1150 → 1164 | 1170 → 1164 | both complete |
| FM-003 29/30, mutual chase, warps 4 and 1 | 1150 → 1159 | 1160 → 1159 | both complete |
| FM-003 21/22, mutual chase, warp 1, gap 6 | 1150 → 1151 | 1156 → 1155 | neither; waypoints now 1155 and 1151 |
| FM-003 0–2, A chases B, B chases Z, Z +60 | A 1200 → 1215 | B stays 1215 | A completes; B keeps chasing Z, waypoint 1250 |
| FM-002 41/42, C3 chases T3 head-on | T3 1080 → 1055 | C3 1040 → 1055 | C3 completes; T3 keeps its own waypoint |

### Refuelling at a starbase (CONFIRMED, FM-004 DK)

After production, a fleet orbiting a planet with its own starbase (one
with a dock) is set to its tank capacity, including a fleet that arrived
there this year. Fuel above capacity is reduced to capacity there, but not
in deep space (a scout holding 400 mg of 300 keeps 400 away from a
starbase). A fleet that leaves the planet this year is not refuelled, nor
is one at a planet without a starbase.

### Other movement rules (BINARY-ONLY)

- A fleet whose current task is "transport" or "lay mines" does not move.
- Warp 10 with an engine not rated for warp 10 (rated: Interspace-10,
  Enigma Pulsar, Trans-Star 10, Trans-Galactic Mizer Scoop, Galaxy Scoop):
  each ship is destroyed with probability 1/10 each year it moves.
- Cheap Engines: at warp 7 or more, a 1 in 10 chance each year that the
  fleet does not move.
- Improved Fuel Efficiency: engine factor `f − trunc(15f/100)`.
- Alternate Reality fleets carrying more than 10 kT of colonists lose
  `trunc((colonists + 11)·3/100)` kT each year they move.
- Radiating Hydro-Ram Scoop engines kill
  `max(1, trunc(colonists·trunc((86 − mid)/2)/100))` kT of carried
  colonists (at most all of them) per year moved, where `mid` =
  `trunc((radiation low + radiation high)/2)`; not for radiation-immune
  races or when low + high ≥ 170.
- Fuel generators (anti-matter) add 50 mg each and fuel transports 200 mg
  each per year, capped at the tank.
- Refuelling at a friend's starbase, and at a starbase without a dock.
- Fuel unloaded onto a planet is lost.

## Open experiments

None for this specification. The three earlier items (Auto Alchemy before
a multi-count item, zero maximum population, cost modifiers) were settled
by KX-001; see the rules above and `PARITY.md`.

## Sources

- Oracle: PG-001..003, PQ-001 and KX-001 (`PARITY.md`); FM-001..004 movement
  corpus (`PARITY.md`, "Fleet Movement", and `experiments/fm00N/`).
- White-box readings: private `stars-decomp` (population, economy,
  research, mining, production, movement and fuel notes; model checks that
  reproduce the PG, PQ and FM observations listed above).
