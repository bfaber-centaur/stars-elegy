#!/usr/bin/env python3
"""Write the TK round-4 (TK-301..TK-305) Combat Lab specs, with predictions.

Round 4 closes TAKEOVER.md's open list where legal orders reach it: Laser
Battery and Planetary Shield against bombs and troops, the "load exactly"
action, ancient artifacts (with random events on, and with slower tech),
and Mystery Trader parts scrapped at a starbase. Colonists given to a
foreign planet by a manual cargo transfer need crafted order files and wait
on the serial decision. Predictions restate the private binary reading
(stars-decomp docs/takeover.md, docs/orders-misc.md) as behavior and are
written here before the runs; `check4.py` summarizes the run dumps.

TK-303 and TK-304 run on a copy of the Combat Lab base whose `.XY` game
options byte (offset 0x10, `scripts/oracle/hst-edit xy`) is 0x00 (random
events on) and 0x02 (random events on, slower tech) instead of 0x80.

  python3 experiments/tk/gen4.py OUTDIR      # write tkNNN.spec files
  python3 experiments/tk/gen4.py --table     # print the prediction table
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import cb_run, grow, D_CHERRY2, D_SMART2, D_FREIGHTER, D_COLONIZER  # noqa: E402
from gen3 import NOBODY, RANDOM_CYCLES, fmt3  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SIX_CYCLES = RANDOM_CYCLES[:6]

# Working (TAKEOVER.md "Planetary defenses against bombs", single precision).
# 10 Cherry2 = 20 Cherry: A = 500, M = 60, I = 200. 10 Smart2 = 20 Smart:
# S = round(1000 - 1000 * 0.987^20) = 230. P' = 1000 after growth, defenses
# 100 installed, 40 counted (ceil(1000/25)).
#   Laser Battery (c 24):    s = 0.37844, sSmart = 0.61699
#     A' = 189, M' = 23, I' = 138  -> pop 811, defenses 0
#     S' = 142                     -> pop 858
#   Planetary Shield (c 30): s = 0.29571, sSmart = 0.54632
#     A' = 148, M' = 18, I' = 130  -> pop 852, defenses 0
#     S' = 126                     -> pop 874
# Troops: 600 dropped before movement on P = 500 with 20 defenses (20 counted):
#   Laser: s = 0.61517, s' = s + (1 - s)/4 = 0.71138, strength floor(660 s') = 469 < 500
#          -> the defender keeps 31, which grows to 35
#   Shield: s = 0.54379, s' = 0.65785, strength 434 -> keeps 66, grows to 75
DEF = {10: dict(name='Laser Battery', bomb=811, smart=858, keep=31),
       16: dict(name='Planetary Shield', bomb=852, smart=874, keep=66)}


def defense_run(name, energy):
    d = DEF[energy]
    r = cb_run(name, f'{d["name"]} (player 1 energy {energy}) against bombs and troops; "load exactly"',
               p1=(energy, 3, 3, 3, 3, 3))
    r.h(NOBODY)
    r.case('B', 'defenses', f'10 Cherry2 bombers (20 Cherry) at player 1 planet 13: P 870, defenses 100, no other '
           f'installations; best defense {d["name"]}')
    r.orbit(13, f'{D_CHERRY2}:10'); r.target(13, 870, mines=0, factories=0, defenses=100)
    r.expect('planet', (13,), dict(owner=1, pop=d['bomb'], defenses=0))
    r.case('S', 'defenses', '10 Smart2 bombers (20 Smart) at player 1 planet 2: P 870, defenses 100')
    r.orbit(2, f'{D_SMART2}:10'); r.target(2, 870, mines=0, factories=0, defenses=100)
    r.expect('planet', (2,), dict(owner=1, pop=d['smart'], defenses=100))
    r.case('G', 'defenses', 'Freighter (600 colonists) unloads on player 1 planet 14 before movement: P 500, '
           'defenses 20')
    r.orbit(14, f'{D_FREIGHTER}:3', plan=1, cargo=(0, 0, 0, 600), task='unload')
    r.target(14, 500, mines=0, factories=0, defenses=20)
    r.expect('planet', (14,), dict(owner=1, pop=grow(d['keep'])))
    r.case('L1', 'load exactly', 'player 0 planet 11 (P 100): empty Freighter loads exactly 30 colonists')
    f1 = r.orbit(11, f'{D_FREIGHTER}:1', plan=1, task='transport -,-,-,3:30,-')
    r.target(11, 100, owner=0, mines=0, factories=0, defenses=0)
    r.expect('fleet', (0, f1), dict(col=30))
    r.expect('planet', (11,), dict(owner=0, pop=grow(70)))
    r.case('L2', 'load exactly', 'player 0 planet 12 (P 100, surface ironium 25): load exactly 40 ironium')
    f2 = r.orbit(12, f'{D_FREIGHTER}:1', plan=1, task='transport 3:40,-,-,-,-')
    r.target(12, 100, owner=0, mines=0, factories=0, defenses=0, fe=25)
    r.expect('fleet', (0, f2), dict(fe=25))
    r.expect('planet', (12,), dict(owner=0, surface=[0, 0, 0]))
    r.case('L3', 'load exactly', 'player 0 planet 16 (P 100, surface ironium 500): load exactly 300 ironium into '
           'a 210 kT hold')
    f3 = r.orbit(16, f'{D_FREIGHTER}:1', plan=1, task='transport 3:300,-,-,-,-')
    r.target(16, 100, owner=0, mines=0, factories=0, defenses=0, fe=500)
    r.expect('fleet', (0, f3), dict(fe=210))
    r.expect('planet', (16,), dict(owner=0, surface=[290, 0, 0]))
    return r


def artifact_run(name, slow):
    r = cb_run(name, 'ancient artifacts, random events on' + (', slower tech' if slow else ''),
               p0=(10,) * 6, cycles=SIX_CYCLES)
    r.base = 'opt02' if slow else 'opt00'
    r.h(NOBODY)
    lo, hi = 100, 400
    r.case('A1', 'artifact', 'Freighter (100) captures player 1 planet 14 (P 10, artifact) before movement')
    r.orbit(14, f'{D_FREIGHTER}:1', plan=1, cargo=(0, 0, 0, 100), task='unload')
    r.target(14, 10, mines=0, factories=0, defenses=0, artifact=1)
    r.expect('planet', (14,), dict(owner=0))
    r.expect('art', (14,), f'0x05e to player 0: planet 14, a field 0-5, points {lo}-{hi} added to that field\'s '
             'research; the planet\'s artifact flag cleared')
    r.case('A2', 'artifact', 'Colonizer (25) colonizes unowned planet 21 (artifact) before movement')
    r.orbit(21, f'{D_COLONIZER}:1', plan=1, cargo=(0, 0, 0, 25), task='colonize'); r.planetset(21, artifact=1)
    r.expect('planet', (21,), dict(owner=0))
    r.expect('art', (21,), f'0x05e to player 0: planet 21, points {lo}-{hi}; flag cleared')
    r.case('A3', 'artifact', 'Colonizer (5) colonizes unowned planet 22 (artifact) before movement')
    r.orbit(22, f'{D_COLONIZER}:1', plan=1, cargo=(0, 0, 0, 5), task='colonize'); r.planetset(22, artifact=1)
    r.expect('planet', (22,), dict(owner=0))
    r.expect('art', (22,), f'0x05e: points scaled by 5/10, so {lo // 2}-{hi // 2}; flag cleared')
    r.case('A4', 'artifact', 'Freighter (10) unloads on player 1 planet 3 (P 100, artifact): the defender wins')
    r.orbit(3, f'{D_FREIGHTER}:1', plan=1, cargo=(0, 0, 0, 10), task='unload')
    r.target(3, 100, mines=0, factories=0, defenses=0, artifact=1)
    r.expect('planet', (3,), dict(owner=1))
    r.expect('art', (3,), 'no 0x05e; flag kept')
    r.case('A5', 'artifact', 'player 1 planet 9 (P 87, artifact), no fleet')
    r.target(9, 87, mines=0, factories=0, defenses=0, artifact=1)
    r.expect('art', (9,), 'no 0x05e; flag kept (an owned artifact planet gives nothing)')
    if slow:
        r.case('Y', 'artifact', 'slower tech on')
        r.expect('art', (-1,), 'points are not halved (binary: the halving comes after the points are added and '
                 'is unused, LEGACY BUG): A1/A2 still 100-400, A3 50-200. If halving applied, every A1/A2 value '
                 'would be at most 200')
    return r


def runs():
    out = [defense_run('tk301', 10), defense_run('tk302', 16),
           artifact_run('tk303', False), artifact_run('tk304', True)]

    # ------------------------------------------------------------------ TK-305
    # Twelve designs with 2 Hush-a-Boom each: rgTechTrader for Hush-a-Boom reaches 24 (cap 25).
    r = cb_run('tk305', 'Mystery Trader parts scrapped at a starbase; player 1 tech 0', p1=(0,) * 6,
               cycles=RANDOM_CYCLES)
    hush = [f'design 0 {i} Mini Bomber, 1 Long Hump 6, 2 Hush-a-Boom = Hush{i}' for i in range(12)]
    r.hdr = [h for h in r.hdr if not h.startswith('design 0')]
    r.hdr = [l for h in r.hdr for l in h.split('\n') if not l.startswith('design 0')]
    r.hdr += hush
    ships = ','.join(f'{i}:1' for i in range(12))
    for n in (0, 2, 3):
        r.case(f'S{n}', 'scrap MT', f'a fleet of 12 Hush-a-Boom bombers (12 designs, 2 Hush-a-Boom each) scraps at '
               f'player 1 planet {n} with an Orbital Fort')
        r.orbit(n, ships, task='scrap'); r.target(n, 87, starbase=True, mines=0, factories=0, defenses=0)
    r.case('Y', 'scrap MT', 'player 1 at the end of the year')
    r.expect('dist', (1,), 'one gain at most per stream. Each attempt: 1/2 to pass; then 13 rand(13) picks, each '
             'giving Hush-a-Boom with chance 24% when it names Hush-a-Boom (P(part) = 1 - (1 - 0.24/13)^13 = '
             '0.215); otherwise a level in a field the bombers needed (construction, propulsion, weapons, '
             'electronics or biotech), never energy. The first attempt that passes gains (P = 0.875 per stream). '
             'A part gain sends 0x13c and sets player 1\'s Hush-a-Boom bit; a level sends 0x13d')
    out.append(r)
    return out


def table():
    for r in runs():
        print(f'### {r.name.upper()}: {r.title}')
        print()
        cyc = '' if len(r.cycles) == 1 else f' Cycles {", ".join(map(str, r.cycles))}.'
        base = {'opt00': ' Base: random events on.', 'opt02': ' Base: random events on, slower tech.'}.get(
            getattr(r, 'base', ''), '')
        print(f'Game {r.game}, {r.years} year(s).{cyc}{base}')
        print()
        print('| Case | Rule | Setup | Predicted |')
        print('|---|---|---|---|')
        for cid, rule, text in r.cases:
            pred = '; '.join(fmt3(k, a, v, y) if k != 'art' else v for c, k, a, v, y in r.checks if c == cid)
            print(f'| {cid} | {rule} | {text} | {pred} |')
        print()


if __name__ == '__main__':
    if sys.argv[1:] == ['--table']:
        table()
    else:
        out = sys.argv[1] if len(sys.argv) > 1 else HERE
        for r in runs():
            r.write(out)
            print(r.name, len(r.cases), 'cases', len(r.checks), 'checks')
