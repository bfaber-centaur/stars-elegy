# RG-004: a representative game with other races, 12 chained years

Sprint milestone 2: multi-year parity on a second representative game, to
widen it beyond the six AIX computer-player races of RG-001 to RG-003.
RG-004 is 12 chained years (2466 to 2477) of a new game in which seven
custom races are played by expert computer players.

**This is not a game recorded from its start.** The game was created on
2026-10-13 at year 2400. Then 65 years were generated **unrecorded** (the
turns that produced 2401 to 2465), with the host planning for the
computer players (the warm-up, below). "Unrecorded" means that no orders
were captured and nothing was checked against Elegy. The host files after
each warm-up year were kept in the apparatus, but they are not part of
any vector.
The recorded chain starts from that state. Every order in the 12 recorded
years was written by the original's computer players, and no order was
injected (MEASURED: each year's order files are the ones the host's planner
wrote, captured unchanged).

Vector: `vectors/rg/rg004.json` (12 chained years) and `rg004-y1` to
`rg004-y12` (each year alone, from the original's files for the year
before). Raw evidence: private apparatus `evidence/rg004`. The race files,
the game definition and the warm-up files stay there.

## Game and races

A new game from a definition file (`docs/ORACLE.md` "New games from a
definition file"). Setup, as written in the definition file: small
universe, dense, close player positions, random events on, no slower tech,
seven players. The host file has 160 planets, random events on and slower
tech off (MEASURED, `initial_state`). Each player is a
custom race built with `racelab` from one base race. Only the primary and
lesser racial traits differ, so all seven want the same planets. Every race
has positive advantage points: 200 to 380 by `racelab`'s count (StarsAPI's
race builder, not the original's editor). The original accepted all seven
files and created the game (MEASURED).

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
This is taken to be equivalent to creating the game with computer
players (ASSUMPTION: no game was created both ways to compare). The step
changed one byte of each player's record, the byte that holds the computer
flag, the level and the personality. The values come from AIX, a game
created with definition-file computer players (MEASURED,
`docs/ORACLE.md` "Computer players in the host file"): types 1 to 6
(Robotoid to Macinti) at expert gave 0x0f, 0x2f, 0x4f, 0x6f, 0x8f and
0xaf. The same step set every pair of players to enemies, as AIX's
computer players start (MEASURED in the AIX host file). Nothing else
changed. The computer-player level bits are inferred: only expert was
measured. Updated 2026-10-14: the level bits for all four levels are now
MEASURED in the UG host files (`vectors/README.md` "Computer level"),
so this byte is the original's own expert byte.

The personalities are the three that Elegy treats as faithful
(`docs/AI.md`):

| Personality | Players |
|---|---|
| Robotoid | 0 (WM), 3 (JoaT), 6 (HE) |
| Rototill | 1 (SD), 5 (IS) |
| Cybertron | 2 (IT), 4 (PP) |

Here a personality plays a race of another PRT than its own. Whatever the
computer players wrote is the original's own behaviour. It is taken to be
legal orders, since the original's own planner wrote it (ASSUMPTION; the
orders were not checked against the client's limits). It is not a sample of
how these personalities play their own races. At the start (2465),
players 1, 2, 3 and 5 held 2, 2, 2 and 3 planets, and players 0, 4 and 6
held 51, 23 and 41 (MEASURED).

## Warm-up and choice of the start year

The warm-up generated the turns that produced 2401 to 2465 with
`tools/fleetlab/years`, the host planning for every player. Years 1 to 40 ran at cycles 20000 + 1000·k.
Years 41 to 65 ran on 25 cycles values chosen to reach different streams
(`docs/ORACLE.md` "Pinned battle RNG"). These years are unrecorded, as
defined above. The start was chosen by counting the battle records in each
warm-up year's files. There were 0 to 2 a year until 2440, 1 to 4 from
2441 to 2454, and 4 to 9 from 2455 to 2465 (MEASURED). The recorded chain
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

All 12 repeats were byte-identical (MEASURED). Every year was also generated at
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

All MEASURED from the recorded files.

| | |
|---|---|
| Fleets at the start | 213 |
| Expectations | 2,941, 404 of them `sample: true` |
| Battle records | 55 (4 to 6 a year) |
| `start_sample: false` | 54 of 55; the drawn one is year 1 at (1320,1343), players 0, 3 and 4 |
| `alt_battle` | 1: year 3 at (1365,1400) |
| Planets taken from another player | 9: HE from WM 4, WM from HE 2, JoaT from HE 1, HE from JoaT 1, SD from WM 1 (corrected 2026-10-13: the first version had the first two reversed) |
| Packets | 23 packet expectations (the PP player) |

## Random events

- **Messages cannot show them.** For computer players, except one
  computer-player setting, only four message kinds are kept
  (`docs/MESSAGES.md` "Computer players"). So the vector's messages do not
  show a random event.
- **A comet in the recorded stream (inferred).** In year 11 (2476), HE's
  planet 10 went from concentrations 94/53/25 to 170/145/119, its
  environment from 95/67/1 to 91/72/1, and its surface minerals from
  9/6/8 to 319/300/1159 (MEASURED). That fits a comet strike. "Comet" is
  inferred, because no message names the event. The 3700 and 1490
  streams left the planet unchanged, so the planet's expectation is
  flagged `sample: true`.
- **Comet-like strikes only in other streams (MEASURED).** In year 4's
  1490 stream, planet 115 (WM) went from 8/73/64 to 70/73/162. In year 9's
  3700 stream, planet 109 (WM) went from 55/13/97 to 153/112/160. Neither
  happened in the recorded stream, so the vector has no expectation for
  them. An engine on its own stream may produce such a strike in any year.
- **The Mystery Trader is absent from the recorded stream (MEASURED).**
  It does appear elsewhere from the same starts: in year 2 at 3700, year 4
  in the planning stream, year 6 at 1490 and year 7 at 3700, and in every
  warm-up year from 2450 to 2464 (apparatus `evidence/rg004`, the
  `type=trader` object in those dumps). An engine on its own stream may
  spawn one. No expectation depends on the Trader: the vector has no
  Trader object and no Trader message, and every player's Trader items
  list is empty from the start.

## Building

`python3 tools/vectors/build.py rg004 <dir named rg004> vectors/rg`, with
the directory a link to apparatus `evidence/rg004/run`
(`vectors/README.md`). The 9 message expectations rebuild only with a
local `stars.exe`.
