#!/usr/bin/env python3
"""TP: Mystery Trader trades with computer players' planets (OBJECTS.md "Computer players' planets").

Base: the AP-001 game after year 2401 (apparatus evidence/ai/ap/run001/y2401/raw/after): human player 0
(homeworld 39 at 1243,1447), expert Turindrone player 1 (homeworld 108 at 1669,1246), expert Automitron
player 2 (homeworld 80 at 1512,1440). One pinned year (2402) per run. The game's fleets and its six
wormholes are kept; three Traders are added, each starting on one homeworld and moving 64 ly along x (warp
8), so each ends within 100 ly of its own homeworld only (the homeworlds are 250+ ly apart).

  python3 experiments/tp/gen.py BASE_DUMP OUTDIR   # BASE_DUMP: combatlab dump of the base AP01.HST
  python3 experiments/tp/gen.py --list

Predictions restate OBJECTS.md (BINARY-ONLY) and were written before the runs.
"""
import os, re, sys

TRADERS = ('thing trader 0 1669 1246 1369 1246 8 item 1\n'      # part bit 0 (Multi Cargo Pod) at Turindrone
           'thing trader 1 1512 1440 1212 1440 8\n'             # research at Automitron
           'thing trader 2 1243 1447 1543 1447 8 item 1\n')     # part bit 0 at the human player
SURFACE = ('planetset 108 fe=3000 bo=2000 ge=2000\n'
           'planetset 80 fe=4000 bo=4000 ge=4000\n'
           'planetset 39 fe=3000 bo=2000 ge=2000\n')
RUNS = {
    'tp001': '',
    'tp002': 'mt 1 0001\n' + ''.join('tech 2 %s 25\n' % f for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio')),
}
CASES = [
    ('TP-001-A', 'Turindrone (expert) homeworld 108, 7,000 kT on the surface, Trader 0 offering a part it lacks '
     '(bit 0)', 'Turindrone\'s part word 0000 -> 0001; planet 108 loses all its surface minerals (a scrapped '
     'Scout may add a few kT afterwards: each mineral at most 20)', 'no trade (only fleets trade)'),
    ('TP-001-B', 'Automitron (expert) homeworld 80, 12,000 kT, tech 10,10,10,13,10,10 (sum 63), Trader 1 offering '
     'research', 'tech 12,11,11,13,11,11 (lowest field +1, six times); price 5,000 kT from germanium first: '
     'germanium 0, boranium down by the rest, ironium untouched', 'no trade; or ironium paid first'),
    ('TP-001-C', 'human homeworld 39, 7,000 kT, Trader 2 offering a part', 'no trade: part word 0000, surface '
     'not taken', 'traded like a computer planet'),
    ('TP-002-A', 'as TP-001-A, but Turindrone already owns bit 0', 'one new bit among 1-12 (bit 12 gives only the '
     'bit); all surface minerals taken', 'nothing (offered part owned)'),
    ('TP-002-B', 'as TP-001-B, but Automitron\'s tech is 25 in every field (sum 150)', 'nothing: tech unchanged, '
     'surface not reduced by 5,000', 'six levels anyway'),
    ('TP-002-C', 'as TP-001-C', 'no trade', ''),
]


def main():
    if sys.argv[1:] == ['--list']:
        print('| Case | Setup | Predicted | Rules out |\n|---|---|---|---|')
        for c in CASES:
            print('| %s | %s | %s | %s |' % c)
        return
    dump, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    raw = [re.search(r'raw=([0-9a-f]{36})', l).group(1) for l in open(dump)
           if ' thing id=' in l and 'type=wormhole' in l and '.HST ' in l]
    keep = ''.join('thing raw %s\n' % h for h in raw)
    for name, extra in RUNS.items():
        spec = '# %s: Trader trades with computer planets (experiments/tp/gen.py)\nkeepfleets\n' % name.upper()
        open(os.path.join(out, name + '.spec'), 'w').write(spec + SURFACE + extra + keep + TRADERS)
        print('wrote', os.path.join(out, name + '.spec'))


if __name__ == '__main__':
    main()
