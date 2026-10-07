"""UG corpus (universe generation) -> new-game vectors. Called by build.py
for CORPUS ug with the apparatus evidence/ug/run directory.

Each game was built from a definition file (docs/ORACLE.md "New games from
a definition file"); the vector's `new_game` holds the definition's
settings and every player's race as the new host file records it, and the
expectations (year 0) describe the generated game. Starting tech and the
number of designs are exact; everything placed by the generator's random
stream (planet count near the candidate limit, which planet is a
homeworld, positions, the shared homeworld mineral draw) is a sample.
ugNN-cXXXXX directories are further streams of game ugNN.
"""
import os, re
import build as B

SIZES = ['tiny', 'small', 'medium', 'large', 'huge']
DENSITIES = ['sparse', 'normal', 'dense', 'packed']
# the seven option flags of a definition file, in order; 2, 5 and 6 are
# not separately identified by this corpus
FLAGS = ['maximum_minerals', 'flag_2', 'accelerated_bbs', 'no_random_events', 'flag_5', 'flag_6', 'galaxy_clumping']


def definition(path):
    lines = [l.strip() for l in open(path, encoding='latin-1').read().replace('\r', '').split('\n')]
    size, density, positions, seed = map(int, lines[1].split())
    flags = list(map(int, lines[2].split()))
    n = int(lines[3])
    players, i = [], 4
    for p in range(n):
        if lines[i].startswith('#'):
            r, lv = map(int, lines[i][1:].split())
            players.append({'player': p, 'computer': {'race': r, 'level': lv}})
        else:
            players.append({'player': p, 'race_file': lines[i].lower()})
        i += 1
    victory = [list(map(int, l.split())) for l in lines[i:i + 8]]
    return {'size': SIZES[size], 'density': DENSITIES[density], 'player_positions': positions, 'seed': seed,
            'options': dict(zip(FLAGS, (bool(f) for f in flags))),
            'victory_condition_lines': victory}, players


NO_INSTALLATIONS = ' excess=0 mines=0 factories=0 defenses=0 scanner=31 leftover=false'


def observe(hst, xy):
    # an AR homeworld has no installations section; B.state needs the keys
    lines = [s + NO_INSTALLATIONS if s.startswith('pdetail ') and 'surface=' in s and 'mines=' not in s else s
             for s in B.dump(hst)]
    st = B.state(lines, B.dump(xy), 'UG')
    planets = sum(1 for s in lines if s.startswith('pdetail '))
    worms = sum(1 for s in lines if s.startswith('thing ') and 'type=wormhole' in s)
    hw, extra = {}, {}
    for s in lines:
        if s.startswith('pdetail ') and 'surface=' in s:
            d = B.kv(s)
            v = {'population': int(d['pop']), 'mines': int(d['mines']), 'factories': int(d['factories']),
                 'defenses': int(d['defenses']), 'surface_minerals': [int(x) for x in d['surface'].split('/')],
                 'concentrations': [int(x) for x in d['conc'].split('/')]}
            (hw if ' homeworld ' in s else extra).setdefault(int(d['owner']), []).append(v)
    spend = {int(s.split()[1]): int(B.kv(s)['spend']) for s in lines if s.startswith('player ') and 'spend' in B.kv(s)}
    return st, planets, worms, hw, extra, spend


def build(ev, out):
    os.makedirs(out, exist_ok=True)
    games = sorted(d for d in os.listdir(ev) if re.fullmatch(r'ug\d\d', d))
    for g in games:
        dirs = [g] + sorted(d for d in os.listdir(ev) if d.startswith(g + '-c'))
        raw = os.path.join(ev, g, 'raw')
        defn = next(f for f in os.listdir(raw) if f.lower().endswith('.def'))
        settings, players = definition(os.path.join(raw, defn))
        name = open(os.path.join(raw, defn), encoding='latin-1').readline().strip()
        settings = dict(name=name, **settings)
        rid = 'UG' + g[2:]
        per = {k: {} for k in 'ABCDE'}
        races, held = None, True
        for d in dirs:
            r = os.path.join(ev, d, 'raw')
            hst = os.path.join(r, next(f for f in os.listdir(r) if f.upper().endswith('.HST')))
            xy = os.path.join(r, next(f for f in os.listdir(r) if f.upper().endswith('.XY')))
            st, planets, worms, hw, extra, spend = observe(hst, xy)
            if races is None:
                races = [dict(p, race=pl['race'], leftover_spend_code=spend.get(pl['id']))
                         for p, pl in zip(players, st['players'])]
                stored = B.game_settings(xy)
                # the .def's victory lines are the input; the game record keeps no value for a disabled
                # condition, so the stored conditions are an observation (case E), not a setting
                settings.update({k: v for k, v in stored.items() if k != 'victory_conditions'})
            held = held and ' 0 mismatch' in open(os.path.join(ev, d, 'check.txt')).read()
            stream = 'cycles ' + (d.split('-c')[1] if '-c' in d else '20000')
            per['A'][stream] = [{'year': 0, 'kind': 'player', 'id': p['id'], 'equals': {
                'tech': p['tech'], 'ship_design_count': p['counts']['ship_designs']}} for p in st['players']]
            per['B'][stream] = [{'year': 0, 'kind': 'sample', 'check': 'planet_count', 'target': [],
                                 'observed': planets, 'constraint': 'PARITY.md "Planet counts": W²/5000 for normal '
                                 'density, sparse 3/4, dense 5/4, packed 15/8; seed-dependent near 999 candidates'}]
            per['C'][stream] = [{'year': 0, 'kind': 'sample', 'check': 'starting_planets', 'target': [],
                                 'observed': {str(p): {'homeworld': hw.get(p), 'other_planets': extra.get(p, []),
                                                       'fleets': len([f for f in st['fleets'] if f['owner'] == p])}
                                              for p in sorted(hw)},
                                 'constraint': 'installations, population, second planet and leftover spends as in '
                                 'PARITY.md "Starting planets"; every homeworld shares one surface draw and planet '
                                 '0\'s concentrations raised to 30 ("Shared homeworld minerals", LEGACY BUG)'}]
            per['E'][stream] = [{'year': 0, 'kind': 'sample', 'check': 'stored_victory_conditions', 'target': [],
                                 'observed': B.game_settings(xy)['victory_conditions'],
                                 'constraint': 'a disabled condition\'s value is stored as 0, which decodes as that condition\'s '
                                 'lowest value (tech level 8, score 1000, ...); enabled conditions keep the .def value'}]
            per['D'][stream] = [{'year': 0, 'kind': 'sample', 'check': 'wormholes', 'target': [],
                                 'observed': worms, 'constraint': 'none with no random events'}]
        vec = {'schema': B.SCHEMA, 'id': rid, 'title': '%s %s, %d players' % (settings['size'], settings['density'],
                                                                             len(players)),
               'source': {'experiment': 'experiments/ug', 'spec_rules': 'docs/UNIVERSE.md',
                          'parity': 'docs/PARITY.md "Universe generation"',
                          'raw_evidence': 'stars-oracle-apparatus evidence/ug/run/%s (private)' % ', '.join(dirs)},
               'years': 0, 'random': 'single_stream' if len(dirs) == 1 else 'several_streams',
               'streams': len(dirs), 'new_game': {'settings': settings, 'races': races}, 'cases': []}
        for k, rule, setup in [('A', 'UNIVERSE Starting tech by PRT; starting designs', 'starting tech and design count per player'),
                               ('B', 'UNIVERSE Planet counts', 'number of planets'),
                               ('C', 'UNIVERSE Starting planets; shared homeworld minerals', 'homeworlds and other starting planets per player'),
                               ('D', 'UNIVERSE Options: no random events', 'wormholes in the new game'),
                               ('E', 'KERNEL Victory conditions', 'victory conditions as stored in the new game')]:
            vec['cases'].append(B.case('%s-%s' % (rid, k), rule, setup, per[k], held, set()))
        with open(os.path.join(out, g + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        print('%s: %d players, %d streams' % (rid, len(players), len(dirs)))
