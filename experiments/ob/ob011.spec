# OB-011: scanning of objects by a JOAT viewer with Rhino scouts (R 50, no penetrating range) (experiments/ob/gen.py)
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
planet 8 scanner none
design 1 1 Scout, 1 Long Hump 6, 1 Rhino Scanner, empty = Rhino Scout
fleet 1 0 at 1050 1040 ships 1:1 plan 0 fuel 50 
fleet 1 1 at 1050 1180 ships 1:1 plan 0 fuel 50 
fleet 1 2 at 1050 1260 ships 1:1 plan 0 fuel 50 
fleet 1 3 at 1110 1360 ships 1:1 plan 0 fuel 50 
fleet 1 4 at 1360 1040 ships 1:1 plan 0 fuel 50 
fleet 1 5 at 1370 1230 ships 1:1 plan 0 fuel 50 
fleet 1 6 at 1220 1060 ships 1:1 plan 0 fuel 50 
fleet 1 7 at 1300 1150 ships 1:1 plan 0 fuel 50 
thing minefield 0 0 1062 1040 100 kind std
thing minefield 0 1 1063 1180 100 kind std
thing minefield 0 2 1080 1260 1000 kind std
thing minefield 0 3 1140 1360 800 kind std
thing minefield 0 4 1360 1080 100 known 2
thing minefield 0 5 1370 1281 100 known 2
thing wormhole 0 1220 1066 1 0
thing wormhole 1 1110 1110 0 0
thing wormhole 2 1210 1230 3 0 seen 2
thing wormhole 3 1300 1310 2 0
thing packet 0 0 1300 1105 6 5 100 0 0
thing trader 0 1020 1100 1380 1100 8
