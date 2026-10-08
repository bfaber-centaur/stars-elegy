"""MF minefield corpus -> vectors. Called by build.py for CORPUS mf.

Each MF run's check.txt gives one verdict line per case (HELD,
CONTRADICTED, OBSERVED = recorded without an exact prediction) followed by
prose detail. A vector holds one run (its -cNNNNN repeats are extra
streams) with one case whose expectations are the observed year: host-file
changes including minefields, and message ids. The per-case verdict lines
are kept in `verdict`.
"""
import hashlib, os, re
import build as B
import build_kx as K


# Runs whose OBSERVED lines the MF owner compared by hand with the predictions
# committed before the run (789bffa): all held. check.py's det kind prints
# observations without comparing them. MF-07sd's design learning is not in
# check.txt: player 1's designs 2 and 4 appear in full in player 0's file.
HAND_HELD = {'mf07', 'mf07f', 'mf07sd'}
# Runs whose fleets cross a field at a speed with a stop chance (OBJECTS.md
# "Minefields": each ly travelled in a field is a draw). Where a fleet stops,
# what it carries and its damage, and the salvage where it stopped, are those
# draws: the moving fleets and salvage are samples in every stream. In a
# single-stream run the fields' mine counts are too (every stop is paid by a
# field, MF-4).
DRAWN = {'mf01', 'mf02', 'mf03h', 'mf03s', 'mf04', 'mf04b', 'mf04d', 'mf05b', 'mf09h', 'mf09s', 'mf14', 'mf15'}
# PARITY records MF-14 and MF-15 as MEASURED: one pinned year each.
MEASURED_ONLY = {'mf14', 'mf15'}
NOTES = {'mf13b': 'the object at 1400,1400 is salvage: a packet-type object with packet-warp field 0 is salvage '
                  'whatever its destination, and its loss of 10% is salvage decay (BINARY-ONLY: OBJECTS.md "Salvage")'}
HAND_NOTE = ('held: every value compared by hand with the predictions committed before the run '
             '(stars-oracle-apparatus evidence/mf/README.md verdict note)')


def start_of(d):
    p = os.path.join(d, 'start.HST')
    return p if os.path.exists(p) else os.path.join(d, 'raw', 'before', 'CB.HST')


def mark_drawn(case, st0, single):
    moved = set()
    f0 = {(f['owner'], f['id']): f for f in st0['fleets']}
    for e in case['expect']:
        if e['kind'] == 'fleet' and ('x' in e['equals'] or 'y' in e['equals']):
            moved.add((e['owner'], e['id']))
        elif e['kind'] == 'fleet_gone':
            moved.add((e['owner'], e['id']))
    out = []
    for e in case['expect']:
        k = e['kind']
        if (k in ('fleet', 'fleet_gone') and (e['owner'], e['id']) in moved) or k == 'salvage_at' or \
                (single and k == 'minefield'):
            e = dict(e, sample=True)
        out.append(e)
    case['expect'] = out


def build(ev, out):
    os.makedirs(out, exist_ok=True)
    groups = {}
    for run in sorted(os.listdir(ev)):
        d = os.path.join(ev, run)
        if not os.path.exists(os.path.join(d, 'check.txt')):
            continue
        h = hashlib.sha256(open(start_of(d), 'rb').read()).hexdigest()
        groups.setdefault(h, []).append(run)
    n = 0
    for runs in sorted(groups.values()):
        name = runs[0]
        lines = [l.strip() for l in open(os.path.join(ev, name, 'check.txt')) if re.match(r'^MF-\S+ (HELD|CONTRADICTED|OBSERVED)', l)]
        if name in HAND_HELD:
            lines = [l.replace(' OBSERVED', ' HELD', 1) for l in lines] + [HAND_NOTE]
        res = [l.split()[1] for l in lines if l.startswith('MF-')]
        rules = sorted(set(re.findall(r'\((MF-\d+)\)', ' '.join(lines))))
        held = 'CONTRADICTED' not in res
        tag = 'CONFIRMED' if all(r == 'HELD' for r in res) and name not in MEASURED_ONLY else 'MEASURED'
        streams = {}
        for r in runs:
            m = re.search(r'-c(\d+)$', r)
            streams['cycles ' + (m.group(1) if m else '20000')] = [os.path.join(ev, r)]
        vid = 'MF-' + name[2:]
        vec = K.chained(vid, 'MF %s' % name[2:], streams, (held, tag, ' | '.join(lines), '', 'OBJECTS ' + ', '.join(rules)))
        if name in DRAWN:
            mark_drawn(vec['cases'][0], vec['initial_state'], len(streams) == 1)
        if name in NOTES:
            vec['cases'][0]['verdict'] += ' | ' + NOTES[name]
        vec['source'] = {'experiment': 'experiments/mf', 'spec_rules': 'docs/OBJECTS.md "Minefields"',
                         'parity': 'docs/PARITY.md "Minefield lane (MF-1..MF-13)"',
                         'raw_evidence': 'stars-oracle-apparatus evidence/mf/{%s} (private)' % ','.join(runs)}
        with open(os.path.join(out, name + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        n += 1
        print('%s: %d streams, %s' % (vid, len(streams), tag))
    print('mf: %d vectors' % n)
