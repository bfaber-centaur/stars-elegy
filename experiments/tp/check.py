#!/usr/bin/env python3
"""Check a TP run: python3 experiments/tp/check.py RUN_ID RUNDIR (RUNDIR holds before.dump and after.dump)."""
import re, sys


def state(path, which):
    pl, pd = {}, {}
    for l in open(path):
        if '/raw/%s/AP01.HST ' % which not in l:
            continue
        b = l.split('AP01.HST ', 1)[1]
        m = re.match(r'player (\d) ', b)
        if m:
            d = dict(re.findall(r'(\w+)=(\S+)', b))
            pl[int(m.group(1))] = (tuple(int(d[f]) for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio')),
                                   re.search(r' mt=(\S+)', b).group(1))  # the first mt= is the part word
        m = re.match(r'pdetail (\d+) ', b)
        if m and 'surface=' in b:
            pd[int(m.group(1))] = tuple(int(v) for v in re.search(r'surface=(\S+)', b).group(1).split('/'))
    return pl, pd


def main():
    rid, run = sys.argv[1], sys.argv[2]
    P0, S0 = state(run + '/before.dump', 'before')
    P1, S1 = state(run + '/after.dump', 'after')
    newbits = lambda p: int(P1[p][1], 16) & ~int(P0[p][1], 16)
    a = newbits(1)
    a_ok = (a == 1 if rid == 'tp001' else bin(a).count('1') == 1 and a & 0x1ffe) and max(S1[108]) <= 20
    print('%s-A %s part word %s -> %s, planet 108 surface %s -> %s' % (
        rid.upper().replace('TP', 'TP-'), 'HELD' if a_ok else 'CONTRADICTED', P0[1][1], P1[1][1], S0[108], S1[108]))
    if rid == 'tp001':
        b_ok = P1[2][0] == (12, 11, 11, 13, 11, 11) and S1[80][2] == 0 and S1[80][0] >= S0[80][0]
    else:
        b_ok = P1[2][0] == P0[2][0] and sum(S1[80]) > sum(S0[80]) - 1000
    print('%s-B %s tech %s -> %s, planet 80 surface %s -> %s' % (
        rid.upper().replace('TP', 'TP-'), 'HELD' if b_ok else 'CONTRADICTED', P0[2][0], P1[2][0], S0[80], S1[80]))
    c_ok = P1[0][1] == P0[0][1] and sum(S1[39]) >= sum(S0[39])
    print('%s-C %s part word %s -> %s, planet 39 surface %s -> %s' % (
        rid.upper().replace('TP', 'TP-'), 'HELD' if c_ok else 'CONTRADICTED', P0[0][1], P1[0][1], S0[39], S1[39]))


if __name__ == '__main__':
    main()
