#!/usr/bin/env python3
"""Compare TK round-2 runs with the predictions in gen2.py.

  python3 experiments/tk/check2.py RUNDIR

RUNDIR/<name>/run/after.dump is a `combatlab dump` of the generated year
(as pinned-turn writes it); a second year, where a run has one, is in
RUNDIR/<name>/run-y2/. Runs with several cycles values use run-<cycles>.
Prints one line per check: OK, MISS (with the observed value) or NODATA.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import runs  # noqa: E402


def parse(path):
    """The host file's state from a combatlab dump (lines of the .HST only)."""
    st = dict(planet={}, sb={}, queue={}, fleet={}, design={}, player={}, things=[])
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
            for k in ('env', 'orig'):
                if k in d:
                    p[k] = tuple(int(x) for x in d[k].split('/'))
            for k in ('mines', 'factories', 'defenses', 'excess'):
                if k in d:
                    p[k] = int(d[k])
            if 'leftover' in d:
                p['leftover'] = d['leftover'] == 'true'
            st['planet'][n] = p
        elif s.startswith('planet '):
            t = s.split()
            d = dict(kv.split('=', 1) for kv in t[2:] if '=' in kv)
            st['sb'][int(t[1])] = int(d['design']) if d.get('starbase') == 'true' else None
        elif s.startswith('queue '):
            d = dict(kv.split('=', 1) for kv in s.split()[1:])
            items = [tuple(int(x) for x in it.split(':')) for it in d.get('items', '').split(',') if it]
            st['queue'][int(d['planet'])] = [(i, c) for i, c, _, _ in items]
        elif s.startswith('fleet '):
            d = dict(kv.split('=', 1) for kv in s.split()[1:] if '=' in kv)
            c = [int(x) for x in d['cargo'].split('/')]
            st['fleet'][(int(d['owner']), int(d['id']))] = dict(
                fe=c[0], bo=c[1], ge=c[2], col=c[3], ships=d['ships'], x=int(d['x']), y=int(d['y']))
        elif s.startswith('design '):
            m2 = re.match(r'design owner=(\d+) n=(\d+) .*:: (.*)', s)
            st['design'][(int(m2.group(1)), int(m2.group(2)))] = m2.group(3)
        elif s.startswith('player '):
            t = s.split()
            st['player'][int(t[1])] = dict(kv.split('=', 1) for kv in t[2:] if '=' in kv)
        elif s.startswith('thing') or s.startswith('object'):
            st['things'].append(s)
    return st


def check(kind, args, want, st, before):
    if kind == 'planet':
        p = st['planet'].get(args[0])
        if p is None:
            return 'NODATA', None
        got = {k: p.get(k, [0, 0, 0] if k == 'surface' else None) for k in want}
        got = {k: list(v) if isinstance(v, tuple) else v for k, v in got.items()}
        w = {k: list(v) if isinstance(v, tuple) else v for k, v in want.items()}
        return ('OK' if got == w else 'MISS'), got
    if kind == 'queue':
        got = st['queue'].get(args[0], [])
        return ('OK' if got == list(want) else 'MISS'), got
    if kind == 'starbase':
        got = st['sb'].get(args[0])
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
    if kind == 'design':
        got = st['design'].get(args)
        was = before['design'].get(args)
        res = 'kept' if got == was else 'part removed'
        return ('OK' if res == want else 'MISS'), got
    if kind == 'salvage':
        # salvage is written as a packet-type object with no destination (dest=1023)
        for t in st['things']:
            d = dict(kv.split('=', 1) for kv in t.split() if '=' in kv)
            if d.get('x') == str(args[0]) and d.get('y') == str(args[1]):
                got = [int(x) for x in d['cargo'].split('/')]
                return ('OK' if got == list(want) and d.get('dest') == '1023' else 'MISS'), t
        return 'MISS', None
    if kind == 'tech':
        pl = st['player'].get(args[0])
        lv = {f: int(pl[f]) for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio')}
        ok = lv['weapons'] in (3, 4) and all(v == 3 for f, v in lv.items() if f != 'weapons')
        return ('OK' if ok else 'MISS'), lv
    return 'NODATA', None


def main(rd):
    for r in runs():
        base = os.path.join(rd, r.name)
        if not os.path.isdir(base):
            print(f'{r.name}: no run')
            continue
        dirs = sorted(d for d in os.listdir(base)
                      if d.startswith('run') and d != 'run-y2' and os.path.isdir(os.path.join(base, d)))
        for d in dirs:
            states = {}
            for y, sub in ((1, d), (2, 'run-y2')):
                p = os.path.join(base, sub, 'after.dump')
                if os.path.exists(p) and (y == 1 or d == 'run'):
                    states[y] = parse(p)
            before = parse(os.path.join(base, d, 'before.dump'))
            for cid, kind, args, want, year in r.checks:
                if year not in states:
                    print(f'{r.name}/{d} {cid} {kind} {args} year {year}: NODATA')
                    continue
                res, got = check(kind, args, want, states[year], before)
                print(f'{r.name}/{d} {cid} {kind} {args} y{year}: {res} want={want} got={got}')


if __name__ == '__main__':
    main(sys.argv[1])
