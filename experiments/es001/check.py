#!/usr/bin/env python3
"""Compare ES-001 predictions with what the original client showed.

  python3 experiments/es001/check.py [predictions.tsv results.tsv]

results.tsv holds the values read from the client's screens (the
screenshots are private evidence, stars-oracle-apparatus
evidence/es/es-001/). Distances are compared as numbers (the waypoint tile
writes "Light Years"); the population popup's growth sentence is compared
by its numbers. T rows are the fleet report's ETA column, which shows the
next waypoint's travel time in short form ("3y"), red when that leg's
fuel estimate exceeds the fleet's fuel.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
pred_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'predictions.tsv')
res_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'results.tsv')


def rows(p):
    lines = [l.rstrip('\n').split('\t') for l in open(p)]
    return lines[1:]


pred = {(r[0], r[2]): r[3] for r in rows(pred_path)}
by_case = {}
for (c, item), v in pred.items():
    by_case.setdefault(c, {})[item] = v


def norm(item, v):
    if item.endswith('distance'):
        return re.sub(r'\s*(l\.y\.|Light Years)$', '', v)
    if item.startswith('planet') and 'population' in item:
        return re.sub(r'^(your population on \S+ )?(will )?', '', v.strip('().'))
    return v


ok = bad = 0
for case, item, obs, where in rows(res_path):
    if case.startswith('T'):
        f = int(case[1:])
        tt = by_case['F%02d-w1' % f]['fleet %d wp 1 travel time' % f]
        fuel = by_case['F%02d-w1' % f]['fleet %d wp 1 est fuel usage' % f]
        y = re.match(r'(\d+) year', tt)
        exp = (y.group(1) + 'y' if y else tt) + (' (red)' if '(red)' in fuel or tt == 'Never' else '')
    else:
        exp = pred[(case, item)]
    good = norm(item, exp) == norm(item, obs)
    ok += good
    bad += not good
    if not good:
        print('MISMATCH %s %s: predicted %r, observed %r' % (case, item, exp, obs))
print('%d match, %d differ' % (ok, bad))
sys.exit(1 if bad else 0)
