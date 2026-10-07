"""OB corpus (universe objects, experiments/ob) -> vectors. Called by build.py
for CORPUS ob with the apparatus evidence/ob directory.

The run's after.dump and before.dump are read with experiments/ob/check.py's
own loader, and every check tuple is written as the observed outcome:

- planets, surface minerals, fleets kept, gone, at a position or after a
  stargate: `planet`, `fleet`, `fleet_gone`;
- minefields: `minefield` (owner, number; x, y, mines, type, detonating).
  A field that a case expected near a point and that no longer exists is
  written as `minefield` with `mines: 0` for the field the start had there;
- what a player sees (scan, scanfleets, thingin, planetlevel): `view`. The
  scan checks of one run compare the viewer's whole object list, so they
  share one case, `<run>-SCAN`, whose setup names the gen.py cases;
- packets: `object` (the packet as in initial_state.objects);
- the Mystery Trader: `trader`, `player` (mystery_trader_items);
- wormhole jiggles and jumps, fleets following a wormhole, and outcomes
  check.py records without a single prediction: `sample`.

Directories obNNN-cXXXXX are further random streams (the base directory is
cycles 20000); obNNN-y1..y3 are successive years of one run.
"""
import os, re, sys
import build as B

sys.path.insert(0, os.path.join(B.ROOT, 'experiments', 'ob'))
import gen  # noqa: E402
import check as C  # noqa: E402

PARITY = {
    None: 'docs/PARITY.md "Universe objects"',
    'OB-003': 'docs/PARITY.md "Packets (CONFIRMED except where marked)"',
    'OB-009': 'docs/PARITY.md "Packets (CONFIRMED except where marked)"',
    'OB-023': 'docs/PARITY.md "Packets (OB-022, OB-023)"',
    'OB-004': 'docs/PARITY.md "Mystery Trader (CONFIRMED, OB-004)"',
    'OB-021': 'docs/PARITY.md "Stargates (CONFIRMED, OB-021, OB-022)"',
    'OB-022': 'docs/PARITY.md "Stargates (CONFIRMED, OB-021, OB-022)"',
}
PLANET_KEYS = {'pop': 'population', 'owner': 'owner', 'defenses': 'defenses', 'mines': 'mines',
               'factories': 'factories'}
SCAN = {'scan'}
FIELD_TYPES = ['standard', 'heavy', 'speed_bump']


def surface(p):
    return [int(x) for x in p.get('surface', '0/0/0').split('/')]


def ships(d):
    out = []
    for a, b in (x.split(':') for x in d['ships'].split(',') if x):
        sh = {'design': int(a), 'count': int(b)}
        if 'dmg' + a in d:
            u, pc = d['dmg' + a].rstrip('%').split('/')
            sh['damage'] = {'units': int(u), 'percent_of_ships': int(pc)}
        out.append(sh)
    return out


def fleet(fleets, owner, fid, keys=('x', 'y')):
    f = fleets.get((owner, fid))
    if f is None:
        return {'kind': 'fleet_gone', 'owner': owner, 'id': fid}
    eq = {}
    for k in keys:
        if k == 'ships':
            eq['ships'] = ships(f)
        elif k == 'cargo':
            eq['cargo'] = dict(zip(B.CARGO[:4], (int(x) for x in f['cargo'].split('/'))))
        else:
            eq[k] = int(f[k])
    return {'kind': 'fleet', 'owner': owner, 'id': fid, 'equals': eq}


def minefield(t):
    return {'kind': 'minefield', 'owner': int(t['owner']), 'id': int(t['num']), 'equals': {
        'x': int(t['x']), 'y': int(t['y']), 'mines': int(t['count']), 'type': FIELD_TYPES[int(t['kind'])],
        'detonating': t['det'] == '1'}}


def fields(A, Bf, owner, x, y, r=6):
    """Minefields of owner near (x, y) after the year; a start field there
    that is gone becomes object_gone."""
    now = C.fields_near(A[0], owner, x, y, r)
    out = [minefield(t) for t in now]
    nums = {int(t['num']) for t in now}
    for t in C.fields_near(Bf[0], owner, x, y, r):
        if int(t['num']) not in nums and not any(int(u['num']) == int(t['num']) for u in A[0]
                                                 if u['type'] == 'minefield' and int(u['owner']) == owner):
            out.append({'kind': 'object_gone', 'subject': {'kind': 'minefield', 'owner': owner, 'id': int(t['num'])}})
    return out


def thing_subject(t):
    s = {'kind': t['type'], 'id': int(t['num'])}
    if t['type'] in ('minefield', 'packet'):
        s['owner'] = int(t['owner'])
    return s


def sample(check, target, got, constraint):
    return {'kind': 'sample', 'check': check, 'target': target, 'observed': B.json.loads(B.json.dumps(got, default=list)),
            'constraint': constraint}


def observe(c, A, Bf, run, M):
    """-> list of expectations for one case (without year)."""
    k = c['check']
    kind = k[0]
    things, planets, fleets, players, wps = A
    if kind == 'surface':
        return [{'kind': 'planet', 'id': k[1], 'equals': {'surface_minerals': surface(planets[k[1]])}}]
    if kind == 'planet':
        p = planets[k[1]]
        eq = {}
        for key in k[2]:
            if key == 'surface':
                eq['surface_minerals'] = surface(p)
            else:
                eq[PLANET_KEYS[key]] = int(p.get(key, -1))
        return [{'kind': 'planet', 'id': k[1], 'equals': eq}]
    if kind in ('fleet', 'fleetat'):
        return [fleet(fleets, k[1], k[2])]
    if kind == 'gate':
        return [fleet(fleets, k[1], k[2], ('x', 'y', 'ships', 'fuel', 'cargo'))]
    if kind == 'mtgift':
        gain = C.techsum(players[k[1]]) - C.techsum(Bf[3][k[1]])
        return [sample('trader_gift', [k[1], k[2]], {'meeting_fleet_gone': (k[1], k[2]) not in fleets,
                                                     'tech_levels_gained': gain},
                       'the meeting fleet is gone and the player gains %d tech levels' % k[3])]
    if kind in ('field', 'fieldat', 'fields', 'fieldobs'):
        out = fields(A, Bf, k[1], k[2], k[3], 0 if kind == 'fieldat' else 6)
        return out or [sample('no_minefield', list(k[1:4]), [], 'no minefield of player %d within 6 ly' % k[1])]
    if kind == 'nofield':
        out = fields(A, Bf, k[1], k[2], k[3], 30) + fields(A, Bf, k[1], k[4], k[5], 30)
        return out or [sample('no_minefield', list(k[1:]), [], 'no minefield of player %d near either point' % k[1])]
    if kind == 'layhold':
        _, owner, fid, x, y = k[:5]
        out = [fleet(fleets, owner, fid)] + fields(A, Bf, owner, x, y)
        ws = wps.get((owner, fid), [])
        if ws:
            out[0]['equals']['first_waypoint_task'] = B.TASKS[int(ws[0]['task'])]
        return out
    if kind == 'laytask':
        return fields(A, Bf, k[1], k[2], k[3])
    if kind in ('minehit', 'minehit2'):
        owner, fid, x, y = k[1:5]
        return [fleet(fleets, owner, fid, ('x', 'y', 'ships'))] + fields(A, Bf, 1, x, y)
    if kind == 'detonate':
        ok, got = C.evaluate(c, A, Bf, run, M)
        return fields(A, Bf, 0, k[1], k[2]) + [sample('detonation', list(k[1:]), got,
                                                      'fleets within 20 ly of the detonating field after the year')]
    if kind == 'scanfleets':
        return [{'kind': 'view', 'viewer': run.scan['viewer'] if run.scan else 1,
                 'subject': {'kind': 'fleet', 'owner': o, 'id': i}, 'equals': {'known': (o, i) in M[2]}}
                for o, i, _ in k[1]]
    if kind == 'planetlevel':
        return [{'kind': 'view', 'viewer': k[1], 'subject': {'kind': 'planet', 'id': k[2]},
                 'equals': {'level': M[5].get(k[2], 0)}}]
    if kind == 'thingin':
        _, mfile, ids, _want = k
        ids = ids if isinstance(ids, list) else [ids]
        seen = {int(t['id']) for t in C.M_ALL[mfile][0]}
        byid = {int(t['id']): t for t in things + Bf[0]}
        return [{'kind': 'view', 'viewer': mfile - 1, 'subject': thing_subject(byid[i]), 'equals': {'known': i in seen}}
                for i in ids if i in byid]
    if kind == 'packetat':
        ps = [t for t in things if t['type'] == 'packet']
        if k[2] is None:
            return [{'kind': 'object', 'equals': B.thing(t)} for t in ps]
        hit = [t for t in ps if abs(int(t['x']) - k[2]) <= 1 and abs(int(t['y']) - k[3]) <= 1]
        return [{'kind': 'object', 'equals': B.thing(t)} for t in hit] or None
    if kind == 'pkt':
        ps = [t for t in things if t['type'] == 'packet' and int(t['owner']) == k[1] and int(t['num']) == k[2]]
        return [{'kind': 'object', 'equals': B.thing(t)} for t in ps] or None
    if kind == 'traderend':
        ts = [t for t in things if t['type'] == 'trader' and int(t['num']) == k[1]]
        if not ts:
            return [sample('trader_gone', [k[1]], 'gone', 'the Trader left the map')]
        t = B.thing(ts[0])
        if k[2] is None:
            return [sample('trader_course', [k[1]], {x: t[x] for x in ('x', 'y', 'destination', 'warp')},
                           'a new destination on the map edge at warp 7 or 8')]
        return [{'kind': 'trader', 'id': k[1], 'equals': {'x': t['x'], 'y': t['y']}},
                sample('trader_course', [k[1]], {x: t[x] for x in ('destination', 'warp')},
                       'a new destination on the map edge at warp 7 or 8')]
    if kind == 'tradergone':
        ts = [t for t in things if t['type'] == 'trader' and int(t['num']) == k[1]]
        return [sample('trader_gone', [k[1]], 'gone' if not ts else B.thing(ts[0]), 'the Trader left the map')]
    if kind == 'mtpart':
        owner, fid = k[1:]
        return [fleet(fleets, owner, fid), sample('trader_part', [owner, fid], {
            'mystery_trader_items': [B.MT_ITEMS[i] for i in B.mask_players(int(players[owner]['mt'], 16), 13)],
            'tech_levels_gained': C.techsum(players[owner]) - C.techsum(Bf[3][owner])},
            'exactly one new Mystery Trader part and no tech')]
    if kind in ('mtship', 'worm', 'wormage', 'wormjump', 'wormfollow', 'wormlost'):
        ok, got = C.evaluate(c, A, Bf, run, M)
        return [sample(kind, [x for x in k[1:] if not isinstance(x, list)] if kind != 'wormjump' else k[1],
                       got, c['expect'])]
    return None


def held_of(path):
    out = {}
    for line in open(path):
        f = line.split()
        if len(f) >= 3 and f[0].startswith('OB-'):
            out[f[0]] = next((w for w in f[1:4] if w in ('HELD', 'CONTRADICTED', 'OBSERVED')), '?')
    return out


def run_dirs(ev, name):
    """[(stream, year, dir)]"""
    out = []
    for d in sorted(os.listdir(ev)):
        m = re.fullmatch(name + r'(?:-c(\d+)|-y(\d))?', d)
        if m and os.path.isdir(os.path.join(ev, d, 'raw')):
            out.append(('cycles ' + (m.group(1) or '20000'), int(m.group(2) or 1), d))
    return out


def build(ev, out):
    os.makedirs(out, exist_ok=True)
    for r in gen.RUNS:
        name = r.rid.lower().replace('-', '')
        dirs = run_dirs(ev, name)
        if not dirs:
            continue
        first = min(dirs, key=lambda t: (t[1], t[0]))[2]
        base = os.path.join(ev, first, 'raw', 'before')
        st = B.state(B.dump(os.path.join(base, 'CB.HST')), B.dump(os.path.join(base, 'CB.XY')), 'CB',
                     os.path.join(base, 'CB.XY'))
        years = max(y for _, y, _ in dirs)
        streams = sorted({s for s, _, _ in dirs})
        per = {}        # case id -> ({stream: [expectations]}, held, observed-only)
        scan_ids = []
        for stream, year, d in dirs:
            after = os.path.join(ev, d, 'after.dump')
            A, Bf = C.load(after), C.load(after.replace('after.dump', 'before.dump'), 'before')
            M = C.load(after, 'after', 'CB.M%d' % (r.scan['viewer'] + 1)) if r.scan else C.load(after, 'after', 'CB.M2')
            C.M_ALL[1], C.M_ALL[2] = C.load(after, 'after', 'CB.M1'), C.load(after, 'after', 'CB.M2')
            held = held_of(os.path.join(ev, d, 'check.txt'))
            for c in r.cases:
                if c.get('year', 1) != year:
                    continue
                if c['check'][0] in SCAN:
                    scan_ids.append(c['id'])
                    cid, exps = r.rid + '-SCAN', None
                    v = r.scan['viewer']
                    seen = {int(t['id']) for t in M[0]}
                    exps = [{'kind': 'view', 'viewer': v, 'subject': thing_subject(t),
                             'equals': {'known': int(t['id']) in seen}}
                            for t in A[0] if not (t['type'] in ('minefield', 'packet') and int(t['owner']) == v)]
                    if cid in per and stream in per[cid][0]:
                        per[cid] = (per[cid][0], per[cid][1] and held.get(c['id']) == 'HELD', False)
                        continue
                else:
                    cid, exps = c['id'], observe(c, A, Bf, r, M)
                if not exps:
                    continue
                exps = [dict(e, year=year) for e in exps]
                p, h, obs_only = per.get(cid, ({}, True, False))
                p.setdefault(stream, []).extend(exps)
                st_held = held.get(c['id'])
                per[cid] = (p, h and st_held == 'HELD', obs_only or st_held == 'OBSERVED')
        if not per:
            continue
        vec = {'schema': B.SCHEMA, 'id': r.rid, 'title': r.title,
               'source': {'experiment': 'experiments/ob', 'spec_rules': 'docs/OBJECTS.md, docs/SCANNING.md',
                          'parity': PARITY.get(r.rid, PARITY[None]),
                          'raw_evidence': 'stars-oracle-apparatus evidence/ob/%s (private)' % ', '.join(d for _, _, d in dirs)},
               'years': years, 'random': 'single_stream' if len(streams) == 1 else 'several_streams',
               'streams': len(streams), 'initial_state': st, 'cases': []}
        done = set()
        for c in r.cases:
            cid = r.rid + '-SCAN' if c['check'][0] in SCAN else c['id']
            if cid not in per or cid in done:
                continue
            done.add(cid)
            p, held, obs_only = per[cid]
            if cid.endswith('-SCAN'):
                ids = sorted(set(scan_ids))
                setup = 'gen.py cases %s: %s' % (', '.join(ids), '; '.join(x['what'] for x in r.cases if x['id'] in ids))
                cs = B.case(cid, ', '.join(sorted({x['pred'] for x in r.cases if x['id'] in ids})), setup, p, held, set())
            else:
                cs = B.case(cid, c['pred'], c['what'], p, held and not obs_only, set())
                cs['prediction'] = c['expect']
            vec['cases'].append(cs)
        with open(os.path.join(out, name + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        print('%s: %d of %d cases, %d streams, %d years' % (r.rid, len(vec['cases']), len(r.cases), len(streams), years))
