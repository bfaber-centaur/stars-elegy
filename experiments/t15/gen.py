#!/usr/bin/env python3
"""T15: the yearly design check against the owner's tech (experiments/t15/README.md).

Writes t15-ctl.spec, t15-pre.spec and t15-up.spec (Combat Lab, two JOAT
players) into the directory given as the only argument. The three starts
differ only in player 0's stored energy research.
"""
import os
import sys

# Level cost (KERNEL.md "Level cost"): base[L] + 10 * (sum of the six levels).
BASE = [0, 50, 80, 130, 210, 340, 550, 890, 1440, 2330, 3770, 6100, 9870, 13850, 18040, 22440,
        27050, 31870, 36900, 42140, 47590, 53250, 59120, 65200, 71490, 77990, 84700]
FIELDS = ['energy', 'weapons', 'prop', 'con', 'elec', 'bio']
P0 = dict(energy=9, weapons=26, prop=26, con=26, elec=26, bio=26)
P1 = dict(energy=26, weapons=26, prop=26, con=26, elec=3, bio=26)
COST10 = BASE[10] + 10 * sum(P0.values())          # energy 9 -> 10: 3770 + 1390 = 5160
assert COST10 == 5160

DESIGNS = [
    # slot, text, name
    (0, 'Scout, 1 Quick Jump 5, empty, 1 Bear Neutrino Barrier', 'Bear Scout'),            # energy 10
    (1, 'Scout, 1 Quick Jump 5, empty, 1 Gorilla Delagator', 'Gorilla Scout'),             # energy 14
    (2, 'Scout, 1 Quick Jump 5, empty, 1 Wolverine Diffuse Shield', 'Wolverine Scout'),    # energy 6
    (3, 'Scout, 1 Quick Jump 5, 1 Possum Scanner, empty', 'Possum Scout'),                 # electronics 5
    (4, 'Scout, 1 Quick Jump 5, 1 Rhino Scanner, empty', 'Rhino Scout'),                   # electronics 1
]
# Deep-space spots more than 30 ly from every Combat Lab planet (experiments/fo/gen.py SPOTS).
FLEETS = [
    # id, design, at, extra
    (0, 0, (1010, 1010), ''),
    (1, 1, (1010, 1055), ''),
    (2, 2, (1010, 1100), ''),
    (3, 3, (1385, 1010), 'task transfer 0'),   # given to player 1 (the first other player)
    (4, 4, (1385, 1055), 'task transfer 0'),
    (5, 3, (1385, 1100), ''),                  # player 0 keeps a Possum Scout of its own
]
VARIANTS = {'t15-ctl': 0, 't15-pre': COST10, 't15-up': COST10 - 1}


def spec(name, accum):
    out = [f'# {name}: T15 design check (experiments/t15/gen.py)']
    for p, t in ((0, P0), (1, P1)):
        out += [f'tech {p} {f} {t[f]}' for f in FIELDS]
    out += ['research 0 0', 'research 1 0', 'field 0 energy', f'accum 0 energy {accum}',
            'relation 0 1 0', 'relation 1 0 0', 'queue 17 none']
    out += [f'design 0 {s} {d} = {n}' for s, d, n in DESIGNS]
    out += [f'fleet 0 {i} at {x} {y} ships {d}:1 fuel 50' + (' ' + e if e else '') for i, d, (x, y), e in FLEETS]
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    d = sys.argv[1]
    for name, accum in VARIANTS.items():
        with open(os.path.join(d, name + '.spec'), 'w') as f:
            f.write(spec(name, accum))


# ---------------------------------------------------------------- DC-4, DC-5 (PREDICTION-DC4.md)
# Written after DC-2's runs, which left player 1's received Possum Scout unchecked.
T26 = dict(energy=26, weapons=26, prop=26, con=26, elec=26, bio=26)
E3 = dict(T26, elec=3)
POSSUM = 'Scout, 1 Quick Jump 5, 1 Possum Scanner, empty'


def spec2(name, p0, p1, designs, fleets):
    out = [f'# {name}: T15 design check, follow-up (experiments/t15/gen.py)']
    for p, t in ((0, p0), (1, p1)):
        out += [f'tech {p} {f} {t[f]}' for f in FIELDS]
    out += ['research 0 0', 'research 1 0', 'relation 0 1 0', 'relation 1 0 0']
    out += designs + fleets
    return '\n'.join(out) + '\n'


VARIANTS2 = {
    # DC-4: player 1's own design above its tech
    't15-p1own': (T26, E3, [f'design 1 6 {POSSUM} = P1 Possum Scout'],
                  ['fleet 1 0 at 1385 1010 ships 6:1 fuel 50']),
    # DC-5: a design received by player 0, whose own designs are checked (DC-1, DC-3, T-37)
    't15-recv0': (E3, T26, [f'design 0 0 {POSSUM} = P0 Possum Scout', f'design 1 6 {POSSUM} = P1 Possum Scout'],
                  ['fleet 0 0 at 1010 1010 ships 0:1 fuel 50',
                   'fleet 1 0 at 1385 1010 ships 6:1 fuel 50 task transfer 0']),
}

if __name__ == '__main__':
    for name, args in VARIANTS2.items():
        with open(os.path.join(sys.argv[1], name + '.spec'), 'w') as f:
            f.write(spec2(name, *args))
