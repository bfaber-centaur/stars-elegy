# CS-003-C2: single-torpedo salvos: Alpha Torpedo, Juggernaut and Doomsday Missile (experiments/cs003/gen.py)
relation 0 1 2
relation 1 0 2
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
research 0 0
research 1 0
plan 0 0 5 1 0 1 = Enemies
plan 1 0 5 1 0 1 = Enemies
design 1 0 Cruiser, 2 Long Hump 6, empty, empty, 1 Laser, empty, empty, empty = Light
design 1 1 Battleship, 4 Long Hump 6, empty, empty, 1 Laser, empty, empty, empty, empty, empty, empty, empty = Heavy
design 0 0 Battleship, 4 Long Hump 6, empty, empty, 1 Alpha Torpedo, empty, empty, empty, empty, empty, empty, empty = T1-00
design 0 1 Battleship, 4 Long Hump 6, empty, empty, 1 Juggernaut Missile, empty, empty, empty, empty, empty, empty, empty = T1-09
design 0 2 Battleship, 4 Long Hump 6, empty, empty, 1 Doomsday Missile, empty, empty, empty, empty, empty, empty, empty = T1-10
fleet 0 0 at 1060 1230 ships 0:1 plan 0 fuel 200
fleet 1 0 at 1060 1230 ships 0:1 plan 0 fuel 200
fleet 0 1 at 1140 1230 ships 1:1 plan 0 fuel 200
fleet 1 1 at 1140 1230 ships 1:1 plan 0 fuel 200
fleet 0 2 at 1220 1230 ships 2:1 plan 0 fuel 200
fleet 1 2 at 1220 1230 ships 1:1 plan 0 fuel 200
