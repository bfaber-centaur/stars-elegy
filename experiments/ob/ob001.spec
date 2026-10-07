# OB-001: minefield sweeping by fleets and starbases (mutual enemies) (experiments/ob/gen.py)
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
planet 5 owner 0 pop 1000 starbase 1
planetset 5 mines=0 factories=0 defenses=0
thing minefield 1 0 1050 1030 1000 kind std
fleet 0 0 at 1070 1030 ships 2:1 plan 0 fuel 50 
thing minefield 1 1 1050 1180 1000 kind std
fleet 0 1 at 1050 1180 ships 1:1 plan 0 fuel 50 
thing minefield 1 2 1050 1250 1000 kind std
fleet 0 2 at 1050 1250 ships 3:1 plan 0 fuel 50 
thing minefield 1 3 1210 1220 1000 kind std
fleet 0 3 at 1210 1220 ships 4:1 plan 0 fuel 50 
thing minefield 1 4 1280 1240 1000 kind std
fleet 0 4 at 1280 1240 ships 1:1 plan 1 fuel 50 
thing minefield 1 5 1370 1220 1000 kind std
fleet 0 5 at 1370 1220 ships 1:1 plan 0 fuel 50 
fleet 0 6 at 1370 1220 ships 1:1 plan 0 fuel 50 
thing minefield 1 6 1080 1360 1000 kind std
fleet 0 7 at 1080 1360 ships 1:3 plan 0 fuel 50 
thing minefield 1 7 1220 1060 1000 kind bump
fleet 0 8 at 1220 1060 ships 1:1 plan 0 fuel 50 
thing minefield 1 8 1360 1040 2000 kind std
fleet 0 9 at 1360 1040 ships 2:1 plan 0 fuel 50 
thing minefield 1 9 1130 1200 1000 kind std
