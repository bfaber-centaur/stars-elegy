#!/usr/bin/env python3
"""Summarize TK round-4 runs against the predictions in gen4.py.

  python3 experiments/tk/check4.py RUNDIR

RUNDIR/<name>/run-<cycles>/ holds after.dump (combatlab dump) and
events.txt (tools/fleetlab/events.py). Deterministic checks print OK or
MISS; artifact and scrap cases print the 0x05e / 0x13c / 0x13d / 0x141
messages and research per cycles value.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check2 import parse  # noqa: E402
from check3 import events  # noqa: E402
from gen4 import runs  # noqa: E402


def main(rundir):
    for r in runs():
        for c in r.cycles:
            run = os.path.join(rundir, r.name, f'run-{c}')
            if not os.path.exists(os.path.join(run, 'after.dump')):
                print(r.name, c, 'NODATA')
                continue
            st = parse(os.path.join(run, 'after.dump'))
            ev = events(os.path.join(run, 'events.txt'))
            print(f'{r.name} cycles {c}')
            for cid, kind, args, want, year in r.checks:
                if kind in ('planet', 'fleet'):
                    obj = st['planet'].get(args[0]) if kind == 'planet' else st['fleet'].get(args)
                    got = {k: (obj or {}).get(k, -1 if k == 'owner' else None) for k in want}
                    print(f'  {cid} {kind} {args}: {"OK" if got == want else "MISS " + str(got)}')
            msgs = [(p, k, s) for p, k, s in ev if k in ('0x05e', '0x13c', '0x13d', '0x141', '0x157')]
            if msgs:
                print('  messages:', ' '.join(f'P{p}:{k}{s}' for p, k, s in msgs))
            for p in (0, 1):
                pl = st['player'][p]
                tech = '/'.join(pl[f] for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio'))
                print(f'  player {p} tech {tech} accum {pl["accum"]}')


if __name__ == '__main__':
    main(sys.argv[1])
