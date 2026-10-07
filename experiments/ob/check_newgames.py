#!/usr/bin/env python3
"""OB-006: compare wormholes in new games (tools/fleetlab/new-game output) with the O-27 predictions.

    python3 experiments/ob/check_newgames.py NGDIR     # NGDIR/<name>/after.dump for each NEWGAMES entry
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv, argv = sys.argv[:1], sys.argv          # gen.py reads sys.argv only in main()
from gen import NEWGAMES, PAIRS                   # noqa: E402


def main():
    root = argv[1]
    for g in NEWGAMES:
        path = os.path.join(root, g['name'], 'after.dump')
        if not os.path.exists(path):
            print('%-12s MISSING' % g['id'])
            continue
        ends = []
        for line in open(path):
            if '.HST thing ' in line and 'type=wormhole' in line:
                f = dict(re.findall(r'(\w+)=(\S+)', line))
                ends.append((int(f['num']), int(f['class']), int(f['years']), int(f['partner'])))
        pairs = len(ends) // 2
        paired = all(any(e[0] == o[3] and o[0] == e[3] for o in ends) for e in ends)
        classes = sorted({e[1] for e in ends})
        years = sorted({e[2] for e in ends})
        if g['events']:
            lo, hi = PAIRS[g['size']]
            ok = lo <= pairs <= hi and paired and set(classes) <= {0, 1, 2} and years in ([], [0])
        else:
            ok = not ends
        print('%-12s %-6s pairs=%d classes=%s years=%s paired=%s' % (
            g['id'], 'HELD' if ok else 'CONTRADICTED', pairs, classes, years, paired))


if __name__ == '__main__':
    main()
