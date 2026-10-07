#!/usr/bin/env python3
"""Generate the FM-003 FleetLab spec and pre-run predictions.

FM-003 follows up FM-002 on PG001 2407 (same method, one turn): chains of
fleet targets in every id order, fleets chasing each other, fuel gained at
free speed, the distance charged when a fleet arrives beyond warp^2, and one
more fuel-threshold point.
Usage: gen.py OUTDIR
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from fmlib import DES, fuel_fm001, write

fleets = []


def add(group, desc, start, wps, ships={0: 1}, fuel=None, cargo=(0, 0, 0, 0), **kw):
    if fuel is None:
        fuel = sum(DES[d][3] * c for d, c in ships.items())
    f = dict(group=group, desc=desc, start=start, wps=wps, ships=ships, fuel=fuel, cargo=cargo)
    f.update(kw)
    fleets.append(f)
    return len(fleets) - 1


def wp(s, dx, dy, warp):
    return ("wp", s[0] + dx, s[1] + dy, warp)


# CH: chain A -> B -> Z (A chases B at warp 9, B chases Z at warp 9, Z moves
# +60x at warp 5, 15 and 10 ly apart), in all six id orders.
for k, order in enumerate(["ABZ", "AZB", "BAZ", "BZA", "ZAB", "ZBA"]):
    y = [1012, 1027, 1042, 1057, 1072, 1087][k]
    start = {"A": (1200, y), "B": (1215, y), "Z": (1225, y)}
    ids = {r: len(fleets) + order.index(r) for r in "ABZ"}
    for r in order:
        if r == "Z":
            add("CH", f"{order}: Z +60x warp 5", start["Z"], [wp(start["Z"], 60, 0, 5)], role="Z", order=order)
        else:
            t = "B" if r == "A" else "Z"
            add("CH", f"{order}: {r} chases {t} warp 9", start[r], [("wpf", ids[t], 9)], role=r, order=order)
# CH-S: B chases a stationary Z; A chases B.
y = 1102
ids = len(fleets)
add("CH", "S: A chases B warp 9", (1200, y), [("wpf", ids + 1, 9)], role="A", order="S")
add("CH", "S: B chases stationary Z warp 9", (1215, y), [("wpf", ids + 2, 9)], role="B", order="S")
add("CH", "S: Z stationary (no waypoint)", (1225, y), [], role="Z", order="S")

# MU: two fleets chasing each other along x (low id west, high id east).
MU = [(6, 1, 1), (40, 3, 3), (60, 5, 5), (20, 3, 4), (10, 4, 1), (30, 5, 3)]
for k, (gap, wl, wh) in enumerate(MU):
    y = 1300 + 12 * k
    lo = len(fleets)
    add("MU", f"low id warp {wl}, gap {gap}", (1150, y), [("wpf", lo + 1, wl)], gap=gap, wl=wl, wh=wh)
    add("MU", f"high id warp {wh}", (1150 + gap, y), [("wpf", lo, wh)], gap=gap, wl=wl, wh=wh)
# MU-D: diagonal mutual chase, 20 ly apart along (12,16), warp 4 each.
lo = len(fleets)
add("MU", "diagonal low id warp 4", (1300, 1300), [("wpf", lo + 1, 4)], gap=None)
add("MU", "diagonal high id warp 4", (1312, 1316), [("wpf", lo, 4)], gap=None)

# FG: fuel gained or not at free speed / standing still (deep space).
for k, (ships, fuel, wps, desc) in enumerate([
        ({0: 1}, 100, [(50, 0, 1)], "QJ5 scout fuel 100, warp 1"),
        ({0: 1}, 0, [(50, 0, 1)], "QJ5 scout fuel 0, warp 1 (repeats FM-002 N27)"),
        ({0: 1}, 100, [], "QJ5 scout fuel 100, no waypoint"),
        ({0: 1}, 0, [], "QJ5 scout fuel 0, no waypoint"),
        ({0: 1}, 100, [(50, 0, 2)], "QJ5 scout fuel 100, warp 2"),
        ({5: 1}, 100, [(50, 0, 1)], "AD8 scout fuel 100, warp 1"),
        ({1: 1}, 50, [(50, 0, 1)], "QJ5 freighter fuel 50, warp 1"),
        ({0: 5}, 0, [(50, 0, 1)], "5 QJ5 scouts fuel 0, warp 1"),
        ({0: 1}, 299, [(50, 0, 1)], "QJ5 scout fuel 299, warp 1")]):
    s = (1010, 1300 + 9 * k)
    add("FG", desc, s, [wp(s, dx, dy, w) for dx, dy, w in wps], ships=ships, fuel=fuel)

# FA: fuel charged on an arrival beyond warp^2 (freighter + 70 kt, warp 5).
for k, (dx, dy) in enumerate([(7, 25), (24, 8), (25, 0)]):
    s = (1080 + 30 * k, 1215)
    add("FA", f"warp 5 arrive ({dx:+d},{dy:+d}) d={math.hypot(dx, dy):.3f}, freighter 70kt Ir",
        s, [wp(s, dx, dy, 5)], ships={1: 1}, cargo=(70, 0, 0, 0))

# K: r = 1960 (warp 6, table 180): m*e*d = 21960.
s = (1350, 1100)
add("K", "r=1960: warp 6 arrive +2x, freighter 30kt Ir", s, [wp(s, 2, 0, 6)], ships={1: 1}, cargo=(30, 0, 0, 0))


def mutual(gap, a, b, N, step):
    x = [0.0, float(gap)]
    sp = [step(a, N), step(b, N)]
    done = [False, False]
    for _ in range(N):
        for i in (0, 1):
            if done[i]:
                x[i] = x[1 - i]
                continue
            d = abs(x[1 - i] - x[i])
            if d <= sp[i]:
                x[i] = x[1 - i]
                done[i] = True
            else:
                x[i] += sp[i] if i == 0 else -sp[i]
    return x


def describe(i, f, mass):
    g = f["group"]
    if g == "CH":
        return "see README"
    if g == "MU":
        if f["gap"] is None:
            return "see README"
        gap, a, b = f["gap"], f["wl"] ** 2, f["wh"] ** 2
        out = []
        for name, N, st in (("4 steps trunc(w2/4)", 4, lambda w, N: math.floor(w / N)),
                            ("5 steps ceil(w2/5)", 5, lambda w, N: math.ceil(w / N)),
                            ("4 steps exact", 4, lambda w, N: w / N)):
            x = mutual(gap, a, b, N, st)
            out.append(f"{name}: low +{x[0]:g}, high -{gap - x[1]:g}")
        return "; ".join(out)
    if g == "FA":
        w = f["wps"][0]
        d = math.hypot(w[1] - f["start"][0], w[2] - f["start"][1])
        return (f"arrive; fuel at ceil(d)={math.ceil(d)}: {fuel_fm001(mass * 100 * math.ceil(d))}, "
                f"at min(d,25): {fuel_fm001(mass * 100 * min(d, 25))}")
    if g == "K":
        return "m*e*d=21960: fuel 1 if C<18040 (C=18000: tenths rule) else 2"
    if g == "FG":
        return "FM-002 N27: fuel 0 at warp 1 moved 1 ly and gained 1 mg (msg 243)"
    return ""


if __name__ == "__main__":
    write(sys.argv[1] if len(sys.argv) > 1 else ".", "FM-003", fleets, describe)
