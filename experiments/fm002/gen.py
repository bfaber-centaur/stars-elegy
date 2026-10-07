#!/usr/bin/env python3
"""Generate the FM-002 FleetLab spec and pre-run predictions.

FM-002 follows up FM-001 on PG001 2407 (same method, one turn): it pins the
fuel rounding constant, tests fuel on non-integer distances, the arrival
rule just beyond warp^2, distance limits under insufficient fuel, mixed
engines/cargo in one fleet, and fleet-chasing dynamics.
Usage: gen.py OUTDIR
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from fmlib import DES, ENG, fuel_fm001, write

CLO, CHI = 17120, 18199  # C range left open by FM-001
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


def frt(cargo_ir):
    return dict(ships={1: 1}, cargo=(cargo_ir, 0, 0, 0))


# K: fuel threshold. Warp 5 (table 100), axis arrival at +d; m*100*d mod 20000
# = r. Fuel = base + [C >= 20000 - r].
K = [(7, 11, 1800), (42, 3, 1900), (13, 5, 2000), ("dll7", 23, 2100), (6, 6, 2200),
     (1, 7, 2400), (14, 5, 2500), (40, 6, 2600), (30, 7, 2700), (7, 6, 2800)]
for k, (c, d, r) in enumerate(K):
    s = (1350, 1010 + 7 * k)
    kw = dict(ships={4: 1}) if c == "dll7" else frt(c)
    add("K", f"r={r}: warp 5 arrive +{d}x, " + ("DLL7 scout" if c == "dll7" else f"freighter {c}kt Ir"),
        s, [wp(s, d, 0, 5)], r=r, **kw)

# FD: fuel on a non-integer (diagonal) arrival distance, freighter + cargo, warp 5.
def fd_cases():
    floor_c, ceil_c, used = [], [], set()
    for dx in range(1, 18):
        for dy in range(1, 18):
            d = math.hypot(dx, dy)
            if d > 24 or d == int(d) or (dx, dy) in used:
                continue
            for c in range(70, -1, -1):
                m = 31 + c
                f = lambda dd: {fuel_fm001(m * 100 * dd, C) for C in (CLO, CHI)}
                ff, fl, fc = f(d), f(math.floor(d)), f(math.ceil(d))
                if len(ff) == 1 and len(fl) == 1 and ff != fl and len(floor_c) < 3 and dx >= 2 * len(floor_c) + 2:
                    floor_c.append((dx, dy, c)); used.add((dx, dy)); break
                if len(ff) == 1 and len(fc) == 1 and ff != fc and len(ceil_c) < 3 and dy >= 2 * len(ceil_c) + 3:
                    ceil_c.append((dx, dy, c)); used.add((dx, dy)); break
    return floor_c + ceil_c
for k, (dx, dy, c) in enumerate(fd_cases()):
    s = (1010 + 30 * k, 1010)
    add("FD", f"warp 5 arrive ({dx:+d},{dy:+d}) d={math.hypot(dx, dy):.3f}, freighter {c}kt Ir",
        s, [wp(s, dx, dy, 5)], **frt(c))

# A: arrival just beyond warp^2.
for k, (dx, dy, w) in enumerate([(16, 20, 5), (25, 6, 5), (25, 5, 5), (26, 1, 5), (7, 25, 5),
                                 (-16, -20, 5), (1, 1, 1), (4, 2, 2)]):
    s = [(1200, 1015), (1235, 1015), (1270, 1015), (1305, 1010), (1200, 1050), (1260, 1080),
         (1290, 1060), (1305, 1060)][k]
    add("A", f"warp {w} to ({dx:+d},{dy:+d}) d={math.hypot(dx, dy):.3f}", s, [wp(s, dx, dy, w)])

# N: fuel-limited movement, QJ5 scouts.
for k, (dx, dy, w, fuel, n, desc) in enumerate([
        (100, 0, 6, 6, 1, "fuel 6 (FM-001 cost of 36 ly)"),
        (60, 80, 6, 5, 1, "fuel 5, toward (60,80)"),
        (60, 80, 6, 3, 1, "fuel 3, toward (60,80)"),
        (100, 0, 1, 0, 1, "fuel 0, warp 1"),
        (100, 0, 2, 0, 1, "fuel 0, warp 2"),
        (5, 0, 6, 1, 1, "fuel 1, warp 6 arrive +5x"),
        (100, 0, 6, 10, 5, "5 scouts, fuel 10, warp 6"),
        (100, 0, 6, 2, 1, "fuel 2, warp 6")]):
    s = [(1010, 1200), (1020, 1215), (1050, 1215), (1010, 1235), (1010, 1245), (1010, 1255),
         (1010, 1265), (1010, 1275)][k]
    add("N", desc, s, [wp(s, dx, dy, w)], ships={0: n}, fuel=fuel)

# X: mixed engines / cargo in one fleet, warp 7 (+100x).
for k, (ships, cargo, desc) in enumerate([
        ({0: 3, 5: 1}, 0, "3 QJ5 scouts + 1 AD8 scout"),
        ({1: 1, 5: 1}, 0, "QJ5 freighter + AD8 scout"),
        ({1: 1, 5: 1}, 70, "QJ5 freighter + AD8 scout, 70kt Ir")]):
    s = (1180, 1290 + 8 * k + (5 if k else 0))
    add("X", desc, s, [wp(s, 100, 0, 7)], ships=ships, cargo=(cargo, 0, 0, 0),
        fuel=sum(DES[d][3] * c for d, c in ships.items()))

# O: fleet-target dynamics. Indexes are fleet ids.
def pair(desc_t, st, wt, desc_c, sc, warp_c, chaser_first):
    if chaser_first:
        c = add("O", desc_c, sc, [("wpf", len(fleets) + 1, warp_c)])
        t = add("O", desc_t, st, [wt])
    else:
        t = add("O", desc_t, st, [wt])
        c = add("O", desc_c, sc, [("wpf", t, warp_c)])
pair("T1 target, +y warp 9", (1390, 1150), wp((1390, 1150), 0, 100, 9),
     "C1 (low id) chases T1 at warp 5 from 50 ly west", (1340, 1150), 5, True)
pair("T2 target, +y warp 9", (1080, 1300), wp((1080, 1300), 0, 90, 9),
     "C2 (high id) chases T2 at warp 5 from 50 ly east", (1130, 1300), 5, False)
e = len(fleets)
add("O", "E (low id) warp 4, mutual chase with F, 20 ly apart", (1150, 1392), [("wpf", e + 1, 4)])
add("O", "F (high id) warp 3, mutual chase with E", (1170, 1392), [("wpf", e, 3)])
pair("T3 target, -x warp 5, head-on toward C3", (1080, 1250), wp((1080, 1250), -35, 0, 5),
     "C3 warp 5 chases T3, 40 ly apart head-on", (1040, 1250), 5, False)
a = len(fleets)
add("O", "A (low id) warp 9 chases B", (1200, 1240), [("wpf", a + 1, 9)])
add("O", "B warp 9 chases Z", (1215, 1240), [("wpf", a + 2, 9)])
add("O", "Z target, +x warp 5", (1225, 1240), [wp((1225, 1240), 60, 0, 5)])


def describe(i, f, mass):
    g = f["group"]
    if g == "O":
        return "see README"
    w = f["wps"][0]
    s = f["start"]
    tx, ty, warp = w[1], w[2], w[3]
    dx, dy = tx - s[0], ty - s[1]
    d = math.hypot(dx, dy)
    step = warp * warp
    ms = sum(DES[k][1] * c for k, c in f["ships"].items())
    if g == "K":
        e = ENG[DES[list(f["ships"])[0]][2]][2][warp]
        med = mass * e * d
        base = math.floor(med / 20000)
        return f"m*e*d={med:.0f} r={f['r']}: fuel used {base} if C<{20000 - f['r']} else {base + 1}"
    if g == "FD":
        out = [f"arrive; m*e*d={mass * 100 * d:.1f}"]
        for name, dd in (("float d", d), ("floor d", math.floor(d)), ("ceil d", math.ceil(d))):
            out.append(f"{name}: {fuel_fm001(mass * 100 * dd)}")
        return "; ".join(out)
    if g == "A":
        rem = d - step
        fx, fy = s[0] + dx * step / d, s[1] + dy * step / d
        rd = (math.floor(fx + 0.5), math.floor(fy + 0.5))
        return (f"round-end==target: {'arrive' if rd == (tx, ty) else f'stop {rd}'}; "
                f"remaining<1: {'arrive' if rem < 1 else 'stop'}; d<=w2+0.5: {'arrive' if d <= step + 0.5 else 'stop'}")
    if g == "N":
        e = ENG[1][2][warp]
        if e == 0 or f["fuel"] * 20000 >= mass * e * step:
            lim = step
        else:
            lim = f["fuel"] * 20000 / (mass * e)
        out = []
        for name, L in (("floor(limit)", math.floor(lim)), ("float limit", lim)):
            L = min(L, d)
            px, py = s[0] + dx * L / d, s[1] + dy * L / d
            out.append(f"{name} {L:.2f} ly -> ({math.floor(px + .5)},{math.floor(py + .5)})")
        return "FM-001 rule: " + "; ".join(out) + ("; or no move (fuel 0)" if f["fuel"] == 0 else "")
    if g == "X":
        per = 0
        tot = 0
        for k, c in f["ships"].items():
            e = ENG[DES[k][2]][2][warp]
            m = DES[k][1] * c
            per += fuel_fm001(m * e * step)
            tot += m * e * step
        cargo = f["cargo"][0]
        out = f"per-stack {per}, one rounding {fuel_fm001(tot)}"
        if cargo:
            out += (f"; cargo on QJ5 freighter: {fuel_fm001(tot + cargo * 500 * step)}"
                    f", on AD8 scout: {fuel_fm001(tot + cargo * 100 * step)}")
        return out
    return ""


if __name__ == "__main__":
    write(sys.argv[1] if len(sys.argv) > 1 else ".", "FM-002", fleets, describe)
