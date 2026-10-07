"""RD-P turn-time race penalty runs (evidence/rd/rpNN) -> vectors.

Called by build.py for CORPUS rp. Each run is one year from a game whose
player 0 race was edited. The expectations are the year's host-file
changes, including the repaired race, and message ids; the verdict is the
PARITY "Turn-time penalty" row (P1..P10) or the follow-up (P11, P12).
"""
import os, re
import build as B
import build_kx as K

VERDICT = {5: 'stat 15 reset to 0 silently: no message (predicted a penalty)',
           6: 'colonists per resource clamped to 2500 silently: no message (predicted a penalty)',
           7: 'PRT 10 became JOAT silently: no message (predicted a penalty)'}
PARITY = {11: 'docs/PARITY.md "Follow-up: AR spends, growth 0, several players (MEASURED, RD-7, RD-P11, RD-P12)"',
          12: 'docs/PARITY.md "Follow-up: AR spends, growth 0, several players (MEASURED, RD-7, RD-P11, RD-P12)"'}


def build(ev, out):
    os.makedirs(out, exist_ok=True)
    n = 0
    for run in sorted(d for d in os.listdir(ev) if re.fullmatch(r'rp\d+', d)):
        k = int(run[2:])
        res = [l.split()[0] for l in open(os.path.join(ev, run, 'check.txt')) if re.match(r'^(MATCH|MISMATCH)\s', l)]
        held = all(r == 'MATCH' for r in res)
        verdict = VERDICT.get(k, 'held')
        vid = 'RD-P%d' % k
        vec = K.chained(vid, 'turn-time race penalty P%d' % k, {'run': [os.path.join(ev, run)]},
                        (held, 'CONFIRMED' if held else 'MEASURED', verdict, '', 'RACES turn-time penalty'))
        vec['source'] = {'experiment': 'experiments/rd', 'spec_rules': 'docs/RACES.md',
                         'parity': PARITY.get(k, 'docs/PARITY.md "Turn-time penalty (RD-P1..RD-P10)"'),
                         'raw_evidence': 'stars-oracle-apparatus evidence/rd/%s (private)' % run}
        with open(os.path.join(out, run + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        n += 1
        print('%s: %s, %d expectations' % (vid, 'held' if held else 'missed', len(vec['cases'][0]['expect'])))
    print('rp: %d vectors' % n)
