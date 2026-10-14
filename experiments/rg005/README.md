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
