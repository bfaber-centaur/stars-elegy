#!/usr/bin/env python3
"""Homeworld facts of new games, from `combatlab dump` output of the new .HST.

    python3 experiments/ug/homeworlds.py OUT/after.dump...

Per game: planet 0's concentrations; each player's PRT, starting tech,
homeworld (concentrations, surface minerals, population, mines, factories,
defenses) and any second planet. Groups homeworlds by concentrations and by surface
minerals, for the UG-9 claims: before leftover-point spends, every homeworld
has planet 0's concentrations raised to at least 30, and the same surface
minerals. Owners that spend on concentrations or minerals (and computer
players of level 2 and up) differ from the shared values by their spend.
"""
import re
import sys

PRT = ['HE', 'SS', 'WM', 'CA', 'IS', 'SD', 'PP', 'IT', 'AR', 'JOAT']


def kv(line):
    return dict(re.findall(r'(\w+)=(\S+)', line))


def game(path):
    players, pd, pos, planets = {}, {}, {}, 0
    for line in open(path):
        if '.HST ' not in line:
            continue
        body = line.split('.HST ', 1)[1]
        if body.startswith('player '):
            n = int(body.split()[1])
            players[n] = kv(body)
        elif body.startswith('pdetail '):
            pd[int(body.split()[1])] = kv(body)
        elif body.startswith('planet '):
            f = body.split()
            pos[int(f[1])] = kv(body)
    return players, pd, pos


def main():
    for path in sys.argv[1:]:
        players, pd, pos = game(path)
        c0 = [int(v) for v in pd[0]['conc'].split('/')]
        want = [max(v, 30) for v in c0]
        print('%s: %d players, planet 0 conc %s' % (path, len(players), '/'.join(map(str, c0))))
        owned = {}
        for n, d in pd.items():
            if int(d['owner']) >= 0:
                owned.setdefault(int(d['owner']), []).append(n)
        surf, concs = {}, {}
        for p in sorted(players):
            pl = players[p]
            hws = owned.get(p, [])
            # the homeworld is the owned planet with the larger population
            hws.sort(key=lambda n: -int(pd[n].get('pop', 0)))
            hw = pd[hws[0]] if hws else {}
            conc = [int(v) for v in hw.get('conc', '0/0/0').split('/')]
            tech = '/'.join(pl[k] for k in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio'))
            ok = conc == want
            line = '  p%-2d %-4s tech %s hw %d conc %s%s surface %s pop %s mines %s fact %s def %s' % (
                p, PRT[int(pl['prt'])], tech, hws[0] if hws else -1, hw.get('conc'), '' if ok else ' (spend?)',
                hw.get('surface'), hw.get('pop'), hw.get('mines'), hw.get('factories'), hw.get('defenses'))
            if len(hws) > 1:
                s = pd[hws[1]]
                line += ' | second %d pop %s mines %s fact %s' % (hws[1], s.get('pop'), s.get('mines'), s.get('factories'))
            print(line)
            surf.setdefault(hw.get('surface'), []).append(p)
            concs.setdefault(hw.get('conc'), []).append(p)
        print('  planet 0 floored: %s' % '/'.join(map(str, want)))
        print('  homeworld conc groups: %s' % '; '.join('%s: players %s' % (k, v) for k, v in concs.items()))
        print('  homeworld surface groups: %s' % '; '.join('%s: players %s' % (k, v) for k, v in surf.items()))


if __name__ == '__main__':
    main()
