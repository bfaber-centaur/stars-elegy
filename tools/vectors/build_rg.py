"""Representative game (RG) -> one chained vector with every player's orders.

Called by build.py for CORPUS rg. EVIDENCE_DIR is the apparatus run
(stars-oracle-apparatus evidence/rg001): yNN/ per generated year, with x/
the order files the computer players wrote for that year, gen/ the year
generated from base/ (the previous year's files plus those orders) at the
pinned cycles, and altC/ the same year generated again from the same files
at other cycles values (other random streams).

The vector starts from year 1's start file and chains: year k's expectations
are what changed in the host file from year k-1 to year k in the gen stream
(build_kx.observe, full=True), plus battles, message ids and score records.
Each year is also written alone as RUN-yK, starting from the original's own
files for the year before, with the same orders, expectations and samples.
Every player's orders for every year are decoded into the `orders` block,
and `random_start` gives the startup tick of the gen stream for each year
(each year ran in a new process, so each year's stream starts at seeding).

An expectation is flagged `sample: true` when the year's draws decide it:
the battle rule of build_cb.mark_samples, plus every field whose value
differed in any alternative stream from the same start and orders. A value
the streams happened to agree on can still be drawn; one that changed only
in an alternative stream has no expectation to flag.
"""
import json, os, re
import build as B
import build_cb as C
import build_kx as K
import build_obs as O
import build_orders as R

GAME = 'AIX'
TICK = {20000: 164}  # docs/ORACLE.md "Pinned battle RNG": cycles 20000 -> tick 164 (TK-307)
RUNS = {
    'rg001': dict(
        id='RG-001', cycles=20000,
        title='representative game: six expert computer players and an idle human race, small universe, '
              '2429 to 2435 chained with every player\'s orders',
        setup='apparatus evidence/ai/aix year 2429 (seven players, 97 fleets); each year the computer players '
              'planned from the current files, then the year was generated with their order files supplied, so '
              'the host ran no computer player and the stream starts at seeding; player 0 submitted nothing'),
}
IDENT = {
    'fleet': ('owner', 'id'), 'fleet_gone': ('owner', 'id'), 'planet': ('id',), 'player': ('id', 'seen_by'),
    'production_queue': ('planet',), 'design': ('owner', 'slot'), 'design_gone': ('owner', 'slot'),
    'starbase_design': ('owner', 'slot'), 'starbase_design_gone': ('owner', 'slot'),
    'battle_plan': ('owner', 'slot'), 'battle_plan_gone': ('owner', 'slot'), 'salvage_at': ('x', 'y'),
    'minefield': ('owner', 'id'), 'message': ('player', 'message_id'), 'battle': ('x', 'y'),
    'battle_actions': ('x', 'y'), 'object_gone': ('subject',),
}


def ident(e):
    if e['kind'] == 'object':
        o = e['equals']
        return ('object', o['kind'], o.get('owner'), o['id'])
    return (e['kind'],) + tuple(json.dumps(e.get(k), sort_keys=True) for k in IDENT[e['kind']])


def close(a, b, tol):
    if tol and isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return all(abs(x - y) <= tol for x, y in zip(a, b))
    return a == b


def drawn(exps, alts):
    """Flag what differed in any alternative stream. A dict-valued `equals`
    is split field by field; anything else is flagged whole."""
    alt = [{ident(e): e for e in a} for a in alts]
    out = []
    for e in exps:
        others = [a.get(ident(e)) for a in alt]
        if e.get('sample'):
            out.append(e)
        elif any(o is None for o in others):
            out.append(dict(e, sample=True))
        elif isinstance(e.get('equals'), dict) and e['kind'] != 'object':
            tol = e.get('tolerance', {})
            moved = {f for f, v in e['equals'].items()
                     for o in others if not close(v, o.get('equals', {}).get(f), tol.get(f))}
            moved |= {f for o in others for f in o.get('equals', {}) if f not in e['equals']}
            if not moved:
                out.append(e)
                continue
            keep = {f: v for f, v in e['equals'].items() if f not in moved}
            got = {f: v for f, v in e['equals'].items() if f in moved}
            if keep:
                out.append(dict(e, equals=keep, tolerance={f: t for f, t in tol.items() if f in keep})
                           if tol else dict(e, equals=keep))
                if not out[-1].get('tolerance', True):
                    out[-1].pop('tolerance')
            if got:
                s = dict(e, equals=got, sample=True)
                s.pop('tolerance', None)
                out.append(s)
        elif any(json.dumps(o, sort_keys=True) != json.dumps(e, sort_keys=True) for o in others):
            out.append(dict(e, sample=True))
        else:
            out.append(e)
    return out


def year_battles(adir):
    bs = {}
    for f in sorted(os.listdir(adir)):
        if re.fullmatch(GAME + r'\.M\d+', f):
            bs.update(C.battles(B.last_section(B.dump(os.path.join(adir, f)))))
    return list(bs.values())


def build(ev, out):
    run = os.path.basename(ev.rstrip('/'))
    r = RUNS[run]
    os.makedirs(out, exist_ok=True)
    ydirs = sorted(d for d in os.listdir(ev) if re.fullmatch(r'y\d\d', d)
                   and os.path.exists(os.path.join(ev, d, 'gen', 'raw', 'after', GAME + '.HST')))
    bdir = os.path.join(ev, ydirs[0], 'gen', 'raw', 'before')
    st0 = B.state(B.dump(os.path.join(bdir, GAME + '.HST')), B.dump(os.path.join(bdir, GAME + '.XY')), GAME,
                  os.path.join(bdir, GAME + '.XY'))
    n = len(st0['players'])
    orders, cases, prev, starts = [], [], st0, []
    for k, yd in enumerate(ydirs, 1):
        y = os.path.join(ev, yd)
        for x in sorted(os.listdir(os.path.join(y, 'x')), key=lambda f: int(f.split('.X')[1])):
            player, ords = R.orders_of(os.path.join(y, 'x', x), n)
            orders.append({'year': k, 'player': player, 'orders': ords})
        b = os.path.join(y, 'gen', 'raw', 'before')
        starts.append(B.state(B.dump(os.path.join(b, GAME + '.HST')), B.dump(os.path.join(b, GAME + '.XY')), GAME,
                              os.path.join(b, GAME + '.XY')))
        adir = os.path.join(y, 'gen', 'raw', 'after')
        st1, exps = K.observe(prev, adir, GAME, k, full=True)
        exps = C.mark_samples(exps, year_battles(adir), single=True)
        alts = [K.observe(prev, os.path.join(y, a, 'raw', 'after'), GAME, k, full=True)[1]
                for a in sorted(os.listdir(y)) if re.fullmatch(r'alt\d+', a)]
        exps = drawn(exps, alts)
        year = 2400 + st1['year'] if st1['year'] < 2400 else st1['year']
        cases.append({'id': '%s-%d' % (r['id'], year), 'rule': 'KERNEL',
                      'setup': 'year %d of the chain (%s)' % (k, r['setup']), 'tag': 'MEASURED',
                      'prediction_held': False, 'varies_by_stream': False,
                      'verdict': 'recorded, no prediction committed; samples flagged from %d other streams'
                                 % len(alts), 'expect': exps})
        prev = st1
    vec = {'schema': B.SCHEMA, 'id': r['id'], 'title': r['title'],
           'source': {'experiment': 'stars-oracle-apparatus evidence/%s (private); start from evidence/ai/aix' % run,
                      'spec_rules': 'docs/KERNEL.md "Turn order"', 'parity': 'docs/PARITY.md "Representative game (RG-001)"',
                      'raw_evidence': 'stars-oracle-apparatus evidence/%s (private)' % run},
           'years': len(ydirs), 'random': 'single_stream', 'streams': 1, 'initial_state': st0,
           'orders': orders,
           'random_start': [{'stream': '', 'year': k, 'tick': TICK[r['cycles']]} for k in range(1, len(ydirs) + 1)],
           'cases': cases}
    O.write(out, run, vec)
    # One-year restarts: year k from the original's own files for the year
    # before (the chained vector's state after year k-1), so a mismatch in
    # one year does not carry into the next.
    for k, (sk, ck) in enumerate(zip(starts, cases), 1):
        one = dict(vec, id='%s-Y%d' % (r['id'], k), years=1, initial_state=sk,
                   title='%s: year %d alone, from the original\'s files for the year before' % (r['id'], k),
                   orders=[dict(o, year=1) for o in orders if o['year'] == k],
                   random_start=[{'stream': '', 'year': 1, 'tick': TICK[r['cycles']]}],
                   cases=[dict(ck, id='%s-Y%d-%s' % (r['id'], k, ck['id'].rsplit('-', 1)[1]),
                               setup='year %d alone (%s)' % (k, r['setup']),
                               expect=[dict(e, year=1) for e in ck['expect']])])
        O.write(out, '%s-y%d' % (run, k), one)
    ne = sum(len(c['expect']) for c in cases)
    ns = sum(1 for c in cases for e in c['expect'] if e.get('sample'))
    print('%s: %d years, %d fleets at start, %d order sets (%d orders), %d expectations, %d samples' % (
        r['id'], len(ydirs), len(st0['fleets']), len(orders), sum(len(o['orders']) for o in orders), ne, ns))
