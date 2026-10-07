"""CS-003 corpus (component stats) -> vectors. Called by build.py for CORPUS cs
with the apparatus evidence/cs/cs-003 directory.

Only the CS-003 runs whose checks map onto vector kinds are converted:
run W (warp 10 losses per engine, fuel generation) and run B (bombs,
colonization, the Orbital Adjuster). Runs S (minefield sweeping), C and C2
(torpedo hit records) and D (designer readouts) check quantities the vector
schema has no kind for yet. Expectations are re-read from each run's
after/CB.HST; check.txt records every case as matching its prediction.
"""
import json, os
import build as B

PARITY = 'docs/PARITY.md "The remaining BINARY-ONLY columns (CS-003, CONFIRMED 2026-10-07)"'
SPEC = 'docs/COMPONENTS.md'
RUNS = {'W': 'one year of warp-10 travel per engine; fuel generation of stationary ships',
        'B': 'one year of bombing per bomb type; colonizing with an Orbital Construction Module; Orbital Adjuster'}


def after(rdir):
    fleets, planets = {}, {}
    for s in B.dump(os.path.join(rdir, 'raw', 'after', 'CB.HST')):
        d = B.kv(s)
        if s.startswith('fleet '):
            fleets[(int(d['owner']), int(d['id']))] = d
        elif s.startswith('pdetail '):
            planets[int(s.split()[1])] = d
    return fleets, planets


def ships(d):
    return [{'design': int(a), 'count': int(b)} for a, b in (x.split(':') for x in d['ships'].split(',') if x)]


def observe(chk, fleets, planets):
    """-> (expectations, deterministic)"""
    k = chk[0]
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
    for run, title in RUNS.items():
        rdir = os.path.join(ev, 'run-' + run.lower())
        before = os.path.join(rdir, 'raw', 'before')
        st = B.state(B.dump(os.path.join(before, 'CB.HST')), B.dump(os.path.join(before, 'CB.XY')), 'CB',
                     os.path.join(before, 'CB.XY'))
        fleets, planets = after(rdir)
        rid = 'CS-003-' + run
        vec = {'schema': B.SCHEMA, 'id': rid, 'title': title,
               'source': {'experiment': 'experiments/cs003', 'spec_rules': SPEC, 'parity': PARITY,
                          'raw_evidence': 'stars-oracle-apparatus evidence/cs/cs-003/run-%s (private)' % run.lower()},
               'years': 1, 'random': 'single_stream', 'streams': 1, 'initial_state': st, 'cases': []}
        for cid, row, col, setup, pred, alt, chk in rows:
            if cid.split('-')[2] != run:
                continue
            exps, det = observe(json.loads(chk), fleets, planets)
            if exps is None:
                continue
            c = B.case(cid, 'COMPONENTS %s: %s' % (row, col), setup, {'cycles 20000': [dict(e, year=1) for e in exps]},
                       ok.get(cid) == 'OK', set())
            c['prediction'] = pred
            vec['cases'].append(c)
        with open(os.path.join(out, 'cs003' + run.lower() + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        print('%s: %d cases' % (rid, len(vec['cases'])))
