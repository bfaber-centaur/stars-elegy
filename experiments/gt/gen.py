#!/usr/bin/env python3
"""GT: stargate cases OB-021/OB-022 left open (stars-decomp O-54..O-67).

One Combat Lab spec on the GT base game: a medium universe (1000..2200),
two human players made with tools/fleetlab/new-game from experiments/gt
(player 0 JOAT with Cheap Engines, player 1 JOAT), tech 26, no random
events. Player 1 lists player 0 as a friend; player 0 lists player 1 as
an enemy, so one run tests friendship in both directions. Every player 0
fleet uses plan "Nobody"; player 1's fleets are unarmed or at friendly
planets, so no battle interferes.

  python3 experiments/gt/gen.py OUTDIR     # writes OUTDIR/gt001.spec and OUTDIR/cases.json
  python3 experiments/gt/gen.py --list     # case table with predictions

Predictions restate docs/OBJECTS.md "Stargates" (BINARY-ONLY rules) and
were written before the run; `alt` is the reading each case rules out.
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
XY = {}
for line in open(os.path.join(HERE, 'planets.txt')):
    n, x, y = map(int, line.split())
    XY[n] = (x, y)
HOME = {0: 142, 1: 70}
LO, HI = 1000, 2200

# gate index -> (name, mass limit, range); None = any
GATES = [('Stargate 100/250', 100, 250), ('Stargate any/300', None, 300), ('Stargate 150/600', 150, 600),
         ('Stargate 300/500', 300, 500), ('Stargate 100/any', 100, None), ('Stargate any/800', None, 800),
         ('Stargate any/any', None, None)]
SB_NOGATE = 8          # starbase design 8: Orbital Fort without a gate; 1 + idx = gate idx


def gate_pct(src, dst, d, mass):
    """OBJECTS.md "Stargates": None when refused, else the danger percent (100 = design lost)."""
    R = GATES[src][2] or 8000
    Ms, Md = GATES[src][1], GATES[dst][1]
    if d > 5 * R:
        return None
    for M in (Ms, Md):
        if M and mass > 5 * M:
            return None
    f = 10000
    if d > R:
        f = (5 * R - d) * 2500 // R
        if f <= 0:
            return 100
    for M in (Ms, Md):
        if M and 0 < M < mass:
            g = (5 * M - mass) * 2500 // M
            if g <= 0:
                return 100
            f = g * f // 10000
    return (10000 - f) // 100


def gate_word(pct, armor):
    """Damage word of every survivor after a jump with 0 < pct < 100 and no earlier damage."""
    nw = max(1, pct * armor // 100)
    return '%d/100%%' % max(1, nw * 500 // armor)


# player 0 designs: (name, spec, mass, armor)
D0 = [('Laser DD', 'Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, empty, empty, empty', 41, 200),
      ('Super Freighter', 'Super Freighter, 3 Long Hump 6, empty, empty, empty', 202, 400),
      ('Small Freighter', 'Small Freighter, 1 Long Hump 6, empty, empty', 34, 25),
      ('JG Freighter', 'Small Freighter, 1 Long Hump 6, 1 Jump Gate, empty', 44, 25),
      ('JG DD', 'Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, empty, 1 Jump Gate, empty', 51, 200),
      ('Heavy 500', 'Super Freighter, 2 Long Hump 6, 1 Super Cargo Pod, 5 Tritanium, empty', 500, 650)]
D1 = [('Laser DD', 'Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, empty, empty, empty', 41, 200),
      ('Scout', 'Scout, 1 Long Hump 6, 1 Possum Scanner, empty', None, None),
      ('Small Freighter', 'Small Freighter, 1 Long Hump 6, empty, empty', 34, 25)]
DD, SF, FR, JGF, JGDD, H500 = range(6)

TECH = ''.join('tech %d %s 26\n' % (p, f) for p in (0, 1) for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio'))
SB = ''
for p in (0, 1):
    SB += ('sbdesign %d 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, '
           '8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Starbase\n' % p)
    for i, g in enumerate(GATES):
        SB += 'sbdesign %d %d Orbital Fort, 1 %s, empty, empty, empty, empty = Gate %s\n' % (p, i + 1, g[0], g[0][9:])
    SB += 'sbdesign %d %d Orbital Fort, empty, empty, empty, empty, empty = Fort\n' % (p, SB_NOGATE)
HEAD = ('# GT-001: stargates (experiments/gt/gen.py)\nrelation 0 1 2\nrelation 1 0 1\n' + TECH +
        'research 0 0\nresearch 1 0\nmt 0 0800\nmt 1 0800\n' +
        ''.join('design 0 %d %s = %s\n' % (i, d[1], d[0]) for i, d in enumerate(D0)) +
        ''.join('design 1 %d %s = %s\n' % (i, d[1], d[0]) for i, d in enumerate(D1)) + SB +
        'plan 0 0 4 1 0 1 = Enemies\nplan 0 1 4 1 0 0 = Nobody\n')
PLAIN = 'mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0 env=50,50,50 excess=0 scanner=31'


def dist(a, b):
    return int(math.hypot(a[0] - b[0], a[1] - b[1]))


class Spec:
    def __init__(self):
        self.used = set(HOME.values())
        self.planets, self.lines, self.cases = [], [], []
        self.nfleet = {0: 0, 1: 0}

    def planet(self, owner, sb, near=None, d=None, tol=60):
        """An unused planet for owner with starbase design sb (None = no starbase), optionally at about d ly from near."""
        best = None
        for n, p in sorted(XY.items(), key=lambda kv: (kv[0] * 97) % len(XY)):
            if n in self.used or any(dist(p, XY[h]) < 60 for h in HOME.values()):
                continue
            if any(dist(p, XY[u]) < 25 for u in self.used):
                continue
            if near is not None:
                e = abs(dist(p, near) - d)
                if e > tol:
                    continue
                if best is None or e < best[0]:
                    best = (e, n)
            else:
                best = (0, n)
                break
        assert best, (owner, sb, near, d)
        n = best[1]
        self.used.add(n)
        self.planets.append('planet %d owner %d pop 1000 starbase %s\nplanetset %d %s\n' % (
            n, owner, 'none' if sb is None else sb, n, PLAIN))
        return n

    def fleet(self, owner, at, ships, wps='', plan=None, fuel=100, cargo=None, planet=None, dmg=None):
        fid = self.nfleet[owner]
        self.nfleet[owner] += 1
        if plan is None:
            plan = 1 if owner == 0 else 0
        s = 'fleet %d %d %sat %d %d ships %s plan %d fuel %d' % (
            owner, fid, 'planet %d ' % planet if planet is not None else '', at[0], at[1], ships, plan, fuel)
        if cargo:
            s += ' cargo %d %d %d %d' % cargo
        if dmg:
            s += ' dmg %s' % dmg
        self.lines.append(s + wps)
        return fid

    def gate(self, owner, src, dst, ships, **k):
        """Fleet orbiting planet src with a warp-11 waypoint to planet dst."""
        return self.fleet(owner, XY[src], ships, planet=src,
                          wps=' to %d %d planet %d warp 11' % (XY[dst] + (dst,)), **k)

    def case(self, cid, pred, what, expect, alt, check):
        self.cases.append(dict(id='GT-001-%s' % cid, pred=pred, what=what, expect=expect, alt=alt, check=check))

    def text(self):
        return HEAD + ''.join(self.planets) + '\n'.join(self.lines) + '\n'


def build():
    s = Spec()
    gp = lambda owner, idx, **k: s.planet(owner, 1 + idx, **k)     # gate planet

    # ---- O-54 Jump Gate from deep space (destination 100/250)
    B = gp(0, 0)
    pt = (XY[B][0] + 200 if XY[B][0] < 1600 else XY[B][0] - 200, XY[B][1])
    f = s.fleet(0, pt, '%d:2' % JGF, cargo=(100, 0, 0, 0), wps=' to %d %d planet %d warp 11' % (XY[B] + (B,)))
    s.case('A', 'O-54', '2 Jump Gate freighters, 100 kT ironium, deep space 200 ly from own 100/250 planet %d' % B,
           'at planet %d with 100 kT, fuel 100, undamaged' % B, 'refused (no source gate); cargo dropped',
           dict(kind='fleet', owner=0, id=f, at=XY[B], ships=2, cargo=(100, 0, 0, 0), fuel=100, dmg=None))
    B = gp(0, 0)
    pt = (XY[B][0] + 300 if XY[B][0] < 1600 else XY[B][0] - 300, XY[B][1])
    pct = gate_pct(0, 0, 300, 44)
    f = s.fleet(0, pt, '%d:5' % JGF, wps=' to %d %d planet %d warp 11' % (XY[B] + (B,)))
    s.case('A2', 'O-54', '5 Jump Gate freighters, deep space 300 ly from own 100/250 planet %d: danger %d%% '
           '(the destination range stands for both ends)' % (B, pct),
           'at planet %d; each lost with %d%%; survivors %s' % (B, pct // 3, gate_word(pct, 25)),
           'undamaged (no range limit for a Jump Gate)',
           dict(kind='fleet', owner=0, id=f, at=XY[B], ships=(5 - 5, 5), dmg=gate_word(pct, 25)))
    B = gp(0, 0)
    pt = (XY[B][0] + 200 if XY[B][0] < 1600 else XY[B][0] - 200, XY[B][1])
    f = s.fleet(0, pt, '%d:1,%d:1' % (JGF, FR), wps=' to %d %d planet %d warp 11' % (XY[B] + (B,)))
    s.case('A3', 'O-54', 'one Jump Gate freighter and one plain freighter in deep space, gate warp to own planet %d' % B,
           'stays (message 0xde)', 'jumps', dict(kind='fleet', owner=0, id=f, at=pt, msg=0xde))

    # ---- O-55 real source gate wins over Jump Gate
    A = gp(0, 0)
    B = gp(6 - 6, 6, near=XY[A], d=300) if False else s.planet(0, 7, near=XY[A], d=300)
    d = dist(XY[A], XY[B]); pct = gate_pct(0, 6, d, 44)
    f = s.gate(0, A, B, '%d:1' % JGF, cargo=(60, 0, 0, 0))
    s.case('B', 'O-55', 'Jump Gate freighter with 60 kT at own 100/250 planet %d, %d ly to own any/any planet %d: danger %d%%'
           % (A, d, B, pct), 'planet %d surface +60; at planet %d empty (or lost with %d%%), damage %s' % (
               A, B, pct // 3, gate_word(pct, 25) if pct else 'none'),
           'cargo kept and no damage (Jump Gate used instead of the planet gate)',
           dict(kind='fleet', owner=0, id=f, at=XY[B], ships=(0, 1), cargo=(0, 0, 0, 0),
                dmg=gate_word(pct, 25) if pct else None, surface=(A, 60)))

    # ---- O-56 Jump Gate needs a destination gate
    B = s.planet(0, SB_NOGATE)
    pt = (XY[B][0] + 100 if XY[B][0] < 1600 else XY[B][0] - 100, XY[B][1])
    f = s.fleet(0, pt, '%d:1' % JGF, cargo=(50, 0, 0, 0), wps=' to %d %d planet %d warp 11' % (XY[B] + (B,)))
    s.case('C', 'O-56', 'Jump Gate freighter 100 ly from own planet %d whose starbase has no gate' % B,
           'stays with its 50 kT (message 0xe2)', 'jumps', dict(kind='fleet', owner=0, id=f, at=pt, cargo=(50, 0, 0, 0), msg=0xe2))
    B = s.planet(0, None)
    pt = (XY[B][0] + 100 if XY[B][0] < 1600 else XY[B][0] - 100, XY[B][1])
    f = s.fleet(0, pt, '%d:1' % JGF, wps=' to %d %d planet %d warp 11' % (XY[B] + (B,)))
    s.case('C2', 'O-56', 'Jump Gate freighter 100 ly from own planet %d with no starbase' % B,
           'stays (message 0xe2)', 'jumps', dict(kind='fleet', owner=0, id=f, at=pt, msg=0xe2))

    # ---- O-57 friend source gate, one-sided (1 lists 0 as friend; 0 lists 1 as enemy)
    A = gp(1, 0); B = gp(0, 0, near=XY[A], d=150)
    f = s.gate(0, A, B, '%d:1' % DD)
    s.case('D', 'O-57', 'player 0 Laser DD at player 1\'s gate planet %d (player 1 lists 0 as friend; 0 lists 1 as enemy) '
           'to own gate planet %d' % (A, B), 'at planet %d' % B, 'stays (fleet owner\'s view, or mutual friendship)',
           dict(kind='fleet', owner=0, id=f, at=XY[B]))
    A = gp(0, 0); B = gp(1, 0, near=XY[A], d=150)
    f = s.gate(1, A, B, '0:1')
    s.case('D2', 'O-57', 'player 1 Laser DD at player 0\'s gate planet %d (0 lists 1 as enemy) to own gate planet %d' % (A, B),
           'stays (message 0xe6)', 'jumps (player 1 lists 0 as friend)', dict(kind='fleet', owner=1, id=f, at=XY[A], msg=0xe6))

    # ---- O-58 friend destination gate
    A = gp(0, 0); B = gp(1, 0, near=XY[A], d=150)
    f = s.gate(0, A, B, '%d:1' % DD)
    s.case('E', 'O-58', 'player 0 Laser DD from own gate %d to player 1\'s gate planet %d' % (A, B),
           'at planet %d; player 1 gets no message naming it' % B, 'stays', dict(kind='fleet', owner=0, id=f, at=XY[B]))
    A = gp(1, 0); B = gp(0, 0, near=XY[A], d=150)
    f = s.gate(1, A, B, '0:1')
    s.case('E2', 'O-58', 'player 1 Laser DD from own gate %d to player 0\'s gate planet %d' % (A, B),
           'stays (message 0xe5)', 'jumps', dict(kind='fleet', owner=1, id=f, at=XY[A], msg=0xe5))

    # ---- O-59 cargo at a friend's gate
    A = gp(1, 0); B = gp(0, 0, near=XY[A], d=150)
    f = s.gate(0, A, B, '%d:1' % FR, cargo=(70, 0, 0, 0))
    s.case('F', 'O-59', 'player 0 freighter with 70 kT ironium at player 1\'s gate planet %d to own gate %d' % (A, B),
           'planet %d (player 1\'s) surface +70; both players get message 0xec; freighter at %d empty' % (A, B),
           'cargo carried; or dumped without telling player 1',
           dict(kind='fleet', owner=0, id=f, at=XY[B], cargo=(0, 0, 0, 0), surface=(A, 70), msg=0xec, msg1=0xec))
    A = gp(1, 0); B = gp(0, 0, near=XY[A], d=150)
    f = s.gate(0, A, B, '%d:1' % FR, cargo=(50, 0, 0, 10))
    s.case('F2', 'O-59', 'player 0 freighter with 50 kT ironium and 10 kT colonists at player 1\'s gate planet %d' % A,
           'stays full (message 0x15e); planet %d surface +0' % A, 'minerals dumped first; or jumps',
           dict(kind='fleet', owner=0, id=f, at=XY[A], cargo=(50, 0, 0, 10), surface=(A, 0), msg=0x15e))
    A = gp(1, 0); B = s.planet(0, SB_NOGATE, near=XY[A], d=150)
    f = s.gate(0, A, B, '%d:1' % FR, cargo=(50, 0, 0, 10))
    s.case('F3', 'O-59', 'as F2, destination own planet %d without a gate' % B,
           'stays full (message 0xe2, checked before 0x15e)', 'message 0x15e',
           dict(kind='fleet', owner=0, id=f, at=XY[A], cargo=(50, 0, 0, 10), surface=(A, 0), msg=0xe2))

    # ---- O-60 range refusal and the exact-5x total loss
    A = gp(0, 0); B = s.planet(0, 7, near=XY[A], d=1350, tol=90)
    d = dist(XY[A], XY[B])
    f = s.gate(0, A, B, '%d:1' % FR, cargo=(50, 0, 0, 0))
    s.case('G', 'O-60', 'freighter with 50 kT from own 100/250 planet %d to own any/any planet %d, %d ly (> 1250)' % (A, B, d),
           'stays, undamaged, empty (message 0xe3); planet %d surface +50' % A, 'jumps with losses',
           dict(kind='fleet', owner=0, id=f, at=XY[A], cargo=(0, 0, 0, 0), dmg=None, surface=(A, 50), msg=0xe3))
    for cid, want in (('G2', 1250), ('G3', 1249), ('G4', 1251)):
        B = None
        for n in sorted(XY):
            if n in s.used:
                continue
            p = XY[n]
            for ang in range(0, 360, 3):
                x = p[0] + int(round(want * math.cos(math.radians(ang))))
                y = p[1] + int(round(want * math.sin(math.radians(ang))))
                if LO + 5 <= x <= HI - 5 and LO + 5 <= y <= HI - 5 and dist((x, y), p) == want and \
                        all(dist((x, y), q) > 30 for q in XY.values()):
                    B, pt = n, (x, y)
                    break
            if B is not None:
                break
        s.used.add(B)
        s.planets.append('planet %d owner 0 pop 1000 starbase 1\nplanetset %d %s\n' % (B, B, PLAIN))
        pct = gate_pct(0, 0, want, 51)
        f = s.fleet(0, pt, '%d:3' % JGDD, wps=' to %d %d planet %d warp 11' % (XY[B] + (B,)))
        if pct is None:
            exp, chk = 'stays, 3 ships, undamaged (message 0xe3)', dict(kind='fleet', owner=0, id=f, at=pt, ships=3, dmg=None, msg=0xe3)
        elif pct == 100:
            exp, chk = 'fleet gone (message 0xe7)', dict(kind='gone', owner=0, id=f, msg=0xe7)
        else:
            exp = 'at planet %d; each lost with %d%%; survivors %s' % (B, pct // 3, gate_word(pct, 200))
            chk = dict(kind='fleet', owner=0, id=f, at=XY[B], ships=(0, 3), dmg=gate_word(pct, 200))
        s.case(cid, 'O-60', '3 Jump Gate DDs in deep space exactly %d ly (truncated) from own 100/250 planet %d' % (want, B),
               exp, 'refused at 1250; or jumps at 1251', chk)

    # ---- O-61 mass exactly 5x: lost; mixed fleet survives
    A = gp(0, 0); B = s.planet(0, 7, near=XY[A], d=100)
    f = s.gate(0, A, B, '%d:1' % H500)
    s.case('H', 'O-61', 'a 500 kT design (5 x 100) at own 100/250 planet %d to own any/any %d' % (A, B),
           'fleet gone (message 0xe7)', 'refused (0xe4) as at 502 kT', dict(kind='gone', owner=0, id=f, msg=0xe7))
    A = gp(0, 0); B = s.planet(0, 7, near=XY[A], d=100)
    f = s.gate(0, A, B, '%d:1,%d:1' % (H500, DD))
    s.case('H2', 'O-61', 'the 500 kT design and a Laser DD in one fleet, same jump (%d to %d)' % (A, B),
           'at planet %d with only the Laser DD, undamaged' % B, 'whole fleet gone or refused',
           dict(kind='fleet', owner=0, id=f, at=XY[B], ships=1, dmg=None, designs={DD: 1}))

    # ---- O-62 no repair after a gate; refused counts as stationary
    A = gp(0, 0); B = gp(0, 0, near=XY[A], d=100)
    f = s.gate(0, A, B, '%d:2' % DD, dmg='0:250:100')
    s.case('I', 'O-62', '2 Laser DDs at 50%% damage, safe jump %d -> %d (100/250 both)' % (A, B),
           'at planet %d, damage still 250/100%%' % B, 'repaired', dict(kind='fleet', owner=0, id=f, at=XY[B], dmg='250/100%'))
    C = gp(0, 0)
    f2 = s.fleet(0, XY[C], '%d:2' % DD, planet=C, dmg='0:250:100')
    A = gp(0, 0); B = s.planet(0, SB_NOGATE, near=XY[A], d=100)
    f3 = s.gate(0, A, B, '%d:2' % DD, dmg='0:250:100')
    s.case('I2', 'O-62', 'control: the same stack parked at own gate planet %d' % C, 'repaired (below 250)', '',
           dict(kind='fleet', owner=0, id=f2, at=XY[C], repaired=True))
    s.case('I3', 'O-62', 'the same stack refused at own gate %d (destination %d has no gate)' % (A, B),
           'stays; repaired exactly as the control I2', 'not repaired (counted as moved or as a jump)',
           dict(kind='fleet', owner=0, id=f3, at=XY[A], msg=0xe2, same_dmg_as=f2))

    # ---- O-64 chasers; O-63 what others see (player 1 scout at the centre)
    A = gp(0, 0); B = gp(0, 0, near=XY[A], d=200)
    F = s.gate(0, A, B, '%d:1' % DD)
    s.case('K', 'O-63', 'player 0 Laser DD gating %d -> %d, seen by player 1' % (A, B),
           'in player 1\'s file at planet %d with warp 0' % B, 'warp shown', dict(kind='seen', owner=0, id=F, at=XY[B], warp=0))
    ex = (XY[A][0] + 120 if XY[A][0] < 1600 else XY[A][0] - 120, XY[A][1] + (60 if XY[A][1] < 1600 else -60))
    E = s.fleet(1, ex, '1:1', wps=' to %d %d fleet 0 %d warp 2' % (XY[A] + (F,)))
    G = s.fleet(0, (ex[0], ex[1] + 20 if ex[1] < 1600 else ex[1] - 20), '%d:1' % DD,
                wps=' to %d %d fleet 0 %d warp 2' % (XY[A] + (F,)))
    s.case('K2', 'O-64', 'player 1 scout chasing that DD (warp 2)', 'waypoint left at planet %d\'s position (departure)' % A,
           'waypoint at planet %d (tracked)' % B, dict(kind='wp', owner=1, id=E, at=XY[A]))
    s.case('K3', 'O-64', 'player 0\'s own DD chasing it (warp 2)', 'waypoint at planet %d (tracked)' % B, 'frozen at %d' % A,
           dict(kind='wp', owner=0, id=G, at=XY[B]))
    mstart = (ex[0], ex[1] + 80 if ex[1] < 1600 else ex[1] - 80)
    mdest = (mstart[0] + (100 if mstart[0] < 1600 else -100), mstart[1])
    M = s.fleet(0, mstart, '%d:1' % DD, wps=' to %d %d warp 6' % mdest)
    E2 = s.fleet(1, (mstart[0], mstart[1] + 30 if mstart[1] < 1600 else mstart[1] - 30), '1:1',
                 wps=' to %d %d fleet 0 %d warp 2' % (mstart + (M,)))
    s.case('K4', 'O-63', 'control: player 0 Laser DD moving 36 ly at warp 6 in deep space', 'player 1 sees warp 6 and a heading',
           '', dict(kind='seen', owner=0, id=M, warp=6))
    s.case('K5', 'O-64', 'control: player 1 scout chasing that normally moving DD', 'waypoint at the DD\'s new position', '',
           dict(kind='wp', owner=1, id=E2, follow=(0, M)))
    s.lines.append('fleet 1 %d at 1600 1600 ships 1:1 plan 0 fuel 100' % s.nfleet[1]); s.nfleet[1] += 1

    # ---- O-65 Cheap Engines never fail on a gate order
    A = gp(0, 0); B = gp(0, 0, near=XY[A], d=100)
    cef = [s.gate(0, A, B, '%d:1' % DD) for _ in range(20)]
    s.case('L', 'O-65', '20 single Laser DDs (Cheap Engines owner) gating %d -> %d (danger 0)' % (A, B),
           'all 20 at planet %d; no message 0xf2' % B, 'about 2 fail (10%% each)',
           dict(kind='many', owner=0, ids=cef, at=XY[B]))
    base = (1100, 2150)
    ctl = [s.fleet(0, (base[0] + 30 * i, base[1]), '%d:1' % DD, wps=' to %d %d warp 9' % (base[0] + 30 * i, base[1] - 81))
           for i in range(20)]
    s.case('L2', 'O-65', 'control: 20 single Laser DDs at warp 9 in deep space', 'some stay with message 0xf2 (about 2)', '',
           dict(kind='ce', owner=0, ids=ctl))

    # ---- O-66 gate to deep space
    A = gp(0, 0)
    pt = (XY[A][0] + 100 if XY[A][0] < 1600 else XY[A][0] - 100, XY[A][1])
    f = s.fleet(0, XY[A], '%d:1' % DD, planet=A, wps=' to %d %d warp 11' % pt)
    s.case('M', 'O-66', 'Laser DD at own gate %d, warp 11 to a deep-space point' % A, 'stays (message 0x147)', 'moves',
           dict(kind='fleet', owner=0, id=f, at=XY[A], msg=0x147))

    # ---- O-67 gate types (destination any/any)
    for cid, idx, d, des, n in (('N1', 1, 400, DD, 3), ('N2', 2, 700, DD, 3), ('N3', 3, 300, H500, 1),
                                ('N4', 4, 300, SF, 3), ('N5', 5, 900, DD, 3), ('N6', 6, 900, SF, 3)):
        A = gp(0, idx); B = s.planet(0, 7, near=XY[A], d=d, tol=30)
        dd = dist(XY[A], XY[B]); mass, armor = D0[des][2], D0[des][3]
        pct = gate_pct(idx, 6, dd, mass)
        f = s.gate(0, A, B, '%d:%d' % (des, n))
        if pct == 0:
            exp, chk = 'at planet %d, undamaged' % B, dict(kind='fleet', owner=0, id=f, at=XY[B], ships=n, dmg=None)
        else:
            exp = 'at planet %d; each lost with %d%%; survivors %s' % (B, pct // 3, gate_word(pct, armor) if armor else 'damaged')
            chk = dict(kind='fleet', owner=0, id=f, at=XY[B], ships=(0, n), dmg=gate_word(pct, armor) if armor else 'any')
        s.case(cid, 'O-67', '%d x %s (%d kT) through %s, %d ly to any/any: danger %d%%' % (n, D0[des][0], mass, GATES[idx][0], dd, pct),
               exp, '', chk)
    return s


H500B = 6
HEAD2 = HEAD.replace('# GT-001', '# GT-002') + \
    'design 0 6 Super Freighter, 1 Long Hump 6, 2 Super Fuel Tank, 5 Tritanium, empty = Heavy 500b\n'


def build2():
    """GT-002, after GT-001-H2 missed: a design lost entirely (pct 100) is subtracted twice from the
    fleet's design count, and the fleet is deleted when the count is exactly 0 (stars-decomp
    fleet-gates-merge.md 2.5, reconciled). Count = designs - 2 x lost designs; written before GT-002."""
    s = Spec()
    s.cases = []
    for cid, mix, deleted in (('H3', ((H500, 1), (DD, 1), (FR, 1)), False),
                              ('H4', ((H500, 1), (H500B, 1), (DD, 1), (FR, 1)), True),
                              ('H5', ((H500, 1), (H500B, 1), (DD, 1)), False),
                              ('H6', ((H500, 1), (H500B, 1)), True),
                              ('H7', ((H500, 1), (DD, 1)), True)):
        A = s.planet(0, 1); B = s.planet(0, 7, near=XY[A], d=100)
        f = s.gate(0, A, B, ','.join('%d:%d' % m for m in mix))
        k, j = len(mix), sum(1 for d, n in mix if d in (H500, H500B))
        names = ' + '.join(['500 kT'] * j + [D0[d][0] for d, n in mix if d not in (H500, H500B)])
        if deleted:
            why = 'every design lost' if j == k else 'count %d - 2 x %d = 0' % (k, j)
            exp, chk = 'fleet gone (message 0xe7): %s' % why, dict(kind='gone', owner=0, id=f, msg=0xe7)
        else:
            keep = {d: n for d, n in mix if d not in (H500, H500B)}
            exp = 'at planet %d with only the %s (count %d - 2 x %d = %d)' % (B, ', '.join(D0[d][0] for d in keep), k, j, k - 2 * j)
            chk = dict(kind='fleet', owner=0, id=f, at=XY[B], designs=keep)
        s.case(cid, 'O-61', '%s in one fleet, 100/250 gate %d to any/any %d (100 ly)' % (names, A, B), exp,
               'deleted only when every design is lost' if not deleted or j < k else '', chk)
    for c in s.cases:
        c['id'] = c['id'].replace('GT-001', 'GT-002')
    return s


H502, H491 = 7, 8
HEAD3 = HEAD2.replace('# GT-002', '# GT-003') + \
    'design 0 7 Super Freighter, 3 Long Hump 6, empty, 5 Tritanium, empty = Heavy 502\n' + \
    'design 0 8 Super Freighter, 1 Long Hump 6, 1 Super Cargo Pod, 5 Tritanium, empty = Heavy 491\n' + \
    'design 1 3 Super Freighter, 3 Long Hump 6, empty, 5 Tritanium, empty = Heavy 502\n'
REFUSALS = (0xde, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0x147, 0x15e)


def build3():
    """GT-003 (BINARY-ONLY sweep): the refusal order with two failures at once, and a design wiped out by
    the loss rolls counting once against the fleet's design count. Written before GT-003."""
    s = Spec()
    gp = lambda owner, idx, **k: s.planet(owner, 1 + idx, **k)
    A = gp(0, 0); B = s.planet(1, SB_NOGATE, near=XY[A], d=150)
    f = s.gate(1, A, B, '0:1')
    s.case('R1', 'refusal order', 'player 1 Laser DD at player 0\'s gate %d (source refused) to own planet %d without a '
           'gate' % (A, B), 'stays; the only refusal message is 0xe6 (source gate)', '0xe2 (destination gate) first',
           dict(kind='fleet', owner=1, id=f, at=XY[A], msg=0xe6, only=True))
    A = gp(1, 0, near=(1000, 1000), d=0, tol=250); B = s.planet(0, 1, near=XY[A], d=1350, tol=90)
    f = s.gate(1, A, B, '0:1')
    s.case('R2', 'refusal order', 'player 1 Laser DD from own 100/250 gate %d to player 0\'s gate %d, %d ly (over 5 x 250)'
           % (A, B, dist(XY[A], XY[B])), 'stays; only 0xe5 (destination owner)', '0xe3 (range) first',
           dict(kind='fleet', owner=1, id=f, at=XY[A], msg=0xe5, only=True))
    A = gp(1, 0); B = gp(0, 0, near=XY[A], d=150)
    f = s.gate(1, A, B, '3:1')
    s.case('R3', 'refusal order', 'player 1 502 kT freighter from own 100/250 gate %d to player 0\'s gate %d' % (A, B),
           'stays; only 0xe5 (destination owner)', '0xe4 (mass) first',
           dict(kind='fleet', owner=1, id=f, at=XY[A], msg=0xe5, only=True))
    A = gp(1, 0); B = gp(0, 0, near=XY[A], d=150)
    f = s.gate(0, A, B, '%d:1' % H502, cargo=(50, 0, 0, 10))
    s.case('R4', 'refusal order', 'player 0 502 kT freighter with 50 kT ironium and 10 kT colonists at player 1\'s gate %d '
           '(friend) to own gate %d' % (A, B), 'stays full; only 0x15e (colonists); planet %d surface +0' % A,
           '0xe4 (mass) after the minerals were unloaded',
           dict(kind='fleet', owner=0, id=f, at=XY[A], cargo=(50, 0, 0, 10), surface=(A, 0), msg=0x15e, only=True))
    A = gp(0, 0, near=(2200, 1000), d=0, tol=250); B = s.planet(0, 7, near=XY[A], d=1350, tol=90)
    f = s.gate(0, A, B, '%d:1' % H502, cargo=(50, 0, 0, 0))
    s.case('R5', 'refusal order', 'player 0 502 kT freighter with 50 kT ironium, own 100/250 gate %d to own any/any %d, '
           '%d ly (over range and over mass)' % (A, B, dist(XY[A], XY[B])),
           'stays empty; only 0xe3 (range before mass); planet %d surface +50' % A, '0xe4 (mass) first',
           dict(kind='fleet', owner=0, id=f, at=XY[A], cargo=(0, 0, 0, 0), surface=(A, 50), msg=0xe3, only=True))
    A = s.planet(0, SB_NOGATE)
    pt = (XY[A][0] + 100 if XY[A][0] < 1600 else XY[A][0] - 100, XY[A][1])
    f = s.fleet(0, XY[A], '%d:1' % FR, planet=A, wps=' to %d %d warp 11' % pt)
    s.case('R6', 'refusal order', 'player 0 freighter (no Jump Gate) at own planet %d without a gate, warp 11 to deep '
           'space' % A, 'stays; only 0xde (no source gate)', '0x147 (destination not a planet) first',
           dict(kind='fleet', owner=0, id=f, at=XY[A], msg=0xde, only=True))
    pct = gate_pct(0, 6, 100, 491)
    for i in range(6):
        A = s.planet(0, 1); B = s.planet(0, 7, near=XY[A], d=100)
        f = s.gate(0, A, B, '%d:1,%d:1' % (H491, DD))
        s.case('W%d' % i, 'O-61 roll', 'Heavy 491 (danger %d%%, lost with %d%%) and a Laser DD, gate %d to %d'
               % (pct, pct // 3, A, B), 'at planet %d with the Laser DD, with or without the Heavy (a design wiped out by '
               'the roll counts once: 2 - 1 = 1)' % B, 'fleet gone (0xe7) whenever the Heavy is destroyed',
               dict(kind='fleet', owner=0, id=f, at=XY[B], has=DD))
    for c in s.cases:
        c['id'] = c['id'].replace('GT-001', 'GT-003')
    return s


def main():
    if sys.argv[1:2] == ['--three']:
        s = build3()
        if sys.argv[2:] == ['--list']:
            for c in s.cases:
                print('| %s | %s | %s | %s | %s |' % (c['id'], c['pred'], c['what'], c['expect'], c['alt']))
            return
        out = sys.argv[2]
        open(os.path.join(out, 'gt003.spec'), 'w').write(HEAD3 + ''.join(s.planets) + '\n'.join(s.lines) + '\n')
        json.dump(s.cases, open(os.path.join(out, 'cases3.json'), 'w'), indent=1)
        return
    if sys.argv[1:2] == ['--two']:
        s = build2()
        if sys.argv[2:] == ['--list']:
            for c in s.cases:
                print('| %s | %s | %s | %s | %s |' % (c['id'], c['pred'], c['what'], c['expect'], c['alt']))
            return
        out = sys.argv[2]
        open(os.path.join(out, 'gt002.spec'), 'w').write(HEAD2 + ''.join(s.planets) + '\n'.join(s.lines) + '\n')
        json.dump(s.cases, open(os.path.join(out, 'cases2.json'), 'w'), indent=1)
        return
    s = build()
    if sys.argv[1:] == ['--list']:
        print('| Case | Prediction | Setup | Predicted | Rules out |\n|---|---|---|---|---|')
        for c in s.cases:
            print('| %s | %s | %s | %s | %s |' % (c['id'], c['pred'], c['what'], c['expect'], c['alt']))
        return
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'gt001.spec'), 'w').write(s.text())
    json.dump(s.cases, open(os.path.join(out, 'cases.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
