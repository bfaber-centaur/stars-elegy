"""RD-P turn-time race penalty runs (evidence/rd/rpNN) -> vectors.

Called by build.py for CORPUS rp. Each run is one year from a game whose
player 0 race was edited. The expectations are the year's host-file
changes, including the repaired race, and message ids; the verdict is the
PARITY "Turn-time penalty" row (P1..P10), the follow-up (P11, P12) or
Round 3 (P13..P21, MEASURED).
"""
import os, re
import build as B
import build_kx as K

VERDICT = {5: 'stat 15 reset to 0 silently: no message (predicted a penalty)',
           6: 'colonists per resource clamped to 2500 silently: no message (predicted a penalty)',
           7: 'PRT 10 became JOAT silently: no message (predicted a penalty)',
           21: 'the committed candidate (a new 0x117 every year while flagged) was ruled out: no new 0x117, races unchanged'}
# Round 3 (RD-P13..P21) is MEASURED in PARITY: one pinned run each.
ROUND3 = 13
MISSED = {21}
PARITY = {11: 'docs/PARITY.md "Follow-up: AR spends, growth 0, several players (MEASURED, RD-7, RD-P11, RD-P12)"',
          12: 'docs/PARITY.md "Follow-up: AR spends, growth 0, several players (MEASURED, RD-7, RD-P11, RD-P12)"'}


def build(ev, out):
    os.makedirs(out, exist_ok=True)
    n = 0
    for run in sorted(d for d in os.listdir(ev) if re.fullmatch(r'rp\d+', d)):
        k = int(run[2:])
        res = [l.split()[0] for l in open(os.path.join(ev, run, 'check.txt')) if re.match(r'^(MATCH|MISMATCH)\s', l)]
        held = all(r == 'MATCH' for r in res) and k not in MISSED
        verdict = VERDICT.get(k, 'held')
        vid = 'RD-P%d' % k
        vec = K.chained(vid, 'turn-time race penalty P%d' % k, {'run': [os.path.join(ev, run)]},
                        (held, 'CONFIRMED' if held and k < ROUND3 else 'MEASURED', verdict, '', 'KERNEL race budget'))
        par = PARITY.get(k, 'docs/PARITY.md "Turn-time penalty (RD-P1..RD-P10)"' if k < ROUND3 else
                         'docs/PARITY.md "Round 3: the remaining BINARY-ONLY rules (MEASURED, RW08, RD-P13..RD-P21)"')
        vec['source'] = {'experiment': 'experiments/rd', 'spec_rules': 'docs/KERNEL.md "Production" (race budget)',
                         'parity': par,
                         'raw_evidence': 'stars-oracle-apparatus evidence/rd/%s (private)' % run}
        with open(os.path.join(out, run + '.json'), 'w') as f:
            B.json.dump(vec, f, indent=1)
            f.write('\n')
        n += 1
        print('%s: %s, %d expectations' % (vid, 'held' if held else 'missed', len(vec['cases'][0]['expect'])))
    print('rp: %d vectors' % n)
