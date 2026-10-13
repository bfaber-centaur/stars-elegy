# Z-MD: chasers of a fleet that mines destroy during movement

Question, from lane D's chase-target mine-death spec: a fleet's
waypoint 1 is aimed at an enemy fleet T, and a minefield destroys T
during movement, before the chasers move (`KERNEL.md` "Chasing another
fleet", rule 1). Where does the chaser go? RG-003 year 11 fitted R-start
once, in one stream.

- **R-start:** to T's start-of-year position S, the waypoint's
  coordinates from the upkeep before movement.
- **R-death:** to P, where T died.
- **R-stop:** the chaser does not move.

## Pre-run record

The prediction is apparatus `evidence/zmd/PREDICTION.md`, committed in
apparatus bb7940c4 and pushed at 2026-10-13T07:21:15Z (activity API).
The runs started at 07:21:26Z. It has not been edited since. Its SHA256
is `fb973accf65470b0991e68dcd09373bae496c32610ab2620b58eacb7efbd1fd9`,
and its text, verbatim, is:

````markdown
# Z-MD prediction: chasers of a fleet that a minefield stops or destroys

Pre-run record. It is written and pushed before any run of this start,
and it is never edited after the runs. The spec is lane D's
chase-target mine-death spec. RG-003 year 11 (MEASURED once, one stream)
fits R-start and rules out R-death and R-stop for that one record.

## Hypotheses

A chaser's waypoint 1 is aimed at player 1's fleet T. A minefield
destroys T during movement, at P = (x0 + d, y), d ly into its leg.

- **R-start** (predicted): the chaser goes to T's start-of-year
  position S, which is the waypoint's coordinates from the pre-movement
  upkeep.
- **R-death**: the chaser goes to P, where T died.
- **R-stop**: the chaser does not move.

## Start

`zmd.spec`, written by `tools/gen.py` (lane table: `lanes.txt`). Combat
Lab base2400.

- Tech 26 in every field, research 0, mutual enemies.
- Player 0 owns a heavy field of 50,000 mines at (1200,1200). It decays
  to about 25,000, radius 158. The owner's fleets are never stopped
  (MF-6). Every fleet is unarmed, so no battle runs.
- Each lane `i` (y = 1065 + 13i, 20 lanes) has:
  - T, player 1's fleet 2 + i, at S = (1160, y), going east to (1241, y)
    at warp 9 (81 ly, the whole leg inside the field);
  - C-near, player 0's Tank at (1140, y − 20), warp 9, aimed at T;
  - C-far, player 0's Tank at (1160, y ± 60), warp 5 (25 ly), aimed at T:
    −60 for y < 1190, +60 otherwise.
- Every start position and every R-start end point is distinct
  (`gen.py` asserts it).

| Case | Lanes | T | Note |
|---|---|---|---|
| Z-MD-1 | 0–11 | Bare DD (Destroyer, no armor parts: armor 200), dies on any heavy-field hit (2000 minimum) | C-near ids 2, 4, …, 24 |
| Z-MD-2 | 12–17 | Tank (3200 armor), survives a hit at P | control |
| Z-MD-3 | 18–19 | Bare DD | C-near is player 0's fleet 0 or 1, below every player-1 fleet number (2–21) |

Hashes (sha256):
- `zmd.HST`: see `SHA256SUMS.pre`
- `zmd.spec`, `tools/gen.py`: see `SHA256SUMS.pre`

Runs: one pinned year at cycles 20000, 30000 and 14000.

P is read from T's new salvage and player 1's minefield message (stop
point). A lane decides only when T was stopped with d ≥ 3. With d = 0,
R-start and R-death coincide. Lanes where T was not stopped are
controls, and all three readings say the chasers chase T's end position.

## Predictions

Z-MD-1 and Z-MD-3, in each lane where T died with d ≥ 3:

| Chaser | R-start (predicted) | R-death | R-stop |
|---|---|---|---|
| C-near | ends at S = (1160, y), waypoint completed (28 ly) | ends at P (within 81 ly when d ≤ 57), else 81 ly toward P | stays at (1140, y − 20) |
| C-far | ends at (1160, y ± 35): 25 ly straight toward S | 25 ly toward P: x = 1160 + round(25d/√(d² + 3600)), not on x = 1160 | stays at (1160, y ± 60) |

Z-MD-3 predicts the same as Z-MD-1, so fleet number order does not
matter.

Z-MD-2 (control, the documented rule for a live target): T is stopped at
P and survives. C-near goes to P, completing its waypoint when P is
within 81 ly (d ≤ 57), otherwise 81 ly toward P. C-far moves 25 ly
toward P.

If no lane has a dying T with d ≥ 3, that case is NOT RUN.
````

The start-file hashes it points to (`SHA256SUMS.pre`):

```text
62f7b9112cc47edd8c0c61efa21f2e033df238541265e1213502f2a129bae856  zmd.HST
33cbbd136445a44ba1f28bdc240c2a26affb5733aa74490553e7afa1ff571a80  zmd.spec
c788af710150f1b2a50beee25c7bd1e8ce3dc98522b781a34af9e57972502be1  tools/gen.py
```

Raw evidence is in the private apparatus, `evidence/zmd`.

## Results

One pinned year at cycles 20000, 30000 and 14000. Each lane-run is one
lane in one stream (20 lanes, 3 streams). d is how far into its leg T
was stopped, read from player 1's minefield message and T's new
salvage.

| Case | Observed | Result |
|---|---|---|
| Z-MD-1 (Bare DD target) | 29 lane-runs, in 3 of 3 streams, had T destroyed with d ≥ 3 (d from 3 to 74). In every one, C-near ended at S with its waypoint completed, and C-far ended 25 ly straight toward S, at (1160, y ± 35). No chaser matched R-death or R-stop. | R-start CONFIRMED by prediction (29 of 29) |
| Z-MD-1, d < 3 | 5 lane-runs (d 1 or 2) | not scored, as the pre-run said |
| Z-MD-1, T not stopped | 2 lane-runs: both chasers chased T's end position | control, as predicted |
| Z-MD-3 (C-near numbered 0 or 1, below every player-1 fleet) | 5 lane-runs with d ≥ 3, in 3 streams: R-start for both chasers. 1 more lane-run had d = 2. | CONFIRMED by prediction: the fleet-number order made no difference here |
| Z-MD-2 (Tank target, survives) | 17 lane-runs with T stopped and alive (d from 1 to 69): C-near ended at P, or 81 ly toward P when d = 69, and C-far moved 25 ly toward P. 1 lane-run had T not stopped. | control CONFIRMED by prediction: the live target's position is used |

MEASURED, not predicted:

- **Message 0x028.** Player 0 got 0x028 once for each C-far whose
  target died, with params (follower, 512 + T's fleet id): 14 + 13 + 13
  = 40 over the 3 streams, one per death. The C-near chasers, whose
  waypoint completed at S, got none.
- **C-far's waypoint 1 after the year.** In all 40 lane-runs where T
  died (34 with d ≥ 3), the waypoint no longer named T. It was deep space
  at S, not at P. In the 17 lane-runs with T alive at P and the 3 with T
  not stopped, it still named T, at T's end position.

## Scope

This covers targets destroyed by mines during movement in this setup:
one player-0 heavy field, a warp 9 target with an 81-ly leg due east,
warp 9 and warp 5 chasers whose waypoint 1 is aimed at it, owned by the
field's owner, and no battle. Other causes of death (battle, scrapping,
merging, a wormhole), other waypoint indexes, chasers that are stopped
themselves, and a target killed by another chaser's field are NOT RUN.
