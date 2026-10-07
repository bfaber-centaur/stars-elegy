#!/usr/bin/env python3
"""Check the FM-001..FM-003 observations against the working description in
docs/PARITY.md ("Fleet movement"). Covers fleets with ordinary (deep-space or
planet) waypoints; fleet-target chases (groups O, CH, MU) are only listed.
Usage: fmcheck.py   (reads experiments/fm00N/{predictions,results}.tsv)"""
import ast, csv, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fmlib import DES, ENG, PL

here = os.path.dirname(os.path.abspath(__file__))


def rows(n):
    pred = {r["id"]: r for r in csv.DictReader(open(f"{here}/fm00{n}/predictions.tsv"), delimiter="\t")}
    res = list(csv.DictReader((l for l in open(f"{here}/fm00{n}/results.tsv") if not l.startswith("#")), delimiter="\t"))
    return [(pred[r["id"]], r) for r in res]


def model(p, r):
    start = ast.literal_eval(p["start"])
    ships = {int(a): int(b) for a, b in (x.split(":") for x in p["ships"].split(","))}
    mass = int(p["mass"])
    cargo = mass - sum(DES[d][1] * c for d, c in ships.items())
    fuel0 = int(p["fuel0"])
    wps = p["waypoints"].split()
    if not wps:
        return start, fuel0, ""
    if wps[0] == "wpp":
        tx, ty, warp = int(wps[2]), int(wps[3]), int(wps[4])
    else:
        tx, ty, warp = int(wps[1]), int(wps[2]), int(wps[3])
    dx, dy = tx - start[0], ty - start[1]
    d = math.hypot(dx, dy)
    step = warp * warp
    arrive = math.floor(d) <= step
    # m*e per ly: every stack at its own engine; cargo at the freighter's
    # engine if there is one (only case seen: FM-002 X34), else design 0's.
    me = sum(DES[k][1] * c * ENG[DES[k][2]][2][warp] for k, c in ships.items())
    carrier = 1 if 1 in ships else min(ships)
    me += cargo * ENG[DES[carrier][2]][2][warp]
    dist = min(math.ceil(d), step) if arrive else step
    cost = math.floor((me * dist + 18000) / 20000)
    if cost <= fuel0 and not (fuel0 == 0 and me > 0):
        if arrive:
            end = (tx, ty)
        else:
            end = (math.floor(start[0] + dx * step / d + .5), math.floor(start[1] + dy * step / d + .5))
        fuel1 = fuel0 - cost
        if me == 0 and warp == 1 and d > 0:  # free speed: ram-scoop fuel, 1 mg per ship, capped
            cap = sum(DES[k][3] * c for k, c in ships.items())
            fuel1 = min(cap, fuel1 + sum(ships.values()))
        return end, fuel1, ""
    # cannot pay for the move (an empty tank never moves at a warp whose
    # table value is not 0, even when the rounded cost would be 0)
    if fuel0 == 0:
        return start, 0, "fuel 0"
    L = math.floor(fuel0 * 20000 / me)
    if L >= d:
        return (tx, ty), 0, "limit"
    return (math.floor(start[0] + dx * L / d + .5), math.floor(start[1] + dy * L / d + .5)), 0, "limit"


bad = 0
for n in (1, 2, 3):
    for p, r in rows(n):
        if p["group"] in ("O", "CH", "MU") or "wpf" in p["waypoints"]:
            continue
        if p["group"] == "C" and len([w for w in p["waypoints"].split() if w in ("wp", "wpp")]) > 1:
            # chaining: stops at waypoint 1 for the year
            w = p["waypoints"].split()
            p = dict(p, waypoints=" ".join(w[:4]))
        end, fuel1, note = model(p, r)
        obs_end, obs_fuel = ast.literal_eval(r["end"]), int(r["fuel1"])
        ok = end == obs_end and fuel1 == obs_fuel
        bad += not ok
        if not ok or "-v" in sys.argv:
            print(f"FM-00{n} {r['id']:>3} {p['group']:>2} {'ok ' if ok else 'BAD'} model end={end} fuel={fuel1} "
                  f"obs end={obs_end} fuel={obs_fuel} {note} | {p['desc']}")
print("mismatches:", bad)
