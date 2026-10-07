"""Write the round-6 combat specs (CB-042..CB-047) next to this file.

CB-042 uses the three-player Combat Lab game CB3P (experiments/cb023,
evidence/cb4/base3p); the others use the two-player base (base2400).
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = "energy weapons prop con elec bio".split()
L_FR = "Frigate, 1 Long Hump 6, empty, 2 Laser, empty"
L_FR1 = "Frigate, 1 Long Hump 6, empty, 1 Laser, empty"
L_FR3 = "Frigate, 1 Long Hump 6, empty, 3 Laser, empty"
L_DD = "Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, 2 Tritanium, empty, empty"
PH_DD = "Destroyer, 1 Long Hump 6, 1 Colloidal Phaser, 1 Colloidal Phaser, empty, 2 Tritanium, empty, empty"
FORT = "Orbital Fort, empty, 12 Colloidal Phaser, empty, empty, empty"
MED = "Medium Freighter, 1 Long Hump 6, empty, empty"
SMALL = "Small Freighter, 1 Long Hump 6, empty, empty"
AMT_DD = "Destroyer, 1 Long Hump 6, 1 Anti Matter Torpedo, 1 Anti Matter Torpedo, empty, 2 Tritanium, empty, empty"
MORPH = ("Mini Morph, 2 Enigma Pulsar, 3 Multi Cargo Pod, 1 Multi Function Pod, 1 Mega Poly Shell, "
         "1 Langston Shell, 2 Laser, empty")
DEEP = (1020, 1230)
P1HW = (8, 1169, 1145)

specs = {}


def tech(players):
    return [f"tech {p} {f} 26" for p in players for f in FIELDS]


def enemies(players):
    return [f"relation {a} {b} 2" for a in players for b in players if a != b]


def one_ship_fleets(p, ids, at, design=0, planet=None):
    where = f"planet {planet} at {at[0]} {at[1]}" if planet is not None else f"at {at[0]} {at[1]}"
    return [f"fleet {p} {i} {where} ships {design}:1 plan 1 fuel 100" for i in ids]


# CB-042 (CAP-A): three mutually hostile players, 100 one-ship fleets each.
s = tech(range(3)) + enemies(range(3))
s += [f"design {p} 0 {L_FR} = Laser Frigate" for p in range(3)]
s += [f"plan {p} 1 5 1 0 1 = Enemies" for p in range(3)]
for p in range(3):
    s += one_ship_fleets(p, range(100), (1060, 1080))
specs["cb042"] = s

# CB-043 (CAP-B): at player 1's planet with an armed Orbital Fort. Player 0:
# fleets 0..139; player 1: fleets 0..129 and fleet 130 with three designs.
s = tech(range(2)) + enemies(range(2)) + [
    f"design 0 0 {L_FR} = Laser Frigate",
    f"design 1 0 {L_FR} = Laser Frigate", f"design 1 1 {L_FR1} = Frigate L1", f"design 1 2 {L_FR3} = Frigate L3",
    f"sbdesign 1 0 {FORT} = Phaser Fort", f"planet {P1HW[0]} starbase 0",
    "plan 0 1 5 1 0 1 = Enemies", "plan 1 1 5 1 0 1 = Enemies"]
s += one_ship_fleets(0, range(140), P1HW[1:], planet=P1HW[0])
s += one_ship_fleets(1, range(130), P1HW[1:], planet=P1HW[0])
s += [f"fleet 1 130 planet {P1HW[0]} at {P1HW[1]} {P1HW[2]} ships 0:1,1:1,2:1 plan 1 fuel 100"]
specs["cb043"] = s

# CB-044 (CAP-C): CB-039 with player 1's fleet 12 holding two designs.
s = tech(range(2)) + enemies(range(2)) + [
    f"design 0 0 {L_FR} = Laser Frigate",
    f"design 1 0 {L_FR} = Laser Frigate", f"design 1 1 {L_FR1} = Frigate L1",
    "plan 0 1 5 1 0 1 = Enemies", "plan 1 1 5 1 0 1 = Enemies"]
s += one_ship_fleets(0, range(140), DEEP)
s += one_ship_fleets(1, [i for i in range(140) if i != 12], DEEP)
s += [f"fleet 1 12 at {DEEP[0]} {DEEP[1]} ships 0:1,1:1 plan 1 fuel 100"]
specs["cb044"] = s

# CB-045: cargo in the speed code. Player 0's Laser Destroyer attacks player
# 1's unarmed freighter fleets in deep space (as CB-038).
s = tech(range(2)) + enemies(range(2)) + [
    f"design 0 0 {L_DD} = Laser DD",
    f"design 1 0 {MED} = Medium", f"design 1 1 {SMALL} = Small",
    "plan 0 1 5 1 0 1 = Enemies",
    f"fleet 0 0 at {DEEP[0]} {DEEP[1]} ships 0:1 plan 1 fuel 100",
    f"fleet 1 0 at {DEEP[0]} {DEEP[1]} ships 0:1,1:1 fuel 100 cargo 140 0 0 0",
    f"fleet 1 1 at {DEEP[0]} {DEEP[1]} ships 0:3 fuel 100 cargo 210 0 0 0",
    f"fleet 1 2 at {DEEP[0]} {DEEP[1]} ships 0:3 fuel 100 cargo 212 0 0 0",
    f"fleet 1 3 at {DEEP[0]} {DEEP[1]} ships 0:3 fuel 100 cargo 213 0 0 0",
]
specs["cb045"] = s

# CB-046: Mystery Trader items from battle. Player 0 (every field at 26, no
# Mystery Trader items) destroys player 1's ships carrying Mystery Trader parts.
base46 = tech(range(2)) + enemies(range(2)) + [
    "mt 0 0", "mt 1 0", "research 0 0", "research 1 0",
    f"design 0 0 {PH_DD} = Phaser DD",
    "plan 0 1 5 1 0 1 = Enemies", "plan 1 1 5 1 0 1 = Enemies"]
specs["cb046"] = base46 + [
    f"design 1 0 {AMT_DD} = AMT DD",
    f"fleet 0 0 at {DEEP[0]} {DEEP[1]} ships 0:30 plan 1 fuel 280",
    f"fleet 1 0 at {DEEP[0]} {DEEP[1]} ships 0:6 plan 1 fuel 280"]
# control: player 0's biotechnology at 3 (the Anti Matter Torpedo needs 21),
# so an attempt that finds no trader part can gain a field
specs["cb046-bio"] = [l for l in base46 if l != "tech 0 bio 26"] + ["tech 0 bio 3"] + [
    f"design 1 0 {AMT_DD} = AMT DD",
    f"fleet 0 0 at {DEEP[0]} {DEEP[1]} ships 0:30 plan 1 fuel 280",
    f"fleet 1 0 at {DEEP[0]} {DEEP[1]} ships 0:6 plan 1 fuel 280"]
specs["cb046-morph"] = base46 + [
    f"design 1 0 {MORPH} = Morph",
    f"fleet 0 0 at {DEEP[0]} {DEEP[1]} ships 0:80 plan 1 fuel 280",
    f"fleet 1 0 at {DEEP[0]} {DEEP[1]} ships 0:3 plan 1 fuel 400"]
# CB-048 (round 7, MT-A): 30 one-ship Morph fleets, so every kill is its own
# kill event; the control puts all 30 Morphs in one fleet.
specs["cb048"] = base46 + [
    f"design 1 0 {MORPH} = Morph",
    f"fleet 0 0 at {DEEP[0]} {DEEP[1]} ships 0:80 plan 1 fuel 280"] + [
    f"fleet 1 {i} at {DEEP[0]} {DEEP[1]} ships 0:1 plan 1 fuel 400" for i in range(30)]
specs["cb048-ctl"] = base46 + [
    f"design 1 0 {MORPH} = Morph",
    f"fleet 0 0 at {DEEP[0]} {DEEP[1]} ships 0:80 plan 1 fuel 280",
    f"fleet 1 0 at {DEEP[0]} {DEEP[1]} ships 0:30 plan 1 fuel 400"]
# CB-049 (round 7): battle movement with many movers on tactics 1 to 4,
# target-type mismatches, weapons of three ranges, capacitors, deflectors,
# sappers and shields (the parts of COMBAT.md's movement rules that the
# CB-041..CB-046 replays did not exercise).
specs["cb049"] = tech(range(2)) + enemies(range(2)) + [
    "design 0 0 Destroyer, 1 Long Hump 6, 1 Colloidal Phaser, 1 Laser, 1 Delta Torpedo, 2 Tritanium, empty, 1 Energy Capacitor = Mixed DD",
    "design 0 1 Destroyer, 1 Long Hump 6, 1 Pulsed Sapper, 1 Pulsed Sapper, 1 Wolverine Diffuse Shield, 2 Tritanium, 1 Beam Deflector, empty = Sapper DD",
    "design 1 0 Destroyer, 1 Long Hump 6, 1 Colloidal Phaser, 1 Rho Torpedo, 1 Wolverine Diffuse Shield, 2 Tritanium, 1 Beam Deflector, 1 Flux Capacitor = Shield DD",
    "design 1 1 Frigate, 1 Long Hump 6, 1 Rhino Scanner, 3 Delta Torpedo, 2 Wolverine Diffuse Shield = Torpedo Frigate",
    "design 1 2 Medium Freighter, 1 Long Hump 6, 1 Rhino Scanner, 1 Wolverine Diffuse Shield = Shield Freighter",
    # plan OWNER K tactic primary secondary who: 1 disengage if challenged, 2 minimize
    # damage to self, 3 maximize net damage, 4 maximize damage ratio; targets 1 any,
    # 3 armed ships, 4 bombers and freighters, 5 unarmed ships
    "plan 0 1 3 1 0 1 = Net", "plan 0 2 2 3 1 1 = Careful", "plan 0 3 4 5 0 1 = Ratio unarmed",
    "plan 1 1 1 1 0 1 = Challenged", "plan 1 2 4 4 0 1 = Ratio freighters",
    "plan 1 3 3 1 0 1 = Net", "plan 1 4 2 3 0 1 = Careful",
    f"fleet 0 0 at {DEEP[0]} {DEEP[1]} ships 0:4 plan 1 fuel 280",
    f"fleet 0 1 at {DEEP[0]} {DEEP[1]} ships 1:3 plan 2 fuel 280",
    f"fleet 0 2 at {DEEP[0]} {DEEP[1]} ships 0:2 plan 3 fuel 280",
    f"fleet 1 0 at {DEEP[0]} {DEEP[1]} ships 0:4 plan 1 fuel 280",
    f"fleet 1 1 at {DEEP[0]} {DEEP[1]} ships 1:3 plan 2 fuel 125",
    f"fleet 1 2 at {DEEP[0]} {DEEP[1]} ships 2:2 plan 3 fuel 450",
    f"fleet 1 3 at {DEEP[0]} {DEEP[1]} ships 0:2 plan 4 fuel 280"]

# CB-047: queued ships lost with a starbase. Player 1's homeworld queues 50
# Laser Destroyers, then 20 factories (planetary item 7). Player 0's Phaser
# Destroyers destroy its armed Space Station; the control has no attackers.
base47 = tech(range(2)) + enemies(range(2)) + [
    f"design 0 0 {PH_DD} = Phaser DD", f"design 1 0 {L_DD} = Laser DD",
    "plan 0 1 5 1 0 1 = Enemies",
    f"queue {P1HW[0]} 0:50:2,7:20:1"]
specs["cb047"] = base47 + [f"fleet 0 0 planet {P1HW[0]} at {P1HW[1]} {P1HW[2]} ships 0:40 plan 1 fuel 280"]
specs["cb047-ctl"] = base47 + [f"fleet 0 0 at {DEEP[0]} {DEEP[1]} ships 0:1 plan 1 fuel 280"]

# Round 8 (stars-decomp #28, "Round 8 predictions"). CB-050: the torpedo
# estimate's shield term. Three players in CB3P deep space; 0 and 2 are
# friends, both enemies of 1. The Upsilon and Jihad stacks target
# starbases only, so only player 1's runner moves. The control's runner
# has no shield.
C3P = (1060, 1080)
base50 = tech(range(3)) + [
    "relation 0 1 2", "relation 0 2 0", "relation 1 0 2", "relation 1 2 2",
    "relation 2 0 0", "relation 2 1 2",
    "design 0 0 Destroyer, 1 Long Hump 6, 1 Upsilon Torpedo, 1 Upsilon Torpedo, empty, 2 Tritanium, empty, empty = Upsilon DD",
    "design 1 0 Destroyer, 1 Long Hump 6, empty, empty, 1 Wolverine Diffuse Shield, 2 Tritanium, empty, empty = Shield Runner",
    "design 1 1 Destroyer, 1 Long Hump 6, empty, empty, empty, 2 Tritanium, empty, empty = Bare Runner",
    "design 2 0 Destroyer, 1 Long Hump 6, 1 Jihad Missile, 1 Jihad Missile, empty, 2 Tritanium, empty, empty = Jihad DD",
    "plan 0 1 2 2 0 1 = Starbases only", "plan 2 1 2 2 0 1 = Starbases only", "plan 1 1 0 1 0 1 = Run",
    f"fleet 0 0 at {C3P[0]} {C3P[1]} ships 0:2 plan 1 fuel 280",
    f"fleet 2 0 at {C3P[0]} {C3P[1]} ships 0:4 plan 1 fuel 280"]
specs["cb050"] = base50 + [f"fleet 1 0 at {C3P[0]} {C3P[1]} ships 0:2 plan 1 fuel 280"]
specs["cb050-ctl"] = base50 + [f"fleet 1 0 at {C3P[0]} {C3P[1]} ships 1:2 plan 1 fuel 280"]
# CB-051: falling back from the primary to the secondary target type.
specs["cb051"] = tech(range(2)) + enemies(range(2)) + [
    f"design 0 0 {L_DD} = Laser DD", f"design 1 0 {L_DD} = Laser DD", f"design 1 1 {MED} = Freighter",
    "plan 0 1 3 2 3 1 = Starbase else armed", "plan 0 2 5 7 1 1 = Freighters else any",
    "plan 1 1 2 3 0 1 = Careful",
    f"fleet 0 0 at {DEEP[0]} {DEEP[1]} ships 0:3 plan 1 fuel 280",
    f"fleet 0 1 at {DEEP[0]} {DEEP[1]} ships 0:2 plan 2 fuel 280",
    f"fleet 1 0 at {DEEP[0]} {DEEP[1]} ships 0:3 plan 1 fuel 280",
    f"fleet 1 1 at {DEEP[0]} {DEEP[1]} ships 1:1 fuel 450"]

for name, lines in specs.items():
    d = os.path.join(os.path.dirname(HERE), name.split("-")[0])
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name + ".spec"), "w") as f:
        f.write("\n".join(lines) + "\n")
