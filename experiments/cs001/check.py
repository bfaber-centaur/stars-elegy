#!/usr/bin/env python3
"""Check docs/COMPONENTS.md against the CS-001 Technology Browser readouts.

Recomputes, from data/components.json and the rules in docs/COMPONENTS.md
("Cost for an owner", "Who can build what", "Technology Browser"), what the
browser shows for every item in each race setup of configs.txt, and compares
with readouts.tsv (decoded from the original game's screens).
  check.py            prints mismatches and a summary
"""
import csv, json, os, sys

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(here, "..", "..")
PRT = ["HE", "SS", "WM", "CA", "IS", "SD", "PP", "IT", "AR", "JOAT"]
LRT = ["IFE", "TT", "ARM", "ISB", "GR", "UR", "MA", "NRSE", "CE", "OBRM", "NAS", "LSP", "BET", "RS"]
FIELDS = ["energy", "weapons", "propulsion", "construction", "electronics", "biotechnology"]
ORDER = ["armor", "beam", "bomb", "electrical", "engine", "mechanical", "mine_layer", "mining_robot",
         "orbital", "planetary", "scanner", "shield", "hull", "starbase_hull", "terraform", "torpedo"]


def round_half_up(n, d):
    return (2 * n + d) // (2 * d)


def owner_cost(item, prt, lrts, tech):
    """[ironium, boranium, germanium, resources] for one unit, before the
    starbase rule (docs/COMPONENTS.md, "Cost for an owner")."""
    c = [item["cost"][k] for k in ("ironium", "boranium", "germanium", "resources")]
    req = [item["tech"][f] for f in FIELDS]
    cat = item["category"]
    exempt = cat == "terraform" or (cat == "planetary" and item["stats"]["kind"] != "genesis_device")
    m = None
    if not exempt:
        gaps = [tech[k] - req[k] for k in range(6) if req[k] > 0]
        m = min(gaps) if gaps else min(tech)
        if m > 0:
            d = min(5 * min(m, 19), 80) if "BET" in lrts else min(4 * min(m, 19), 75)
            c = [max(1, x - round_half_up(x * d, 100)) if x else 0 for x in c]
    if cat == "orbital" and item["stats"]["kind"] == "stargate" and prt == "IT":
        c = [x - x // 4 for x in c]
    elif cat in ("beam", "torpedo", "bomb") and prt == "WM":
        c = [x - x // 4 for x in c]
    elif cat in ("beam", "torpedo", "bomb") and prt == "IS":
        c = [x + x // 4 for x in c]
    elif cat == "terraform" and prt == "CA":
        c[3] //= 2
    elif cat == "engine" and "CE" in lrts:
        c = [x - x // 2 for x in c]
    if m is not None and m < 1 and "BET" in lrts and any(req):
        c = [2 * x for x in c]
    return c


def can_build(item, prt, lrts, owned_mt):
    r = item["restriction"]
    if r["prt_only"] and prt not in r["prt_only"]:
        return False
    if prt in r["prt_not"]:
        return False
    if any(t not in lrts for t in r["lrt_required"]) or any(t in lrts for t in r["lrt_forbidden"]):
        return False
    return not item["mystery_trader"] or owned_mt


def browser(items, prt, lrts, tech, owned_mt):
    for cat in ORDER:
        for it in sorted((x for x in items if x["category"] == cat), key=lambda x: x["index"]):
            if it["mystery_trader"] and not owned_mt:
                continue                      # not listed at all
            c = owner_cost(it, prt, lrts, tech)
            if cat in ("starbase_hull", "orbital"):
                c = [x - x // 2 for x in c]
            met = all(tech[k] >= it["tech"][f] for k, f in enumerate(FIELDS))
            ok = can_build(it, prt, lrts, owned_mt)
            label = "Available" if ok and met else ("UnAvail" if not ok else "cost")
            yield it, c + [it["mass"] or 0], label


def main():
    items = json.load(open(os.path.join(root, "data", "components.json")))["items"]
    cfgs = {}
    for line in open(os.path.join(here, "configs.txt")):
        name, *kv = line.split()
        d = dict(x.split("=") for x in kv)
        lrt = int(d["lrt"], 16)
        cfgs[name] = (PRT[int(d["prt"])], {t for k, t in enumerate(LRT) if lrt >> k & 1},
                      [int(x) for x in d["tech"].split(",")], d["mt"] != "0")
    obs = {}
    for r in csv.DictReader(open(os.path.join(here, "readouts.tsv")), delimiter="\t"):
        obs.setdefault(r["config"], []).append(r)
    n = bad = 0
    for name, (prt, lrts, tech, mt) in sorted(cfgs.items()):
        pred = list(browser(items, prt, lrts, tech, mt))
        got = {(o["category"], o["index"]): o for o in obs[name]}
        if len(pred) != len(got):
            print(name, "item count", len(pred), "vs", len(got)); bad += 1
        for it, vals, label in pred:
            n += 1
            o = got.get((it["category"], str(it["index"])))
            if o is None:
                bad += 1; print(name, it["name"], "not listed in the browser"); continue
            ov = [int(o[k]) for k in ("ironium", "boranium", "germanium", "resources", "mass")]
            if (it["category"], str(it["index"]), it["name"]) != (o["category"], o["index"], o["name"]) \
                    or ov != vals or label != o["label"]:
                bad += 1
                print(name, it["name"], vals, label, "observed", ov, o["label"])
    print(f"{n - bad}/{n} readouts as computed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
