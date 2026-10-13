# RG-002: a late-game representative game (state-edited start)

Lane F of the engine completion sprint. RG-002 is the second representative
game for multi-turn parity. It aims at the economy behaviours that RG-001
never exercised (the economy lane's coverage run over RG-001; its top gaps
were the auto queue items, population over the maximum, late-game mining,
late research under slower tech, and remote mining).

**RG-002 is not an unedited played game.** Its start is the AIX
computer-player game at 2461 with the edits below, followed by one settling
year. The recorded years are played from there.

Public vectors: `vectors/rg/rg002.json` (the six years chained) and
`rg002-y1` to `rg002-y6` (each year alone). They are built with
`tools/vectors/build.py rg evidence/rg002`. Raw evidence is in the private
apparatus `evidence/rg002`. That includes the game files and the client's
order files, which carry the registered serial.

## Start

The source is year 2461 of the apparatus game `evidence/ai/aix`, the year
after RG-001's source years end:

- a small universe, normal density, random events on, seven players;
- player 0 is the human slot (it never submitted orders in AIX);
- players 1 to 6 are the expert Robotoid, Turindrone, Automitron, Rototill,
  Cybertron and Macinti.

Before any edit, the state is already late game:

- two homeworlds have concentrations of 18/16/16, and a third has 31/29/29;
- 87 planets have some mineral below concentration 30;
- tech runs to level 13;
- there are 183 fleets.

## Edits

Every edit is in `rg002.spec` (`combatlab build`, with the new
`keepdesigns` directive). Two more edits follow:

- `hst-edit edit … player=0 field=0,7` sets player 0's next field to
  lowest.
- `hst-edit xy … 10:06` turns on slower tech (game option bit 1).

Nothing else changed.

**Player 0:**

| What | Edit |
|---|---|
| Race | JOAT + ARM. Its habitat is unchanged; its advantage points are 246 (legal). |
| Research | Energy raised from 12 to 25, with its other levels as before. The energy accumulation is set close to level 26 under slower tech. Research is 30% (was 15%). The field is energy and the next field is lowest. |
| Homeworld | Population 18,000 units, which is 150% of its JOAT maximum of 12,000. Concentration set to 25/22/28. |
| Colonies | Planets 92, 95 and 100 were unowned and are now player 0's. Each colony had its current environment moved inside player 0's range on one axis, and has 10 to 30 mines and factories. |
| Colony 92 | Population 800, over its maximum of 600 at habitability 3. Ironium concentration 3. |
| Colony 95 | Population 2,600, just over its maximum of 2,400. Boranium concentration 5. |
| Colony 100 | Population 3,000, under its maximum of 4,920. |
| Queues | Every player-0 queue and its default queue hold Auto Factories 100, Auto Mines 100, Auto Defenses 20, Auto Min Terraform 5 and Auto Max Terraform 5. The homeworld also queues its starbase design slot 1, a second Space Station design that replaces its own. |
| Designs | A remote miner design (ship slot 3) is added, with starbase slots 1 (Space Station), 2 (Orbital Fort) and 3 (Ultra Station). Colony 95 gets the Orbital Fort and colony 100 the Ultra Station. |
| Fleets | Four one-ship remote miners with the remote-mining task, on unowned planets 73, 87, 116 and 45. A scout in deep space at (1400, 1500). A freighter carrying 50 colonists, two years from colony 92 at warp 5, with an unload order. |

**Other players:**

- **Macinti (AR):** its empty starbase slot 3 becomes a Death Star (an
  AR-only hull), placed on its planet 46.
- **Rototill (CA):** a second ship of its Orbital Adjuster design (slot 2)
  over player 0's colony 95. Rototill gives no orders to ships of that
  design (`docs/ai/rototill.md`).

**Already in the unedited state:**

- Macinti's two-ship remote miner works its own homeworld.
- Rototill's first Orbital Adjuster ship is over its own homeworld.
- The Robotoid player (HE) is immune on every axis.
- The Cybertron player (PP) launches about 35 packets a year.

### Edits tried and dropped (observations, not part of the vectors)

- **Planets taken from the Robotoid.** With three of its planets given to
  player 0, the host stopped on "Player log file aix.x2 appears to be
  corrupt". The Robotoid's order file, planned from its own view, still
  referred to them. Player 0's colonies were taken from unowned planets
  instead.
- **Death Star on player 0's homeworld.** A Death Star queued at player
  0's homeworld (JOAT) was removed from the queue without a message. Its
  hull is AR-only.
- **Ultra Station and Space Dock replacing player 0's Space Station.** A
  queued Ultra Station (empty, or with parts in matching slots) and a
  queued Space Dock were also removed without a message. That happened at
  construction 8, 12, 14, 20 and 26. An Orbital Fort and a Space Station
  design were built.
  - UNRESOLVED. SL-12 built an Ultra Station at tech 26 for an AR player.
  - The client listed the Ultra Station as an upgrade.
  - The homeworld replacement uses a Space Station design instead.

## Settling year

One year (2461 to 2462) was generated from the edited files with no
player-0 orders. That way every player's `.M` file shows the edited state
before any computer player plans from it. The settling year is not
recorded. The vectors start from its result, the 2462 files.

Observed in it:

- No race-degrade message was sent.
- The homeworld's starbase was replaced.
- Overcrowding messages (0x026) came from the homeworld and colonies 92
  and 95.
- The Death Star stayed on Macinti's planet. Macinti rewrote that design
  slot's parts: it is still a Death Star.

## Recording (`tools/rg2-chain` in the apparatus)

Each of the six years runs as follows:

1. Player 0's orders are written by the original client
   (`tools/fleetlab/client-orders`, with the year's command file in
   `cmds/`).
2. The computer players plan in a pinned generation with that order file
   present. Only their order files are kept.
3. The year is generated with every order file supplied, at cycles 20000.
   The host runs no computer player, and the year's draws start at seeding
   (tick 164).
4. The year is generated a second time to check that the output repeats.

Each year was also generated at cycles 3700 and 1490 (other streams) to
flag drawn outcomes as samples, as in RG-001.

Player 0's client orders, by year:

| Year | Orders |
|---|---|
| 1 (2462) | Scrap the deep-space scout (salvage). |
| 2 (2463) | Add one Auto Mineral Packets at the top of the homeworld queue. The homeworld has no mass driver. |
| 3 (2464) | Raise the research budget by 10 percentage points. |
| 4 (2465) | Clear the remote-mining task of the miner on planet 45. |
| 5 (2466) | Add Auto Mines 30 at the top of the homeworld queue. The command asked for 30 Defenses (left-list row 8); the list had changed that year, and the row added was Auto Mines. The vector carries the order as submitted. |
| 6 (2467) | Change the field being researched to propulsion (field 2); the next field stays lowest. The planned order, scrapping the freighter at the homeworld's starbase, could not be given: the Robotoid player destroyed the homeworld's starbase in 2465 and the freighter in 2466. That first attempt, with no player-0 orders, is kept in the apparatus as `run/y06-noorders` and is not in the vectors. |

## Results

Recording:

- All six recorded years advanced, and each gen2 repeat was byte-identical
  to its gen run.
- Each year was also generated at cycles 3700 and 1490. The first 1490
  runs stopped the oracle mid-write, because `pinned-turn` took the host
  file's brief absence during the rewrite as the new year. `pinned-turn`
  now waits for a turn number that differs (this PR). It then ran all six.
  The 3700 runs had used the old loop, and year 6's host file
  (`y06/alt3700`) was cut off while Stars! was still writing it. Before
  2026-10-13 the dump tool hid the error, and the vector builder read
  that stream without its host file. Year 6 was re-run at 3700 on
  2026-10-13 (`docs/ORACLE.md` "Dump audit (DA-1)").
- The vector has 6 years, 189 fleets at the start, 42 order sets (1,867
  orders) and 2,669 expectations, 408 of them `sample: true`. The year's
  draws start at tick 164 in every year (`random_start`). Corrected
  2026-10-13: this said "(1,866 orders) and 2,610 expectations, 764 of
  them `sample: true`", an earlier build. The build before the year-6
  re-run gave 1,867 orders, 2,652 expectations and 785 samples.

Observed (one stream each; samples flagged in the vector):

- **Population over the maximum.** The homeworld fell from 18,000 to
  15,744 units over the six years. Colony 92 (maximum 600) fell from 800
  to 772. Colony 95 (maximum 2,400) fell from 2,600 to 2,544.
  Colony 100, under its maximum, grew from 3,000 to 3,216.
- **Auto queue items.** The homeworld and colonies 95 and 100 built
  mines and factories every year. The homeworld had 15 mines at the start
  and 599 in 2468. Colony 92 built only factories, 15 at the start and 53
  in 2468; its 10 mines did not change.
- **Slower tech and the lowest field.** Energy reached level 26 in 2464
  (recorded year 2). The field switched to biotechnology, the lowest,
  which reached level 6 in 2465.
- **Remote mining.** Surface minerals rose every year on the four
  mined planets 73, 87, 116 and 45. Year 4's order cleared the miner's
  task on planet 45, and planet 45 did not change in 2466. The Cybertron
  player colonized it in 2467.
- **Starbases.** Colony 100's Ultra Station fought in 2463, 2466 and 2468.
  Its damage was 9 in 2466, repaired to 0 in 2467, and 26 in 2468. The
  Robotoid player attacked the homeworld every year from 2463 to 2466.
  The Space Station was damaged to 30 in 2464 and destroyed in 2465. The
  freighter there (fleet 1) was destroyed in 2466. Macinti's Death Star
  fought once, in 2468.
- **Hostile Orbital Adjuster.** Rototill's second adjuster stayed over
  colony 95 for all six years. Colony 95's environment did not change.
  The colony kept its Orbital Fort throughout, so this observes "a
  hostile adjuster does nothing at a planet with a starbase" (one
  planet). It does not reach the worsening clicks.
- **Salvage.** The year-1 scrap left salvage at (1,400, 1,500). The
  computer players aimed fleets at salvage and loaded from it
  (cargo kind 0x82, decoded in `build_orders`). The vectors write those
  orders with the new `packet_object` waypoint target and `salvage`
  cargo partner.
- 44 battles (8, 7, 7, 8, 5 and 9 in 2463 to 2468).
- **Default queue cleared.** Player 0's default production queue (the
  edited Auto items) was empty after recorded year 1 and stayed empty.
  Player 0's year-1 order file, written by the client, held one waypoint
  order and one record the client adds on saving (block type 46, the
  default-queue record), with no queue order. Without a
  player-0 order file it was kept: in the settling year, and in both RM
  years (`experiments/rm`), which start from the same settled files.
  The client's 2462 `.M1` file showed the edited default queue. The
  type 46 record carried no items and leftover off, and the host copied
  it over the player's default. That record is the client's own empty
  default template, written because it differed from the player's
  setting (rule BINARY-ONLY, `docs/ORDERS.md` "The player's default
  queue"). The later files held no type 46 record. The vectors carry
  the record as a year-1 `default_queue` order and the result as a
  year-1 `player` expectation (`default_queue: []`).

Elegy (main 79f3cdc), as of this PR:

- Elegy skips every RG-002 case. The computer players' orders aim at
  salvage (`packet_object` targets and `salvage` cargo), which Elegy does
  not read yet.
- With those orders removed (a local copy only; 59 orders in the chained
  vector), `rg002-y6` passes in all 8 seed variants. Years 1 to 5 differ,
  partly because of the removed orders. That run is not parity.

Economy's coverage method (`go test -coverpkg=./engine/...,./terraform/...,./objects/...`
over the 8 seed variants of every year vector, RG-001 against RG-002, with
the salvage orders removed from RG-002):

- Statements covered: 63.6% for RG-001, 67.0% for RG-002.
- Covered by RG-002 and not by RG-001 (0% before):
  - `autoInstall` (72.7%) and `terraform.AutoUnits` (66.7%);
  - `CanRemoteMine`, the remote-mining adapters (100%), `RemoteMine`
    (84.6%) and `remoteMineTask` (40.9%);
  - `starbaseDamage` (100%) and `loseStarbase` (50%);
  - the adjuster `relation` check (60%).
- Raised: `ResearchLevelCost` from 85.7% to 100%, `AddResearch` from 83.1%
  to 98.6%, `GrowPopulation` from 75.0% to 85.7%, `MaxPopulation` to 100%,
  and `depletionConcentration` to 100%.
- Still 0%: `terraform.Worsen` (the adjuster's planet has a starbase),
  `recycledResources` (no scrap at a starbase: year 6's planned scrap
  lost its starbase and freighter in battle), and the salvage load and
  unload paths (Elegy does not read those orders yet).
