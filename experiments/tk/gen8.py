#!/usr/bin/env python3
"""Write the TK round-8 spec and client command file: a manual gift to
another player's fleet that moves away the same year.

Question: is a manual cross-owner gift credited in place when the order is
replayed (before movement), or queued and credited in a later pass (after
movement, with 0x042-0x04d)? Same shape as round 7 (`gen7.py`), with
controls that differ from the receivers only in the cargo or fuel the gift
would add.

Year 1 is the Combat Lab start; the year-2 movement must happen in the
client's year, so each player 1 fleet's waypoint 1 is its own position
(reached in year 1) and waypoint 2 lies 49 ly east at warp 7 (reached in
year 2). `check8.py` reads the year-2 dump.

  python3 experiments/tk/gen8.py OUTDIR      # write tk505.spec and tk505.cmds
  python3 experiments/tk/gen8.py --table     # print the prediction table
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import cb_run, D_FREIGHTER  # noqa: E402
from gen3 import NOBODY  # noqa: E402
from gen7 import P1_FREIGHTER, SPOTS  # noqa: E402

LEG = 49


def mover(r, at, cargo, fuel):
    i = r._fleet(1)
    r.start = getattr(r, 'start', {})
    r.start[i] = at
    r.lines.append(f"fleet 1 {i} at {at[0]} {at[1]} ships {P1_FREIGHTER}:1 plan 0 fuel {fuel} "
                   f"cargo {' '.join(str(c) for c in cargo)} to {at[0]} {at[1]} warp 7 "
                   f"to {at[0] + LEG} {at[1]} warp 7")
    return i


def run():
    r = cb_run('tk505', 'manual gifts to a player 1 fleet that moves away (client orders)', rel=2)
    r.h(NOBODY)
    r.h(f'design 1 {P1_FREIGHTER} Medium Freighter, 1 Long Hump 6, empty, empty = Freighter')
    r.cmds = ['fleet first']
    f0 = r.orbit(17, f'{D_FREIGHTER}:1', plan=1)
    assert f0 == 0
    steps = []
    spots = iter(SPOTS)

    def giver(at, cargo, fuel, xfer):
        g = r._fleet(0)
        r.lines.append(f"fleet 0 {g} at {at[0]} {at[1]} ships {D_FREIGHTER}:1 plan 1 fuel {fuel} "
                       f"cargo {' '.join(str(c) for c in cargo)}")
        steps.append((g, ['fleet other 0', 'fleet cargo'] + [f'xfer {k} {n}' for k, n in xfer] + ['xfer ok']))
        return g

    # Controls first so their ids are fixed: same hull, same legs, no gift.
    r.lines.append('# controls (player 1 Freighters, same legs, no gift): C0 empty with 0 mg; '
                   'C200 empty with 200 mg; C100 with 100 kT ironium and 200 mg')
    c0 = mover(r, next(spots), (0, 0, 0, 0), 0)
    c200 = mover(r, next(spots), (0, 0, 0, 0), 200)
    c100 = mover(r, next(spots), (100, 0, 0, 0), 200)
    r.controls = dict(C0=c0, C200=c200, C100=c100)

    r.case('TK-415', 'manual gift', 'giver gives 200 mg of fuel to an empty player 1 Freighter with 0 mg '
           'that moves 49 ly east this year')
    at = next(spots)
    g = giver(at, (0, 0, 0, 0), 300, [('fuel', 200)])
    v = mover(r, at, (0, 0, 0, 0), 0)
    r.expect('fleet', (0, g), dict(fuel=100))
    r.expect('same', (1, v, 'C200', 'C0'), 'credited when the order is replayed, before movement: the receiver moves '
             'and burns fuel exactly like C200 (same x, y and fuel), not like C0. A credit after movement '
             'would leave it where C0 is, with C0\'s fuel + 200')
    r.expect('nomsg', ('0x043', '0x045'), 'no gift message to either player')

    r.case('TK-416', 'manual gift', 'giver gives 100 kT ironium to an empty player 1 Freighter with 200 mg '
           'that moves 49 ly east this year')
    at = next(spots)
    g = giver(at, (100, 0, 0, 0), 200, [('ir', 100)])
    v = mover(r, at, (0, 0, 0, 0), 200)
    r.expect('fleet', (0, g), dict(fe=0))
    r.expect('same', (1, v, 'C100', 'C200'), 'the 100 kT travels in the hold: same x, y, cargo and fuel as C100 '
             '(fuel differs from C200 only if 100 kT changes the burn). A credit after movement would burn '
             'like C200 and add the ironium at the destination')
    r.expect('nomsg', ('0x042', '0x044'), 'no gift message to either player')

    for i, cmds in sorted(steps, reverse=True):
        r.cmds += ['fleet next'] + cmds
    return r


def runs():
    return [run()]


def table():
    for r in runs():
        print(f'### {r.name.upper()}: {r.title}')
        print()
        print('Controls: ' + ', '.join(f'{k} = fleet 1/{v}' for k, v in r.controls.items()) + '.')
        print()
        print('| Case | Setup | Predicted |')
        print('|---|---|---|')
        for cid, rule, text in r.cases:
            pred = []
            for c, k, a, v, y in r.checks:
                if c != cid:
                    continue
                if k == 'fleet':
                    pred.append(f'fleet {a[0]}/{a[1]}: ' + ', '.join(f'{x} {y}' for x, y in v.items()))
                elif k == 'same':
                    pred.append(f'fleet {a[0]}/{a[1]} matches {a[2]}: {v}')
                else:
                    pred.append(v)
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
                f.write(f'# {r.name}: {r.title} (experiments/tk/gen8.py)\n' + '\n'.join(r.cmds) + '\n')
            print(r.name, len(r.cases), 'cases')
