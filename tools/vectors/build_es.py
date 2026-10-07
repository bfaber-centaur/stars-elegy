"""ES-001 and ES-002 corpora (client estimates) -> vectors. Called by build.py
for CORPUS es with the apparatus evidence/es directory.

Each run is one generated year from a Combat Lab start; afterwards the
values the original client displays (waypoint distance, travel time and
fuel, estimated range, report ETA, production completion, research,
population popup, planet value and mining rate) were read off its screens
into results.tsv. Each reading becomes a `client_estimate` expectation
holding the value as a number or a short value with its unit, never the
client's wording. check.txt lists the readings that missed a prediction.
"""
import os, re
import build as B

RUNS = [('ES-001', 'es-001', 'client estimates after one year: fleets, production, research, planets',
         'docs/PARITY.md "Client estimates (ES-001)"'),
        ('ES-002', 'es-002', 'client estimates follow-up: stargate legs, Skipped, report ETA, Generalized Research, a maxed field',
         'docs/PARITY.md "Client estimates follow-up (ES-002)"')]
SCREENS = [('Fleet Waypoints', 'fleet_waypoints'), ('Fleet Composition', 'fleet_composition'),
           ('Fleet Summary Report', 'fleet_summary_report'), ('Fleet report', 'fleet_summary_report'),
           ('Planet Summary Report', 'planet_summary_report'), ('Production dialog', 'production_dialog'),
           ('Production tile', 'production_tile'), ('Research dialog', 'research_dialog'),
           ('Status tile', 'status_tile')]
WORDS = {'Never': 'never', 'Uncertain': 'uncertain', 'Unknown': 'unknown', 'Danger': 'danger', 'Unload': 'unload',
         'Infinite': 'infinite', 'Skipped': 'skipped', 'As Needed': 'as_needed', 'Maxed Out': 'maxed_out',
         'same field': 'same_field'}
SECTION = {'distance': 'ESTIMATES Leg distance', 'travel_time': 'ESTIMATES Travel time',
           'fuel_usage': 'ESTIMATES Est. fuel usage', 'range': 'ESTIMATES Est. range', 'eta': 'ESTIMATES Travel time',
           'completion': 'ESTIMATES Production completion', 'population': 'ESTIMATES Population popup',
           'value': 'ESTIMATES Value and optimal value', 'mining_rate': 'ESTIMATES Mining rate'}


def num(s):
    return float(s) if '.' in s else int(s)


def value(obs):
    """The displayed value as {unit: number} or {"state": word}."""
    red = obs.endswith(' (red)')
    obs = obs[:-6] if red else obs
    if obs in WORDS:
        v = {'state': WORDS[obs]}
    elif re.fullmatch(r'[\d.]+ (Light Years|l\.y\.)', obs):
        v = {'light_years': num(obs.split()[0])}
    elif re.fullmatch(r'\d+ years?|\d+y', obs):
        v = {'years': int(re.match(r'\d+', obs).group())}
    elif re.fullmatch(r'\d+ - (\d+|\?\?\?) years', obs):
        a, b = re.match(r'(\d+) - (\S+)', obs).groups()
        v = {'years_min': int(a), 'years_max': None if b == '???' else int(b)}
    elif re.fullmatch(r'\d+mg', obs):
        v = {'mg': int(obs[:-2])}
    elif re.fullmatch(r'-?\d+% / \d+%', obs):
        a, b = re.findall(r'-?\d+', obs)
        v = {'value_percent': int(a), 'optimal_percent': int(b)}
    elif re.fullmatch(r'\d+/\d+/\d+', obs):
        v = {'kt_per_year': [int(x) for x in obs.split('/')]}
    elif obs.startswith('grow by'):
        a, b = re.findall(r'\d+', obs)
        v = {'growth': int(a), 'next_year': int(b)}
    elif obs == '(no growth line)':
        v = {'state': 'no_growth_line'}
    elif 'kill off approximately' in obs:
        v = {'death_percent': num(re.search(r'approximately ([\d.]+)%', obs).group(1))}
    elif re.fullmatch(r'\d+', obs):
        v = {'resources': int(obs)}
    else:
        raise ValueError(obs)
    if red:
        v['warning'] = True
    return v


def reading(item, obs, where):
    """-> (subject, field, screen) or None for a host-file row."""
    screen = next((s for k, s in SCREENS if where.startswith(k)), None)
    if screen is None:
        return None
    m = re.match(r'fleet (\d+) (wp (\d+) )?(.*)', item)
    if m:
        subj = {'kind': 'fleet', 'owner': 0, 'id': int(m.group(1))}
        if m.group(3):
            subj['waypoint'] = int(m.group(3))
        rest = m.group(4)
        field = ('distance' if rest == 'distance' else 'travel_time' if rest == 'travel time' else
                 'fuel_usage' if rest == 'est fuel usage' else 'range' if rest.startswith('est. range') else
                 'eta' if rest == 'report ETA' else None)
        return subj, field, screen
    m = re.match(r'planet (\d+) (.*)', item)
    if m:
        subj, rest = {'kind': 'planet', 'id': int(m.group(1))}, m.group(2)
        q = re.match(r'item (\d+) ', rest)
        if q:
            return dict(subj, queue_item=int(q.group(1))), 'completion', screen
        field = ('population' if rest.startswith('population') else 'value' if rest.startswith('value') else
                 'mining_rate' if rest == 'mining rate' else None)
        return subj, field, screen
    m = re.match(r'(?:player (\d+) )?(.*)', item)
    subj, rest = {'kind': 'player', 'id': int(m.group(1) or 0)}, m.group(2)
    f = re.match(r'(?:field )?(\w+) \(?level (\d+)\)?.*resources needed', rest)
    if f:
        return dict(subj, research_field=f.group(1), level=int(f.group(2))), 'resources_needed', screen
    rest = re.sub(r' \(GR\)$', '', rest).replace('resources needed to complete', 'resources needed')
    field = re.sub(r'[^a-z0-9]+', '_', rest.lower().replace("year's", 'year')).strip('_')
    return subj, field, screen


def build(ev, out):
    os.makedirs(out, exist_ok=True)
    for rid, d, title, parity in RUNS:
        rdir = os.path.join(ev, d)
        before = os.path.join(rdir, 'raw', 'before')
        st = B.state(B.dump(os.path.join(before, 'CB.HST')), B.dump(os.path.join(before, 'CB.XY')), 'CB',
                     os.path.join(before, 'CB.XY'))
        missed = {m.group(1) for m in re.finditer(r'^MISMATCH (\S+)', open(os.path.join(rdir, 'check.txt')).read(), re.M)}
        cases = {}
        for line in open(os.path.join(rdir, 'results.tsv')).read().splitlines()[1:]:
            cid, item, obs, where = line.split('\t')[:4]
            r = reading(item, obs, where)
            if r is None:
                if cid == 'K1':      # host file after the year: player 1's energy level
                    e = {'kind': 'player', 'id': 1, 'equals': {'tech': {'energy': int(obs)}}}
                    cases.setdefault(cid, ('KERNEL Research', item, []))[2].append(e)
                continue
            subj, field, screen = r
            e = {'kind': 'client_estimate', 'screen': screen, 'subject': subj, 'field': field, 'equals': value(obs)}
            rule = SECTION.get(field, 'ESTIMATES Research')
            cases.setdefault(cid, (rule, item, []))[2].append(e)
        vec = {'schema': B.SCHEMA, 'id': rid, 'title': title,
               'source': {'experiment': 'experiments/' + d.replace('-', ''), 'spec_rules': 'docs/ESTIMATES.md',
                          'parity': parity, 'raw_evidence': 'stars-oracle-apparatus evidence/es/%s (private)' % d},
               'years': 1, 'random': 'single_stream', 'streams': 1, 'initial_state': st, 'cases': []}
        for cid, (rule, item, exps) in cases.items():
            setup = re.sub(r' (distance|travel time|est fuel usage)$', '', item) if '-w' in cid else item
            vec['cases'].append(B.case('%s-%s' % (rid, cid), rule, setup,
                                       {'cycles 20000': [dict(e, year=1) for e in exps]}, cid not in missed, set()))
        with open(os.path.join(out, d.replace('-', '') + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        print('%s: %d cases, %d readings' % (rid, len(vec['cases']), sum(len(c['expect']) for c in vec['cases'])))
