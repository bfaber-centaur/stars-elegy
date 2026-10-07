#!/usr/bin/env python3
"""Generate the FM-001 FleetLab spec and pre-run predictions.

FM-001 is a one-turn fleet-movement batch on PG001 (2407): every player-0
fleet is replaced by the fleets below, each an isolated scenario in deep
space. Output: fm001.spec (FleetLab input) and predictions.tsv.
Usage: gen.py OUTDIR
"""
import math, os, sys

PLANETS = [(int(a), int(b), int(c)) for a, b, c in
           (p.split() for p in """0 1019 1354;1 1031 1365;2 1045 1108;3 1047 1038;4 1057 1168;5 1085 1086;6 1101 1283;7 1113 1298;8 1130 1383;9 1133 1346;10 1133 1116;11 1146 1073;12 1153 1335;13 1156 1114;14 1159 1365;15 1159 1062;16 1164 1024;17 1221 1348;18 1237 1248;19 1244 1140;20 1246 1343;21 1269 1133;22 1270 1250;23 1301 1084;24 1305 1140;25 1320 1057;26 1322 1175;27 1328 1354;28 1337 1268;29 1339 1113;30 1378 1287;31 1386 1022""".split(';'))]
PL = {i: (x, y) for i, x, y in PLANETS}

# Engine fuel tables, warp 0..10, and engine masses: StarsAPI UNEDITED.MOD
# (documented, not verified here). Item ids are StarsAPI engine ids.
ENG = {1: ("QJ5", 4, [0, 0, 25, 100, 100, 100, 180, 500, 800, 900, 1080]),
       3: ("LH6", 9, [0, 0, 20, 60, 100, 100, 105, 450, 750, 900, 1080]),
       4: ("DLL7", 13, [0, 0, 20, 60, 70, 100, 100, 110, 600, 750, 900]),
       5: ("AD8", 17, [0, 0, 15, 50, 60, 70, 100, 100, 115, 700, 840])}
# design -> (name, mass, engine id, fuel capacity)
DES = {0: ("Scout/QJ5", 18, 1, 300), 1: ("SmallFreighter/QJ5", 31, 1, 130),
       2: ("ColonyShip/QJ5", 56, 1, 200),
       3: ("Scout/LH6", 23, 3, 300), 4: ("Scout/DLL7", 27, 4, 300), 5: ("Scout/AD8", 31, 5, 300)}

fleets = []  # dicts

def add(group, desc, start, wps, ships={0: 1}, fuel=300, cargo=(0, 0, 0, 0), planet=None):
    fleets.append(dict(group=group, desc=desc, start=start, wps=wps, ships=ships, fuel=fuel,
                       cargo=cargo, planet=planet))

def rel(s, dx, dy, warp):
    return ("wp", s[0] + dx, s[1] + dy, warp)

# R: replica of the FM-000 pilot fleet.
s = (1200, 1200); add("R", "pilot replica: +100x at warp 5", s, [rel(s, 100, 0, 5)])

# W: warp sweep, long +x leg (no arrival).
for w in range(1, 11):
    s = (1010, 1004 + 8 * w + (3 if w >= 5 else 0)); add("W", f"warp {w}, +160x", s, [rel(s, 160, 0, w)])

# D: arrival boundary at warp 5 (25 ly).
for dx, dy in [(24, 0), (25, 0), (26, 0), (24, 7), (20, 15), (25, 1), (24, 8), (23, 9), (18, 17),
               (0, -25), (-25, 0), (-24, -7)]:
    i = sum(1 for f in fleets if f["group"] == "D")
    s = (1190 + 60 * (i % 4), 1020 + 45 * (i // 4) if i < 8 else 1300 + 30 * (i // 4 - 2))
    add("D", f"warp 5 to ({dx:+d},{dy:+d}), dist {math.hypot(dx, dy):.3f}", s, [rel(s, dx, dy, 5)])

# Q: direction / rounding of partial moves.
for k, (dx, dy, w) in enumerate([(90, 37, 5), (-90, 37, 5), (90, -37, 5), (-90, -37, 5),
                                 (70, 60, 5), (-70, -60, 5), (70, -60, 5), (-70, 60, 5)]):
    s = (1110 + 50 * (k % 4) + (30 if dx < 0 else 0), 1190 + 50 * (k // 4) + (40 if dy < 0 else 0))
    add("Q", f"warp {w} toward ({dx:+d},{dy:+d})", s, [rel(s, dx, dy, w)])

# F: fuel versus arrival distance, warp 5, single scout.
for k, d in enumerate([1, 5, 11, 12, 16, 17, 22, 23]):
    s = (1350, 1180 + 9 * k); add("F", f"warp 5 arrive at +{d}x", s, [rel(s, d, 0, 5)])

# M: mass at warp 6 (36 ly), +100x, no arrival.
for k, (ships, cargo, desc) in enumerate([
        ({0: 2}, (0, 0, 0, 0), "2 scouts"), ({0: 3}, (0, 0, 0, 0), "3 scouts"),
        ({0: 5}, (0, 0, 0, 0), "5 scouts"), ({0: 7}, (0, 0, 0, 0), "7 scouts"),
        ({1: 1}, (0, 0, 0, 0), "freighter empty"), ({1: 1}, (1, 0, 0, 0), "freighter 1kt Ir"),
        ({1: 1}, (35, 0, 0, 0), "freighter 35kt Ir"), ({1: 1}, (70, 0, 0, 0), "freighter 70kt Ir"),
        ({2: 1}, (0, 0, 0, 0), "colony ship"), ({0: 1, 1: 1}, (0, 0, 0, 0), "scout+freighter")]):
    s = (1180, 1072 + 6 * k)
    fuel = sum(DES[d][3] * c for d, c in ships.items())
    add("M", f"warp 6 +100x, {desc}", s, [rel(s, 100, 0, 6)], ships=ships, fuel=fuel, cargo=cargo)

# E: engines.
for k, (d, w) in enumerate([(3, 6), (4, 6), (5, 6), (3, 9), (4, 9), (5, 9)]):
    s = (1010, 1095 + 7 * k + (2 if k >= 3 else 0)); add("E", f"{DES[d][0]} warp {w} +160x", s, [rel(s, 160, 0, w)], ships={d: 1})

# N: insufficient fuel, warp 6 +100x (and one warp 9).
for k, (fuel, w) in enumerate([(0, 6), (1, 6), (3, 6), (5, 6), (10, 9)]):
    s = (1010, 1150 + 8 * k); add("N", f"fuel {fuel}, warp {w} +160x", s, [rel(s, 160, 0, w)], fuel=fuel)

# C: waypoint chaining at warp 5.
for k, (legs, desc) in enumerate([
        ([(10, 0, 5), (50, 0, 5)], "wp1 +10x, wp2 +50x"),
        ([(10, 0, 5), (10, 30, 5)], "wp1 +10x, wp2 (+10,+30)"),
        ([(0, 0, 5), (50, 0, 5)], "wp1 = start, wp2 +50x"),
        ([(25, 0, 5), (50, 0, 5)], "wp1 +25x, wp2 +50x"),
        ([(10, 0, 5), (100, 0, 9)], "wp1 +10x w5, wp2 +100x w9")]):
    s = (1255, [1196, 1212, 1222, 1232, 1242][k])
    add("C", desc, s, [rel(s, dx, dy, w) for dx, dy, w in legs])

# P: planet targets at warp 5.
add("P", "warp 5 to planet 26 at 19.8 ly", (1340, 1185), [("wpp", 26, PL[26][0], PL[26][1], 5)])
add("P", "warp 5 to planet 4 at ~61 ly", (1060, 1229), [("wpp", 4, PL[4][0], PL[4][1], 5)])

fleets_idx = len(fleets)
# O: ordering. Chaser/target pairs; ids assigned in list order.
add("O", "a: LOW id chases fleet b (warp 9)", (1290, 1300), [("wpf", "next", 0, 0, 9)])
add("O", "b: HIGH id target, +100x warp 5", (1320, 1300), [rel((1320, 1300), 60, 0, 5)])
add("O", "c: LOW id target, +100x warp 5", (1290, 1316), [rel((1290, 1316), 60, 0, 5)])
add("O", "d: HIGH id chases fleet c (warp 9)", (1260, 1316), [("wpf", "prev", 0, 0, 9)])
add("O", "e: LOW id, mutual chase warp 4", (1200, 1380), [("wpf", "next", 0, 0, 4)])
add("O", "f: HIGH id, mutual chase warp 4", (1220, 1380), [("wpf", "prev", 0, 0, 4)])
add("O", "g: LOW id, mutual chase warp 3", (1270, 1385), [("wpf", "next", 0, 0, 3)])
add("O", "h: HIGH id, mutual chase warp 3", (1286, 1385), [("wpf", "prev", 0, 0, 3)])

def main(out):
    os.makedirs(out, exist_ok=True)
    spec = ["# FM-001: generated by experiments/fm001/gen.py", "tech prop 7",
            "design 3 clone 0 engine 3", "design 4 clone 0 engine 4", "design 5 clone 0 engine 5"]
    pred = ["id\tgroup\tdesc\tstart\twaypoints\tships\tmass\tfuel0\tpred"]
    pts = []
    for i, f in enumerate(fleets):
        wps = []
        for w in f["wps"]:
            if w[0] == "wpf":
                j = i + 1 if w[1] == "next" else i - 1
                t = fleets[j]["start"]
                wps.append(f"wpf {j} {t[0]} {t[1]} {w[4]}")
                pts.append(t)
            elif w[0] == "wpp":
                wps.append(f"wpp {w[1]} {w[2]} {w[3]} {w[4]}")
            else:
                wps.append(f"wp {w[1]} {w[2]} {w[3]}")
                pts.append((w[1], w[2]))
        pts.append(f["start"])
        ships = ",".join(f"{d}:{c}" for d, c in f["ships"].items())
        line = f"fleet {i} at {f['start'][0]} {f['start'][1]} ships {ships} fuel {f['fuel']}"
        if any(f["cargo"]): line += " cargo " + " ".join(map(str, f["cargo"]))
        spec.append(line + " " + " ".join(wps) + f"   # {f['group']}: {f['desc']}")
        mass = sum(DES[d][1] * c for d, c in f["ships"].items()) + sum(f["cargo"])
        pred.append("\t".join(map(str, [i, f["group"], f["desc"], f["start"], " ".join(wps), ships, mass,
                                        f["fuel"], predict(f, mass)])))
    for x, y in pts:
        assert 1005 <= x <= 1395 and 1005 <= y <= 1395, (x, y)
        for p, px, py in PLANETS:
            if p not in (26, 4):
                assert math.hypot(x - px, y - py) >= 3, ((x, y), p)
    open(os.path.join(out, "fm001.spec"), "w").write("\n".join(spec) + "\n")
    open(os.path.join(out, "predictions.tsv"), "w").write("\n".join(pred) + "\n")
    print(f"{len(fleets)} fleets")

def predict(f, mass):
    """Working hypotheses, written before the run. Position: a partial move
    covers warp^2 ly along the straight line; candidate roundings trunc
    (toward zero), floor, round. Arrival iff exact distance <= warp^2.
    Fuel: ceil(mass * table[warp] * dist / 20000), dist = distance actually
    moved, with quotient q shown; fits only the FM-000 pilot (18 kt, 25 ly,
    warp 5 -> 3 mg)."""
    if f["group"] == "O":
        return "see ordering hypotheses"
    w = f["wps"][0]
    s = f["start"]
    if w[0] == "wpp":
        tx, ty, warp = w[2], w[3], w[4]
    else:
        tx, ty, warp = w[1], w[2], w[3]
    dx, dy = tx - s[0], ty - s[1]
    d = math.hypot(dx, dy)
    step = warp * warp
    out = []
    if d <= step:
        out.append(f"arrive ({tx},{ty}) d={d:.3f}")
        moved = d
    else:
        fx, fy = s[0] + dx * step / d, s[1] + dy * step / d
        tr = (s[0] + math.trunc(dx * step / d), s[1] + math.trunc(dy * step / d))
        fl = (math.floor(fx), math.floor(fy))
        rd = (math.floor(fx + 0.5), math.floor(fy + 0.5))
        out.append(f"exact ({fx:.3f},{fy:.3f}) trunc{tr} floor{fl} round{rd}")
        moved = step
    eng = {DES[d][2] for d in f["ships"]}
    if len(eng) == 1:
        e = ENG[eng.pop()][2][warp]
        q = mass * e * moved / 20000
        out.append(f"fuel q={q:.3f} ceil={math.ceil(q - 1e-9)} -> {f['fuel'] - math.ceil(q - 1e-9)} left")
    return "; ".join(out)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
