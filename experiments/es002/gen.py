#!/usr/bin/env python3
"""Write the ES-002 Combat Lab spec: the client estimates ES-001 left
BINARY-ONLY (docs/ESTIMATES.md).

  - stargate legs: a usable gate, cargo, range and mass danger, an own
    planet without a gate, another player's planet, deep space, an
    unowned planet, a source planet without a gate;
  - "Skipped": automatic items with nothing to do;
  - Generalized Research: player 0 has GR (with No Ram Scoop Engines,
    Cheap Engines, Only Basic Remote Mining, Low Starting Population and
    Bleeding Edge Tech to keep the race legal, docs/ORACLE.md);
  - a field at level 26: player 1's energy reaches 26 this year with
    "next field" left at "same field" (KERNEL.md, KX-005 R3: research
    moves to the lowest field, weapons here); its research dialog then
    shows weapons, and selecting energy should read "Maxed Out";
  - leg distances whose hundredths have a leading zero (20.02 -> "20.2"?).

As in ES-001 every fleet's first order is a zero-length leg, so the
generation leaves the other legs (gate legs included) as orders.

  python3 experiments/es002/gen.py OUTDIR      # OUTDIR/es002.spec, OUTDIR/expect.tsv
"""
import os, sys

XY = {0: (1045, 1291), 1: (1071, 1087), 2: (1090, 1295), 3: (1129, 1265), 4: (1143, 1103),
      5: (1146, 1180), 6: (1166, 1017), 7: (1166, 1382), 8: (1169, 1145), 9: (1208, 1297),
      10: (1224, 1359), 11: (1243, 1123), 12: (1245, 1158), 13: (1249, 1354), 14: (1268, 1317),
      15: (1281, 1064), 16: (1284, 1383), 17: (1306, 1060), 18: (1324, 1192), 19: (1342, 1123),
      20: (1348, 1290), 21: (1359, 1121), 22: (1368, 1292), 23: (1380, 1295)}
FIELDS = ('energy', 'weapons', 'prop', 'con', 'elec', 'bio')
BASE_COST = [0, 50, 80, 130, 210, 340, 550, 890, 1440, 2330, 3770, 6100, 9870, 13850,
             18040, 22440, 27050, 31870, 36900, 42140, 47590, 53250, 59120, 65200,
             71490, 77990, 84700]

lines = ['# ES-002: client estimates, BINARY-ONLY follow-up (experiments/es002/gen.py)']
T0 = dict(energy=7, weapons=4, prop=26, con=7, elec=9, bio=4)
lines += ['tech 0 %s %d' % kv for kv in T0.items()]
lines += ['lrt 0 0x1b90', 'research 0 10', 'field 0 weapons']
# player 1: energy 25 -> 26 this year, everything else 3
T1 = dict(energy=25, weapons=3, prop=3, con=3, elec=3, bio=3)
lines += ['tech 1 %s %d' % kv for kv in T1.items()]
cost26 = BASE_COST[26] + 10 * sum(T1.values())
lines += ['research 1 15', 'field 1 energy', 'accum 1 energy %d' % (cost26 - 10)]

lines += ['design 0 0 Scout, 1 Long Hump 6, empty, empty = Gater',
          'design 0 1 Medium Freighter, 1 Quick Jump 5, empty, empty = Hauler',
          'design 0 2 Medium Freighter, 1 Quick Jump 5, empty, 1 Crobmnium = Heavy']
lines += ['sbdesign 0 0 Space Station, Stargate 100/250, ' + ', '.join(['empty'] * 11) + ' = Gate Station',
          'sbdesign 0 1 Orbital Fort, Stargate 100/250, empty, empty, empty, empty = Gate A',
          'sbdesign 0 2 Orbital Fort, Stargate 150/600, empty, empty, empty, empty = Gate B']

# planets of player 0: starbase design, settings, queue
P = [
    (15, 200, 1, 'mines=20 factories=20 fe=300 bo=300 ge=300 conc=50,50,50 env=50,50,50', 'none'),
    (19, 200, 1, 'mines=20 factories=20 fe=300 bo=300 ge=300 conc=50,50,50 env=50,50,50', 'none'),
    (16, 100, 1, 'mines=10 factories=10 fe=100 bo=100 ge=100 conc=50,50,50 env=50,50,50', 'none'),
    (4, 150, 2, 'mines=15 factories=15 fe=100 bo=100 ge=100 conc=50,50,50 env=50,50,50', 'none'),
    (21, 100, 'none', 'mines=10 factories=10 fe=100 bo=100 ge=100 conc=40,40,40 env=50,50,50', 'none'),
    # Skipped: auto mines with more mines than the population can operate, then a mine
    (18, 300, 'none', 'mines=500 factories=20 fe=50 bo=50 ge=50 conc=40,40,40 env=50,50,50', '0:50:1,8:5:1'),
    # Skipped: auto defenses at the planet's defense limit, then auto factories, then a factory
    (11, 700, 'none', 'mines=10 factories=10 defenses=100 fe=3000 bo=3000 ge=3000 conc=30,30,30 env=50,50,50',
     '2:50:1,1:20:1,7:5:1'),
]
for n, pop, sb, kv, q in P:
    lines.append('planet %d owner 0 pop %d starbase %s' % (n, pop, sb))
    lines.append('planetset %d excess=0 %s' % (n, kv if 'defenses=' in kv else 'defenses=0 ' + kv))
    if q != 'none':
        lines.append('queue %d %s' % (n, q))
lines.append('planet 17 owner 0 pop 250 starbase 0')

fid = [0]


def fleet(planet, at, ships, legs, fuel=50, cargo=None):
    s = 'fleet 0 %d ' % fid[0] + ('planet %d ' % planet if planet is not None else '')
    s += 'at %d %d ships %s fuel %d' % (at[0], at[1], ships, fuel)
    if cargo:
        s += ' cargo %d %d %d %d' % cargo
    s += ' to %d %d warp 5' % at
    for leg in legs:
        s += ' to ' + leg
    lines.append(s)
    fid[0] += 1


def to(n, warp):
    return '%d %d planet %d warp %d' % (XY[n] + (n, warp))


fleet(15, XY[15], '0:1', [to(19, 11), '1342 1150 warp 5'])          # G1 usable gate, then a 27 ly leg
fleet(15, XY[15], '1:1', [to(19, 11)], fuel=100, cargo=(50, 0, 0, 0))  # G2 cargo
fleet(15, XY[15], '0:1', [to(16, 11)])                               # G3 319 ly through a 250 ly gate
fleet(4, XY[4], '2:1', [to(19, 11)], fuel=100)                       # G4 120 kT into a 100 kT gate
fleet(15, XY[15], '0:1', [to(21, 11)])                               # G5 own planet without a gate
fleet(15, XY[15], '0:1', ['1169 1145 planet 8 warp 11'])             # G6 player 1's homeworld
fleet(15, XY[15], '0:1', ['1300 1100 warp 11'])                      # G7 deep space
fleet(15, XY[15], '0:1', [to(12, 11)])                               # G8 unowned planet
fleet(21, XY[21], '0:1', [to(19, 11)])                               # G9 source without a gate
fleet(17, XY[17], '0:1', [to(15, 11), to(19, 11)])                   # G10 two gate legs (Guano's station has a gate)
fleet(None, (1020, 1230), '0:1', ['1040 1231 warp 5', '1050 1232 warp 5', '1053 1233 warp 2',
                                  '1058 1234 warp 3'])               # D1 distances 20.02, 10.05, 3.16, 5.10
fleet(None, (1020, 1260), '0:1', ['1020 1263 warp 2', '1027 1264 warp 3'])   # D2 3.0, 7.07

out = sys.argv[1] if len(sys.argv) > 1 else '.'
os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'es002.spec'), 'w').write('\n'.join(lines) + '\n')
# KERNEL.md (KX-005 R3) prediction for player 1's research after the year
open(os.path.join(out, 'expect.tsv'), 'w').write(
    'case\titem\tprediction\n'
    'K1\tplayer 1 energy level after the year\t26\n'
    'K2\tplayer 1 current field after the year\tweapons (lowest, first in field order)\n'
    'K3\tplayer 1 next-field choice after the year\tsame field\n')
print('wrote', out, fid[0], 'fleets')
