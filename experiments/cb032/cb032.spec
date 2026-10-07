prt 0 9
prt 1 9
prt 2 9
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
tech 2 energy 26
tech 2 weapons 26
tech 2 prop 26
tech 2 con 26
tech 2 elec 26
tech 2 bio 26
relation 0 1 2
relation 2 1 2
relation 0 2 0
relation 2 0 0
relation 1 0 0
relation 1 2 0
design 0 0 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, 2 Tritanium, empty, empty = Brute
design 2 0 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, 2 Tritanium, empty, empty = Brute
design 1 0 Small Freighter, 1 Long Hump 6, empty, empty = Runner
plan 0 1 5 1 0 5 = Hunt P1
plan 1 1 0 1 0 0 = Run
plan 2 1 5 1 0 5 = Hunt P1
# players 0 and 2 (Laser Destroyers) both name player 1, whose only token is an unarmed Freighter
fleet 0 0 at 1060 1080 ships 0:2 plan 1 fuel 100
fleet 1 0 at 1060 1080 ships 0:1 plan 1 fuel 100
fleet 2 0 at 1060 1080 ships 0:2 plan 1 fuel 100
