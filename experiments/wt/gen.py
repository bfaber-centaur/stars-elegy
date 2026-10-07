#!/usr/bin/env python3
"""Write the WT (wormholes and Mystery Trader) batch specs and predictions.

  python3 experiments/wt/gen.py OUTDIR      # writes OUTDIR/wt00N.spec
  python3 experiments/wt/gen.py --list      # case table with predictions

Predictions are the objects decomp lane's O-43..O-53 (stars-decomp #21),
restated as behavior and committed before any WT-001..004 run. `alt` is the
competing reading a case rules out. WT-001..003 are deterministic (one
year, one stream; repeated under a second stream as a control). WT-004 is
run once per cycles value in STREAMS and tallied.

Not run in this batch:
- O-45 (stability names) is a wormhole-report UI reading; the oracle reads
  files, not report text.
- O-53 (computer planets trade) needs a computer player in the Combat Lab
  base; lower priority per the decomp.
- The 25th-redraw LEGACY BUG fires about 1% of meetings for a maxed player
  missing one part; 16 streams cannot reach it.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wt import Run, TECH26, WORMHOLE, TRADER, axis_move

# Distinct startup ticks (WT-000 fingerprints; KX-004 map in ORACLE.md)
STREAMS = [20000, 21000, 35000, 11500, 10500, 6000, 5200, 3700, 2260, 1985, 1750, 1490, 1210, 1170, 1155, 1130]

SF2 = '2:2'          # two Super Freighters (player 0 design 2): 5,000 kT fits
MF24 = '0:24'        # 24 Medium Freighters (player 1 design 0): 5,040 kT hold
GIFT = 'ship: one of M.T. Lifeboat (Nubian) 1/4, M.T. Scout 3/8, M.T. Probe 3/8 (Mini Morph)'

RUNS = []


def run(*a, **k):
    r = Run(*a, **k)
    RUNS.append(r)
    return r


# ---------------------------------------------------------------- WT-001 wormhole knowledge and travel; O-47
r = run('WT-001', 'wormhole destination knowledge, what transits, aiming at the Trader (mutual enemies)')
r.extra += 'tech 1 elec 10\n'   # player 1 scouts see unknown ends within R/4 = 50 ly
# A (O-43): both ends known (seen) to both players, destination unknown to both; player 0 transits.
a0, a1 = r.pair((1040, 1040), (1240, 1040), seen=(0x3, 0x3))
r.enter(0, (1040, 1080), a0, (1040, 1040), 9)
r.fleet(1, 1045, 1040, '1:1')                   # player 1 scouts beside each end (seen this year)
r.fleet(1, 1245, 1040, '1:1')
r.case('A1', 'O-43: player 0 scout 40 ly from end 0 (known to both players, destination known to none) at '
       'warp 9, waypoint on the wormhole', 'scout at end 1\'s start position (1240,1040)', 'stays at end 0',
       ('fleetat', 0, 0, 1240, 1040))
r.case('A2', 'O-43: the transit sets the destination mask on both ends for the traveller only',
       'end 0 and end 1 destination mask 0x1; end 1 known mask has bit 0x1', 'destination bit for player 1 too',
       [('worm', 0, 'seen2', 0x1), ('worm', 1, 'seen2', 0x1), ('wormbit', 1, 'seen', 0x1)])
# G (O-43 control): ends player 1 sees this year but nobody transits.
g0, g1 = r.pair((1380, 1380), (1100, 1390))
r.fleet(1, 1375, 1380, '1:1')
r.fleet(1, 1105, 1390, '1:1')
r.case('G', 'O-43: player 1 scouts beside both ends of an unknown pair, no transit',
       'both ends known to player 1 (known mask bit 0x2); destination mask 0 on both',
       'destination known once both ends are seen',
       [('wormbit', 2, 'seen', 0x2), ('wormbit', 3, 'seen', 0x2), ('worm', 2, 'seen2', 0), ('worm', 3, 'seen2', 0)])
# B (O-46): a plain waypoint on a wormhole's position does not transit; a thing waypoint does.
b0, b1 = r.pair((1380, 1220), (1200, 1240))
r.fleet(0, 1350, 1220, '0:1', fuel=200, extra='to 1380 1220 warp 6')
r.case('B1', 'O-46: scout 30 ly from end 4 with a plain waypoint at its position, warp 6',
       'scout at (1380,1220) in normal space', 'scout at end 5\'s start (1200,1240)', ('fleetat', 0, 1, 1380, 1220))
r.enter(0, (1380, 1190), b0, (1380, 1220), 6)
r.case('B2', 'O-46: scout 30 ly from end 4 with a waypoint on the wormhole, warp 6',
       'scout at end 5\'s start position (1200,1240)', 'stays at (1380,1220)', ('fleetat', 0, 2, 1200, 1240))
# C (O-46): passing over a wormhole mid-move does not transit.
c0, c1 = r.pair((1030, 1150), (1300, 1350))
r.fleet(0, 1010, 1150, '0:1', fuel=200, extra='to 1070 1150 warp 8')
r.case('C', 'O-46: scout flies 60 ly east along y=1150 over end 6 (20 ly along its path), plain waypoint',
       'scout at (1070,1150)', 'scout at end 7 (1300,1350)', ('fleetat', 0, 3, 1070, 1150))
# D (O-46 / 5.7): a packet ending its move on a wormhole stays in normal space.
d0, d1 = r.pair((1166, 1270), (1390, 1160))
r.lines.append('thing packet 0 0 1166 1370 6 10 1000 0 0')
r.case('D', '5.7: player 0 warp-10 packet from (1166,1370) toward planet 6 (1166,1017); end 8 sits at its '
       '100 ly point (1166,1270)', 'packet near (1166,1270) (within 1 ly), not near end 9 (1390,1160)',
       'packet at end 9', ('packetat', 0, 0, 1166, 1270))
# E (5.7): the Trader ending its move on a wormhole stays in normal space.
e0, e1 = r.pair((1264, 1100), (1050, 1390))
r.trader((1200, 1100), (1395, 1100), 8)
r.case('E', '5.7: Trader 0 at (1200,1100) heading east at warp 8 ends its 64 ly move on end 10 (1264,1100)',
       'Trader 0 at (1264,1100), destination unchanged', 'Trader at end 11 (1050,1390)',
       ('trader', 0, 1264, 1100, None))
# F (O-47): aiming at the Trader reaches its start-of-year position.
r.trader((1200, 1300), (1395, 1300), 9)
# Setup fix after the first WT-001 run: from 60 ly at warp 9 the loaded freighters ran dry after 8 ly.
r.fleet(0, 1170, 1300, SF2, fuel=2000, extra='cargo 5000 0 0 0 to 1200 1300 thing %#x warp 6' % (TRADER | 1))
r.case('F1', 'O-47: player 0 fleet with 5000 kT 30 ly west of Trader 1 (heading east, warp 9), waypoint on '
       'the Trader, warp 6', 'fleet at (1200,1300), kept with its cargo; no trade',
       'fleet follows the Trader to (1281,1300) and trades', [('fleetat', 0, 4, 1200, 1300), ('cargo', 0, 4, 5000)])
r.meet(1, axis_move((1200, 1300), (1395, 1300), 9), 20, 5, MF24, '5000 0 0 0')
r.case('F2', 'O-47: player 1 fleet with 5000 kT flying onto (1281,1300), Trader 1\'s end point',
       'fleet consumed; Trader 1 at (1281,1300) with met mask 0x2; player 1 gains 6 levels in total',
       'no trade', [('gone', 1, 4), ('trader', 1, 1281, 1300, 0x2), ('techgain', 1, 6)])

# ---------------------------------------------------------------- WT-002 research gifts (O-50, O-52)
T50 = ''.join('tech 0 %s 26\n' % f for f in ('energy', 'weapons', 'prop', 'con', 'elec')) + 'tech 0 bio 0\n'
T52 = ''.join('tech 1 %s 5\n' % f for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio'))
r = run('WT-002', 'Trader research gifts: one step keeps accumulated research; an owned part becomes research',
        tech=T50, extra=T52 + 'accum 0 bio 20\nfield 0 energy\nmt 1 0x0040\n')
r.trader((1100, 1200), (1395, 1200), 8, item=0)
r.meet(0, axis_move((1100, 1200), (1395, 1200), 8), 20, 5, SF2, '5000 0 0 0')
r.case('A', 'O-50: player 0 at 26 in five fields and 0 in biotech with 20 accumulated in biotech, research 0%, '
       'field energy; 5000 kT to Trader 0 (item 0)',
       'biotech 0 -> 1, biotech accumulated research still 20, other fields 26; message 0x109',
       '40 (doubled kept) or 0 (cleared)',
       [('gone', 0, 0), ('tech', 0, [26, 26, 26, 26, 26, 1]), ('accum', 0, 5, 20), ('msg', 0, 0x109)])
r.trader((1100, 1350), (1395, 1350), 8, item=0x40)
r.meet(1, axis_move((1100, 1350), (1395, 1350), 8), 20, 5, '0:36', '7400 0 0 0')
r.case('B', 'O-52: player 1 at tech 5 everywhere owning the Anti Matter Torpedo (mt 0x40); 7400 kT to Trader 1 '
       'offering it', 'research: exactly 8 levels in total (sum 30 -> 38); mt still 0x0040; message 0x109',
       'a part, or another level count',
       [('gone', 1, 0), ('techgain', 1, 8), ('mt', 1, 0x0040), ('msg', 1, 0x109)])

# ---------------------------------------------------------------- WT-003 part bits (O-48) and a full design table (O-49)
PARTS = ['Multi Cargo Pod', 'Multi Function Pod', 'Langston Shell', 'Mega Poly Shell', 'Alien Miner',
         'Hush-a-Boom', 'Anti Matter Torpedo', 'Multi Contained Munition', 'Mini Morph', 'Enigma Pulsar',
         'Genesis Device', 'Jump Gate']
MSG = {8: 0x10c, 10: 0x10f}
D16 = ''.join('design 1 %d Scout, 1 Long Hump 6, empty, empty = Scout %d\n' % (n, n) for n in range(2, 16))
r = run('WT-003', 'Trader part bits and a full design table', extra=D16)
for b in range(12):
    y = 1030 + 30 * b
    r.trader((1050, y), (1395, y), 8, item=1 << b)
    r.meet(0, axis_move((1050, y), (1395, y), 8), 20, 5, SF2, '5000 0 0 0')
    r.case('A%02d' % b, 'O-48: player 0 (mt 0) trades 5000 kT with Trader %d offering bit %d' % (b, b),
           'part %s: bit 0x%04x added; tech unchanged; message %#x' % (PARTS[b], 1 << b, MSG.get(b, 0x10b)),
           'research or another part', [('gone', 0, b), ('msg', 0, MSG.get(b, 0x10b))])
r.case('A', 'O-48: all twelve trades together', 'player 0 mt 0x0fff, tech 26 everywhere',
       '', [('mt', 0, 0x0fff), ('tech', 0, [26] * 6)])
r.trader((1250, 1100), (1395, 1100), 8, item=0x1000)
r.meet(1, axis_move((1250, 1100), (1395, 1100), 8), 20, 5, MF24, '5000 0 0 0')
r.case('B', 'O-49: player 1 with all 16 design slots used trades 5000 kT with Trader 12 offering a ship',
       'fleet consumed; no new fleet or design; mt unchanged; message 0x150', 'a ship',
       [('gone', 1, 0), ('nonew', 1), ('designs', 1, 16), ('mt', 1, 0), ('msg', 1, 0x150)])

# ---------------------------------------------------------------- WT-004 jumps (O-44), ship gifts (O-49, O-51)
r = run('WT-004', 'wormhole jumps keep destination knowledge; ship gifts (one run per stream)',
        extra='mt 0 0x0fff\nplanet 17 scanner none\n')
n = 0
for x in (1040, 1120, 1200, 1280, 1360):
    for y0 in (1030, 1230):
        r.pair((x, y0), (x, y0 + 100), cls=(2, 2), years=(30, 30), seen=(0x1, 0x1), seen2=(0x1, 0x1))
        n += 2
r.case('A', 'O-44: ten class-2 pairs at 30 years (6%/year), known to player 0 with known destination',
       'each end either jiggles (each axis within 12 ly; years 31; known and destination bit 0x1) or jumps '
       '(years 0; known bit 0x1 cleared; destination bit 0x1 kept)', 'a jump clears the destination mask',
       ('jumps', n))
r.trader((1010, 1175), (1395, 1175), 8)
r.meet(0, axis_move((1010, 1175), (1395, 1175), 8), 20, 5, SF2, '5000 0 0 0')
r.case('B', 'O-51: player 0 at tech 26 owning all twelve parts trades 5000 kT with Trader 0 (item 0)',
       'nothing (message 0x10e) 1/5, else ' + GIFT + '; mt unchanged', 'research or a part',
       ('gift', 0, 0, 4, 0x0fff))
r.trader((1010, 1290), (1395, 1290), 8, item=0x1000)
r.meet(1, axis_move((1010, 1290), (1395, 1290), 8), 20, 5, MF24, '5000 0 0 0')
r.case('C', 'O-49: player 1 (tech 3, 2 designs) trades 5000 kT with Trader 1 offering a ship (year index 0)',
       GIFT + ' in design slot 2; 1 ship 2/3 or 2 ships 1/3, plus 0..count more for the Mini Morphs '
       '(objects.py mtmeet); new fleet at the trade point with full fuel; mt unchanged',
       'no ship, or a ship elsewhere', ('gift', 1, 0, 2, 0))


# ---------------------------------------------------------------- WT-005 follow-up on O-47 (after WT-001)
# WT-001-F1 (fixed setup) ended at (1206,1300): 36 ly east at warp 6, past the Trader's start (1200,1300),
# i.e. toward its end point (1281,1300). This run discriminates the two readings.
r = run('WT-005', 'aiming at a moving Trader (follow-up to WT-001-F1)')
r.trader((1200, 1300), (1395, 1300), 9)
r.fleet(0, 1250, 1300, SF2, fuel=2000, extra='cargo 5000 0 0 0 to 1200 1300 thing %#x warp 6' % TRADER)
r.case('A', 'player 0 fleet with 5000 kT 50 ly east of Trader 0\'s start (heading east, warp 9), waypoint on the '
       'Trader, warp 6 (36 ly)', 'flies 31 ly to the Trader\'s end point (1281,1300) and trades: consumed; '
       'Trader met mask 0x1', 'flies 36 ly west toward the start (1214,1300), kept (O-47)',
       [('gone', 0, 0), ('trader', 0, 1281, 1300, 0x1)])
r.fleet(1, 1170, 1300, MF24, fuel=2000, extra='cargo 5000 0 0 0 to 1200 1300 thing %#x warp 6' % TRADER)
r.case('B', 'WT-001-F1 repeated by player 1: 30 ly west of the start, waypoint on the Trader, warp 6',
       'moves 36 ly east to (1206,1300), kept', 'stops at (1200,1300)', [('fleetat', 1, 0, 1206, 1300)])

def table():
    out = []
    for r in RUNS:
        out.append('\n### %s: %s\n' % (r.rid, r.title))
        out.append('| Case | Setup | Predicted | Rules out |')
        out.append('|---|---|---|---|')
        for c in r.cases:
            out.append('| %s | %s | %s | %s |' % (c['id'], c['what'], c['prediction'], c['alt']))
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    if sys.argv[1:] == ['--list']:
        print(table())
    else:
        out = sys.argv[1] if len(sys.argv) > 1 else '.'
        for r in RUNS:
            open(os.path.join(out, r.rid.lower().replace('-', '') + '.spec'), 'w').write(r.spec())
        print('wrote %d specs to %s' % (len(RUNS), out))
