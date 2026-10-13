# RG-004: a representative game with other races, 12 chained years

Sprint milestone 2: multi-year parity on a second representative game, to
widen it beyond the six AIX computer-player races of RG-001 to RG-003.
RG-004 is 12 chained years (2466 to 2477) of a new game in which seven
custom races are played by expert computer players.

**This is not a game recorded from its start.** The game was created on
2026-10-13, then 65 years (2400 to 2465) were generated **unrecorded**,
with the host planning for the computer players (the warm-up, below).
The recorded chain starts from that state. Every order in the 12 recorded
years was written by the original's computer players. No order was
injected.

Vector: `vectors/rg/rg004.json` (12 chained years) and `rg004-y1` to
`rg004-y12` (each year alone, from the original's files for the year
before). Raw evidence: private apparatus `evidence/rg004`. The race files,
the game definition and the warm-up files stay there.

## Game and races

A new game from a definition file (`docs/ORACLE.md` "New games from a
definition file"): small universe (160 planets), dense, close player
positions, random events on, no slower tech, seven players. Each player is a
custom race built with `racelab` from one base race. Only the primary and
lesser racial traits differ, so all seven want the same planets. Every race
has positive advantage points.

| Player | Name | PRT | LRTs |
|---|---|---|---|
| 0 | Warlords | WM | IFE, NRSE |
| 1 | Sappers | SD | ISB |
| 2 | Gaters | IT | GR, OBRM |
| 3 | Jackals | JoaT | TT, CE |
| 4 | Slingers | PP | MA, NAS |
| 5 | Settlers | IS | LSP, RS |
| 6 | Swarms | HE | UR, BET |

The same for every race: growth 10%; habitability gravity, temperature
and radiation each centred at 50 with range 15 to 85; 1,000 colonists per
resource; factories 10 output, 10 cost, 10 per 10,000; mines 10, 5, 10;
normal research cost in every field; leftover points to surface
minerals. The vector's `initial_state` carries each race in full.

## Computer players (setup step)

A definition file can name a race file for a human player or a built-in
computer player, but not a computer player with a custom race. Before the
first year, one setup step made every player an expert computer player.
This is equivalent to creating the game with computer players. The step
changed one byte of each player's record, the byte that holds the computer
flag, the level and the personality. The values come from AIX, a game
created with definition-file computer players (MEASURED,
`docs/ORACLE.md` "Computer players in the host file"): types 1 to 6
(Robotoid to Macinti) at expert gave 0x0f, 0x2f, 0x4f, 0x6f, 0x8f and
0xaf. The same step set every pair of players to enemies, as AIX's
computer players start. Nothing else changed.

The personalities are the three that Elegy treats as faithful
(`docs/AI.md`):

| Personality | Players |
|---|---|
| Robotoid | 0 (WM), 3 (JoaT), 6 (HE) |
| Rototill | 1 (SD), 5 (IS) |
| Cybertron | 2 (IT), 4 (PP) |

Here a personality plays a race of another PRT than its own. Whatever the
computer players wrote is the original's own behaviour and only legal
orders. It is not a sample of how these personalities play their own
races. In the warm-up, players 1, 2, 3 and 5 stayed at one to four
planets, while players 0, 4 and 6 expanded.

## Warm-up and choice of the start year

The warm-up ran years 2401 to 2465 with `tools/fleetlab/years`, the host
planning for every player. Years 1 to 40 ran at cycles 20000 + 1000·k.
Years 41 to 65 ran on 25 cycles values chosen to reach different streams
(`docs/ORACLE.md` "Pinned battle RNG"). These years are not part of the
vector and were not checked against anything. The start was chosen by
counting battle records per year. There were 0 to 2 a year until 2440, 1
to 4 from 2441 to 2454, and 4 to 9 from 2455 to 2465. The recorded chain
starts from the state after 2465, the last warm-up year.

## Recording

The method is RG-001's (`experiments/rg002/README.md` "Recording"), with
no client orders:

- the computer players plan from the current files, and every player's
  last order file is captured;
- the year is generated with every order file supplied, so the host runs
  no computer player and the random stream starts at seeding (cycles
  20000, tick 164);
- the year is generated again from the same files.

All 12 repeats were byte-identical. Every year was also generated at
cycles 3700 and 1490 from the same files and orders. An expectation that
differed in either stream is flagged `sample: true`, with `start_sample`
on battles and `alt_battle` for places only another stream fought
(`vectors/README.md`).

Every order every player gave is in the vector's `orders`, decoded: 2,049
orders in 84 order sets. Most are waypoint changes (1,259) and production
queues (410). The rest are waypoint adds and deletes, research, cargo,
fleet battle plans, planet settings, ship moves between fleets, and
designs and design deletions.

## Counts

| | |
|---|---|
| Fleets at the start | 213 |
| Expectations | 2,941, 404 of them `sample: true` |
| Battle records | 55 (4 to 6 a year) |
| `start_sample: false` | 54 of 55; the drawn one is year 1 at (1320,1343), players 0, 3 and 4 |
| `alt_battle` | 1: year 3 at (1365,1400) |
| Planets taken from another player | 9: WM from HE 4, HE from WM 2, JoaT from HE 1, HE from JoaT 1, SD from WM 1 |
| Packets | 23 packet expectations (the PP player) |

The Mystery Trader was not on the map in the recorded years. Computer
players keep only four message kinds (`docs/MESSAGES.md`), so the
vector's messages cannot show a random event. A comet or other event in
these years would have changed planets differently in the other streams,
and those planet values are flagged as samples.
