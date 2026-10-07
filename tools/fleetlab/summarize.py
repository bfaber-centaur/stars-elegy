#!/usr/bin/env python3
"""Summarize one FleetLab oracle turn: per fleet, start, end, distance moved,
fuel before/after/used, waypoints left (with the first remaining target),
and the event message ids the M file carries for that fleet.
  summarize.py RUNDIR   (RUNDIR from tools/fleetlab/oracle-turn)
Output is tab-separated."""
import math, re, sys
from collections import defaultdict

def fleets(path, filt):
    out, cur = {}, None
    for line in open(path):
        if filt not in line:
            continue
        m = re.search(r" fleet (\d+) .* obj=(\d+) x=(\d+) y=(\d+) ships=(\S+) cargo=(\S+) fuel=(\d+) mass=(\d+) waypoints=(\d+)", line)
        if m:
            cur = int(m[1])
            out[cur] = dict(obj=int(m[2]), x=int(m[3]), y=int(m[4]), ships=m[5], cargo=m[6], fuel=int(m[7]),
                            mass=int(m[8]), wps=[])
            continue
        m = re.search(r" wp fleet=(\d+) i=(\d+) x=(\d+) y=(\d+) obj=(\d+) type=(\S+) warp=(\d+)", line)
        if m:
            out[int(m[1])]["wps"].append((int(m[3]), int(m[4]), int(m[5]), m[6], int(m[7])))
    return out

# Event record lengths seen so far (bytes): unknown ids are reported raw.
EVENT_LEN = {63: 5, 78: 5, 139: 6, 243: 6}

def messages(path):
    """Event messages from the M file (block type 12), keyed by fleet id
    (records whose 3rd/4th bytes are a fleet object id with bit 15 set)."""
    msgs = defaultdict(list)
    for line in open(path):
        if "M1 block type=12 " not in line:
            continue
        b = list(map(int, line.split("data=")[1].split()))
        i = 0
        while i < len(b):
            mid = b[i]
            n = EVENT_LEN.get(mid)
            if n is None:
                msgs["raw"].append(" ".join(map(str, b[i:])))
                break
            rec = b[i:i + n]
            if rec[3] & 0x80:
                msgs[rec[2] | ((rec[3] & 1) << 8)].append(mid)
            else:
                msgs[("planet", rec[2])].append(mid)
            i += n
    return msgs

run = sys.argv[1]
before = fleets(f"{run}/before.dump", "PG001.HST")
after = fleets(f"{run}/after.dump", "PG001.HST")
msgs = messages(f"{run}/after.dump")
print("id\tstart\tend\tmoved\tfuel0\tfuel1\tused\twps_left\tnext_target\tmsgs")
for i in sorted(before):
    b, a = before[i], after.get(i)
    if a is None:
        print(f"{i}\t({b['x']},{b['y']})\tGONE"); continue
    nxt = a["wps"][1] if len(a["wps"]) > 1 else None
    print("\t".join(map(str, [i, (b['x'], b['y']), (a['x'], a['y']),
                              round(math.hypot(a['x'] - b['x'], a['y'] - b['y']), 3), b['fuel'], a['fuel'],
                              b['fuel'] - a['fuel'], len(a['wps']),
                              f"({nxt[0]},{nxt[1]}) w{nxt[4]}" if nxt else f"wp0 obj={a['wps'][0][2]} w{a['wps'][0][4]}",
                              ",".join(map(str, msgs.get(i, [])))])))
if msgs.get("raw"):
    print("unparsed events:", msgs["raw"])
