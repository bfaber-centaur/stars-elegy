#!/usr/bin/env python3
"""Ship launch oracle batch (SL-01..SL-12): CombatLab specs on the Combat Lab base.

  experiments/sl/gen.py OUTDIR      # writes OUTDIR/<name>/spec.txt

Predictions and results: experiments/sl/README.md.
"""
import os, sys

TECH = ''.join(f'tech {p} {f} 26\n' for p in (0, 1) for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio'))
STATION = ('Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, '
           '8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield')
GATE_STATION = STATION.replace('Space Station, empty,', 'Space Station, 1 Stargate 100/250,', 1)
SCOUT = 'Scout, 1 Long Hump 6, 1 Rhino Scanner, 1 X-Ray Laser = Scout'
QJ5 = 'Scout, 1 Quick Jump 5, 1 Bat Scanner = QJ5 Scout'
TANKER = 'Scout, 1 Long Hump 6, 1 Rhino Scanner, 1 Fuel Tank = Tanker'
COLONY = 'Colony Ship, 1 Long Hump 6, 1 Colonization Module = Colony'
MINER = 'Mini-Miner, 1 Long Hump 6, 1 Rhino Scanner, 1 Robo-Mini-Miner, 1 Robo-Mini-Miner = Miner'
RICH = 'env=50,50,50 factories=100 fe=20000 bo=20000 ge=20000'


def owned(n, owner, sb, pop=1000, extra=''):
    sbs = 'none' if sb is None else sb
    return f'planet {n} owner {owner} pop {pop} starbase {sbs}\nplanetset {n} {RICH}{extra}\n'


def routes():
    # SL-01..07. Player 0: stations everywhere it builds; one route per source.
    s = TECH + 'relation 0 1 2\nrelation 1 0 2\n'
    s += f'design 0 0 {SCOUT}\ndesign 0 1 {QJ5}\ndesign 0 2 {COLONY}\n'
    s += f'sbdesign 0 0 {STATION} = Station\nsbdesign 0 1 Orbital Fort, empty, 12 Colloidal Phaser, empty, empty, empty = Fort\n'
    s += f'sbdesign 0 2 {GATE_STATION} = Gate Station\n'
    # route cases: source -> destination
    R = {22: 23, 19: 21, 10: 13, 14: 13, 12: 18, 0: 6,      # unowned destinations (SL-04)
         17: 19, 9: 7, 20: 14,                              # own station destinations (SL-05)
         4: 5, 11: 8,                                       # controls: own Fort, player 1 station
         16: 16,                                            # route to itself (SL-07)
         2: 3, 1: 7}                                        # gates both ends (SL-06)
    gates = {1, 2, 3, 7}
    for n in sorted(set(R) | {3, 5, 7, 15}):
        sb = 1 if n == 5 else 2 if n in gates else 0
        s += owned(n, 0, sb, extra=f' route={R[n]}' if n in R else '')
        if n in R:
            s += f'queue {n} 0:1:2,1:1:2\n'
    s += 'queue 15 0:2:2,0:1:2,2:1:2\n'                     # SL-01, SL-03: no route
    s += owned(8, 1, 0)                                     # player 1 homeworld (SL-02)
    s += 'queue 8 0:1:2,0:1:2\n'
    for i in (0, 1, 3):
        s += f'fleet 1 {i} at 1169 1145 planet 8 ships 1:1 fuel 300\n'
    return s


def limit_a(ctl=False):
    # SL-08 (player 0 at 511 fleets) and SL-09 (player 1 at 512); none at the planet.
    s = TECH + 'relation 0 1 2\nrelation 1 0 2\n'
    s += owned(17, 0, 0) + owned(8, 1, 0)
    s += 'queue 17 0:1:2,0:1:2\n'
    s += 'queue 8 7:5:1\n' if ctl else 'queue 8 0:2:2,2:1:2,7:5:1\n'
    s += 'fleets 0 0-510 at 1020 1230 ships 1:1 fuel 300\n'
    s += 'fleets 1 0-511 at 1300 1230 ships 1:1 fuel 300\n'
    return s


def limit_b(ctl=False):
    # SL-10: player 0 at 512 with fleets 3 (10 damaged Scouts) and 5 at the planet;
    # player 1 at 512 with fleet 3 holding 32765 Scouts.
    s = TECH + 'relation 0 1 2\nrelation 1 0 2\n'
    s += owned(17, 0, 0) + owned(8, 1, 0)
    if not ctl:
        s += 'queue 17 0:1:2\nqueue 8 0:1:2\n'
    for p, (x, y), planet in ((0, (1306, 1060), 17), (1, (1169, 1145), 8)):
        s += f'fleets {p} 0-2 at 1020 {1230 + 20 * p} ships 1:1 fuel 300\n'
        s += f'fleet {p} 4 at 1020 {1230 + 20 * p} ships 1:1 fuel 300\n'
        s += f'fleets {p} 6-511 at 1020 {1230 + 20 * p} ships 1:1 fuel 300\n'
        s += f'fleet {p} 5 at {x} {y} planet {planet} ships 0:1 fuel 50\n'
    s += 'fleet 0 3 at 1306 1060 planet 17 ships 0:10 dmg 0:100:50 fuel 500\n'
    s += 'fleet 1 3 at 1169 1145 planet 8 ships 0:32765 fuel 1638250\n'
    return s


def starbases():
    # SL-11 and SL-12. Player 0 JOAT + Improved Starbases; player 1 AR + Improved Starbases.
    s = TECH + 'relation 0 1 2\nrelation 1 0 2\nlrt 0 0x0008\nlrt 1 0x0008\nprt 1 8\n'
    s += f'design 0 0 {SCOUT}\ndesign 0 1 {MINER}\ndesign 1 0 {SCOUT}\ndesign 1 1 {MINER}\n'
    s += (f'sbdesign 0 0 {STATION} = Station\nsbdesign 0 1 Space Dock = Dock\n'
          f'sbdesign 0 2 {STATION} = Station B\nsbdesign 0 3 Orbital Fort = Fort\n')
    s += f'sbdesign 1 0 {STATION} = Station\nsbdesign 1 1 Death Star = Death Star\nsbdesign 1 2 Ultra Station = Ultra\n'
    s += owned(17, 0, 0) + 'queue 17 17:1:2,0:2:2\n'                      # Station -> Dock
    s += owned(15, 0, 1) + 'queue 15 16:1:2,0:2:2\n'                      # Dock -> Station
    s += owned(11, 0, 0) + 'queue 11 18:1:2,0:2:2\n'                      # Station -> Station B
    s += owned(12, 0, 0, extra=' sbdmg=200') + 'queue 12 18:1:2,0:2:2\n'  # damaged Station -> Station B
    s += owned(19, 0, 3) + 'queue 19 0:1:2\n'                             # Fort builds a Scout
    s += owned(18, 0, 1) + 'queue 18 1:1:2\n'                             # Dock builds a 574 kT Mini-Miner (SL-11b)
    s += owned(8, 1, 1) + 'queue 8 18:1:2,0:2:2\n'                        # Death Star -> Ultra Station
    s += owned(4, 1, 0, extra=' mines=0') + 'queue 4 1:1:2\n'             # AR Mini-Miner (SL-11a)
    s += 'fleet 0 0 at 1020 1230 ships 0:1 fuel 50\nfleet 1 0 at 1300 1230 ships 0:1 fuel 50\n'
    return s


SPECS = {'sl-routes': routes(), 'sl-limit-a': limit_a(), 'sl-limit-a-ctl': limit_a(True),
         'sl-limit-b': limit_b(), 'sl-limit-b-ctl': limit_b(True), 'sl-starbases': starbases()}

if __name__ == '__main__':
    for name, spec in SPECS.items():
        os.makedirs(os.path.join(sys.argv[1], name), exist_ok=True)
        with open(os.path.join(sys.argv[1], name, 'spec.txt'), 'w') as f:
            f.write(f'# {name} (experiments/sl/gen.py)\n' + spec)
