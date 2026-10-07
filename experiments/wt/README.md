# WT: wormholes and Mystery Trader corpus

Oracle tooling for the wormhole and Mystery Trader rules in
`docs/OBJECTS.md` (open experiments 2 and 3: jump odds, what a jump does to
fleets heading for a wormhole, Trader spawn, path and rewards). Predictions
come from the objects decomp lane and are committed here before any WT run
they describe. WT-000 is a tooling smoke run with no predictions.

## Tools

| Tool | What it does |
|---|---|
| `wt.py` | Spec helpers on top of Combat Lab: `pair` (two wormhole ends with chosen positions, class 0–3, years since the last jump and the two player masks), `enter` (a fleet whose waypoint 1 is a wormhole), `trader` (a Trader at a point heading for a destination at a warp), `meet` (a cargo fleet staged to fly onto the Trader's end point), `axis_move` (the OB-004 axis-aligned Trader step, for staging only). |
| `smoke.py` | Writes `wt000.spec` (WT-000). |
| `tools/fleetlab/years` | Generates N pinned years in a row from one start: `years START BASE OUT N [CYCLES] [STEP]`, one `OUT/yK` per year. |
| `trace.py` | Reads a `years` output (or pinned-turn outputs in order) and prints each year: player tech and Trader item mask; every wormhole end with its move since the year before; every Trader with its move, destination, warp and raw words; every fleet with position, ships, damage, cargo and fuel. `--json` gives the same as data. |
| `combatlab` `thing` lines | Wormholes and Traders gain `w14`/`w16` and `w10`/`w16` tokens (hex) for setting their raw words. A Trader's `w10` token replaces the whole word, warp included. |

```sh
python3 experiments/wt/smoke.py OUT
tools/fleetlab/combatlab build BASE/CB.HST OUT/wt000.spec OUT/wt000.HST
tools/fleetlab/years OUT/wt000.HST BASE OUT/wt000 3 20000 1000
python3 experiments/wt/trace.py OUT/wt000
```

## Random streams across years

Every pinned year starts a fresh DOSBox, and the stream depends on the
cycles value. With the same cycles every year (`STEP 0`), each year replays
the same draws. In WT-000 both class-0 ends moved by the same vector three
years running, (+2,−5) and (−8,+9). `trace.py` flags such a year
`SAME STREAM?`.

Different cycles values do not always give different streams. Year 1 of
WT-000, fingerprinted by wormhole 0's first move, fell into a few classes:

| Stream (wormhole 0, wormhole 3 first moves) | Cycles values |
|---|---|
| (+2,−5), (−3,−9) | 20000, 21500, 22000, 24000, 25000, 27000, 28000, 29000, 33000 |
| (+2,−2), (−7,+7) | 20100, 20200, 20300, 20500, 20700, 23000; 21000 (from year 2 of `wt000s`) |
| (−3,−7), (−7,+2) | 26000, 31000, 35000, 45000 |

That is 3 streams from 21 values between 20000 and 45000. It fits the
KX-004 cycles-to-tick map (stars-elegy #44, ORACLE.md): the startup tick
is about trunc(k·54.925) ms with k ≈ 70000/cycles. So sampling jump odds
needs a sweep down to low cycles, as in `experiments/kx004/sweep.sh`,
rather than nearby values.

For a multi-year chain, pass a CYCLES list whose consecutive values fall in
different classes, for example `20000,21000,26000`.

## WT-000 smoke run (observed, no predictions)

Raw evidence: stars-oracle-apparatus `evidence/wt/wt000`, `wt000s` (cycles
20000, 21000, 22000) and `fp*` (year 1 fingerprints).

- The wormhole helpers placed the pairs as written. Both ends of each pair
  became known to player 0 (seen and seen2 `0001`) when its fleet transited.
- The scout 30 ly from wormhole 0 at warp 6 ended year 1 on wormhole 1's
  start position (1290,1240), as in OB-005-C.
- Two Laser DDs with damage 100/50% transited a class-3 end at 200 years.
  They ended on the partner's start position (1360,1040), damage 95, then
  85 and 75. That is consistent with repair after transit and no transit
  damage.
- The class-3, 200-year ends did not jump in 3 years. The streams were
  20000 ×3, and 20000/21000/22000.
- Trader 0, heading east at warp 8 from (1010,1210), moved +64 ly a year.
  Its `w10` went from 0008 to 0018 after the first move, and its `w16`
  counted 0, 1, 2 in the files after years 1–3.
- Trader 1, heading for (1005,1390) from (1395,1010) at warp 9, moved
  (−58,+57), (−58,+56), (−58,+57).
- Player 1's 24 freighters with 5000 kT flew 20 ly onto Trader 0's end
  point. The fleet was removed, the Trader's met mask became `0002`, and
  player 1's tech went from 3 everywhere to 5,6,3,3,4,3 (+6 levels in
  total, as in OB-004-D).

## Batch WT-001..004: predictions

These predictions are from stars-decomp #21 (commit f1daf60,
`objects.md` §5b, O-43..O-53), restated as behavior. They were committed
before any WT-001..004 run. Outcome sets come from the decomp's
`objects.py mtmeet`. `gen.py --list` prints the same table.

- WT-001..003 are deterministic. Each runs at cycles 20000 and again at
  26000 as a control.
- WT-004 runs once per value in `gen.STREAMS`: 16 cycles values with
  distinct startup ticks.
- Not run:
  - O-45, stability names: it is a report-text reading.
  - O-53, computer planets: there is no computer player in the Combat Lab
    base.
  - The 25th-redraw LEGACY BUG: about 1% of meetings for a maxed player
    missing one part, which 16 streams cannot reach.
- Message checks are byte matches in the player file's event block, whose
  record layout is not decoded.
- In WT-001, player 1 has electronics 10, so its JOAT scouts see unknown
  ends within R/4 = 50 ly. The F2 research gift is still 6 levels in every
  `mtmeet` outcome for tech 3,3,3,3,10,3.
- In WT-004 the O-49 outcome set is (`mtmeet --item 0x1000 --year 0`):

  | Gift | Ships | Probability |
  |---|---|---|
  | Lifeboat | 1 | 1/6 |
  | Lifeboat | 2 | 1/12 |
  | Scout or Probe, each | 1 | 1/8 |
  | Scout or Probe, each | 2 | 1/6 |
  | Scout or Probe, each | 3 | 1/24 |
  | Scout or Probe, each | 4 | 1/24 |

- O-51 adds "nothing" with 1/5 and scales the rest by 4/5.
- A jiggling end keeps its known bit. Only a jump clears it (O-30).

### WT-001: wormhole destination knowledge, what transits, aiming at the Trader (mutual enemies)

| Case | Setup | Predicted | Rules out |
|---|---|---|---|
| WT-001-A1 | O-43: player 0 scout 40 ly from end 0 (known to both players, destination known to none) at warp 9, waypoint on the wormhole | scout at end 1's start position (1240,1040) | stays at end 0 |
| WT-001-A2 | O-43: the transit sets the destination mask on both ends for the traveller only | end 0 and end 1 destination mask 0x1; end 1 known mask has bit 0x1 | destination bit for player 1 too |
| WT-001-G | O-43: player 1 scouts beside both ends of an unknown pair, no transit | both ends known to player 1 (known mask bit 0x2); destination mask 0 on both | destination known once both ends are seen |
| WT-001-B1 | O-46: scout 30 ly from end 4 with a plain waypoint at its position, warp 6 | scout at (1380,1220) in normal space | scout at end 5's start (1200,1240) |
| WT-001-B2 | O-46: scout 30 ly from end 4 with a waypoint on the wormhole, warp 6 | scout at end 5's start position (1200,1240) | stays at (1380,1220) |
| WT-001-C | O-46: scout flies 60 ly east along y=1150 over end 6 (20 ly along its path), plain waypoint | scout at (1070,1150) | scout at end 7 (1300,1350) |
| WT-001-D | 5.7: player 0 warp-10 packet from (1166,1370) toward planet 6 (1166,1017); end 8 sits at its 100 ly point (1166,1270) | packet near (1166,1270) (within 1 ly), not near end 9 (1390,1160) | packet at end 9 |
| WT-001-E | 5.7: Trader 0 at (1200,1100) heading east at warp 8 ends its 64 ly move on end 10 (1264,1100) | Trader 0 at (1264,1100), destination unchanged | Trader at end 11 (1050,1390) |
| WT-001-F1 | O-47: player 0 fleet with 5000 kT 60 ly west of Trader 1 (heading east, warp 9), waypoint on the Trader, warp 9 | fleet at (1200,1300), kept with its cargo; no trade | fleet follows the Trader to (1281,1300) and trades |
| WT-001-F2 | O-47: player 1 fleet with 5000 kT flying onto (1281,1300), Trader 1's end point | fleet consumed; Trader 1 at (1281,1300) with met mask 0x2; player 1 gains 6 levels in total | no trade |

### WT-002: Trader research gifts: one step keeps accumulated research; an owned part becomes research

| Case | Setup | Predicted | Rules out |
|---|---|---|---|
| WT-002-A | O-50: player 0 at 26 in five fields and 0 in biotech with 20 accumulated in biotech, research 0%, field energy; 5000 kT to Trader 0 (item 0) | biotech 0 -> 1, biotech accumulated research still 20, other fields 26; message 0x109 | 40 (doubled kept) or 0 (cleared) |
| WT-002-B | O-52: player 1 at tech 5 everywhere owning the Anti Matter Torpedo (mt 0x40); 7400 kT to Trader 1 offering it | research: exactly 8 levels in total (sum 30 -> 38); mt still 0x0040; message 0x109 | a part, or another level count |

### WT-003: Trader part bits and a full design table

| Case | Setup | Predicted | Rules out |
|---|---|---|---|
| WT-003-A00 | O-48: player 0 (mt 0) trades 5000 kT with Trader 0 offering bit 0 | part Multi Cargo Pod: bit 0x0001 added; tech unchanged; message 0x10b | research or another part |
| WT-003-A01 | O-48: player 0 (mt 0) trades 5000 kT with Trader 1 offering bit 1 | part Multi Function Pod: bit 0x0002 added; tech unchanged; message 0x10b | research or another part |
| WT-003-A02 | O-48: player 0 (mt 0) trades 5000 kT with Trader 2 offering bit 2 | part Langston Shell: bit 0x0004 added; tech unchanged; message 0x10b | research or another part |
| WT-003-A03 | O-48: player 0 (mt 0) trades 5000 kT with Trader 3 offering bit 3 | part Mega Poly Shell: bit 0x0008 added; tech unchanged; message 0x10b | research or another part |
| WT-003-A04 | O-48: player 0 (mt 0) trades 5000 kT with Trader 4 offering bit 4 | part Alien Miner: bit 0x0010 added; tech unchanged; message 0x10b | research or another part |
| WT-003-A05 | O-48: player 0 (mt 0) trades 5000 kT with Trader 5 offering bit 5 | part Hush-a-Boom: bit 0x0020 added; tech unchanged; message 0x10b | research or another part |
| WT-003-A06 | O-48: player 0 (mt 0) trades 5000 kT with Trader 6 offering bit 6 | part Anti Matter Torpedo: bit 0x0040 added; tech unchanged; message 0x10b | research or another part |
| WT-003-A07 | O-48: player 0 (mt 0) trades 5000 kT with Trader 7 offering bit 7 | part Multi Contained Munition: bit 0x0080 added; tech unchanged; message 0x10b | research or another part |
| WT-003-A08 | O-48: player 0 (mt 0) trades 5000 kT with Trader 8 offering bit 8 | part Mini Morph: bit 0x0100 added; tech unchanged; message 0x10c | research or another part |
| WT-003-A09 | O-48: player 0 (mt 0) trades 5000 kT with Trader 9 offering bit 9 | part Enigma Pulsar: bit 0x0200 added; tech unchanged; message 0x10b | research or another part |
| WT-003-A10 | O-48: player 0 (mt 0) trades 5000 kT with Trader 10 offering bit 10 | part Genesis Device: bit 0x0400 added; tech unchanged; message 0x10f | research or another part |
| WT-003-A11 | O-48: player 0 (mt 0) trades 5000 kT with Trader 11 offering bit 11 | part Jump Gate: bit 0x0800 added; tech unchanged; message 0x10b | research or another part |
| WT-003-A | O-48: all twelve trades together | player 0 mt 0x0fff, tech 26 everywhere |  |
| WT-003-B | O-49: player 1 with all 16 design slots used trades 5000 kT with Trader 12 offering a ship | fleet consumed; no new fleet or design; mt unchanged; message 0x150 | a ship |

### WT-004: wormhole jumps keep destination knowledge; ship gifts (one run per stream)

| Case | Setup | Predicted | Rules out |
|---|---|---|---|
| WT-004-A | O-44: ten class-2 pairs at 30 years (6%/year), known to player 0 with known destination | each end either jiggles (each axis within 12 ly; years 31; known and destination bit 0x1) or jumps (years 0; known bit 0x1 cleared; destination bit 0x1 kept) | a jump clears the destination mask |
| WT-004-B | O-51: player 0 at tech 26 owning all twelve parts trades 5000 kT with Trader 0 (item 0) | nothing (message 0x10e) 1/5, else ship: one of M.T. Lifeboat (Nubian) 1/4, M.T. Scout 3/8, M.T. Probe 3/8 (Mini Morph); mt unchanged | research or a part |
| WT-004-C | O-49: player 1 (tech 3, 2 designs) trades 5000 kT with Trader 1 offering a ship (year index 0) | ship: one of M.T. Lifeboat (Nubian) 1/4, M.T. Scout 3/8, M.T. Probe 3/8 (Mini Morph) in design slot 2; 1 ship 2/3 or 2 ships 1/3, plus 0..count more for the Mini Morphs (objects.py mtmeet); new fleet at the trade point with full fuel; mt unchanged | no ship, or a ship elsewhere |


## WT-005: follow-up predictions

These were committed after WT-001..003 ran and before WT-005 ran.

- **WT-001-F1 setup fix.** As first written, the fleet started 60 ly away
  at warp 9. The loaded freighters ran dry after 8 ly, so that run says
  nothing about O-47. The fixed case starts 30 ly away at warp 6.
- **What the fixed case showed.** The fleet ended at (1206,1300). It flew
  its full 36 ly east, past the Trader's start (1200,1300), toward the
  Trader's end point (1281,1300). WT-005 tells the two readings apart.
### WT-005: aiming at a moving Trader (follow-up to WT-001-F1)

| Case | Setup | Predicted | Rules out |
|---|---|---|---|
| WT-005-A | player 0 fleet with 5000 kT 50 ly east of Trader 0's start (heading east, warp 9), waypoint on the Trader, warp 6 (36 ly) | flies 31 ly to the Trader's end point (1281,1300) and trades: consumed; Trader met mask 0x1 | flies 36 ly west toward the start (1214,1300), kept (O-47) |
| WT-005-B | WT-001-F1 repeated by player 1: 30 ly west of the start, waypoint on the Trader, warp 6 | moves 36 ly east to (1206,1300), kept | stops at (1200,1300) |


## Results

Raw `check.py` output: apparatus `evidence/wt/batch/check.out`. The full
record is in PARITY.md "Universe objects" → "Wormholes and Mystery Trader,
round 2".

**Held:**
- O-43: WT-001 A1, A2, G.
- O-44: 18 of 18 jumps kept the destination bit.
- O-46: WT-001 B1, B2, C, D, E.
- O-48: WT-003 A00–A11 and A at cycles 20000.
- O-49: WT-003 B, and WT-004 C over 15 streams.
- O-50: WT-002 A.
- O-51: WT-004 B over 15 streams; 3 gave nothing.
- O-52: WT-002 B.

Two message checks first failed because the checker matched the whole
header word. 0x109 was written as `09 03`, with a flag bit above the 9-bit
id. The check was fixed to match the id bits only; the game's output was
unchanged.

**Missed:**
- **O-47.** A fleet aimed at the Trader flies toward the Trader's position
  after the Trader moves, not toward its start-of-year position.
  - WT-001 F1 (fixed setup) ended at (1206,1300).
  - WT-005 A traded at the Trader's end point (1281,1300). This was
    predicted after F1.
- **O-44, known bit.** 4 of the 18 jumped ends still had player 0's
  known bit. Each was in player 0's file, 21–107 ly from the M.T. ship
  player 0 received that year, so it was seen again after the jump
  (PARITY.md). That makes them a scanning observation, not a jump-rule
  miss.

**Void (the Trader's yearly warp bump moved it off the staged point):**
- WT-003 at cycles 26000: Traders 11 and 12 (A11, A, B).
- WT-004 C at 1490 and B at 1155.
