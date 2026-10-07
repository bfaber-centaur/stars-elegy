"""SC scanning corpus -> vectors. Called by build.py for CORPUS sc.

Each SC run's check.txt compares the scanning model with what each viewer's
player file showed after the year: `expected` is the advance prediction and
`got` the original's value. Every check becomes a `view` expectation of the
observed value. SC-015 (tamper check fired) and SC-021 (invalid setup) are
left out; REC lines (record only, no expectation) and VIEW-DIFF lines
(differences outside the cases) are not cases.
"""
import ast, hashlib, os, re
import build as B

SKIP = {'sc015', 'sc021', 'tools'}
PARITY = 'docs/PARITY.md "Scanning"'
OLD = re.compile(r'^(OK|MISS|MISMATCH)\s+(\S+)\s+viewer (\d+) (planet|fleet) (\S+)\s+expected (\S+) got (\S+)\s*(.*)$')
NEW = re.compile(r'^(OK|MISS|MISMATCH)\s+(SC\S+)\s+(\w+)\s+(\(.*?\))\s+expected (.*?)\s+got (.*?)\s{2,}(.*)$')
DESIGNS = re.compile(r'^(OK|MISS|MISMATCH)\s+player (\d+) foreign (designs|sbdesigns) partial/full: model \((\d+), (\d+)\) observed \((\d+), (\d+)\)')
BLOCK = re.compile(r"^(OK|MISS|MISMATCH)\s+player (\d+) block of player (\d+): model (\S+) observed (.*)$")


NOPRED = object()


def lit(s):
    s = s.strip()
    if s == '':
        return None
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return s


def level(s):
    return int(s.lstrip('L'))


def subj(kind, a):
    if kind == 'planet':
        return {'kind': 'planet', 'id': a}
    o, i = a
    return {'kind': 'fleet', 'owner': o, 'id': i}


def new_line(kind, args, want, got):
    """Round-4 check -> (viewer, subject, field, predicted, observed)."""
    v = args[0]
    if kind in ('fleet', 'heading', 'mass', 'cargo'):
        s = subj('fleet', (args[1], args[2]))
    elif kind in ('planet', 'sbbit', 'env', 'defest', 'popest'):
        s = subj('planet', args[1])
    elif kind in ('player', 'sbdesigns'):
        s = {'kind': 'player', 'id': args[1]}
    elif kind == 'design':
        s = {'kind': 'design', 'owner': args[1], 'id': args[2]}
    else:
        raise ValueError(kind)
    field = {'fleet': 'level', 'planet': 'level', 'player': 'player_block', 'sbbit': 'starbase_visible',
             'sbdesigns': 'starbase_designs_full', 'env': 'environment_visible', 'heading': 'heading',
             'mass': 'mass_shown', 'cargo': 'cargo_shown', 'defest': 'defense_estimate',
             'popest': 'population_estimate', 'design': 'design_full'}[kind]
    w, g = lit(want), lit(got)
    if isinstance(g, tuple):
        g = list(g)
    if isinstance(w, tuple):
        w = list(w)
    return v, s, field, w, g


def cases_of(d):
    """Rule claims and notes from the run's .cases table (rounds 1-3)."""
    out = {}
    for f in os.listdir(d):
        if f.endswith('.cases'):
            for line in open(os.path.join(d, f)):
                if line.startswith('#') or not line.strip():
                    continue
                c = line.rstrip('\n').split('\t')
                out[c[0]] = (c[4], c[6] if len(c) > 6 else '')
    return out


def parse(d, run):
    cases = []
    meta = cases_of(d)
    for line in open(os.path.join(d, 'check.txt')):
        line = line.rstrip('\n')
        m = OLD.match(line)
        if m:
            res, cid, v, kind, obj, want, got, note = m.groups()
            a = int(obj) if kind == 'planet' else tuple(int(x) for x in obj.split('/'))
            rule, setup = meta.get(cid, ('', note))
            cases.append((cid, rule, setup or note, res, int(v), subj(kind, a), 'level', level(want), level(got)))
            continue
        m = NEW.match(line)
        if m:
            res, cid, kind, args, want, got, note = m.groups()
            if kind == 'record':
                continue
            v, s, field, w, g = new_line(kind, ast.literal_eval(args), want, got)
            if not want.strip():
                w = NOPRED
            cases.append((cid, '', note, res, v, s, field, w, g))
            continue
        m = DESIGNS.match(line)
        if m:
            res, v, which, mp, mf, op, of = m.groups()
            cid = '%s-%s-p%s' % (run.upper().replace('SC', 'SC-'), which, v)
            field = 'foreign_designs' if which == 'designs' else 'foreign_starbase_designs'
            cases.append((cid, '', 'foreign %s known partially / fully' % which, res, int(v),
                          {'kind': 'other_players'}, field,
                          {'partial': int(mp), 'full': int(mf)}, {'partial': int(op), 'full': int(of)}))
            continue
        m = BLOCK.match(line)
        if m:
            res, v, q, model, obs = m.groups()
            o = lit(obs)
            o = o[0] if isinstance(o, tuple) else o
            cid = '%s-block-p%s-p%s' % (run.upper().replace('SC', 'SC-'), v, q)
            cases.append((cid, '', "player %s's knowledge of player %s's player block" % (v, q), res, int(v),
                          {'kind': 'player', 'id': int(q)}, 'player_block', None if model == 'None' else model, o))
    return cases


def start_of(d):
    p = os.path.join(d, 'start.HST')
    return p if os.path.exists(p) else os.path.join(d, 'raw', 'before', 'CB.HST')


def build(ev, out):
    os.makedirs(out, exist_ok=True)
    groups = {}
    for run in sorted(os.listdir(ev)):
        d = os.path.join(ev, run)
        if run in SKIP or not os.path.isdir(d) or not os.path.exists(os.path.join(d, 'check.txt')):
            continue
        h = hashlib.sha256(open(start_of(d), 'rb').read()).hexdigest()
        groups.setdefault(h, []).append(run)
    n = 0
    for h, runs in sorted(groups.items(), key=lambda kv: kv[1][0]):
        name = runs[0]
        d0 = os.path.join(ev, name)
        bxy = os.path.join(d0, 'raw', 'before', 'CB.XY')
        st = B.state(B.dump(start_of(d0)), B.dump(bxy), 'CB', bxy)
        per = {}
        for run in runs:
            for cid, rule, setup, res, v, s, field, w, g in parse(os.path.join(ev, run), name):
                c = per.setdefault(cid, {'rule': rule, 'setup': setup, 'held': True, 'pred': w, 'streams': {}})
                c['held'] = c['held'] and res == 'OK'
                e = {'year': 1, 'kind': 'view', 'viewer': v, 'subject': s, 'equals': {field: g}}
                c['streams'].setdefault('cycles 30000' if 'cycles30000' in run else 'cycles 20000', []).append(e)
        vid = 'SC-' + name[2:]
        vec = {'schema': B.SCHEMA, 'id': vid, 'title': 'scanning run %s' % name,
               'source': {'experiment': 'experiments/sc', 'spec_rules': 'docs/SCANNING.md', 'parity': PARITY,
                          'raw_evidence': 'stars-oracle-apparatus evidence/sc/{%s} (private)' % ','.join(runs)},
               'years': 1, 'random': 'single_stream' if len(runs) == 1 else 'several_streams',
               'streams': len(runs), 'initial_state': st, 'cases': []}
        for cid, c in per.items():
            cs = B.case(cid, ('SCANNING ' + c['rule']).strip(), c['setup'], c['streams'], c['held'], set())
            if c['pred'] is NOPRED:
                cs['tag'] = 'MEASURED'
            else:
                cs['prediction'] = B.json.dumps(c['pred'])
            vec['cases'].append(cs)
        with open(os.path.join(out, name + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        n += 1
    print('sc: %d vectors' % n)
