# Fleet numbering after a fleet leaves during the year (FN-01..FN-05)

Shrinks the RG-001 fleet-numbering mismatch (`docs/PARITY.md`,
"Representative game (RG-001)"). In RG-001 year 3, player 6's fleet 3
colonized at waypoint 0 and was gone after the year, yet the three colony
ships player 6 built that year were numbered 4, 13 and 14, not 3. Fleet 3
was reused in year 4. The ship-launch rule says a new fleet takes the
owner's lowest unused number (SL-02, CONFIRMED), and `KERNEL.md` "Turn
order" runs waypoint-0 colonize (step 2) before production (step 4).

Combat Lab base (game CB), `gen.py OUTDIR`. Player 1 owns fleets 1 and 2
at its homeworld, planet 8, which builds two Scouts (population 1000,
100 factories, 20000 kT of each mineral). Each variant adds a fleet 0
that leaves before production, except the control. Year 2 queues one more
Scout on the year-1 host file (`year2.txt`, `keepfleets`). Pinned at
cycles 20000 and 30000. Raw evidence: stars-oracle-apparatus
`evidence/fn/`.

## Candidate explanations

- **H-defer.** A fleet removed during the year keeps its number in use
  until a cleanup after production, so the year's new fleets skip it.
- **H-now.** The number is free at once, and RG-001's skip has another
  cause.
- **H-colonize.** Only colonizing defers the number (a colonizing fleet is
  marked consumed rather than removed); scrap and merge free it at once.

## Predictions (committed before the runs)

| case | fleet 0 | new fleets in year 1 | year 2's new fleet |
|---|---|---|---|
| FN-01 `fn-ctl` | none | 0 and 3 | 4 |
| FN-02 `fn-colonize` | colonizes unowned planet 5 at waypoint 0 | **3 and 4** | 0 |
| FN-03 `fn-colonize-arrive` | arrives at planet 5 (10 ly) and colonizes | **3 and 4** | 0 |
| FN-04 `fn-scrap` | scrapped at planet 8 at waypoint 0 | open: 3 and 4 (H-defer) or 0 and 3 (H-now, H-colonize) | 0 or 4 |
| FN-05 `fn-merge` | waypoint-0 merge into fleet 1 | open: 3 and 4 (H-defer) or 0 and 3 (H-now, H-colonize) | 0 or 4 |

FN-02 follows RG-001; FN-03 tests a colonize after movement. In every
variant fleet 0 is gone after year 1. FN-01 fixes the baseline: if it does
not give 0 and 3, the setup is wrong and nothing else is read.

## Results

Every variant ran at cycles 20000 and 30000, year 1 and year 2. The two
streams agreed in every number.

| case | fleet 0's fate (player 1's messages) | new fleets in year 1 | year 2's new fleet |
|---|---|---|---|
| FN-01 `fn-ctl` | (none) | 0 and 3 | 4 |
| FN-02 `fn-colonize` | planet 5 colonized (owner 1, 2,400 colonists) | **3 and 4** | **0** |
| FN-03 `fn-colonize-arrive` | moved 10 ly, colonized planet 5 | **3 and 4** | **0** |
| FN-04 `fn-scrap` | scrapped at planet 8 (0x5a) | **3 and 4** | **0** |
| FN-05 `fn-merge` | merged into fleet 1, which holds 2 Scouts (0xf7) | **3 and 4** | **0** |

- **CONFIRMED (FN-02..05, 2 of 2 streams each):** a fleet removed during
  the year before production, by a waypoint-0 colonize, a colonize on
  arrival after movement, a waypoint-0 scrap or a waypoint-0 merge, keeps
  its number in use for that year's production: the year's new fleets
  skip it. The next year's first new fleet takes it.
- FN-01 held, so the setup is sound. FN-02 matches RG-001 year 3.
- The FN-05 merge also sent player 1 message 0x138: fleet 0's only
  waypoint named fleet 1 at its own position and fleet 1 had no orders,
  the co-located idle-leader case `MESSAGES.md` lists for 0x138. The
  merge still happened.
- Not tested: a fleet destroyed in battle (after production), and a
  merge or split order replayed in step 1.
