"""WT corpus (experiments/wt) -> vectors. Called by build.py for CORPUS wt.

WT runs record their outcomes through experiments/wt/check.py rather than a
check.out of want/got pairs, so this adapter re-reads each stream's dumps and
writes the observed value behind every check tuple.
"""
import os, re, sys
import build as B

sys.path.insert(0, os.path.join(B.ROOT, 'experiments', 'wt'))
import gen, check  # noqa: E402

PARITY = 'docs/PARITY.md "Wormholes and Mystery Trader, round 2 (WT-001 to WT-005)"'


def cargo(f):
    return dict(zip(B.CARGO[:4], (int(x) for x in f['cargo'].split('/'))))


def observe(c, b, a, ev, pk, des):
    k = c[0]
    if k in ('fleetat', 'cargo'):
        f = a['fleets'].get((c[1], c[2]))
        if f is None:
            return {'kind': 'fleet_gone', 'owner': c[1], 'id': c[2]}
        eq = {'x': f['x'], 'y': f['y']} if k == 'fleetat' else {'cargo': {'ironium': cargo(f)['ironium']}}
        return {'kind': 'fleet', 'owner': c[1], 'id': c[2], 'equals': eq}
    if k == 'gone':
        f = a['fleets'].get((c[1], c[2]))
        if f is None:
            return {'kind': 'fleet_gone', 'owner': c[1], 'id': c[2]}
        return {'kind': 'fleet', 'owner': c[1], 'id': c[2], 'equals': {'x': f['x'], 'y': f['y']}}
    if k in ('worm', 'wormbit'):
        w = a['worms'][c[1]]
        field = {'seen': 'known_to', 'seen2': 'destination_known_to'}[c[2]]
        return {'kind': 'wormhole', 'id': c[1], 'equals': {field: B.mask_players(int(w[c[2]], 16))}}
    if k == 'packetat':
        got = pk.get((c[1], c[2]))
        if got is None:
            return {'kind': 'packet_gone', 'owner': c[1], 'id': c[2]}
        return {'kind': 'packet', 'owner': c[1], 'id': c[2], 'equals': {'x': got[0], 'y': got[1]}, 'tolerance': 1}
    if k == 'trader':
        t = a['traders'][c[1]]
        return {'kind': 'trader', 'id': c[1], 'equals': {'x': t['x'], 'y': t['y'], 'warp': t['warp'],
                                                         'destination': list(t['dest']),
                                                         'met': B.mask_players(int(t['met'], 16))}}
    if k == 'tech':
        return {'kind': 'player', 'id': c[1], 'equals': {'tech': dict(zip(B.TECH, a['players'][c[1]]['tech']))}}
    if k == 'techgain':
        per = [x - y for x, y in zip(a['players'][c[1]]['tech'], b['players'][c[1]]['tech'])]
        return {'kind': 'sample', 'check': 'tech_gain', 'target': [c[1]], 'constraint': 'total levels gained = %d' % c[2],
                'observed': {'total': sum(per), 'by_field': dict(zip(B.TECH, per))}}
    if k == 'accum':
        return {'kind': 'player', 'id': c[1],
                'equals': {'research_accumulated': {B.TECH[c[2]]: a['players'][c[1]]['accum'][c[2]]}}}
    if k == 'mt':
        m = int(a['players'][c[1]]['mt'], 16)
        return {'kind': 'player', 'id': c[1], 'equals': {'mystery_trader_items': [B.MT_ITEMS[i] for i in B.mask_players(m, 13)]}}
    if k == 'msg':
        return {'kind': 'message', 'player': c[1], 'message_id': c[2], 'present': check.has_msg(ev[c[1]], c[2])}
    if k == 'designs':
        return {'kind': 'player', 'id': c[1],
                'equals': {'ship_design_count': sum(1 for (o, _) in des if o == str(c[1]))}}
    if k == 'nonew':
        new = sorted(f[1] for f in a['fleets'] if f[0] == c[1] and f not in b['fleets'])
        return {'kind': 'no_new_fleets', 'owner': c[1], 'observed_new': new}
    raise ValueError(k)


def jumps(b, a, n):
    out = []
    for k in range(n):
        o, w = b['worms'][k], a['worms'][k]
        out.append({'id': k, 'jumped': w['years'] == 0, 'move': [w['x'] - o['x'], w['y'] - o['y']],
                    'years_since_jump': w['years'], 'known_to': B.mask_players(int(w['seen'], 16)),
                    'destination_known_to': B.mask_players(int(w['seen2'], 16))})
    return {'kind': 'sample', 'check': 'wormhole_jumps', 'target': [n], 'observed': out,
            'constraint': 'each end jiggles (each axis within 12 ly, years +1, both masks kept) or jumps '
                          '(years 0, known bit cleared unless re-seen, destination bit kept)'}


def gift(b, a, des, owner, fid):
    new = [k for k in a['fleets'] if k[0] == owner and k not in b['fleets']]
    obs = {'meeting_fleet_gone': (owner, fid) not in a['fleets'],
           'mystery_trader_items': [B.MT_ITEMS[i] for i in B.mask_players(int(a['players'][owner]['mt'], 16), 13)],
           'tech_changed': a['players'][owner]['tech'] != b['players'][owner]['tech']}
    if new:
        f = a['fleets'][new[0]]
        d, n = map(int, f['ships'].split(':'))
        hull, sl = B.slots(des.get((str(owner), d), '?'))
        obs['new_fleet'] = {'x': f['x'], 'y': f['y'], 'fuel': f['fuel'], 'design_slot': d, 'count': n,
                            'design': {'hull': hull, 'slots': sl}}
    return {'kind': 'sample', 'check': 'trader_gift', 'target': [owner, fid], 'observed': obs,
            'constraint': 'one of: nothing, M.T. Lifeboat x1-2, M.T. Scout or Probe x1-4, in the first free design slot'}


def trader_of(rid, tn, cid):
    """The Trader a case's meeting is staged with (a warp bump voids it)."""
    if rid == 'WT-003':
        return {'WT-003-A': 'any', 'WT-003-B': 12}.get(cid, tn)
    if rid == 'WT-004':
        return tn - 1 if tn else None
    return None


def rule_of(c):
    found = sorted(set(re.findall(r'O-\d+', c['what'] + ' ' + c['prediction'] + ' ' + c['alt'])))
    sec = re.match(r'(\d+\.\d+):', c['what'])
    if sec:
        found.insert(0, 'OBJECTS %s' % sec.group(1))
    return ', '.join(found) or 'O-47 (follow-up)'


def build(ev, out):
    os.makedirs(out, exist_ok=True)
    root = os.path.join(ev, 'batch', 'run')
    for r in gen.RUNS:
        name = r.rid.lower().replace('-', '')
        dirs = sorted(d for d in os.listdir(root) if d.startswith(name + '-c'))
        st = B.state(B.dump(os.path.join(root, dirs[0], 'raw', 'before', 'CB.HST')),
                     B.dump(os.path.join(root, dirs[0], 'raw', 'before', 'CB.XY')), 'CB',
                     os.path.join(root, dirs[0], 'raw', 'before', 'CB.XY'))
        vec = {'schema': B.SCHEMA, 'id': r.rid, 'title': r.title,
               'source': {'experiment': 'experiments/wt', 'spec_rules': 'docs/OBJECTS.md', 'parity': PARITY,
                          'raw_evidence': 'stars-oracle-apparatus evidence/wt/batch/run/%s-c* (private)' % name},
               'years': 1, 'random': 'several_streams', 'streams': len(dirs), 'initial_state': st, 'cases': []}
        per_case = {c['id']: ({}, True, []) for c in r.cases}
        for d in dirs:
            stream = 'cycles ' + d.split('-c')[1]
            res, (b, a, des, des0, ev2) = check.check_run(r.rid, os.path.join(root, d))
            ok = dict((cid, o) for cid, o, _ in res)
            pk, _ = check.host_extra(os.path.join(root, d, 'after.dump'))
            bumped = check.bumps(b, a)
            for tn, c in enumerate(r.cases):
                per, held, void = per_case[c['id']]
                chk = c['check']
                if chk is None:
                    continue
                t = trader_of(r.rid, tn, c['id'])
                if t is not None and (t == 'any' and bumped or t in bumped):
                    void.append(stream)
                    continue
                if chk[0] == 'jumps':
                    e = [jumps(b, a, chk[1])]
                    rows = check.jumps(b, a, chk[1])
                    o = all(x[2] for x in rows)
                elif chk[0] == 'gift':
                    e = [gift(b, a, des, chk[1], chk[2])]
                    o = check.gift(b, a, des, des0, ev2, *chk[1:])[1]
                else:
                    e = [observe(x, b, a, ev2, pk, des) for x in (chk if isinstance(chk, list) else [chk])]
                    o = ok[c['id']]
                per[stream] = [dict(x, year=1) for x in e]
                per_case[c['id']] = (per, held and o, void)
        for tn, c in enumerate(r.cases):
            per, held, void = per_case[c['id']]
            if not per:
                continue
            chk = c['check'] if isinstance(c['check'], list) else [c['check']]
            meets = any(x and x[0] in ('trader', 'mt', 'techgain', 'gift') for x in chk)
            if trader_of(r.rid, tn, c['id']) is not None or meets:
                # a Trader encounter: where the Trader ends, and so which fleet it
                # meets, depends on its 1/25 warp rise (OBJECTS.md "Movement"); the
                # oracle streams where it rose are void (WT-003, WT-004), but each
                # remaining stream is still one draw
                per = {st: [dict(x, sample=True) if x['kind'] != 'sample' else x for x in xs]
                       for st, xs in per.items()}
            cs = B.case(c['id'], rule_of(c), c['what'], per, held, set())
            cs['prediction'] = c['prediction']
            if void:
                cs['void_streams'] = {'streams': void, 'reason': 'the Trader warp-bumped before the meeting'}
            vec['cases'].append(cs)
        with open(os.path.join(out, name + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        print('%s: %d cases, %d streams' % (r.rid, len(vec['cases']), len(dirs)))
