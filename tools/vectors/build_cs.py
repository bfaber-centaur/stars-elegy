"""CS-003 corpus (component stats) -> vectors. Called by build.py for CORPUS cs
with the apparatus evidence/cs/cs-003 directory.

One vector per CS-003 run: W (warp 10 losses per engine, fuel
generation), B (bombs, colonization, the Orbital Adjuster), S (minefield
sweeping by each beam weapon, new fields), C and C2 (torpedo and missile
hit records; one battle per weapon) and D (the ship designer's readouts,
typed from screenshots into experiments/cs003/designer.tsv, as
client_estimate). Expectations are re-read from each run's after/ files;
check.txt records each case's result.
"""
import json, os, re
import build as B
import build_cb

PARITY = 'docs/PARITY.md "The remaining BINARY-ONLY columns (CS-003, CONFIRMED 2026-10-07)"'
SPEC = 'docs/COMPONENTS.md'
RUNS = {'W': 'one year of warp-10 travel per engine; fuel generation of stationary ships',
        'B': 'one year of bombing per bomb type; colonizing with an Orbital Construction Module; Orbital Adjuster',
        'S': 'one year of minefield sweeping per beam weapon; mine laying by the Super Mine Layer',
        'C': 'torpedo and missile damage per hit; minimum beam damage against an Orbital Fort',
        'C2': 'torpedo and missile damage per hit against heavier armor',
        'D': 'ship designer readouts: mass, battle movement, cloaking, jamming, scanner ranges'}
FIELD_TYPES = ['standard', 'heavy', 'speed_bump']
PLANET_XY = {4: (1143, 1103), 5: (1146, 1180), 12: (1245, 1158)}   # experiments/cs003/check.py XY


def after(rdir):
    fleets, planets, fields, battles = {}, {}, [], {}
    adir = os.path.join(rdir, 'raw', 'after')
    for s in B.dump(os.path.join(adir, 'CB.HST')):
        d = B.kv(s)
        if s.startswith('fleet '):
            fleets[(int(d['owner']), int(d['id']))] = d
        elif s.startswith('pdetail '):
            planets[int(s.split()[1])] = d
        elif s.startswith('thing ') and d.get('type') == 'minefield':
            fields.append(d)
    for f in sorted(os.listdir(adir)):
        if re.search(r'\.M\d+$', f):
            for b in build_cb.battles(B.dump(os.path.join(adir, f))).values():
                battles[(b['x'], b['y'])] = b
    return fleets, planets, fields, battles


def minefield(t):
    return {'kind': 'minefield', 'owner': int(t['owner']), 'id': int(t['num']), 'equals': {
        'x': int(t['x']), 'y': int(t['y']), 'mines': int(t['count']), 'type': FIELD_TYPES[int(t['kind'])],
        'detonating': t['det'] == '1'}}


def battle(battles, x, y):
    b = dict(battles[(x, y)])
    acts = b.pop('actions')
    return [b, {'kind': 'battle_actions', 'x': x, 'y': y, 'actions': acts}]


def moves(s):
    """'2 1/4' -> 2.25"""
    total = 0.0
    for part in s.split():
        a, _, b = part.partition('/')
        total += int(a) / int(b) if b else int(a)
    return total


def designer(row):
    mass, mv, cloak, jam, scan = row
    out = [('mass', {'kt': int(mass)}), ('battle_movement', {'squares': moves(mv)}),
           ('cloaking', {'percent': int(cloak)}), ('jamming', {'percent': int(jam)})]
    if scan:
        a, b = (int(x) for x in scan.split('/'))
        out.append(('scanner', {'normal_ly': a, 'penetrating_ly': b}))
    return out


def ships(d):
    return [{'design': int(a), 'count': int(b)} for a, b in (x.split(':') for x in d['ships'].split(',') if x)]


def observe(chk, obs, designs=None):
    """-> (expectations, deterministic)"""
    fleets, planets, fields, battles = obs
    k = chk[0]
    if k == 'field':
        _, owner, num, x, y, n = chk
        got = [t for t in fields if int(t['owner']) == owner and int(t['num']) == num]
        return ([minefield(got[0])] if got else
                [{'kind': 'object_gone', 'subject': {'kind': 'minefield', 'owner': owner, 'id': num}}]), True
    if k == 'newfield':
        _, owner, x, y, n = chk
        return [minefield(t) for t in fields if int(t['owner']) == owner and (int(t['x']), int(t['y'])) == (x, y)], True
    if k in ('torp', 'torp1'):
        return battle(battles, chk[1], chk[2]), False
    if k == 'beam0':
        return battle(battles, *PLANET_XY[chk[1]]), False
    if k == 'designer':
        return [{'kind': 'client_estimate', 'screen': 'ship_designer', 'subject': {'kind': 'design', 'owner': 0,
                 'slot': chk[2]}, 'field': f, 'equals': v} for f, v in designer(designs[chk[2]])], True
    if k == 'warp10':
        _, owner, fids, rated, total = chk
        if rated:
            return [{'kind': 'fleet', 'owner': owner, 'id': f, 'equals': {'ships': ships(fleets[(owner, f)])}}
                    if (owner, f) in fleets else {'kind': 'fleet_gone', 'owner': owner, 'id': f} for f in fids], True
        left = {str(f): sum(s['count'] for s in ships(fleets[(owner, f)])) if (owner, f) in fleets else 0 for f in fids}
        return [{'kind': 'sample', 'check': 'warp10_losses', 'target': [owner] + fids, 'observed': left,
                 'constraint': 'ships left per fleet of 10; engine not rated for warp 10: some of the %d ships lost '
                               '(KERNEL.md "Fleet movement")' % total}], False
    if k == 'fuel':
        return [{'kind': 'fleet', 'owner': chk[1], 'id': chk[2], 'equals': {'fuel': int(fleets[(chk[1], chk[2])]['fuel'])}}], True
    p = planets[chk[1]]
    if k == 'pop':
        return [{'kind': 'planet', 'id': chk[1], 'equals': {'population': int(p['pop'])}}], True
    if k == 'popinst':
        eq = {'population': int(p['pop']), 'mines': int(p['mines'])}
        if chk[4] is not None:
            eq['factories'] = int(p['factories'])
        return [{'kind': 'planet', 'id': chk[1], 'equals': eq}], True
    if k == 'owner':
        return [{'kind': 'planet', 'id': chk[1], 'equals': {'owner': int(p['owner'])}}], True
    if k == 'mined':
        return [{'kind': 'planet', 'id': chk[1], 'equals': {
            'surface_minerals': [int(x) for x in p.get('surface', '0/0/0').split('/')]}}], True
    return None, None


def build(ev, out):
    os.makedirs(out, exist_ok=True)
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(ev, 'predictions.tsv'))][1:]
    ok = {l.split()[0]: l.split()[1] for l in open(os.path.join(ev, 'check.txt')) if l.startswith('CS-003-')}
    verdict = {l.split()[0]: l.split('| observed: ')[1].strip() for l in open(os.path.join(ev, 'check.txt'))
               if l.startswith('CS-003-') and '| observed: ' in l}
    designs = {int(f[0]): f[1:] for f in (l.rstrip('\n').split('\t') for l in
               open(os.path.join(B.ROOT, 'experiments', 'cs003', 'designer.tsv')).read().splitlines()[1:])}
    for run, title in RUNS.items():
        rdir = os.path.join(ev, 'run-' + run.lower())
        before = os.path.join(rdir, 'raw', 'before')
        st = B.state(B.dump(os.path.join(before, 'CB.HST')), B.dump(os.path.join(before, 'CB.XY')), 'CB',
                     os.path.join(before, 'CB.XY'))
        obs = after(rdir)
        rid = 'CS-003-' + run
        vec = {'schema': B.SCHEMA, 'id': rid, 'title': title,
               'source': {'experiment': 'experiments/cs003', 'spec_rules': SPEC, 'parity': PARITY,
                          'raw_evidence': 'stars-oracle-apparatus evidence/cs/cs-003/run-%s (private)' % run.lower()},
               'years': 1, 'random': 'single_stream', 'streams': 1, 'initial_state': st, 'cases': []}
        for cid, row, col, setup, pred, alt, chk in rows:
            if cid.split('-')[2] != run:
                continue
            exps, det = observe(json.loads(chk), obs, designs)
            if not exps:
                continue
            c = B.case(cid, 'COMPONENTS %s: %s' % (row, col), setup, {'cycles 20000': [dict(e, year=1) for e in exps]},
                       ok.get(cid) in ('OK', 'n/d'), set())
            c['prediction'] = pred
            if not det:
                # one pinned stream of a random battle: the records are exact for that stream only
                c['tag'] = 'MEASURED'
                c['verdict'] = ('prediction not discriminated: ' if ok.get(cid) == 'n/d' else '') + verdict.get(cid, '')
            vec['cases'].append(c)
        with open(os.path.join(out, 'cs003' + run.lower() + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        print('%s: %d cases' % (rid, len(vec['cases'])))
