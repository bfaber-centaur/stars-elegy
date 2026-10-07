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
HAND_NOTE = ('held: every value compared by hand with the predictions committed before the run '
             '(stars-oracle-apparatus evidence/mf/README.md verdict note)')


def start_of(d):
    p = os.path.join(d, 'start.HST')
    return p if os.path.exists(p) else os.path.join(d, 'raw', 'before', 'CB.HST')


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
        tag = 'CONFIRMED' if all(r == 'HELD' for r in res) else 'MEASURED'
        streams = {}
        for r in runs:
            m = re.search(r'-c(\d+)$', r)
            streams['cycles ' + (m.group(1) if m else '20000')] = [os.path.join(ev, r)]
        vid = 'MF-' + name[2:]
        vec = K.chained(vid, 'MF %s' % name[2:], streams, (held, tag, ' | '.join(lines), '', 'OBJECTS ' + ', '.join(rules)))
        vec['source'] = {'experiment': 'experiments/mf', 'spec_rules': 'docs/OBJECTS.md "Minefields"',
                         'parity': 'docs/PARITY.md "Minefield lane (MF-1..MF-13)"',
                         'raw_evidence': 'stars-oracle-apparatus evidence/mf/{%s} (private)' % ','.join(runs)}
        with open(os.path.join(out, name + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        n += 1
        print('%s: %d streams, %s' % (vid, len(streams), tag))
    print('mf: %d vectors' % n)
