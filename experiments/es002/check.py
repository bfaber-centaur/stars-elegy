#!/usr/bin/env python3
"""Compare ES-002 predictions (predictions.tsv, expect.tsv) with what the
original client and host showed (results.tsv).

  python3 experiments/es002/check.py

Screenshots are private evidence (stars-oracle-apparatus
evidence/es/es-002/). Distances are compared as numbers (the waypoint tile
writes "Light Years"). predictions.tsv was committed before the run; the
one miss (G8: F07-w1 travel time and T07) is kept as a miss here. Rerun
predict.py with the .M1 dump to get the corrected model's "Uncertain".
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def rows(p):
    return [l.rstrip('\n').split('\t') for l in open(os.path.join(HERE, p))][1:]


pred = {(r[0], r[2]): r[3] for r in rows('predictions.tsv')}
pred.update({(r[0], r[1]): r[2] for r in rows('expect.tsv')})


def norm(item, v):
    if item.endswith('distance'):
        return re.sub(r'\s*(l\.y\.|Light Years)$', '', v)
    return v


ok = bad = 0
for case, item, obs, where in rows('results.tsv'):
    exp = pred[(case, item)]
    if norm(item, exp) == norm(item, obs):
        ok += 1
    else:
        bad += 1
        print('MISMATCH %s %s: predicted %r, observed %r' % (case, item, exp, obs))
print('%d match, %d differ' % (ok, bad))
sys.exit(1 if bad else 0)
