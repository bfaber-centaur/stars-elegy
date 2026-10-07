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
relation 1 0 2
design 0 0 Destroyer, 1 Long Hump 6, 1 Laser, empty, empty, 2 Tritanium, empty, empty = Watcher
design 1 0 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
plan 0 1 5 2 0 1 = Starbases Only
plan 1 1 0 1 0 1 dump = Dumper
plan 1 2 0 1 0 1 = Keeper
planet 5 owner 1 pop 500 starbase none
planetset 5 fe=100 bo=100 ge=100
planet 22 owner 1 pop 500 starbase none
planetset 22 fe=100 bo=100 ge=100
# D1 deep space: a Watcher (never fires) meets a dumping Hauler
fleet 0 0 at 1020 1230 ships 0:1 plan 1 fuel 100
fleet 1 0 at 1020 1230 ships 0:1 plan 1 fuel 100 cargo 20 10 5 0
# D2 at player 1's planet 5 (no starbase)
fleet 0 1 planet 5 at 1146 1180 ships 0:1 plan 1 fuel 100
fleet 1 1 planet 5 at 1146 1180 ships 0:1 plan 1 fuel 100 cargo 20 10 5 0
# C1 deep space, dump plan, no battle
fleet 1 2 at 1100 1230 ships 0:1 plan 1 fuel 100 cargo 20 10 5 0
# C2 player 1's planet 22, dump plan, no battle
fleet 1 3 planet 22 at 1368 1292 ships 0:1 plan 1 fuel 100 cargo 20 10 5 0
# C3 deep space battle, plan without dump
fleet 0 2 at 1180 1230 ships 0:1 plan 1 fuel 100
fleet 1 4 at 1180 1230 ships 0:1 plan 2 fuel 100 cargo 20 10 5 0
