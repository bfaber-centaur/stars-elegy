#!/usr/bin/env python3
"""Check CS-003 runs against predictions.tsv.

  python3 experiments/cs003/check.py RUNDIR_W RUNDIR_S RUNDIR_B RUNDIR_C RUNDIR_C2 [designer.tsv]

Each RUNDIR is a pinned-turn output directory (after.dump from
`tools/fleetlab/combatlab dump`). designer.tsv holds the designer readouts
of CS-003-D (design, mass, moves, cloak, jam, scanner), typed from the
screenshots. Prints one line per case and a summary.

Torpedo cases replay each hit record on the target stack with the
COMBAT.md "Damage" rule (no shields): a torpedo or missile hit puts
hits·D/2 into armor twice (integer halves), D the per-torpedo damage
being tested. A record that no hit count up to the salvo size reproduces
rules that D out.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def parse(dump):
    st = dict(fleets={}, things=[], planets={}, battles=[])
    cur = None
    for line in open(dump, encoding='latin-1'):
        if '/after/' not in line:
            continue
        path, _, rest = line.partition('/after/')
        fn, _, body = rest.partition(' ')
        if fn == 'CB.HST':
            if body.startswith('fleet '):
                kv = dict(re.findall(r'(\w+)=(\S+)', body))
                ships = sum(int(s.split(':')[1]) for s in kv['ships'].split(','))
                st['fleets'][(int(kv['owner']), int(kv['id']))] = dict(kv, nships=ships)
            elif body.startswith('thing ') and 'type=minefield' in body:
                st['things'].append({k: int(v) if v.lstrip('-').isdigit() else v
                                     for k, v in re.findall(r'(\w+)=(\S+)', body)})
            elif body.startswith('pdetail '):
                n = int(body.split()[1])
                st['planets'][n] = dict(re.findall(r'(\w+)=(\S+)', body))
        elif fn == 'CB.M1':
            m = re.match(r'battle turn=1 .* x=(\d+) y=(\d+)', body)
            if m:
                cur = dict(x=int(m.group(1)), y=int(m.group(2)), toks=[], hits=[])
                st['battles'].append(cur)
                continue
            if cur is None:
                continue
            m = re.match(r'\s+tok (\d+) .*owner=(\d+) .*ships=(\d+)', body)
            if m:
                cur['toks'].append(dict(owner=int(m.group(2)), ships=int(m.group(3))))
                continue
            m = re.match(r'\s+hit tok=(\d+) flags=(\w+) kills=(\d+) shielddmg=(\d+) dmg=(\d+)/(\d+)%', body)
            if m:
                cur['hits'].append(dict(tok=int(m.group(1)), flags=int(m.group(2), 16), kills=int(m.group(3)),
                                        units=int(m.group(5)), pct=int(m.group(6))))
            elif not body.startswith((' ', 'battlehex')):
                cur = None
    return st


def damage(state, dp, killmax):
    """COMBAT.md "Damage" steps 3-6 for an unshielded ship stack."""
    ships, units, pct, armor = state['ships'], state['units'], state['pct'], state['armor']
    damaged = max(1, ships * pct // 100) if units else 0
    per = max(1, units * armor // 500) if units else 0
    surv, km = ships, killmax
    while damaged and armor - per <= dp and km:
        dp -= armor - per; damaged -= 1; surv -= 1; km -= 1
    while surv and armor <= dp and km:
        dp -= armor; surv -= 1; km -= 1
    if km == 0:
        dp = 0
    if dp and surv:
        dp = (dp + damaged * per + surv - 1) // surv if damaged else dp // surv
        dp = max(1, dp)
        units, pct = max(1, -(-dp * 500 // armor)), 100
    elif damaged:
        pct = -(-damaged * 100 // surv)
    else:
        units = pct = 0
    return dict(state, ships=surv, units=min(units, 499), pct=pct), ships - surv


def torp_ok(battle, D, armor, maxhits):
    tg = [i for i, t in enumerate(battle['toks']) if t['owner'] == 1][0]
    st = dict(ships=battle['toks'][tg]['ships'], units=0, pct=0, armor=armor)
    n = 0
    for h in battle['hits']:
        if h['tok'] != tg or h['flags'] & 0x80:      # 0x80: miss record
            continue
        n += 1
        good = False
        for hits in range(1, maxhits + 1):
            half = hits * D // 2
            s2, kills = damage(st, half + half, hits)
            if kills == h['kills'] and (kills == st['ships'] or (s2['units'], s2['pct']) == (h['units'], h['pct'])):
                good = True
        if not good:
            return False, n
        st = dict(st, ships=st['ships'] - h['kills'], units=h['units'], pct=h['pct'])
    return True, n


def main():
    runs = dict(zip(('W', 'S', 'B', 'C', 'C2'), sys.argv[1:6]))
    st = {k: parse(os.path.join(v, 'after.dump')) for k, v in runs.items()}
    des = {}
    if len(sys.argv) > 6:
        for line in open(sys.argv[6]):
            if line.startswith('design'):
                continue
            f = line.rstrip('\n').split('\t')
            des[int(f[0])] = f[1:]
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(HERE, 'predictions.tsv'))][1:]
    tally = {}
    out = []
    for cid, row, col, setup, pred, alt, chk in rows:
        c = json.loads(chk)
        kind = c[0]
        run = cid.split('-')[2]
        s = st.get(run)
        obs, ok = '', None
        if kind == 'warp10':
            _, owner, fids, rated, tot = c
            left = sum(s['fleets'].get((owner, f), dict(nships=0))['nships'] for f in fids)
            obs = '%d of %d ships left' % (left, tot)
            ok = (left == tot) if rated else (left < tot)
        elif kind == 'fuel':
            f = s['fleets'][(c[1], c[2])]
            obs, ok = 'fuel %s' % f['fuel'], int(f['fuel']) == c[3]
        elif kind == 'field':
            _, owner, num, x, y, n = c
            got = [t['count'] for t in s['things'] if t['owner'] == owner and t['num'] == num]
            obs = 'field %s' % (got[0] if got else 'gone')
            ok = got == [n] or (n <= 0 and not got)
        elif kind == 'newfield':
            _, owner, x, y, n = c
            got = [t['count'] for t in s['things'] if t['owner'] == owner and (t['x'], t['y']) == (x, y)]
            obs, ok = 'new field %s' % (got or 'none'), got == [n]
        elif kind == 'pop':
            p = s['planets'][c[1]]
            obs, ok = 'pop %s' % p.get('pop'), int(p.get('pop', -1)) == c[2]
        elif kind == 'popinst':
            _, n, pop, mines, fac = c
            p = s['planets'][n]
            obs = 'pop %s, mines %s, factories %s' % (p.get('pop'), p.get('mines'), p.get('factories'))
            ok = int(p['pop']) == pop and int(p['mines']) == mines and (fac is None or int(p['factories']) == fac)
        elif kind == 'owner':
            p = s['planets'][c[1]]
            own = int(p['owner'])
            obs = 'owner %s, pop %s' % ('none' if own < 0 else own, p.get('pop', '-'))
            ok = own == (c[2] if c[2] is not None else -1)
        elif kind == 'mined':
            p = s['planets'][c[1]]
            sur = p.get('surface', '0/0/0')
            obs, ok = 'surface %s' % sur, sur == '/'.join([str(c[2])] * 3)
        elif kind in ('torp', 'torp1'):
            x, y, D = c[1], c[2], c[3]
            b = [b for b in s['battles'] if (b['x'], b['y']) == (x, y)][0]
            armor, maxh = (3650, 2) if kind == 'torp' else (c[4], 1)   # salvo = one slot: 2 torpedoes in CS-003-C
            alt_D = D // 2 if 'missile' in pred else D * 2
            okp, n = torp_ok(b, D, armor, maxh)
            oka, _ = torp_ok(b, alt_D, armor, maxh)
            mflag = sorted({h['flags'] & 0x0c for h in b['hits'] if h['flags'] & 4})
            obs = '%d hit records: predicted %s, alternative %s; record flags %s' % (
                n, 'fits' if okp else 'fails', 'fits' if oka else 'fails', ','.join('%02x' % f for f in mflag))
            ok = okp if not oka else None     # None: not discriminated
        elif kind == 'beam0':
            b = [b for b in s['battles'] if (b['x'], b['y']) == XY[c[1]]][0]
            first = b['hits'][0] if b['hits'] else None
            obs = 'first hit on the fort: %s' % (
                'kills=%d units=%d' % (first['kills'], first['units']) if first else 'none')
            # Orbital Fort armor 100: units = damage·500/100 = 5·damage until it dies
            ok = bool(first) and (first['kills'] == 1 or first['units'] == 5 * c[2])
        elif kind == 'designer':
            d = des.get(c[2])
            if d:
                mass, moves, cloak, jam, scan = d
                obs = 'mass %s, moves %s, cloak/jam %s/%s%s' % (mass, moves, cloak, jam, ', scanner %s' % scan if scan else '')
                want = pred.replace('%', '')
                got = 'mass %s, moves %s, cloak/jam %s/%s' % (mass, moves, cloak, jam) + (', scanner %s' % scan if scan else '')
                ok = want == got
        out.append((cid, row, pred, obs, ok))
        tally[ok] = tally.get(ok, 0) + 1
    for cid, row, pred, obs, ok in out:
        print('%-26s %-5s %-26s | predicted: %s | observed: %s' % (
            cid, {True: 'OK', False: 'FAIL', None: 'n/d'}[ok], row, pred, obs))
    print('matched %d, failed %d, not decided %d' % (tally.get(True, 0), tally.get(False, 0), tally.get(None, 0)))


XY = {4: (1143, 1103), 5: (1146, 1180), 12: (1245, 1158)}     # Combat Lab planets used by CS-003-C


if __name__ == '__main__':
    main()
