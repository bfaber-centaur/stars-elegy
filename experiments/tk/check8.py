#!/usr/bin/env python3
"""Summarize the TK round-8 run (a gift to a fleet that moves away) against gen8.py.

  python3 experiments/tk/check8.py RUNDIR

RUNDIR/tk505/y2/ holds the second year's after.dump and events.txt. Each
receiver's distance moved, cargo and fuel are compared with the control it should match and the one it would
match if the gift were credited after movement.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check2 import parse  # noqa: E402
from check3 import events  # noqa: E402
from gen8 import runs  # noqa: E402

KEYS = ('dx', 'dy', 'fe', 'fuel')


def state(r, st, i):
    """Player 1 fleet i: distance moved from its start, cargo and fuel."""
    f = st['fleet'].get((1, i)) or {}
    x0, y0 = r.start[i]
    return dict(dx=f.get('x', x0) - x0, dy=f.get('y', y0) - y0, fe=f.get('fe'), fuel=f.get('fuel'))


def main(rundir):
    for r in runs():
        y2 = os.path.join(rundir, r.name, 'y2')
        if not os.path.exists(os.path.join(y2, 'after.dump')):
            print(r.name, 'NODATA')
            continue
        st = parse(os.path.join(y2, 'after.dump'))
        ev = events(os.path.join(y2, 'events.txt'))
        print(r.name)
        for k, i in r.controls.items():
            print(f'  control {k} fleet 1/{i}:', state(r, st, i))
        for cid, kind, args, want, year in r.checks:
            if kind == 'fleet':
                obj = st['fleet'].get(tuple(args)) or {}
                got = {k: obj.get(k) for k in want}
                print(f'  {cid} fleet {args[0]}/{args[1]}: {"OK" if got == want else "MISS " + str(got)}')
            elif kind == 'same':
                got = state(r, st, args[1])
                ctl = state(r, st, r.controls[args[2]])
                alt = state(r, st, r.controls[args[3]])
                print(f'  {cid} fleet {args[0]}/{args[1]} {got}: '
                      f'{"OK matches " + args[2] if got == ctl else "MISS (" + args[2] + " " + str(ctl) + ")"}; '
                      f'{args[3]} {alt}')
            elif kind == 'nomsg':
                seen = [(p, k, s) for p, k, s in ev if k in args]
                print(f'  {cid} none of {"/".join(args)}: {"OK" if not seen else "SEEN " + str(seen)}')
        print('  messages:', ' '.join(f'P{p}:{k}{s}' for p, k, s in ev if k not in ('0x03f',)))


if __name__ == '__main__':
    main(sys.argv[1])
