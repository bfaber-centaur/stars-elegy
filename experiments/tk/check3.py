#!/usr/bin/env python3
"""Summarize TK round-3 runs against the predictions in gen3.py.

  python3 experiments/tk/check3.py RUNDIR

RUNDIR/<name>/run-<cycles>/ holds after.dump (combatlab dump) and
events.txt (tools/fleetlab/events.py); TK-201's second year is in
run-y2-<cycles>/. Deterministic checks print OK or MISS; the random cases
print one row per cycles value so streams can be counted.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check2 import parse  # noqa: E402
from gen3 import runs  # noqa: E402


def events(path):
    out = []
    for line in open(path):
        m = re.match(r'\S+ M(\d) (0x[0-9a-f]+) focus=(\S+) slots=\[(.*)\]', line)
        if m:
            out.append((int(m.group(1)) - 1, m.group(2), [int(x) for x in m.group(4).split(',') if x.strip()]))
    return out


def homeworlds(path):
    marks, rec = {}, {}
    for line in open(path):
        m = re.search(r'\.HST planet (\d+) owner=(-?\d+) homeworld=(\w+)', line)
        if m:
            marks[int(m.group(1))] = m.group(3) == 'true'
        m = re.search(r'\.HST player (\d+) .*homeworld=(\d+)', line)
        if m:
            rec[int(m.group(1))] = int(m.group(2))
    return marks, rec


def check_simple(r, st, run, y2=None):
    for cid, kind, args, want, year in r.checks:
        s = st if year == 1 else y2
        if kind in ('planet', 'fleet'):
            obj = s['planet'].get(args[0]) if kind == 'planet' else s['fleet'].get(args)
            got = {k: (obj or {}).get(k, -1 if k == 'owner' else None) for k in want}
            print(f'  {cid} {kind} {args}: {"OK" if got == want else "MISS " + str(got)}')
        elif kind == 'homeworld':
            marks, rec = homeworlds(os.path.join(run if year == 1 else run.replace('run-', 'run-y2-'), 'after.dump'))
            owner = want.get('owner_record', 0)
            ok = marks.get(args[0]) == want['mark'] and rec.get(owner) == want['record']
            print(f'  {cid} homeworld {args[0]} year {year}: {"OK" if ok else "MISS"} mark={marks.get(args[0])} '
                  f'record={rec.get(owner)}')


def main(rundir):
    for r in runs():
        base = os.path.join(rundir, r.name)
        for c in r.cycles:
            run = os.path.join(base, f'run-{c}')
            if not os.path.exists(os.path.join(run, 'after.dump')):
                print(r.name, c, 'NODATA')
                continue
            st = parse(os.path.join(run, 'after.dump'))
            ev = events(os.path.join(run, 'events.txt'))
            if r.name == 'tk201':
                y2run = os.path.join(base, f'run-y2-{c}', 'after.dump')
                y2 = parse(y2run) if os.path.exists(y2run) else None
                print(f'{r.name} cycles {c}')
                check_simple(r, st, run, y2)
                m0 = [(k, s) for p, k, s in ev if p == 0]
                print('  player 0 messages:', ' '.join(f'{k}{s}' for k, s in m0 if k not in ('0x03f',)))
            elif r.name == 'tk202':
                row = []
                for n in (0, 2, 3, 9, 13, 14, 20, 22, 21, 23):
                    p = st['planet'][n]
                    row.append(f'{n}:{p["pop"]}/m{p["mines"]}/f{p["factories"]}/d{p["defenses"]}')
                kinds = sorted({k for _, k, _ in ev if k >= '0x060' and k not in ('0x07f', '0x080', '0x081', '0x082',
                                                                               '0x0a9')})
                print(f'{r.name} {c:>5}', ' '.join(row), ' kinds', ','.join(kinds))
            elif r.name == 'tk203':
                p1 = st['player'][1]
                tech = '/'.join(p1[f] for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio'))
                msgs = [(k, s) for p, k, s in ev if p == 1 and k in ('0x13c', '0x13d', '0x140', '0x141')]
                print(f'{r.name} {c:>5} player 1 tech {tech} accum {p1["accum"]}', msgs)


if __name__ == '__main__':
    main(sys.argv[1])
