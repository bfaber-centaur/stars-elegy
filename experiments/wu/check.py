#!/usr/bin/env python3
"""Summarise a waypoint-upkeep (WU) oracle run.

Reads the before/after CombatLab dumps a run produced (pinned-turn writes
before.dump and after.dump into each run directory) and prints, per subject
fleet, how its owner and waypoint list changed, plus any patrol intercept the
host set. Keeps observation separate from interpretation: it reports the raw
after-state, not a verdict.

  python3 experiments/wu/check.py RUNDIR [RUNDIR...]

RUNDIR is a pinned-turn / host-turn output directory (holds before.dump and
after.dump). Raw run directories live in the private apparatus repository.
"""
import os
import re
import sys


def parse(dump_path):
    """fleets[(owner,id)] = {'line': str, 'wps': [str, ...]}, in file order."""
    fleets = {}
    cur = None
    if not os.path.exists(dump_path):
        return fleets
    with open(dump_path) as f:
        for line in f:
            m = re.search(r"fleet owner=(\d+) id=(\d+) .*", line)
            if m:
                cur = (int(m.group(1)), int(m.group(2)))
                fleets[cur] = {"line": line.split(" ", 1)[1].rstrip(), "wps": []}
                continue
            if cur is not None and "  wp " in line:
                fleets[cur]["wps"].append(line.split("wp ", 1)[1].rstrip())


    return fleets


def summarise(rundir):
    before = parse(os.path.join(rundir, "before.dump"))
    after = parse(os.path.join(rundir, "after.dump"))
    print(f"==== {os.path.basename(rundir)} ====")
    # subjects are player-0 fleets present before
    for key in sorted(before):
        owner, fid = key
        if owner != 0:
            continue
        b = before[key]
        a = after.get(key)
        print(f"  fleet 0/{fid}:")
        print(f"    before wps: {b['wps']}")
        if a is None:
            # look for it under another owner (transferred away)
            moved = [k for k in after if k[1] == fid and k[0] != 0]
            if moved:
                print(f"    AFTER: transferred to player {moved[0][0]}")
            else:
                print("    AFTER: gone")
            continue
        print(f"    after  wps: {a['wps']}")
        # patrol intercept: a task=7 waypoint that now names a fleet target
        for wp in a["wps"]:
            if "task=7" in wp and "type=12" in wp:
                obj = int(re.search(r"obj=(\d+)", wp).group(1))
                warp = int(re.search(r"warp=(\d+)", wp).group(1))
                print(f"    PATROL intercept -> fleet {obj & 0x1ff} of player {obj >> 9}, warp {warp}")


def main():
    if len(sys.argv) < 2:
        print("usage: check.py RUNDIR [RUNDIR...]", file=sys.stderr)
        sys.exit(2)
    for rundir in sys.argv[1:]:
        summarise(rundir)


if __name__ == "__main__":
    main()
