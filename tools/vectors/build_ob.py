"""OB corpus (universe objects, experiments/ob) -> vectors. Called by build.py
for CORPUS ob with the apparatus evidence/ob directory.

Only cases whose check maps onto an existing vector kind are converted:
planet values, surface minerals, fleets kept, gone or at a position, and
fleets after a stargate jump. Minefield, scan-knowledge, packet-cargo and
wormhole-age checks have no vector kind yet; their cases are left out, and
a run with no convertible case gets no vector. Directories obNNN-cXXXXX are
further random streams of run obNNN; the base directory is cycles 20000.
"""
import os, re, sys
import build as B

sys.path.insert(0, os.path.join(B.ROOT, 'experiments', 'ob'))
import gen  # noqa: E402

PARITY = {
    None: 'docs/PARITY.md "Universe objects"',
    'OB-003': 'docs/PARITY.md "Packets (CONFIRMED except where marked)"',
    'OB-009': 'docs/PARITY.md "Packets (CONFIRMED except where marked)"',
    'OB-004': 'docs/PARITY.md "Mystery Trader (CONFIRMED, OB-004)"',
    'OB-021': 'docs/PARITY.md "Stargates (CONFIRMED, OB-021, OB-022)"',
    'OB-022': 'docs/PARITY.md "Stargates (CONFIRMED, OB-021, OB-022)"',
}
KINDS = {'planet', 'surface', 'fleet', 'fleetat', 'gate', 'mtgift'}
PLANET_KEYS = {'pop': 'population', 'owner': 'owner', 'defenses': 'defenses', 'mines': 'mines',
               'factories': 'factories'}


def load(path):
    planets, fleets, players = {}, {}, {}
    for s in B.dump(path):
        d = B.kv(s)
        if s.startswith('pdetail '):
            planets[int(s.split()[1])] = d
        elif s.startswith('fleet '):
            fleets[(int(d['owner']), int(d['id']))] = d
        elif s.startswith('player ') and 'energy' in d:
            players[int(s.split()[1])] = d
    return planets, fleets, players


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


def observe(k, after, before):
    planets, fleets, players = after
    kind = k[0]
    if kind == 'surface':
        return {'kind': 'planet', 'id': k[1], 'equals': {'surface_minerals': surface(planets[k[1]])}}
    if kind == 'planet':
        p = planets[k[1]]
        eq = {}
        for key in k[2]:
            if key == 'surface':
                eq['surface_minerals'] = surface(p)
            else:
                eq[PLANET_KEYS[key]] = int(p.get(key, -1))
        return {'kind': 'planet', 'id': k[1], 'equals': eq}
    if kind in ('fleet', 'fleetat'):
        f = fleets.get((k[1], k[2]))
        if f is None:
            return {'kind': 'fleet_gone', 'owner': k[1], 'id': k[2]}
        return {'kind': 'fleet', 'owner': k[1], 'id': k[2], 'equals': {'x': int(f['x']), 'y': int(f['y'])}}
    if kind == 'gate':
        f = fleets.get((k[1], k[2]))
        if f is None:
            return {'kind': 'fleet_gone', 'owner': k[1], 'id': k[2]}
        c = [int(x) for x in f['cargo'].split('/')]
        return {'kind': 'fleet', 'owner': k[1], 'id': k[2], 'equals': {
            'x': int(f['x']), 'y': int(f['y']), 'ships': ships(f), 'fuel': int(f['fuel']),
            'cargo': dict(zip(B.CARGO[:4], c))}}
    if kind == 'mtgift':
        gain = sum(int(players[k[1]][t]) - int(before[2][k[1]][t]) for t in B.DUMP_TECH)
        return {'kind': 'sample', 'check': 'trader_gift', 'target': [k[1], k[2]],
                'observed': {'meeting_fleet_gone': (k[1], k[2]) not in fleets, 'tech_levels_gained': gain},
                'constraint': 'the meeting fleet is gone and the player gains %d tech levels' % k[3]}
    raise ValueError(kind)


def held_of(path):
    out = {}
    for line in open(path):
        f = line.split()
        if len(f) >= 3 and f[0].startswith('OB-'):
            out[f[0]] = next((w for w in f[1:4] if w in ('HELD', 'CONTRADICTED', 'OBSERVED')), '?')
    return out


def build(ev, out):
    os.makedirs(out, exist_ok=True)
    for r in gen.RUNS:
        cases = [c for c in r.cases if c['check'][0] in KINDS]
        name = r.rid.lower().replace('-', '')
        dirs = sorted(d for d in os.listdir(ev) if d == name or re.fullmatch(name + r'-c\d+', d))
        if not cases or not dirs:
            continue
        base = os.path.join(ev, dirs[0], 'raw', 'before')
        st = B.state(B.dump(os.path.join(base, 'CB.HST')), B.dump(os.path.join(base, 'CB.XY')), 'CB')
        per_case = {c['id']: ({}, True) for c in cases}
        for d in dirs:
            stream = 'cycles ' + (d.split('-c')[1] if '-c' in d else '20000')
            after = load(os.path.join(ev, d, 'raw', 'after', 'CB.HST'))
            before = load(os.path.join(ev, d, 'raw', 'before', 'CB.HST'))
            held = held_of(os.path.join(ev, d, 'check.txt'))
            for c in cases:
                per, ok = per_case[c['id']]
                per[stream] = [dict(observe(c['check'], after, before), year=1)]
                per_case[c['id']] = (per, ok and held.get(c['id']) == 'HELD')
        vec = {'schema': B.SCHEMA, 'id': r.rid, 'title': r.title,
               'source': {'experiment': 'experiments/ob', 'spec_rules': 'docs/OBJECTS.md',
                          'parity': PARITY.get(r.rid, PARITY[None]),
                          'raw_evidence': 'stars-oracle-apparatus evidence/ob/%s (private)' % ', '.join(dirs)},
               'years': 1, 'random': 'single_stream' if len(dirs) == 1 else 'several_streams',
               'streams': len(dirs), 'initial_state': st, 'cases': []}
        for c in cases:
            per, ok = per_case[c['id']]
            cs = B.case(c['id'], c['pred'], c['what'], per, ok, set())
            cs['prediction'] = c['expect']
            vec['cases'].append(cs)
        with open(os.path.join(out, name + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        print('%s: %d of %d cases, %d streams' % (r.rid, len(cases), len(r.cases), len(dirs)))
