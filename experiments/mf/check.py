#!/usr/bin/env python3
"""Compare one MF- run with the gen.py predictions.

  python3 experiments/mf/check.py MF-01 RUNDIR

Reads RUNDIR/after.dump (combatlab dump of raw/after/*), prints one line
per case: HELD, CONTRADICTED or OBSERVED, followed by the observations.
"""
import math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen  # noqa: E402


def kv(line):
    return dict(re.findall(r'(\w+)=(\S+)', line))


def load(path, fname):
    things, fleets, msgs, designs = [], {}, [], []
    for line in open(path):
        if '/raw/after/%s ' % fname not in line:
            continue
        body = line.split(fname + ' ', 1)[1].rstrip('\n')
        if body.startswith('thing id='):
            things.append(kv(body))
        elif body.startswith('fleet owner='):
            d = kv(body)
            d['dmg'] = dict((int(k[3:]), v) for k, v in d.items() if k.startswith('dmg'))
            fleets[(int(d['owner']), int(d['id']))] = d
        elif body.startswith('msg id='):
            msgs.append(kv(body))
        elif body.startswith('design owner='):
            designs.append(body)
    return things, fleets, msgs, designs


def minerate(obs):
    """obs: [(draws, stopped)] -> (per mille MLE, (lo, hi) 95% profile interval, k, n)."""
    n = sum(d for d, h in obs)
    k = sum(1 for d, h in obs if h)
    if n == 0:
        return None

    def ll(p):
        return k * math.log(p) + (n - k) * math.log(1 - p)
    mle = k / n
    top = ll(mle) if 0 < mle < 1 else 0.0
    ok = [p / 100000 for p in range(1, 100000) if top - ll(p / 100000) <= 1.92]
    return 1000 * mle, (1000 * min(ok), 1000 * max(ok)), k, n


def legs(run, fleets, sel):
    """[(fleet spec, stopped, offset)] for the moving fleets matching sel."""
    out = []
    for f in run.fleets:
        if not sel(f) or (f['to'] is None and f['follow'] is None):
            continue
        a = fleets.get((f['owner'], f['id']))
        if a is None:
            out.append((f, 'gone', None))
            continue
        x = int(a['x'])
        end = f['to'][0] if f['to'] else None
        stopped = bool(a['dmg']) and not f['prior']
        out.append((f, stopped, x - f['x']))
    return out


def rate_line(rows, leg):
    obs = [((off + 1) if st else leg, st) for f, st, off in rows]
    r = minerate(obs)
    if r is None:
        return 'no draws', None
    return 'rate %.1f per mille, 95%% interval %.1f-%.1f (%d stops in %d draws)' % (r[0], r[1][0], r[1][1],
                                                                                   r[2], r[3]), r


def fields(things, owner=None):
    return [t for t in things if t['type'] == 'minefield' and (owner is None or int(t['owner']) == owner)]


def main():
    rid, rdir = sys.argv[1], sys.argv[2]
    run = next(r for r in gen.RUNS if r.rid == rid)
    dump = os.path.join(rdir, 'after.dump')
    things, fleets, _, _ = load(dump, 'CB.HST')
    m = {p: load(dump, 'CB.M%d' % (p + 1)) for p in (0, 1)}
    for c in run.cases:
        chk = c['check']
        verdict, notes = 'OBSERVED', []
        kind = chk[0]
        if kind in ('rate', 'nohits'):
            rows = legs(run, fleets, lambda f: f['tag'] == 'p1')
            line, r = rate_line(rows, 81)
            notes.append(line)
            for name, d in (('uncloaked', gen.TANK), ('cloaked', gen.CLOAK)):
                sub = [x for x in rows if x[0]['stacks'][0][0] == d]
                notes.append('%s: %s; offsets %s' % (name, rate_line(sub, 81)[0],
                                                     sorted(o for f, st, o in sub if st)))
            if kind == 'rate':
                verdict = 'HELD' if r and r[1][0] <= 30 <= r[1][1] else 'CONTRADICTED'
            else:
                verdict = 'HELD' if not any(st for _, st, _ in rows) else 'CONTRADICTED'
        elif kind == 'dmg':
            rows = legs(run, fleets, lambda f: f['tag'] == 'p1')
            ws = set()
            for f, st, off in rows:
                if st:
                    ws |= set(fleets[(1, f['id'])]['dmg'].values())
            want = '%d/100%%' % gen.word(2000, 3200)
            notes.append('damage words of stopped fleets: %s' % sorted(ws))
            hm = [x for x in m[1][2] if x['id'] in ('0xc6', '0xc7', '0xc8')]
            notes.append('%d hit messages to player 1' % len(hm))
            verdict = 'HELD' if ws == {want} else 'CONTRADICTED'
        elif kind == 'own':
            rows = legs(run, fleets, lambda f: f['tag'] == 'own')
            bad = [(f['id'], o, fleets[(0, f['id'])]['dmg']) for f, st, o in rows if o != 81 or st]
            notes.append('own fleets not at their waypoint or damaged: %s' % bad)
            verdict = 'HELD' if not bad else 'CONTRADICTED'
        elif kind == 'chain':
            ok = True
            for role in 'ABC':
                for order in ('ABC', 'CBA'):
                    rows = legs(run, fleets, lambda f: f['tag'] == 'chain-%s-%s' % (role, order))
                    stops = [o for f, st, o in rows if st]
                    notes.append('%s (numbered %s): %d/6 stopped, offsets %s; end offsets %s' % (
                        role, order, len(stops), stops, [o for f, st, o in rows]))
                    if role == 'A' and stops:
                        ok = False
            verdict = 'HELD' if ok else 'CONTRADICTED'
        elif kind == 'pairs':
            rows = legs(run, fleets, lambda f: f['tag'].startswith('pair-'))
            stops = [(f['tag'], o) for f, st, o in rows if st]
            notes.append('%d/%d stopped %s; end offsets W %s, E %s' % (
                len(stops), len(rows), stops, [o for f, st, o in rows if f['tag'] == 'pair-W'],
                [o for f, st, o in rows if f['tag'] == 'pair-E']))
            verdict = 'HELD' if not stops else 'CONTRADICTED'
        elif kind == 'legs':
            leg, pm = chk[1], chk[2]
            rows = legs(run, fleets, lambda f: f['tag'] == 'leg%d' % leg)
            line, r = rate_line(rows, leg)
            notes.append(line + '; offsets %s' % sorted(o for f, st, o in rows if st))
            if pm == 0:
                verdict = 'HELD' if not any(st for _, st, _ in rows) else 'CONTRADICTED'
            elif leg in (81, 50):
                verdict = 'HELD' if r and r[1][0] <= pm <= r[1][1] else 'CONTRADICTED'
        elif kind == 'payer':
            rows = legs(run, fleets, lambda f: f['tag'] == 'mf4')
            stops = [(f['x'] + o, f['y']) for f, st, o in rows if st]
            notes.append('stops at %s' % stops)
            for t in fields(things, 0):
                notes.append('field %s at %s,%s count %s' % (t['num'], t['x'], t['y'], t['count']))
            inside2 = [s for s in stops if (s[0] - 1210) ** 2 + (s[1] - 1200) ** 2 <= 400]
            notes.append('%d stops inside F2' % len(inside2))
            f2 = [t for t in fields(things, 0) if t['num'] == '1']
            verdict = 'HELD' if f2 and int(f2[0]['count']) == 390 else 'CONTRADICTED'
        elif kind == 'alone':
            rows = legs(run, fleets, lambda f: f['tag'] == 'mf4')
            n = sum(1 for _, st, _ in rows if st)
            cnt = chk[2]
            for _ in range(n):
                cnt -= gen.shrink(cnt)
            fd = run.fields[0]
            # planets are counted with the count after this year's stops
            want = gen.decay(cnt, len(gen.planets_in(fd['x'], fd['y'], cnt))) - (1280 if fd['planets'] else 0)
            t = fields(things, 0)
            got = int(t[0]['count']) if t else 0
            notes.append('%d stops %s; field %d, predicted %d' % (
                n, [(f['x'] + o, f['y']) for f, st, o in rows if st], got, want))
            verdict = 'HELD' if got == want else 'CONTRADICTED'
        elif kind == 'det':
            tag = chk[1]
            for f in run.fleets:
                if f['tag'].startswith(tag + '-'):
                    a = fleets.get((f['owner'], f['id']))
                    notes.append('%s: %s' % (f['tag'], 'gone' if a is None else
                                              'at %s,%s ships %s dmg %s' % (a['x'], a['y'], a['ships'], a['dmg'])))
            fd = next(fd for fd in run.fields if fd['tag'] == tag)
            t = [t for t in fields(things, 0) if int(t['num']) == fd['num']]
            notes.append('field %s' % (t[0]['count'] if t else 'gone'))
        elif kind == 'fieldat':
            _, o, x, y, n = chk
            near = [t for t in fields(things, o) if abs(int(t['x']) - x) <= 12 and abs(int(t['y']) - y) <= 12]
            notes.append('fields near: %s' % ['(%s,%s) %s' % (t['x'], t['y'], t['count']) for t in near])
            verdict = 'HELD' if any(int(t['x']) == x and int(t['y']) == y and int(t['count']) == n
                                    for t in near) and len(near) == 1 else 'CONTRADICTED'
        elif kind == 'mix':
            for i in range(5):
                rows = legs(run, fleets, lambda f: f['tag'] == 'mix%d' % i)
                ws = [fleets[(1, f['id'])]['dmg'] for f, st, o in rows if st]
                notes.append('mix%d %s: %d/%d stopped, dmg %s' % (i, '+'.join('%d:%d' % s for s in rows[0][0]['stacks']),
                                                                 len(ws), len(rows), ws))
        elif kind in ('newfield', 'nonewfield'):
            x, y = chk[2], chk[3]
            near = [t for t in fields(things, 0) if (int(t['x']) - x) ** 2 + (int(t['y']) - y) ** 2 <= 100]
            allf = fields(things, 0)
            notes.append('player-0 fields: %s' % ['(%s,%s) %s' % (t['x'], t['y'], t['count']) for t in allf])
            if kind == 'newfield':
                verdict = 'HELD' if any(int(t['count']) == chk[4] for t in near) else 'CONTRADICTED'
            else:
                verdict = 'HELD' if not near else 'CONTRADICTED'
        elif kind == 'limit':
            near = [t for t in fields(things, 0) if (int(t['x']) - 1100) ** 2 + (int(t['y']) - 1300) ** 2 <= 100]
            notes.append('fields at the open layer: %s; player-0 fields %d' % (
                ['(%s,%s) %s num %s' % (t['x'], t['y'], t['count'], t['num']) for t in near], len(fields(things, 0))))
            lm = [x for x in m[0][2] if x['id'] in ('0x17e', '0xc3', '0xc4')]
            notes.append('laying messages: %s' % ['%s %s' % (x['name'], x['p']) for x in lm])
            verdict = 'HELD' if (not near) == chk[1] else 'CONTRADICTED'
        elif kind == 'merge_tiny':
            big = [t for t in fields(things, 0) if int(t['count']) > 100]
            notes.append('tiny fields above 100: %s' % ['(%s,%s) %s num %s' % (t['x'], t['y'], t['count'], t['num'])
                                                       for t in big])
            verdict = 'HELD' if any(int(t['count']) == 250 for t in big) else 'CONTRADICTED'
        print('%s %s (%s): %s' % (c['id'], verdict, c['pred'], c['expect']))
        for n in notes:
            print('    ' + n)
    print('fields after: %s' % ['%s/%s (%s,%s) %s %s' % (t['owner'], t['num'], t['x'], t['y'], t['count'],
                                                       ['std', 'heavy', 'bump'][int(t['kind'])])
                                for t in fields(things)][:12])
    for p in (0, 1):
        mm = [x for x in m[p][2] if x['name'] != '-']
        print('player %d mine messages: %d (%s)' % (p, len(mm), ', '.join(sorted(set(x['name'] for x in mm)))))


if __name__ == '__main__':
    main()
