#!/usr/bin/env python3
"""Write the TK round-3 (TK-201..TK-203) Combat Lab specs, with predictions.

Round 3 sweeps the TAKEOVER.md rules still tagged BINARY-ONLY after rounds
1 and 2: the order of drops and bombing passes across planets, minerals
unloaded on another player's or an unowned planet, unloads in deep space,
loading every colonist off an own planet (and off the homeworld), the
colonize failures not yet seen (deep space, no colonists), the "mines
never go negative" clause, the bombing messages for several fleets, and
tech learned from scrapping at a starbase. Predictions restate the private
binary reading (stars-decomp docs/takeover.md, docs/messages/) as behavior
and are written here before the runs; `check3.py` compares them with the
run dumps and message decodes.

Specs use the round-2 writer (gen2.py `cb_run`): Combat Lab, two JOAT
players, player 0 tech 26, research 0%, enemies, plan 0 "Enemies".
Populations in units of 100 colonists; growth (15%) runs before the
after-movement phase, so P = 870 is 1000 when bombs fall.

  python3 experiments/tk/gen3.py OUTDIR      # write tkNNN.spec files
  python3 experiments/tk/gen3.py --table     # print the prediction table
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import cb_run, grow, D_CHERRY2, D_LADY1, D_FREIGHTER, D_COLONIZER, fmt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
D_SCOUT = 14
SCOUT = 'design 0 14 Scout, 1 Long Hump 6, empty = Scout LH6'
NOBODY = 'plan 0 1 4 1 0 0 = Nobody'
RANDOM_CYCLES = (20000, 30000, 50000, 10000, 12000, 15000, 17000, 11500, 9800, 6000, 5200, 3700)


def runs():
    out = []

    # ------------------------------------------------------------------ TK-201
    r = cb_run('tk201', 'order across planets, foreign and deep-space unloads, emptying own planets, '
               'colonize failures; second year for the homeworld mark', years=2, cycles=(20000, 30000))
    r.h(NOBODY)
    r.case('A', 'drop order', 'fleet 0 Freighter unloads 100 colonists on player 1 planet 14 (P 10); fleet 1 '
           'Freighter unloads 100 on player 1 planet 3 (P 10); both in orbit, before movement')
    f0 = r.orbit(14, f'{D_FREIGHTER}:1', plan=1, cargo=(0, 0, 0, 100), task='unload'); r.target(14, 10)
    f1 = r.orbit(3, f'{D_FREIGHTER}:1', plan=1, cargo=(0, 0, 0, 100), task='unload'); r.target(3, 10)
    r.expect('planet', (14,), dict(owner=0, pop=grow(90)))
    r.expect('planet', (3,), dict(owner=0, pop=grow(90)))
    r.expect('order', ('drops', 0), 'player 0 invasion messages: planet 14 before planet 3 (fleet order), '
             'not planet order')
    r.case('B', 'bombing order', 'fleet 2 Cherry2 bomber at player 1 planet 13 (P 87); fleet 3 Cherry2 at '
           'player 1 planet 2 (P 87); no defenses or installations')
    r.orbit(13, f'{D_CHERRY2}:1'); r.target(13, 87, mines=0, factories=0, defenses=0)
    r.orbit(2, f'{D_CHERRY2}:1'); r.target(2, 87, mines=0, factories=0, defenses=0)
    r.expect('planet', (13,), dict(owner=1, pop=94))
    r.expect('planet', (2,), dict(owner=1, pop=94))
    r.expect('order', ('bombing', 0), 'player 0 bombing messages: planet 13 before planet 2; player 1\'s the '
             'same order')
    r.case('C', 'minerals to a foreign planet', 'fleet 4 Freighter with 50 kT ironium unloads all on player 1 '
           'planet 9 (P 87, no starbase, surface 0)')
    f4 = r.orbit(9, f'{D_FREIGHTER}:1', plan=1, cargo=(50, 0, 0, 0), task='transport 2:0,-,-,-,-')
    r.target(9, 87, mines=0, factories=0, defenses=0)
    r.expect('planet', (9,), dict(owner=1, surface=[50, 0, 0]))
    r.expect('fleet', (0, f4), dict(fe=0))
    r.case('D', 'minerals to a foreign planet', 'fleet 5 the same at player 1 planet 10 with an Orbital Fort')
    f5 = r.orbit(10, f'{D_FREIGHTER}:1', plan=1, cargo=(50, 0, 0, 0), task='transport 2:0,-,-,-,-')
    r.target(10, 87, starbase=True, mines=0, factories=0, defenses=0)
    r.expect('planet', (10,), dict(owner=1, surface=[50, 0, 0]))
    r.expect('fleet', (0, f5), dict(fe=0))
    r.case('E', 'minerals to an unowned planet', 'fleet 6 the same at unowned planet 4 (surface 0)')
    f6 = r.orbit(4, f'{D_FREIGHTER}:1', plan=1, cargo=(50, 0, 0, 0), task='transport 2:0,-,-,-,-')
    r.expect('planet', (4,), dict(owner=-1, surface=[50, 0, 0]))
    r.expect('fleet', (0, f6), dict(fe=0))
    r.case('F', 'deep space unload', 'fleet 7 Freighter at (1200,1230) with 50 kT ironium and 50 colonists: '
           'unload all ironium and all colonists')
    f7 = r.space(1200, 1230, f'{D_FREIGHTER}:1', task='transport 2:0,-,-,2:0,-')
    r.lines[-1] += ' cargo 50 0 0 50'
    r.expect('fleet', (0, f7), dict(fe=0, col=50))
    r.expect('msg', (0,), '0x02d for the 50 ironium, then 0x165 (colonists refused); no salvage object')
    r.case('G1', 'loading every colonist', 'player 0 planet 11 (P 870, growing) and planet 12 (P 50); fleet 8 '
           'empty Freighter at planet 12 loads all colonists')
    r.target(11, 870, owner=0, mines=0, factories=0, defenses=0)
    r.target(12, 50, owner=0, mines=0, factories=0, defenses=0)
    f8 = r.orbit(12, f'{D_FREIGHTER}:1', plan=1, task='transport -,-,-,1:0,-')
    r.expect('fleet', (0, f8), dict(col=50))
    r.expect('planet', (12,), dict(owner=-1, pop=0))
    r.expect('msg', (0,), '0x02c (50 colonists), then at growth 0x040 for planet 12 (planet 11 before it grew)')
    r.case('G2', 'emptying the homeworld', 'player 0 homeworld 17 set to P 50 with no starbase; player 0 planet '
           '16 (P 870, growing); fleet 9 empty Freighter at 17 loads all colonists')
    r.lines.append('planet 17 owner 0 pop 50 starbase none')
    r.target(16, 870, owner=0, mines=0, factories=0, defenses=0)
    f9 = r.orbit(17, f'{D_FREIGHTER}:1', plan=1, task='transport -,-,-,1:0,-')
    r.expect('fleet', (0, f9), dict(col=50))
    r.expect('planet', (17,), dict(owner=-1, pop=0))
    r.expect('homeworld', (17,), dict(mark=True, record=17))
    r.expect('homeworld', (17,), dict(mark=True, record=17), year=2)
    r.case('H1', 'colonize failure', 'fleet 10 Colonizer with 25 colonists at (1100,1230), task colonize')
    f10 = r.space(1100, 1230, f'{D_COLONIZER}:1', task='colonize')
    r.lines[-1] += ' cargo 0 0 0 25'
    r.expect('fleet', (0, f10), dict(col=25, task=0))
    r.expect('msg', (0,), '0x051 (not orbiting a planet), then 0x04e')
    r.case('H2', 'colonize failure', 'fleet 11 Colonizer with no colonists at unowned planet 22, task colonize')
    f11 = r.orbit(22, f'{D_COLONIZER}:1', plan=1, task='colonize')
    r.expect('fleet', (0, f11), dict(col=0, task=0))
    r.expect('planet', (22,), dict(owner=-1))
    r.expect('msg', (0,), '0x053 (no colonists), then 0x04e')
    r.case('I', 'homeworld mark (T-41)', 'fleet 12 Freighter unloads 100 colonists on player 1\'s homeworld 8 '
           '(P 10, no starbase); player 1 keeps other planets')
    r.orbit(8, f'{D_FREIGHTER}:1', plan=1, cargo=(0, 0, 0, 100), task='unload')
    r.lines.append('planet 8 owner 1 pop 10 starbase none')
    r.expect('planet', (8,), dict(owner=0))
    r.expect('homeworld', (8,), dict(mark=True, record=8, owner_record=1))
    out.append(r)

    # ------------------------------------------------------------------ TK-202
    r = cb_run('tk202', 'mines never go negative; bombing messages for several fleets; player 1 energy 26 '
               '(Neutron Shield)', p1=(26, 3, 3, 3, 3, 3), cycles=RANDOM_CYCLES)
    for n in (0, 2, 3, 9, 13, 14):
        r.case(f'M{n}', 'mines floor', f'one Lady1 bomber at player 1 planet {n}: P 870, mines 1, factories 20, '
               'defenses 20 (Neutron Shield, 20 counted): I = 1, T = 41')
        r.orbit(n, f'{D_LADY1}:1'); r.target(n, 870, mines=1, factories=20, defenses=20)
        r.expect('planet', (n,), dict(owner=1, pop=997))
        r.expect('dist', (n,), 'factories 20 or 19 (19 w.p. 20/41), defenses the same, independently; mines 0 '
                 'only when both stay at 20 (p 0.262), else 1; never 2')
    for n in (20, 22):
        r.case(f'D{n}', 'several fleets', f'two Lady1 fleets at player 1 planet {n}, as M: I = 3, A = 6, M = 3')
        r.orbit(n, f'{D_LADY1}:1'); r.orbit(n, f'{D_LADY1}:1')
        r.target(n, 870, mines=1, factories=20, defenses=20)
        r.expect('planet', (n,), dict(owner=1, pop=994))
        r.expect('dist', (n,), 'factories 19 or 18 (18 w.p. 19/41), defenses the same; mines 0 only when both '
                 'are 19 (p 0.288), else 1; player 0 gets 0x16f and player 1 0x179 (several installations, '
                 'defenses stopped a share)')
    r.case('U21', 'several fleets', 'two Lady1 fleets at player 1 planet 21: P 870, mines 1, no factories or '
           'defenses')
    r.orbit(21, f'{D_LADY1}:1'); r.orbit(21, f'{D_LADY1}:1')
    r.target(21, 870, mines=1, factories=0, defenses=0)
    r.expect('planet', (21,), dict(owner=1, pop=988, mines=0))
    r.expect('msg', (0,), '0x169 to player 0, 0x173 to player 1 (colonists and one installation)')
    r.case('U23', 'several fleets', 'two Lady1 fleets at player 1 planet 23: P 870, mines 10, no factories or '
           'defenses')
    r.orbit(23, f'{D_LADY1}:1'); r.orbit(23, f'{D_LADY1}:1')
    r.target(23, 870, mines=10, factories=0, defenses=0)
    r.expect('planet', (23,), dict(owner=1, pop=988, mines=6))
    r.expect('msg', (0,), '0x16a to player 0, 0x174 to player 1 (colonists and several installations)')
    out.append(r)

    # ------------------------------------------------------------------ TK-203
    r = cb_run('tk203', 'tech learned from scrapping at a starbase; player 1 tech 0 in every field',
               p1=(0,) * 6, cycles=RANDOM_CYCLES)
    r.h(SCOUT)
    for i, n in enumerate((0, 2)):
        r.case(f'S{n}', 'scrap tech', f'player 0 Scout (Long Hump 6: propulsion 3) scraps at player 1 planet {n} '
               'with an Orbital Fort (P 87)')
        r.orbit(n, f'{D_SCOUT}:1', task='scrap'); r.target(n, 87, starbase=True, mines=0, factories=0, defenses=0)
        r.expect('dist', (n,), ('attempt 1' if i == 0 else 'attempt 2, made only when S0 gained nothing (else no '
                 'draws and 0x141)') + ': 1/2 to pass, then up to 6 field draws until propulsion comes up: gain '
                 'w.p. 1/2 x (1 - (5/6)^6) = 0.333; a gain sends player 1 0x13d (field propulsion) instead of 0x141')
    r.case('S3', 'scrap tech', 'the same at player 1 planet 3 with no starbase (control)')
    r.orbit(3, f'{D_SCOUT}:1', task='scrap'); r.target(3, 87, mines=0, factories=0, defenses=0)
    r.expect('dist', (3,), '0x140 to player 1, no tech attempt')
    r.case('Y', 'scrap tech', 'player 1 tech at the end of the year')
    r.expect('dist', (1,), 'per stream: propulsion 0 or 1 (1 w.p. 0.555), never 2; every other field 0; the '
             'fleet owner (player 0) never gains')
    out.append(r)
    return out


def table():
    for r in runs():
        print(f'### {r.name.upper()}: {r.title}')
        print()
        cyc = '' if len(r.cycles) == 1 else f' Cycles {", ".join(map(str, r.cycles))}.'
        print(f'Game {r.game}, {r.years} year(s).{cyc}')
        print()
        print('| Case | Rule | Setup | Predicted |')
        print('|---|---|---|---|')
        for cid, rule, text in r.cases:
            pred = '; '.join(fmt3(k, a, v, y) for c, k, a, v, y in r.checks if c == cid)
            print(f'| {cid} | {rule} | {text} | {pred} |')
        print()


def fmt3(kind, args, v, year):
    y = '' if year == 1 else f' (year {year})'
    if kind == 'homeworld':
        return f'planet {args[0]} homeworld mark {v["mark"]}, player record names {v["record"]}' + y
    if kind in ('order', 'msg', 'dist'):
        return v + y
    return fmt(kind, args, v, year)


if __name__ == '__main__':
    if sys.argv[1:] == ['--table']:
        table()
    else:
        out = sys.argv[1] if len(sys.argv) > 1 else HERE
        for r in runs():
            r.write(out)
            print(r.name, len(r.cases), 'cases', len(r.checks), 'checks')
