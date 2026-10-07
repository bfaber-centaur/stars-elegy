# Race design specification: points, legality and random races

Behavioral specification of how J-RC3 scores a race design, which designs
are legal, how malformed or illegal races are handled when a game is
created and while it runs, and how the wizard's Random race is generated.
It is written for an implementer working only from this public repository
and describes what happens, not how any file encodes it.

`PARITY.md`, section "Race design", holds the experiment records (RD-1 to
RD-6 new games, RD-P1 to RD-P10 penalty years; case tables in
`experiments/rd/`). This file restates them as rules and adds rules that so
far come only from white-box analysis of the original program (private
`stars-decomp`, promoted here as behavior only).

Rules this file relies on but does not restate: habitability (`KERNEL.md`
"Habitability"), and what a race's leftover points buy at game creation
(`UNIVERSE.md` "Leftover advantage points").

## Status of each rule

- **CONFIRMED**: a white-box reading agrees with original-game oracle
  observations. The RD games were compared with a whole predicted game,
  field by field, including each player's race and name; all matched.
- **MEASURED**: observed, but in one case only or without a full model
  check.
- **BINARY-ONLY**: read from the original program, with no oracle
  observation yet. Listed again under Open experiments.
- **LEGACY BUG**: looks like an accident of the original implementation.
  Implement it for parity, isolated so it can be switched off.

## Conventions

- Integer arithmetic; divisions truncate toward zero. `|x|` is absolute
  value.
- Habitat values are on the 0–100 scale of `KERNEL.md`. Axes in order
  gravity, temperature, radiation.

## Race settings (CONFIRMED, RD-1..RD-7)

| Setting | Range | Default race |
|---|---|---|
| primary racial trait (PRT) | HE, SS, WM, CA, IS, SD, PP, IT, AR, JOAT | JOAT |
| lesser racial traits (LRTs) | any subset of IFE, TT, ARM, ISB, GR, UR, MA, NRSE, CE, OBRM, NAS, LSP, BET, RS | none |
| habitat per axis | `lo..hi` with centre `c = lo + (hi − lo)/2`, or immune | 15–85, centre 50 |
| maximum growth `g` | 1–20 % | 15 |
| colonists per resource | 700–2500, in steps of 100 (stored as 7–25) | 1000 |
| factory output (per 10 factories) | 5–15 | 10 |
| factory cost | 5–25 | 10 |
| factories operated (per 10,000 colonists) | 5–25 | 10 |
| mine output (per 10 mines) | 5–25 | 10 |
| mine cost | 2–15 | 5 |
| mines operated (per 10,000 colonists) | 5–25 | 10 |
| leftover-points spend | 0–4 in the wizard (0–6 accepted) | 0 |
| research cost per field (energy, weapons, propulsion, construction, electronics, biotech) | costs 75% extra / normal / costs 50% less | normal |
| expensive fields start at tech 3 | on/off | off |
| factories cost one less germanium | on/off | off |

In the race files and in the oracle records (the `lrt=` words in
`PARITY.md` "Race design"), these traits share one 32-bit word: bits 0–13
are the LRTs in the order listed above (IFE = bit 0 … RS = bit 13), bit 29
is "expensive fields start at tech 3", bit 30 marks the wizard's Random
race template, and bit 31 is "factories cost one less germanium". So
`a000006d` is IFE, ARM, ISB, UR, MA, bit 29 and bit 31.

The default race is the wizard's Humanoid race. It scores 25 points.

Below, `col` is colonists per resource / 100, `fo` factory output, `fc`
factory cost, `fn` factories operated, `mo` mine output, `mc` mine cost,
`mn` mines operated, and `r_f` the research setting of field `f`: 0 for
75% extra, 1 normal, 2 for 50% less.

## Advantage points (CONFIRMED)

The wizard shows a race's **advantage points**. A race is legal when its
points are at least 0. The leftover the race takes into a game is
`min(50, points)`.

CONFIRMED by RD-1..RD-4 (48 legal races with predicted points 1..50, each
seen through its leftover; boundaries 0, 50, 51) and RD-4..RD-6 (14
generated Random races, all scored exactly). The races covered every
growth-table row from 3 to 20, one to three immunities, a 0–20 axis, the
factory and mine settings, colonists per resource from 700 to 2500, AR, NAS
with PP, SS and JOAT, LRT sets, every research setting and every PRT.

Compute `P` as follows, then the result is `P/3`.

### 1. Repairs first

The race is first repaired as in "Repairs" below. The points are those of
the repaired race.

### 2. Habitability integral `H`

`H` measures how much of the galaxy the race can live on, with and without
terraforming. It is summed over three passes `k = 0, 1, 2` with an
allowance `t`: 0; then 5 (8 with TT); then 15 (17 with TT). Each pass has a
weight: 7, 5, 6.

For each pass and each axis:

- an immune axis uses the single value 50, and its scale factor is 11;
- otherwise `low = max(0, lo − t)`, `top = min(100, hi + t)`,
  `width = top − low`, and the axis uses 11 test values
  `x_i = low + width·i/10` for `i = 0..10` (the first is `low`). Its scale
  factor is `width/100`.

In passes 1 and 2 each test value of a non-immune axis is moved toward the
race's centre: with `δ = c − x`, `δ' = 0` if `|δ| ≤ t`, else `δ` shortened
by `t` toward 0; the value used is `c − δ'`.

For every combination of test values (one per axis), take the planet value
`h` of that environment for this race (`KERNEL.md` "Habitability"). In
passes 1 and 2, if `δ'_grav + δ'_temp + δ'_rad > t` (signed sum), then
`h = max(0, h − (sum − t))`. Add `weight·h²`.

Scaling, innermost axis first: the radiation sum of each (gravity,
temperature) cell is scaled by its factor as an integer (`·width/100`,
truncated; `·11` when immune). The temperature and gravity scalings are
done in floating point (`·width·0.01`, or `·11.0` when immune). After all
three passes, `H = trunc(total·0.1 + 0.5)`.

### 3. Growth

`hab = H / 2000`. With `g` the growth (after repairs):

| `g` | base | mult |
|---|---|---|
| 1–5 | `(6 − g)·4200 + 1650` | `g` |
| 6 | 5250 | `2g − 5` |
| 7 | 3900 | `2g − 5` |
| 8 | 2250 | `2g − 5` |
| 9 | 1875 | `2g − 5` |
| 10–13 | 1650 | `2g − 5` |
| 14–19 | 1650 | `(g − 6)·3` |
| 20 | 1650 | 45 |

`P = base − mult·hab/24`.

### 4. Habitat shape

- Each non-immune axis: `P += 4·|c − 50|`.
- Two or three immune axes: `P −= 150`.
- If `fn > 10` or `fo > 10`: `a = max(1, fn − 9)`,
  `b = max(1, fo − 9)·(3 for HE, else 2)`. With fewer than two immune axes
  `P += (a·b·g)/(−9)`; otherwise `P −= (a·b·g)/2`.

### 5. Colonists per resource

`col` (at most 25): below 8, −2400; 8, −1260; 9, −600; 10, 0; above 10,
`+120·(col − 10)`.

### 6. Economy

AR: `P += 210`, and nothing else in this step applies (AR's factory, mine
and germanium settings do not count).

Otherwise:

- Factories: `E = (fo − 10)·(−121 if fo ≥ 10, else −100)`;
  `E += 55·(fc − 10)` if `fc > 10`, else `−60·(10 − fc)²`;
  with `n = 10 − fn`, `E += n·(35 if n ≤ 0, else 40)`.
  If `E > 700`, `E = (E − 700)/3 + 700`.
  Then if `n < −6`: `n < −14` gives `E −= 360`; `n < −11` gives
  `E += (n + 7)·45`; otherwise `E += (n + 6)·30`.
  If `fo > 12`: `E += (12 − fo)·60`.
  `P += E`.
- Factories cost one less germanium: `P −= 175`.
- Mines: `(mo − 10)·(−169 if mo ≥ 10, else −100)`; plus
  `(mc − 3)·65 + 80` if `mc ≥ 3`, else −360; plus `n·(35 if n ≤ 0, else 40)`
  with `n = 10 − mn`.

### 7. Traits

- PRT cost, subtracted: HE 40, SS 95, WM 45, CA 10, IS −100, SD −150, PP
  120, IT 180, AR 90, JOAT −66.
- Each LRT taken adds: IFE −235, TT −25, ARM −159, ISB −201, GR 40, UR −240,
  MA −155, NRSE 160, CE 240, OBRM 255, NAS 325, LSP 180, BET 70, RS 30. Call
  the negative ones "good" (they cost points) and the positive ones "bad".
- With `n` LRTs: `n > 4` gives `−10·n·(n − 4)`. With `d = bad − good`:
  `d > 3` gives `−60·(d − 3)`. With `d = good − bad`: `d > 3` gives
  `−40·(d − 3)`.
- NAS with PP: −280; with SS: −200; with JOAT: −40.

### 8. Research

`s = Σ (r_f − 1)` over the six fields (−6..6).

- `s < 0`: add 150, 330, 540, 780, 1050, 1380 for `s` = −1..−6; then −190
  more if `s < −4` and `col < 10`.
- `s > 0`: `−130·s²`, then +520 if `s = 5`, +1430 if `s = 6`.
- Expensive fields start at tech 3: −180.
- AR with energy at "costs 50% less": −100.

Finally `points = P/3`.

**StarsAPI.** StarsAPI's race calculator (used by `tools/fleetlab/racelab`)
agrees except that it truncates the step-4 factory term in floating point
after subtracting, which leaves it one point lower on about one race in six
(11 of the RD races; the original agreed with the rule above). It also
disagrees on a growth-0 race. Elegy should implement the rule above.

## Repairs (CONFIRMED in part)

Before scoring, the original repairs malformed fields. Each repair marks
the race as **tampered**, a per-race flag that is visible in the game files:

- Habitat, per axis. Only the low decides immunity: a low equal to the
  immune marker (the byte 255, read as −1) makes the whole axis immune, and
  a centre or high that is not also the marker is set to it (a repair).
  Any other low is a number: `lo` is clamped to 0..100, `hi` to
  `lo..100` (a high below the low becomes the low), and the centre is
  forced to `lo + (hi − lo)/2`. A value outside 0..100 is therefore
  clamped, never turned into immunity (CONFIRMED: a centre one off was
  moved back, RD-4; RD-P4; a low of −5 became 0, RD-P8; the immune-marker
  case and `hi > 100` are BINARY-ONLY). Settings are stored as signed
  bytes, so a stored 200 reads as −56 and clamps to the low end.
- Growth above 20 becomes 20 (BINARY-ONLY). Growth below 1 becomes **1**
  (CONFIRMED for growth 0, RD-4).
- Every other setting is clamped to its range in the table above: a value
  below the range becomes the minimum, one above it the maximum. For a
  research field that means below "costs 75% extra" stays "costs 75%
  extra" and above "costs 50% less" becomes "costs 50% less"; a PRT above
  JOAT becomes JOAT (RD-P7). Colonists per resource are stored in hundreds
  (7–25), so a value that is not a multiple of 100 cannot occur in the
  original. Race stat 15, an unused field, must be 0 (CONFIRMED at
  creation, RD-4).

## At game creation (CONFIRMED)

For each player's race file:

1. **Corrupt files are refused.** A race file whose checksum does not match
   stops game creation with "The game file X appears to be corrupt"
   (MEASURED, three files in RD-4).
2. **Repairs** apply as above. A repaired race is kept, with the tampered
   flag (RD-4: centre, stat 15, growth 0).
3. **Illegal human races are replaced.** A human race with points < 0
   becomes the default race (JOAT, growth 15, 15–85 on every axis, standard
   economy and research, no LRTs), marked tampered, and is given a random
   computer-player name (RD-4: −1 and −1433 points). Its leftover is then 25.
4. **Computer players are not checked.** Built-in computer races keep their
   settings whatever they score (RD-4 and RD-5 had computer races worth 963,
   −75 and −173 points).
5. Leftover `L = min(50, points)`; spends 5 and 6 act as spend 0 (surface
   minerals) (RD-4).
6. Random races are generated (below) when the players are given their
   homeworlds, after homeworld placement.

## In a running game (CONFIRMED, RD-P1..RD-P10)

Every year, before fleets move, each player's race is checked:

1. **Silent clamps.** Every race setting is clamped to its range with no
   message and no flag (RD-P5: stat 15 = 1 → 0; RD-P6: colonists per
   resource 2600 → 2500; RD-P7: PRT out of range → JOAT). The research
   share outside 0–100% becomes 15%; growth below 0 becomes 1, above 20
   becomes 20 (BINARY-ONLY).
2. **Check.** The race is scored. For a human player, the race is
   **punished** if its points are negative, or if the scoring repairs
   something (by now only the habitat, or growth 0) that newly sets the
   tampered flag (RD-P1..P4, P8, P10). A race at exactly 0 is left alone
   (RD-P9). Growth 0 reaching this check is punished: growth becomes 1,
   the race is marked tampered and the player gets the penalty message
   (CONFIRMED, RD-P11).
3. **Penalty.** The player gets message "Your race definition has been
   tampered with…", and every other player a "Hacked race discovered…"
   message (CONFIRMED, RD-P12, a six-player game: all four other human players
   got it; whether a computer player is told is not observable, since its
   player file carries no messages). The race is
   marked tampered. Then:
   - colonists per resource rise by 100 at a time until the race has at
     least 500 points or reaches 2500;
   - then growth falls by 1 at a time until at least 500 points or growth 1;
   - then research fields are set to "costs 75% extra" one at a time, in
     field order, until more than 499 points (BINARY-ONLY; this step looks
     unreachable, since growth 1 alone is worth thousands of points).

   Observed: −444 points → colonists 2500, growth 7 (1042); −2092 → 2500,
   growth 4; −3667 → 2500, growth 3; −1 → 2500, growth 9 (559); a centre
   of 51 → centre 50, colonists 1700 (525).
4. A race already marked tampered is punished again only while its points
   are negative or a new repair is needed (BINARY-ONLY; follows from step 2).
5. **Computer players** get steps 1 and 2 without the penalty: the silent
   clamps, then the scoring repairs (habitat, growth 0 → 1), which do set
   the tampered flag, but no message and no change to colonists, growth or
   research, whatever the points (BINARY-ONLY).

This differs from creation, where stat 15 = 1 marked the race tampered.

Elegy note: the penalty exists to punish hand-edited files. Elegy can keep
it as a compatibility rule, but it needs the rule above only if it accepts
races from outside its own designer.

## Random race (CONFIRMED in outcome, details BINARY-ONLY)

The wizard's Random race is a template: HE, growth 15, 17–83 on every axis,
with a "random" marker. At creation it is replaced by a generated race:

1. **Habitat**, one draw `k = rand(25)`:
   - `k < 4`: all three axes immune; growth `2 + rand(4)`.
   - `k < 7`: all three axes 0–100; growth `3 + rand(4)`.
   - `k < 9`: gravity and temperature each 0–100 or 17–83 at random
     (radiation always stays 17–83); growth `2 + rand(5)`.
   - otherwise every axis gets an even width `w = 2·(10 + rand(40))` (20–98)
     at `lo = rand(101 − w)`. Then for `k` = 9–11 one random axis becomes
     immune; for 12–13 one random axis becomes 0–100; for 14–16 one random
     axis becomes `lo = rand(81)`, 20 wide; for 17–24 nothing more. Growth
     `7 + rand(9)`.
2. **Research**: with probability 1/3 all fields normal, else each field
   uniformly one of the three settings.
3. **Traits**: PRT uniform over the ten. With probability 1/4 no LRTs, else
   each LRT independently with probability 1/2. Each of the two options
   (expensive fields at tech 3, cheaper germanium) with probability 1/2.
4. **Economy**: with probability 1/3 the default economy and a spend
   uniform in 0–4; otherwise each economy setting and the spend uniform
   over its whole range (so spends 5 and 6 can occur).
5. A race named "Random" gets a random computer-player name; any other
   name is kept (RD-4: "Zorgon").
6. **Adjust to 0..50 points.** Until the race scores 0..50, take one step.
   A step picks one kind of change at random and tries its options in
   order; the first option that brings the points strictly closer to
   0..50 is kept and ends the step, and when none does the race is left as
   it was. Distance is `max(points − 50, −points)`. "Else" below means
   "try this next", never a coin flip: there is exactly one random draw for
   the kind of change and one for which field, trait, setting or axis.
   - 3 in 10: one of the six research fields, uniform. Try one step dearer
     (skipped when already "costs 75% extra"), then one step cheaper
     (skipped when already "costs 50% less").
   - 3 in 10: one of the 14 LRTs, uniform. Try it off, then on. Setting it
     to its current value changes nothing, so this is a toggle kept only if
     it helps.
   - 3 in 10: one of the seven economy settings (colonists per resource,
     factory output, factory cost, factories operated, mine output, mine
     cost, mines operated), uniform. Try one step down, then one step up.
     Each try is clamped to the setting's range, so at a limit the blocked
     direction is a try that changes nothing.
   - 1 in 20: one of the three axes, uniform. An immune axis becomes `lo =
     rand(31)`, `hi = lo + 70`, centre `lo + 35`; any other axis becomes
     immune.
   - 1 in 20: growth one lower (tried only above 1), then one higher (tried
     only below 15).

   After 251 steps without success the race becomes the default race,
   keeping its name.

All 14 generated races in RD-4..RD-6 scored 0..50 (3 to 44). Each matched
the predicted race exactly, so the draw order and the adjust loop above
are confirmed for those cases. Elegy does not need the original's random
stream, only these distributions and the 0..50 target.

## Wizard (BINARY-ONLY)

- Habitat ranges are at least 20 wide. Unchecking "immune" gives 20–80.
- Choosing AR resets the economy to the default (10/10/10, 10/5/10) and
  clears the germanium option, which is disabled for AR.
- The race cannot be saved while its points are negative.
- The wizard offers spends 0–4: surface minerals, concentrations, mines,
  factories, defenses.

## Open experiments

1. A second year after a punished race (predicted: no change).
2. Out-of-range axis values other than a centre (e.g. `hi > 100`) at
   creation and in a running game.
3. The 251-step fallback of the Random race (needs a race that cannot
   reach 0..50).
