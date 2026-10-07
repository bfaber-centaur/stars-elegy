"""Observed-turn corpora with curated verdicts -> vectors.

Called by build.py for CORPUS cb7, tk3, sl or gt. Each setup is a start file
and pinned runs (one per stream, chained for second years). A vector has one
case whose expectations are each year's observed changes (build_kx.observe:
battles, host-file changes, message ids, score records). The verdict is the
setup's result from PARITY.md, or the check lines of experiments/gt/check.py.
"""
import os, re
import build as B
import build_kx as K

# corpus: [(setup dir, vector id, title, prediction held, tag, verdict, spec, parity)]
R7 = 'docs/PARITY.md "Round 7 (CB-048, CB-049) and scanning SC-035/SC-036"'
TK3 = 'docs/PARITY.md "Round 3 (TK-201 to TK-203)"'
SL = 'docs/PARITY.md "Ship launch (SL-01 to SL-12)"'
SLNOTE = '; both SL races were illegal and degraded before production (resources only, PARITY)'
SETUPS = {
    'cb7': [
        ('cb048', 'CB-048', 'Mystery Trader items from battle: thirty one-ship Mini Morph fleets', True, 'CONFIRMED',
         'one item in 10 of 20 streams; the reconciled chance rule and the replay named every gaining stream', 'docs/COMBAT.md', R7),
        ('cb048-ctl', 'CB-048-ctl', 'CB-048 control: the same 30 Morphs in one fleet', True, 'CONFIRMED',
         'one item in 1 of 12 streams', 'docs/COMBAT.md', R7),
        ('cb049', 'CB-049', 'battle movement: seven moving stacks on tactics 1 to 4', True, 'MEASURED',
         'recorded, replay pending: every hit replayed in 5 streams; one hit at cycles 7000 is open', 'docs/COMBAT.md', R7),
        ('sc035', 'SC-035', 'scanning after bombing a colony to empty', True, 'CONFIRMED',
         'the bomber owner got a normal report of the emptied planet; position only at the control planet',
         'docs/SCANNING.md', R7),
        ('sc036', 'SC-036', 'designs and player blocks after a three-player battle', True, 'CONFIRMED',
         "each participant held the other two players' designs in full and their player blocks", 'docs/SCANNING.md', R7),
    ],
    'tk3': [
        ('tk201', 'TK-201', 'order across planets, unloads, emptying planets, colonize failures, homeworld mark (two years)',
         True, 'CONFIRMED', 'every prediction held', 'docs/TAKEOVER.md', TK3),
        ('tk202', 'TK-202', 'mines never go negative; several-fleet bombing messages', True, 'CONFIRMED',
         'every prediction held; the installation outcome is random (10 distinct outcomes in 12 streams)', 'docs/TAKEOVER.md', TK3),
        ('tk203', 'TK-203', 'tech from scrapping at a starbase', True, 'CONFIRMED', 'every prediction held', 'docs/TAKEOVER.md', TK3),
    ],
    'sl': [
        ('sl-routes', 'SL-routes', 'SL-01..07: new fleets, numbering, route warps (two years)', True, 'CONFIRMED',
         '28 of 28 route warps and every new-fleet value as predicted' + SLNOTE, 'docs/ORDERS.md', SL),
        ('sl-limit-a', 'SL-limit-a', 'SL-08/09: the 512-fleet limit', True, 'CONFIRMED', 'as predicted' + SLNOTE, 'docs/ORDERS.md', SL),
        ('sl-limit-a-ctl', 'SL-limit-a-ctl', 'SL-08/09 control', True, 'CONFIRMED', 'control' + SLNOTE, 'docs/ORDERS.md', SL),
        ('sl-limit-b', 'SL-limit-b', 'SL-10: the 512-fleet limit with fleets at the planet', True, 'CONFIRMED',
         'as predicted' + SLNOTE, 'docs/ORDERS.md', SL),
        ('sl-limit-b-ctl', 'SL-limit-b-ctl', 'SL-10 control', True, 'CONFIRMED', 'control' + SLNOTE, 'docs/ORDERS.md', SL),
        ('sl-limit-b300', 'SL-limit-b300', 'SL-10 follow-up: merged damage at 300 units', True, 'CONFIRMED',
         'as predicted' + SLNOTE, 'docs/ORDERS.md', SL),
        ('sl-limit-b300-ctl', 'SL-limit-b300-ctl', 'SL-10 follow-up control', True, 'CONFIRMED', 'control' + SLNOTE,
         'docs/ORDERS.md', SL),
        ('sl-starbases', 'SL-starbases', 'SL-11/12: default orders, replacing a starbase (two years)', True, 'CONFIRMED',
         'as predicted; a Space Dock built a 574 kT Mini-Miner (LEGACY BUG: no dock-size check)' + SLNOTE,
         'docs/ORDERS.md', SL),
        ('sl-starbases-ctl', 'SL-starbases-ctl', 'SL-11/12 control (two years)', True, 'CONFIRMED',
         'control; an AR planet with no mines and no miner gained minerals (not predicted)' + SLNOTE, 'docs/ORDERS.md', SL),
    ],
}


def streams_of(sd):
    out = {}
    for r in sorted(os.listdir(sd)):
        m = re.fullmatch(r'run-(\d+)', r)
        if not m:
            continue
        chain = [os.path.join(sd, r)]
        for y2 in (os.path.join(sd, 'run-y2-' + m.group(1)), os.path.join(sd, 'year2', r)):
            if os.path.isdir(y2):
                chain.append(y2)
        out['cycles ' + m.group(1)] = chain
    return out


def write(out, name, vec, compact=False):
    with open(os.path.join(out, name + '.json'), 'w') as f:
        if compact:
            B.json.dump(vec, f, separators=(',', ':'))
        else:
            B.json.dump(vec, f, indent=1)
        f.write('\n')


def build(corpus, ev, out):
    os.makedirs(out, exist_ok=True)
    if corpus == 'gt':
        return build_gt(ev, out)
    for setup, vid, title, held, tag, verdict, spec, parity in SETUPS[corpus]:
        sd = os.path.join(ev, setup)
        streams = streams_of(sd)
        vec = K.chained(vid, title, streams, (held, tag, verdict, '', spec))
        exp = {'tk3': 'tk', 'sl': 'sl'}.get(corpus) or ('sc' if setup.startswith('sc') else re.sub(r'-ctl$', '', setup))
        vec['source'] = {'experiment': 'experiments/' + exp,
                         'spec_rules': spec, 'parity': parity,
                         'raw_evidence': 'stars-oracle-apparatus evidence/%s/%s (private)' % (corpus, setup)}
        write(out, setup, vec, compact=corpus in ('cb7', 'sl'))
        print('%s: %d streams, %d years, %d expectations' % (vid, len(streams), vec['years'],
                                                             len(vec['cases'][0]['expect'])))


def build_gt(ev, out):
    for run in sorted(d for d in os.listdir(ev) if re.fullmatch(r'gt\d+', d)):
        sd = os.path.join(ev, run)
        lines = [l.strip() for l in open(os.path.join(sd, 'check.txt'))
                 if re.match(r'^GT-\S+ \S+ (HELD|MISSED|MISS|OBSERVED|CONTRADICTED)', l)]
        res = [l.split()[2].rstrip(':') for l in lines]
        rules = sorted(set(l.split()[1] for l in lines), key=lambda r: int(re.sub(r'\D', '', r) or 0))
        held = all(r in ('HELD', 'OBSERVED') for r in res)
        tag = 'CONFIRMED' if all(r == 'HELD' for r in res) else 'MEASURED'
        vid = 'GT-' + run[2:]
        vec = K.chained(vid, 'stargates %s' % vid, {'run': [sd]}, (held, tag, ' | '.join(lines), '',
                                                                   'OBJECTS ' + ', '.join(rules)))
        vec['source'] = {'experiment': 'experiments/gt', 'spec_rules': 'docs/OBJECTS.md "Stargates"',
                         'parity': 'docs/PARITY.md "Stargates"',
                         'raw_evidence': 'stars-oracle-apparatus evidence/gt/%s (private)' % run}
        write(out, run, vec)
        print('%s: %s, %d expectations' % (vid, tag, len(vec['cases'][0]['expect'])))
