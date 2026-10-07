#!/usr/bin/env python3
"""Summarize TK round-6 runs (bombing message variants) against gen6.py.

  python3 experiments/tk/check6.py RUNDIR

RUNDIR/<name>/run-20000/ holds after.dump and events.txt. Planet checks print OK or MISS; message
checks print whether that kind reached that player, with every message of
the year listed below.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check2 import parse  # noqa: E402
from check3 import events  # noqa: E402
from gen6 import runs  # noqa: E402


def main(rundir):
    for r in runs():
        y2 = os.path.join(rundir, r.name, 'run-20000')
        if not os.path.exists(os.path.join(y2, 'after.dump')):
            print(r.name, 'NODATA')
            continue
        st = parse(os.path.join(y2, 'after.dump'))
        ev = events(os.path.join(y2, 'events.txt'))
        print(r.name)
        for cid, kind, args, want, year in r.checks:
            if kind == 'planet':
                obj = st['planet'].get(args[0]) or {}
                # a planet with no installations left has no installations block
                got = {k: obj.get(k, -1 if k == 'owner' else 0) for k in want}
                got = {k: list(v) if isinstance(v, tuple) else v for k, v in got.items()}
                print(f'  {cid} planet {args[0]}: {"OK" if got == want else "MISS " + str(got)}')
            elif kind == 'msg':
                seen = [s for p, k, s in ev if p == args[0] and k == args[1]]
                print(f'  {cid} {args[1]} to player {args[0]}: {"seen " + str(seen) if seen else "NOT SEEN"}')
        print('  messages:', ' '.join(f'P{p}:{k}{s}' for p, k, s in ev if k not in ('0x03f',)))


if __name__ == '__main__':
    main(sys.argv[1])
