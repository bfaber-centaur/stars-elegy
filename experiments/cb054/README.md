# CB-054: does a dropped part leave the design cost from the next year?

`COMBAT.md` "Parts the game drops from a design": when the game reads a
design with a part its hull slot does not take, the part is dropped, but
the cost is computed just before the drop. So in that generation the part
still counts in target choice and salvage (MEASURED, CB-009 K2). The
section adds, without a label or a case, that from the next generation
the cost is computed from the design without the part. This case tests
that second year.

Combat Lab base, deep space at (1020,1230), mutual enemies, tech 26 in
every field for both players (as CB-009, so miniaturization is at its
cap and research cannot change a cost).

- Player 1 (the victims' owner) has two designs:
  - `Hauler`: Small Freighter, Quick Jump 5, nothing else;
  - `Deflector Hauler`: the same with a Beam Deflector in the
    shield-or-armor slot, which the slot does not take (CB-009's design).
- 30 victims in one fleet, plan "Nobody".
- Player 0: 10 Laser Frigates, plan "Max Any".

| case | victims | player 0's frigates |
|---|---|---|
| `cb054-y1-defl` | Deflector Hauler | at the victims: battle in year 1 |
| `cb054-y1-plain` | Hauler | at the victims: battle in year 1 |
| `cb054-y2-defl` | Deflector Hauler | 40 ly away, flying to them at warp 5: battle in year 2 |
| `cb054-y2-plain` | Hauler | 40 ly away, flying to them at warp 5: battle in year 2 |

Each `y2` case runs two years from its start file; year 2 starts from
the original's own year-1 output. Pinned at cycles 20000 and 30000.

## Predictions (committed before the runs)

Cost per ship at tech 26, read from CB-009 K2 (three ships per kill
event): `Deflector Hauler` with the part 4/0/7 (ironium, boranium,
germanium); `Hauler` 4/0/5. Salvage per kill event of `k` ships, per
mineral: `S = trunc(k·c/3)`, then `S − trunc(S/4)` in deep space; the
salvage object holds the sum.

- `cb054-y1-plain` and `cb054-y2-plain`: `c` = 4/0/5. These fix the
  arithmetic for the kill events each battle record shows.
- `cb054-y1-defl`: `c` = 4/0/7, the part still counted (as CB-009).
- `cb054-y2-defl`: **`c` = 4/0/5**, the part no longer counted, so the
  salvage equals the plain case's for the same kill events. The other
  reading, the part still counted in year 2, gives 4/0/7.
- In `y2`, no battle in year 1; the year-1 host file already holds
  `Deflector Hauler` without the Beam Deflector.
- The kill events are random (samples); the salvage given the events is
  not.

## Results

Cycles 20000 and 30000 each gave one battle record per case, the same in
all four cases of a stream: kill events of 7, 8 and 8 Victims at 20000,
and 7, 7 and 7 at 30000.

| case | salvage at 20000 | at 30000 | `c` that fits |
|---|---|---|---|
| `cb054-y1-defl` | 23/0/40 | 21/0/36 | 4/0/7 |
| `cb054-y1-plain` | 23/0/29 | 21/0/27 | 4/0/5 |
| `cb054-y2-defl` | **23/0/29** | **21/0/27** | **4/0/5** |
| `cb054-y2-plain` | 23/0/29 | 21/0/27 | 4/0/5 |

For example at 30000, `c` = 4/0/7 gives per event `trunc(7·7/3)` = 16
germanium, 12 after the quarter lost, 36 for three events; 4/0/5 gives
11, then 9, then 27.

- **CONFIRMED (2 of 2 streams):** the year the game first reads the
  design, the dropped Beam Deflector still counts in the salvage cost; in
  the next year it does not, and the salvage equals the plain design's.
  Every prediction held.
- The `y2` cases had no battle in year 1, and their year-1 host files
  already held `Deflector Hauler` without the part (mass 29).
- Raw evidence: apparatus `evidence/cb054`.
