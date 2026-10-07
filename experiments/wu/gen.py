#!/usr/bin/env python3
"""Generate CombatLab specs for the waypoint-upkeep (WU) oracle batch.

Each spec is a controlled start on the two-player Combat Lab base (players 0
and 1, JOAT, homeworlds planet 17 at 1306,1060 and planet 8 at 1169,1145).
Player 0 carries the subject fleets; player 1 supplies targets/enemies.

Covers coverage-audit gap 3 (stars-elegy ORDERS.md "Waypoint upkeep and the
remaining tasks"): repeat vs dropped waypoints, live/dead fleet targets, the
route task, the idle message, the transfer-fleet refusals, and direct
measurement of patrol target choice across distances and enemy sets.

  python3 experiments/wu/gen.py OUTDIR
writes OUTDIR/<name>.spec for each scenario below.
"""
import os
import sys

# name -> spec text. Comments (#) document the expected behaviour.
SPECS = {
    # Batch A: waypoint upkeep with no war (neutral relations, no combat).
    # Short legs (20 ly) at warp 5 (25 ly/turn) so each fleet reaches its
    # first listed waypoint in the generated turn.
    "wuA": """
# waypoint upkeep: repeat/drop, idle, live/dead fleet target
# fleet 10: repeat ON, round trip -> reached wp should rotate to the end
fleet 0 10 at 1100 1230 ships 1:3 fuel 600 repeat to 1120 1230 warp 5 to 1100 1230 warp 5
# fleet 11: repeat OFF, same round trip -> reached wp should be dropped
fleet 0 11 at 1100 1240 ships 1:3 fuel 600 to 1120 1240 warp 5 to 1100 1240 warp 5
# fleet 12: single go-to waypoint reached, nothing after -> idle + message
fleet 0 12 at 1100 1250 ships 1:3 fuel 600 to 1120 1250 warp 5
# fleet 13: waypoint targets a LIVE moving enemy fleet (warp 0, just tracks)
fleet 0 13 at 1100 1260 ships 4:1 fuel 600 to 1180 1260 fleet 1 20 warp 0
# fleet 14: waypoint targets a NONEXISTENT fleet -> target cleared, plain go-to
fleet 0 14 at 1100 1270 ships 4:1 fuel 600 to 1180 1270 fleet 1 99 warp 0
# player 1 target fleet 20 moves north so fleet 13's tracking waypoint updates
fleet 1 20 at 1180 1260 ships 1:1 fuel 600 to 1180 1320 warp 5
""",

    # Batch B1: transfer-fleet to an enemy recipient -> refused.
    "wuB1": """
# transfer fleet to a recipient that treats the giver as an enemy
relation 1 0 2
fleet 0 30 at 1100 1230 ships 1:1 fuel 600 task transfer 0
fleet 1 20 at 1180 1230 ships 1:1 fuel 600
""",

    # Batch B2: colonist-carrying transfer refused; empty transfer succeeds.
    "wuB2": """
# recipient neutral to giver; only the colonist rule should refuse
relation 1 0 0
# fleet 31 carries colonists -> transfer refused
fleet 0 31 at 1100 1230 ships 2:1 fuel 600 cargo 0 0 0 100 task transfer 0
# fleet 32 carries no colonists -> transfer should succeed (becomes player 1)
fleet 0 32 at 1100 1240 ships 1:1 fuel 600 task transfer 0
fleet 1 20 at 1180 1230 ships 1:1 fuel 600
""",

    # Batch C: patrol target choice. Players at war. Patroller at 1150,1230.
    # Enemies on the y=1230 corridor at controlled distances.
    # CP1: two enemies, 60 ly and 150 ly -> which is chosen, at what warp.
    "wuCP1": """
relation 0 1 2
relation 1 0 2
fleet 0 50 at 1150 1230 ships 4:1 fuel 2000 task patrol 250
fleet 1 60 at 1210 1230 ships 1:1 fuel 600
fleet 1 61 at 1300 1230 ships 1:1 fuel 600
""",

    # CP2: two enemies equidistant (60 ly either side), one weak one strong.
    "wuCP2": """
relation 0 1 2
relation 1 0 2
fleet 0 50 at 1150 1230 ships 4:1 fuel 2000 task patrol 250
fleet 1 60 at 1210 1230 ships 0:1 fuel 600
fleet 1 61 at 1090 1230 ships 4:5 fuel 2000
""",

    # CP3: range cutoff. Range 100: enemy at 80 ly (in) and 150 ly (out).
    "wuCP3": """
relation 0 1 2
relation 1 0 2
fleet 0 50 at 1150 1230 ships 4:1 fuel 2000 task patrol 100
fleet 1 60 at 1230 1230 ships 1:1 fuel 600
fleet 1 61 at 1300 1230 ships 1:1 fuel 600
""",

    # CP4: single enemy at 150 ly, generous range -> intercept warp at distance.
    "wuCP4": """
relation 0 1 2
relation 1 0 2
fleet 0 50 at 1150 1230 ships 4:1 fuel 2000 task patrol 250
fleet 1 61 at 1300 1230 ships 1:1 fuel 600
""",
}


def main():
    if len(sys.argv) != 2:
        print("usage: gen.py OUTDIR", file=sys.stderr)
        sys.exit(2)
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name, spec in SPECS.items():
        path = os.path.join(out, name + ".spec")
        with open(path, "w") as f:
            f.write(spec.lstrip("\n"))
        print(path)


if __name__ == "__main__":
    main()
