"""PQ-001 corpus (production queues) -> vectors. Called by build.py for CORPUS pq.

PQ-001 has no generator or check.out: each case is a hand-edited PG001 2407
state (planet 7 and player 0) run for one year, or two for C01 and C14.
This adapter reads each case's before/ files for the initial state and the
after/ files for the observed outcome: planet 7's minerals and
installations, its production queue (with partial percentages), player 0's tech and research
accumulation (where the year's research went), and the year's message ids.
PARITY.md "PQ-001" records every case as matching its prediction.
"""
import os
import build as B

PARITY = 'docs/PARITY.md "PQ-001 — production-queue boundary corpus"'
SPEC = 'docs/KERNEL.md "Production"'
PLANET, PLAYER = 7, 0
COMPLETED = 0x3e  # "completed its orders"

# case -> (rule, setup, repeat dirs). Setup text summarises PARITY.md's
# prediction table; common edits are mines 0, factories 0, defenses 10,
# research budget 0%, leftover-only off, minerals 500/500/500.
CASES = {
    'C01': ('KERNEL Production: partial percentage; spent amount of a carried partial',
            'pop 1050 (R 105); Factory x20; two years'),
    'C02': ('KERNEL Production: a non-auto item short of a mineral stops the queue',
            'pop 2000 (R 200), Ge 10; Factory x5, Mine x5'),
    'C03': ('KERNEL Production: an auto item short of a mineral is skipped and suppresses "completed its orders"',
            'pop 2000, Ge 2; Auto Factories x100, Mine x5'),
    'C04': ('KERNEL Production: a resource-limited auto item leaves a hidden x1 partial at the front',
            'pop 230 (R 23); Auto Mines x100'),
    'C05': ('KERNEL Production: Auto Alchemy as the last item ignores its count',
            'pop 2500 (R 250), minerals 100/100/100; Auto Alchemy x1'),
    'C06': ('KERNEL Production: Auto Alchemy before an item buys its mineral shortfall',
            'pop 4000 (R 400), minerals 100/100/1; Auto Alchemy x1, Factory x1, Mine x2'),
    'C07': ('KERNEL Production: Auto Alchemy prefix short of resources leaves a Mineral Alchemy partial',
            'pop 2500, minerals 100/100/1; Auto Alchemy x1, Factory x1, Mine x2', ['C07', 'C07r']),
    'C08a': ('KERNEL Research: the research tax is taken before production',
             'pop 1070 (R 107), research budget 15%; Factory x20'),
    'C08b': ('KERNEL Research: the leftover-only box skips the research tax',
             'pop 1070 (R 107), research budget 15%, leftover-only on; Factory x20'),
    'C09': ('KERNEL Production: auto caps from operable installations after growth; mining (not predicted)',
            'pop 500, factories 50, mines 48 (R 100); Auto Mines x100, Auto Factories x3'),
    'C10': ('KERNEL Production: non-auto installation orders are clipped to the cap, with a message',
            'pop 1000, factories 995 (R 200); Factory x10'),
    'C11': ('KERNEL Production: remaining cost of a carried partial; a zero-resource partial',
            'pop 50 (R 5), minerals 100/100/2; Factory x1 @59%, Mine x10', ['C11', 'C11r']),
    'C12': ('KERNEL Production: the partial percentage is the minimum over cost components',
            'pop 1000 (R 100), minerals 3/2/100; Defenses x5, Mine x2'),
    'C13': ('KERNEL Production: operable defenses cap ceil(P/25) after growth',
            'pop 1010 (R 101), defenses 40; Auto Defenses x100'),
    'C14': ('KERNEL Production: the hidden partial is finished first next year',
            'pop 230 (R 23); Auto Mines x100; two years'),
    'P0': ('KERNEL Research: research tax; leftover goes to research; mining',
           'pilot: unedited PG001 2407 (budget 15%, its own mines and factories) plus Factory x5'),
}


def after_dirs(case_dir):
    if os.path.isdir(os.path.join(case_dir, 'after')):
        return [os.path.join(case_dir, 'after')]
    return [os.path.join(case_dir, 'after1'), os.path.join(case_dir, 'after2')]


def observe(year, adir, mined):
    """Expectations for one generated year from its .HST and .M1. When the
    planet had mines at the start of the year (`mined`), its minerals include
    the mining draw and go in a separate sampled expectation."""
    hst = B.dump(os.path.join(adir, 'PG001.HST'))
    m1 = B.dump(os.path.join(adir, 'PG001.M1'))
    planet, queue, player = None, [], None
    for s in hst:
        d = B.kv(s)
        if s.startswith('pdetail %d ' % PLANET):
            planet = d
        elif s.startswith('queue planet=%d ' % PLANET):
            queue = [it.split(':') for it in d.get('items', '').split(',') if it]
        elif s.startswith('player %d ' % PLAYER) and 'energy' in d:
            player = d
    minerals = [int(x) for x in planet['surface'].split('/')]
    eq = {'mines': int(planet['mines']), 'factories': int(planet['factories']), 'defenses': int(planet['defenses'])}
    if not mined:
        eq = dict(surface_minerals=minerals, **eq)
    out = [
        {'year': year, 'kind': 'planet', 'id': PLANET, 'equals': eq},
        {'year': year, 'kind': 'production_queue', 'planet': PLANET,
         'equals': [{k: v for k, v in B.queue_item(i).items() if k != 'kind'} for i in queue]},
        {'year': year, 'kind': 'player', 'id': PLAYER, 'equals': {
            'tech': {B.TECH[i]: int(player[B.DUMP_TECH[i]]) for i in range(6)},
            'research_accumulated': dict(zip(B.TECH, (int(x) for x in player['accum'].split(','))))}},
    ]
    ids = []
    for s in m1:
        if s.startswith('msg '):
            mid = int(B.kv(s)['id'], 16)
            if mid not in ids:
                ids.append(mid)
    for mid in ids:
        out.append({'year': year, 'kind': 'message', 'player': PLAYER, 'message_id': mid, 'present': True})
    if COMPLETED not in ids:
        out.append({'year': year, 'kind': 'message', 'player': PLAYER, 'message_id': COMPLETED, 'present': False})
    sample = None
    if mined:
        sample = {'year': year, 'kind': 'sample', 'check': 'surface_minerals_after_mining', 'target': [PLANET],
                  'observed': minerals,
                  'constraint': 'production spending plus mining, which includes a random draw '
                                '(KERNEL.md "Mining"); the run was not pinned to a random stream'}
    return out, sample, int(planet['mines'])


def build(ev, out):
    os.makedirs(out, exist_ok=True)
    raw = os.path.join(ev, 'raw')
    for name, spec in CASES.items():
        rule, setup = spec[0], spec[1]
        dirs = spec[2] if len(spec) > 2 else [name]
        before = os.path.join(raw, dirs[0], 'before')
        st = B.state(B.dump(os.path.join(before, 'PG001.HST')), B.dump(os.path.join(before, 'PG001.XY')), 'PG001',
                     os.path.join(before, 'PG001.XY'))
        mines0 = next(p['mines'] for p in st['planets'] if p['id'] == PLANET)
        per, sampled = {}, {}
        for d in dirs:
            exps, mines = [], mines0
            for y, adir in enumerate(after_dirs(os.path.join(raw, d)), 1):
                e, smp, mines2 = observe(y, adir, mines > 0)
                exps += e
                if smp:
                    sampled.setdefault('run ' + d, []).append(smp)
                mines = mines2
            per['run ' + d] = exps
        years = max(e['year'] for e in per['run ' + dirs[0]])
        rid = 'PQ-001-' + name
        vec = {'schema': B.SCHEMA, 'id': rid, 'title': 'production queue: ' + setup,
               'source': {'experiment': 'PQ-001 (no generator; edits in PARITY.md)', 'spec_rules': SPEC,
                          'parity': PARITY,
                          'raw_evidence': 'stars-oracle-apparatus evidence/pq001/raw/%s (private)' % ', '.join(dirs)},
               'years': years,
               'random': 'single_stream' if len(dirs) == 1 else 'several_streams',
               'streams': len(dirs), 'initial_state': st,
               'cases': [B.case(rid, rule, setup, per, True, set())]}
        if sampled:
            vec['cases'].append(B.case(rid + '-mining', 'KERNEL Mining (not predicted by PQ-001)',
                                       setup + '; surface minerals after the year\'s mining', sampled, True, set()))
        with open(os.path.join(out, name.lower() + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        print('%s: %d years, %d streams, %d expectations' % (rid, years, len(dirs), len(vec['cases'][0]['expect'])))
