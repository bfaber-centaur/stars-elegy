#!/usr/bin/env python3
"""Build public parity vectors (vectors/<corpus>/<run>.json) from an oracle corpus.

  python3 tools/vectors/build.py CORPUS EVIDENCE_DIR [OUT_DIR]
      CORPUS: fm2 | fo | tk2 | wt      (vectors/README.md lists the format)
      EVIDENCE_DIR: the corpus's raw-evidence directory (private apparatus
      repository, e.g. stars-oracle-apparatus/evidence/fm2)

Each vector holds one oracle run: the complete initial state read from the
run's start host file (`combatlab dump`, behavior values only), the number
of years generated, and one entry per case with the outcome the original
game produced. Outcomes come from the corpus checker's recorded output
(check.out), so a case whose prediction missed still carries the observed
value. No file bytes, serials or screenshots are copied: the builder writes
only the decoded quantities listed in vectors/README.md.
"""
import ast, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMBATLAB = os.path.join(ROOT, 'tools', 'fleetlab', 'combatlab')
SCHEMA = 'stars-elegy-vector/1'
TECH = ['energy', 'weapons', 'propulsion', 'construction', 'electronics', 'biotechnology']
DUMP_TECH = ['energy', 'weapons', 'prop', 'con', 'elec', 'bio']
PRT = ['HE', 'SS', 'WM', 'CA', 'IS', 'SD', 'PP', 'IT', 'AR', 'JOAT']
LRT = ['IFE', 'TT', 'ARM', 'ISB', 'GR', 'UR', 'MA', 'NRSE', 'CE', 'OBRM', 'NAS', 'LSP', 'BET', 'RS']
RELATION = {0: 'neutral', 1: 'friend', 2: 'enemy'}
RCOST = {0: 'expensive', 1: 'normal', 2: 'cheap'}
TASKS = {0: 'none', 1: 'transport', 2: 'colonize', 3: 'remote_mine', 4: 'merge', 5: 'scrap',
         6: 'lay_mines', 7: 'patrol', 8: 'route', 9: 'transfer'}
ACTIONS = {0: 'none', 1: 'load_all', 2: 'unload_all', 3: 'load_exactly', 4: 'unload_exactly',
           5: 'fill_to_percent', 6: 'wait_for_percent', 7: 'load_optimal', 8: 'set_amount_to',
           9: 'set_waypoint_to'}
CARGO = ['ironium', 'boranium', 'germanium', 'colonists', 'fuel']
MT_ITEMS = ['Multi Cargo Pod', 'Multi Function Pod', 'Langston Shell', 'Mega Poly Shell', 'Alien Miner',
            'Hush-a-Boom', 'Anti Matter Torpedo', 'Multi Contained Munition', 'Mini Morph', 'Enigma Pulsar',
            'Genesis Device', 'Jump Gate', 'ship']
GAMES = {
    'CB': dict(name='Combat Lab', size='tiny', bounds=[1000, 1000, 1400, 1400], density='sparse'),
    'CB3P': dict(name='CB3P', size='tiny', bounds=[1000, 1000, 1400, 1400]),
    'CB5P': dict(name='CB5P', size='tiny', bounds=[1000, 1000, 1400, 1400]),
    'CB16P': dict(name='CB16P', size='tiny', bounds=[1000, 1000, 1400, 1400]),
    'PG001': dict(name='PG001', size='tiny'),
    'RD07': dict(name='RD07'),
    'GT': dict(name='GT', size='medium'),
    'TK3': dict(name='TK3', size='tiny', bounds=[1000, 1000, 1400, 1400]),
}


# ------------------------------------------------------------------ dumps

def dump(path):
    out = subprocess.run([COMBATLAB, 'dump', path], capture_output=True, text=True, check=True).stdout
    return [line.split(' ', 1)[1] for line in out.splitlines() if ' ' in line]


def last_section(lines):
    """A player's .M holds one section per year since the player last
    submitted; the generated year is the last one."""
    starts = [i for i, s in enumerate(lines) if s.startswith('file ')]
    return lines[starts[-1]:] if starts else lines


def kv(s):
    return dict(m.groups() for m in re.finditer(r'(\w+)=(\S+)', s))


def mask_players(m, n=16):
    return [p for p in range(n) if m >> p & 1]


def slots(desc):
    """'Scout, 1 Long Hump 6, empty' -> hull, [{'count':1,'part':'Long Hump 6'}, None]"""
    parts = [x.strip() for x in desc.split(',')]
    out = []
    for p in parts[1:]:
        if p == 'empty':
            out.append(None)
        else:
            c, name = p.split(' ', 1)
            out.append({'count': int(c), 'part': name})
    return parts[0], out


def waypoint(d, owner, nplayers):
    t = int(d['type'], 16) & 0xf
    obj = int(d['obj'])
    wp = {'x': int(d['x']), 'y': int(d['y']), 'warp': int(d['warp'])}
    if t == 1:
        wp['target'] = {'kind': 'planet', 'id': obj}
    elif t == 2:
        wp['target'] = {'kind': 'fleet', 'owner': obj >> 9, 'id': obj & 0x1ff}
    elif t == 8:
        wp['target'] = {'kind': {2: 'wormhole', 3: 'trader'}.get(obj >> 13, 'object'), 'id': obj & 0x1ff}
    else:
        wp['target'] = {'kind': 'space'}
    task = int(d['task'])
    words = [int(w, 16) for w in d.get('orders', '').split(',') if w]
    tk = {'kind': TASKS.get(task, str(task))}
    if task == 1:
        tk['orders'] = {}
        for k, w in enumerate(words[:5]):
            if w:
                tk['orders'][CARGO[k]] = {'action': ACTIONS[w >> 12], 'value': w & 0xfff}
    elif task == 6 and words:
        tk['years'] = 'indefinitely' if words[0] == 5 else words[0]
    elif task == 9 and words:
        tk['to_player'] = [p for p in range(nplayers) if p != owner][words[0]]
    elif task == 7 and words:
        if words[0] >> 15:
            raise ValueError('patrol order word with bit 15 set: not decoded')
        tk['range'] = words[0]
    wp['task'] = tk
    return wp


HSTEDIT = os.path.join(ROOT, 'scripts', 'oracle', 'hst-edit')
VICTORY = [('planets_owned_percent', lambda v: (v + 4) * 5), ('tech_level', lambda v: v + 8),
           ('tech_fields', lambda v: v + 2), ('score', lambda v: (v + 1) * 1000),
           ('lead_over_second_percent', lambda v: (v + 2) * 10), ('resources_thousands', lambda v: (v + 1) * 10),
           ('capital_ships', lambda v: (v + 1) * 10), ('highest_score_after_years', lambda v: (v + 3) * 10),
           ('conditions_needed', lambda v: v), ('minimum_years', lambda v: (v + 3) * 10)]
TOGGLED = {'planets_owned_percent', 'tech_level', 'score', 'lead_over_second_percent', 'resources_thousands',
           'capital_ships', 'highest_score_after_years'}


def game_settings(xy_path):
    """Options and victory conditions from the .XY game record (ORACLE.md, hst-edit xy)."""
    out = subprocess.run([HSTEDIT, 'dump', xy_path], capture_output=True, text=True, check=True).stdout
    g = bytes.fromhex(re.search(r' game ([0-9a-f]+)', out).group(1))
    o = g[0x10]
    vc = {}
    for i, (name, f) in enumerate(VICTORY):
        b = g[0x14 + i]
        vc[name] = {'value': f(b & 0x7f)}
        if name in TOGGLED:
            vc[name]['enabled'] = bool(b & 0x80)
    return {'slower_tech': bool(o & 2), 'random_events': not o & 0x80, 'public_scores': bool(o & 0x40),
            'victory_conditions': vc}


def queue_item(i):
    it = {'id': int(i[0]), 'count': int(i[1])}
    if int(i[2]):
        it['percent'] = int(i[2])
    it['kind'] = int(i[3])
    return it


def state(hst, xy, game, xy_path=None):
    """Initial state from a host-file dump and the .XY dump."""
    st = dict(year=None, game=dict(GAMES.get(game, {'name': game})), players=[], planets=[], designs=[], starbase_designs=[],
              battle_plans=[], fleets=[], objects=[], production_queues=[])
    pos = {}
    for s in xy:
        if s.startswith('xy planet'):
            d = kv(s)
            pos[int(s.split()[2])] = (int(d['x']), int(d['y']))
    planets, sb = {}, {}
    owners, idx = [], {'ship': 0, 'sb': 0}
    fleet = None
    for s in hst:
        d = kv(s)
        if s.startswith('file '):
            st['year'] = int(d['year'])
        elif s.startswith('player ') and 'energy' in d:
            p = int(s.split()[1])
            rel = [int(x) for x in re.search(r'relations=\[([^\]]*)\]', s).group(1).split(',') if x.strip()]
            econ = [int(x) for x in d['econ'].split(',')]
            lrt = int(d['lrt'], 16)
            hab = [int(x) for x in d['hab'].split(',')]
            st['players'].append({
                'id': p,
                'tech': {TECH[i]: int(d[DUMP_TECH[i]]) for i in range(6)},
                'research_accumulated': dict(zip(TECH, (int(x) for x in d['accum'].split(',')))),
                'research_percent': int(d['researchPct']), 'research_field': TECH[int(d['field'])],
                'relations': {str(q): RELATION[r] for q, r in enumerate(rel) if q != p},
                'mystery_trader_items': [MT_ITEMS[b] for b in mask_players(int(d['mt'], 16), 13)],
                'race': {
                    'prt': PRT[int(d['prt'])] if int(d['prt']) < len(PRT) else int(d['prt']), 'lrt': [LRT[b] for b in mask_players(lrt, 14)],
                    'growth_percent': int(d['growth']),
                    'habitability': {'gravity': hab[0::3], 'temperature': hab[1::3], 'radiation': hab[2::3],
                                     'order': 'center, low, high (255 = immune)'},
                    'colonists_per_resource': 100 * econ[0],
                    'factory': {'output': econ[1], 'cost': econ[2], 'per_10k': econ[3]},
                    'mine': {'output': econ[4], 'cost': econ[5], 'per_10k': econ[6]},
                    'research_cost': dict(zip(TECH, (RCOST[int(x)] for x in d['rcost'].split(',')))),
                    'leftover_spend': ['surface_minerals', 'mineral_concentrations', 'mines', 'factories',
                                       'defenses'][int(d['spend'])] if 0 <= int(d['spend']) < 5 else int(d['spend']),
                    'stat_15': int(d.get('stat15', 0)),
                    'techs_start_high': bool(int(d['traits'], 16) >> 13 & 1),
                    'factories_cost_less': bool(int(d['traits'], 16) >> 15 & 1),
                },
                'counts': {'ship_designs': int(d['shipdesigns']), 'starbase_designs': int(d['sbdesigns'])},
            })
            owners.append(p)
        elif s.startswith('design ') or s.startswith('sbdesign '):
            m = re.match(r'(sb)?design owner=(\d+) n=(\d+) mass=(\d+) armor=(-?\d+) full=\w+ :: (.*)', s)
            hull, sl = slots(m.group(6))
            (st['starbase_designs'] if m.group(1) else st['designs']).append(
                {'owner': int(m.group(2)), 'slot': int(m.group(3)), 'hull': hull, 'slots': sl,
                 'mass': int(m.group(4))})
        elif s.startswith('plan '):
            st['battle_plans'].append({'owner': int(d['owner']), 'slot': int(d['k']), 'tactic': int(d['tactic']),
                                       'primary': int(d['primary']), 'secondary': int(d['secondary']),
                                       'attack_who': int(d['who']), 'dump_cargo': d['dump'] == 'true',
                                       'name': s.split('name=', 1)[1]})
        elif s.startswith('planet ') and d.get('owner') != '-1':  # an unowned planet has no starbase
            n = int(s.split()[1])
            sb[n] = dict(design=int(d['design']) if d.get('starbase') == 'true' else None,
                         damage=int(d.get('sbdmg', 0)))
        elif s.startswith('pdetail '):
            n = int(s.split()[1])
            p = {'id': n, 'x': pos[n][0], 'y': pos[n][1], 'owner': int(d['owner'])}
            p['concentrations'] = [int(x) for x in d['conc'].split('/')]
            p['environment'] = [int(x) for x in d['env'].split('/')]
            if 'orig' in d:
                p['original_environment'] = [int(x) for x in d['orig'].split('/')]
            if 'surface' in d:
                p['surface_minerals'] = [int(x) for x in d['surface'].split('/')]
                for k, name in (('pop', 'population'), ('excess', 'excess'), ('mines', 'mines'),
                                ('factories', 'factories'), ('defenses', 'defenses')):
                    if k in d:
                        p[name] = int(d[k])
                if 'scanner' in d:
                    p['planetary_scanner'] = None if int(d['scanner']) == 31 else int(d['scanner'])
                if 'leftover' in d:
                    p['leftover_to_research'] = d['leftover'] == 'true'
                if 'route' in d and int(d['route'], 16) & 0x3ff:
                    p['route_to'] = (int(d['route'], 16) & 0x3ff) - 1
            planets[n] = p
        elif s.startswith('queue '):
            items = [it.split(':') for it in d.get('items', '').split(',') if it]
            st['production_queues'].append({'planet': int(d['planet']), 'items': [queue_item(i) for i in items]})
        elif s.startswith('fleet '):
            ships = [{'design': int(a), 'count': int(b)} for a, b in
                     (x.split(':') for x in d['ships'].split(',') if x)]
            dmg = {int(k[3:]): v for k, v in d.items() if k.startswith('dmg') and k[3:].isdigit()}
            for sh in ships:
                if sh['design'] in dmg:
                    u, pc = dmg[sh['design']].rstrip('%').split('/')
                    sh['damage'] = {'units': int(u), 'percent_of_ships': int(pc)}
            c = [int(x) for x in d['cargo'].split('/')]
            fleet = {'owner': int(d['owner']), 'id': int(d['id']), 'x': int(d['x']), 'y': int(d['y']),
                     'orbiting': None if int(d['obj']) == 65535 else int(d['obj']), 'ships': ships,
                     'cargo': dict(zip(CARGO[:4], c)), 'fuel': int(d['fuel']), 'battle_plan': int(d['plan']),
                     'waypoints': []}
            if int(d['b5'], 16) & 2:
                fleet['repeat_orders'] = True
            st['fleets'].append(fleet)
        elif s.startswith('  wp ') and fleet is not None:
            fleet['waypoints'].append(waypoint(d, fleet['owner'], len(owners)))
        elif s.startswith('thing ') and 'type' in d:
            st['objects'].append(thing(d))
        if not s.startswith('  wp ') and not s.startswith('fleet '):
            fleet = None
    for n, p in planets.items():
        if n in sb:
            p['starbase'] = sb[n]
    st['planets'] = [planets[n] for n in sorted(planets)]
    st['game']['players'] = len(st['players'])
    if xy_path:
        st['game'].pop('random_events', None)
        st['game'].update(game_settings(xy_path))
    return st


def thing(d):
    t, n, x, y = d['type'], int(d['num']), int(d['x']), int(d['y'])
    if t == 'wormhole':
        return {'kind': 'wormhole', 'id': n, 'x': x, 'y': y, 'partner': int(d['partner']),
                'stability_class': int(d['class']), 'years_since_jump': int(d['years']),
                'known_to': mask_players(int(d['seen'], 16)), 'destination_known_to': mask_players(int(d['seen2'], 16))}
    if t == 'trader':
        dx, dy = d['dest'].split(',')
        item = int(d['item'], 16)
        return {'kind': 'trader', 'id': n, 'x': x, 'y': y, 'destination': [int(dx), int(dy)], 'warp': int(d['warp']),
                'met': mask_players(int(d['met'], 16)),
                'offer': 'research' if item == 0 else ', '.join(MT_ITEMS[b] for b in mask_players(item, 13))}
    if t == 'packet':
        c = [int(v) for v in d['cargo'].split('/')]
        return {'kind': 'packet', 'owner': int(d['owner']), 'id': n, 'x': x, 'y': y, 'destination_planet': int(d['dest']),
                'warp': int(d['warp']), 'minerals': c, 'decay_class': int(d['class'])}
    if t == 'minefield':
        m = {'kind': 'minefield', 'owner': int(d['owner']), 'id': n, 'x': x, 'y': y, 'mines': int(d['count']),
             'type': ['standard', 'heavy', 'speed_bump'][int(d['kind'])], 'detonating': d['det'] == '1'}
        if 'known' in d:
            m['known_to'] = mask_players(int(d['known'], 16))
        return m
    raise ValueError(t)


# ------------------------------------------------------------------ expectations

FLEET_KEYS = {'fe': 'ironium', 'bo': 'boranium', 'ge': 'germanium', 'col': 'colonists'}
PLANET_KEYS = {'surface': 'surface_minerals', 'pop': 'population', 'env': 'environment',
               'orig': 'original_environment', 'owner': 'owner', 'mines': 'mines', 'factories': 'factories',
               'defenses': 'defenses', 'excess': 'excess', 'leftover': 'leftover_to_research'}


def norm_fleet(got):
    out = {}
    for k, v in got.items():
        if k in FLEET_KEYS:
            out.setdefault('cargo', {})[FLEET_KEYS[k]] = v
        elif k == 'ships':
            out['ships'] = [{'design': int(a), 'count': int(b)} for a, b in (x.split(':') for x in v.split(',') if x)]
        elif k == 'dmg':
            out['damage'] = [{'design': int(dd), 'units': u, 'percent_of_ships': p} for dd, (u, p) in sorted(v.items())]
        elif k == 'task':
            out['first_waypoint_task'] = TASKS.get(v, v)
        elif k == 'warp':
            out['next_waypoint_warp'] = v
        elif k in ('x', 'y', 'fuel'):
            out[k] = v
    return out


def norm_planet(got):
    out = {}
    for k, v in got.items():
        out[PLANET_KEYS.get(k, k)] = list(v) if isinstance(v, tuple) else v
    return out


def expectation(kind, args, year, res, want, got):
    """One recorded check -> one public expectation of what the original did."""
    e = {'year': year}
    if kind == 'fleet':
        if got == 'gone':
            e.update(kind='fleet_gone', owner=args[0], id=args[1])
        else:
            e.update(kind='fleet', owner=args[0], id=args[1], equals=norm_fleet(got))
    elif kind == 'nofleet':
        if res == 'OK':
            e.update(kind='fleet_gone', owner=args[0], id=args[1])
        else:
            e.update(kind='fleet', owner=args[0], id=args[1], equals=norm_fleet(got))
    elif kind == 'fleetat':
        e.update(kind='fleet_at', owner=args[0], x=args[1], y=args[2], equals=norm_fleet(got))
    elif kind == 'nofleetat':
        e.update(kind='no_fleet_at', owner=args[0], x=args[1], y=args[2])
        if res != 'OK':
            e['observed'] = 'a fleet was there'
    elif kind == 'planet':
        e.update(kind='planet', id=args[0], equals=norm_planet(got))
    elif kind == 'starbase':
        e.update(kind='planet', id=args[0], equals={'starbase_design': got})
    elif kind == 'queue':
        e.update(kind='production_queue', planet=args[0], equals=[{'id': i, 'count': c} for i, c in got])
    elif kind == 'design':
        hull, sl = slots(got)
        e.update(kind='design', owner=args[0], slot=args[1], equals={'hull': hull, 'slots': sl})
    elif kind == 'tech' and isinstance(got, dict):
        t = {TECH[DUMP_TECH.index(k)] if k in DUMP_TECH else k: v for k, v in got.items()}
        if isinstance(want, dict):
            e.update(kind='player', id=args[0], equals={'tech': t})
        else:
            e.update(kind='sample', check='tech', target=args, observed={'tech': t}, constraint=want)
    elif kind == 'salvage':
        e.update(kind='salvage_at', x=args[0], y=args[1])
        if got:
            e['equals'] = {'minerals': [int(x) for x in kv(got)['cargo'].split('/')]}
        else:
            e['observed'] = 'none'
    else:
        e.update(kind='sample', check=kind, target=args, observed=got, constraint=want)
    return e


def merge_streams(per):
    """{stream: [expectation]} -> one list. An expectation found unchanged in
    every stream is listed once; the rest are listed per stream (`stream`)."""
    streams = sorted(per)
    if len(streams) == 1:
        return per[streams[0]], False
    key = lambda e: json.dumps(e, sort_keys=True)
    common = set(map(key, per[streams[0]]))
    for st in streams[1:]:
        common &= set(map(key, per[st]))
    out, seen = [], set()
    for e in per[streams[0]]:
        if key(e) in common and key(e) not in seen:
            seen.add(key(e))
            out.append(e)
    varies = False
    for st in streams:
        for e in per[st]:
            if key(e) not in common:
                varies = True
                out.append(dict(e, stream=st))
    return out, varies


def case(case_id, rule, text, per, held, legacy):
    exps, varies = merge_streams(per)
    sampled = varies or any(e['kind'] == 'sample' for e in exps)
    tag = 'LEGACY BUG' if case_id in legacy else ('MEASURED' if sampled or not held else 'CONFIRMED')
    return {'id': case_id, 'rule': rule, 'setup': text, 'tag': tag, 'prediction_held': held,
            'varies_by_stream': varies, 'expect': exps}


# ------------------------------------------------------------------ corpora

def load_gen(path, mod):
    sys.path.insert(0, os.path.join(ROOT, path))
    for m in ('gen', 'gen2', 'model', 'check', 'check2', 'trace', 'wt'):
        sys.modules.pop(m, None)
    return __import__(mod)


def lit(s):
    if s in (None, 'None'):
        return None
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return s


def read_checks(path, with_rundir):
    """check.out lines -> {(run, rundir): [(cid, kind, args, year, res, want, got)]}"""
    pat = re.compile(r'^(\S+) (\S+) (\w+) (\(.*?\))(?: y(\d+))?: (OK|MISS|NODATA)(?: want=(.*?) got=(.*))?$')
    out = {}
    for line in open(path):
        line = line.rstrip('\n')
        if with_rundir:
            m = re.match(r'^(\S+)/(\S+) (.*)$', line)
            if not m:
                continue
            run, rd, rest = m.group(1), m.group(2), m.group(3)
            line = run + ' ' + rest
        else:
            rd = 'run'
        m = pat.match(line)
        if not m:
            continue
        run, cid, kind, args, y, res, want, got = m.groups()
        out.setdefault((run, rd), []).append((cid, kind, ast.literal_eval(args), int(y or 1), res, lit(want), lit(got)))
    return out


CORPORA = {
    'fm2': dict(path='experiments/fm2', mod='gen', check='check.out', rundir=False, prefix='FM',
                doc='docs/KERNEL.md "Fleet movement"', parity='docs/PARITY.md "Fleet Movement" > "Round 2"',
                legacy={'FM-102-F', 'FM-105-A', 'FM-105-B', 'FM-105-C'}),
    'fo': dict(path='experiments/fo', mod='gen', check='check.out', rundir=False, prefix='FO',
               doc='docs/ORDERS.md "Fleet operations"', parity='docs/PARITY.md "Fleet Operations"',
               legacy={'FO-03-E'}),
    'tk2': dict(path='experiments/tk', mod='gen2', check='check2.out', rundir=True, prefix='TK',
                doc='docs/TAKEOVER.md', parity='docs/PARITY.md "Planet takeover" > "Round 2 (TK-101 to TK-121)"',
                legacy=set()),
}


def run_id(prefix, name):
    return '%s-%s' % (prefix, re.sub(r'^\D+', '', name))


def build(corpus, ev, out):
    c = CORPORA[corpus]
    gen = load_gen(c['path'], c['mod'])
    checks = read_checks(os.path.join(ev, c['check']), c['rundir'])
    os.makedirs(out, exist_ok=True)
    n = 0
    for r in gen.runs():
        rdirs = sorted(rd for (run, rd) in checks if run == r.name)
        if not rdirs:
            print('%s: no recorded checks, skipped' % r.name)
            continue
        base = os.path.join(ev, r.name, rdirs[0], 'raw', 'before')
        game = getattr(r, 'game', 'CB')
        st = state(dump(os.path.join(base, game + '.HST')), dump(os.path.join(base, game + '.XY')), game,
                   os.path.join(base, game + '.XY'))
        rid = run_id(c['prefix'], r.name)
        vec = {'schema': SCHEMA, 'id': rid, 'title': getattr(r, 'title', ''),
               'source': {'experiment': c['path'], 'spec_rules': c['doc'], 'parity': c['parity'],
                          'raw_evidence': 'stars-oracle-apparatus evidence/%s/%s (private)' % (os.path.basename(ev.rstrip('/')), r.name)},
               'years': r.years,
               'random': 'single_stream' if len(rdirs) == 1 else 'several_streams',
               'streams': len(rdirs),
               'initial_state': st, 'cases': []}
        for cid, rule, text in r.cases:
            per, held = {}, True
            for rd in rdirs:
                for (ccid, kind, args, year, res, want, got) in checks[(r.name, rd)]:
                    if ccid == cid:
                        per.setdefault(rd.replace('run-', 'cycles '), []).append(expectation(kind, args, year, res, want, got))
                        held = held and res == 'OK'
            if per:
                vec['cases'].append(case('%s-%s' % (rid, cid), rule, text, per, held, c['legacy']))
        with open(os.path.join(out, r.name + '.json'), 'w') as f:
            json.dump(vec, f, indent=1)
            f.write('\n')
        n += 1
    print('%s: %d vectors in %s' % (corpus, n, out))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    corpus, ev = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, 'vectors', corpus)
    if corpus in ('cb7', 'tk3', 'sl', 'gt'):
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        __import__('build_obs').build(corpus, ev, out)
    elif corpus in ('kx001', 'kx002', 'kx003', 'kx004'):
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        kx = __import__('build_kx')
        kx.build(corpus, ev, out) if corpus in ('kx001', 'kx002') else getattr(kx, 'build_' + corpus)(ev, out)
    elif corpus in ('cb', 'sc', 'mf', 'rp'):
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        __import__('build_' + corpus).build(ev, out)
    elif corpus in ('xf', 'bp', 'tk5', 'wu'):
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        __import__('build_orders').build(corpus, ev, out)
    elif corpus == 'wt':
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import build_wt
        build_wt.build(ev, out)
    else:
        build(corpus, ev, out)
