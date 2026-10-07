"""Order-driven corpora -> vectors with an `orders` block.

Called by build.py for CORPUS xf, bp, tk5 or wu. The client-order runs (xf,
bp, tk5) start from a host year whose player order file the original client
wrote; the file's orders are decoded into the vector's `orders` block in
behavior terms (what each order asks for, never how the file stores it).
The WU runs need no order file: their orders are the fleets' waypoints and
repeat flags in the start file. Each run is one pinned year in one random
stream, so every case is MEASURED; `prediction_held` records whether a
prediction committed before the run held.
"""
import os, re
import build as B
import build_kx as K
import build_obs as O

FIELDS = B.TECH
NEXT = {i: f for i, f in enumerate(FIELDS)}
NEXT[7] = 'lowest'
CARGO_DUMP = {'ir': 'ironium', 'bo': 'boranium', 'ge': 'germanium', 'col': 'colonists', 'fuel': 'fuel'}
OTHER = {1: 'planet', 2: 'fleet'}


def u16(b, o):
    return b[o] | b[o + 1] << 8


def orders_of(xpath, nplayers):
    """(player, [order, ...]) from a player order file, in file order."""
    player, out = None, []
    for s in B.dump(xpath):
        d = B.kv(s)
        if s.startswith('file '):
            player = int(d['player'])
        elif s.startswith('order cargo '):
            kind = int(d['kind'], 16)
            if kind & 15 != 2 or kind >> 4 not in OTHER:
                raise ValueError('cargo order kind %02x not decoded' % kind)
            other = {'kind': OTHER[kind >> 4], 'id': int(d['other'])}
            if other['kind'] == 'fleet':
                raise ValueError('cargo to a fleet: the other fleet id word is not decoded yet')
            out.append({'kind': 'cargo', 'fleet': int(d['fleet']), 'with': other,
                        'amounts': {CARGO_DUMP[k]: int(v) for k, v in d.items() if k in CARGO_DUMP}})
        elif s.startswith('order queue '):
            items = [it.split(':') for it in d.get('items', '').split(',') if it]
            out.append({'kind': 'production_queue', 'planet': int(d['planet']),
                        'items': [B.queue_item(i) for i in items]})
        elif s.startswith('order research '):
            out.append({'kind': 'research', 'percent': int(d['pct']), 'field': FIELDS[int(d['field'])],
                        'next_field': NEXT.get(int(d['next']), int(d['next']))})
        elif s.startswith('plan '):
            out.append({'kind': 'battle_plan', 'slot': int(d['k']), 'name': s.split('name=', 1)[1],
                        'tactic': int(d['tactic']), 'primary': int(d['primary']),
                        'secondary': int(d['secondary']), 'attack_who': int(d['who']),
                        'dump_cargo': d['dump'] == 'true'})
        elif s.startswith('order plan-delete '):
            out.append({'kind': 'battle_plan_delete', 'slot': int(d['k'])})
        elif s.startswith('order fleet-plan '):
            out.append({'kind': 'fleet_battle_plan', 'fleet': int(d['fleet']), 'plan': int(d['plan'])})
        elif s.startswith('design ') or s.startswith('sbdesign '):
            m = re.match(r'(sb)?design owner=(\d+) n=(\d+) mass=\d+ armor=-?\d+ full=true :: (.*)', s)
            if not m:
                raise ValueError('design order not decoded: ' + s)
            hull, sl = B.slots(m.group(4))
            out.append({'kind': 'design', 'starbase': bool(m.group(1)), 'slot': int(m.group(3)),
                        'hull': hull, 'slots': sl})
        elif s.startswith('order design-delete '):
            out.append({'kind': 'design_delete', 'starbase': s.split()[2] == 'starbase', 'slot': int(d['slot'])})
        elif s.startswith('order type=5 '):
            # waypoint change: fleet word, waypoint index word, then the waypoint
            # (x, y, target object, warp and task, target type, task order words)
            r = [int(x) for x in s.split('raw=', 1)[1].split()]
            words = ['%04x' % u16(r, o) for o in range(12, len(r) - 1, 2)]
            wd = {'x': u16(r, 4), 'y': u16(r, 6), 'obj': u16(r, 8), 'warp': r[10] >> 4, 'task': r[10] & 15,
                  'type': '%02x' % r[11], 'orders': ','.join(words)}
            out.append({'kind': 'waypoint_change', 'fleet': u16(r, 0) & 0x1ff, 'index': u16(r, 2),
                        'waypoint': B.waypoint(wd, player, nplayers)})
        elif s.startswith('order '):
            raise ValueError('order not decoded: ' + s.split(' raw=')[0])
    return player, out


CLIENT = 'docs/ORACLE.md, client orders'
XF_SPEC = 'docs/ORDERS.md "Fleet operations"; docs/TAKEOVER.md'
# corpus: [(run dir, case id, title, prediction held, verdict, spec, parity, experiment)]
RUNS = {
    'xf': [
        ('xf1/run', 'XF-1', 'manual cargo transfers: load and unload at the own homeworld, unload at an unowned '
         'planet and at a foreign homeworld with a starbase', False,
         'no prediction committed; the host applied every transfer: minerals added at both planets, colonists '
         'lost with message 0x058 at the foreign homeworld (starbase) and 0x002 at the unowned planet',
         XF_SPEC, CLIENT + ' (XF-1)', 'experiments/xf'),
        ('explore/xf1/run', 'XF-1-explore', 'XF-1 exploration run: unloads at the foreign homeworld and the '
         'unowned planet', False, 'no prediction committed; hand-driven run before the command existed',
         XF_SPEC, CLIENT + ' (XF-1)', 'experiments/xf'),
        ('pq1/run', 'PQ-1', 'production queue replaced and research settings changed', False,
         'no prediction committed; the host replaced the queue with the order and built from it the same year '
         '(factory x10 -> 3 built); research percent and field applied',
         'docs/ORDERS.md "Scope and vocabulary"; docs/KERNEL.md "Production"', CLIENT + ' (PQ-1)', 'experiments/xf'),
        ('explore/pq1/run', 'PQ-1-explore', 'PQ-1 exploration run: queue and research', False,
         'no prediction committed; hand-driven run before the command existed',
         'docs/ORDERS.md "Scope and vocabulary"; docs/KERNEL.md "Production"', CLIENT + ' (PQ-1)', 'experiments/xf'),
        ('wp1/run', 'WP-1', 'waypoint-0 tasks: exact transport amounts, colonize without a colony module, scrap '
         'at a foreign homeworld', False,
         'no prediction committed; unload exactly 25 kT ironium and load exactly 30 kT germanium were exact; '
         'colonize failed with 0x054; scrap removed the fleet, gave cargo and scrap to the planet, 0x05a',
         'docs/ORDERS.md "Turn placement"; docs/TAKEOVER.md', CLIENT + ' (WP-1)', 'experiments/xf'),
        ('explore/wp1/run', 'WP-1-explore', 'WP-1 exploration run: one transport task', False,
         'no prediction committed; hand-driven run before the command existed',
         'docs/ORDERS.md "Turn placement"; docs/TAKEOVER.md', CLIENT + ' (WP-1)', 'experiments/xf'),
        ('ds1/run', 'DS-1', 'new design (copy of the Hauler with a Bat Scanner) and lay mines at a deep-space '
         'position (ML-1)', False,
         'no prediction committed; the new design was stored in ship slot 0; an 80-mine field was laid at the '
         'fleet position with message 0x0c3',
         'docs/ORDERS.md "Range and legality clamps"; docs/OBJECTS.md "Minefields"', CLIENT + ' (DS-1, ML-1)',
         'experiments/xf'),
        ('explore/ds1/run', 'DS-1-explore', 'DS-1 exploration run: new design, then delete the in-use Hauler '
         'design', False,
         'no prediction committed; the new design was stored in slot 0 and deleting the in-use design destroyed '
         'all three Haulers that year', 'docs/ORDERS.md "Range and legality clamps"', CLIENT + ' (DS-1)',
         'experiments/xf'),
    ],
    'bp': [
        ('bp1/run', 'BP-1', 'battle plans: two copies, four fleet assignments, delete a plan in use', True,
         'held: six plans remain, fleets end on plans 2, 5, 2, 4; users of the deleted plan get the plan before it',
         'docs/COMBAT.md', 'docs/PARITY.md "Battle plans through the client (BP)"', 'experiments/bp'),
        ('bpl/run', 'BP-L', 'battle plans: ten copies, the client stops at 15 plans', True,
         'held: the client wrote plans 5..14 (a 16th copy was refused) and the host kept 15 plans',
         'docs/COMBAT.md', 'docs/PARITY.md "Battle plans through the client (BP)"', 'experiments/bp'),
    ],
    'tk5': [
        ('tk501/y2', 'TK-501', 'manual cargo transfers to enemy and unowned planets (TK-401..405, TK-410)', False,
         'every planet outcome held; TK-405: ironium given to an enemy planet arrived (+100) but messages '
         '0x042/0x044 were not sent (predicted); planets resolved in the order of the order records',
         'docs/TAKEOVER.md; docs/ORDERS.md "Cross-owner cargo"',
         'docs/PARITY.md "Round 5: manual cargo transfers (TK-501, TK-502)"', 'experiments/tk'),
        ('tk502/y2', 'TK-502', 'manual cargo transfers to a friend (TK-411, TK-412)', False,
         'TK-411 held (captured as an enemy planet); TK-412: ironium arrived (+100) but messages 0x042/0x044 were '
         'not sent (predicted)', 'docs/TAKEOVER.md; docs/ORDERS.md "Cross-owner cargo"',
         'docs/PARITY.md "Round 5: manual cargo transfers (TK-501, TK-502)"', 'experiments/tk'),
    ],
}

WU_SPEC = 'docs/ORDERS.md (waypoint upkeep and the remaining tasks)'
WU_PAR = 'experiments/wu/README.md (turn orders lane)'
# (run, case id, title, prediction held, verdict)
WU = [
    ('wuA', 'WU-A', 'waypoint upkeep: repeat on and off, last waypoint reached, live and gone fleet targets', True,
     'held: repeat off drops the reached waypoint, repeat on moves it to the end; reaching the last waypoint idles '
     'the fleet with the completion message; a live fleet target is tracked; a gone fleet target clears to a '
     'plain go-to at its last position'),
    ('wuB1', 'WU-B1', 'transfer fleet to a recipient at war with the giver', True, 'held: refused'),
    ('wuB2', 'WU-B2', 'transfer fleet: one carrying colonists, one empty', True,
     'held: the colonist-carrying transfer was refused; the empty fleet went to player 1'),
    ('wuROUTE', 'WU-ROUTE', 'route task at a planet with a route', True,
     'held: the fleet was sent to the route destination at warp 6 (~161 ly hop)'),
    ('wuFALLBACK', 'WU-FALLBACK', 'repeat fall-backs: one forward waypoint; two coincident waypoints', True,
     'held: with one forward waypoint the circuit is not regenerated (idle as if repeat were off); with two '
     'coincident waypoints no third is appended'),
    ('wuFOLLOW', 'WU-FOLLOW', 'follower chain and a two-fleet cycle', True,
     'held: each follower advanced one hop and re-pointed at its leader; the mutual pair met at the midpoint and '
     'both waypoints cleared to plain go-tos'),
]
NOPRED = ' (no prediction committed)'
for n in ('CP1', 'CP2', 'CP3', 'CP4'):
    WU.append(('wu' + n, 'WU-' + n, 'patrol: enemies at 60 to 200 ly, Rhino scanner', False,
               'no target chosen: the enemies were beyond the engage radius (diagnostic run)' + NOPRED))
WU.append(('wuCP5', 'WU-CP5', 'patrol: one enemy at 40 ly, Rhino scanner', False, 'intercepted at warp 10' + NOPRED))
for n in ('LP1', 'LP2', 'LP3', 'LP4'):
    WU.append(('wu' + n, 'WU-' + n, 'patrol: enemies at 80 to 200 ly with a 300 ly scanner', False,
               'scanned but not intercepted: the engage radius is not the scanner range' + NOPRED))
for r in (40, 50, 55, 70, 85):
    WU.append(('wuSW%d' % r, 'WU-SW%d' % r, 'patrol: one enemy at %d ly, 300 ly scanner' % r, False,
               ('intercepted' if r <= 50 else 'not intercepted') + ': the engage radius is between 50 and 55 ly'
               + NOPRED))
WU += [
    ('wuTWO', 'WU-TWO', 'patrol: enemies at 30 and 45 ly', False, 'the nearer was chosen' + NOPRED),
    ('wuTWOEQ', 'WU-TWOEQ', 'patrol: two equidistant enemies (40 ly), strong and weak', False,
     'the lowest-numbered fleet was chosen' + NOPRED),
    ('wuTWOEQ2', 'WU-TWOEQ2', 'patrol: two equidistant enemies with strong and weak swapped', False,
     'the same fleet was chosen: strength does not decide' + NOPRED),
    ('wuRNG20', 'WU-RNG20', 'patrol range 20, enemy at 40 ly', False, 'intercepted at warp 4 = min(10, 20/5)' + NOPRED),
    ('wuWARP40', 'WU-WARP40', 'patrol range 40', False, 'intercept warp 8' + NOPRED),
    ('wuWARP90', 'WU-WARP90', 'patrol range 90', False, 'intercept warp 10' + NOPRED),
]

def one(rundir, vid, title, held, verdict, x_orders=True):
    bdir = os.path.join(rundir, 'raw', 'before')
    g = [f for f in os.listdir(bdir) if f.endswith('.HST')][0][:-4]
    st0 = B.state(B.dump(os.path.join(bdir, g + '.HST')), B.dump(os.path.join(bdir, g + '.XY')), g,
                  os.path.join(bdir, g + '.XY'))
    _, exps = K.observe(st0, os.path.join(rundir, 'raw', 'after'), g, 1, full=True)
    cs = B.case(vid, '', title, {'run': exps}, held, set())
    cs['tag'], cs['verdict'] = 'MEASURED', verdict
    vec = {'schema': B.SCHEMA, 'id': vid, 'title': title, 'years': 1, 'random': 'single_stream', 'streams': 1,
           'initial_state': st0}
    if x_orders:
        xs = sorted(f for f in os.listdir(bdir) if re.fullmatch(re.escape(g) + r'\.X\d+', f))
        vec['orders'] = []
        for x in xs:
            player, ords = orders_of(os.path.join(bdir, x), len(st0['players']))
            vec['orders'].append({'year': 1, 'player': player, 'orders': ords})
    vec['cases'] = [cs]
    return vec


def build(corpus, ev, out):
    os.makedirs(out, exist_ok=True)
    if corpus == 'wu':
        runs = [w + (WU_SPEC, WU_PAR, 'experiments/wu') for w in WU]
    else:
        runs = RUNS[corpus]
    for run, vid, title, held, verdict, spec, parity, exp in runs:
        rd = os.path.join(ev, run)
        vec = one(rd, vid, title, held, verdict, corpus != 'wu')
        vec['cases'][0]['rule'] = spec.split(';')[0].split(' (')[0].replace('docs/', '').replace('.md', '')
        vec['source'] = {'experiment': exp, 'spec_rules': spec, 'parity': parity,
                         'raw_evidence': 'stars-oracle-apparatus evidence/%s/%s (private)' % (corpus, run)}
        name = vid.lower()
        O.write(out, name, vec)
        n = sum(len(o['orders']) for o in vec.get('orders', []))
        print('%s: %d orders, %d expectations' % (vid, n, len(vec['cases'][0]['expect'])))
