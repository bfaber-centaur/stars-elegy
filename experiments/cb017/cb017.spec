tech 0 energy 26
tech 0 weapons 26
tech 0 prop 26
tech 0 con 26
tech 0 elec 26
tech 0 bio 26
tech 1 energy 26
tech 1 weapons 26
tech 1 prop 26
tech 1 con 26
tech 1 elec 26
tech 1 bio 26
relation 0 1 0
relation 1 0 0
design 0 0 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
design 0 1 Fuel Transport, 1 Long Hump 6 = Tanker
design 0 2 Super-Fuel Xport, 1 Long Hump 6 = Super Tanker
sbdesign 0 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Laser Station
sbdesign 0 1 Orbital Fort, empty, empty, empty, empty, empty = Bare Fort
sbdesign 0 2 Space Dock, empty = Bare Dock
plan 0 1 5 1 0 1 = Max Any
planet 18 owner 0 pop 500 starbase 0
planet 19 owner 0 pop 500 starbase 2
planet 21 owner 0 pop 500 starbase 1
planet 22 owner 0 pop 500 starbase none
planet 5 owner 1 pop 500 starbase none
# every player-0 stack starts with 300/500 damage on all ships; neutral relations, no battles
# R1 deep space, stationary
fleet 0 0 at 1020 1230 ships 0:3 plan 1 fuel 100 dmg 0:300:100
# R2 deep space with a Fuel Transport in the fleet
fleet 0 1 at 1060 1230 ships 0:3,1:1 plan 1 fuel 100 dmg 0:300:100
# R3 deep space with a Super-Fuel Xport in the fleet
fleet 0 2 at 1100 1230 ships 0:3,2:1 plan 1 fuel 100 dmg 0:300:100
# R4 orbiting player 1's planet 5 (no starbase)
fleet 0 3 planet 5 at 1146 1180 ships 0:3 plan 1 fuel 100 dmg 0:300:100
# R5 orbiting unowned planet 0
fleet 0 4 planet 0 at 1045 1291 ships 0:3 plan 1 fuel 100 dmg 0:300:100
# R6 own planet 22, no starbase
fleet 0 5 planet 22 at 1368 1292 ships 0:3 plan 1 fuel 100 dmg 0:300:100
# R7 own planet 21, Orbital Fort (no dock)
fleet 0 6 planet 21 at 1359 1121 ships 0:3 plan 1 fuel 100 dmg 0:300:100
# R8 own planet 19, Space Dock
fleet 0 7 planet 19 at 1342 1123 ships 0:3 plan 1 fuel 100 dmg 0:300:100
# R9 own planet 18, Space Station
fleet 0 8 planet 18 at 1324 1192 ships 0:3 plan 1 fuel 100 dmg 0:300:100
# R10 own planet 22 as R6, plus a Fuel Transport
fleet 0 9 planet 22 at 1368 1292 ships 0:3,1:1 plan 1 fuel 100 dmg 0:300:100
fleet 1 0 at 1300 1230 ships 0:1 fuel 100
