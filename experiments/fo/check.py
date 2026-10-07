#!/usr/bin/env python3
"""Compare FO runs with the predictions in gen.py.

  python3 experiments/fo/check.py RUNDIR

RUNDIR/<name>/after.dump and before.dump are `combatlab dump` output of the
generated year and the start (as pinned-turn writes them). Prints one line
per check: OK, MISS (with the observed value) or NODATA.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import runs  # noqa: E402


def parse(path):
    """Planets, fleets and designs of the host file in a combatlab dump."""
    st = dict(planet={}, fleet={}, design={})
    last = None
    for line in open(path):
        m = re.match(r'\S+\.HST (.*)', line)
        if not m:
            continue
        s = m.group(1)
        if s.startswith('pdetail '):
            n = int(s.split()[1])
            d = dict(kv.split('=', 1) for kv in s.split()[2:])
            p = dict(owner=int(d['owner']))
            if 'surface' in d:
                p['surface'] = [int(x) for x in d['surface'].split('/')]
                p['pop'] = int(d['pop'])
            st['planet'][n] = p
            last = None
        elif s.startswith('fleet '):
            d = dict(kv.split('=', 1) for kv in s.split()[1:] if '=' in kv)
            c = [int(x) for x in d['cargo'].split('/')]
            dmg = {int(k[3:]): tuple(int(x) for x in v.rstrip('%').split('/'))
                   for k, v in d.items() if k.startswith('dmg')}
            last = dict(fe=c[0], bo=c[1], ge=c[2], col=c[3], fuel=int(d['fuel']), ships=d['ships'],
                        x=int(d['x']), y=int(d['y']), dmg=dmg, owner=int(d['owner']))
            st['fleet'][(int(d['owner']), int(d['id']))] = last
        elif s.startswith('  wp ') and last is not None and 'task' not in last:
            last['task'] = int(dict(kv.split('=', 1) for kv in s.split() if '=' in kv)['task'])
        elif s.startswith('design '):
            m2 = re.match(r'design owner=(\d+) n=(\d+) .*:: (.*)', s)
            st['design'][(int(m2.group(1)), int(m2.group(2)))] = m2.group(3)
            last = None
        else:
            last = None
    return st


def check(kind, args, want, st):
    if kind == 'planet':
        p = st['planet'].get(args[0])
        if p is None:
            return 'NODATA', None
        got = {k: p.get(k) for k in want}
        return ('OK' if got == want else 'MISS'), got
    if kind == 'fleet':
        f = st['fleet'].get(args)
        if f is None:
            return 'MISS', 'gone'
        got = {k: f[k] for k in want}
        return ('OK' if got == want else 'MISS'), got
    if kind == 'nofleet':
        f = st['fleet'].get(args)
        return ('OK' if f is None else 'MISS'), f
    if kind in ('fleetat', 'nofleetat'):
        hits = [(k, f) for k, f in st['fleet'].items() if k[0] == args[0] and (f['x'], f['y']) == args[1:]]
        if kind == 'nofleetat':
            return ('OK' if not hits else 'MISS'), hits
        if len(hits) != 1:
            return 'MISS', hits
        (owner, fid), f = hits[0]
        slots = [tuple(int(v) for v in s.split(':')) for s in f['ships'].split(',')]
        got = dict(n=sum(c for _, c in slots), fe=f['fe'], fuel=f['fuel'],
                   hull=st['design'].get((owner, slots[0][0]), '').split(',')[0])
        got = {k: got[k] for k in want}
        return ('OK' if got == want else 'MISS'), dict(got, id=fid, ships=f['ships'])
    return 'NODATA', None


def main(rd):
    for r in runs():
        p = os.path.join(rd, r.name, 'after.dump')
        if not os.path.exists(p):
            print(f'{r.name}: no run')
            continue
        st = parse(p)
        for cid, kind, args, want, year in r.checks:
            res, got = check(kind, args, want, st)
            print(f'{r.name} {cid} {kind} {args}: {res} want={want} got={got}')


if __name__ == '__main__':
    main(sys.argv[1])
