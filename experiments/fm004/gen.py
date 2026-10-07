#!/usr/bin/env python3
"""Generate the FM-004 FleetLab spec and case list.

FM-004 tests predictions that the private stars-decomp reading of fleet
movement makes and FM-001..003 did not cover (PG001 2407, one turn, same
method): the distance a fuel-limited fleet covers, the warp a fleet drops to
when it runs dry, fuel gained at free warps above 1, fuel per ship stack in
mixed fleets, which stack carries the cargo, the fuel top-up on a leg the
fleet could afford at departure, starbase refuelling, and a deep-space
waypoint placed on a planet.

The predictions in predictions.tsv were computed from the decomp's model
before the turn was generated (see README.md).
Usage: gen.py OUTDIR
"""
import json, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from fmlib import DES, HEADER, PL, PLANETS, write

HDR = HEADER + ["design 6 clone 0 engine 0", "design 7 clone 0 engine 2",
                "design 8 clone 0 engine 10", "design 9 clone 1 engine 3"]
fleets = []
rows = iter(range(1010, 1395, 6))


def clear(p):
    return all(math.hypot(p[0] - x, p[1] - y) >= 3 for _, x, y in PLANETS)


def add(group, desc, ships, fuel, leg=None, warp=0, cargo=(0, 0, 0, 0), start=None, wps=None, **kw):
    """Default: deep-space start at x=1010 on the next free row, one waypoint
    LEG = (dx, dy) away at WARP."""
    if start is None:
        while True:
            start = (1010, next(rows))
            ends = [start] + ([(start[0] + leg[0], start[1] + leg[1])] if leg else [])
            # partial moves end on the line; keep the whole segment clear of planets
            if all(clear(p) for p in ends) and all(
                    clear((start[0] + leg[0] * t / 50, start[1] + leg[1] * t / 50)) for t in range(51)) if leg else clear(start):
                break
    if wps is None:
        wps = [("wp", start[0] + leg[0], start[1] + leg[1], warp)] if leg else []
    f = dict(group=group, desc=desc, start=start, wps=wps, ships=ships, fuel=fuel, cargo=cargo)
    f.update(kw)
    fleets.append(f)


E = (100, 0)
# LR: fuel-limited distance; the decomp predicts R = fuel*1000 / trunc(tenths/10),
# FM-001..003 fitted floor(fuel*20000/M). These cases differ by 1 ly.
for d, n, w, F, c in [(3, 1, 6, 3, 0), (4, 1, 7, 4, 0), (3, 1, 8, 25, 0), (5, 3, 8, 31, 0),
                      (9, 1, 6, 7, 10), (6, 1, 10, 23, 0)]:
    add("LR", f"{n}x {DES[d][0]} warp {w} fuel {F}" + (f" cargo {c} Ir" if c else ""),
        {d: n}, F, E, w, cargo=(c, 0, 0, 0))
add("LR", "control: QJ5 scout warp 9 fuel 10", {0: 1}, 10, E, 9)

# WD: warp after running dry (decomp: lowest warp whose full-leg cost is
# nonzero, minus one).
add("WD", "FM scout warp 7 fuel 5", {7: 1}, 5, E, 7)
add("WD", "FM scout warp 9 fuel 10", {7: 1}, 10, E, 9)
add("WD", "SD scout warp 8 fuel 10", {6: 1}, 10, E, 8)
add("WD", "RHRS scout warp 8 fuel 10", {8: 1}, 10, E, 8)
add("WD", "FM scout warp 7 fuel 0", {7: 1}, 0, E, 7)
add("WD", "FM scout warp 7 fuel 0, leg 2 ly", {7: 1}, 0, (2, 0), 7)
add("WD", "QJ5 scout warp 7 fuel 0", {0: 1}, 0, E, 7)
add("WD", "FM scout warp 7 fuel 5, arrives at 20 ly", {7: 1}, 5, (20, 0), 7)

# RS: fuel gained at free warps (fuel 100 of 300 unless stated).
for w in (1, 2, 3, 4, 5):
    add("RS", f"FM scout warp {w}", {7: 1}, 100, E, w)
for w in (1, 2, 3, 4, 5, 6, 7):
    add("RS", f"SD scout warp {w}", {6: 1}, 100, E, w)
for w in (4, 6):
    add("RS", f"RHRS scout warp {w}", {8: 1}, 100, E, w)
add("RS", "3 FM scouts warp 2", {7: 3}, 100, E, 2)
add("RS", "QJ5 scout + FM scout warp 2", {0: 1, 7: 1}, 100, E, 2)
add("RS", "SD scout warp 3 fuel 250 (cap)", {6: 1}, 250, E, 3)
add("RS", "SD scout warp 4 arrives at 10 ly", {6: 1}, 100, (10, 0), 4)
add("RS", "SD scout warp 4 arrives at (7,7)", {6: 1}, 100, (7, 7), 4)
add("RS", "FM scout warp 2 arrives at 3 ly", {7: 1}, 100, (3, 0), 2)
add("RS", "control: QJ5 scout warp 1", {0: 1}, 100, E, 1)
add("RS", "control: AD8 scout warp 1", {5: 1}, 100, E, 1)

# MS: mixed-design fleets where per-stack rounding differs from the fitted rule.
for ships, w in [({0: 1, 3: 1}, 2), ({0: 1, 7: 1}, 5), ({3: 2, 4: 1}, 5), ({0: 1, 6: 1}, 8)]:
    add("MS", " + ".join(f"{n}x {DES[d][0]}" for d, n in ships.items()) + f" warp {w}",
        ships, 300 * sum(ships.values()), E, w)

# CA: which stack carries the cargo (QJ5 freighter + LH6 freighter, warp 6).
for c in (70, 100):
    add("CA", f"QJ5 freighter + LH6 freighter, {c} kt Ir, warp 6", {1: 1, 9: 1}, 260, E, 6,
        cargo=(c, 0, 0, 0))

# TU: fuel top-up on a leg affordable at departure.
add("TU", "QJ5 scout warp 9 fuel 102, leg 126", {0: 1}, 102, (126, 0), 9)
add("TU", "QJ5 scout warp 9 fuel 101, leg 126", {0: 1}, 101, (126, 0), 9)
add("TU", "QJ5 freighter 70 kt Ir warp 6 fuel 130, leg 143", {1: 1}, 130, (143, 0), 6,
    cargo=(70, 0, 0, 0))

# DK: starbase refuelling (planet 7 has the homeworld starbase).
h = PL[7]
add("DK", "QJ5 scout at planet 7, fuel 50, no orders", {0: 1}, 50, start=h, wps=[], planet=7)
add("DK", "QJ5 scout at planet 7, fuel 400, no orders", {0: 1}, 400, start=h, wps=[], planet=7)
add("DK", "QJ5 freighter at planet 7, fuel 10, no orders", {1: 1}, 10, start=h, wps=[], planet=7)
add("DK", "QJ5 scout in deep space, fuel 400, no orders", {0: 1}, 400)
add("DK", "QJ5 scout arrives at planet 7 (planet waypoint), warp 5, fuel 100", {0: 1}, 100,
    start=(h[0] - 20, h[1]), wps=[("wpp", 7, 5)])
add("DK", "QJ5 scout leaves planet 7 east 50 ly, warp 5, fuel 100", {0: 1}, 100,
    start=h, wps=[("wp", h[0] + 50, h[1], 5)], planet=7)
p6 = PL[6]
add("DK", "QJ5 scout arrives at planet 6 (no starbase), warp 5, fuel 100", {0: 1}, 100,
    start=(p6[0] - 20, p6[1]), wps=[("wpp", 6, 5)])

# OR: deep-space waypoint exactly on a planet.
add("OR", "QJ5 scout to deep-space waypoint on planet 7, warp 5, fuel 100", {0: 1}, 100,
    start=(h[0], h[1] - 20), wps=[("wp", h[0], h[1], 5)], on_planet_ok=True)
p12 = PL[12]
add("OR", "QJ5 scout to deep-space waypoint on planet 12, warp 5, fuel 100", {0: 1}, 100,
    start=(p12[0] + 20, p12[1]), wps=[("wp", p12[0], p12[1], 5)], on_planet_ok=True)

out = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
here = os.path.dirname(os.path.abspath(__file__))
pred = {}
bp = os.path.join(here, "binpred.tsv")
if os.path.exists(bp):
    for line in open(bp):
        if not line.startswith("id\t"):
            i, rest = line.rstrip("\n").split("\t", 1)
            pred[int(i)] = rest.replace("\t", "; ")
write(out, "FM-004", fleets, lambda i, f, m: pred.get(i, "?"), header=HDR)
json.dump(fleets, open(os.path.join(out, "cases.json"), "w"), indent=0) if out != here else None

# Competing prediction: the description FM-001..003 fitted (experiments/fmcheck.py).
from fmcheck import model
p = os.path.join(out, "predictions.tsv")
lines = open(p).read().splitlines()
hdr = lines[0].split("\t")
rows_ = [dict(zip(hdr, l.split("\t"))) for l in lines[1:]]
outl = [lines[0] + "\tfitted"]
for l, r in zip(lines[1:], rows_):
    end, fuel1, note = model(r, None)
    outl.append(l + f"\tpos={end[0]},{end[1]} fuel={fuel1}" + (f" ({note})" if note else ""))
open(p, "w").write("\n".join(outl) + "\n")
