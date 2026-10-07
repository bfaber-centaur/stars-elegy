#!/usr/bin/env python3
"""KB predictions from the public KERNEL.md rules (no private material).

  python3 experiments/kb/kbmodel.py kb1a|kb1b
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
    print("KB1-A (player 0 JOAT+OBRM, player 1 JOAT 40..60)")
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
    print("KB1-B (player 1 AR, tech 26)")
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

if __name__ == '__main__':
    {'kb1a': kb1a, 'kb1b': kb1b}[sys.argv[1]]()
