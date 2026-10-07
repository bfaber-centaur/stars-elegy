#!/usr/bin/env python3
"""Write the CB-011..CB-015 specs (starbase and planet cases)."""
TECH = ''.join(f'tech {p} {f} 26\n' for p in (0, 1)
               for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio'))
DESIGNS = """design 0 0 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
design 1 0 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 1 1 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
sbdesign 0 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Laser Station
sbdesign 0 1 Space Station, empty, empty, 8 Mole-skin Shield, empty, empty, 8 Mole-skin Shield, empty, empty, empty, empty, empty, empty = Unarmed Station
sbdesign 0 2 Orbital Fort, empty, empty, empty, empty, empty = Bare Fort
sbdesign 1 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Laser Station
sbdesign 1 1 Space Station, empty, empty, 8 Mole-skin Shield, empty, empty, 8 Mole-skin Shield, empty, empty, empty, empty, empty, empty = Unarmed Station
"""
XY = {4: (1143, 1103), 5: (1146, 1180), 12: (1245, 1158), 15: (1281, 1064),
      18: (1324, 1192), 19: (1342, 1123), 21: (1359, 1121), 22: (1368, 1292)}
PLANETS = """planet 18 owner 0 pop 500 starbase 0
planet 19 owner 0 pop 500 starbase 1
planet 21 owner 0 pop 500 starbase 0
planet 15 owner 0 pop 500 starbase 0
planet 22 owner 0 pop 500 starbase none
planet 5 owner 1 pop 500 starbase 1
planet 12 owner 1 pop 500 starbase 1
"""


def fleet(p, i, n, ships, plan):
    x, y = XY[n]
    return f'fleet {p} {i} planet {n} at {x} {y} ships {ships} plan {plan} fuel 100\n'


def one_sided(who0, name):
    """P0 sees P1 as enemy, P1 sees P0 as neutral. P0's plan 0 attack-who = who0."""
    return (TECH + 'relation 0 1 2\nrelation 1 0 0\n' + DESIGNS + PLANETS +
            f'plan 0 0 5 1 0 {who0} = {name}\n'
            'plan 0 1 5 1 0 1 = Max Any\n'
            'plan 0 3 5 5 0 1 = Unarmed Only\n'
            'plan 0 4 5 3 0 1 = Armed Only\n'
            'plan 1 1 5 1 0 1 = Max Any\n'
            'plan 1 2 5 1 0 0 = Nobody\n'
            '# S1 planet 18, armed station: armed P1 fleet attacking enemies (P1 sees P0 as neutral)\n'
            + fleet(1, 0, 18, '1:5', 1) +
            '# S2 planet 19, unarmed station: same visitor\n'
            + fleet(1, 1, 19, '1:5', 1) +
            '# S3 planet 21, armed station: unarmed P1 visitor attacking enemies\n'
            + fleet(1, 2, 21, '0:3', 1) +
            '# S4 planet 5 (P1, unarmed station): P0 frigates, primary unarmed, no secondary\n'
            + fleet(0, 0, 5, '0:5', 3) +
            '# S5 planet 12 (P1, unarmed station): P0 frigates, primary armed, no secondary\n'
            + fleet(0, 1, 12, '0:5', 4) +
            '# S6 planet 15 (P0, armed station): P0 frigates destroy P1 haulers\n'
            + fleet(0, 2, 15, '0:10', 1) + fleet(1, 3, 15, '0:6', 2) +
            '# S7 planet 22 (P0, no starbase): the same\n'
            + fleet(0, 3, 22, '0:10', 1) + fleet(1, 4, 22, '0:6', 2))


specs = {
    'cb011': one_sided(1, 'Station Enemies'),
    'cb012': one_sided(3, 'Station Everyone'),
    'cb013': one_sided(5, 'Station Player 1'),
    'cb014': one_sided(0, 'Station Nobody'),
    # Q-3, Q-5: mutual enemies; P0 plan 0 primary starbase, no secondary
    'cb015': (TECH + 'relation 0 1 2\nrelation 1 0 2\n' + DESIGNS +
              PLANETS.replace('planet 19 owner 0 pop 500 starbase 1', 'planet 19 owner 0 pop 500 starbase 2') +
              'plan 0 0 5 2 0 1 = Station Starbase Only\n'
              'plan 0 1 5 1 0 1 = Max Any\n'
              'plan 1 1 5 1 0 1 = Max Any\n'
              '# T1 planet 18, armed station: P0 frigates start a battle with P1 frigates\n'
              + fleet(0, 0, 18, '0:5', 1) + fleet(1, 0, 18, '1:5', 1) +
              '# T2 planet 19, bare Orbital Fort: P1 frigates attack it\n'
              + fleet(1, 1, 19, '1:10', 1)),
}
for k, v in specs.items():
    open(f'{k}.spec', 'w').write(v)
