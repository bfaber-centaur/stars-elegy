#!/usr/bin/env python3
"""Write the ES-001 Combat Lab spec (client estimates, docs/ESTIMATES.md).

One pinned generation 2400 -> 2401 of the Combat Lab universe gives
player 0 fleets with multi-leg routes, planets with production queues,
a research field and planets of different habitability. The client's
estimates for the 2401 state are then read from the original client's
screens (docs/ORACLE.md "Client estimates") and compared with
experiments/es001/predict.py, which computes them from the 2401 host
file with the public rules (experiments/es001/estimates.py).

  python3 experiments/es001/gen.py OUTDIR      # OUTDIR/es001.spec
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estimates as E

XY = {0: (1045, 1291), 1: (1071, 1087), 2: (1090, 1295), 3: (1129, 1265), 4: (1143, 1103),
      5: (1146, 1180), 6: (1166, 1017), 7: (1166, 1382), 8: (1169, 1145), 9: (1208, 1297),
      10: (1224, 1359), 11: (1243, 1123), 12: (1245, 1158), 13: (1249, 1354), 14: (1268, 1317),
      15: (1281, 1064), 16: (1284, 1383), 17: (1306, 1060), 18: (1324, 1192), 19: (1342, 1123),
      20: (1348, 1290), 21: (1359, 1121), 22: (1368, 1292), 23: (1380, 1295)}

# player 0's tech: every part below is within it (designs above the owner's
# tech are stripped by the game, docs/ORACLE.md); weapons is researched
TECH = dict(energy=7, weapons=4, prop=26, con=7, elec=9, bio=4)

# ship designs (at most 16): one Scout per engine for "Est. Range", freighters
SCOUT_ENGINES = ["Quick Jump 5", "Fuel Mizer", "Long Hump 6", "Daddy Long Legs 7", "Alpha Drive 8",
                 "Trans-Galactic Drive", "Interspace-10", "Enigma Pulsar", "Trans-Star 10",
                 "Settler's Delight", "Sub-Galactic Fuel Scoop", "Trans-Galactic Mizer Scoop",
                 "Galaxy Scoop"]
lines = ['# ES-001: client estimates (experiments/es001/gen.py)']
lines += ['tech 0 %s %d' % kv for kv in TECH.items()]
lines += ['research 0 10', 'field 0 weapons']
D = {}
for i, e in enumerate(SCOUT_ENGINES):
    lines.append('design 0 %d Scout, 1 %s, empty, empty = R-%s' % (i, e, e.split()[0][:8]))
    D[e] = i
MF = len(D)
lines.append('design 0 %d Medium Freighter, 1 Quick Jump 5, empty, empty = Hauler' % MF)
FT = MF + 1
lines.append('design 0 %d Fuel Transport, 1 Long Hump 6, empty = Tanker' % FT)
SK = FT + 1
lines.append('design 0 %d Scout, 1 Sub-Galactic Fuel Scoop, 1 Rhino Scanner, empty = Scoop' % SK)
assert SK < 16

fid = [0]


def fleet(at, ships, legs, fuel, cargo=None, planet=None):
    """A fleet whose first order is a zero-length leg at its own position,
    so the generation consumes that leg and leaves the rest as orders."""
    s = 'fleet 0 %d ' % fid[0] + ('planet %d ' % planet if planet is not None else '')
    s += 'at %d %d ships %s fuel %d' % (at[0], at[1], ships, fuel)
    if cargo:
        s += ' cargo %d %d %d %d' % cargo
    s += ' to %d %d warp 5' % at
    for leg in legs:
        s += ' to ' + leg
    lines.append(s)
    fid[0] += 1


# ---- travel time and fuel (Fleet Waypoints tile, fleet report)
fleet((1020, 1230), '%d:3' % MF, ['1040 1250 warp 5', '1040 1300 warp 6', '1070 1330 warp 4'], 400,
      cargo=(300, 0, 0, 0))                                    # E1 heavy, multi-year legs
fleet((1100, 1230), '%d:1' % D['Long Hump 6'], ['1130 1230 warp 0', '1150 1230 warp 6'], 50)
fleet((1100, 1260), '%d:1' % D['Quick Jump 5'], ['1103 1262 warp 1', '1103 1262 warp 5', '1160 1262 warp 7'], 50)
fleet((1020, 1030), '%d:2,%d:1' % (MF, SK), ['1120 1030 warp 5', '1120 1130 warp 6'], 300,
      cargo=(100, 0, 0, 0))                                    # E5 ram-scoop gain over 4 years
fleet((1020, 1100), '%d:1,%d:1' % (FT, MF), ['1170 1100 warp 6', '1170 1200 warp 7'], 300)   # E5 fuel transport
fleet((1250, 1020), '%d:1' % MF, ['1306 1060 planet 17 warp 7', '1390 1010 warp 8', '1390 1210 warp 9'], 200)  # E6 dock
fleet((1200, 1390), '%d:1' % D['Alpha Drive 8'], ['1390 1390 warp 9', '1390 1200 warp 8'], 30)             # E7 red
fleet((1050, 1160), '%d:1' % D['Long Hump 6'], ['1075 1165 warp 5', '1100 1165 warp 5'], 50)               # D = 25.5
fleet((1060, 1380), '%d:1' % D['Settler\'s Delight'], ['1110 1380 warp 3', '1200 1380 warp 6'], 20)      # free engine
# ---- Est. Range: every Scout, in deep space, part-filled tanks
for k, e in enumerate(SCOUT_ENGINES):
    x, y = 1030 + 25 * k, 1340
    lines.append('fleet 0 %d at %d %d ships %d:1 fuel %d' % (fid[0], x, y, D[e], 23 + k))
    fid[0] += 1
lines.append('fleet 0 %d at 1030 1060 ships %d:2,%d:1 fuel 333 cargo 150 0 0 0' % (fid[0], MF, SK))
fid[0] += 1

# ---- planets: production estimates, population, value
# (planet, pop, settings, queue)
P = [
    (15, 200, 'mines=20 factories=20 fe=500 bo=500 ge=500 conc=60,60,60 env=50,50,50',
     '7:200:1'),                                               # factories, resource-limited
    (19, 400, 'mines=10 factories=40 fe=300 bo=300 ge=10 conc=50,50,1 env=50,50,50',
     '8:20:1,7:100:1'),                                        # Ge-limited factories
    (21, 100, 'mines=0 factories=10 fe=100 bo=100 ge=0 conc=40,40,1 env=50,50,50',
     '7:5:1,8:3:1'),                                           # factory with no Ge: never
    (11, 700, 'mines=10 factories=10 fe=3000 bo=3000 ge=3000 conc=30,30,30 env=34,50,50 orig=34,50,50',
     '0:50:1,2:50:1,8:5:1'),                                   # auto mines, auto defenses
    (12, 300, 'mines=30 factories=30 fe=5 bo=5 ge=5 conc=20,20,20 env=50,50,50',
     '3:1:1,7:10:1,8:5:1'),                                    # alchemy feeding factories
    (18, 300, 'mines=20 factories=20 fe=50 bo=50 ge=50 conc=40,40,40 env=30,50,62 orig=30,50,62',
     '8:5:1,7:3:1,3:1:1'),                                     # alchemy last
    (4, 150, 'mines=15 factories=15 fe=0 bo=0 ge=0 conc=10,10,1 env=50,50,50',
     '1:20:1,8:5:1'),                                          # auto factories, Ge-blocked
    (6, 50, 'mines=0 factories=0 fe=20 bo=20 ge=20 conc=10,10,10 env=95,50,50', 'none'),   # hostile
    (5, 2000, 'mines=10 factories=10 fe=100 bo=100 ge=100 conc=30,30,30 env=17,17,17 orig=17,17,17',
     '7:20:1,8:30:1,9:10:1'),                                  # crowded
]
for n, pop, kv, q in P:
    lines.append('planet %d owner 0 pop %d starbase none' % (n, pop))
    lines.append('planetset %d excess=0 defenses=0 %s' % (n, kv))
    lines.append('queue %d %s' % (n, q))

out = sys.argv[1] if len(sys.argv) > 1 else '.'
os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'es001.spec'), 'w').write('\n'.join(lines) + '\n')
print('wrote', os.path.join(out, 'es001.spec'), '-', fid[0], 'fleets')
