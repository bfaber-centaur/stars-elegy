#!/usr/bin/env python3
"""Mark the columns CS-003 observed as CONFIRMED in data/components.json.

  python3 experiments/cs003/apply.py

Reads predictions.tsv (row name and columns per case) and results.tsv
(match / not discriminated per case). A column becomes observed when a
matching case names it. EXTRA lists the columns observed by earlier
corpora (CB-000 designer moves; TK T-18). Rows whose binary_only list
becomes empty get status CONFIRMED.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, '..', '..', 'data', 'components.json')

# columns observed by earlier corpora, not by a CS-003 case
EXTRA = {
    # CB-000: every engine's scout showed moves = (battle_warp - 4 [+ 1 Enigma] + 2)/4 squares (all 16 engines)
    **{('engine', n): ['battle_warp'] for n in (
        "Settler's Delight", 'Quick Jump 5', 'Fuel Mizer', 'Long Hump 6', 'Daddy Long Legs 7', 'Alpha Drive 8',
        'Trans-Galactic Drive', 'Interspace-10', 'Enigma Pulsar', 'Trans-Star 10', 'Radiating Hydro-Ram Scoop',
        'Sub-Galactic Fuel Scoop', 'Trans-Galactic Fuel Scoop', 'Trans-Galactic Super Scoop',
        'Trans-Galactic Mizer Scoop', 'Galaxy Scoop')},
    # CB-000 (one Enigma scout: 2 1/4) and CS-003-D-A/-E (moves of 4 Enigmas; Enigma + Alien Miner):
    # the Enigma Pulsar's half step, through (Enigma Pulsars + Alien Miners + 1)/2
    ('engine', 'Enigma Pulsar'): ['battle_warp', 'battle_speed_half_steps'],
    # TK-005 T-18: one MCM frigate on P' = 100 killed 3 (2% would be 2): the minimum 3 units
    ('beam', 'Multi Contained Munition'): ['bomb_min_kill'],
    # OB-002: Mini Mine Layer with two Mine Dispenser 40 laid 160
    ('hull', 'Mini Mine Layer'): ['mine_layer_multiplier'],
}


def main():
    table = json.load(open(PATH))
    res = {l.split('\t')[0]: l.split('\t')[1] for l in open(os.path.join(HERE, 'results.tsv')).read().splitlines()[1:]}
    seen = {}
    for line in open(os.path.join(HERE, 'predictions.tsv')).read().splitlines()[1:]:
        cid, row, cols = line.split('\t')[:3]
        if res.get(cid) != 'match':
            continue
        for c in cols.split(','):
            seen.setdefault(row, set()).add(c.strip())
    for (cat, name), cols in EXTRA.items():
        seen.setdefault(name, set()).update(cols)
    changed = 0
    for r in table['items']:
        if not r['binary_only']:
            continue
        left = [c for c in r['binary_only'] if c.split('.', 1)[1] not in seen.get(r['name'], ())]
        if left != r['binary_only']:
            changed += 1
        r['binary_only'] = left
        r['status'] = 'CONFIRMED' if not left else 'BINARY-ONLY'
    text = open(PATH).read()
    head = text[:text.index(' "items": [')]
    with open(PATH, 'w') as fh:
        fh.write(head + ' "items": [\n')
        fh.write(',\n'.join('  ' + json.dumps(r, ensure_ascii=False) for r in table['items']))
        fh.write('\n ]\n}\n')
    n = {}
    for r in table['items']:
        n[r['status']] = n.get(r['status'], 0) + 1
    print('rows changed', changed, n)
    for r in table['items']:
        if r['binary_only']:
            print('still BINARY-ONLY:', r['category'], r['name'], r['binary_only'])


if __name__ == '__main__':
    main()
