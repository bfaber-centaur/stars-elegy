#!/usr/bin/env python3
"""Write the TK round-5 specs and client command files: manual cargo transfers.

Manual transfers are client orders (`manual-transfers.md`). Each run is two
pinned years from a Combat Lab start: year 1 makes player 0's `.M1`, the
client (`client-orders`, docs/ORACLE.md "Client orders") gives the
transfers in that turn, and year 2 runs with the client's `.X1`. Player 1's
targets start at P 87 and have grown to 100 when the orders are given.
Predictions restate the private binary reading as behavior (see
`manual-transfers.md`) and are written here before the runs; `check5.py`
summarizes the dumps.

Fleet numbers: the client's "fleet first" selects fleet 0 (#1, at player
0's homeworld 17) and "fleet next" then walks #8, #7, ... #2; the commands
follow that order, and the order dump says which fleet each record names.

  python3 experiments/tk/gen5.py OUTDIR      # write tkNNN.spec and tkNNN.cmds
  python3 experiments/tk/gen5.py --table     # print the prediction table
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import cb_run, grow, D_FREIGHTER  # noqa: E402
from gen3 import NOBODY  # noqa: E402


def land(troops, defenders):
    """Ground combat with no defenses (TAKEOVER.md): what the planet holds after."""
    st = troops * 110 // 100
    if defenders > st:
        return 1, defenders - defenders * st // defenders
    return 0, troops * ((st - defenders) * st // st) // st


def transfer_run(name, rel, title):
    r = cb_run(name, title, rel=rel)
    r.h(NOBODY)
    r.cmds = ['fleet first']
    f0 = r.orbit(17, f'{D_FREIGHTER}:1', plan=1)           # fleet 0: where "fleet first" starts
    assert f0 == 0
    steps = []                                            # client commands per fleet, in fleet order

    def hand(n, cargo, give, text, setup=None):
        i = r.orbit(n, f'{D_FREIGHTER}:1', plan=1, cargo=cargo)
        if setup: setup()
        steps.append((i, ['fleet xfer'] + [f'xfer {k} {v}' for k, v in give] + ['xfer ok']))
        return i

    if name == 'tk501':
        r.case('TK-410', 'manual drop', 'fleet 1 gives 30 colonists to player 1\'s homeworld 8 (starbase)')
        hand(8, (0, 0, 0, 30), [('col', 30)], '')
        r.expect('msg', (0, '0x058'), 'colonists lost; 0x058 to player 0; planet 8 unchanged apart from growth')
        r.case('TK-404', 'manual drop', 'fleet 2 gives 30 colonists to unowned planet 21')
        hand(21, (0, 0, 0, 30), [('col', 30)], '')
        r.expect('planet', (21,), dict(owner=-1))
        r.expect('msg', (0, '0x002'), '0x002 to player 0 (colonists 30, planet 21)')
        r.case('TK-405', 'manual gift', 'fleet 3 gives 100 ironium to player 1 planet 2 (surface 0)')
        hand(2, (100, 0, 0, 0), [('ir', 100)], '', lambda: r.target(2, 87, mines=0, factories=0, defenses=0))
        r.expect('planet', (2,), dict(owner=1, surface=[100, 0, 0]))
        r.expect('msg', (0, '0x042'), '0x042 to player 0 (fleet 3, 100, ironium, planet 2); 0x044 to player 1')
        r.case('TK-403', 'manual drop', 'player 1 planet 3 (100): fleet 4 unloads 50 colonists by its waypoint '
               'task (set in the client) and fleet 5 gives 200 by hand: one ground combat, 250 troops')
        i4 = r.orbit(3, f'{D_FREIGHTER}:1', plan=1, cargo=(0, 0, 0, 50))
        r.target(3, 87, mines=0, factories=0, defenses=0)
        steps.append((i4, ['wp select 0', 'wp task 1', 'wp transport 4 2']))
        hand(3, (0, 0, 0, 200), [('col', 200)], '')
        r.expect('planet', (3,), dict(owner=0, pop=grow(land(250, 100)[1])))
        r.case('TK-402', 'manual drop', 'fleet 6 gives 200 colonists to player 1 planet 14 (100)')
        hand(14, (0, 0, 0, 200), [('col', 200)], '', lambda: r.target(14, 87, mines=0, factories=0, defenses=0))
        r.expect('planet', (14,), dict(owner=0, pop=grow(land(200, 100)[1])))
        r.case('TK-401', 'manual drop', 'fleet 7 gives 30 colonists to player 1 planet 13 (100)')
        hand(13, (0, 0, 0, 30), [('col', 30)], '', lambda: r.target(13, 87, mines=0, factories=0, defenses=0))
        r.expect('planet', (13,), dict(owner=1, pop=grow(land(30, 100)[1])))
        r.expect('msg', (0, '0x000'), '0x000 to player 0 and 0x003 to player 1, as for an unload')
    else:
        r.case('TK-411', 'manual drop', 'players 0 and 1 are friends; fleet 1 gives 200 colonists to player 1 '
               'planet 14 (100)')
        hand(14, (0, 0, 0, 200), [('col', 200)], '', lambda: r.target(14, 87, mines=0, factories=0, defenses=0))
        r.expect('planet', (14,), dict(owner=0, pop=grow(land(200, 100)[1])))
        r.expect('msg', (0, '0x00c'), 'captured as between enemies (the drop code has no relation check): '
                 '0x00c to player 0, 0x007 to player 1')
        r.case('TK-412', 'manual gift', 'fleet 2 gives 100 ironium to player 1 planet 2 (friend)')
        hand(2, (100, 0, 0, 0), [('ir', 100)], '', lambda: r.target(2, 87, mines=0, factories=0, defenses=0))
        r.expect('planet', (2,), dict(owner=1, surface=[100, 0, 0]))
        r.expect('msg', (0, '0x042'), '0x042 to player 0, 0x044 to player 1')
    # "fleet first" is fleet 0; "fleet next" walks down from the highest number.
    for i, cmds in sorted(steps, reverse=True):
        r.cmds += ['fleet next'] + cmds
    return r


def runs():
    return [transfer_run('tk501', 2, 'manual cargo transfers to an enemy (client orders)'),
            transfer_run('tk502', 1, 'manual cargo transfers to a friend (client orders)')]


def table():
    for r in runs():
        print(f'### {r.name.upper()}: {r.title}')
        print()
        print('| Case | Setup | Predicted |')
        print('|---|---|---|')
        for cid, rule, text in r.cases:
            pred = []
            for c, k, a, v, y in r.checks:
                if c != cid:
                    continue
                if k == 'msg':
                    pred.append(v)
                else:
                    pred.append(f'planet {a[0]}: ' + ', '.join(f'{x} {y}' for x, y in v.items()))
            print(f'| {cid} | {text} | {"; ".join(pred)} |')
        print()


if __name__ == '__main__':
    if sys.argv[1:] == ['--table']:
        table()
    else:
        out = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
        for r in runs():
            r.write(out)
            with open(os.path.join(out, r.name + '.cmds'), 'w') as f:
                f.write(f'# {r.name}: {r.title} (experiments/tk/gen5.py)\n' + '\n'.join(r.cmds) + '\n')
            print(r.name, len(r.cases), 'cases')
