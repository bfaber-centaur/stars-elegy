# T15 prediction: the yearly design check against the owner's tech

Pre-run record. It is written and pushed before any run of these starts,
and it is never edited after the runs. The question comes from the
review of lane A's T-37 work: Elegy's ASSUMPTION T15 says that

- (a) the year's design check uses the owner's tech from before the
  year's research, so a part that becomes in-tech through the year's
  level-up is still removed that year; and
- (b) a design received with a fleet transfer is checked against the
  recipient's tech.

What is already known (`TAKEOVER.md` "Design parts dropped when the year
is generated"; PARITY "Design parts dropped" and T-37): parts the owner
lacks the tech for are removed when the year is generated (bombs at tech
3; LBU-17 and LBU-32 at electronics 7; a scanner in SC-021). Every part
measured so far was gated by weapons, electronics or construction, or
by several fields, never by energy alone. No run had a level-up in the
gating field, and none had a design received by transfer. The transfer
task is the last task of the year (`TAKEOVER.md` "Other waypoint
tasks", FO-04).

## Starts

`gen.py` writes three Combat Lab specs. They differ only in player 0's
stored energy research.

- Two JOAT players, neutral to each other, research 0%.
- Player 0: energy 9, every other field 26, current field energy.
  Planet 17 (its homeworld) has no queue, so all of its resources go to
  research. Energy 9 → 10 costs 3770 + 10 × 139 = 5160.
- Player 1: electronics 3, every other field 26.
- Player 0's designs, one ship each, in deep space:

| Slot | Design | Part and its tech | Fleet |
|---|---|---|---|
| 0 | Bear Scout | Bear Neutrino Barrier, energy 10 | 0/0 |
| 1 | Gorilla Scout | Gorilla Delagator, energy 14 | 0/1 |
| 2 | Wolverine Scout | Wolverine Diffuse Shield, energy 6 | 0/2 |
| 3 | Possum Scout | Possum Scanner, electronics 5 | 0/3 (transfer to player 1), 0/5 (kept) |
| 4 | Rhino Scout | Rhino Scanner, electronics 1 | 0/4 (transfer to player 1) |

Fleets 0/3 and 0/4 have the Transfer Fleet task (to player 1) at
waypoint 0. None of these parts is a Mystery Trader or race-only part.

| Start | Player 0's stored energy research | Energy after the year |
|---|---|---|
| `t15-ctl` | 0 | 9 (no level) |
| `t15-pre` | 5160: enough when the year starts, so it levels at the first level-up check | 10 |
| `t15-up` | 5159: one short, so it levels with this year's research | 10 |

If energy does not end at those values, DC-1 is not read for that start.

Hashes (sha256) of the specs, `gen.py` and the built `.HST` starts are
in the private apparatus, `evidence/t15/SHA256SUMS.pre`.

Runs: two chained years (`tools/fleetlab/years`, step 1000) per start,
at cycles 20000, 30000 and 14000. The check involves no random draw, so
the streams are repeats.

## DC-1: a level-up in the gating field (ASSUMPTION T15 (a))

Bear Scout's barrier needs energy 10, and player 0 starts the year at 9.

| Reading | `t15-ctl` | `t15-pre` | `t15-up` |
|---|---|---|---|
| **H-before (predicted, T15 (a))**: the check uses the tech from before any of the year's research | removed | removed | removed |
| H-mid: the check runs after the first level-up check and before production | removed | kept | removed |
| H-after: the check uses the tech at the end of the year | removed | kept | kept |

"Removed" means that after year 1 the stored design has the slot empty.

## DC-2: a design received with a fleet transfer (ASSUMPTION T15 (b))

Player 1 receives a fleet of a copied Possum Scout design (electronics 5,
above its 3) and one of a copied Rhino Scout design (electronics 1).

Predicted, reading T15 (b) with the check placed as in (a), which runs
before the transfer:
- After year 1, player 1's copy of Possum Scout still has the Possum
  Scanner.
- After year 2, player 1's copy has the scanner slot empty.
- The Rhino copy keeps its scanner in both years.
- Player 0's own Possum Scout (slot 3, fleet 0/5) keeps its scanner in
  both years.

Other readings:
- H-copy: the scanner is dropped when the design is copied, or later in
  year 1, so it is gone after year 1.
- H-never: a received design is never checked, so the scanner is still
  there after year 2.

If player 1's electronics reaches 5 by the end of year 2, DC-2's year-2
reading is void.

## DC-3: an energy-gated part (energy above the owner's level)

| Design | `t15-ctl`, `t15-pre`, `t15-up` after year 1 |
|---|---|
| Gorilla Scout (energy 14, owner at 9 or 10) | removed (predicted) |
| Wolverine Scout (energy 6) | kept (predicted) |

## What is recorded

- Every design of both players after each year: hull, slots and mass.
- Both players' tech and stored research after each year.
- The fleets after each year, including player 1's received fleets and
  the design slots they point to.
- Both players' messages.
