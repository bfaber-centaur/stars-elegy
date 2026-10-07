#!/usr/bin/env python3
"""Write the TK round-7 specs and client command files: manual gifts to
another player's fleet.

Same shape as round 5 (`gen5.py`): year 1 from a Combat Lab start makes
player 0's `.M1`, the client (`client-orders`, docs/ORACLE.md "Client
orders", fleet panel "Other Fleets Here" > Cargo) gives the transfers, and
year 2 runs with the client's `.X1`. The predictions are the revised ones
in `manual-transfers.md` ("Revised predictions for fleet receivers"),
committed before these runs; `check7.py` summarizes the year-2 dumps.

Each giver sits with one player 1 Freighter and nothing else, in deep space
(TK-406..409) or at a player 1 planet without a starbase (TK-413), so
"Other Fleets Here" item 0 is the receiver.

  python3 experiments/tk/gen7.py OUTDIR      # write tkNNN.spec and tkNNN.cmds
  python3 experiments/tk/gen7.py --table     # print the prediction table
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import cb_run, D_FREIGHTER  # noqa: E402
from gen3 import NOBODY  # noqa: E402

P1_FREIGHTER = 0
SPOTS = [(1010, 1010), (1010, 1110), (1010, 1210), (1010, 1310), (1050, 1020)]


def fleet(r, owner, at, ships, cargo=(0, 0, 0, 0), fuel=200, task=None, planet=None):
    i = r._fleet(owner)
    s = f"fleet {owner} {i} " + (f"planet {planet} " if planet is not None else "") + \
        f"at {at[0]} {at[1]} ships {ships} plan {1 if owner == 0 else 0} fuel {fuel}"
    s += " cargo " + " ".join(str(c) for c in cargo)
    if task: s += f" task {task}"
    r.lines.append(s)
    return i


def gift_run(name, rel, title):
    r = cb_run(name, title, rel=rel)
    r.h(NOBODY)
    r.h(f'design 1 {P1_FREIGHTER} Medium Freighter, 1 Long Hump 6, empty, empty = Freighter')
    r.cmds = ['fleet first']
    f0 = r.orbit(17, f'{D_FREIGHTER}:1', plan=1)
    assert f0 == 0
    steps = []
    spots = iter(SPOTS)

    def pair(give_cargo, give_fuel, recv_cargo, recv_fuel, xfer, at=None, planet=None, task=None):
        at = at or next(spots)
        g = fleet(r, 0, at, f'{D_FREIGHTER}:1', give_cargo, give_fuel, planet=planet)
        v = fleet(r, 1, at, f'{P1_FREIGHTER}:1', recv_cargo, recv_fuel, task=task, planet=planet)
        steps.append((g, ['fleet other 0', 'fleet cargo'] + [f'xfer {k} {n}' for k, n in xfer] + ['xfer ok']))
        return g, v

    if name == 'tk503':
        r.case('TK-406', 'manual gift', 'giver offers 100 ironium to a player 1 Freighter holding 160 kT (50 free)')
        g, v = pair((100, 0, 0, 0), 200, (160, 0, 0, 0), 200, [('ir', 100)])
        r.expect('fleet', (1, v), dict(fe=210))
        r.expect('nomsg', ('0x046', '0x048'), 'credited at order time: receiver full at 210; no 0x046/0x048 '
                 '(the client may cap the order at 50; 0x0dd to player 0 if 100 reached the host)')
        r.case('TK-407', 'manual gift', 'giver offers 100 ironium to a full player 1 Freighter (210 kT)')
        g, v = pair((100, 0, 0, 0), 200, (210, 0, 0, 0), 200, [('ir', 100)])
        r.expect('fleet', (1, v), dict(fe=210))
        r.expect('nomsg', ('0x04a', '0x04c'), 'nothing received; no 0x04a/0x04c (the client may refuse the order)')
        r.case('TK-408', 'manual gift', 'giver gives 20 colonists to an empty player 1 Freighter')
        g, v = pair((0, 0, 0, 20), 200, (0, 0, 0, 0), 200, [('col', 20)])
        r.expect('fleet', (1, v), dict(col=20))
        r.expect('fleet', (0, g), dict(col=0))
        r.expect('nomsg', ('0x042', '0x044'), 'received in full at order time; no message to either player')
        r.case('TK-409', 'manual gift', 'giver gives 50 mg of fuel to a player 1 Freighter with 100 mg')
        g, v = pair((0, 0, 0, 0), 200, (0, 0, 0, 0), 100, [('fuel', 50)])
        r.expect('fleet', (1, v), dict(fuel=150))
        r.expect('fleet', (0, g), dict(fuel=150))
        r.expect('nomsg', ('0x043', '0x045'), 'received at order time; no message')
        r.case('TK-413', 'manual gift', 'at player 1 planet 2 (P 87, no starbase, surface 0): giver gives 100 '
               'ironium to a player 1 Freighter whose waypoint-0 task is unload all')
        g, v = pair((100, 0, 0, 0), 200, (0, 0, 0, 0), 200, [('ir', 100)], at=r.xy[2], planet=2,
                    task='transport 2:0,-,-,-,-')
        r.target(2, 87, mines=0, factories=0, defenses=0)
        r.expect('fleet', (1, v), dict(fe=0))
        r.expect('planet', (2,), dict(owner=1, surface=[100, 0, 0]))
        r.expect('msg', (1, '0x02d'), 'the receiver unloads the gift before movement the same year: 0x02d to '
                 'player 1 (a queued gift would arrive after the unload and stay in the hold)')
    else:
        r.case('TK-414', 'manual gift', 'players 0 and 1 are friends; giver gives 20 colonists to an empty '
               'player 1 Freighter')
        g, v = pair((0, 0, 0, 20), 200, (0, 0, 0, 0), 200, [('col', 20)])
        r.expect('fleet', (1, v), dict(col=20))
        r.expect('nomsg', ('0x042', '0x044'), 'as TK-408')
    for i, cmds in sorted(steps, reverse=True):
        r.cmds += ['fleet next'] + cmds
    return r


def runs():
    return [gift_run('tk503', 2, 'manual gifts to an enemy fleet (client orders)'),
            gift_run('tk504', 1, 'manual gifts to a friend\'s fleet (client orders)')]


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
                if k in ('msg', 'nomsg'):
                    pred.append(v)
                else:
                    who = f'planet {a[0]}' if k == 'planet' else f'fleet {a[0]}/{a[1]}'
                    pred.append(f'{who}: ' + ', '.join(f'{x} {y}' for x, y in v.items()))
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
                f.write(f'# {r.name}: {r.title} (experiments/tk/gen7.py)\n' + '\n'.join(r.cmds) + '\n')
            print(r.name, len(r.cases), 'cases')
