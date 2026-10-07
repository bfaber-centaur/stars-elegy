#!/usr/bin/env python3
"""Compare a GT run with the gen.py predictions.

  python3 experiments/gt/check.py CASES.json RUNDIR

RUNDIR is a pinned-turn output (before.dump, after.dump). Prints one line
per case: HELD, MISSED or OBSERVED, with what was seen.
"""
import json, re, sys


def kv(s):
    return dict(re.findall(r'(\w+)=(\S+)', s))


def load(path, fname):
    fleets, wps, planets, msgs, last = {}, {}, {}, [], None
    for line in open(path):
        if '/%s ' % fname not in line:
            continue
        body = line.split(fname + ' ', 1)[1]
        if body.startswith('fleet owner='):
            d = kv(body)
            last = (int(d['owner']), int(d['id']))
            fleets[last] = d
            wps[last] = []
        elif body.startswith('  wp '):
            wps[last].append(kv(body))
        elif body.startswith('planet '):
            planets[int(body.split()[1])] = kv(body)
        elif body.startswith('msg id='):
            d = kv(body)
            p = [int(v) for v in d.get('p', '').split(',') if v]
            msgs.append((int(d['id'], 16), int(d['obj'], 16), p))
    return fleets, wps, planets, msgs


def main():
    cases = json.load(open(sys.argv[1]))
    run = sys.argv[2]
    bh = load(run + '/before.dump', 'GT.HST')
    ah = load(run + '/after.dump', 'GT.HST')
    m1 = load(run + '/after.dump', 'GT.M1')
    m2 = load(run + '/after.dump', 'GT.M2')
    msgs = {0: m1[3], 1: m2[3]}

    def fmsg(owner, fid):
        return sorted({hex(i) for i, o, p in msgs[owner] if o == (0x8000 | owner << 9 | fid)})

    def surface(n):
        a = [int(v) for v in ah[2][n]['minerals'].split('/')]
        b = [int(v) for v in bh[2][n]['minerals'].split('/')]
        return a[0] - b[0]

    def ships(f):
        return sum(int(x.split(':')[1]) for x in f['ships'].split(',') if x)

    def dmg(f):
        v = [x for k, x in f.items() if k.startswith('dmg')]
        return v[0] if v else None

    out = []
    for c in cases:
        k, ok, seen = c['check'], True, []
        kind = k['kind']
        if kind in ('fleet', 'gone'):
            f = ah[0].get((k['owner'], k['id']))
            ms = fmsg(k['owner'], k['id'])
            seen.append('msgs %s' % (','.join(ms) or '-'))
            if kind == 'gone':
                ok &= f is None
                seen.append('fleet gone' if f is None else 'fleet at %s,%s ships %s' % (f['x'], f['y'], f['ships']))
            elif f is None:
                ok = False
                seen.append('fleet gone')
            else:
                at = (int(f['x']), int(f['y']))
                seen.append('at %d,%d ships %s cargo %s fuel %s dmg %s b5 %s' % (at + (f['ships'], f['cargo'], f['fuel'], dmg(f), f['b5'])))
                ok &= at == tuple(k['at'])
                if 'ships' in k:
                    s = k['ships']
                    ok &= (s[0] <= ships(f) <= s[1]) if isinstance(s, list) else ships(f) == s
                if 'cargo' in k:
                    ok &= f['cargo'] == '/'.join(map(str, k['cargo']))
                if 'fuel' in k:
                    ok &= int(f['fuel']) == k['fuel']
                if 'dmg' in k and k['dmg'] != 'any':
                    ok &= dmg(f) == k['dmg']
                if k.get('repaired'):
                    b = bh[0][(k['owner'], k['id'])]
                    ok &= dmg(f) is None or int(dmg(f).split('/')[0]) < int(dmg(b).split('/')[0])
                if 'same_dmg_as' in k:
                    o = ah[0][(k['owner'], k['same_dmg_as'])]
                    ok &= dmg(f) == dmg(o)
                if 'designs' in k:
                    ok &= sorted(f['ships'].split(',')) == sorted('%s:%d' % (d, n) for d, n in k['designs'].items())
            if 'msg' in k:
                ok &= hex(k['msg']) in ms
            if 'msg1' in k:
                m = sorted({hex(i) for i, o, p in msgs[1] if p and p[0] == k['id'] and o < 0x8000})
                seen.append('player 1 msgs %s' % (','.join(m) or '-'))
                ok &= hex(k['msg1']) in m
            if 'surface' in k:
                n, want = k['surface']
                seen.append('planet %d ironium %+d' % (n, surface(n)))
                ok &= surface(n) == want
        elif kind == 'seen':
            f = m2[0].get((k['owner'], k['id']))
            if f is None:
                ok = False
                seen.append('not in player 1 file')
            else:
                seen.append('player 1 sees it at %s,%s warp %s dx %s dy %s' % (f['x'], f['y'], f['warp'], f['dx'], f['dy']))
                ok &= int(f['warp']) == k['warp']
                if 'at' in k:
                    ok &= (int(f['x']), int(f['y'])) == tuple(k['at'])
        elif kind == 'wp':
            w = ah[1][(k['owner'], k['id'])]
            w1 = (int(w[1]['x']), int(w[1]['y'])) if len(w) > 1 else None
            seen.append('waypoint 1 at %s' % (w1,))
            if 'follow' in k:
                t = ah[0][tuple(k['follow'])]
                ok &= w1 == (int(t['x']), int(t['y']))
            else:
                ok &= w1 == tuple(k['at'])
        elif kind == 'many':
            fs = [ah[0].get((0, i)) for i in k['ids']]
            arrived = sum(1 for f in fs if f and (int(f['x']), int(f['y'])) == tuple(k['at']))
            ce = sum(1 for i in k['ids'] if '0xf2' in fmsg(0, i))
            seen.append('%d of %d arrived; %d with message 0xf2' % (arrived, len(fs), ce))
            ok &= arrived == len(fs) and ce == 0
        elif kind == 'ce':
            ce = [i for i in k['ids'] if '0xf2' in fmsg(0, i)]
            seen.append('%d of %d with message 0xf2 (fleets %s)' % (len(ce), len(k['ids']), ce))
            ok = None
        verdict = 'OBSERVED' if ok is None else ('HELD' if ok else 'MISSED')
        out.append('%s %s %s: %s' % (c['id'], c['pred'], verdict, '; '.join(seen)))
    print('\n'.join(out))
    print('player 1 messages naming a player 0 fleet: %s' % (
        [(hex(i), hex(o), p) for i, o, p in msgs[1] if 0x8000 <= o < 0x8200] or 'none'))
    print('player 1 messages: %s' % sorted({hex(i) for i, o, p in msgs[1]}))


if __name__ == '__main__':
    main()
