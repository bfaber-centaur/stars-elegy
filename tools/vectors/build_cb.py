"""CB combat corpus -> vectors. Called by build.py for CORPUS cb.

The combat rounds have no per-case checker output: predictions are in each
experiments/cbNNN/README.md and the verdicts in PARITY.md "Combat". So a CB
vector holds one case per experiment setup whose expectations are the
original's observed outcome: every battle record (decoded) and every
fleet, planet, player and salvage change in the host file after the turn.
The verdict and tag for each setup are curated below from those READMEs.
"""
import hashlib, os, re
import build as B

ROUNDS = ['cb', 'cb2', 'cb3', 'cb4', 'cb4b', 'cb5', 'cb6']
SKIP = {'cb000', 'cb018-batch1', 'cb046-morph-v1', 'cltool', 'pin', 'tools', 'newgame', 'analysis'}
PARITY = 'docs/PARITY.md "Combat"'

# setup: (prediction_held, tag, verdict). Tag CONFIRMED = the advance
# prediction held; MEASURED = it missed, was inconclusive or there was none;
# LEGACY BUG = the setup shows a documented defect.
VERDICT = {
    'cb001': (True, 'CONFIRMED', 'token values, start squares, salvo counts and damage spread as predicted; B1 salvage (round 1, unpinned)'),
    'cb002': (False, 'MEASURED', 'weapon results as predicted; C9/C10 contradicted: a lone starbase does not start a battle (round 1, unpinned)'),
    'cb003': (False, 'MEASURED', 'S2 contradicted: a starbase does not start a battle (round 1, unpinned)'),
    'cb004': (False, 'MEASURED', 'S2 contradicted: a starbase does not start a battle (round 1, unpinned)'),
    'cb005': (False, 'MEASURED', 'contradicted: an unarmed station appears as a token (round 1, unpinned)'),
    'cb006': (False, 'MEASURED', 'contradicted: a lone starbase does not start a battle (round 1, unpinned)'),
    'cb007': (True, 'CONFIRMED', 'Regenerating Shields as predicted (round 1, unpinned)'),
    'cb008': (True, 'CONFIRMED', 'Regenerating Shields as predicted (round 1, unpinned)'),
    'cb009': (True, 'CONFIRMED', 'deterministic deep-space cases K1..K8 as predicted'),
    'cb010': (True, 'CONFIRMED', 'leftover beam damage carried to the next stack (Q-7)'),
    'cb011': (True, 'CONFIRMED', 'S1 battle with plan "enemies"; S2-S7 as predicted (Q-1, Q-4, Q-13)'),
    'cb012': (False, 'MEASURED', 'Q-2 contradicted: plan 0 "everyone" gave a battle at S1 in every stream'),
    'cb013': (True, 'CONFIRMED', 'S1 battle with plan "player 1" (Q-1)'),
    'cb014': (True, 'CONFIRMED', 'no battle with plan "nobody"'),
    'cb015': (True, 'MEASURED', 'T1 inconclusive (visitors died before station range), T2 as predicted'),
    'cb016': (True, 'CONFIRMED', 'the station fired at the frigates (Q-3)'),
    'cb017': (True, 'CONFIRMED', 'repair between turns (Q-12); only the first year is a vector here'),
    'cb018': (True, 'MEASURED', 'tech from battle (Q-11), measured over 14 streams'),
    'cb018-control': (True, 'MEASURED', 'control for CB-018: research without a battle'),
    'cb019-t3': (False, 'MEASURED', 'tactics 3 vs 4 prediction contradicted'),
    'cb019-t4': (False, 'MEASURED', 'tactics 3 vs 4 prediction contradicted'),
    'cb020-t5': (True, 'CONFIRMED', 'tactics 3, 4 and 5 at six pinned streams (R-8)'),
    'cb021': (True, 'CONFIRMED', 'tech from battle at six pinned streams (R-9)'),
    'cb022': (True, 'LEGACY BUG', 'plan 0 "player i" one-player battle (R-10)'),
    'cb022-enemies': (True, 'LEGACY BUG', 'plan 0 "enemies" variant of the R-10 battle'),
    'cb022-everyone': (False, 'LEGACY BUG', '"everyone" contradicted the prediction; recorded as part of the R-10 LEGACY BUG'),
    'cb022-nolone': (True, 'LEGACY BUG', 'without the lone hauler there is no battle record (R-10)'),
    'cb023': (False, 'MEASURED', 'fuel lost with destroyed ships: rule confirmed, the committed fuel value (124) missed'),
    'cb023-control': (True, 'MEASURED', 'control for CB-023'),
    'cb024': (True, 'CONFIRMED', 'repair rates, Inner Strength and starbases (28/28)'),
    'cb025': (True, 'CONFIRMED', 'dump cargo at battle setup'),
    'cb026': (True, 'CONFIRMED', 'a range-0 beam on a starbase'),
    'cb027': (True, 'CONFIRMED', "a starbase's plain cost in target choice"),
    'cb028': (False, 'MEASURED', 'disengage partly confirmed; the Runner changed square on every move (missed)'),
    'cb029': (True, 'CONFIRMED', 'tech attempt of a wiped-out participant'),
    'cb030': (True, 'CONFIRMED', 'several movers on both sides (2 streams)'),
    'cb031-n3': (True, 'CONFIRMED', 'tech attempts with three players'),
    'cb031-obs': (True, 'LEGACY BUG', 'observer tech attempt LEGACY BUG, 12/12 streams; the observer gets no record'),
    'cb032': (False, 'MEASURED', 'contradicted: the Runner never stayed on its square; the rule is untested'),
    'cb033': (True, 'CONFIRMED', 'a player found out at step 5 keeps firing (6/6)'),
    'cb034': (True, 'CONFIRMED', 'a disengaging token stays on its square (6/6)'),
    'cb035': (True, 'LEGACY BUG', 'plan 0 value X on the first location of a turn'),
    'cb035-lone': (True, 'LEGACY BUG', 'CB-035 variant'),
    'cb035-move': (True, 'LEGACY BUG', 'CB-035 variant'),
    'cb035-p0lone': (True, 'LEGACY BUG', 'CB-035 variant'),
    'cb035-prev3': (False, 'LEGACY BUG', 'X carried from the previous location confirmed; the side prediction for player 1 missed'),
    'cb035-prevbattle': (True, 'LEGACY BUG', 'X carried from the previous battle'),
    'cb036': (True, 'CONFIRMED', 'start squares for n = 4 and 6, and a starbase owner past row n'),
    'cb037': (True, 'LEGACY BUG', 'the observer tech LEGACY BUG for players other than 0'),
    'cb037-deep': (True, 'LEGACY BUG', 'CB-037 in deep space'),
    'cb037-owner': (True, 'LEGACY BUG', 'CB-037 with the planet owner'),
    'cb038': (False, 'MEASURED', 'speed code confirmed for one-ship stacks; the cargo prediction missed'),
    'cb038-wm': (True, 'CONFIRMED', 'War Monger in the speed code'),
    'cb039': (False, 'MEASURED', 'token cap: 255, not 256, and player 1 got the extra token (missed); left-out fleets confirmed'),
    'cb040': (True, 'CONFIRMED', 'salvage past 30000 kT'),
    'cb041': (False, 'MEASURED', 'AR starbase destroyed: survival prediction missed; the after-turn rule confirmed'),
    'cb041-joat': (True, 'MEASURED', 'JOAT control for CB-041; resolved by replay afterwards'),
    'cb041-sf': (True, 'CONFIRMED', 'AR with a surviving fleet'),
    'cb041-sf-joat': (True, 'MEASURED', 'JOAT control for CB-041-sf'),
    'cb042': (True, 'CONFIRMED', 'token cap with three players (CAP-A)'),
    'cb043': (True, 'CONFIRMED', 'token cap with a starbase and a three-design fleet (CAP-B)'),
    'cb044': (True, 'CONFIRMED', 'the second pass skips a fleet that does not fit (CAP-C)'),
    'cb045': (True, 'CONFIRMED', "how a fleet's cargo enters the speed code"),
    'cb046': (False, 'MEASURED', 'Mystery Trader items from battle: no gain anywhere (missed)'),
    'cb046-bio': (False, 'MEASURED', 'CB-046 variant; biotechnology gains explained by replay afterwards'),
    'cb046-morph': (False, 'MEASURED', 'CB-046 variant'),
    'cb047': (True, 'CONFIRMED', 'queued ships lost with a starbase'),
    'cb047-ctl': (True, 'MEASURED', 'control for CB-047'),
}


def stream_name(r):
    b = os.path.basename(r)
    return 'cycles ' + b[4:] if b.startswith('run-') else b


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def battles(lines):
    """Decoded battle records from one .M dump: {key: battle}."""
    out, b, act = {}, None, None
    for s in lines:
        d = B.kv(s)
        if s.startswith('battle '):
            b = {'kind': 'battle', 'x': int(d['x']), 'y': int(d['y']),
                 'planet': None if int(d['planet']) == 65535 else int(d['planet']),
                 'players': B.mask_players(int(d['mask'], 16)), 'tokens': [], 'actions': []}
            key = None
        elif s.startswith('battlehex ') and b is not None:
            out[s.split(' ', 1)[1]] = b
        elif s.startswith('  tok ') and b is not None:
            obj, kind = int(d['obj']), int(d['kind'])
            u, pc = d['dmg'].rstrip('%').split('/')
            sq = [int(v) for v in d['sq'].strip('()').split(',')]
            t = {'owner': int(d['owner']), 'kind': {1: 'starbase', 2: 'ships'}.get(kind, kind),
                 'design': int(d['design']), 'start_square': sq, 'initiative': int(d['init']),
                 'jammer': int(d['jam']), 'computer': int(d['comp']), 'capacitor': int(d['cap']),
                 'deflector': int(d['defl']), 'mass': int(d['mass']), 'shield': int(d['shield']),
                 'ships': int(d['ships']), 'damage': {'units': int(u), 'percent_of_ships': int(pc)}}
            t['planet' if kind == 1 else 'fleet'] = obj if kind == 1 else obj & 0x1ff
            b['tokens'].append(t)
        elif s.startswith('  act ') and b is not None:
            to = d['to']
            act = {'round': int(d['round']), 'token': int(d['tok']),
                   'to': None if to == 'off' else [int(v) for v in to.strip('()').split(',')], 'hits': []}
            b['actions'].append(act)
        elif s.startswith('    hit ') and act is not None:
            u, pc = d['dmg'].rstrip('%').split('/')
            act['hits'].append({'token': int(d['tok']), 'flags': int(d['flags'], 16), 'kills': int(d['kills']),
                                'shield_damage': int(d['shielddmg']),
                                'armor_damage': {'units': int(u), 'percent_of_ships': int(pc)}})
    return out


def strip_fleet(f):
    return {k: v for k, v in f.items() if k not in ('owner', 'id', 'waypoints', 'battle_plan')}


def diff(st0, st1):
    """Host-file changes over the turn as expectations."""
    ex = []
    f0 = {(f['owner'], f['id']): f for f in st0['fleets']}
    f1 = {(f['owner'], f['id']): f for f in st1['fleets']}
    for k in sorted(set(f0) | set(f1)):
        if k not in f1:
            ex.append({'kind': 'fleet_gone', 'owner': k[0], 'id': k[1]})
        elif k not in f0 or strip_fleet(f0[k]) != strip_fleet(f1[k]):
            ex.append({'kind': 'fleet', 'owner': k[0], 'id': k[1], 'equals': strip_fleet(f1[k])})
    p0 = {p['id']: p for p in st0['planets']}
    for p in st1['planets']:
        q = p0.get(p['id'], {})
        ch = {k: v for k, v in p.items() if k not in ('id', 'x', 'y') and q.get(k) != v}
        for k in q:
            if k not in p and k not in ('id', 'x', 'y'):
                ch[k] = None
        if ch:
            ex.append({'kind': 'planet', 'id': p['id'], 'equals': ch})
    pl0 = {p['id']: p for p in st0['players']}
    for p in st1['players']:
        ch = {k: p[k] for k in ('tech', 'research_accumulated', 'mystery_trader_items', 'race') if p[k] != pl0[p['id']][k]}
        if ch:
            ex.append({'kind': 'player', 'id': p['id'], 'equals': ch})
    q0 = {q['planet']: q['items'] for q in st0['production_queues']}
    for q in st1['production_queues']:
        if q0.get(q['planet']) != q['items']:
            ex.append({'kind': 'production_queue', 'planet': q['planet'],
                       'equals': [{k: v for k, v in i.items() if k != 'kind'} for i in q['items']]})
    ident = lambda o: (o['kind'], o.get('owner'), o['id'])
    o0 = {ident(o): o for o in st0['objects']}
    o1 = {ident(o): o for o in st1['objects']}
    for o in st1['objects']:
        if o['kind'] == 'packet' and o['destination_planet'] == 1023:
            ex.append({'kind': 'salvage_at', 'x': o['x'], 'y': o['y'], 'equals': {'minerals': o['minerals']}})
        elif o['kind'] == 'minefield' and o0.get(ident(o)) != o:
            ex.append({'kind': 'minefield', 'owner': o['owner'], 'id': o['id'],
                       'equals': {k: v for k, v in o.items() if k not in ('kind', 'owner', 'id')}})
        elif o0.get(ident(o)) != o:
            ex.append({'kind': 'object', 'equals': o})
    for k, o in o0.items():
        if k not in o1 and not (o['kind'] == 'packet' and o['destination_planet'] == 1023):
            ex.append({'kind': 'object_gone', 'subject': {'kind': o['kind'], 'owner': o.get('owner'), 'id': o['id']}})
    return ex


def build(ev, out):
    os.makedirs(out, exist_ok=True)
    root = os.path.dirname(ev.rstrip('/'))
    n = 0
    pool = {}
    for rnd in ROUNDS:
        for setup in sorted(os.listdir(os.path.join(root, rnd))):
            sd = os.path.join(root, rnd, setup)
            start = os.path.join(sd, 'start.HST')
            if setup in SKIP or not os.path.exists(start):
                continue
            h = sha(start)
            for r in sorted(os.listdir(sd)):
                bdir = os.path.join(sd, r, 'raw', 'before')
                if not r.startswith('run') or not os.path.isdir(bdir):
                    continue
                hs = [f for f in os.listdir(bdir) if f.endswith('.HST')]
                if hs and sha(os.path.join(bdir, hs[0])) == h:
                    e = pool.setdefault(setup, {'start': start, 'hash': h, 'rounds': [], 'runs': []})
                    if e['hash'] != h:
                        raise SystemExit('%s: start files differ between rounds' % setup)
                    if rnd not in e['rounds']:
                        e['rounds'].append(rnd)
                    e['runs'].append(os.path.join(sd, r))
    for setup in sorted(pool):
            start, runs, rnd = pool[setup]['start'], pool[setup]['runs'], '+'.join(pool[setup]['rounds'])
            sd = os.path.dirname(runs[0])
            name = re.sub(r'^cb', '', setup)
            vid = 'CB-' + name
            path = os.path.join(out, setup + '.json')
            bdir = os.path.join(runs[0], 'raw', 'before')
            g = [f for f in os.listdir(bdir) if f.endswith('.HST')][0][:-4]
            st0 = B.state(B.dump(start), B.dump(os.path.join(bdir, g + '.XY')), g, os.path.join(bdir, g + '.XY'))
            per = {}
            for r in runs:
                adir = os.path.join(r, 'raw', 'after')
                st1 = B.state(B.dump(os.path.join(adir, g + '.HST')), B.dump(os.path.join(adir, g + '.XY')), g)
                bs = {}
                for f in sorted(os.listdir(adir)):
                    if re.search(r'\.M\d+$', f):
                        bs.update(battles(B.dump(os.path.join(adir, f))))
                exps = []
                for b in sorted(bs.values(), key=lambda b: (b['x'], b['y'])):
                    acts = b.pop('actions')
                    exps.append(b)
                    exps.append({'kind': 'battle_actions', 'x': b['x'], 'y': b['y'], 'actions': acts})
                if not exps:
                    exps = [{'kind': 'no_battle'}]
                exps = [dict(e, year=1) for e in exps + diff(st0, st1)]
                sn = stream_name(r)
                per[sn if sn not in per else sn + ' (' + r.split('/')[-3] + ')'] = exps
            held, tag, verdict = VERDICT[setup]
            cs = B.case(vid, 'docs/COMBAT.md', 'see experiments/%s/README.md' % readme(setup), per, held, set())
            cs['tag'], cs['verdict'] = tag, verdict
            vec = {'schema': B.SCHEMA, 'id': vid, 'title': title(setup),
                   'source': {'experiment': 'experiments/' + readme(setup), 'spec_rules': 'docs/COMBAT.md',
                              'parity': PARITY,
                              'raw_evidence': 'stars-oracle-apparatus evidence/{%s}/%s (private)' % (rnd.replace('+', ','), setup)},
                   'years': 1, 'random': 'single_stream' if len(runs) == 1 else 'several_streams',
                   'streams': len(runs), 'initial_state': st0, 'cases': [cs]}
            with open(path, 'w') as f:
                B.json.dump(vec, f, separators=(',', ':'))
                f.write('\n')
            n += 1
            print('%s: %d streams, %d expectations, %d KB' % (vid, len(runs), len(cs['expect']),
                                                              os.path.getsize(path) // 1024))
    print('cb: %d vectors' % n)


def readme(setup):
    num = int(re.match(r'cb(\d+)', setup).group(1))
    for cand in ('cb%03d' % num, 'cb%03d' % (num - 1), 'cb011', 'cb005', 'cb003', 'cb007', 'cb031'):
        p = os.path.join(B.ROOT, 'experiments', cand, 'README.md')
        if os.path.exists(p) and ('CB-%03d' % num) in open(p).read():
            return cand
    return 'cb%03d' % num


def title(setup):
    p = os.path.join(B.ROOT, 'experiments', readme(setup), 'README.md')
    head = open(p).readline().lstrip('# ').strip()
    return head + ('' if setup == readme(setup) else ' (%s)' % setup)
