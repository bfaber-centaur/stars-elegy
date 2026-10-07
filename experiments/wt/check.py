#!/usr/bin/env python3
"""Check a WT run against the gen.py predictions.

  python3 experiments/wt/check.py WT-001 RUNDIR        # RUNDIR from pinned-turn
  python3 experiments/wt/check.py WT-004 RUNDIR...     # one RUNDIR per stream; tallied

Reads RUNDIR/before.dump and RUNDIR/after.dump (host file, plus the player
files for messages). Message checks look for the 2-byte message id in the
player file's event block for the new year. The record layout is not
decoded (ORACLE.md), so a hit is a byte match, and the raw block is printed
with every result.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen
from trace import parse, KV

GIFT_HULLS = {'Nubian': 'M.T. Lifeboat', 'Mini Morph': None}


def host_extra(path):
    """Packets and designs from the host lines of a dump, which trace.parse skips."""
    packets, designs = {}, {}
    for line in open(path):
        head, _, rest = line.partition(' ')
        if not head.endswith('.HST'):
            continue
        kv = dict(KV.findall(rest))
        if rest.startswith('thing ') and kv.get('type') == 'packet':
            packets[(int(kv['owner']), int(kv['num']))] = (int(kv['x']), int(kv['y']))
        elif rest.startswith('design '):
            designs[(kv['owner'], int(kv['n']))] = rest.split(':: ', 1)[1].strip()
    return packets, designs


def events(path, player, turn):
    """Hex of player's event blocks in its .M file for `turn`."""
    out, cur = [], None
    for line in open(path):
        head, _, rest = line.partition(' ')
        if not head.endswith('.M%d' % (player + 1)):
            continue
        if rest.startswith('file '):
            cur = int(dict(KV.findall(rest))['turn'])
        elif rest.startswith('events raw=') and cur == turn:
            out.append(rest.split('=', 1)[1].strip())
    return ''.join(out)


def has_msg(hexs, mid):
    pat = '%02x%02x' % (mid & 0xff, mid >> 8)
    return any(hexs.startswith(pat, i) for i in range(0, len(hexs) - 3, 2))


def gift_kind(desc):
    if desc.startswith('Nubian'):
        return 'M.T. Lifeboat'
    if desc.startswith('Mini Morph'):
        return 'M.T. Probe' if 'Mega Poly Shell' in desc else 'M.T. Scout'
    return 'other: ' + desc


def check_run(rid, d, quiet=False):
    r = [x for x in gen.RUNS if x.rid == rid][0]
    b, a = parse(os.path.join(d, 'before.dump')), parse(os.path.join(d, 'after.dump'))
    pk, des = host_extra(os.path.join(d, 'after.dump'))
    _, des0 = host_extra(os.path.join(d, 'before.dump'))
    turn = a['year'] - 2400
    ev = {p: events(os.path.join(d, 'after.dump'), p, turn) for p in (0, 1)}
    results = []

    def one(c):
        k = c[0]
        if k == 'fleetat':
            f = a['fleets'].get((c[1], c[2]))
            got = f and (f['x'], f['y'])
            return got == (c[3], c[4]), 'at %s' % (got,)
        if k == 'cargo':
            f = a['fleets'].get((c[1], c[2]))
            got = f and int(f['cargo'].split('/')[0])
            return got == c[3], 'ironium %s' % got
        if k == 'gone':
            return (c[1], c[2]) not in a['fleets'], 'present' if (c[1], c[2]) in a['fleets'] else 'gone'
        if k == 'worm':
            w = a['worms'].get(c[1])
            got = w and int(w[c[2]], 16)
            return got == c[3], '%s=%s' % (c[2], w and w[c[2]])
        if k == 'wormbit':
            w = a['worms'].get(c[1])
            got = w and int(w[c[2]], 16)
            return bool(got is not None and got & c[3]), '%s=%s' % (c[2], w and w[c[2]])
        if k == 'packetat':
            got = pk.get((c[1], c[2]))
            ok = got is not None and abs(got[0] - c[3]) <= 1 and abs(got[1] - c[4]) <= 1
            return ok, 'at %s' % (got,)
        if k == 'trader':
            t = a['traders'].get(c[1])
            got = t and (t['x'], t['y'])
            ok = got == (c[2], c[3]) and (c[4] is None or int(t['met'], 16) == c[4])
            return ok, 'at %s met=%s dest=%s' % (got, t and t['met'], t and (t['dest'],))
        if k == 'tech':
            got = a['players'][c[1]]['tech']
            return got == c[2], 'tech %s' % got
        if k == 'techgain':
            g = sum(a['players'][c[1]]['tech']) - sum(b['players'][c[1]]['tech'])
            per = [x - y for x, y in zip(a['players'][c[1]]['tech'], b['players'][c[1]]['tech'])]
            return g == c[2], '+%d %s' % (g, per)
        if k == 'accum':
            got = a['players'][c[1]]['accum'][c[2]]
            return got == c[3], 'accum %s' % a['players'][c[1]]['accum']
        if k == 'mt':
            got = int(a['players'][c[1]]['mt'], 16)
            return got == c[2], 'mt %04x' % got
        if k == 'msg':
            return has_msg(ev[c[1]], c[2]), 'events %s' % ev[c[1]]
        if k == 'designs':
            n = sum(1 for (o, _) in des if o == str(c[1]))
            return n == c[2], '%d designs' % n
        if k == 'nonew':
            new = [f for f in a['fleets'] if f[0] == c[1] and f not in b['fleets']]
            return not new, 'new fleets %s' % new
        raise ValueError(k)

    for case in r.cases:
        chk = case['check']
        if chk is None:
            continue
        if chk[0] in ('jumps', 'gift'):
            continue
        chks = chk if isinstance(chk, list) else [chk]
        outs = [one(c) for c in chks]
        ok = all(o for o, _ in outs)
        results.append((case['id'], ok, '; '.join(s for _, s in outs)))
    return results, (b, a, des, des0, ev)


def jumps(b, a, n):
    """O-44: classify every wormhole end."""
    rows = []
    for k in range(n):
        o, w = b['worms'][k], a['worms'].get(k)
        if w is None:
            rows.append((k, 'gone', False))
            continue
        dx, dy = w['x'] - o['x'], w['y'] - o['y']
        s8, sA = int(w['seen'], 16), int(w['seen2'], 16)
        if w['years'] == 0:
            ok = not (s8 & 1) and bool(sA & 1)
            rows.append((k, 'JUMP d=(%+d,%+d) seen=%s seen2=%s' % (dx, dy, w['seen'], w['seen2']), ok))
        else:
            ok = abs(dx) <= 12 and abs(dy) <= 12 and w['years'] == o['years'] + 1 and bool(s8 & 1) and bool(sA & 1)
            rows.append((k, 'jiggle d=(%+d,%+d) years=%d seen=%s seen2=%s' % (dx, dy, w['years'], w['seen'],
                                                                             w['seen2']), ok))
    return rows


def gift(b, a, des, des0, ev, owner, fid, slot, mt):
    """O-49 / O-51: what one meeting gave."""
    if (owner, fid) in a['fleets']:
        return 'fleet kept', False
    new = [k for k in a['fleets'] if k[0] == owner and k not in b['fleets']]
    mt_ok = int(a['players'][owner]['mt'], 16) == mt
    tech_ok = a['players'][owner]['tech'] == b['players'][owner]['tech']
    if not new:
        ok = has_msg(ev[owner], 0x10e) and mt_ok and tech_ok and owner == 0
        return 'nothing (0x10e %s)' % has_msg(ev[owner], 0x10e), ok
    f = a['fleets'][new[0]]
    d, n = map(int, f['ships'].split(':'))
    desc = des.get((str(owner), d), '?')
    kind = gift_kind(desc)
    full = des0.get((str(owner), d)) is None
    ok = (len(new) == 1 and d == slot and full and mt_ok and tech_ok and not kind.startswith('other')
          and 1 <= n <= (2 if kind == 'M.T. Lifeboat' else 4))
    return '%s x%d in slot %d at (%d,%d) fuel %d' % (kind, n, d, f['x'], f['y'], f['fuel']), ok


def main(argv):
    rid, dirs = argv[0], argv[1:]
    if rid != 'WT-004':
        for d in dirs:
            res, _ = check_run(rid, d)
            print('== %s %s' % (rid, d))
            for cid, ok, s in res:
                print('%-8s %s  %s' % (cid, 'OK  ' if ok else 'MISS', s))
            print('%d/%d OK' % (sum(ok for _, ok, _ in res), len(res)))
        return
    r = [x for x in gen.RUNS if x.rid == rid][0]
    njump, nbad, tally = 0, 0, {}
    for d in dirs:
        _, (b, a, des, des0, ev) = check_run(rid, d)
        print('== %s %s' % (rid, d))
        for k, s, ok in jumps(b, a, r.cases[0]['check'][1]):
            if s.startswith('JUMP') or not ok:
                print('   end %2d %s %s' % (k, s, 'OK' if ok else 'MISS'))
            njump += s.startswith('JUMP')
            nbad += not ok
        for case in r.cases[1:]:
            _, owner, fid, slot, mt = case['check']
            s, ok = gift(b, a, des, des0, ev, owner, fid, slot, mt)
            print('   %s %s %s' % (case['id'], s, 'OK' if ok else 'MISS'))
            nbad += not ok
            key = (case['id'], re.sub(r' in slot.*| \(0x10e.*', '', s))
            tally[key] = tally.get(key, 0) + 1
    print('== tally over %d streams: %d jumps, %d misses' % (len(dirs), njump, nbad))
    for (cid, s), c in sorted(tally.items()):
        print('   %s %-30s %d' % (cid, s, c))


if __name__ == '__main__':
    main(sys.argv[1:])
