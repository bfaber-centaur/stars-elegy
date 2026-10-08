"""RD/RW race-design new games -> new-game vectors. Called by build.py for
CORPUS rw with the apparatus evidence/rd directory.

The games rw01..rw06, rd07 and rw08 test what game creation does with the
race files it is given (PARITY.md "Race design"). Unlike the UG games, the
input is the race *file*: `new_game.races` holds each human player's race
as decoded from the .r1 file the game was built from (`tools/fleetlab/racelab
dump`), with `random: true` for a wizard Random race (experiments/rd/races.tsv,
and every human race of RD-5 and RD-6).
Case R is each human player's race as the new host file records it: exact,
except a Random race, which the generator draws (a sample). Cases A..E are
the UG cases (build_ug): starting tech and design count, planet count,
starting planets (where the leftover points show), wormholes and stored
victory conditions. One generation each, so every case is MEASURED.
"""
import os, re, subprocess
import build as B
import build_ug as U

GAMES = [
    # dir, vector id, PARITY section
    ('rw01', 'RD-1', 'Advantage points and leftover (MEASURED, RD-1..RD-4)'),
    ('rw02', 'RD-2', 'Advantage points and leftover (MEASURED, RD-1..RD-4)'),
    ('rw03', 'RD-3', 'Advantage points and leftover (MEASURED, RD-1..RD-4)'),
    ('rw04', 'RD-4', 'Illegal, malformed and Random races at game creation (MEASURED, RD-4..RD-6)'),
    ('rw05', 'RD-5', 'Illegal, malformed and Random races at game creation (MEASURED, RD-4..RD-6)'),
    ('rw06', 'RD-6', 'Illegal, malformed and Random races at game creation (MEASURED, RD-4..RD-6)'),
    ('rd07', 'RD-7', 'Follow-up: AR spends, growth 0, several players (MEASURED, RD-7, RD-P11, RD-P12)'),
    ('rw08', 'RW08', 'Round 3: the remaining BINARY-ONLY rules (MEASURED, RW08, RD-P13..RD-P21)'),
]
NOTE = {'rw04': 'three corpus files had bad footer checksums and the game refused them; the run used them with '
                'only the checksum rewritten (PARITY "Illegal, malformed and Random races"), and those are the inputs here'}
# experiments/rd/README.md: every human race in RD-5 and RD-6 is a wizard Random race
RANDOM_GAMES = {'rw05', 'rw06'}
RACELAB = os.path.join(B.ROOT, 'tools', 'fleetlab', 'racelab')
SPENDS = ['surface_minerals', 'mineral_concentrations', 'mines', 'factories', 'defenses']


def random_files():
    out = set()
    for line in open(os.path.join(B.ROOT, 'experiments', 'rd', 'races.tsv')):
        f = line.rstrip('\n').split('\t')
        if len(f) > 3 and f[3].startswith('random race'):
            out.add(f[0] + '.r1')
    return out


def race_file(path):
    """The race in a .r1 file, in the form of initial_state players' `race`."""
    line = subprocess.run([RACELAB, 'dump', path], check=True, capture_output=True, text=True).stdout.strip()
    d = dict(kv.split('=', 1) for kv in line.split()[1:] if '=' in kv)
    c, lo, hi = ([int(x) for x in part.split(',')] for part in d['hab'].split('/'))
    st = [int(x) for x in d['stats'].split(',')]
    traits = int(d['traits'], 16)
    prt = d['prt']
    return {
        'prt': prt if prt in B.PRT else int(prt), 'lrt': [B.LRT[b] for b in B.mask_players(int(d['lrt'], 16), 14)],
        'growth_percent': int(d['growth']),
        'habitability': {'gravity': [c[0], lo[0], hi[0]], 'temperature': [c[1], lo[1], hi[1]],
                         'radiation': [c[2], lo[2], hi[2]], 'order': 'center, low, high (255 = immune)'},
        'colonists_per_resource': 100 * st[0],
        'factory': {'output': st[1], 'cost': st[2], 'per_10k': st[3]},
        'mine': {'output': st[4], 'cost': st[5], 'per_10k': st[6]},
        'research_cost': dict(zip(B.TECH, (B.RCOST.get(x, x) for x in st[8:14]))),
        'leftover_spend': SPENDS[st[7]] if 0 <= st[7] < 5 else st[7],
        'stat_15': st[15],
        'techs_start_high': bool(traits >> 13 & 1),
        'factories_cost_less': bool(traits >> 15 & 1),
    }


def build(ev, out):
    os.makedirs(out, exist_ok=True)
    rnd = random_files()
    for g, vid, section in GAMES:
        is_random = lambda f: f in rnd or g in RANDOM_GAMES
        raw = os.path.join(ev, g, 'raw')
        if not os.path.isdir(raw):
            continue
        files = {f.lower(): os.path.join(raw, f) for f in os.listdir(raw)}
        defn = next(f for f in files if f.endswith('.def'))
        settings, players = U.definition(files[defn])
        name = open(files[defn], encoding='latin-1').readline().strip()
        settings = dict(name=name, **settings)
        hst = next(p for f, p in files.items() if f.endswith('.hst'))
        xy = next(p for f, p in files.items() if f.endswith('.xy'))
        st, planets, worms, hw, extra, spend = U.observe(hst, xy)
        settings.update({k: v for k, v in B.game_settings(xy).items() if k != 'victory_conditions'})
        races, rexp = [], []
        for p, pl in zip(players, st['players']):
            if 'race_file' in p:
                r = dict(p, race=race_file(files[p['race_file']]))
                if is_random(p['race_file']):
                    r['random'] = True
                races.append(r)
                e = {'year': 0, 'kind': 'player', 'id': pl['id'], 'equals': {'race': pl['race']}}
                if is_random(p['race_file']):
                    e['sample'] = True
                rexp.append(e)
            else:
                races.append(dict(p, race=pl['race']))
        held = ' 0 mismatch' in open(os.path.join(ev, g, 'check.txt')).read()
        stream = 'cycles 20000'
        per = {
            'R': rexp,
            'A': [{'year': 0, 'kind': 'player', 'id': p['id'], 'equals': {
                'tech': p['tech'], 'ship_design_count': p['counts']['ship_designs']}} for p in st['players']],
            'B': [{'year': 0, 'kind': 'sample', 'check': 'planet_count', 'target': [], 'observed': planets,
                   'constraint': 'PARITY.md "Planet counts"'}],
            'C': [{'year': 0, 'kind': 'sample', 'check': 'starting_planets', 'target': [],
                   'observed': {str(p): {'homeworld': hw.get(p), 'other_planets': extra.get(p, []),
                                         'fleets': len([f for f in st['fleets'] if f['owner'] == p]),
                                         'leftover_spend_code': spend.get(p)} for p in sorted(hw)},
                   'constraint': 'PARITY.md "Race design": leftover L = points (at most 50) spent as the race says; '
                   'every homeworld shares one surface draw ("Shared homeworld minerals")'}],
            'D': [{'year': 0, 'kind': 'sample', 'check': 'wormholes', 'target': [], 'observed': worms,
                   'constraint': 'OBJECTS.md "Creation"'}],
            'E': [{'year': 0, 'kind': 'sample', 'check': 'stored_victory_conditions', 'target': [],
                   'observed': B.game_settings(xy)['victory_conditions'],
                   'constraint': 'a disabled condition is stored as 0'}],
        }
        vec = {'schema': B.SCHEMA, 'id': vid, 'title': 'race design: %s, %d players' % (name, len(players)),
               'source': {'experiment': 'experiments/rd', 'spec_rules': 'docs/RACES.md, docs/UNIVERSE.md',
                          'parity': 'docs/PARITY.md "%s"' % section,
                          'raw_evidence': 'stars-oracle-apparatus evidence/rd/%s (private)' % g},
               'years': 0, 'random': 'single_stream', 'streams': 1,
               'new_game': {'settings': settings, 'races': races}, 'cases': []}
        for k, rule, setup in [('R', 'RACES race files at game creation', "each human player's race as created"),
                               ('A', 'UNIVERSE Starting tech by PRT; starting designs', 'starting tech and design count per player'),
                               ('B', 'UNIVERSE Planet counts', 'number of planets'),
                               ('C', 'UNIVERSE Starting planets; leftover points', 'homeworlds and other starting planets per player'),
                               ('D', 'OBJECTS Wormholes: Creation', 'wormholes in the new game'),
                               ('E', 'KERNEL Victory conditions', 'victory conditions as stored in the new game')]:
            if not per[k]:
                continue
            cs = B.case('%s-%s' % (vid, k), rule, setup, {stream: per[k]}, held, set())
            cs['tag'] = 'MEASURED'
            cs['verdict'] = ('the private comparison with the predicted game found 0 mismatches' if held else
                             'the private comparison with the predicted game found mismatches') + \
                ('; ' + NOTE[g] if g in NOTE else '')
            vec['cases'].append(cs)
        with open(os.path.join(out, g + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        print('%s: %d players, %d random races' % (vid, len(players), sum(1 for r in races if r.get('random'))))
