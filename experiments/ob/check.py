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


def load(path, which='after', fname='CB.HST'):
    """Objects of one file in a dump; for .M files only the last year's section."""
    things, planets, fleets, players, wps = [], {}, {}, {}, {}
    seen = {}
    last = None
    lines = [l for l in open(path) if '/raw/%s/%s ' % (which, fname) in l]
    turns = [int(re.search(r'file turn=(\d+)', l).group(1)) for l in lines if ' file turn=' in l]
    cur = None
    for line in lines:
        body = line.split(fname + ' ', 1)[1]
        m = re.match(r'file turn=(\d+)', body)
        if m:
            cur = int(m.group(1))
            continue
        if turns and cur != max(turns):
            continue
        if body.startswith('seen planet'):
            d = kv(body)
            seen[int(body.split()[2])] = int(d['level'])
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
    if fname != 'CB.HST':
        return things, planets, fleets, players, wps, seen
    return things, planets, fleets, players, wps


def fields_near(things, owner, x, y, r=6):
    return [t for t in things if t['type'] == 'minefield' and int(t['owner']) == owner
            and abs(int(t['x']) - x) <= r and abs(int(t['y']) - y) <= r]


def techsum(p):
    return sum(int(p[f]) for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio'))


def scan_expect(run, A, B):
    """S-17..S-19 rules: the viewer's expected set of other players' object ids."""
    v = run.scan['viewer']
    bit = 1 << v
    things, planets, fleets = A[0], A[1], A[2]
    before = {int(t['id']): t for t in B[0]}
    scanners = []          # (x, y, R, P, is_fleet)
    for (o, i), f in fleets.items():
        if o == v and 'ppacket' not in run.scan:
            scanners.append((int(f['x']), int(f['y']), 50, 0, True))
    if run.scan.get('ppacket'):
        for t in things:
            if t['type'] == 'packet' and int(t['owner']) == v:
                w = int(t['warp'])
                scanners.append((int(t['x']), int(t['y']), 0, w * w, False))
    exp = set()
    for t in things:
        tid, owner, kind = int(t['id']), int(t['owner']), t['type']
        if kind in ('minefield', 'packet') and owner == v:
            continue
        x, y = int(t['x']), int(t['y'])
        b = before.get(tid, {})
        ok = False
        for sx, sy, R, P, isf in scanners:
            d2 = (sx - x) ** 2 + (sy - y) ** 2
            if kind == 'trader':
                ok = True
            elif kind == 'packet':
                ok |= d2 <= R * R or bool(run.scan.get('ppacket'))
            elif kind == 'wormhole':
                ok |= bool(int(b.get('seen', '0'), 16) & bit) or d2 <= R * R // 16 or d2 <= P * P
            else:
                known = bool(int(b.get('known', '0'), 16) & bit)
                ok |= (known and d2 <= R * R) or d2 <= P * P or d2 <= R * R // 16 or \
                    (isf and d2 <= int(t['count']))
        if kind == 'trader' or (kind == 'packet' and run.scan.get('ppacket')):
            ok = True
        if ok:
            exp.add(tid)
    return exp


def evaluate(c, A, B, run=None, M=None):
    things, planets, fleets, players, wps = A
    k = c['check']
    kind = k[0]
    if kind == 'scan':
        exp = scan_expect(run, A, B)
        v = run.scan['viewer']
        got = {int(t['id']) for t in M[0] if not (t['type'] in ('minefield', 'packet') and int(t['owner']) == v)}
        diff = dict(missing=sorted(exp - got), extra=sorted(got - exp))
        return exp == got, dict(seen=sorted(got), **diff)
    if kind == 'scanfleets':
        got = [(o, i, (o, i) in M[2]) for o, i, _ in k[1]]
        return got == [tuple(e) for e in k[1]], got
    if kind == 'planetlevel':
        _, viewer, n, lv = k
        g = M[5].get(n, 0)
        return (g >= lv) if lv >= 0 else (g < -lv), dict(level=g)
    if kind == 'fieldobs':
        _, owner, x, y = k
        return None, [int(f['count']) for f in fields_near(things, owner, x, y)]
    if kind == 'nofield':
        _, owner, x0, y0, x1, y1 = k
        fs = fields_near(things, owner, x0, y0, 30) + fields_near(things, owner, x1, y1, 30)
        return not fs, [(f['x'], f['y'], f['count']) for f in fs]
    if kind == 'minehit':
        _, owner, fid, x, y = k
        f = fleets.get((owner, fid))
        cnt = [int(t['count']) for t in fields_near(things, 1, x, y)]
        got = dict(fleet=(f['x'], f['y'], f['ships'], ' '.join(v for kk, v in f.items() if kk.startswith('dmg'))) if f else None,
                   field=cnt)
        if f and (int(f['x']), int(f['y'])) == (1241, 1230):
            return cnt == [2940] and not any(kk.startswith('dmg') for kk in f), got
        return bool(f) and cnt == [2891] and f.get('dmg1') == '250/100%', got
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
    M = load(after, 'after', 'CB.M%d' % (run.scan['viewer'] + 1)) if run.scan else load(after, 'after', 'CB.M2')
    for c in run.cases:
        ok, got = evaluate(c, A, B, run, M)
        print('%-9s %-12s %-12s %s' % (c['id'], c['pred'], {True: 'HELD', False: 'CONTRADICTED', None: 'OBSERVED'}[ok], got))


if __name__ == '__main__':
    main()
