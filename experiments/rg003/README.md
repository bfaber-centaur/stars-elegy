# RG-003: RG-002 extended to 12 chained years

Sprint milestone 2: multi-year parity on a representative game. RG-003 is
RG-002 continued from 6 to 12 chained years (2462 to 2474), published as its
own vector so that the 6-year RG-002 ledger stays stable.

**This is not an unedited played game, and player 0's orders are not
original AIX play.** Years 1 to 6 are RG-002's recorded years, unchanged:
the same files and the same orders (`experiments/rg002/README.md` lists
every start edit and those years' orders). In those years the vector's
initial state, orders and expectations equal RG-002's, compared field by
field when it was built. Years 7 to 12 were recorded on 2026-10-13 by lane F
in the same way, continuing from RG-002 year 6's generated files.

Vector: `vectors/rg/rg003.json` (12 chained years) and `rg003-y1` to
`rg003-y12` (each year alone, from the original's files for the year
before). Raw evidence: private apparatus `evidence/rg003`.

## Recording (years 7 to 12)

The method is RG-002's (`experiments/rg002/README.md` "Recording"):

- player 0's orders written by the original client;
- the computer players plan from the current files, and their last order
  files are captured;
- the year is generated with every order file supplied, so the host runs
  no computer player and the random stream starts at seeding (cycles
  20000, tick 164);
- the year is generated again from the same files.

All six repeats were byte-identical. Every year was also generated at
cycles 3700 and 1490 from the same files and orders, and an expectation
that differed in either stream is flagged `sample: true`.

Every order every player gave is in the vector's `orders`, decoded. No
order kind was new to the decoder, and no year or order was dropped.

## Player 0's injected orders

After year 6, player 0 (JOAT, the edited human slot) held its homeworld
(planet 51) without a starbase, three colonies and five fleets, none in
orbit at the homeworld. Lane F chose one client command set per year
(`cmds/`), using order kinds the decoder already handled and avoiding the
fleet operations that need host-accepted order files. They keep a player
giving client orders every year, as in RG-002. They do not reproduce any
human's play.

| Year | Commands (`cmds/yNN.txt`) | Order the client wrote |
|---|---|---|
| 7 (2469) | add the Home Station starbase at the top of the homeworld queue | production queue, starbase first. The starbase was built in 2470 |
| 8 (2470) | research budget +15, next field item 1 | research 55%, field propulsion, next energy |
| 9 (2471) | copy battle plan 0 as "Guard", primary 2, attack-who 1 | battle plan in slot 5 |
| 10 (2472) | remove the first item of the homeworld queue | production queue without that item |
| 11 (2473) | research field 4, budget -5 | research 50%, field electronics |
| 12 (2474) | add item 8 ×20 at the top of the homeworld queue; "leftover resources to research" on | production queue, plus planet settings (leftover to research) |

## Counts

| | Years 1–6 (RG-002) | Years 7–12 | RG-003 |
|---|---|---|---|
| Order sets (player-years) | 42 | 42 | 84 |
| Orders | 1,867 | 1,864 | 3,731 |
| Expectations | 2,652 | 3,199 | 5,851 |
| Samples | 785 | 552 | 1,337 |
| Battles | 44 | 58 | 102 |

Expectations by kind (all 12 years):

- fleet 2,062, planet 1,615;
- production_queue 773, object 507, player 184, minefield 173;
- battle 102, battle_actions 102, fleet_gone 95;
- message_sequence 84 (every player, every year), message 73;
- salvage_at 59, object_gone 9, design 8;
- starbase_design 4, battle_plan 1.

The default-queue record of year 1 is carried, as in RG-002.
