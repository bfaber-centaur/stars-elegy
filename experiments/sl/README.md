# Ship launch oracle batch (SL-01 to SL-12)

Behavior-level restatement of the stars-decomp ship-launch predictions
(SL-01..SL-12, stars-decomp #23), committed before the runs. The
geometry is that of the Combat Lab base, game CB.
`gen.py OUTDIR` writes the CombatLab specs. Runs are pinned at cycles
20000 and 30000; `sl-routes` and `sl-starbases` also run a second year
from each first year's result.
Raw evidence is in stars-oracle-apparatus `evidence/sl/`.

Designs:
- Scout: Scout hull, Long Hump 6, Rhino Scanner, X-Ray Laser (23 kT, 50 mg).
- QJ5 Scout: Scout hull, Quick Jump 5, Bat Scanner (14 kT, 50 mg).
- Colony: Colony Ship hull, Long Hump 6, Colonization Module (200 mg).
- Mini-Miner: 574 kT, 210 mg.

Every building planet has population 1000 (100,000 colonists),
100 factories and 20000 kT of each mineral. Tech is 26 in every field.

## Predictions

### `sl-routes` (player 0 JOAT, stations; player 1 JOAT)

- **SL-01.** Planet 15 has queue `[Scout ×2, Scout ×1, Colony ×1]` and no
  route. It makes three new fleets, holding 2, 1 and 1 ships. Each has
  full fuel (100, 50, 200), no cargo, battle plan 0, and one waypoint at
  the planet (task none, warp 0).
- **SL-02.** Player 1 owns fleets 0, 1 and 3, and planet 8 queues
  `[Scout ×1, Scout ×1]`. The new fleets are numbered 2 and 4.
- **SL-03.** In the build year a new fleet's byte 5 lacks bit 0x20. In
  year 2, the SL-01 fleets, which stay put, have it.
- **SL-04..SL-07.** Each source planet queues `[Scout ×1, QJ5 Scout ×1]`
  with a route. Each new fleet's waypoint 1 is the destination, with
  task route and this warp:

| case | source → destination | distance | destination | Scout | QJ5 |
|---|---|---|---|---|---|
| SL-04 | 22 → 23 | 12 | unowned | 4 | 4 |
| SL-04 | 19 → 21 | 17 | unowned | 5 | 5 |
| SL-04 | 10 → 13 | 25 | unowned | 6 | 4 |
| SL-04 | 14 → 13 | 41 | unowned | 5 | 5 |
| SL-04 | 12 → 18 | 86 | unowned | 6 | 5 |
| SL-04 | 0 → 6 | 299 | unowned | 6 | 5 |
| SL-05 | 17 → 19 | 72 | own Station | 7 | 9 |
| SL-05 | 9 → 7 | 94 | own Station (gate) | 7 | 7 |
| SL-05 | 20 → 14 | 84 | own Station | 7 | 7 |
| SL-05 control | 4 → 5 | 77 | own Orbital Fort | 6 | 5 |
| SL-05 control | 11 → 8 | 77 | player 1 Station | 6 | 5 |
| SL-06 | 2 → 3 | 49 | own Station, gates both ends, safe | 11 | 11 |
| SL-06 | 1 → 7 | 309 | own Station, gates both ends, beyond the 250 ly range | 6 | 6 |
| SL-07 | 16 → 16 | 0 | itself (Station) | 2 | 2 |

  The gates are Stargate 100/250. In SL-05, a dock at the destination
  would give 7/9, 7/7 and 7/7; with no dock the same distances give
  5/5, 6/5 and 6/5. The controls would give 7/9 if the dock rule applied
  to them. Every route word is unchanged after the turn.

### `sl-limit-a` and `sl-limit-a-ctl`

- **SL-08.** Player 0 owns fleets 0..510, none at planet 17, which queues
  `[Scout ×1, Scout ×1]`. Fleet 511 is made, holding 2 Scouts. There is
  no fleet 512, and the player count reads 512 fleets.
- **SL-09.** Player 1 owns fleets 0..511, none at planet 8, which queues
  `[Scout ×2, Colony ×1, Factory ×5]`. No ship is built and no fleet
  changes. Both ship items leave the queue and the 5 factories are
  built (100 → 105). Research ends lower than in the control (queue
  `[Factory ×5]` only) by the ships' resource cost: the resources are
  spent, not refunded.

### `sl-limit-b` and `sl-limit-b-ctl`

- **SL-10.** Player 0 owns 512 fleets. Fleets 3 and 5 orbit planet 17:
  fleet 3 holds 10 Scouts at 50% damaged / 100 units, and fleet 5 one
  healthy Scout. Planet 17 queues `[Scout ×1]`. Fleet 3 receives the
  Scout: 11 Scouts at **45% / 125 units**. Fleet 5 is unchanged and
  there is no new fleet.
- **SL-10 variant.** Player 1 owns 512 fleets; fleet 3 holds 32765
  Scouts and fleet 5 one, both at planet 8, which queues `[Scout ×1]`.
  Fleet 5 receives the Scout (2 Scouts), and fleet 3 stays at 32765.
- The control has the same fleets with empty queues. It shows what the
  year does to fleet 3's damage without a build, such as repair at the
  starbase.
- **SL-10 follow-up** (`sl-limit-b300`, added after the first runs and
  committed before its own). This is the same setup with fleet 3 at
  50% / 300 units. The merge predicts 11 Scouts at 45% / 375 units.
  After that year's repair, the final units should be 375 less the
  repair that its control (`sl-limit-b300-ctl`) shows on 300 units.

### `sl-starbases` (player 0 JOAT + Improved Starbases; player 1 AR + Improved Starbases)

- **SL-12.** Each queue is `[new starbase ×1, Scout ×2]` unless noted:

  | planet | old → new | Scouts built |
  |---|---|---|
  | 17 | Space Station → Space Dock | 0 (ship items removed; queue empty) |
  | 15 | Space Dock → Space Station | 2 |
  | 11 | Space Station → Station B (same hull) | 2 |
  | 12 | Station at 200 damage units → Station B | 2; new starbase keeps 200 units |
  | 8 (player 1) | Death Star → Ultra Station | 0 |
  | 19 | Orbital Fort, queue `[Scout ×1]` | 1 |
  | 18 | Space Dock, queue `[Mini-Miner ×1]` (574 kT, above the 200 kT dock) | built (LEGACY BUG) |

- **SL-11.** (a) Player 1 (AR) builds a Mini-Miner at its own Station
  planet 4, with no route. Its waypoint 0 task is remote mining and its
  battle plan 0. In the build year planet 4's surface minerals change
  only by the Mini-Miner's cost (no mining). In year 2, staying put, it
  mines. (b) Player 0 (JOAT) builds the planet-18 Mini-Miner with task
  none.

## Results (two streams each, cycles 20000 and 30000; identical in both unless stated)

- **SL-01: CONFIRMED.** Planet 15 made three fleets: 2 Scouts with
  fuel 100, 1 Scout with fuel 50, and 1 Colony with fuel 200. Each had
  plan 0 and one waypoint at the planet (task 0, warp 0).
- **SL-02: CONFIRMED.** Player 1's new fleets were numbered 2 and 4.
- **SL-03: CONFIRMED.** Every new fleet had byte 5 = 0x09 in its build
  year. The pre-existing fleets that stayed put had 0x29. In year 2 the
  SL-01 fleets read 0x29.
  - Not predicted: the route-to-itself fleets (SL-07) still read 0x09
    in year 2, at their planet with 2 waypoints.
  - Not predicted: the AR Mini-Miner on remote mining (SL-11a) also
    read 0x09 in year 2.
- **SL-04..SL-07: CONFIRMED, 28 of 28 warps.** Every fleet's waypoint 1
  was its destination with task 8, at the warp in the table, including:
  - 11 through the safe gates;
  - 6/6 beyond the gate range;
  - the dock rule only at own Stations, not at the own Fort or player
    1's Station;
  - warp 2 for the route to itself.
  Every route word was unchanged.
- **SL-08: CONFIRMED.** Player 0 made fleet 511 holding both Scouts and
  reached 512 fleets, with no fleet 512.
- **SL-09: CONFIRMED in part.** No ship was built and no fleet changed.
  The queue emptied and factories went from 100 to 105.
  - Planet 8's minerals ended 12/6/13 kT lower than in the control (Fe/Bo/Ge),
    so the ships' minerals were spent, not refunded.
  - Not testable here: the research comparison. Both players were at
    tech 26 in every field, and research accumulation stayed 0 in both
    runs.
- **SL-10: CONFIRMED (with the year's repair after the merge).** Fleet 3
  received the Scout: 11 Scouts at 45%, with 25 units after the year
  (predicted 45% / 125 at the merge). Its control went from 100 units
  to undamaged. In the follow-up the control went 300 → 200 units, a
  repair of 100. The merge ended at 45% / 275, which is the predicted
  375 less that 100. That rules out the merge-order rule (46% / 100
  units scale).
- **SL-10 variant: CONFIRMED.** Fleet 5 received the Scout (2 Scouts),
  and fleet 3 stayed at 32765.
- **SL-11: CONFIRMED.**
  - (a) Player 1's AR Mini-Miner had waypoint 0 task 3 (remote mining)
    and plan 0.
  - AR planet 4 gains minerals with no mines and no miner: +19/+3/+27 kT
    in year 1 and +20/+3/+29 in year 2 in `sl-starbases-ctl`.
  - In the build year, planet 4 changed by exactly that baseline less
    the Mini-Miner's cost. The cost is 22/0/7, the same as player 0's
    Mini-Miner at planet 18, so there was no mining.
  - In year 2 it added +5/+1/+7 over the control's baseline.
  - (b) Player 0's Mini-Miner had task 0.
- **SL-12: CONFIRMED.**
  - Station → Dock: Dock built, no Scouts, queue empty.
  - Death Star → Ultra Station (AR): Ultra built, no Scouts.
  - Station → Station B: built, 2 Scouts.
  - Orbital Fort: built its Scout.
  - Space Dock: built the 574 kT Mini-Miner (LEGACY BUG).
  - Damaged Station → Station B: the new Station read 150 units after
    the year, and the unreplaced control Station went 200 → 150 → 100.
    So the damage is kept and then repaired as usual.
  - Dock → Station first reached only 88% for lack of resources. In
    `sl-starbases-ctl`, with three times the resources, the Station was
    built and so were both Scouts.
