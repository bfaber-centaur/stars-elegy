"""Kernel edit-turn corpora (KX-001, KX-002) -> vectors.

Called by build.py for CORPUS kx001 or kx002. Each case is one edited PG001
year file run for one year (KX-002 N2: three). The expectations are what
changed in the host file (planets, player tech and research, queues,
fleets) and the message ids the player received; the verdict comes from the
corpus README's "vs prediction" column and the prediction text from the
model's prediction file. Mining's +1 remainder is random (KERNEL.md), so
surface minerals carry a tolerance of 1.
"""
import os, re, subprocess
import build as B
import build_cb as C

PARITY = {'kx001': 'docs/PARITY.md "KX-001 — Auto Alchemy before a multi-count item; race cost options"',
          'kx002': 'docs/PARITY.md "KX-002 — untested BINARY-ONLY kernel rules"'}


def verdicts(readme):
    out = {}
    for line in open(readme):
        m = re.match(r'^\|\s*([A-Z]\d+[a-z]?)\s*\|.*\|\s*([^|]*?)\s*\|\s*$', line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def predictions(path):
    out, cur = {}, None
    for line in open(path):
        m = re.match(r'^([A-Z]\d+[a-z]?)[: ]\s*(.*)$', line)
        if m:
            cur = m.group(1)
            out[cur] = m.group(2).strip()
        elif cur and line.strip():
            out[cur] += '; ' + line.strip()
    return out


def messages(mpath):
    ids = []
    for s in B.dump(mpath):
        m = re.match(r'msg id=0x([0-9a-f]+)', s)
        if m and int(m.group(1), 16) not in ids:
            ids.append(int(m.group(1), 16))
    return ids


CONDITIONS = [(0x40, 'planets_owned_percent'), (0x80, 'tech_level'), (0x100, 'score'),
              (0x200, 'lead_over_second_percent'), (0x400, 'resources_thousands'), (0x800, 'capital_ships'),
              (0x1000, 'highest_score_after_years')]


def score_records(mpath):
    """Yearly score records in a .M file (KERNEL.md "Yearly score record")."""
    out = subprocess.run([B.HSTEDIT, 'dump', mpath], capture_output=True, text=True).stdout
    recs = []
    for m in re.finditer(r' scores ([0-9a-f]+)', out):
        b = bytes.fromhex(m.group(1))
        for o in range(0, len(b) - 23, 24):
            w = [int.from_bytes(b[o + i:o + i + 2], 'little') for i in range(0, 24, 2)]
            recs.append({'player': w[0] & 0x1f, 'rank': w[1], 'score': w[2] | w[3] << 16,
                         'resources': w[4] | w[5] << 16, 'planets': w[6], 'starbases': w[7], 'unarmed_ships': w[8],
                         'escort_ships': w[9], 'capital_ships': w[10], 'tech_level_sum': w[11],
                         'victory_conditions_met': [n for bit, n in CONDITIONS if w[0] & bit]})
    return recs


def observe(st_prev, adir, g, year):
    """Expectations for one generated year: host-file changes since the
    previous year, message ids and score records from every player file."""
    st1 = B.state(B.dump(os.path.join(adir, g + '.HST')), B.dump(os.path.join(adir, g + '.XY')), g)
    exps = []
    for e in C.diff(st_prev, st1):
        if e['kind'] == 'planet' and 'surface_minerals' in e['equals']:
            e['tolerance'] = {'surface_minerals': 1}
        exps.append(dict(e, year=year))
    bs = {}
    for f in sorted(os.listdir(adir)):
        if re.fullmatch(re.escape(g) + r'\.M\d+', f):
            bs.update(C.battles(B.dump(os.path.join(adir, f))))
    for b in sorted(bs.values(), key=lambda b: (b['x'], b['y'])):
        acts = b.pop('actions')
        exps.append(dict(b, year=year))
        exps.append({'kind': 'battle_actions', 'x': b['x'], 'y': b['y'], 'actions': acts, 'year': year})
    for f in sorted(os.listdir(adir)):
        m = re.fullmatch(re.escape(g) + r'\.M(\d+)', f)
        if not m:
            continue
        p = int(m.group(1)) - 1
        exps += [{'kind': 'message', 'player': p, 'message_id': i, 'present': True, 'year': year}
                 for i in messages(os.path.join(adir, f))]
        for r in score_records(os.path.join(adir, f)):
            exps.append({'kind': 'player', 'id': r.pop('player'), 'equals': {'score_record': r},
                         'seen_by': p, 'year': year})
    return st1, exps


def build(corpus, ev, out):
    os.makedirs(out, exist_ok=True)
    raw = os.path.join(ev, 'raw')
    ver = verdicts(os.path.join(ev, 'README.md'))
    pred = predictions(os.path.join(raw, 'model-predictions.txt'))
    n = 0
    for case in sorted(os.listdir(raw)):
        d = os.path.join(raw, case)
        if not os.path.isdir(os.path.join(d, 'before')):
            continue
        bdir = os.path.join(d, 'before')
        st0 = B.state(B.dump(os.path.join(bdir, 'PG001.HST')), B.dump(os.path.join(bdir, 'PG001.XY')), 'PG001',
                      os.path.join(bdir, 'PG001.XY'))
        afters = sorted(a for a in os.listdir(d) if re.fullmatch(r'after\d*', a))
        exps, years, prev = [], 0, st0
        for k, a in enumerate(afters, 1):
            adir = os.path.join(d, a)
            st1, ex = observe(prev, adir, 'PG001', k)
            if st1['year'] == prev['year']:
                break
            years, prev = k, st1
            exps += ex
        v = ver.get(case, '')
        if not years:
            print('%s/%s: no year generated (%s), skipped' % (corpus, case, v or 'crash'))
            continue
        if 'void' in v:
            print('%s/%s: prediction void (%s), skipped' % (corpus, case, v))
            continue
        held = v.startswith('match')
        vid = 'KX-%s-%s' % (corpus[2:], case)
        cs = {'id': vid, 'rule': 'KERNEL', 'setup': 'edited: ' + ', '.join(open(os.path.join(d, 'edit-args.txt')).read().split())
              if os.path.exists(os.path.join(d, 'edit-args.txt')) else case,
              'tag': 'CONFIRMED' if held else 'MEASURED', 'prediction_held': held, 'varies_by_stream': False,
              'verdict': v, 'expect': exps}
        if case in pred:
            cs['prediction'] = pred[case]
        vec = {'schema': B.SCHEMA, 'id': vid, 'title': '%s case %s' % (corpus.upper(), case),
               'source': {'experiment': 'stars-oracle-apparatus evidence/%s (private)' % corpus,
                          'spec_rules': 'docs/KERNEL.md', 'parity': PARITY[corpus],
                          'raw_evidence': 'stars-oracle-apparatus evidence/%s/raw/%s (private)' % (corpus, case)},
               'years': years, 'random': 'single_stream', 'streams': 1, 'initial_state': st0, 'cases': [cs]}
        with open(os.path.join(out, case.lower() + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        n += 1
    print('%s: %d vectors' % (corpus, n))


def chained(vid, title, streams, meta):
    """One vector from runs that each start where the last ended.
    streams: {stream: [rundir, ...]} (pinned-turn layout raw/before, raw/after)."""
    first = list(streams.values())[0][0]
    bdir = os.path.join(first, 'raw', 'before')
    g = [f for f in os.listdir(bdir) if f.endswith('.HST')][0][:-4]
    st0 = B.state(B.dump(os.path.join(bdir, g + '.HST')), B.dump(os.path.join(bdir, g + '.XY')), g,
                  os.path.join(bdir, g + '.XY'))
    per, years = {}, 0
    for sname, dirs in streams.items():
        prev, exps = st0, []
        for k, d in enumerate(dirs, 1):
            prev, ex = observe(prev, os.path.join(d, 'raw', 'after'), g, k)
            exps += ex
        per[sname] = exps
        years = len(dirs)
    held, tag, verdict, pred, rule = meta
    cs = B.case(vid, rule, title, per, held, set())
    cs['tag'], cs['verdict'] = tag, verdict
    if pred:
        cs['prediction'] = pred
    return {'schema': B.SCHEMA, 'id': vid, 'title': title, 'years': years,
            'random': 'single_stream' if len(per) == 1 else 'several_streams', 'streams': len(per),
            'initial_state': st0, 'cases': [cs]}


KX3 = {
    'r1': (['r1'], 's1', True, 'CONFIRMED', 'score records and victory flags as predicted (player 1 research 435 from pre-growth resources)',
           'scores, ranks and victory-condition flags'),
    'r2': (['r2a', 'r2b'], 's2', True, 'CONFIRMED', 'slower tech: stored research and levels as predicted (corrected figures)',
           'slower tech over two years'),
    'r3': (['r3'], 's3', False, 'MEASURED', 'Claim Adjuster drift as predicted; the Super Stealth part is void (the race tripped message 0x117)',
           'Claim Adjuster and Super Stealth'),
    'r3l': (['r3l'], 's3b', True, 'CONFIRMED', 'research with the LRT race and Claim Adjuster as predicted',
            'Claim Adjuster with an LRT race'),
}


def build_kx003(ev, out):
    os.makedirs(out, exist_ok=True)
    raw = os.path.join(ev, 'raw')
    for name, (dirs, pfile, held, tag, verdict, title) in KX3.items():
        pp = os.path.join(raw, pfile + '-predictions.txt')
        pred = '; '.join(l.strip() for l in open(pp) if l.strip()) if os.path.exists(pp) else ''
        vec = chained('KX-003-' + name, 'KX-003 %s: %s' % (name, title), {'run': [os.path.join(raw, d) for d in dirs]},
                      (held, tag, verdict, pred, 'KERNEL'))
        vec['source'] = {'experiment': 'experiments/kx003', 'spec_rules': 'docs/KERNEL.md',
                         'parity': 'docs/PARITY.md "KX-003 — scores, victory conditions, slower tech, Claim Adjuster, Super Stealth"',
                         'raw_evidence': 'stars-oracle-apparatus evidence/kx003/raw/{%s} (private)' % ','.join(dirs)}
        with open(os.path.join(out, name + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
    print('kx003: %d vectors' % len(KX3))


KX4 = {
    'S1': (False, 'MEASURED', 'random events from E1 year 2430; the first-round draw order missed and was corrected from this run'),
}


def build_kx004(ev, out):
    os.makedirs(out, exist_ok=True)
    raw = os.path.join(ev, 'raw')
    n = 0
    for s in sorted((d for d in os.listdir(raw) if re.fullmatch(r'S\d+', d)), key=lambda d: int(d[1:])):
        sd = os.path.join(raw, s)
        streams = {'cycles ' + c[1:]: [os.path.join(sd, c)] for c in sorted(os.listdir(sd), key=lambda c: int(c[1:]))
                   if re.fullmatch(r'c\d+', c)}
        held, tag, verdict = KX4.get(s, (True, 'CONFIRMED', 'random events (comet strike, climate change, new minerals) '
                                         'and Mystery Trader appearance as predicted in every stream'))
        vec = chained('KX-004-' + s, 'KX-004 %s: one year of random events under %d streams' % (s, len(streams)),
                      streams, (held, tag, verdict, '', 'KERNEL random events'))
        vec['source'] = {'experiment': 'experiments/kx004', 'spec_rules': 'docs/KERNEL.md "Random events"',
                         'parity': 'docs/PARITY.md "KX-004 — random events and turn-time game options"',
                         'raw_evidence': 'stars-oracle-apparatus evidence/kx004/raw/%s (private)' % s}
        with open(os.path.join(out, s.lower() + '.json'), 'w') as f:
            B.json.dump(vec, f, separators=(',', ':'))
            f.write('\n')
        n += 1
        print('KX-004-%s: %d streams, %d expectations' % (s, len(streams), len(vec['cases'][0]['expect'])))
    print('kx004: %d vectors' % n)
