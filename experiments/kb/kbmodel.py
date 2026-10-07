#!/usr/bin/env python3
"""KB predictions from the public KERNEL.md rules (no private material).

  python3 experiments/kb/kbmodel.py kb1a|kb1b|kb2a|kb2b|kb2c|kb4a
Prints the predicted end-of-year state for each case. Alternatives (the
readings each case rules out) are printed with 'alt'."""
import math, sys

BASE = [0, 50, 80, 130, 210, 340, 550, 890, 1440, 2330, 3770, 6100, 9870,
        13850, 18040, 22440, 27050, 31870, 36900, 42140, 47590, 53250, 59120,
        65200, 71490, 77990, 84700]

def tdiv(a, b):
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q

def hab(env, c, lo, hi, cap=15):
    neg = 0; hostile = False
    for i in range(3):
        if env[i] < lo[i]: hostile = True; neg += min(cap, lo[i] - env[i])
        elif env[i] > hi[i]: hostile = True; neg += min(cap, env[i] - hi[i])
    if hostile: return -neg
    S = 0; M = 10000
    for i in range(3):
        d = abs(env[i] - c[i]); w = (c[i] - lo[i]) if env[i] < c[i] else (hi[i] - c[i])
        e = 100 - tdiv(100 * d, w); S += e * e
        if 2 * d - w > 0: M = tdiv(M * (2 * w - (2 * d - w)), 2 * w)
    return tdiv(int(math.sqrt(S / 3) + 0.9) * M, 10000)

def maxpop(h, joat=False, obrm=False, additive=False):
    m = 100 * h if h >= 5 else 500
    if additive:
        return m + (m // 5 if joat else 0) + (m // 10 if obrm else 0)
    if joat: m += m // 5
    if obrm: m += m // 10
    return m

def grow(P, k, h, mx, G):
    if P == 0: return P, k
    if h < 0:
        t = max(1, tdiv(-h * P, 10)); q = t // 100; r = t - 100 * q
        k -= r
        if k < 0: k += 100; q += 1
        return P - q, k
    g = G * h
    if P < mx // 4: pass
    elif P < mx:
        c = 1000 * P // mx
        if g < 1000: g = g * (1000 - c) ** 2 // 562500
        else: g = 10 * ((g // 10) * (1000 - c) ** 2 // 562500)
    elif P <= mx + 10: return P, k
    else:
        c = 1000 * P // mx
        g = 4 * max(-300, tdiv(c, -10) + 99)
    t = tdiv(g * P, 100)
    if t >= 10000000: t = (g // 100) * P
    q = tdiv(t, 100); r = t - 100 * q
    if q == 0 and r == 0: r = 1
    k += r
    if k >= 100: q += 1; k -= 100
    if k < 0: q -= 1; k += 100
    return P + q, k

def eff_pop(P, mx, cap2=True):
    if P <= mx: return P
    E = mx + (P - mx) // 2
    return min(2 * mx, E) if cap2 else E

def resources(P, mx, factories, R0=10, F=10, Fo=10, cap2=True):
    E = eff_pop(P, mx, cap2)
    maxF = max(10, mx * Fo // 100)
    oper = max(1, min(maxF, P * Fo // 100))
    n = min(factories, oper)
    r = E // R0 + (F * n + 9) // 10
    return r if r > 0 or P == 0 else 1

def cost(L, levels):
    return BASE[L] + 10 * sum(levels)

def research(add, levels, accum, cur):
    levels = list(levels); L = accum[cur] + add
    while levels[cur] < 26 and L >= cost(levels[cur] + 1, levels):
        L -= cost(levels[cur] + 1, levels); levels[cur] += 1
    accum = list(accum); accum[cur] = L
    return levels, accum

def mine(conc, frac, m, eff=10, home=False, clamp10=True):
    used = 30 if home and conc < 30 else conc
    prod = used * m; amt = prod * eff // 10
    gain, rem = amt // 100, amt % 100
    p = prod // 100
    while p > 0 and conc > 1:
        if conc > 100: cc = 100
        elif conc >= 25: cc = conc
        elif conc >= 5: cc = 25
        else: cc = 10 if clamp10 else 25
        s = frac or 256
        need = (s * 12500 // 256) // cc
        if need <= p:
            p -= need; conc -= 1; frac = 0; continue
        fp = (need - p) * 256 // (12500 // cc)
        if fp < 1: fp = 1
        if fp >= s: fp = s - 1
        frac = fp
        if frac == 0: conc -= 1
        break
    return gain, rem, conc, frac

def defenses_max(h, cap=True, floor=True):
    v = 4 * h
    if floor: v = max(10, v)
    if cap: v = min(100, v)
    return v

def kb1a():
    G = 15
    p0 = ([50] * 3, [15] * 3, [85] * 3); p1 = ([50] * 3, [40] * 3, [60] * 3)
    print("KB-1A (player 0 JOAT+OBRM, player 1 JOAT 40..60)")
    # planet 13
    h = hab([70, 50, 50], *p0); mx = maxpop(h, True, True); mxa = maxpop(h, True, True, additive=True)
    print(f"  13: hab {h}, max {mx}; pop 10430 -> {grow(10430, 0, h, mx, G)}; alt additive max {mxa} -> {grow(10430, 0, h, mxa, G)}")
    r13 = resources(10430, mx, 0)
    # planet 9
    mx9 = maxpop(100, True, True)
    r9 = resources(45000, mx9, 10); r9a = resources(45000, mx9, 10, cap2=False)
    print(f"  9: max {mx9}; pop 45000 -> {grow(45000, 0, 100, mx9, G)}; resources {r9} (alt no 2·max limit {r9a})")
    # planet 12 mining
    g = [mine(c, 0, 500) for c in (4, 100, 100)]
    alt = mine(4, 0, 500, clamp10=False)
    print(f"  12: pop 5000 -> {grow(5000, 0, 100, mx9, G)}; mining (gain, rem, conc, frac) {g}; alt clamp 25 for ironium {alt}")
    r12 = resources(5000, mx9, 0)
    # planet 16 defenses
    P16, _ = grow(5000, 0, 100, mx9, G)
    oper = lambda md, P: min(md, 1000, -(-P // 25))
    r16 = resources(5000, mx9, 0)
    b = oper(defenses_max(100), P16) - 95
    ba = oper(defenses_max(100, cap=False), P16) - 95
    nb = min(b, r16 // 15)
    print(f"  16: pop after growth {P16}; operable defenses {oper(defenses_max(100), P16)}; builds {nb} -> {95 + nb} defenses, "
          f"minerals {1000 - 5 * nb} each; resources {r16}, leftover {r16 - 15 * nb}; alt no cap of 100: operable "
          f"{oper(defenses_max(100, cap=False), P16)}, would build {min(ba, r16 // 15)} whole units")
    r17 = resources(250, mx9, 10)
    hw = [mine(c, 0, 10, home=True) for c in (30, 30, 89)]
    print(f"  17 (homeworld): pop 250 -> {grow(250, 0, 100, mx9, G)}; resources {r17}; mining {hw} (germanium +1 with chance 90%)")
    tot = r17 + r9 + r12 + r13 + (r16 - 15 * nb)
    lv, ac = research(tot, [3] * 6, [0] * 6, 0)
    lva, aca = research(tot - r9 + r9a, [3] * 6, [0] * 6, 0)
    print(f"  player 0 research {tot} (17 {r17}, 9 {r9}, 12 {r12}, 13 {r13}, 16 leftover {r16 - 15 * nb}) -> energy {lv[0]} accum {ac[0]}; "
          f"alt no 2·max limit: {tot - r9 + r9a} -> energy {lva[0]} accum {aca[0]}")
    # player 1
    h10 = hab([90, 50, 50], *p1); h10a = hab([90, 50, 50], *p1, cap=99)
    h11 = hab([90, 90, 50], *p1); h11a = hab([90, 90, 50], *p1, cap=99)
    print(f"  10: hab {h10} (alt uncapped {h10a}); pop 1000 -> {grow(1000, 0, h10, 600, G)} (alt {grow(1000, 0, h10a, 600, G)})")
    print(f"  11: hab {h11} (alt uncapped {h11a}); pop 1000 -> {grow(1000, 0, h11, 600, G)} (alt {grow(1000, 0, h11a, 600, G)})")
    mxh = maxpop(h10, True)
    r10 = resources(1000, mxh, 10); P10, _ = grow(1000, 0, h10, mxh, G)
    md = defenses_max(h10); od = min(md, 1000, -(-P10 // 25)); nb10 = min(max(0, od - 5), r10 // 15)
    print(f"  10: max {mxh}, resources {r10}, maximum defenses {md}, operable {od}: builds {nb10} -> {5 + nb10}, minerals {100 - 5 * nb10} each, "
          f"leftover {r10 - 15 * nb10}; alt no floor: maximum {defenses_max(h10, floor=False)}, builds 0")
    rm = [mine(c, 0, min(4000, 80 * 2 * 27)) for c in (68, 78, 76)]
    rma = [mine(c, 0, 80 * 2 * 27) for c in (68, 78, 76)]
    print(f"  14 (unowned, remote-mined by 4320 robot points, capped at 4000): (gain, rem, conc, frac) {rm}; alt no cap {rma}")

def ar_resources(P, mx, energy, h, R0=10):
    E = eff_pop(P, mx)
    r = int(math.sqrt((E / R0) * max(1, energy)) * max(25, h) * 0.1 + 0.999)
    return r if r > 0 or P == 0 else 1

def kb1b():
    G = 15
    print("KB-1B (player 1 AR, tech 26)")
    hulls = {13: ('Orbital Fort', 2500, 2505, (114, 97, 14), 100, 0), 9: ('Space Dock', 5000, 5005, (100, 86, 95), 3, 0),
             12: ('Space Station', 10000, 10005, (15, 82, 45), 100, 8), 10: ('Ultra Station', 20000, 20005, (94, 104, 24), 100, 0),
             11: ('Death Star', 30000, 30005, (79, 49, 13), 100, 0)}
    R = 0; Ra = 0
    for n, (hull, mx, P, conc, h, robots) in hulls.items():
        m = math.isqrt(P) + robots
        g = [mine(c, 0, m) for c in conc]
        P2, k2 = grow(P, 0, h, mx, G)
        R += ar_resources(P2, mx, 26, h); Ra += ar_resources(P2, mx, 26, h) if h >= 25 else int(math.sqrt((eff_pop(P2, mx) / 10) * 26) * h * 0.1 + 0.999)
        line = (f"  {n}: {hull}, hab {h}, max {mx}: pop {P} -> {(P2, k2)}; alt habitability maximum {maxpop(h)} -> {grow(P, 0, h, maxpop(h), G)}; "
                f"AR mines {math.isqrt(P)}+{robots} = {m}: (gain, rem, conc, frac) {g} (+1 possible where rem > 0)")
        if robots:
            line += f"; alt without the miner: {[mine(c, 0, math.isqrt(P)) for c in conc]}"
        print(line)
    P8, _ = grow(250, 0, 100, 10000, G); R += ar_resources(P8, 10000, 26, 100); Ra += ar_resources(P8, 10000, 26, 100)
    print(f"  8 (homeworld, Space Station): pop 250 -> {grow(250, 0, 100, 10000, G)}")
    print(f"  player 1 score record R (after growth) = {R}; alt without the max(25, hab) floor: {Ra}")
    print("  12: Auto Mines, Auto Factories, Auto Defenses ×10: none built (AR maximum mines, factories and defenses are 0); "
          "queue unchanged; mines, factories and defenses stay 0; surface minerals 1000 + mining only")

FIELDS = ['energy', 'weapons', 'propulsion', 'construction', 'electronics', 'biotech']

def owner_cost(c, tech, req, bet=False):
    """COMPONENTS.md "Cost for an owner", steps 1 and 3 (no PRT step)."""
    if any(req): m = min(tech[i] - req[i] for i in range(6) if req[i] > 0)
    else: m = min(tech)
    if m > 0:
        d = min(5 * min(m, 19), 80) if bet else min(4 * min(m, 19), 75)
        c = max(1, c - (c * d + 50) // 100) if c else 0
    elif bet and any(req):
        c *= 2
    return c

def research_switch(add, levels, accum, cur, mode):
    """KERNEL.md Research allocation. mode: 'same', 'lowest', or
    'same26' (a stored "same" that reaches 26: leftover to the lowest field,
    then 'lowest' switching for the rest of the year). Returns levels,
    accum, current field and the fields levelled in order."""
    levels = list(levels); accum = list(accum); accum[cur] += add; trail = []
    while True:
        if levels[cur] < 26 and accum[cur] >= cost(levels[cur] + 1, levels):
            accum[cur] -= cost(levels[cur] + 1, levels); levels[cur] += 1
            trail.append(f"{FIELDS[cur]} {levels[cur]}")
            switch = mode == 'lowest' or (mode == 'same26' and (levels[cur] == 26 or trail[:-1]))
            if levels[cur] == 26 and mode in ('same', 'same26'): switch = True
            if switch:
                new = min(range(6), key=lambda f: (levels[f], f))
                if new != cur: accum[new] += accum[cur]; accum[cur] = 0; cur = new
            continue
        return levels, accum, cur, trail

def kb2a():
    print("KB-2A")
    tech0 = [3] * 6
    hull = owner_cost(50, tech0, [0, 0, 0, 2, 0, 0], bet=True)
    qj5 = owner_cost(3, tech0, [0] * 6, bet=True)
    bat = owner_cost(1, tech0, [0] * 6, bet=True)
    rmm = owner_cost(100, tech0, [0, 0, 0, 2, 1, 0], bet=True)
    one = hull + qj5 + bat + 2 * rmm; x = 10 * one
    print(f"  player 1 Scrap design owner cost: Mini-Miner {hull} + Quick Jump 5 {qj5} + Bat Scanner {bat} + 2 x Robo-Mini-Miner {rmm} = {one}; x = {x}")
    r8 = resources(250, 12000, 10); r13 = resources(5000, 12000, 0); r9 = resources(3000, 12000, 0)
    r12 = resources(2000, 12000, 0); r16 = resources(4000, 12000, 0)
    bonus = x * r13 // (x + r13)
    print(f"  13: resources {r13}, scrap bonus trunc({x}·{r13}/{x + r13}) = {bonus} (messages 0x5c/0x5d show {bonus}); "
          f"minerals 9C/20 of the fleet's cost added to the surface")
    print(f"  9: Planetary Scanner removed (message 0xb9), queue freed (0x3e); {r9} resources to research")
    print(f"  12: packet removed (message 0x129), queue freed (0x3e); {r12} resources to research; surface 1000 each + mining")
    print(f"  16: zero-item queue: no research from its {r16} resources, no message")
    tot = r8 + r13 + bonus + r9 + r12
    for name, t in (('predicted', tot), ('alt no bonus', tot - bonus), ('alt bonus = x', tot - bonus + x),
                    ('alt zero-item queue sends all to research', tot + r16)):
        lv, ac, cur, tr = research_switch(t, tech0, [0] * 6, 0, 'same')
        print(f"  player 1 {name}: research {t} -> levels {lv}, stored {ac}, levelled {tr}")
    lv1 = [25, 0, 0, 5, 5, 5]; acc1 = [85080, 0, 0, 0, 0, 0]
    t1 = resources(250, 12000, 10) + resources(11000, 12000, 0)
    for name, mode in (('predicted (lowest for the rest of the year)', 'same26'), ('alt "same" kept after the move', 'same')):
        lv, ac, cur, tr = research_switch(t1, lv1, acc1, 0, mode)
        print(f"  player 0 {name}: research {t1} -> levels {lv}, stored {ac}, current {FIELDS[cur]}, levelled {tr}; next field stays \"same\" (alt: the stored choice becomes \"lowest\")")

def kb2b():
    print("KB-2B (slower tech; research as in KX-003 S3L: player 0 weapons 355, player 1 Super Stealth energy 95; 2 players)")
    lv = [3] * 6
    def slow(stored, add, f):
        L = 2 * stored + add; levels = list(lv)
        while L >= 2 * cost(levels[f] + 1, levels): L -= 2 * cost(levels[f] + 1, levels); levels[f] += 1
        return levels[f], (L + 1) // 2
    w0 = slow(0, 355, 1); e1 = slow(0, 95, 0)
    se = (95 // 2) // 2; sw = (355 // 2) // 2
    print(f"  player 0: weapons level {w0[0]}, stored {w0[1]}")
    print(f"  player 1: own energy level {e1[0]}, stored {e1[1]}; stolen s: energy {se}, weapons {sw} (messages 0x159 show {se} and {sw})")
    print(f"  player 1 predicted stored: energy {e1[1] + (se + 1) // 2}, weapons {(sw + 1) // 2} (stolen halved rounding up)")
    print(f"  alt full scale: energy {e1[1] + se}, weapons {sw}; alt halved truncating: energy {e1[1] + se // 2}, weapons {sw // 2}")

def kb2c():
    print("KB-2C (player 1 gravity immune, temperature and radiation 45..55, reach ±3)")
    print("  10: 20/47/50, capacity gravity 0 (immune) + temperature 3 + radiation 0 = 3: Terraform x5 cut to x3 (message 0x12f), "
          "3 built (300 resources) -> 20/50/50, item gone; alt gravity counted: capacity 6, x5 kept")
    print("  11: 10/50/50, capacity 0: Terraform x2 removed (message 0x12f), nothing built, 10/50/50; alt gravity counted: units built on gravity")

QJ5 = [0, 0, 25, 100, 100, 100, 180, 500, 800, 900, 1080]

def ife(f): return f - 15 * f // 100

def fuel_tenths(stacks, cargo, L):
    """KERNEL.md "Fuel cost": stacks = [(f, n, m, cap)] in the fleet's design
    order; cargo goes to increasing f, equal f in that order."""
    order = sorted(range(len(stacks)), key=lambda i: stacks[i][0]); left = cargo; t = 0
    for i in order:
        f, n, m, cap = stacks[i]; c = min(left, n * cap); left -= c
        t += f * L * (n * m + c) // 2000
    return t

def mg(t): return (t + 9) // 10

def place(x0, y0, x1, y1, A):
    D = math.hypot(x1 - x0, y1 - y0)
    if math.trunc(D - 0.99999) < A: return x1, y1
    r = lambda d: math.trunc(d * A / D + (0.5 if d > 0 else -0.5))
    return x0 + r(x1 - x0), y0 + r(y1 - y0)

def kb4a():
    print("KB-4A (player 0 IT + IFE, tech 26)")
    f6, f9 = ife(QJ5[6]), ife(QJ5[9])
    print(f"  G1: 100 + 50 = 150; G2: 230 + 50 capped at 250 (alt uncapped 280)")
    print(f"  X1: 1000 + 200 = 1200; X2: 2150 + 200 capped at 2250 (alt 2350)")
    tE = fuel_tenths([(f6, 1, 17, 0)], 0, 36); tEa = fuel_tenths([(QJ5[6], 1, 17, 0)], 0, 36)
    print(f"  E: f(6) = {f6} with IFE: {tE} tenths -> {mg(tE)} mg, fuel {300 - mg(tE)}, at {place(1020, 1030, 1120, 1030, 36)} (alt no IFE: {300 - mg(tEa)})")
    leg = mg(fuel_tenths([(f6, 1, 17, 0)], 0, 300)); C1000 = fuel_tenths([(f6, 1, 17, 0)], 0, 1000) // 10
    print(f"  K: whole leg {leg} mg > 20; R = trunc(20000/{C1000}) = {20000 // C1000} >= 36: moves 36, fuel {20 - mg(tE)}, warp stays 6, no out-of-fuel message (alt: warp lowered)")
    kill = max(1, 70 * ((86 - (15 + 85) // 2) // 2) // 100)
    print(f"  H: colonists 70 - {kill} = {70 - kill} (message 0x74); H0 (stationary): 70")
    tQ = fuel_tenths([(f6, 1, 29, 70), (f6, 1, 64, 210)], 111, 36); tQa = fuel_tenths([(f6, 1, 64, 210), (f6, 1, 29, 70)], 111, 36)
    print(f"  Q: Small Freighter first: {tQ} tenths -> {mg(tQ)} mg, fuel {300 - mg(tQ)} (alt Medium first: {tQa} -> fuel {300 - mg(tQa)})")
    C9 = fuel_tenths([(f9, 1, 17, 0)], 0, 1000) // 10; R = 5000 // C9
    tx, ty = place(1020, 1030, 1120, 1030, 36)
    print(f"  C: f(9) = {f9}, C1000 = {C9}, R = {R}: moves {R} ly toward E's end {tx, ty} -> {place(1020, 1010, tx, ty, R)}, "
          f"fuel 0, out of fuel, warp lowered to 1; its waypoint takes E's end position")
    tT = fuel_tenths([(ife(QJ5[5]), 1, 29, 70)], 0, 25)
    print(f"  T1: holds at planet 9 (1208, 1297), task kept; T2: unloads 10 kT on planet 12, moves to (1245, 1183), fuel {100 - mg(tT)}")
    print("  F1: 10 -> 300 (friend's Space Station); F2: 400 -> 300; F3: 10 (player 0 is neutral to player 1); "
          "F4: 10 (Orbital Fort has no dock); F5: 10 -> 300")

if __name__ == '__main__':
    {'kb1a': kb1a, 'kb1b': kb1b, 'kb2a': kb2a, 'kb2b': kb2b, 'kb2c': kb2c, 'kb4a': kb4a}[sys.argv[1]]()
