#!/usr/bin/env python3
"""Compare FM-004 results.tsv with both pre-run predictions in
predictions.tsv (`pred`: decomp model; `fitted`: FM-001..003 description).
Usage: compare.py [-v]"""
import csv, os, re, sys
here = os.path.dirname(os.path.abspath(__file__))
pred = {r["id"]: r for r in csv.DictReader(open(f"{here}/predictions.tsv"), delimiter="\t")}
res = list(csv.DictReader((l for l in open(f"{here}/results.tsv") if not l.startswith("#")), delimiter="\t"))
nb = nf = 0
for r in res:
    p = pred[r["id"]]
    pos, fuel, warp, obj, wps, ev = [x.strip() for x in p["pred"].split(";")[:6]]
    evs = sorted(re.findall(r"\b(\d+)(?:\([^)]*\))?", ev))
    oev = sorted(x for x in r["msgs"].split(",") if x)
    ob = (r["end"], r["fuel1"], r["warp"], r["obj"], r["wps_left"], oev)
    ok_b = ob == (pos, fuel, r["warp"] if warp == "-" else warp, obj, wps, evs)
    ok_f = p["fitted"].split(" (")[0] == f"pos={r['end']} fuel={r['fuel1']}"
    nb += not ok_b
    nf += not ok_f
    if "-v" in sys.argv or not ok_b or not ok_f:
        print(f"{r['id']:>3} {p['group']} decomp={'ok ' if ok_b else 'BAD'} fitted={'ok ' if ok_f else 'BAD'} "
              f"obs end={r['end']} fuel={r['fuel1']} warp={r['warp']} obj={r['obj']} ev={','.join(oev)} | {p['desc']}")
print(f"decomp model mismatches: {nb}/{len(res)}; fitted description mismatches: {nf}/{len(res)}")
