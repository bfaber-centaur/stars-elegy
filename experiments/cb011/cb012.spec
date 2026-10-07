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
relation 0 1 2
relation 1 0 0
design 0 0 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
design 1 0 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 1 1 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
sbdesign 0 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Laser Station
sbdesign 0 1 Space Station, empty, empty, 8 Mole-skin Shield, empty, empty, 8 Mole-skin Shield, empty, empty, empty, empty, empty, empty = Unarmed Station
sbdesign 0 2 Orbital Fort, empty, empty, empty, empty, empty = Bare Fort
sbdesign 1 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Laser Station
sbdesign 1 1 Space Station, empty, empty, 8 Mole-skin Shield, empty, empty, 8 Mole-skin Shield, empty, empty, empty, empty, empty, empty = Unarmed Station
planet 18 owner 0 pop 500 starbase 0
planet 19 owner 0 pop 500 starbase 1
planet 21 owner 0 pop 500 starbase 0
planet 15 owner 0 pop 500 starbase 0
planet 22 owner 0 pop 500 starbase none
planet 5 owner 1 pop 500 starbase 1
planet 12 owner 1 pop 500 starbase 1
plan 0 0 5 1 0 3 = Station Everyone
plan 0 1 5 1 0 1 = Max Any
plan 0 3 5 5 0 1 = Unarmed Only
plan 0 4 5 3 0 1 = Armed Only
plan 1 1 5 1 0 1 = Max Any
plan 1 2 5 1 0 0 = Nobody
# S1 planet 18, armed station: armed P1 fleet attacking enemies (P1 sees P0 as neutral)
fleet 1 0 planet 18 at 1324 1192 ships 1:5 plan 1 fuel 100
# S2 planet 19, unarmed station: same visitor
fleet 1 1 planet 19 at 1342 1123 ships 1:5 plan 1 fuel 100
# S3 planet 21, armed station: unarmed P1 visitor attacking enemies
fleet 1 2 planet 21 at 1359 1121 ships 0:3 plan 1 fuel 100
# S4 planet 5 (P1, unarmed station): P0 frigates, primary unarmed, no secondary
fleet 0 0 planet 5 at 1146 1180 ships 0:5 plan 3 fuel 100
# S5 planet 12 (P1, unarmed station): P0 frigates, primary armed, no secondary
fleet 0 1 planet 12 at 1245 1158 ships 0:5 plan 4 fuel 100
# S6 planet 15 (P0, armed station): P0 frigates destroy P1 haulers
fleet 0 2 planet 15 at 1281 1064 ships 0:10 plan 1 fuel 100
fleet 1 3 planet 15 at 1281 1064 ships 0:6 plan 2 fuel 100
# S7 planet 22 (P0, no starbase): the same
fleet 0 3 planet 22 at 1368 1292 ships 0:10 plan 1 fuel 100
fleet 1 4 planet 22 at 1368 1292 ships 0:6 plan 2 fuel 100
