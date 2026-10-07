"""PG-002 and PG-003 corpora (population growth) -> vectors. Called by build.py
for CORPUS pg with the apparatus `evidence` directory.

Each run is the pristine PG001 2407 universe advanced year by year with no
orders; the run kept the .HST of every year (raw/YYYY-PG001-<sha8>.HST) but
not the .XY, which no turn changes, so the .XY comes from the PQ-001 corpus
(evidence/pq001/raw/P0/before). The expectations are planet 7's population
and growth carry (`excess`) each year. The runs were not pinned to a random
stream (each turn seeded from the clock), so only quantities with no random
draw are recorded: minerals, which include a random mining draw, are left out.
"""
import glob, os
import build as B

PLANET = 7
SPEC = 'docs/KERNEL.md "Population growth"'
RUNS = [
    ('PG-002', 'pg002', 'PG001 2407 advanced 19 years with empty orders; first crowded year 2426; unpinned clock-seeded turns, so random outcomes (mining) are not exact',
     'docs/PARITY.md "Measured behavior — PG-002, first crowded turn"'),
    ('PG-003', 'pg003', 'PG001 2407 advanced 29 years with empty orders; crowded years 2426-2436 (repeats PG-002); unpinned clock-seeded turns, so random outcomes (mining) are not exact',
     'docs/PARITY.md "Measured behavior — PG-003, crowded turns 2427–2436"'),
]
CROWDED = 2426  # first year whose start population is above 25% of capacity


def build(ev, out):
    os.makedirs(out, exist_ok=True)
    xy = B.dump(os.path.join(ev, 'pq001', 'raw', 'P0', 'before', 'PG001.XY'))
    for rid, d, title, parity in RUNS:
        files = sorted(glob.glob(os.path.join(ev, d, 'raw', '24??-PG001-*.HST')))
        st = B.state(B.dump(files[0]), xy, 'PG001')
        start = st['year']
        uncrowded, crowded = [], []
        for f in files[1:]:
            year = int(os.path.basename(f)[:4])
            p = B.kv(next(s for s in B.dump(f) if s.startswith('pdetail %d ' % PLANET)))
            e = {'year': year - start, 'kind': 'planet', 'id': PLANET,
                 'equals': {'population': int(p['pop']), 'excess': int(p['excess'])}}
            (crowded if year >= CROWDED else uncrowded).append(e)
        last = int(os.path.basename(files[-1])[:4])
        cases = [B.case(rid + '-A', 'KERNEL Population growth: uncrowded growth and carry (PG-001 model)',
                        'years %d-%d, population below 25%% of capacity at the start of each year' % (start + 1, CROWDED - 1),
                        {'run': uncrowded}, True, set()),
                 B.case(rid + '-B', 'KERNEL Population growth: crowding factor above 25% of capacity',
                        'years %d-%d; the run\'s predictions (H0-H2) were all rejected' % (CROWDED, last),
                        {'run': crowded}, False, set())]
        vec = {'schema': B.SCHEMA, 'id': rid, 'title': title,
               'source': {'experiment': rid + ' (no generator; procedure in PARITY.md)', 'spec_rules': SPEC,
                          'parity': parity,
                          'raw_evidence': 'stars-oracle-apparatus evidence/%s/raw (private)' % d},
               'years': last - start, 'random': 'single_stream', 'streams': 1, 'initial_state': st,
               'cases': cases}
        with open(os.path.join(out, d + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        print('%s: %d years, %d + %d expectations' % (rid, last - start, len(uncrowded), len(crowded)))
