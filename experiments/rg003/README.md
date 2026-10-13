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
that differed in either stream is flagged `sample: true`. For message
sequences, a message is a sample when it is not in a longest common
subsequence with both other streams. This applies to all 12 years and
to every file: rebuilding from the raw evidence gives the 13 published
files byte for byte. Of the 156 messages in the 84 sequences, 20 are
samples by the battle rule and 7 more only by this rule (years 2, 5, 7
and 10, the same in the single-year files).

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

What the orders did (checked 2026-10-13 against the raw files and the
client's screenshots):

- **Year 9, battle plan.** The client wrote plan 5 "Guard" with tactic 4,
  primary 2 (starbase), secondary 1 and attack-who 2, which is plan 0's
  attack-who. `plan who 1` changed nothing: in this game the dialog showed
  the Attack Who list greyed out, reading "Everyone", before and after the
  keys. So the injected order copied the plan and set its name and
  primary target, but **not** the intended attack-who. In BP-1 (Combat
  Lab, `experiments/bp`) the same command did change it. Why the list was
  greyed here is UNRESOLVED.
- **Year 10, queue removal.** The removed row was a Mine ×1 at 39%: the
  hidden partial item that an auto item leaves at the front of the queue
  (`PARITY.md` "Production Queues", C04/C14). It was spawned in 2470,
  when the Auto Mines items ran out of resources. The client wrote the
  queue without it (7 items, as shown on screen). The year started with
  the order applied: the homeworld built 30 + 21 = 51 mines (718 to 769),
  while in the other years a carried partial is finished first and the
  first count is 31 (2471: 31 + 27, 660 to 718; 2473: 31 + 35). At the
  end of 2472 the Auto Mines item ran short again and left a **new**
  Mine ×1 partial, at 79%. That is why the queue still starts with a
  Mine ×1 partial. So the removal took effect, as in LQ-2
  (`LIMITS.md`: a removed partial item is dropped). The host neither
  refused the removal nor dropped the order.
- **Year 12, "item 8".** Item 8 of the client's buildable list is
  Defenses. 20 were built in 2474 (0x03a).

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

## Start tokens in the other streams (`start_sample`)

These tables let anyone check the `start_sample` label (vectors/README.md)
on two year-10 (2472) battles without the private files. Each row is one
start token as the battle record gives it, in the record's own order:
owner, fleet (or the planet for a starbase), design, ships, and damage
(units, percent of ships). "20000" is the recorded stream that the
vector holds; 1490 and 3700 are the alternative streams. Read with
`build_cb.battles` from each stream's `.M` files (apparatus
`evidence/rg003/run/y10`). MEASURED, one run per stream.

Battle at (1513,1113), over planet 83, players 1, 4 and 5:
`start_sample: false`.

| Stream | Tokens in record order (owner, fleet, design, ships, damage) |
|---|---|
| 20000 | (4, 0, 1, 1, 0/0); (4, planet 83, 25, 1, 0/0); (4, 2, 2, 1, 0/0); (5, 1, 7, 8, 237/75); (1, 45, 13, 1, 0/0) |
| 1490 | (4, 2, 2, 1, 0/0); (4, planet 83, 25, 1, 0/0); (5, 1, 7, 8, 237/75); (1, 45, 13, 1, 0/0); (4, 0, 1, 1, 0/0) |
| 3700 | (4, planet 83, 25, 1, 0/0); (4, 2, 2, 1, 0/0); (1, 45, 13, 1, 0/0); (5, 1, 7, 8, 237/75); (4, 0, 1, 1, 0/0) |

The same five stacks appear in all three streams. Only their order
differs, so the record keeps `sample: true`.

Battle at (1571,1434), over planet 94, players 1 and 5:
`start_sample: true`.

| Stream | Tokens in record order (owner, fleet, design, ships, damage) |
|---|---|
| 20000 | (1, 88, 13, 1, 0/0); (5, 91, 1, 1, 0/0); (5, 74, 0, 4, 0/0); (5, 92, 1, 1, 0/0); (1, 86, 14, 1, 0/0); (1, 81, 14, 1, 0/0) |
| 1490 | (1, 88, 13, 1, 0/0); (5, 74, 0, 4, 0/0); (1, 86, 14, 1, 0/0); (5, 92, 1, 1, 0/0); (5, 91, 1, 1, 0/0); (1, 81, 14, 1, 0/0) |
| 3700 | (5, 74, 0, 4, 0/0); (1, 81, 14, 1, 0/0); (1, 86, 14, 1, 0/0); (5, 91, 1, 1, 0/0); (5, 92, 1, 1, 0/0) |

Stream 3700 has no token for player 1's fleet 88, so the stacks differ.
In both battles, every token that is present starts on the same square
in all three streams.
