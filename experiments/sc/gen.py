#!/usr/bin/env python3
"""Generate the SC- scanning corpus: one CombatLab spec and one case table per run.

  experiments/sc/gen.py CB.XY OUTDIR

CB.XY is the Combat Lab universe file (planet positions are read from it).
Writes OUTDIR/scNNN.spec and OUTDIR/scNNN.cases. Every expectation comes from
the model in sclib.py; the cases file also lists, per expectation, the
alternative rules that would predict a different outcome.
"""
import os, sys
from sclib import Game, Placer, rep_at_most, rep_above, reps, planets_xy

QJ = '1 Quick Jump 5'


def base(pxy):
    g = Game(pxy)
    g.planet_lines = ['planet 17 scanner none', 'planet 8 scanner none']
    return g


def targets(g):
    """Player-1 target designs (Small Freighter + Quick Jump 5 + one part)."""
    T = {}
    T['plain'] = g.design(1, 0, 'Small Freighter', [(1, 'Quick Jump 5'), (0, ''), (0, '')], 'Plain')
    T['st'] = g.design(1, 1, 'Small Freighter', [(1, 'Quick Jump 5'), (1, 'Stealth Cloak'), (0, '')], 'Stealth')
    T['ss'] = g.design(1, 2, 'Small Freighter', [(1, 'Quick Jump 5'), (1, 'Super-Stealth Cloak'), (0, '')], 'SuperStealth')
    T['us'] = g.design(1, 3, 'Small Freighter', [(1, 'Quick Jump 5'), (1, 'Ultra-Stealth Cloak'), (0, '')], 'UltraStealth')
    T['tc'] = g.design(1, 4, 'Small Freighter', [(1, 'Quick Jump 5'), (1, 'Transport Cloaking'), (0, '')], 'Transport')
    T['98'] = g.design(1, 5, 'Super Freighter', [(3, 'Quick Jump 5'), (3, 'Ultra-Stealth Cloak'), (0, ''),
                                                 (2, 'Ultra-Stealth Cloak')], 'Ghost')
    return T


def sf(g, owner, num, part, name, engine='Quick Jump 5'):
    return g.design(owner, num, 'Small Freighter', [(1, engine), (1 if part else 0, part or ''), (0, '')], name)


def pair(g, P, C, vgroup, cid, T, stacks_fn, bound, claims, cargo=(0, 0, 0, 0), fuel=50, lo=0, note=''):
    """A target just inside (seen) and just outside (unseen) a squared-distance bound."""
    din = rep_at_most(bound, lo)
    dout = rep_above(bound)
    for tag, d2 in (('in', din), ('out', dout)):
        x, y = P.at(C, d2)
        f = g.fleet(1, stacks_fn(), x, y, vgroup, cargo=cargo, fuel=fuel, tag='%s-%s d2=%d' % (cid, tag, d2))
        g.expect('%s-%s' % (cid, tag), 0, ('fleet', 1, f.id), claims, '%sd2=%d bound=%d' % (note, d2, bound),
                 group=vgroup)


def single(g, P, C, vgroup, cid, stacks, d2, claims, note='', **k):
    x, y = P.at(C, d2) if d2 else P.take(C)
    f = g.fleet(1, stacks, x, y, vgroup, tag='%s d2=%d' % (cid, d2), **k)
    g.expect(cid, 0, ('fleet', 1, f.id), claims, '%sd2=%d' % (note, d2), group=vgroup)
    return f


# ------------------------------------------------------------------ runs

def sc001(pxy):
    """X-1: cloak and range edges, Rhino (50) and two Rhinos (59); stacks don't combine."""
    g = base(pxy)
    T = targets(g)
    rhino = sf(g, 0, 0, 'Rhino Scanner', 'Rhino')
    rhino_b = sf(g, 0, 1, 'Rhino Scanner', 'Rhino B', engine='Long Hump 6')
    two = g.design(0, 2, 'Large Freighter', [(2, 'Quick Jump 5'), (2, 'Rhino Scanner'), (0, '')], 'Two Rhino')
    P = Placer(g)
    C1, C2, C3, C4 = (1080, 1080), (1080, 1320), (1320, 1320), (1220, 1200)
    for c in (C1, C2, C3, C4):
        P.take(c)
    g.fleet(0, [(rhino, 1)], *C1, 'G1', tag='G1 viewer Rhino 50')
    one = lambda d: (lambda: [(T[d], 1)])
    pair(g, P, C1, 'G1', 'SC001-plain', T, one('plain'), 2500, ['S-1', 'S-13'])
    pair(g, P, C1, 'G1', 'SC001-st35', T, one('st'), 1056, ['S-12', 'S-13'], lo=1024)
    pair(g, P, C1, 'G1', 'SC001-st17', T, one('st'), 1722, ['S-12', 'S-13'], cargo=(31, 0, 0, 0), lo=1681)
    pair(g, P, C1, 'G1', 'SC001-st10', T, one('st'), 2025, ['S-12', 'S-13'], cargo=(70, 0, 0, 0))
    pair(g, P, C1, 'G1', 'SC001-ss55', T, one('ss'), 506, ['S-12', 'S-13'], lo=484)
    pair(g, P, C1, 'G1', 'SC001-tc75', T, one('tc'), 156, ['S-12', 'S-13'], lo=144)
    pair(g, P, C1, 'G1', 'SC001-us85', T, one('us'), 56, ['S-12', 'S-13'], lo=49)
    pair(g, P, C1, 'G1', 'SC001-mix18', T, lambda: [(T['st'], 1), (T['plain'], 1)], 1681, ['S-12', 'S-13'])
    single(g, P, C1, 'G1', 'SC001-fuel', [(T['st'], 1)], rep_above(1056), ['S-12'], fuel=130,
           note='Stealth, fuel 130, ')

    g.fleet(0, [(two, 1)], *C2, 'G2', tag='G2 viewer two Rhinos 59')
    pair(g, P, C2, 'G2', 'SC001-two', T, one('plain'), 3481, ['S-2'])
    pair(g, P, C2, 'G2', 'SC001-two-st26', T, one('st'), 1905, ['S-13'], cargo=(10, 0, 0, 0))
    pair(g, P, C2, 'G2', 'SC001-two-st31', T, one('st'), 1656, ['S-13'], cargo=(4, 0, 0, 0))
    pair(g, P, C2, 'G2', 'SC001-two-ss45', T, one('ss'), 1052, ['S-13'], cargo=(17, 0, 0, 0))

    g.fleet(0, [(rhino, 1), (rhino_b, 1)], *C3, 'G3', tag='G3 viewer two Rhino stacks')
    single(g, P, C3, 'G3', 'SC001-stacks-in', [(T['plain'], 1)], 2500, ['S-3'])
    single(g, P, C3, 'G3', 'SC001-stacks-out', [(T['plain'], 1)], 3025, ['S-3'])
    g.fleet(0, [(rhino, 2)], *C4, 'G4', tag='G4 viewer two Rhino ships')
    single(g, P, C4, 'G4', 'SC001-ships-out', [(T['plain'], 1)], 3025, ['S-3'])
    return g


def sc001f(pxy):
    """S-23: SC-001 with both players friends."""
    g = sc001(pxy)
    g.relations = ['relation 0 1 1', 'relation 1 0 1']
    g.cases = [(c[0].replace('SC001', 'SC001F'),) + c[1:4] + (['S-23'],) + c[5:] for c in g.cases]
    return g


def sc002(pxy):
    """X-3 and S-20: blind, Bat, co-located, orbit reports, Pick Pocket."""
    g = base(pxy)
    T = targets(g)
    blind = sf(g, 0, 0, None, 'Blind')
    bat = sf(g, 0, 1, 'Bat Scanner', 'Bat')
    pp = sf(g, 0, 2, 'Pick Pocket Scanner', 'Pocket')
    rhino = sf(g, 0, 3, 'Rhino Scanner', 'Rhino')
    P = Placer(g)
    C1, C2, C5, C6 = (1100, 1230), (1180, 1240), (1060, 1060), (1330, 1350)
    A, B = 2, 10          # unowned planets to orbit
    for c in (C1, C2, C5, C6):
        P.take(c)
    v1 = g.fleet(0, [(blind, 1)], *C1, 'G1', tag='G1 blind viewer')
    single(g, P, C1, 'G1', 'SC002-blind-coloc98', [(T['98'], 1)], 0, ['S-15'])
    single(g, P, C1, 'G1', 'SC002-blind-d1', [(T['plain'], 1)], 1, ['S-4'])
    g.expect('SC002-p1-coloc-blind', 1, ('fleet', 0, v1.id), ['S-15'], 'blind Ghost sees the co-located viewer')
    g.fleet(0, [(bat, 1)], *C2, 'G2', tag='G2 Bat viewer')
    single(g, P, C2, 'G2', 'SC002-bat-coloc85', [(T['us'], 1)], 0, ['S-4', 'S-15'])
    single(g, P, C2, 'G2', 'SC002-bat-d1', [(T['plain'], 1)], 1, ['S-4'])
    pa, pb = pxy[A], pxy[B]
    g.fleet(0, [(blind, 1)], *pa, 'G3', planet=A, tag='G3 blind viewer orbiting')
    g.expect('SC002-blind-orbit', 0, ('planet', A), ['S-4'], 'orbited by a blind fleet', group='G3')
    single(g, P, pa, 'G3', 'SC002-blind-orbit-coloc98', [(T['98'], 1)], 0, ['S-15'], planet=A)
    g.fleet(0, [(bat, 1)], *pb, 'G4', planet=B, tag='G4 Bat viewer orbiting')
    g.expect('SC002-bat-orbit', 0, ('planet', B), ['S-4'], 'orbited by a Bat fleet', group='G4')
    single(g, P, pb, 'G4', 'SC002-bat-orbit-coloc', [(T['plain'], 1)], 0, ['S-4', 'S-15'], planet=B)
    g.fleet(0, [(pp, 1)], *C5, 'G5', tag='G5 Pick Pocket viewer')
    single(g, P, C5, 'G5', 'SC002-pp-coloc', [(T['plain'], 1)], 0, ['S-20'], cargo=(11, 12, 13, 0))
    single(g, P, C5, 'G5', 'SC002-pp-d30', [(T['plain'], 1)], 900, ['S-20'], cargo=(21, 22, 23, 0))
    g.fleet(0, [(rhino, 1)], *C6, 'G6', tag='G6 Rhino viewer')
    single(g, P, C6, 'G6', 'SC002-rhino-coloc', [(T['plain'], 1)], 0, ['S-20'], cargo=(31, 32, 33, 0))
    return g


def pen_run(pxy, part, cid, setup=None, design=None, deep=False):
    """X-2: a planet at the penetrating edge, one just past it, orbiting targets at both."""
    g = base(pxy)
    if setup:
        setup(g)
    T = targets(g)
    v = design(g) if design else sf(g, 0, 0, part, part.split()[0])
    R, Pn = v.scanner((), g.race(0))[:2]
    P = Placer(g)
    best = None
    dout = rep_above(Pn * Pn)
    inside = lambda p, q, r2: (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 <= r2
    for a, pa in enumerate(pxy):
        if a in (8, 17):
            continue
        for dx, dy in reps(Pn * Pn):
            V = (pa[0] + dx, pa[1] + dy)
            if not (1000 < V[0] < 1400 and 1000 < V[1] < 1400) or V in pxy:
                continue
            for b, pb in enumerate(pxy):
                if b in (8, 17, a) or inside(V, pb, Pn * Pn):
                    continue
                for ex, ey in reps(dout):
                    W = (pb[0] + ex, pb[1] + ey)
                    if not (1000 < W[0] < 1400 and 1000 < W[1] < 1400) or W in pxy or W == V:
                        continue
                    # margin: nearest other planet distance from the pen edge, either viewer
                    m = min(abs((q[0] - X[0]) ** 2 + (q[1] - X[1]) ** 2 - Pn * Pn)
                            for X in (V, W) for i, q in enumerate(pxy) if i not in (a, b))
                    if best is None or m > best[0]:
                        best = (m, a, V, b, W)
    m, a, V, b, W = best
    P.take(V); P.take(W)
    g.fleet(0, [(v, 1)], *V, 'GV', tag='%s viewer, planet %d at the pen edge' % (part, a))
    g.fleet(0, [(v, 1)], *W, 'GW', tag='%s viewer, planet %d just past the pen edge' % (part, b))
    g.expect('%s-planet-edge' % cid, 0, ('planet', a), ['S-5', 'S-6'], 'd2=%d pen=%d' % (Pn * Pn, Pn))
    g.expect('%s-planet-past' % cid, 0, ('planet', b), ['S-5', 'S-6'], 'd2=%d pen=%d' % (dout, Pn))
    f = g.fleet(1, [(T['plain'], 1)], *pxy[a], 'GV', planet=a, tag='orbits %d' % a)
    g.expect('%s-orbit-edge' % cid, 0, ('fleet', 1, f.id), ['S-6'], 'd2=%d' % (Pn * Pn))
    f = g.fleet(1, [(T['plain'], 1)], *pxy[b], 'GW', planet=b, tag='orbits %d' % b)
    g.expect('%s-orbit-past' % cid, 0, ('fleet', 1, f.id), ['S-6'], 'd2=%d' % dout)
    f = g.fleet(1, [(T['st'], 1)], *pxy[a], 'GV', planet=a, tag='Stealth orbits %d' % a)
    g.expect('%s-orbit-st35' % cid, 0, ('fleet', 1, f.id), ['S-6', 'S-13'], 'd2=%d' % (Pn * Pn))
    x, y = P.at(V, Pn * Pn)
    f = g.fleet(1, [(T['st'], 1)], x, y, 'GV', tag='Stealth deep space')
    g.expect('%s-deep-st35' % cid, 0, ('fleet', 1, f.id), ['S-6', 'S-13'], 'd2=%d' % (Pn * Pn))
    for name, d2 in (('R', R * R), ('Rp', R * R + 1)) if deep else ():
        try:
            x, y = P.at(V, d2, avoid=[W])
        except ValueError:
            continue
        f = g.fleet(1, [(T['plain'], 1)], x, y, 'GV', tag='plain deep space')
        g.expect('%s-deep-%s' % (cid, name), 0, ('fleet', 1, f.id), ['S-1'], 'd2=%d R=%d' % (d2, R))
    # every other planet: reported iff within pen of a viewer
    for i in range(len(pxy)):
        if i not in (a, b, 8, 17):
            g.expect('%s-planet%d' % (cid, i), 0, ('planet', i), ['S-5'])
    g.notes = 'margin %d' % m
    return g


def mole_run(pxy):
    """S-5/S-6 with a non-penetrating scanner (Mole 100/0) next to planets."""
    g = base(pxy)
    T = targets(g)
    v = sf(g, 0, 0, 'Mole Scanner', 'Mole')
    P = Placer(g)
    a = 12
    V = P.take((pxy[a][0] + 30, pxy[a][1]))
    g.fleet(0, [(v, 1)], *V, 'GV', tag='Mole viewer 30 ly from planet %d' % a)
    for i in range(len(pxy)):
        if i not in (8, 17):
            g.expect('SC008-planet%d' % i, 0, ('planet', i), ['S-5'])
    f = g.fleet(1, [(T['plain'], 1)], *pxy[a], 'GV', planet=a, tag='orbits %d' % a)
    g.expect('SC008-orbit30', 0, ('fleet', 1, f.id), ['S-6'], 'd2=900')
    single(g, P, V, 'GV', 'SC008-deep30', [(T['plain'], 1)], 900, ['S-1'])
    single(g, P, V, 'GV', 'SC008-deep100', [(T['plain'], 1)], 10000, ['S-1'])
    single(g, P, V, 'GV', 'SC008-deep101', [(T['plain'], 1)], 10001, ['S-1'])
    return g


def sb_run(pxy):
    """X-4: cloaked starbases seen through a Dolphin (220/100)."""
    g = base(pxy)
    T = targets(g)
    v = sf(g, 0, 0, 'Dolphin Scanner', 'Dolphin')
    E = [(0, '')]
    sb0 = g.design(1, 0, 'Space Station', E * 12, 'Station', starbase=True)
    sb1 = g.design(1, 1, 'Space Station', E * 6 + [(1, 'Stealth Cloak')] + E * 5, 'Cloak35', starbase=True)
    sb2 = g.design(1, 2, 'Space Station', E * 6 + [(2, 'Stealth Cloak')] + E * 5, 'Cloak55', starbase=True)
    g.sb[8] = sb0
    P = Placer(g)
    # planet, design, squared distance of its viewer
    plan = [(4, sb1, 4225, 'SC009-sb35-edge'), (13, sb1, 4226, 'SC009-sb35-past'),
            (21, sb2, 2025, 'SC009-sb55-edge'), (0, sb2, 2026, 'SC009-sb55-past')]
    for pid, d, d2, cid in plan:
        g.owned[pid] = 1
        g.pscanner[pid] = False
        g.sb[pid] = d
        g.planet_lines.append('planet %d owner 1 starbase %d scanner none' % (pid, d.num))
    for pid, d, d2, cid in plan:
        best = None
        for dx, dy in reps(d2):
            V = (pxy[pid][0] + dx, pxy[pid][1] + dy)
            if not (1000 < V[0] < 1400 and 1000 < V[1] < 1400) or V in P.used:
                continue
            # the other starbase planets must be out of this viewer's pen range
            far = min((pxy[q][0] - V[0]) ** 2 + (pxy[q][1] - V[1]) ** 2 for q, *_ in plan if q != pid)
            if far > 10000 and (best is None or far > best[0]):
                best = (far, V)
        assert best, cid
        P.take(best[1])
        g.fleet(0, [(v, 1)], *best[1], cid, tag='%s viewer, planet %d' % (cid, pid))
    for pid, d, d2, cid in plan:
        g.expect(cid, 0, ('planet', pid), ['S-16'], 'starbase %s d2=%d' % (d.name, d2))
    return g


def tach_run(pxy):
    """S-14: Mole (100) with 0, 1, 2 Tachyon Detectors vs Transport Cloaking (75%)."""
    g = base(pxy)
    T = targets(g)
    P = Placer(g)
    one = lambda: [(T['tc'], 1)]
    for n, C in ((0, (1080, 1080)), (1, (1320, 1080)), (2, (1080, 1320))):
        P.take(C)
        slots = [(3, 'Quick Jump 5'), (1, 'Mole Scanner'), (0, ''), (n, 'Tachyon Detector' if n else '')]
        d = g.design(0, n, 'Super Freighter', slots, 'Mole TD%d' % n)
        grp = 'TD%d' % n
        g.fleet(0, [(d, 1)], *C, grp, tag='viewer Mole + %d Tachyon' % n)
        for d2 in (625, 626, 841, 842, 900, 961, 962):
            single(g, P, C, grp, 'SC010-td%d-%d' % (n, d2), one(), d2, ['S-14'])
    return g


def ptech_run(pxy, elec, cid, energy=26, bio=26, lrt=0, extra=(), orbits=False):
    """X-7: planet scanner from tech; player 0's homeworld keeps its scanner."""
    g = base(pxy)
    g.lrt[0] = lrt
    T = targets(g)
    g.planet_lines = ['planet 8 scanner none']
    g.pscanner[17] = True
    g.tech[0] = [energy, 26, 26, 26, elec, bio]
    blind = sf(g, 0, 0, None, 'Blind')
    P = Placer(g)
    g.fleet(0, [(blind, 1)], 1020, 1390, 'GB', tag='blind player-0 fleet, far away')
    hw = pxy[17]
    r, p = g.planet_scan(17, 0, ())
    for name, d2 in (('150', 22500), ('150p', 22501), ('220', 48400), ('220p', 48401),
                     ('280', 78400), ('280p', 78401), ('320', 102400), ('320p', 102401)):
        try:
            x, y = P.at(hw, d2)
        except ValueError:
            continue
        f = g.fleet(1, [(T['plain'], 1)], x, y, 'GP', tag='%s-%s' % (cid, name))
        g.expect('%s-%s' % (cid, name), 0, ('fleet', 1, f.id), ['S-7', 'S-8'], 'd2=%d planet range %d/%d' % (d2, r, p))
    if p or orbits:
        for i in range(len(pxy)):
            if i not in (8, 17):
                g.expect('%s-planet%d' % (cid, i), 0, ('planet', i), ['S-8'])
                if (pxy[i][0] - hw[0]) ** 2 + (pxy[i][1] - hw[1]) ** 2 <= 250 ** 2:
                    f = g.fleet(1, [(T['plain'], 1)], *pxy[i], 'GP', planet=i, tag='orbits %d' % i)
                    g.expect('%s-orbit%d' % (cid, i), 0, ('fleet', 1, f.id), ['S-8'])
    return g


def rb_run(pxy):
    """S-20: Robber Baron in orbit (planet detail, enemy cargo) and a Rhino control."""
    g = base(pxy)
    T = targets(g)
    rb = sf(g, 0, 0, 'Robber Baron Scanner', 'Baron')
    rhino = sf(g, 0, 1, 'Rhino Scanner', 'Rhino')
    a, b = 3, 22
    g.fleet(0, [(rb, 1)], *pxy[a], 'GA', planet=a, tag='Robber Baron orbiting %d' % a)
    g.expect('SC014-rb-orbit', 0, ('planet', a), ['S-20'], 'orbited by a Robber Baron fleet', group='GA')
    f = g.fleet(1, [(T['plain'], 1)], *pxy[a], 'GA', planet=a, cargo=(41, 42, 43, 0), tag='loaded, orbits %d' % a)
    g.expect('SC014-rb-coloc', 0, ('fleet', 1, f.id), ['S-20'], 'co-located loaded freighter', group='GA')
    g.fleet(0, [(rhino, 1)], *pxy[b], 'GB', planet=b, tag='Rhino orbiting %d' % b)
    g.expect('SC014-rhino-orbit', 0, ('planet', b), ['S-4'], 'orbited by a Rhino fleet', group='GB')
    f = g.fleet(1, [(T['plain'], 1)], *pxy[b], 'GB', planet=b, cargo=(51, 52, 53, 0), tag='loaded, orbits %d' % b)
    g.expect('SC014-rhino-coloc', 0, ('fleet', 1, f.id), ['S-20'], 'co-located loaded freighter', group='GB')
    return g


def wm_ca_run(pxy, prt, cid, contact=True):
    """S-20: War Monger (full designs) or Claim Adjuster (hab ranges) viewer."""
    g = base(pxy)
    g.prt[0] = prt
    g.hab[1] = [40, 60, 45, 25, 35, 20, 55, 85, 70]   # narrower than the default (legal)
    T = targets(g)
    v = sf(g, 0, 0, 'Rhino Scanner', 'Rhino')
    P = Placer(g)
    C = P.take((1100, 1230))
    g.fleet(0, [(v, 1)], *C, 'G', tag='Rhino viewer')
    if contact:
        single(g, P, C, 'G', '%s-plain' % cid, [(T['plain'], 1)], 900, ['S-20'])
        single(g, P, C, 'G', '%s-st35' % cid, [(T['st'], 1)], 900, ['S-20'])
        single(g, P, C, 'G', '%s-us85-out' % cid, [(T['us'], 1)], 2025, ['S-20'])
    else:
        x, y = 1380, 1020
        g.fleet(1, [(T['plain'], 1)], x, y, 'G', tag='far away, unseen')
    return g


def nas_planet_run(pxy, cid):
    """S-9: NAS player planet scanner at electronics 10 (Snooper 320X without NAS)."""
    g = ptech_run(pxy, 10, cid, energy=3, bio=3, lrt=0x400, extra=(('560', 313600), ('560p', 313601)), orbits=True)
    return g


def nas_ship_run(pxy, cid):
    """S-9: NAS Rhino (100) against plain and Stealth targets."""
    g = base(pxy)
    g.lrt[0] = 0x400
    T = targets(g)
    v = sf(g, 0, 0, 'Rhino Scanner', 'Rhino')
    P = Placer(g)
    C = P.take((1200, 1230))
    g.fleet(0, [(v, 1)], *C, 'G', tag='NAS Rhino viewer')
    one = lambda d: (lambda: [(T[d], 1)])
    pair(g, P, C, 'G', '%s-plain' % cid, T, one('plain'), 10000, ['S-9'])
    pair(g, P, C, 'G', '%s-st35' % cid, T, one('st'), 4225, ['S-9', 'S-13'])
    return g


RUNS = {
    'sc001': sc001,
    'sc001f': sc001f,
    'sc002': sc002,
    'sc003': lambda p: pen_run(p, 'Ferret Scanner', 'SC003'),
    'sc004': lambda p: pen_run(p, 'Chameleon Scanner', 'SC004'),
    'sc005': lambda p: pen_run(p, 'Dolphin Scanner', 'SC005'),
    'sc006': lambda p: pen_run(p, 'Robber Baron Scanner', 'SC006'),
    'sc007': lambda p: pen_run(p, 'Elephant Scanner', 'SC007'),
    'sc008': mole_run,
    'sc009': sb_run,
    'sc010': tach_run,
    'sc011': lambda p: ptech_run(p, 5, 'SC011'),
    'sc012': lambda p: ptech_run(p, 6, 'SC012'),
    'sc013': lambda p: ptech_run(p, 10, 'SC013', energy=3, bio=3),
    'sc014': rb_run,
    'sc015': lambda p: wm_ca_run(p, 2, 'SC015'),
    'sc016': lambda p: wm_ca_run(p, 3, 'SC016'),
    'sc016n': lambda p: wm_ca_run(p, 3, 'SC016N', contact=False),
    'sc017': lambda p: nas_ship_run(p, 'SC017'),
    'sc018': lambda p: pen_run(p, 'Ferret Scanner', 'SC018', setup=lambda g: g.lrt.update({0: 0x400})),
    'sc019': lambda p: nas_planet_run(p, 'SC019'),
    'sc020': lambda p: pen_run(p, None, 'SC020', setup=joat10, deep=True,
                               design=lambda g: g.design(0, 0, 'Scout', [(1, 'Quick Jump 5'), (0, ''), (0, '')], 'Bare Scout')),
    'sc021': lambda p: pen_run(p, None, 'SC021', setup=joat10, deep=True,
                               design=lambda g: g.design(0, 0, 'Scout', [(1, 'Quick Jump 5'), (1, 'Elephant Scanner'), (0, '')], 'Elephant Scout')),
}


def joat10(g):
    g.tech[0][4] = 10


def main():
    xy, out = sys.argv[1], sys.argv[2]
    only = sys.argv[3:]
    pxy = planets_xy(xy)
    os.makedirs(out, exist_ok=True)
    for name, fn in RUNS.items():
        if only and name not in only:
            continue
        g = fn(pxy)
        doc = (fn.__doc__ or name).strip().splitlines()[0]
        with open(os.path.join(out, name + '.spec'), 'w') as f:
            f.write(g.spec('%s: %s' % (name.upper(), doc)))
        with open(os.path.join(out, name + '.cases'), 'w') as f:
            f.write(g.table())
        print('%s: %d fleets, %d cases %s' % (name, len(g.fleets), len(g.cases), getattr(g, 'notes', '')))


if __name__ == '__main__':
    main()
