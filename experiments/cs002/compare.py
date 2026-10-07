#!/usr/bin/env python3
"""Compare CS-002 oracle turns with predictions.tsv.
  compare.py RUNDIR0 RUNDIR1 RUNDIR2 RUNDIR3 > results.tsv
RUNDIRn: tools/fleetlab/oracle-turn output for turnN.spec. For each fleet:
end x, end fuel, ship count; the fuel charge actually paid is recovered as
start fuel + predicted ram-scoop gain - end fuel when the fleet kept all its
ships, and the engine factor f(w) implied by that charge is printed."""
import csv, os, re, sys
here = os.path.dirname(os.path.abspath(__file__))


def fleets(path):
    out = {}
    for line in open(path):
        if "PG001.HST" not in line:
            continue
        m = re.search(r" fleet (\d+) .* x=(\d+) y=(\d+) ships=(\S+) cargo=(\S+) fuel=(\d+) mass=(\d+)", line)
        if m:
            out[int(m[1])] = dict(x=int(m[2]), y=int(m[3]), ships=m[4], cargo=m[5], fuel=int(m[6]), mass=int(m[7]))
    return out


def charge(f, w, M):
    return -(-(f * w * w * M // 2000) // 10)


pred = list(csv.DictReader(open(os.path.join(here, "predictions.tsv")), delimiter="\t"))
after = [fleets(os.path.join(d, "after.dump")) for d in sys.argv[1:5]]
bad = 0
print("turn\tfleet\tengine\twarp\tships0\tships1\tx1\tfuel1\tcharge\tf_implied\tf_pred\tresult")
for p in pred:
    t, i = int(p["turn"]), int(p["fleet"])
    a = after[t].get(i)
    w, M, n = int(p["warp"]), int(p["mass"]), int(p["ships"])
    if a is None:
        print(f"{t}\t{i}\t{p['name']}\t{w}\t{n}\t0\t-\t-\t-\t-\t{p['f_pred']}\tGONE"); bad += 1; continue
    n1 = int(a["ships"].split(":")[1])
    paid = int(p["fuel0"]) + int(p["gain_pred"]) - a["fuel"]
    fi = [f for f in range(0, 2001) if charge(f, w, M) == paid] if n1 == n else []
    if n1 == n:
        ok = a["x"] == int(p["x_pred"]) and a["fuel"] == int(p["fuel_pred"])
        res = "ok" if ok else "MISMATCH"
    else:
        # ships lost after paying: fuel and cargo keep the survivors' share
        cargo1 = int(a["cargo"].split("/")[0])
        ok = (a["x"] == int(p["x_pred"]) and a["fuel"] == int(p["fuel_pred"]) * n1 // n
              and cargo1 == int(p["cargo"]) * n1 // n)
        res = "ok, %d of %d ships lost after paying; fuel and cargo x%d/%d" % (n - n1, n, n1, n) if ok else "SHIPS LOST, MISMATCH"
        if ok:
            paid = int(p["charge_pred"])
            fi = [f for f in range(0, 2001) if charge(f, w, M) == int(p["charge_pred"])]
    bad += not ok
    print(f"{t}\t{i}\t{p['name']}\t{w}\t{n}\t{n1}\t{a['x']}\t{a['fuel']}\t{paid}\t"
          f"{fi[0] if len(fi) == 1 else ','.join(map(str, fi)) or '-'}\t{p['f_pred']}\t{res}")
print(f"# {len(pred) - bad}/{len(pred)} as predicted", file=sys.stderr)
