#!/usr/bin/env python3
"""Write the MG- (messages) Combat Lab specs and print their predictions.

The predictions restate the private message reading (stars-decomp
docs/messages-predictions.md M-1..M-10, PR #25) as behavior, before any
MG run. Decode results with tools/fleetlab/events.py.

  python3 experiments/mg/gen.py OUTDIR     # writes OUTDIR/mgNNN.spec
  python3 experiments/mg/gen.py --list     # case table
"""
import os, sys

XY = {0: (1045, 1291), 1: (1071, 1087), 2: (1090, 1295), 3: (1129, 1265), 4: (1143, 1103), 5: (1146, 1180),
      6: (1166, 1017), 7: (1166, 1382), 8: (1169, 1145), 9: (1208, 1297), 10: (1224, 1359), 11: (1243, 1123),
      12: (1245, 1158), 13: (1249, 1354), 14: (1268, 1317), 15: (1281, 1064), 16: (1284, 1383), 17: (1306, 1060),
      18: (1324, 1192), 19: (1342, 1123), 20: (1348, 1290), 21: (1359, 1121), 22: (1368, 1292), 23: (1380, 1295)}
TECH = ''.join('tech %d %s 26\n' % (p, f) for p in (0, 1)
               for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio'))
COMMON = TECH + 'relation 0 1 2\nrelation 1 0 2\nresearch 0 0\nresearch 1 0\n' \
    'design 0 0 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, empty, empty, empty = Laser DD\n' \
    'design 0 1 Scout, 1 Long Hump 6, empty = Scout\n' \
    'design 1 0 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, empty, empty, empty = Laser DD\n' \
    'plan 0 0 4 1 0 0 = Nobody\nplan 1 0 4 1 0 0 = Nobody\n'
PLAIN = 'mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0 excess=0 scanner=31'

RUNS = []


class Run:
    def __init__(self, rid, title, extra=''):
        self.rid, self.title, self.lines, self.cases = rid, title, [COMMON + extra], []
        RUNS.append(self)

    def add(self, s):
        self.lines.append(s if s.endswith('\n') else s + '\n')

    def own(self, n, owner, pop, sb='none', env='50,50,50', extra=''):
        self.add('planet %d owner %d pop %d starbase %s' % (n, owner, pop, sb))
        self.add('planetset %d %s env=%s %s' % (n, PLAIN, env, extra))

    def case(self, cid, pred, setup, expect, alt=''):
        self.cases.append((cid, pred, setup, expect, alt))

    def spec(self):
        return '# %s: %s (experiments/mg/gen.py)\n' % (self.rid, self.title) + ''.join(self.lines)


# ------------------------------------------------------------- MG-001 packets (PP) and a refused gate
r = Run('MG-001', 'PP packet terraforming and impact messages; a gate jump to an enemy gate',
        'prt 0 6\nhab 0 50,50,50,15,15,15,85,85,85\n'
        'sbdesign 0 0 Orbital Fort, 1 Stargate 100/250, empty, empty, empty, empty = Gate Fort\n'
        'sbdesign 1 0 Space Station, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Station\n'
        'sbdesign 1 1 Orbital Fort, 1 Stargate 100/250, empty, empty, empty, empty = Gate Fort\n')
x, y = XY[20]; r.own(20, 1, 2000, env='30,70,30'); r.add('thing packet 0 0 %d %d 20 10 400 400 400' % (x, y + 50))
r.case('A', 'M-1', 'player 0 (PP) packet, 400/400/400 kT at warp 10, into player 1 planet 20 (no starbase, '
       'pop 2000, environment 30/70/30; PP centre 50/50/50)',
       'player 0 gets 0x131 and/or 0x133 per changed axis, each followed by its pair 0x132/0x134 (same slots); '
       'player 1 gets no 0x131..0x134, only the impact message', 'player 1 gets 0x132/0x134')
x, y = XY[22]; r.add('planetset 22 env=30,70,30'); r.add('thing packet 0 1 %d %d 22 10 400 400 400' % (x, y + 50))
r.case('B', 'M-1', 'the same packet into unowned planet 22 (environment 30/70/30)',
       'player 0 gets 0x131/0x133 for planet 22 with no 0x132/0x134', '')
x, y = XY[23]; r.own(23, 1, 0); r.add('thing packet 0 2 %d %d 23 10 400 400 400' % (x, y + 50))
r.case('C', 'M-2', 'the same packet into player 1 planet 23, owned with population 0',
       'player 1 gets 0x181 with slots (planet 23, 0 = the packet owner, 0, 0) rather than a damage amount', '')
r.own(12, 0, 1000, sb='0'); r.own(11, 1, 1000, sb='1')
x, y = XY[12]; tx, ty = XY[11]
r.add('fleet 0 0 planet 12 at %d %d ships 0:1 plan 0 fuel 100 to %d %d planet 11 warp 11' % (x, y, tx, ty))
r.case('D', 'M-8', 'player 0 Laser DD at its own gate (planet 12) ordered through the gate to enemy player 1\'s gate '
       'at planet 11', 'refused: stays at planet 12; 0x0e5 with slots (fleet 0, 11, 11, 11): all three planet '
       'slots hold the destination', 'departure planet 12 in the second slot')

# ------------------------------------------------------------- MG-002 population, production, fuel (JOAT player 0)
r = Run('MG-002', 'empty-planet messages, build-count messages and load-optimal fuel (player 0)')
r.own(0, 0, 0)
r.case('A', 'M-3', 'player 0 planet 0 (the first planet) owned with population 0', 'uninhabited; 0x023 or 0x040 '
       '(depends on an uninitialised value; recorded, not predicted)', '')
r.own(2, 0, 15000); r.own(3, 0, 0)
r.case('B', 'M-3', 'planet 2 overcrowded (15000 of 10000: shrinks), planet 3 owned with population 0',
       'planet 3 uninhabited with **0x023** (the planet before it shrank)', '0x040')
r.own(5, 0, 1000); r.own(6, 0, 0)
r.case('C', 'M-3', 'planet 5 growing (1000), planet 6 owned with population 0',
       'planet 6 uninhabited with **0x040** (the planet before it grew)', '0x023')
for n, q, exp, alt in ((9, '7:3:1,7:2:1', 'two 0x036: 3, then 2', 'one 0x036 with 5'),
                       (10, '7:1:1,7:4:1', 'one 0x036 with 5 (a single 0x035 is absorbed)', '0x035 + 0x036 4'),
                       (13, '7:2:1,7:1:1', '0x036 with 2, then 0x035', 'one 0x036 with 3'),
                       (14, '7:1:1,7:1:1', 'one 0x036 with 2', 'two 0x035')):
    r.own(n, 0, 2000, extra='ge=200'); r.add('queue %d %s' % (n, q))
    r.case('D%d' % n, 'M-4', 'planet %d queue: factories %s' % (n, q.replace(':1', '').replace('7:', '')), exp, alt)
FUEL = 'task transport -,-,-,-,7:0'
for n in (15, 16, 18, 19):
    r.own(n, 0, 1000)
x, y = XY[15]; fx, fy = XY[6]
r.add('fleet 0 1 planet 15 at %d %d ships 0:1 plan 0 fuel 1 %s to %d %d warp 6' % (x, y, FUEL, 1020, 1380))
r.case('E', 'M-5', 'Laser DD, fuel 1, load-optimal fuel at own planet 15 (no starbase), next leg 400 ly at warp 6',
       '0x03c (or 0x03d if its tank is too small) with the shortfall; fuel not raised by the order; no 0x02b', '0x02b')
x, y = XY[16]
r.add('fleet 0 2 planet 16 at %d %d ships 1:1 plan 0 fuel 2 %s to %d %d warp 10' % (x, y, FUEL, 1020, 1020))
r.case('F', 'M-5', 'Scout, fuel 2, load-optimal fuel at own planet 16, next leg about 450 ly at warp 10',
       '0x03d (tank smaller than the need) or 0x03c, with capacity and need in the slots; no fuel gained', '')
x, y = XY[18]
r.add('fleet 0 3 planet 18 at %d %d ships 0:1 plan 0 fuel 280 %s to %d %d warp 6' % (x, y, FUEL, x, y - 20))
r.case('G', 'M-5', 'Laser DD, fuel 280 (full), load-optimal fuel at own planet 18, next leg 20 ly',
       'the fuel above the need is unloaded: 0x02d (fuel), fleet keeps about the need', 'no message, fuel kept')
x, y = XY[19]
r.add('fleet 0 4 planet 19 at %d %d ships 0:1 plan 0 fuel 280 %s' % (x, y, FUEL))
r.case('H', 'M-5', 'Laser DD, fuel 280, load-optimal fuel at own planet 19, no further waypoint',
       'all fuel unloaded: 0x02d with 280, fuel 0', 'fuel kept')
x, y = XY[4]
r.add('fleet 0 5 at %d %d ships 0:1 plan 0 fuel 3 to %d %d planet 4 warp 6 %s to 1380 1380 warp 6' % (x, y + 20, x, y, FUEL))
r.case('I', 'M-5', 'Laser DD, fuel 3, arrives at unowned planet 4 with load-optimal fuel, next leg about 350 ly',
       '0x126 (cannot load fuel there) after arrival', 'no message')


# ------------------------------------------------------------- MG-003 load-optimal fuel into a fleet (after MG-002 missed)
# MG-002 E..I (planet targets) sent no fuel message at all and kept every fleet's fuel. Two readings remain:
# H1 the need is the trip to the next waypoint and a planet simply takes no fuel; H2 the need is computed as 0,
# so all fuel counts as surplus and is offered to the target. A fleet target takes fuel, which separates them.
r = Run('MG-003', 'load-optimal fuel with an own fleet as the target (follow-up to MG-002 E..I)')
for i, (x, y, ships, fuel, to, warp) in enumerate(((1040, 1230, '0:1', 50, (1380, 1230), 6),
                                                  (1200, 1230, '0:1', 280, (1200, 1250), 6),
                                                  (1100, 1230, '1:1', 2, (1390, 1390), 10))):
    r.add('fleet 0 %d at %d %d ships 0:1 plan 0 fuel 0' % (2 * i + 1, x, y))
    r.add('fleet 0 %d at %d %d ships %s plan 0 fuel %d target fleet 0 %d task transport -,-,-,-,7:0 to %d %d warp %d'
          % (2 * i, x, y, ships, fuel, 2 * i + 1, to[0], to[1], warp))
r.case('A', 'M-5', 'Laser DD X, fuel 50, load-optimal fuel targeting own empty Laser DD Y (deep space), next leg 340 ly '
       'at warp 6', 'H1: 0x03c with the shortfall, X keeps 50, Y 0. H2: X gives all 50 to Y (0x02d 50)', '')
r.case('B', 'M-5', 'the same with X fuel 280 and a 20-ly next leg',
       'H1: X keeps about the need for 20 ly and Y gets the rest (0x02d). H2: Y gets all 280', '')
r.case('C', 'M-5', 'Scout X, fuel 2, next leg about 330 ly at warp 10, own empty Laser DD Y',
       'H1: 0x03d (capacity 50 below the need) or 0x03c, X keeps 2. H2: Y gets 2 (0x02d)', '')


# ------------------------------------------------------------- MG-004 load-optimal fuel at an own planet with a starbase
# MG-003 matched H1 for fleet targets, yet at planets without a starbase (MG-002 E..I) the order did nothing and the
# fleets left. Does a planet with a starbase (a fuel source) behave like a fleet target?
r = Run('MG-004', 'load-optimal fuel at own planets with a starbase (follow-up to MG-002 and MG-003)',
        'sbdesign 0 0 Orbital Fort, empty, empty, empty, empty, empty = Fort\n')
for n, fid, fuel, to, warp in ((15, 0, 1, (1020, 1380), 6), (18, 1, 280, (1324, 1172), 6)):
    x, y = XY[n]; r.own(n, 0, 1000, sb='0')
    r.add('fleet 0 %d planet %d at %d %d ships 0:1 plan 0 fuel %d %s to %d %d warp %d' % (fid, n, x, y, fuel, FUEL, to[0], to[1], warp))
r.case('A', 'M-5', 'Laser DD, fuel 1, load-optimal fuel at own planet 15 with an Orbital Fort, next leg 400 ly at warp 6',
       'if the order runs as with a fleet target: 0x03c and the fleet waits (no load, H1); '
       'if planets are skipped as in MG-002: no message and the fleet leaves', '')
r.case('B', 'M-5', 'Laser DD, fuel 280, load-optimal fuel at own planet 18 with an Orbital Fort, next leg 20 ly',
       'if the order runs: surplus offered to the planet; else no message, fuel kept', '')


# ------------------------------------------------------------- MG-005 homeworld mark after a capture (KERNEL step 3.6)
# Binary reading (stars-decomp takeover.md): each year every planet's homeworld mark is cleared and then set on the
# planet each player's record names as its homeworld. Only new-game creation writes that record, so the mark stays
# on the captured planet under its new owner.
r = Run('MG-005', 'homeworld mark after the homeworld is captured',
        'design 0 2 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter\n')
x, y = XY[8]
r.add('planet 8 pop 10 starbase none')
r.add('fleet 0 0 planet 8 at %d %d ships 2:1 plan 0 fuel 200 cargo 0 0 0 100 task unload' % (x, y))
r.case('A', 'T-41', 'player 0 freighter in orbit of player 1\'s homeworld 8 (pop 10, no starbase) unloads 100 '
       'colonists on waypoint 0 (invasion before movement, T-5)',
       'planet 8 owned by player 0 and still marked homeworld; player 1\'s record still names planet 8; '
       'player 0\'s homeworld 17 still marked', 'mark cleared, or moved to a planet of player 1')


# ------------------------------------------------------------- MG-006 fuel orders by target type (after MG-002..004)
# Binary reading (stars-decomp messages-predictions.md M-5b): fuel is handled only when waypoint 0 targets a fleet or
# deep space. For a planet or an object every fuel action is skipped; deep space accepts no fuel.
r = Run('MG-006', 'fuel orders by waypoint target: planets, deep space (follow-up to MG-002..004)',
        'design 0 2 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter\n'
        'sbdesign 0 0 Orbital Fort, empty, empty, empty, empty, empty = Fort\n')
r.own(15, 0, 1000); r.own(16, 0, 1000, sb='0')
x, y = XY[15]
r.add('fleet 0 0 planet 15 at %d %d ships 2:1 plan 0 fuel 300 cargo 20 0 0 0 task transport 2:0,-,-,-,4:100' % (x, y))
r.case('A', 'M-5b F1', 'Freighter at own planet 15 (no starbase), 20 kT ironium, fuel 300: unload all ironium and unload '
       'exactly 100 fuel', '0x02d for the ironium (20); no fuel message, fuel 300', 'fuel 200')
x, y = XY[16]
r.add('fleet 0 1 planet 16 at %d %d ships 2:1 plan 0 fuel 100 task transport -,-,-,-,1:0' % (x, y))
r.case('B', 'M-5b F1', 'Freighter at own planet 16 with an Orbital Fort, fuel 100: load all fuel',
       'no 0x02b for fuel (the fort refuels it at the end of the year anyway)', '0x02b fuel')
x, y = XY[4]
r.add('fleet 0 2 planet 4 at %d %d ships 2:1 plan 0 fuel 300 task transport -,-,-,-,7:0' % (x, y))
r.case('C', 'M-5b F1', 'Freighter at unowned planet 4, fuel 300: load optimal, no further waypoint',
       'no message, fuel 300', '0x02d 300')
r.add('fleet 0 3 at 1040 1230 ships 2:1 plan 0 fuel 20 task transport -,-,-,-,7:0 to 1380 1230 warp 6')
r.case('D', 'M-5b F2', 'Freighter in deep space (1040,1230), fuel 20: load optimal, next leg 340 ly at warp 6',
       '0x03c with location (1040,1230) and the shortfall; the fleet waits with fuel 20', 'leaves')
r.add('fleet 0 4 at 1200 1230 ships 2:1 plan 0 fuel 300 task transport -,-,-,-,7:0')
r.case('E', 'M-5b F3', 'Freighter in deep space (1200,1230), fuel 300: load optimal, no further waypoint',
       'no message, fuel 300 (deep space takes no fuel)', '0x02d 300, fuel 0')
r.add('fleet 0 5 at 1100 1230 ships 2:1 plan 0 fuel 300 task transport -,-,-,-,2:0')
r.case('F', 'M-5b F4', 'Freighter in deep space (1100,1230), fuel 300: unload all fuel', 'no message, fuel 300',
       'fuel 0')
r.add('fleet 0 6 at 1260 1230 ships 1:1 plan 0 fuel 2 task transport -,-,-,-,7:0 to 1000 1000 warp 10')
r.case('G', 'M-5b F2', 'Scout in deep space (1260,1230), fuel 2: load optimal, next leg about 347 ly at warp 10',
       '0x03d (capacity 50 below the need); waits with fuel 2', 'leaves')


def main():
    if sys.argv[1:] == ['--list']:
        for r in RUNS:
            print('### %s: %s\n\n| Case | Prediction | Setup | Predicted | Rules out |\n|---|---|---|---|---|' % (r.rid, r.title))
            for c in r.cases:
                print('| %s-%s | %s | %s | %s | %s |' % ((r.rid,) + c))
            print()
        return
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for r in RUNS:
        open(os.path.join(out, r.rid.lower().replace('-', '') + '.spec'), 'w').write(r.spec())


main()
