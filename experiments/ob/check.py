#!/usr/bin/env python3
"""Compare one OB- run's generated host file with the gen.py predictions.

  python3 experiments/ob/check.py OB-001 RUNDIR/after.dump [RUNDIR/before.dump]

Reads the `combatlab dump` of the generated CB.HST (lines from
raw/after/CB.HST) and prints one line per case: HELD, CONTRADICTED or
OBSERVED (no single predicted value), with the observed value.
"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen


def kv(line):
    return dict(re.findall(r'(\w+)=(\S+)', line))


def load(path, which='after'):
    things, planets, fleets, players, wps = [], {}, {}, {}, {}
    last = None
    for line in open(path):
        if '/raw/%s/CB.HST ' % which not in line:
            continue
        body = line.split('CB.HST ', 1)[1]
        if body.startswith('thing id='):
            d = kv(body)
            things.append(d)
        elif body.startswith('pdetail'):
            n = int(body.split()[1])
            planets[n] = kv(body)
        elif body.startswith('fleet owner='):
            d = kv(body)
            last = (int(d['owner']), int(d['id']))
            fleets[last] = d
            wps[last] = []
        elif body.startswith('  wp '):
            wps[last].append(kv(body))
        elif body.startswith('player '):
            players[int(body.split()[1])] = kv(body)
    return things, planets, fleets, players, wps


def fields_near(things, owner, x, y, r=6):
    return [t for t in things if t['type'] == 'minefield' and int(t['owner']) == owner
            and abs(int(t['x']) - x) <= r and abs(int(t['y']) - y) <= r]


def techsum(p):
    return sum(int(p[f]) for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio'))


def evaluate(c, A, B):
    things, planets, fleets, players, wps = A
    k = c['check']
    kind = k[0]
    if kind in ('field', 'fieldat'):
        _, owner, x, y, want = k
        fs = fields_near(things, owner, x, y, 0 if kind == 'fieldat' else 6)
        got = [int(f['count']) for f in fs] or [0]
        if kind == 'fieldat' and not fs:
            got = ['none at (%d,%d); near: %s' % (x, y, [(f['x'], f['y'], f['count']) for f in fields_near(things, owner, x, y, 15)])]
        return got == [want], got
    if kind == 'fields':
        _, owner, x, y, want = k
        got = {f['kind']: int(f['count']) for f in fields_near(things, owner, x, y)}
        return got == want, got
    if kind == 'laytask':
        _, owner, x, y, want = k
        fs = fields_near(things, owner, x, y)
        tasks = [w['task'] for (o, i), ws in wps.items() for w in ws[:1]
                 if o == owner and int(fleets[(o, i)]['x']) == x and int(fleets[(o, i)]['y']) == y]
        got = ([int(f['count']) for f in fs], tasks)
        return got == ([want], ['0']), got
    if kind == 'surface':
        _, n, want = k
        before = tuple(int(v) for v in B[1][n].get('surface', '0/0/0').split('/'))
        after = tuple(int(v) for v in planets[n].get('surface', '0/0/0').split('/'))
        got = tuple(a - b for a, b in zip(after, before))
        return got == want, got
    if kind == 'planet':
        _, n, want = k
        p = planets[n]
        got = {}
        ok = True
        for key, w in want.items():
            if key == 'surface':
                before = tuple(int(v) for v in B[1][n].get('surface', '0/0/0').split('/'))
                after = tuple(int(v) for v in p.get('surface', '0/0/0').split('/'))
                g = tuple(a - b for a, b in zip(after, before))
            elif key == 'owner':
                g = int(p['owner'])
            else:
                g = int(p.get(key, -999))
            got[key] = g
            ok &= g == w
        return ok, got
    if kind == 'packetat':
        _, owner, x, y, want = k
        ps = [t for t in things if t['type'] == 'packet']
        got = [(t['x'], t['y'], t['cargo'], t['class'], t['moved']) for t in ps]
        if x is None:
            return None, got
        hit = [t for t in ps if abs(int(t['x']) - x) <= 1 and abs(int(t['y']) - y) <= 1]
        return bool(hit) and int(hit[0]['cargo'].split('/')[0]) == want, got
    if kind == 'fleet':
        _, owner, fid, want = k
        got = 'kept' if (owner, fid) in fleets else 'gone'
        return got == want, got
    if kind == 'mtgift':
        _, owner, fid, levels = k
        gone = (owner, fid) not in fleets
        d = techsum(players[owner]) - techsum(B[3][owner])
        return gone and d == levels, dict(fleet='gone' if gone else 'kept', tech_levels_gained=d)
    if kind == 'fleetat':
        _, owner, fid, x, y = k
        f = fleets.get((owner, fid))
        got = (int(f['x']), int(f['y'])) if f else None
        return got == (x, y), got
    if kind == 'worm':
        _, num, x, y = k
        w = [t for t in things if t['type'] == 'wormhole' and int(t['num']) in (num, num + 1)]
        bw = {int(t['num']): t for t in B[0] if t['type'] == 'wormhole'}
        got = [(t['num'], int(t['x']) - int(bw[int(t['num'])]['x']), int(t['y']) - int(bw[int(t['num'])]['y']),
                t['years']) for t in w]
        ok = all(abs(dx) <= 12 and abs(dy) <= 12 and (dx, dy) != (0, 0) for _, dx, dy, _ in got)
        return (ok if num == 0 else None), got
    if kind == 'detonate':
        _, x, y = k
        f = fields_near(things, 0, x, y)
        got = dict(field=[int(t['count']) for t in f])
        for key, d in fleets.items():
            if abs(int(d['x']) - x) <= 20 and abs(int(d['y']) - y) <= 20:
                got['fleet%d/%d' % key] = (d['ships'], ' '.join(v for kk, v in d.items() if kk.startswith('dmg')))
        return None, got
    raise SystemExit('unknown check ' + kind)


def main():
    rid, after = sys.argv[1], sys.argv[2]
    before = sys.argv[3] if len(sys.argv) > 3 else after.replace('after.dump', 'before.dump')
    run = [r for r in gen.RUNS if r.rid == rid][0]
    A, B = load(after), load(before, 'before')
    for c in run.cases:
        ok, got = evaluate(c, A, B)
        print('%-9s %-12s %-12s %s' % (c['id'], c['pred'], {True: 'HELD', False: 'CONTRADICTED', None: 'OBSERVED'}[ok], got))


if __name__ == '__main__':
    main()
