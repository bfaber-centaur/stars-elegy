# OB-009: packet impacts with population growth controlled (player 0 packets, mutual enemies) (experiments/ob/gen.py)
relation 0 1 2
relation 1 0 2
tech 0 energy 26
tech 0 weapons 26
tech 0 prop 26
tech 0 con 26
tech 0 elec 26
tech 0 bio 26
research 0 0
research 1 0
# player 0 ship designs (all parts within tech 26)
design 0 0 Mini Mine Layer, 1 Long Hump 6, 2 Mine Dispenser 40, empty, empty = Layer
design 0 1 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, empty, empty, empty = Laser DD
design 0 2 Destroyer, 1 Long Hump 6, 1 Gatling Gun, 1 Gatling Gun, empty, empty, empty, empty = Gatling DD
design 0 3 Destroyer, 1 Long Hump 6, 1 Mini Gun, empty, empty, empty, empty, empty = Mini Gun DD
design 0 4 Destroyer, 1 Long Hump 6, 1 Pulsed Sapper, 1 Pulsed Sapper, empty, empty, empty, empty = Sapper DD
design 0 5 Mini Mine Layer, 1 Long Hump 6, 2 Mine Dispenser 40, 2 Heavy Dispenser 50, empty = Layer2
design 0 6 Frigate, 1 Long Hump 6, empty, 3 Speed Trap 20, empty = Trap Frigate
design 0 7 Frigate, 1 Long Hump 6, empty, 2 Mine Dispenser 40, empty = MD40 Frigate
design 0 8 Frigate, 1 Long Hump 6, empty, 1 Multi Contained Munition, empty = MCM Frigate
design 0 9 Super Freighter, 3 Long Hump 6, empty, empty, empty = Super Freighter
design 0 10 Scout, 1 Long Hump 6, empty, empty = Scout
# player 0 starbase designs: 0 = the 2400 homeworld design, unchanged
sbdesign 0 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Starbase
sbdesign 0 1 Orbital Fort, empty, 2 Laser, empty, empty, empty = Laser Fort
sbdesign 0 2 Orbital Fort, 1 Mass Driver 7, empty, empty, empty, empty = Catcher 7
# plans: tactic 4, primary any, no secondary, attack who
plan 0 0 4 1 0 1 = Enemies
plan 0 1 4 1 0 0 = Nobody
plan 0 2 4 1 0 2 = Neutral and enemies
plan 0 3 4 1 0 3 = Everyone
plan 0 4 4 1 0 5 = Player 1 only
planet 9 owner 0 pop 1000 starbase 2
planetset 9 mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0 env=50,50,50 excess=0
planet 14 owner 0 pop 1000 starbase 2
planetset 14 mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0 env=50,50,50 excess=0
planet 10 owner 0 pop 1000 starbase none
planetset 10 mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0 env=50,50,50 excess=0
planet 16 owner 0 pop 1000 starbase none
planetset 16 mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0 env=50,50,50 excess=0
planet 20 owner 1 pop 1000 starbase none
planetset 20 mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0 env=50,50,50 excess=0
planet 22 owner 1 pop 500 starbase none
planetset 22 mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0 env=50,50,50 excess=0
planet 18 owner 1 pop 1000 starbase none
planetset 18 mines=0 factories=0 fe=0 bo=0 ge=0 env=50,50,50 excess=0 defenses=50
planet 21 owner 1 pop 1000 starbase none
planetset 21 mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0 env=50,50,50 excess=0
thing packet 0 0 1208 1347 9 10 1000 0 0
thing packet 0 1 1268 1347 14 7 1000 0 0
thing packet 0 2 1224 1309 10 10 1000 0 0
thing packet 0 3 1348 1340 20 10 1000 0 0
thing packet 0 4 1368 1342 22 10 1000 0 0
thing packet 0 5 1324 1242 18 10 1000 0 0
