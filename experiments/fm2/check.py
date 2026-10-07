#!/usr/bin/env python3
"""Compare FM round-2 runs with the predictions in gen.py.

  python3 experiments/fm2/check.py RUNDIR

RUNDIR/<name>/run/after.dump is a `combatlab dump` of the generated year
(pinned-turn output); a second year is in RUNDIR/<name>/run-y2/. Prints one
line per check: OK, MISS (with the observed value) or NODATA.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import runs, D  # noqa: E402
from model import Fleet  # noqa: E402


def parse(path):
    st = dict(fleet={}, design={})
    last = None
    for line in open(path):
        m = re.match(r'\S+\.HST (.*)', line)
        if not m:
            continue
        s = m.group(1)
        if s.startswith('fleet '):
            d = dict(kv.split('=', 1) for kv in s.split()[1:] if '=' in kv)
            c = [int(x) for x in d['cargo'].split('/')]
            last = dict(fe=c[0], bo=c[1], ge=c[2], col=c[3], fuel=int(d['fuel']), ships=d['ships'],
                        x=int(d['x']), y=int(d['y']), wps=[])
            st['fleet'][(int(d['owner']), int(d['id']))] = last
        elif s.startswith('  wp ') and last is not None:
            d = dict(kv.split('=', 1) for kv in s.split() if '=' in kv)
            last['wps'].append(dict(x=int(d['x']), y=int(d['y']), warp=int(d['warp']), task=int(d['task'])))
        else:
            last = None
    return st


def slots(ships):
    return {int(a): int(b) for a, b in (s.split(':') for s in ships.split(',') if s)}


def check(kind, args, want, st):
    if kind == 'fleet':
        f = st['fleet'].get(args)
        if f is None:
            return 'MISS', 'gone'
        g = dict(f)
        g['warp'] = f['wps'][1]['warp'] if len(f['wps']) > 1 else None
        got = {k: g[k] for k in want}
        return ('OK' if got == want else 'MISS'), got
    if kind == 'ce':
        stay = moved = other = 0
        for key in args:
            f = st['fleet'][key]
            if (f['x'], f['y']) == want['start'] and f['fuel'] == 300 and len(f['wps']) == 2:
                stay += 1
            elif (f['x'], f['y']) == want['dest']:
                moved += 1
            else:
                other += 1
        ok = other == 0 and want['lo'] <= stay <= want['hi']
        return ('OK' if ok else 'MISS'), dict(stayed=stay, moved=moved, other=other)
    if kind == 'warp10':
        f = st['fleet'].get(args)
        if f is None:
            return 'MISS', 'gone'
        n = slots(f['ships']).get(want['design'], 0)
        k = want['n0'] - n
        fuel = want['fuel0'] - want['fuel0'] * k // want['n0']
        fuel -= Fleet(0, 0, 0, [(D[want['design']], n)], fuel).cost(10, want['dist'])
        got = dict(lost=k, fuel=f['fuel'], x=f['x'], y=f['y'])
        ok = want['lo'] <= k <= want['hi'] and (f['x'], f['y']) == (want['x'], want['y']) and f['fuel'] == fuel
        return ('OK' if ok else 'MISS'), dict(got, fuel_predicted=fuel)
    if kind == 'warp10mix':
        f = st['fleet'].get(args)
        if f is None:
            return 'MISS', 'gone'
        sl = slots(f['ships'])
        k = 50 - sl.get(want['lost_design'], 0)
        ok = sl.get(2) == 50 and want['lo'] <= k <= want['hi'] and (f['x'], f['y']) == (want['x'], want['y'])
        return ('OK' if ok else 'MISS'), dict(ships=f['ships'], lost=k, x=f['x'], y=f['y'], fuel=f['fuel'])
    return 'NODATA', None


def main(rd):
    for r in runs():
        states = {}
        for y, sub in ((1, 'run'), (2, 'run-y2')):
            p = os.path.join(rd, r.name, sub, 'after.dump')
            if os.path.exists(p):
                states[y] = parse(p)
        for cid, kind, args, want, year in r.checks:
            if year not in states:
                print(f'{r.name} {cid} {kind} {args} y{year}: NODATA')
                continue
            res, got = check(kind, args, want, states[year])
            print(f'{r.name} {cid} {kind} {args} y{year}: {res} want={want} got={got}')


if __name__ == '__main__':
    main(sys.argv[1])
