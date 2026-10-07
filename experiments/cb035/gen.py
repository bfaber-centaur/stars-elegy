#!/usr/bin/env python3
"""Write the round-5 combat specs (CB-035..CB-041) next to this file.

CB-035..CB-037 use a sixteen-player game built by tools/fleetlab/new-game
from cb16p.def (game CB16P); CB-038..CB-041 use the two-player Combat Lab
base game (base2400, see experiments/cb000).
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = "energy weapons prop con elec bio".split()


def tech(p, low=None):
    low = low or {}
    return [f"tech {p} {f} {low.get(f, 26)}" for f in FIELDS]


def players16(low=None, rel=None):
    """16 JOAT players, tech 26 (or `low` per player), all neutral unless `rel`."""
    low = low or {}
    out = [f"prt {p} 9" for p in range(16)]
    for p in range(16):
        out += tech(p, low.get(p))
    for (a, b), r in sorted((rel or {}).items()):
        out.append(f"relation {a} {b} {r}")
    return out


L_FR = "Frigate, 1 Long Hump 6, empty, 2 Laser, empty"
PH_FR = "Frigate, 1 Long Hump 6, empty, 2 Colloidal Phaser, empty"
PH_DD = "Destroyer, 1 Long Hump 6, 1 Colloidal Phaser, 1 Colloidal Phaser, empty, 2 Tritanium, empty, empty"
LASER_DD = "Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, 2 Tritanium, empty, empty"
HAULER = "Small Freighter, 1 Quick Jump 5, empty, empty"
BARE_STATION = "Space Station" + ", empty" * 12
LASER_STATION = ("Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, "
                 "8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield")
HW0 = (16, 1263, 1280)  # player 0's homeworld in CB16P
DEEP = (1060, 1080)

specs = {}


def everyone_designs(design):
    return [f"design {p} 0 {design} = D{p}" for p in range(16)]


# CB-035: the plan-0 value X on the first location of the turn.
# Player 0's armed station at its homeworld, plan 0 "player 1". Players 1..14
# orbit it with Laser Frigates; player 1's plan names player 15 (absent), the
# others attack nobody. Player 0 has no fleets, so this ring is the first one.
def a6(extra, rel=None):
    s = players16(rel=rel) + everyone_designs(L_FR) + [
        f"sbdesign 0 0 {LASER_STATION} = Laser Station",
        f"planet {HW0[0]} owner 0 pop 500 starbase 0",
        "plan 0 0 5 1 0 5 = Station Player 1",
        "plan 1 1 5 1 0 19 = Player 15",
    ] + [f"plan {p} 1 5 1 0 0 = Nobody" for p in range(2, 15)]
    s += [f"fleet {p} 0 planet {HW0[0]} at {HW0[1]} {HW0[2]} ships 0:1 plan 1 fuel 100" for p in range(1, 15)]
    return s + extra


specs["cb035"] = a6([])
# more fleets in later rings: one lone fleet each for players 2..14 in deep space
specs["cb035-lone"] = a6([f"fleet {p} 1 at {1000 + 10 * p} 1100 ships 0:1 fuel 100" for p in range(2, 15)])
# moving fleets: players 2..14 each fly a fleet across deep space this turn
specs["cb035-move"] = a6([f"fleet {p} 1 at {1000 + 10 * p} 1100 ships 0:1 fuel 100 to {1000 + 10 * p} 1160 warp 5"
                          for p in range(2, 15)])
# control: a lone player-0 fleet in deep space is the first ring, so X = 0
specs["cb035-p0lone"] = a6(["fleet 0 0 at 1060 1080 ships 0:1 fuel 100"])
# a first ring with no battle whose last fleet is player 3's: X = 3
specs["cb035-prev3"] = a6(["fleet 0 0 at 1060 1080 ships 0:1 fuel 100",
                           "fleet 3 1 at 1060 1080 ships 0:1 plan 1 fuel 100"])
# the same ring with a battle (players 0 and 3 enemies there): X = 0
specs["cb035-prevbattle"] = a6(["plan 0 1 5 1 0 1 = Enemies", "plan 3 2 5 1 0 1 = Enemies",
                                "fleet 0 0 at 1060 1080 ships 0:1 plan 1 fuel 100",
                                "fleet 3 1 at 1060 1080 ships 0:1 plan 2 fuel 100"],
                               rel={(0, 3): 2, (3, 0): 2})

# CB-036: start squares for n = 4 and 6, and a starbase owner past row n.
rel = {(a, b): 2 for a in range(1, 7) for b in range(1, 7) if a != b}
s = players16(rel=rel) + everyone_designs(L_FR) + [
    f"sbdesign 0 0 {BARE_STATION} = Bare Station",
    f"planet {HW0[0]} owner 0 pop 500 starbase 0",
] + [f"plan {p} 1 5 1 0 1 = Enemies" for p in range(1, 7)]
s += ["# n = 4 at (1060,1080): players 1..4"]
s += [f"fleet {p} 0 at 1060 1080 ships 0:1 plan 1 fuel 100" for p in range(1, 5)]
s += ["# n = 6 at (1100,1080): players 1..6"]
s += [f"fleet {p} 1 at 1100 1080 ships 0:1 plan 1 fuel 100" for p in range(1, 7)]
s += ["# n = 2 at player 0's planet: unarmed station (player 0 neutral to all) and players 1, 2"]
s += [f"fleet {p} 2 planet {HW0[0]} at {HW0[1]} {HW0[2]} ships 0:1 plan 1 fuel 100" for p in (1, 2)]
specs["cb036"] = s

# CB-037: the observer LEGACY BUG for players other than 0.
low = {p: {"weapons": 3} for p in (1, 2, 3, 4)}
rel = {(5, 6): 2, (6, 5): 2}
obs_common = players16(low=low, rel=rel) + [f"research {p} 0" for p in (1, 2, 3, 4)] + [
    f"design {p} 0 {HAULER} = Hauler" for p in (1, 2, 3, 4)] + [
    f"design 5 0 {PH_DD} = Phaser DD", f"design 6 0 {PH_FR} = Phaser Frigate",
    "plan 5 1 5 1 0 1 = Enemies", "plan 6 1 5 1 0 1 = Enemies"]
# observers 1, 2, 3 (mask 0b1110): players 2 and 3 qualify, 1 does not; 4 has no fleet
specs["cb037"] = obs_common + [
    "fleet 5 0 at 1060 1080 ships 0:6 plan 1 fuel 100",
    "fleet 6 0 at 1060 1080 ships 0:2 plan 1 fuel 100",
] + [f"fleet {p} 0 at 1060 1080 ships 0:1 fuel 100" for p in (1, 2, 3)]
# planet owner's bit: battle at a player-1 planet without a starbase, player 1 a participant
rel2 = {(1, 6): 2, (6, 1): 2}
own = players16(low={3: {"weapons": 3}}, rel=rel2) + ["research 3 0",
    f"design 1 0 {PH_DD} = Phaser DD", f"design 3 0 {HAULER} = Hauler", f"design 6 0 {PH_FR} = Phaser Frigate",
    "plan 1 1 5 1 0 1 = Enemies", "plan 6 1 5 1 0 1 = Enemies"]
P1PL = (19, 1299, 1114)
specs["cb037-owner"] = own + [
    f"planet {P1PL[0]} owner 1 pop 500 starbase none",
    f"fleet 1 0 planet {P1PL[0]} at {P1PL[1]} {P1PL[2]} ships 0:6 plan 1 fuel 100",
    f"fleet 6 0 planet {P1PL[0]} at {P1PL[1]} {P1PL[2]} ships 0:2 plan 1 fuel 100",
    f"fleet 3 0 planet {P1PL[0]} at {P1PL[1]} {P1PL[2]} ships 0:1 fuel 100",
]
# control: the same three fleets in deep space (observers = {3}: player 3 never qualifies)
specs["cb037-deep"] = own + [
    "fleet 1 0 at 1060 1080 ships 0:6 plan 1 fuel 100",
    "fleet 6 0 at 1060 1080 ships 0:2 plan 1 fuel 100",
    "fleet 3 0 at 1060 1080 ships 0:1 fuel 100",
]


# Two-player specs (base2400)
def h2(rel=2, low0=None, low1=None):
    return tech(0, low0) + tech(1, low1) + [f"relation 0 1 {rel}", f"relation 1 0 {rel}"]


# CB-038: cargo and War Monger in the speed code
MED = "Medium Freighter, 1 Long Hump 6, empty, empty"
FRIG = "Frigate, 1 Long Hump 6, empty, empty, empty"
speed = h2() + [
    f"design 0 0 {LASER_DD} = Laser DD",
    f"design 1 0 {MED} = Medium",
    f"design 1 1 {FRIG} = Bare Frigate",
    "plan 0 1 5 1 0 1 = Enemies",
    "fleet 0 0 at 1020 1230 ships 0:1 plan 1 fuel 100",
    "# M0 empty, M1 1 kT, M71 71 kT, a 2-freighter stack with 1 kT, a freighter + frigate fleet with 1 kT",
    "fleet 1 0 at 1020 1230 ships 0:1 fuel 100",
    "fleet 1 1 at 1020 1230 ships 0:1 fuel 100 cargo 1 0 0 0",
    "fleet 1 2 at 1020 1230 ships 0:1 fuel 100 cargo 71 0 0 0",
    "fleet 1 3 at 1020 1230 ships 0:2 fuel 100 cargo 1 0 0 0",
    "fleet 1 4 at 1020 1230 ships 0:1,1:1 fuel 100 cargo 1 0 0 0",
]
specs["cb038"] = speed
specs["cb038-wm"] = ["prt 1 2", "lrt 1 0x1b80"] + speed

# CB-039: the token cap. 140 one-ship fleets per side.
cap = h2() + [f"design 0 0 {L_FR} = Laser Frigate", f"design 1 0 {L_FR} = Laser Frigate",
              "plan 0 1 5 1 0 1 = Enemies", "plan 1 1 5 1 0 1 = Enemies"]
for p in (0, 1):
    cap += [f"fleet {p} {i} at 1020 1230 ships 0:1 plan 1 fuel 100" for i in range(140)]
specs["cb039"] = cap

# CB-040: salvage past 30000 kT in deep space
SUPER = "Super Freighter, 3 Long Hump 6, empty, empty, empty"
specs["cb040"] = h2() + [
    f"design 0 0 {PH_DD} = Phaser DD",
    f"design 1 0 {SUPER} = Super",
    "plan 0 1 5 1 0 1 = Enemies",
    "fleet 0 0 at 1020 1230 ships 0:40 plan 1 fuel 280",
    "fleet 1 0 at 1020 1230 ships 0:16 fuel 1000 cargo 48000 0 0 0",
]

# CB-041: an Alternate Reality starbase destroyed. Player 0's Destroyers use
# the Trans-Galactic Drive (propulsion 9); player 1 has propulsion 3 and a
# Freighter at the planet, so it is a participant with something left.
AR_FORT = "Orbital Fort, empty, 12 Colloidal Phaser, empty, empty, empty"
TGD_DD = "Destroyer, 1 Trans-Galactic Drive, 1 Laser, 1 Laser, empty, 2 Tritanium, empty, empty"
P1HW = (8, 1169, 1145)
ar = h2(low1={"prop": 3}) + ["research 1 0",
    f"design 0 0 {TGD_DD} = TGD DD",
    f"design 1 0 {HAULER} = Hauler",
    f"sbdesign 1 0 {AR_FORT} = Phaser Fort",
    f"planet {P1HW[0]} owner 1 pop 500 starbase 0",
    "plan 0 1 5 1 0 1 = Enemies",
    f"fleet 0 0 planet {P1HW[0]} at {P1HW[1]} {P1HW[2]} ships 0:8 plan 1 fuel 100",
    f"fleet 1 0 planet {P1HW[0]} at {P1HW[1]} {P1HW[2]} ships 0:1 fuel 100",
]
specs["cb041"] = ["prt 1 8", "lrt 1 0x1b80"] + ar
specs["cb041-joat"] = ar

for name, lines in specs.items():
    exp = name.split("-")[0]
    d = os.path.join(os.path.dirname(HERE), exp)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name + ".spec"), "w") as f:
        f.write("\n".join(lines) + "\n")
