# RG-005: an out-of-sample validation game, 12 chained years

RG-005 is for validation, not development. Its configuration, method,
acceptance criteria and predictions are in `PREDICTION.md`, the pre-run
record. That record was pushed alone in 1019fa7 at 2026-10-14T02:19:31Z
(activity API), and the oracle run started at 02:19:47Z (apparatus
`evidence/rg005/started`). The engine under test is elegy 8584f92, run
unchanged. This file records how the game was generated. It holds no
comparison result: lane B runs the first comparison and records it as
found.

**This is not a game recorded from its start.** As in RG-004, the game
was created at 2400 and generated unrecorded (no orders captured,
nothing checked) up to the chain's start.

Vector: `vectors/rg/rg005.json` (12 chained years, 2466 to 2477) and
`rg005-y1` to `rg005-y12` (each year alone, from the original's files
for the year before). Raw evidence: private apparatus `evidence/rg005`.
The race files, the definition and the warm-up files stay there.

## What ran, against the record

- **Game and setup step:** as recorded. The original created RG5
  (MEASURED: 288 planets, game options public scores on, slower tech
  off, random events on in `initial_state`). The setup step is a state
  edit: each player's computer-player byte (expert; Turindrone,
  Automitron, Macinti, Rototill, Cybertron for players 0 to 4) and
  every pair at enemy. Nothing else was edited, and no player gave
  client orders.
- **Warm-up and W:** 70 years at cycles 20000 + 1000·(k−1). Distinct
  battle ids per year (apparatus `pick-w.txt`, MEASURED): 0 in years 1
  to 45, 1 in year 46, 0 in years 47 to 64, 2 in year 65. By the rule
  (first year from 45 on with at least 2), W = 65. The chain starts from
  the state after 2465.
- **Chain:** RG-004's `rg-chain` at cycles 20000. In each year the
  computer players planned from the current files, and the year was
  generated with every player's order file supplied, so the host ran no
  computer player and the stream started at seeding. Each year was
  generated twice; all 12 repeats were byte-identical (MEASURED). Every
  year was also generated at cycles 3700 and 1490 from the same files
  and orders, to flag samples.
- **Length:** the 6 years plus their alternative streams took 1,576 s
  from the run's start, warm-up included. The extension to 12 years was
  decided on that cost alone at 02:46:03Z, before any comparison
  (apparatus `extend.txt`).

## Chain length against the record

`PREDICTION.md` (Method, step 3) says: "Chain: `rg-chain` (RG-004's),
6 years at cycles 20000, then `rg-alt` at 3700 and 1490. Extended to
12 years the same way only if cost allows, decided before any
comparison is run."

So the record allowed the extension to 12 years, on two conditions:
cost, and a decision before any comparison. The decision was recorded
at 02:46:03Z, before any comparison was run. But the record set no
threshold for "cost allows", so whether to extend was lane F's
judgement, not a rule fixed in advance. To keep that judgement out of
the scoring, only years 1 to 6 (2466 to 2471: restarts y1 to y6 and
chained year 1) can support CONFIRMED by prediction. Results from years
7 to 12 (2472 to 2477, restarts y7 to y12, and those chained years)
support MEASURED only, whatever they show. So lane B's first-run
tallies are reported in two parts: restarts y1 to y6 with chained year
1, and restarts y7 to y12.

## Why the same years as RG-004

RG-004 also covers 2466 to 2477. For RG-005 that is the output of the
warm-up rule, not a choice: the game starts at 2400, and the rule
(first warm-up year from 45 on with at least 2 battle records, or 70)
gave W = 65 (`pick-w.txt` above). RG-004's 65 warm-up years were not
picked by that rule; they were set in its own run (40 years, then 25
more; `experiments/rg004/README.md`). The identical years are a
coincidence.

RG-005 shares no game file or state with RG-004 (apparatus, checked
2026-10-14 by comparing the two `SHA256SUMS`). RG5 was created new
from its own definition (name RG5, seed 5005, medium universe), unlike
RG-004's RGF (seed 4004, small universe), with five race files that
are not RG-004's. Every year after that was generated from RG5's own
files. Of the 4,557 hashed RG-005 files, only two contents also occur
in RG-004, and neither is game state: the empty file (the `done`
markers and the empty planning captures) and the `repeat.txt` text
"repeat identical". The two runs do share the `rg-chain` and `rg-alt`
scripts, as the record says.

## Messages

All 60 message sequences in the vector are empty, and the vector has no
`message` expectations. That is what the original wrote, not a capture
gap (MEASURED, 2026-10-14): a scan of the raw block headers of every
RG-005 player file (`RG5.M1` to `RG5.M5`, 12 years: 60 files in the
recorded stream and 120 in the 3700 and 1490 streams) found no message
block (type 12), and every file parsed to its end. The same scan finds 8
message blocks in RG-004's 84 recorded player files, and the dump the
vector build uses decodes them. In RG-005, player 2 (AR) lost 14
planets to no owner over the 12 years and got no message for them in
its file. Why computer players' files carry so few messages is not
explained here.

## Counts

All MEASURED from the recorded files.

| | |
|---|---|
| Players | 5 (CA, SS, AR, WM, SD), all expert computer players |
| Planets | 288 |
| Fleets at the start | 107 |
| Orders | 1,050 in 60 order sets: production queues 426, waypoint changes 154, waypoint adds 140, designs 80, design deletions 80, cargo 60, research 54, planet settings 29, ship moves between fleets 27 |
| Expectations (chained run) | 2,749, 270 of them `sample: true` |
| Battle records (chained run) | 18; none `start_sample`; no `alt_battle` |
| Battle records (chained run and restarts) | 36 |

## Building

`python3 tools/vectors/build.py rg005 <dir named rg005> vectors/rg`, with
the directory a link to apparatus `evidence/rg005/run`
(`vectors/README.md`). The message expectations rebuild only with a
local `stars.exe`.

For elegy's ledger (`engine/testdata/vectors/README.md` "Adding a
representative game"), the header counts are `# restarts: 12` and
`# battle records: 36`.
