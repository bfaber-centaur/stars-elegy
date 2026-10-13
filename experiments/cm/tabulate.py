#!/usr/bin/env python3
"""List every stored 0x02b-0x02e message in the preserved oracle evidence.

CM-1 reads no new run. It decodes the player-message block of every dump
under an apparatus `evidence/` tree with tools/fleetlab/events.py and
prints one line per distinct message:

  SOURCE KIND [fleet, amount lo, amount hi, cargo type, loc 1, loc 2] WHERE

Messages with the same slots in the same case are printed once. SAME
maps runs that repeat another run's setup onto one source, so a repeated
case counts once. WHERE names the location form from the two location
slots (planet, fleet, object or x,y).

  python3 experiments/cm/tabulate.py APPARATUS/evidence
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools', 'fleetlab'))
import events  # noqa: E402

KINDS = {0x02b: '0x02b', 0x02c: '0x02c', 0x02d: '0x02d', 0x02e: '0x02e'}

# Runs that repeat another run's fleets: counted once, under the right side.
SAME = [
    (r'^et1/et1b|^et2/et2b|^et2/et2c|^et2(?=/run)', 'et1+et2'),
    (r'^et1(?=/run)', 'et1+et2'),
    (r'^tk4/tk30[12]', 'tk4/tk301+tk302'),
    (r'^xf/(explore/)?wp1', 'xf/wp1'),
    (r'^t15/run3/load-', 't15/run3/load'),
    (r'^kb/raw/KB4A', 'kb/KB4A'),
    # RG-002's game: the record under test and RM runs started from the same
    # game. Never counted as support.
    (r'^rg002/|^rm/', 'RG-002 game (#403, under test)'),
]


def source(rel):
    for pat, name in SAME:
        if re.search(pat, rel):
            return name
    return re.sub(r'/(run|raw)\b.*', '', rel)


def where(a, b):
    if a == 0xFFFF:
        return f'fleet {b & 0x7FFF}' if b & 0x8000 else f'planet {b}'
    if a == 0xFFFE:
        return f'object {b:#06x}'
    return f'x,y {a},{b}'


def main(root):
    files = subprocess.run(['grep', '-rlE', 'events raw=|block type=12', root],
                           capture_output=True, text=True).stdout.split()
    seen = set()
    for f in sorted(files):
        rel = os.path.relpath(f, root)
        for _, player, block in events.blocks(f):
            msgs, complete = events.decode(block)
            if not complete:
                print(f'# incomplete block: {rel} M{player}')
            for kind, _, slots in msgs:
                if kind not in KINDS:
                    continue
                key = (source(rel), player, kind, tuple(slots))
                if key in seen:
                    continue
                seen.add(key)
                print(f'{key[0]} M{player} {KINDS[kind]} {slots} {where(slots[4], slots[5])}')


if __name__ == '__main__':
    main(sys.argv[1])
