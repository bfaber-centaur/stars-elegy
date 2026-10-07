#!/usr/bin/env python3
"""Write the round-4 combat specs (CB-023..CB-034) next to this file.

CB-023..CB-030 use the two-player Combat Lab base game (base2400, see
experiments/cb000); CB-031, CB-032 and CB-034 use a three-player game built by
tools/fleetlab/new-game from cb031/cb3p.def, CB-033 a five-player game
from cb033/cb5p.def (planet numbers differ).
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = "energy weapons prop con elec bio".split()


def tech(p, low=None):
    low = low or {}
    return [f"tech {p} {f} {low.get(f, 26)}" for f in FIELDS]


def h2(rel=2, low0=None):
    return tech(0, low0) + tech(1) + [f"relation 0 1 {rel}", f"relation 1 0 {rel}"]


STATION = "Space Station" + ", empty" * 12
FORT = "Orbital Fort" + ", empty" * 5
HUNTER = "Destroyer, 1 Trans-Galactic Drive, 1 Colloidal Phaser, 1 Colloidal Phaser, empty, 2 Tritanium, empty, empty"
WATCHER = "Destroyer, 1 Long Hump 6, 1 Laser, empty, empty, 2 Tritanium, empty, empty"
HAULER = "Small Freighter, 1 Quick Jump 5, empty, empty"
TANKER = "Fuel Transport, 1 Quick Jump 5, empty"

specs = {}

# CB-023: fuel lost with destroyed ships, shared by fuel capacity
fuel = h2() + [
    f"design 0 0 {HUNTER} = Hunter",
    f"design 1 0 {TANKER} = Tanker",
    f"design 1 1 {HAULER} = Hauler",
    "plan 0 1 5 6 0 1 = Tankers Only",
]
specs["cb023"] = fuel + [
    "# two Hunters destroy the two Fuel Transports of a 2 Tanker + 3 Hauler fleet (fuel 600)",
    "fleet 0 0 at 1020 1230 ships 0:2 plan 1 fuel 280",
    "fleet 1 0 at 1020 1230 ships 0:2,1:3 fuel 600",
]
specs["cb023-control"] = fuel + [
    "# the same fleets, apart: no battle",
    "fleet 0 0 at 1100 1230 ships 0:2 plan 1 fuel 280",
    "fleet 1 0 at 1020 1230 ships 0:2,1:3 fuel 600",
]

# CB-024: repair without battles; player 0 Inner Strength
rep = ["prt 0 4"] + h2(rel=0)
for p in (0, 1):
    rep += [f"design {p} 0 {HAULER} = Hauler", f"design {p} 1 {TANKER} = Tanker",
            f"sbdesign {p} 0 {STATION} = Bare Station", f"sbdesign {p} 1 {FORT} = Bare Fort"]
rep += [
    "planet 12 owner 0 pop 500 starbase none",
    "planet 18 owner 0 pop 500 starbase 1",
    "planet 5 owner 1 pop 500 starbase none",
    "planet 0 owner 1 pop 500 starbase 1",
    "planetset 17 sbdmg=200",
    "planetset 8 sbdmg=200",
    "planetset 18 sbdmg=100",
    "planetset 0 sbdmg=100",
]
D = "dmg 0:400:100"
DT = "dmg 0:400:100,1:400:100"
rep += [
    f"fleet 0 0 at 1020 1230 ships 0:1 fuel 100 {D}",
    f"fleet 0 1 at 1100 1230 ships 0:1 fuel 100 {D} to 1160 1230 warp 5",
    f"fleet 0 2 planet 8 at 1169 1145 ships 0:1 fuel 100 {D}",
    f"fleet 0 3 planet 17 at 1306 1060 ships 0:1 fuel 100 {D}",
    f"fleet 0 4 planet 12 at 1245 1158 ships 0:1 fuel 100 {D}",
    f"fleet 0 5 planet 18 at 1324 1192 ships 0:1 fuel 100 {D}",
    f"fleet 0 6 at 1220 1230 ships 0:1,1:1 fuel 100 {DT}",
    f"fleet 1 0 at 1060 1230 ships 0:1 fuel 100 {D}",
    f"fleet 1 1 at 1100 1260 ships 0:1 fuel 100 {D} to 1160 1260 warp 5",
    f"fleet 1 2 planet 17 at 1306 1060 ships 0:1 fuel 100 {D}",
    f"fleet 1 3 planet 8 at 1169 1145 ships 0:1 fuel 100 {D}",
    f"fleet 1 4 planet 5 at 1146 1180 ships 0:1 fuel 100 {D}",
    f"fleet 1 5 planet 0 at 1045 1291 ships 0:1 fuel 100 {D}",
    f"fleet 1 6 at 1260 1230 ships 0:1,1:1 fuel 100 {DT}",
]
specs["cb024"] = rep

# CB-025: dump cargo at setup
specs["cb025"] = h2() + [
    f"design 0 0 {WATCHER} = Watcher",
    f"design 1 0 {HAULER} = Hauler",
    "plan 0 1 5 2 0 1 = Starbases Only",
    "plan 1 1 0 1 0 1 dump = Dumper",
    "plan 1 2 0 1 0 1 = Keeper",
    "planet 5 owner 1 pop 500 starbase none",
    "planetset 5 fe=100 bo=100 ge=100",
    "planet 22 owner 1 pop 500 starbase none",
    "planetset 22 fe=100 bo=100 ge=100",
    "# D1 deep space: a Watcher (never fires) meets a dumping Hauler",
    "fleet 0 0 at 1020 1230 ships 0:1 plan 1 fuel 100",
    "fleet 1 0 at 1020 1230 ships 0:1 plan 1 fuel 100 cargo 20 10 5 0",
    "# D2 at player 1's planet 5 (no starbase)",
    "fleet 0 1 planet 5 at 1146 1180 ships 0:1 plan 1 fuel 100",
    "fleet 1 1 planet 5 at 1146 1180 ships 0:1 plan 1 fuel 100 cargo 20 10 5 0",
    "# C1 deep space, dump plan, no battle",
    "fleet 1 2 at 1100 1230 ships 0:1 plan 1 fuel 100 cargo 20 10 5 0",
    "# C2 player 1's planet 22, dump plan, no battle",
    "fleet 1 3 planet 22 at 1368 1292 ships 0:1 plan 1 fuel 100 cargo 20 10 5 0",
    "# C3 deep space battle, plan without dump",
    "fleet 0 2 at 1180 1230 ships 0:1 plan 1 fuel 100",
    "fleet 1 4 at 1180 1230 ships 0:1 plan 2 fuel 100 cargo 20 10 5 0",
]

# CB-026: range-0 beams on a starbase
specs["cb026"] = h2() + [
    f"sbdesign 0 0 Space Station, empty, 2 Blackjack{', empty' * 10} = Jack Station",
    "planet 18 owner 0 pop 500 starbase 0",
    "plan 0 0 5 1 0 1 = Station Enemies",
    "design 1 0 Destroyer, 1 Daddy Long Legs 7, 1 Laser, empty, empty, 2 Tritanium, empty, empty = Slow DD",
    "plan 1 1 5 1 0 1 = Max Any",
    "# five slow Destroyers approach player 0's Blackjack station at planet 18",
    "fleet 1 0 planet 18 at 1324 1192 ships 0:5 plan 1 fuel 100",
]

# CB-027: a starbase's cost in target choice
specs["cb027"] = h2() + [
    f"sbdesign 0 0 {STATION} = Bare Station",
    "planet 18 owner 0 pop 500 starbase 0",
    "plan 0 0 5 1 0 1 = Station Enemies",
    "design 0 0 Fuel Transport, 1 Quick Jump 5, 1 Mole-skin Shield = Tanker",
    "design 1 0 Destroyer, 1 Trans-Galactic Drive, 1 Colloidal Phaser, empty, empty, 2 Tritanium, empty, empty = Hunter",
    "plan 1 1 5 1 0 1 = Max Any",
    "fleet 0 0 planet 18 at 1324 1192 ships 0:1 fuel 100",
    "# one Hunter (primary any) attacks the bare station and the Tanker at planet 18",
    "fleet 1 0 planet 18 at 1324 1192 ships 0:1 plan 1 fuel 100",
]

# CB-028: a disengaging token that stays on its square
specs["cb028"] = h2() + [
    f"design 0 0 {WATCHER} = Watcher",
    "plan 0 1 5 2 0 1 = Starbases Only",
    "design 1 0 Small Freighter, 1 Long Hump 6, empty, empty = Runner",
    "fleet 0 0 at 1020 1230 ships 0:1 plan 1 fuel 100",
    "fleet 1 0 at 1020 1230 ships 0:1 fuel 100",
]

# CB-029: tech attempt of a wiped-out participant (two players)
specs["cb029"] = h2(low0={"weapons": 3}) + [
    "research 0 0",
    "design 0 0 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, 2 Tritanium, empty, empty = Laser DD",
    "design 1 0 Destroyer, 1 Long Hump 6, 1 Colloidal Phaser, 1 Laser, empty, empty, empty, empty = Charger",
    "design 1 1 Destroyer, 1 Long Hump 6, 1 Colloidal Phaser, 1 Colloidal Phaser, empty, 2 Tritanium, empty, empty = Phaser DD",
    "plan 0 1 5 1 0 1 = Max Any",
    "plan 1 1 5 1 0 1 = Max Any",
    "fleet 0 0 at 1020 1230 ships 0:5 plan 1 fuel 100",
    "fleet 1 0 at 1020 1230 ships 0:1,1:4 plan 1 fuel 100",
]

# CB-030: several movers on both sides
mm = h2()
for p in (0, 1):
    mm += [f"design {p} 0 Destroyer, 1 Daddy Long Legs 7, 1 Laser, 1 Laser, empty, 2 Tritanium, empty, empty = Heavy",
           f"design {p} 1 Frigate, 1 Daddy Long Legs 7, empty, 2 Laser, empty = Light",
           f"plan {p} 1 5 1 0 1 = Max Any"]
specs["cb030"] = mm + [
    "fleet 0 0 at 1020 1230 ships 0:2,1:3 plan 1 fuel 100",
    "fleet 1 0 at 1020 1230 ships 0:2,1:3 plan 1 fuel 100",
]


# CB-031: three players (cb3p base)
def h3(rel):
    out = [f"prt {p} 9" for p in range(3)] + tech(0, {"weapons": 3}) + tech(1) + tech(2) + ["research 0 0"]
    for (a, b), r in rel.items():
        out.append(f"relation {a} {b} {r}")
    return out


PH_DD = "Destroyer, 1 Long Hump 6, 1 Colloidal Phaser, 1 Colloidal Phaser, empty, 2 Tritanium, empty, empty"
PH_FR = "Frigate, 1 Long Hump 6, empty, 2 Colloidal Phaser, empty"
specs["cb031-obs"] = h3({(0, 1): 0, (0, 2): 0, (1, 0): 0, (1, 2): 2, (2, 0): 0, (2, 1): 2}) + [
    f"design 0 0 {HAULER} = Hauler",
    f"design 1 0 {PH_DD} = Phaser DD",
    f"design 2 0 {PH_FR} = Phaser Frigate",
    "plan 1 1 5 1 0 1 = Max Any",
    "plan 2 1 5 1 0 1 = Max Any",
    "# player 1 destroys player 2's frigates; player 0 (weapons 3) watches with a Hauler",
    "fleet 0 0 at 1060 1080 ships 0:1 fuel 100",
    "fleet 1 0 at 1060 1080 ships 0:4 plan 1 fuel 100",
    "fleet 2 0 at 1060 1080 ships 0:3 plan 1 fuel 100",
]
specs["cb031-n3"] = h3({(a, b): 2 for a in range(3) for b in range(3) if a != b}) + [
    "design 0 0 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate",
    f"design 1 0 {PH_DD} = Phaser DD",
    f"design 2 0 {PH_FR} = Phaser Frigate",
    f"design 2 1 {PH_DD} = Phaser DD",
    "plan 0 1 5 1 0 1 = Max Any",
    "plan 1 1 5 1 0 1 = Max Any",
    "plan 2 1 5 1 0 1 = Max Any",
    "# all three players are enemies; player 0 (weapons 3) has two Laser Frigates",
    "fleet 0 0 at 1060 1080 ships 0:2 plan 1 fuel 100",
    "fleet 1 0 at 1060 1080 ships 0:4 plan 1 fuel 100",
    "fleet 2 0 at 1060 1080 ships 0:3,1:2 plan 1 fuel 100",
]

# Round 4b. CB-032: a disengaging token that stays on its square (3 players)
BRUTE = "Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, 2 Tritanium, empty, empty"
RUNNER = "Small Freighter, 1 Long Hump 6, empty, empty"
specs["cb032"] = [f"prt {p} 9" for p in range(3)] + tech(0) + tech(1) + tech(2) + [
    "relation 0 1 2", "relation 2 1 2", "relation 0 2 0", "relation 2 0 0",
    "relation 1 0 0", "relation 1 2 0",
    f"design 0 0 {BRUTE} = Brute",
    f"design 2 0 {BRUTE} = Brute",
    f"design 1 0 {RUNNER} = Runner",
    "plan 0 1 5 1 0 5 = Hunt P1",
    "plan 1 1 0 1 0 0 = Run",
    "plan 2 1 5 1 0 5 = Hunt P1",
    "# players 0 and 2 (Laser Destroyers) both name player 1, whose only token is an unarmed Freighter",
    "fleet 0 0 at 1060 1080 ships 0:2 plan 1 fuel 100",
    "fleet 1 0 at 1060 1080 ships 0:1 plan 1 fuel 100",
    "fleet 2 0 at 1060 1080 ships 0:2 plan 1 fuel 100",
]

# CB-033: a player found out at step 5 keeps firing (5 players, friends join)
TOUGH = "Destroyer, 1 Long Hump 6, 1 Laser, empty, empty, 2 Tritanium, empty, empty"
L_FR = "Frigate, 1 Long Hump 6, empty, 2 Laser, empty"
rel5 = {(a, b): 0 for a in range(5) for b in range(5) if a != b}
rel5[(2, 0)] = 1
specs["cb033"] = [f"prt {p} 9" for p in range(5)] + [x for p in range(5) for x in tech(p)] + [
    f"relation {a} {b} {r}" for (a, b), r in sorted(rel5.items())] + [
    f"design 0 0 {L_FR} = Laser Frigate",
    f"design 1 0 {PH_DD} = Phaser DD",
    f"design 2 0 {PH_FR} = Phaser Frigate",
    f"design 3 0 {TOUGH} = Tough DD",
    f"design 4 0 {TOUGH} = Tough DD",
    "plan 0 1 5 1 0 5 = Hunt P1",
    "plan 1 1 5 1 0 4 = Hunt P0",
    "plan 2 1 5 1 0 0 = Nobody",
    "plan 3 1 5 1 0 8 = Hunt P4",
    "plan 4 1 5 1 0 7 = Hunt P3",
    "# A (0) and E (1) name each other; F (2) names nobody and is player 0's friend;",
    "# players 3 and 4 fight each other all battle",
    "fleet 0 0 at 1060 1080 ships 0:1 plan 1 fuel 100",
    "fleet 1 0 at 1060 1080 ships 0:4 plan 1 fuel 100",
    "fleet 2 0 at 1060 1080 ships 0:1 plan 1 fuel 100",
    "fleet 3 0 at 1060 1080 ships 0:3 plan 1 fuel 100",
    "fleet 4 0 at 1060 1080 ships 0:3 plan 1 fuel 100",
]

# Round 4c. CB-034: CB-032's geometry with enemies that out-damage the Runner at
# every distance (Delta Torpedoes) but have no target type it matches
DELTA_DD = "Destroyer, 1 Long Hump 6, 1 Delta Torpedo, 1 Delta Torpedo, empty, 2 Tritanium, empty, empty"
specs["cb034"] = [f"prt {p} 9" for p in range(3)] + tech(0) + tech(1) + tech(2) + [
    "relation 0 1 2", "relation 2 1 2", "relation 0 2 0", "relation 2 0 0",
    "relation 1 0 0", "relation 1 2 0",
    f"design 0 0 {DELTA_DD} = Delta DD",
    f"design 2 0 {DELTA_DD} = Delta DD",
    f"design 1 0 {RUNNER} = Runner",
    "plan 0 1 5 3 2 5 = Armed P1",
    "plan 2 1 5 3 2 5 = Armed P1",
    "plan 1 1 0 1 0 0 = Run",
    "# players 0 and 2: 12 Delta Torpedo Destroyers each, naming player 1 but targeting only",
    "# armed ships and starbases; player 1's only token is an unarmed Freighter",
    "fleet 0 0 at 1060 1080 ships 0:12 plan 1 fuel 100",
    "fleet 1 0 at 1060 1080 ships 0:1 plan 1 fuel 100",
    "fleet 2 0 at 1060 1080 ships 0:12 plan 1 fuel 100",
]

for name, lines in specs.items():
    exp = name.split("-")[0]
    d = os.path.join(os.path.dirname(HERE), exp)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name + ".spec"), "w") as f:
        f.write("\n".join(lines) + "\n")
