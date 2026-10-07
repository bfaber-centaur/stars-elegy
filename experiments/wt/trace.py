#!/usr/bin/env python3
"""Follow wormholes, Mystery Traders, fleets and player tech year by year.

  python3 experiments/wt/trace.py OUTDIR            # OUTDIR from tools/fleetlab/years
  python3 experiments/wt/trace.py RUNDIR [RUNDIR...]  # pinned-turn outputs, in order
  python3 experiments/wt/trace.py --json OUTDIR

Year 0 is the start file (the first run's before.dump); each later year is a
run's after.dump. Only the host file's lines are read. Wormhole lines show
each end's move since the year before (dx, dy) and flag `JUMP?` when either
axis moved more than 12 ly or the years count went back to 0 (the OB-005
jiggle bound and the jump rule in docs/OBJECTS.md); fleets show position,
ships, damage words, cargo and fuel; players show tech levels and their
Mystery Trader item mask. A year whose wormhole moves all repeat the year
before's is flagged `SAME STREAM?`: tools/fleetlab/years then probably
replayed one random stream (see its header).
"""
import json, os, re, sys

KV = re.compile(r'(\w+)=(\S+)')


def host_lines(path):
    """Lines of a combatlab dump that belong to the host file."""
    out = []
    for line in open(path):
        head, _, rest = line.partition(' ')
        if head.endswith('.HST'):
            out.append(rest.rstrip('\n'))
    return out


def parse(path):
    st = dict(year=None, worms={}, traders={}, fleets={}, players={})
    for line in host_lines(path):
        kv = dict(KV.findall(line))
        if line.startswith('file '):
            st['year'] = int(kv['year'])
        elif line.startswith('thing '):
            num = int(kv['num'])
            if kv['type'] == 'wormhole':
                st['worms'][num] = dict(x=int(kv['x']), y=int(kv['y']), cls=int(kv['class']),
                                        years=int(kv['years']), partner=int(kv['partner']),
                                        seen=kv['seen'], seen2=kv['seen2'], w14=kv['w14'], w16=kv['w16'])
            elif kv['type'] == 'trader':
                dx, dy = kv['dest'].split(',')
                st['traders'][num] = dict(x=int(kv['x']), y=int(kv['y']), dest=(int(dx), int(dy)),
                                          warp=int(kv['warp']), w10=kv['w10'], met=kv['met'],
                                          item=kv['item'], w16=kv['w16'])
        elif line.startswith('fleet '):
            key = (int(kv['owner']), int(kv['id']))
            st['fleets'][key] = dict(x=int(kv['x']), y=int(kv['y']), ships=kv['ships'], cargo=kv['cargo'],
                                     fuel=int(kv['fuel']),
                                     dmg=' '.join('%s=%s' % (k, v) for k, v in kv.items() if k.startswith('dmg')))
        elif line.startswith('player ') and 'energy=' in line:
            p = int(line.split()[1])
            st['players'][p] = dict(tech=[int(kv[k]) for k in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio')],
                                    mt=kv.get('mt', '?'),
                                    accum=[int(x) for x in kv.get('accum', '0,0,0,0,0,0').split(',')])
    return st


def runs(args):
    """Expand a `years` OUTDIR into its y1..yN run dirs."""
    out = []
    for a in args:
        ys = sorted((d for d in os.listdir(a) if re.fullmatch(r'y\d+', d)), key=lambda d: int(d[1:])) \
            if os.path.isdir(a) and not os.path.exists(os.path.join(a, 'after.dump')) else []
        out += [os.path.join(a, d) for d in ys] if ys else [a]
    return out


def trace(dirs):
    states = [parse(os.path.join(dirs[0], 'before.dump'))]
    states += [parse(os.path.join(d, 'after.dump')) for d in dirs]
    return states


def moves(prev, st):
    return tuple((n, w['x'] - prev['worms'][n]['x'], w['y'] - prev['worms'][n]['y'])
                 for n, w in sorted(st['worms'].items()) if n in prev['worms'])


def show(states):
    prev, last = None, None
    for st in states:
        mv = moves(prev, st) if prev else None
        flag = '  SAME STREAM?' if mv and mv == last else ''
        last = mv
        print('== year %s%s' % (st['year'], flag))
        for p, v in sorted(st['players'].items()):
            print('  player %d tech=%s mt=%s' % (p, ','.join(map(str, v['tech'])), v['mt']))
        for n, w in sorted(st['worms'].items()):
            note = ''
            if prev and n in prev['worms']:
                o = prev['worms'][n]
                dx, dy = w['x'] - o['x'], w['y'] - o['y']
                jump = abs(dx) > 12 or abs(dy) > 12 or (w['years'] == 0 and o['years'] > 0)
                note = ' d=(%+d,%+d)%s' % (dx, dy, ' JUMP?' if jump else '')
            elif prev:
                note = ' (new)'
            print('  wormhole %d (%d,%d) class=%d years=%d partner=%d seen=%s seen2=%s%s'
                  % (n, w['x'], w['y'], w['cls'], w['years'], w['partner'], w['seen'], w['seen2'], note))
        if prev:
            for n in sorted(set(prev['worms']) - set(st['worms'])):
                print('  wormhole %d gone' % n)
        for n, t in sorted(st['traders'].items()):
            note = ''
            if prev and n in prev['traders']:
                o = prev['traders'][n]
                note = ' d=(%+d,%+d)' % (t['x'] - o['x'], t['y'] - o['y'])
            print('  trader %d (%d,%d) dest=%d,%d warp=%d w10=%s met=%s item=%s w16=%s%s'
                  % (n, t['x'], t['y'], t['dest'][0], t['dest'][1], t['warp'], t['w10'], t['met'], t['item'],
                     t['w16'], note))
        if prev:
            for n in sorted(set(prev['traders']) - set(st['traders'])):
                print('  trader %d gone' % n)
        for k, f in sorted(st['fleets'].items()):
            print('  fleet %d/%d (%d,%d) ships=%s cargo=%s fuel=%d%s'
                  % (k[0], k[1], f['x'], f['y'], f['ships'], f['cargo'], f['fuel'], ' ' + f['dmg'] if f['dmg'] else ''))
        if prev:
            for k in sorted(set(prev['fleets']) - set(st['fleets'])):
                print('  fleet %d/%d gone' % k)
        prev = st


def main(argv):
    as_json = argv[:1] == ['--json']
    args = argv[1:] if as_json else argv
    if not args:
        sys.exit(__doc__)
    states = trace(runs(args))
    if as_json:
        for st in states:
            st['fleets'] = {'%d/%d' % k: v for k, v in st['fleets'].items()}
        json.dump(states, sys.stdout, indent=1)
        print()
    else:
        show(states)


if __name__ == '__main__':
    main(sys.argv[1:])
